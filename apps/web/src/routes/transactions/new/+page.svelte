<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import type {
		Account,
		Book,
		TransactionCreatePreviewResponse,
		TransactionCreateRequest,
		TransactionCreateSettings,
		TransactionCreateSplitRequest
	} from '$lib/api/types';
	import { DEFAULT_LOCALE, messages, t, type Locale, type MessageKey } from '$lib/i18n';

	type DraftSplit = TransactionCreateSplitRequest & { client_id: string };
	type PageForm = {
		preview?: TransactionCreatePreviewResponse;
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
		accounts: Account[];
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

	function initialDraftSplits(payload: TransactionCreateRequest | null, accounts: Account[]): DraftSplit[] {
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

	function accountLabel(account: Account): string {
		return `${account.full_name} / ${account.type} / ${account.currency}`;
	}

	function accountById(accountId: string): Account | undefined {
		return data.accounts.find((account) => account.id === accountId);
	}

	function newSplit(): DraftSplit {
		const split = { client_id: `added-${splitOrdinal}`, account_id: '', amount: '', memo: '' };
		splitOrdinal += 1;
		return split;
	}

	function addSplit() {
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

	function decimalStringToUnits(value: string): bigint | null {
		const trimmed = value.trim();
		const match = /^([+-]?)(\d+)(?:\.(\d+))?$/.exec(trimmed);
		if (!match) return null;
		const sign = match[1] === '-' ? -1n : 1n;
		const whole = match[2];
		const fraction = match[3] ?? '';
		if (fraction.length > 2) return null;
		return sign * BigInt(`${whole}${fraction.padEnd(2, '0')}`);
	}

	function formatUnits(value: bigint): string {
		const sign = value < 0n ? '-' : '';
		const absolute = value < 0n ? -value : value;
		const raw = absolute.toString().padStart(3, '0');
		const whole = raw.slice(0, -2) || '0';
		const fraction = raw.slice(-2);
		return `${sign}${whole}.${fraction}`;
	}

	const runningBalance = $derived.by(() => {
		let total = 0n;
		let invalid = false;
		for (const split of splits) {
			const units = decimalStringToUnits(split.amount);
			if (units === null) {
				if (split.amount.trim()) invalid = true;
				continue;
			}
			total += units;
		}
		return {
			label: formatUnits(total),
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
		<h2 id="create-policy-title" class="text-lg font-semibold">CREATE policy</h2>
		<dl class="mt-3 grid min-w-0 gap-3 sm:grid-cols-2">
			<div class="min-w-0"><dt class="font-medium">Book</dt><dd class="break-words">{selectedBook?.name ?? 'No active book'}</dd></div>
			<div class="min-w-0"><dt class="font-medium">Policy</dt><dd class="break-words">confirm_allowed depends on server policy; deployment {String(data.createSettings.deployment_writes_enabled)}, per-book {String(data.createSettings.enabled)}, effective {String(data.createSettings.effective_enabled)}</dd></div>
			<div class="min-w-0"><dt class="font-medium">Visible accounts</dt><dd>{visibleAccountCount}; full path / type / currency is shown for each selectable account.</dd></div>
			<div class="min-w-0"><dt class="font-medium">Scope</dt><dd>2..50 split rows; No transaction note field; no FX conversion; no PATCH, DELETE, batch, import, or banking action.</dd></div>
		</dl>
	</section>

	{#if errorSummary}
		<section id="transaction-create-error-summary" class="mt-6 rounded-2xl border p-4 text-sm" role="alert" tabindex="-1" style="border-color: var(--app-danger); background: var(--app-card-bg); color: var(--app-text);">
			<h2 class="font-semibold">Request failed safely</h2>
			<p class="mt-1">{errorSummary}</p>
			{#if form?.requestRef}<p class="mt-1 text-xs" style="color: var(--app-muted);">request_ref: {form.requestRef}</p>{/if}
			{#if form?.recoveryRef}<p class="mt-1 text-xs" style="color: var(--app-muted);">recovery_ref: {form.recoveryRef}</p>{/if}
		</section>
	{/if}

	<form id="transaction-create-form" method="POST" aria-describedby="create-policy-title running-balance split-editor-help transaction-create-error-summary" class="mt-6 min-w-0 space-y-5 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" data-mobile-contract="320px no horizontal overflow">
		<input type="hidden" name="book_id" value={selectedBook?.id ?? ''} />

		<div class="grid min-w-0 gap-4 sm:grid-cols-2">
			<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-date">
				Date
				<input id="transaction-date" name="date" type="date" required bind:value={date} aria-invalid={fieldErrors.date ? 'true' : undefined} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
			</label>
			<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-currency">
				Currency
				<input id="transaction-currency" name="currency" maxlength="3" pattern="[A-Za-z][A-Za-z][A-Za-z]" required bind:value={currency} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 uppercase" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
			</label>
		</div>

		<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for="transaction-description">
			Description
			<input id="transaction-description" name="description" required maxlength="256" bind:value={description} aria-invalid={fieldErrors.description ? 'true' : undefined} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" />
		</label>

		<section id="split-editor" class="min-w-0 rounded-2xl border p-4" aria-labelledby="split-editor-title" aria-describedby="split-editor-help running-balance" style="border-color: var(--app-border); background: var(--app-bg);">
			<div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
				<div class="min-w-0">
					<h2 id="split-editor-title" class="text-lg font-semibold" style="color: var(--app-text);">Split editor</h2>
					<p id="split-editor-help" class="mt-1 text-sm" style="color: var(--app-muted);">Use 2..50 split rows. Amounts are signed decimal strings and must produce Exact zero-sum before confirm.</p>
				</div>
				<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);" onclick={addSplit}>Add split</button>
			</div>

			<div id="running-balance" class="mt-4 rounded-xl border p-3 text-sm" aria-live="polite" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);">
				<p class="font-semibold">Running balance: {runningBalance.label} {draftTransaction.currency}</p>
				<p class="mt-1">{runningBalance.isZero ? t(locale, 'transactionCreate.balanceZero') : t(locale, 'transactionCreate.balanceNonZero')}</p>
			</div>

			{#if fieldErrors.splits}
				<p class="mt-3 rounded-xl border p-3 text-sm" role="alert" style="border-color: var(--app-danger); color: var(--app-text); background: var(--app-card-bg);">{message(fieldErrors.splits)}</p>
			{/if}

			<div class="mt-4 space-y-4">
				{#each splits as split, index (split.client_id)}
					{@const selectedAccount = accountById(split.account_id)}
					<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
						<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">Split {index + 1}</legend>
						<div class="grid min-w-0 gap-3 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
							<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-account-${split.client_id}`}>
								Account
								<select id={`split-account-${split.client_id}`} name="split_account_id" required bind:value={split.account_id} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);">
									<option value="">Choose account</option>
									{#each data.accounts as account (account.id)}
										<option value={account.id}>{accountLabel(account)}</option>
									{/each}
								</select>
							</label>
							<label class="block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-amount-${split.client_id}`}>
								Amount
								<input id={`split-amount-${split.client_id}`} name="split_amount" inputmode="decimal" required placeholder="-320.00" bind:value={split.amount} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" />
							</label>
						</div>
						<label class="mt-3 block min-w-0 text-sm font-medium" style="color: var(--app-text);" for={`split-memo-${split.client_id}`}>
							Split memo
							<input id={`split-memo-${split.client_id}`} name="split_memo" maxlength="512" bind:value={split.memo} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" />
						</label>
						<p class="mt-2 break-words text-xs" style="color: var(--app-muted);">Selected account: {selectedAccount ? accountLabel(selectedAccount) : 'none'}</p>
						<div class="mt-3 flex min-w-0 flex-wrap gap-2">
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-border); color: var(--app-text);" onclick={() => moveSplit(index, -1)} disabled={index === 0}>Move up</button>
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-border); color: var(--app-text);" onclick={() => moveSplit(index, 1)} disabled={index === splits.length - 1}>Move down</button>
							<button type="button" class="min-h-11 rounded-lg border px-3 py-2 text-sm" style="border-color: var(--app-danger); color: var(--app-danger);" onclick={() => removeSplit(index)} disabled={splits.length <= 2}>Remove split</button>
						</div>
					</fieldset>
				{/each}
			</div>
		</section>

		<div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<p class="text-sm" style="color: var(--app-muted);">Preview calls only the server preview endpoint. Backend policy decides confirm_allowed.</p>
			<button type="submit" formaction="?/preview" class="min-h-11 rounded-xl px-4 py-2 font-semibold text-white" style="background: var(--app-accent);">{t(locale, 'transactionCreate.previewSubmit')}</button>
		</div>
	</form>

	{#if previewIsStale}
		<section class="mt-6 rounded-2xl border p-4 text-sm" role="status" aria-live="polite" style="border-color: #f59e0b; background: #fffbeb; color: #92400e;">
			<h2 class="font-semibold">Draft changed after preview</h2>
			<p class="mt-1">{t(locale, 'transactionCreate.previewStale')}</p>
		</section>
	{/if}

	{#if preview}
		<section id="normalized-preview" class="mt-6 min-w-0 rounded-2xl border p-4" aria-labelledby="normalized-preview-title" style="border-color: var(--app-border); background: var(--app-card-bg);">
			<h2 id="normalized-preview-title" class="text-lg font-semibold" style="color: var(--app-text);">Normalized preview</h2>
			<dl class="mt-3 grid min-w-0 gap-3 text-sm sm:grid-cols-2" style="color: var(--app-text);">
				<div class="min-w-0"><dt class="font-medium">confirm_allowed</dt><dd>{String(preview.confirm_allowed)}</dd></div>
				<div class="min-w-0"><dt class="font-medium">create_count</dt><dd>{preview.create_count}</dd></div>
				<div class="min-w-0"><dt class="font-medium">expires_at</dt><dd class="break-words">{preview.expires_at}</dd></div>
				<div class="min-w-0"><dt class="font-medium">create_generation</dt><dd>{preview.create_generation}</dd></div>
				<div class="min-w-0"><dt class="font-medium">Date</dt><dd>{preview.date}</dd></div>
				<div class="min-w-0"><dt class="font-medium">Currency</dt><dd>{preview.currency}</dd></div>
				<div class="min-w-0 sm:col-span-2"><dt class="font-medium">Description</dt><dd class="break-words">{preview.description}</dd></div>
			</dl>
			<ul class="mt-4 space-y-3">
				{#each preview.splits as split (split.index)}
					<li class="min-w-0 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); color: var(--app-text);">
						<p class="font-semibold">Split {split.index + 1}: {split.amount} {preview.currency}</p>
						<p class="break-words">{split.account.full_name} / {split.account.type} / {split.account.currency}</p>
						<p class="break-words" style="color: var(--app-muted);">Memo: {split.memo || '—'}</p>
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
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">Confirm CREATE</h2>
			<p id="confirm-create-help" class="mt-1 text-sm" style="color: var(--app-muted);">Confirm reuses the same idempotency_key and preview_token. Double-submit suppression disables this button while submitting.</p>
			<button type="submit" formaction="?/confirm" disabled={confirmSubmitting} class="mt-4 min-h-11 rounded-xl px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60" style="background: var(--app-accent);">{t(locale, 'transactionCreate.confirmSubmit')}</button>
		</form>
	{:else if preview}
		<section class="mt-6 rounded-2xl border p-4 text-sm" role="status" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);">
			<h2 class="font-semibold">Confirm unavailable</h2>
			<p class="mt-1">Confirm is disabled unless confirm_allowed is true and the preview is not stale.</p>
		</section>
	{/if}

	<section class="mt-6 rounded-2xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-card-bg); color: var(--app-text);" aria-labelledby="safe-results-title">
		<h2 id="safe-results-title" class="font-semibold">Safe result states</h2>
		<p class="mt-1">created and already_created are the only success states. UI never displays backup filenames or raw backend details.</p>
		<ul class="mt-2 list-disc pl-5">
			<li>{t(locale, 'transactionCreate.success.created')}</li>
			<li>{t(locale, 'transactionCreate.success.already_created')}</li>
		</ul>
	</section>
</main>
