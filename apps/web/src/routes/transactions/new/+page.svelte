<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import type {
		AccountOption,
		Book,
		TransactionCreatePreviewResponse,
		TransactionCreateRequest,
		TransactionCreateSettings,
		TransactionCreateSplitRequest
	} from '$lib/api/types';
	import { DEFAULT_LOCALE, messages, t, type Locale, type MessageKey } from '$lib/i18n';

	type DraftSplit = TransactionCreateSplitRequest & { client_id: string };
	type PageForm = {
		preview?: TransactionCreatePreviewResponse | null;
		payload?: TransactionCreateRequest | null;
		fieldErrors?: Partial<Record<'book_id' | 'date' | 'description' | 'currency' | 'splits', string>>;
		errorCode?: string;
		errorKey?: string;
		requestRef?: string;
		retryable?: boolean;
		recoveryRef?: string | null;
	} | null;
	type PageData = {
		locale?: Locale;
		books: Book[];
		activeBook: Book | null;
		accounts: AccountOption[];
		accountOptionsAvailable: boolean;
		accountOptionsLimited: boolean;
		accountOptionsPartialFailure: boolean;
		accountOptionsErrorCode: string | null;
		createSettings: TransactionCreateSettings;
		previewOnly: boolean;
	};

	let { data, form }: { data: PageData; form?: PageForm } = $props();
	const locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	const preview = $derived(form?.preview ?? null);
	const fieldErrors = $derived(form?.fieldErrors ?? {});
	const selectedBook = $derived(data.activeBook ?? data.books[0] ?? null);

	function isKnownMessageKey(key: string | undefined): key is MessageKey {
		return Boolean(key && Object.hasOwn(messages[DEFAULT_LOCALE], key));
	}

	function message(key: string | undefined): string {
		const safeKey = isKnownMessageKey(key) ? key : 'transactionCreate.error.generic';
		return t(locale, safeKey);
	}

	function todayFallback(): string {
		return '';
	}

	function initialPayload(): TransactionCreateRequest | null {
		return form?.payload ?? null;
	}

	function initialCurrency(): string {
		return initialPayload()?.currency ?? (data.activeBook ?? data.books[0] ?? null)?.base_currency ?? 'SEK';
	}

	function initialSplits(): DraftSplit[] {
		return initialDraftSplits(initialPayload(), data.accounts);
	}

	function initialDraftSplits(payload: TransactionCreateRequest | null, accounts: AccountOption[]): DraftSplit[] {
		if (payload?.splits.length) {
			return payload.splits.map((split, index) => ({
				client_id: `loaded-${index}-${split.account_id}`,
				account_id: split.account_id,
				amount: split.amount,
				memo: split.memo
			}));
		}
		return [
			{ client_id: 'initial-debit', account_id: accounts[0]?.id ?? '', amount: '', memo: '' },
			{ client_id: 'initial-credit', account_id: accounts[1]?.id ?? '', amount: '', memo: '' }
		];
	}

	let date = $state(initialPayload()?.date ?? todayFallback());
	let description = $state(initialPayload()?.description ?? '');
	let currency = $state(initialCurrency());
	let splits = $state<DraftSplit[]>(initialSplits());
	let splitOrdinal = $state(3);
	let confirmSubmitting = $state(false);

	const previewTransactionJson = $derived.by(() => {
		const payload = initialPayload();
		return payload ? JSON.stringify(payload) : '';
	});
	const draftTransaction = $derived.by<TransactionCreateRequest>(() => ({
		date: date.trim(),
		description: description.trim(),
		currency: currency.trim().toUpperCase(),
		splits: splits.map((split) => ({
			account_id: split.account_id,
			amount: split.amount.trim(),
			memo: split.memo.trim()
		}))
	}));
	const transactionJson = $derived(JSON.stringify(draftTransaction));
	const previewIsStale = $derived(Boolean(preview) && transactionJson !== previewTransactionJson);
	const confirmDisabled = $derived(!preview || !preview.confirm_allowed || previewIsStale || confirmSubmitting);
	const visibleAccountCount = $derived(data.accounts.length);
	const errorSummary = $derived(message(form?.errorKey));

	function accountLabel(account: AccountOption): string {
		return `${account.display_name || account.name} · ${account.type} · ${account.currency}`;
	}

	function accountTitle(account: AccountOption): string {
		return `${account.full_name} · ${account.type} · ${account.currency}`;
	}

	function accountById(accountId: string): AccountOption | undefined {
		return data.accounts.find((account) => account.id === accountId);
	}

	function createPolicySummary(settings: TransactionCreateSettings): string {
		if (settings.known === false) return t(locale, 'transactionCreate.policyServerDecided');
		const deployment = settings.deployment_writes_enabled ?? settings.deployment?.writes_enabled;
		const effective = settings.effective_enabled ?? settings.effective?.enabled;
		const generation = settings.transaction_create_generation ?? settings.generation ?? settings.create_generation;
		const recovery = settings.recovery_required || settings.recovery?.required;
		const blockedCodes = settings.blocked_codes?.length ? `; blocked ${settings.blocked_codes.join(',')}` : '';
		return `enabled ${String(settings.enabled)}; deployment ${deployment === undefined ? t(locale, 'transactionCreate.policyUnknown') : String(deployment)}; effective ${effective === undefined ? t(locale, 'transactionCreate.policyUnknown') : String(effective)}; generation ${generation}; recovery ${String(Boolean(recovery))}${blockedCodes}`;
	}

	function newSplit(): DraftSplit {
		const split = { client_id: `added-${splitOrdinal}`, account_id: '', amount: '', memo: '' };
		splitOrdinal += 1;
		return split;
	}

	function addSplit() {
		if (splits.length >= 50) return;
		splits = [...splits, newSplit()];
	}

	function removeSplit(index: number) {
		if (splits.length <= 2) return;
		splits = splits.filter((_, itemIndex) => itemIndex !== index);
	}

	function moveSplit(index: number, direction: -1 | 1) {
		const target = index + direction;
		if (target < 0 || target >= splits.length) return;
		const next = splits.slice();
		const current = next[index];
		next[index] = next[target];
		next[target] = current;
		splits = next;
	}

	type DecimalStringParts = { sign: bigint; digits: string; scale: number };

	function decimalStringToParts(value: string): DecimalStringParts | null {
		const trimmed = value.trim();
		const match = /^([+-]?)(\d+)(?:\.(\d+))?$/.exec(trimmed);
		if (!match) return null;
		const sign = match[1] === '-' ? -1n : 1n;
		const whole = match[2].replace(/^0+(?=\d)/, '');
		const fraction = match[3] ?? '';
		const significant = `${whole}${fraction}`.replace(/^0+/, '');
		if ((significant || '0').length > 18 || trimmed.length > 64) return null;
		return { sign, digits: `${whole}${fraction}` || '0', scale: fraction.length };
	}

	function scaleDecimalParts(parts: DecimalStringParts, maxScale: number): bigint {
		return parts.sign * BigInt(`${parts.digits}${'0'.repeat(maxScale - parts.scale)}`);
	}

	function decimalStringToUnits(value: string): bigint | null {
		const parts = decimalStringToParts(value);
		return parts ? scaleDecimalParts(parts, parts.scale) : null;
	}

	function formatScaledUnits(value: bigint, maxScale: number): string {
		const sign = value < 0n ? '-' : '';
		const absolute = value < 0n ? -value : value;
		if (maxScale === 0) return `${sign}${absolute.toString()}`;
		const raw = absolute.toString().padStart(maxScale + 1, '0');
		const whole = raw.substring(0, raw.length - maxScale) || '0';
		const fraction = raw.substring(raw.length - maxScale);
		return `${sign}${whole}.${fraction}`;
	}

	const runningBalance = $derived.by(() => {
		const parsed: DecimalStringParts[] = [];
		let invalid = false;
		for (const split of splits) {
			const parts = decimalStringToParts(split.amount);
			if (parts === null) {
				if (split.amount.trim()) invalid = true;
				continue;
			}
			parsed.push(parts);
		}
		const maxScale = parsed.reduce((scale, parts) => Math.max(scale, parts.scale), 0);
		let total = 0n;
		for (const parts of parsed) total += scaleDecimalParts(parts, maxScale);
		return {
			label: formatScaledUnits(total, maxScale),
			invalid,
			isZero: total === 0n && !invalid && splits.length >= 2
		};
	});

	function handleConfirmSubmit(event: SubmitEvent) {
		if (confirmDisabled) {
			event.preventDefault();
			return;
		}
		confirmSubmitting = true;
	}
</script>

<svelte:head>
	<title>{t(locale, 'transactionCreate.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl min-w-0 px-4 py-8">
	<div class="space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
		<h1 class="text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'transactionCreate.title')}</h1>
		<p class="max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'transactionCreate.subtitle')}</p>
	</div>

	<div class="mt-6">
		<WriteModeWarning compact {locale} />
	</div>

	<section class="mt-6 rounded-2xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);" aria-labelledby="create-policy-title">
		<h2 id="create-policy-title" class="text-lg font-semibold">{t(locale, 'transactionCreate.policyTitle')}</h2>
		<dl class="mt-3 grid min-w-0 gap-3 sm:grid-cols-2">
			<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.policyBook')}</dt><dd class="break-words">{selectedBook?.name ?? t(locale, 'transactionCreate.policyBookNone')}</dd></div>
			<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.policyState')}</dt><dd class="break-words">{createPolicySummary(data.createSettings)}</dd></div>
			<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.visibleAccounts')}</dt><dd>{visibleAccountCount}</dd></div>
			<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.scopeTitle')}</dt><dd>{t(locale, 'transactionCreate.scopeCopy')}</dd></div>
		</dl>
	</section>

	{#if !data.accountOptionsAvailable || data.accountOptionsPartialFailure}
		<section
			id="transaction-create-account-options-status"
			class="mt-6 rounded-2xl border p-4 text-sm"
			style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);"
			role={data.accountOptionsAvailable ? 'status' : 'alert'}
		>
			<h2 class="font-semibold">
				{!data.accountOptionsAvailable
					? locale === 'ru' ? 'Варианты posting-счетов временно недоступны' : 'Posting-account choices are temporarily unavailable'
					: locale === 'ru' ? 'Список posting-счетов ограничен' : 'Posting-account choices are partially limited'}
			</h2>
			<p class="mt-1">
				{data.accountOptionsAvailable
					? locale === 'ru'
						? 'Доступен ограниченный bounded-набор posting-счетов; preview остаётся доступен без legacy balance reads.'
						: 'A bounded subset of posting accounts is available; preview remains usable without legacy balance reads.'
					: locale === 'ru'
						? 'Выбор счетов и отправка preview отключены безопасно. Другие read-only разделы остаются доступны.'
						: 'Account selection and preview submission are safely disabled. Other read-only views remain available.'}
			</p>
			<a class="mt-3 inline-flex min-h-11 items-center rounded-xl border px-4 py-2 font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href="/diagnostics">
				{locale === 'ru' ? 'Открыть redacted diagnostics' : 'Open redacted diagnostics'}
			</a>
		</section>
	{/if}

	{#if errorSummary}
		<section id="transaction-create-error-summary" class="mt-6 rounded-2xl border p-4 text-sm" role="alert" tabindex="-1" style="border-color: var(--app-danger); background: var(--app-card-bg); color: var(--app-text);">
			<h2 class="font-semibold">{t(locale, 'transactionCreate.requestFailedTitle')}</h2>
			<p class="mt-1">{errorSummary}</p>
			{#if form?.requestRef}<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'transactionCreate.requestRef')}: {form.requestRef}</p>{/if}
			{#if form?.recoveryRef}<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'transactionCreate.recoveryRef')}: {form.recoveryRef}</p>{/if}
		</section>
	{/if}

	<form id="transaction-create-form" method="POST" aria-describedby="create-policy-title running-balance split-editor-help transaction-create-error-summary" class="mt-6 min-w-0 space-y-5 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" data-mobile-contract="320px no horizontal overflow">
		<input type="hidden" name="book_id" value={selectedBook?.id ?? ''} />

		<div class="grid min-w-0 gap-4 sm:grid-cols-2">
			<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-date">
				{t(locale, 'transactionCreate.dateLabel')}
				<input id="transaction-date" name="date" type="date" required bind:value={date} aria-invalid={fieldErrors.date ? 'true' : undefined} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
			</label>
			<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-currency">
				{t(locale, 'transactionCreate.currencyLabel')}
				<input id="transaction-currency" name="currency" maxlength="3" pattern="[A-Za-z][A-Za-z][A-Za-z]" required bind:value={currency} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 uppercase" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
			</label>
		</div>

		<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-description">
			{t(locale, 'transactionCreate.descriptionLabel')}
			<input id="transaction-description" name="description" required maxlength="256" bind:value={description} aria-invalid={fieldErrors.description ? 'true' : undefined} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
		</label>

		<section id="split-editor" class="min-w-0 rounded-2xl border p-4" aria-labelledby="split-editor-title" aria-describedby="split-editor-help running-balance" style="border-color: var(--app-border); background: var(--app-bg);">
			<div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
				<div class="min-w-0">
					<h2 id="split-editor-title" class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'transactionCreate.splitEditorTitle')}</h2>
					<p id="split-editor-help" class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'transactionCreate.splitEditorHelp')}</p>
				</div>
				<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60" style="border-color: var(--app-border); color: var(--app-text);" onclick={addSplit} disabled={splits.length >= 50}>{splits.length >= 50 ? t(locale, 'transactionCreate.addSplitLimit') : t(locale, 'transactionCreate.addSplit')}</button>
			</div>

			<div id="running-balance" class="mt-4 rounded-xl border p-3 text-sm" aria-live="polite" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);">
				<p class="font-semibold">{t(locale, 'transactionCreate.runningBalance')}: {runningBalance.label} {draftTransaction.currency}</p>
				<p class="mt-1">{runningBalance.isZero ? t(locale, 'transactionCreate.balanceZero') : t(locale, 'transactionCreate.balanceNonZero')}</p>
			</div>

			{#if fieldErrors.splits}
				<p class="mt-3 rounded-xl border p-3 text-sm" role="alert" style="border-color: var(--app-danger); color: var(--app-text); background: var(--app-card-bg);">{message(fieldErrors.splits)}</p>
			{/if}

			<div class="mt-4 space-y-4">
				{#each splits as split, index (split.client_id)}
					{@const selectedAccount = accountById(split.account_id)}
					<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
						<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactionCreate.splitLegend')} {index + 1}</legend>
						<div class="grid min-w-0 gap-3 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
							<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-account-${split.client_id}`}>
								{t(locale, 'transactionCreate.accountLabel')}
								<select id={`split-account-${split.client_id}`} name="split_account_id" required bind:value={split.account_id} disabled={!data.accountOptionsAvailable} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 disabled:cursor-not-allowed disabled:opacity-60" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);">
									<option value="">{t(locale, 'transactionCreate.accountChoose')}</option>
									{#each data.accounts as account (account.id)}
										<option value={account.id} title={accountTitle(account)}>{accountLabel(account)}</option>
									{/each}
								</select>
							</label>
							<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-amount-${split.client_id}`}>
								{t(locale, 'transactionCreate.amountLabel')}
								<input id={`split-amount-${split.client_id}`} name="split_amount" inputmode="decimal" required placeholder="-320.123" bind:value={split.amount} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" />
							</label>
						</div>
						<label class="mt-3 block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-memo-${split.client_id}`}>
							{t(locale, 'transactionCreate.memoLabel')}
							<input id={`split-memo-${split.client_id}`} name="split_memo" maxlength="512" bind:value={split.memo} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" />
						</label>
						<p class="mt-2 break-words text-xs" style="color: var(--app-muted);">{t(locale, 'transactionCreate.selectedAccount')}: {selectedAccount ? accountLabel(selectedAccount) : t(locale, 'transactionCreate.none')}</p>
						<div class="mt-3 flex min-w-0 flex-wrap gap-2">
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-border); color: var(--app-text);" onclick={() => moveSplit(index, -1)} disabled={index === 0}>{t(locale, 'transactionCreate.moveUp')}</button>
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-border); color: var(--app-text);" onclick={() => moveSplit(index, 1)} disabled={index === splits.length - 1}>{t(locale, 'transactionCreate.moveDown')}</button>
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-danger); color: var(--app-danger);" onclick={() => removeSplit(index)} disabled={splits.length <= 2}>{t(locale, 'transactionCreate.removeSplit')}</button>
						</div>
					</fieldset>
				{/each}
			</div>
		</section>

		<div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'transactionCreate.previewHelp')}</p>
			<button type="submit" formaction="?/preview" disabled={!data.accountOptionsAvailable} class="min-h-11 rounded-xl px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60" style="background: var(--app-accent);">{t(locale, 'transactionCreate.previewSubmit')}</button>
		</div>
	</form>

	{#if previewIsStale}
		<section class="mt-6 rounded-2xl border p-4 text-sm" role="status" aria-live="polite" style="border-color: #f59e0b; background: #fffbeb; color: #92400e;">
			<h2 class="font-semibold">{t(locale, 'transactionCreate.previewStaleTitle')}</h2>
			<p class="mt-1">{t(locale, 'transactionCreate.previewStale')}</p>
		</section>
	{/if}

	{#if preview}
		<section id="normalized-preview" class="mt-6 min-w-0 rounded-2xl border p-4" aria-labelledby="normalized-preview-title" style="border-color: var(--app-border); background: var(--app-card-bg);">
			<h2 id="normalized-preview-title" class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'transactionCreate.normalizedPreviewTitle')}</h2>
			<dl class="mt-3 grid min-w-0 gap-3 text-sm sm:grid-cols-2" style="color: var(--app-text);">
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.confirmAllowed')}</dt><dd>{String(preview.confirm_allowed)}</dd></div>
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.createCount')}</dt><dd>{preview.create_count}</dd></div>
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.expiresAt')}</dt><dd class="break-words">{preview.expires_at}</dd></div>
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.generation')}</dt><dd>{preview.create_generation}</dd></div>
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.dateLabel')}</dt><dd>{preview.date}</dd></div>
				<div class="min-w-0"><dt class="font-medium">{t(locale, 'transactionCreate.currencyLabel')}</dt><dd>{preview.currency}</dd></div>
				<div class="min-w-0 sm:col-span-2"><dt class="font-medium">{t(locale, 'transactionCreate.descriptionLabel')}</dt><dd class="break-words">{preview.description}</dd></div>
			</dl>
			<ul class="mt-4 space-y-3">
				{#each preview.splits as split (split.index)}
					<li class="min-w-0 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); color: var(--app-text);">
						<p class="font-semibold">{t(locale, 'transactionCreate.previewSplit')} {split.index + 1}: {split.amount} {preview.currency}</p>
						<p class="break-words" title={split.account.full_name}>{split.account.display_name || split.account.name || split.account.full_name} · {split.account.type} · {split.account.currency}</p>
						<p class="break-words" style="color: var(--app-muted);">{t(locale, 'transactionCreate.memoDisplay')}: {split.memo || '—'}</p>
					</li>
				{/each}
			</ul>
			{#if preview.warnings.length}
				<ul class="mt-4 list-disc pl-5 text-sm" style="color: #92400e;">
					{#each preview.warnings as warning}
						<li>{message(warning.message_key)}</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/if}

	{#if preview && preview.confirm_allowed && !previewIsStale}
		<form id="confirm-create-form" method="POST" action="?/confirm" onsubmit={handleConfirmSubmit} class="mt-6 min-w-0 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-describedby="confirm-create-help">
			<input type="hidden" name="book_id" value={selectedBook?.id ?? ''} />
			<input type="hidden" name="preview_token" value={preview.preview_token} />
			<input type="hidden" name="idempotency_key" value={preview.idempotency_key} />
			<input type="hidden" name="transaction_json" value={transactionJson} />
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'transactionCreate.confirmTitle')}</h2>
			<p id="confirm-create-help" class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'transactionCreate.confirmHelp')}</p>
			<button type="submit" formaction="?/confirm" disabled={confirmSubmitting} class="mt-4 min-h-11 rounded-xl px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60" style="background: var(--app-accent);">{t(locale, 'transactionCreate.confirmSubmit')}</button>
		</form>
	{:else if preview}
		<section class="mt-6 rounded-2xl border p-4 text-sm" role="status" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);">
			<h2 class="font-semibold">{t(locale, 'transactionCreate.confirmUnavailableTitle')}</h2>
			<p class="mt-1">{t(locale, 'transactionCreate.confirmUnavailableHelp')}</p>
		</section>
	{/if}

	<section class="mt-6 rounded-2xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);" aria-labelledby="safe-results-title">
		<h2 id="safe-results-title" class="font-semibold">{t(locale, 'transactionCreate.safeResultsTitle')}</h2>
		<p class="mt-1">{t(locale, 'transactionCreate.safeResultsHelp')}</p>
		<ul class="mt-2 list-disc pl-5">
			<li>{t(locale, 'transactionCreate.success.created')}</li>
			<li>{t(locale, 'transactionCreate.success.already_created')}</li>
		</ul>
	</section>
</main>
