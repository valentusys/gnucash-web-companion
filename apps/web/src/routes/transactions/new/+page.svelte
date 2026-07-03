<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import type { Account } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	type PreviousPayload = {
		date?: string;
		debit_account_id?: string;
		credit_account_id?: string;
		amount?: string;
		currency?: string;
		description?: string;
		memo?: string;
	};
	type PreviewFieldErrors = Partial<Record<keyof PreviousPayload | 'book_id', string>>;

	const today = new Date().toISOString().slice(0, 10);
	const previous = $derived((form?.payload ?? {}) as PreviousPayload);
	const preview = $derived((form as any)?.preview);
	const fieldErrors = $derived(((form as any)?.fieldErrors ?? {}) as PreviewFieldErrors);
	const selectableAccounts = $derived((data.accounts as Account[]).filter((account) => !account.placeholder && !account.hidden));
	let debitAccountQuery = $state('');
	let creditAccountQuery = $state('');
	let selectedDebitAccountId = $state('');
	let selectedCreditAccountId = $state('');
	let clientAccountError = $state('');
	const currentDebitAccountId = $derived(selectedDebitAccountId || previous.debit_account_id || '');
	const currentCreditAccountId = $derived(selectedCreditAccountId || previous.credit_account_id || '');
	const sameAccountError = $derived(
		currentDebitAccountId && currentCreditAccountId && currentDebitAccountId === currentCreditAccountId
			? 'Source and destination accounts must be different. No write was executed.'
			: ''
	);
	const debitAccountError = $derived(clientAccountError || sameAccountError || fieldErrors.debit_account_id || '');
	const creditAccountError = $derived(clientAccountError || sameAccountError || fieldErrors.credit_account_id || '');
	const dateError = $derived(fieldErrors.date ?? '');
	const amountError = $derived(fieldErrors.amount ?? '');
	const currencyError = $derived(fieldErrors.currency ?? '');
	const descriptionError = $derived(fieldErrors.description ?? '');
	const memoError = $derived(fieldErrors.memo ?? '');
	const selectedDebitAccount = $derived(selectableAccounts.find((account) => account.id === currentDebitAccountId));
	const selectedCreditAccount = $derived(selectableAccounts.find((account) => account.id === currentCreditAccountId));

	function normalizeAccountSearch(value: string): string {
		return value.trim().toLowerCase();
	}

	function accountMatches(account: Account, query: string): boolean {
		const normalizedQuery = normalizeAccountSearch(query);
		if (!normalizedQuery) return true;
		return [account.full_name, account.name, account.type, account.currency]
			.filter(Boolean)
			.some((value) => String(value).toLowerCase().includes(normalizedQuery));
	}

	function filteredAccounts(query: string, selectedAccountId: string): Account[] {
		const matches = selectableAccounts.filter((account) => accountMatches(account, query));
		const selected = selectableAccounts.find((account) => account.id === selectedAccountId);
		if (selected && !matches.some((account) => account.id === selected.id)) {
			return [selected, ...matches];
		}
		return matches;
	}

	const debitAccountOptions = $derived(filteredAccounts(debitAccountQuery, currentDebitAccountId));
	const creditAccountOptions = $derived(filteredAccounts(creditAccountQuery, currentCreditAccountId));

	function handleDebitAccountChange(event: Event) {
		selectedDebitAccountId = (event.currentTarget as HTMLSelectElement).value;
		clientAccountError = '';
	}

	function handleCreditAccountChange(event: Event) {
		selectedCreditAccountId = (event.currentTarget as HTMLSelectElement).value;
		clientAccountError = '';
	}

	function handlePreviewSubmit(event: SubmitEvent) {
		const formElement = event.currentTarget as HTMLFormElement;
		const formData = new FormData(formElement);
		const debitAccountId = String(formData.get('debit_account_id') ?? '');
		const creditAccountId = String(formData.get('credit_account_id') ?? '');
		if (debitAccountId && creditAccountId && debitAccountId === creditAccountId) {
			event.preventDefault();
			clientAccountError = 'Source and destination accounts must be different. No write was executed.';
			return;
		}
		clientAccountError = '';
	}
</script>

<svelte:head>
	<title>Preview transaction — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">Transaction entry preview</h1>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">
				Owner-only browser/mobile form for validating one future CREATE. This slice is preview only; no write is executed.
			</p>
		</div>
		<a class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions">Back</a>
	</div>

	{#if form?.error}
		<div class="mb-4 rounded-2xl p-4 text-sm" role="alert" aria-live="assertive" style="border: 1px solid #fecaca; background: #fef2f2; color: #991b1b;">
			<p class="font-semibold">Preview validation failed safely</p>
			<p class="mt-1">{form.error}</p>
			<p class="mt-1 font-semibold">No CREATE/PATCH/DELETE/batch executed.</p>
			<p class="mt-1">Review the highlighted fields below. Raw private paths, secrets, and runtime internals are not shown.</p>
		</div>
	{/if}

	<div class="mb-4 rounded-2xl p-4 text-sm" role="status" style="border: 1px solid #93c5fd; background: #eff6ff; color: #1e3a8a;">
		<p class="font-semibold">Preview only / no write executed</p>
		<p class="mt-1">
			This page calls only POST /books/&lbrace;book_id&rbrace;/transactions/create-preview, a non-mutating backend preview endpoint.
			No CREATE, PATCH, DELETE, or batch operation is executed. A future CREATE still requires fresh owner approval,
			exact CREATE count, enabled write gates, backup/read-back/audit/reset/probes, and private verification.
		</p>
	</div>

	<div class="mb-4">
		<WriteModeWarning {locale} compact />
	</div>

	<form method="POST" onsubmit={handlePreviewSubmit} class="space-y-5 rounded-2xl p-5" style="background: var(--app-panel); border: 1px solid var(--app-border); box-shadow: 0 1px 3px var(--app-panel-shadow);">
		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Book
			<select name="book_id" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
				{#each data.books as book}
					<option value={book.id} selected={book.id === data.activeBook?.id}>{book.name}</option>
				{/each}
			</select>
		</label>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Date
				<input name="date" type="date" required value={previous.date ?? today} aria-invalid={dateError ? 'true' : undefined} aria-describedby={dateError ? 'preview-date-error' : undefined} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				{#if dateError}
					<p id="preview-date-error" class="mt-1 text-xs" style="color: #dc2626;">{dateError}</p>
				{/if}
			</label>
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Currency
				<input name="currency" maxlength="3" required value={previous.currency ?? data.activeBook?.base_currency ?? 'SEK'} aria-invalid={currencyError ? 'true' : undefined} aria-describedby={currencyError ? 'preview-currency-error' : undefined} class="mt-1 w-full rounded-xl px-3 py-2 uppercase" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				{#if currencyError}
					<p id="preview-currency-error" class="mt-1 text-xs" style="color: #dc2626;">{currencyError}</p>
				{/if}
			</label>
		</div>

		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Description
			<input name="description" required value={previous.description ?? ''} aria-invalid={descriptionError ? 'true' : undefined} aria-describedby={descriptionError ? 'preview-description-error' : undefined} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			{#if descriptionError}
				<p id="preview-description-error" class="mt-1 text-xs" style="color: #dc2626;">{descriptionError}</p>
			{/if}
		</label>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Amount
				<input name="amount" inputmode="decimal" required placeholder="320.00" value={previous.amount ?? ''} aria-invalid={amountError ? 'true' : undefined} aria-describedby={amountError ? 'preview-amount-error' : undefined} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				{#if amountError}
					<p id="preview-amount-error" class="mt-1 text-xs" style="color: #dc2626;">{amountError}</p>
				{/if}
			</label>
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Memo (optional)
				<input name="memo" placeholder="Optional metadata only" value={previous.memo ?? ''} aria-invalid={memoError ? 'true' : undefined} aria-describedby={memoError ? 'preview-memo-error' : undefined} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				{#if memoError}
					<p id="preview-memo-error" class="mt-1 text-xs" style="color: #dc2626;">{memoError}</p>
				{/if}
			</label>
		</div>

		<section class="rounded-2xl border p-4" aria-labelledby="account-selector-title" style="border-color: var(--app-border); background: var(--app-bg);">
			<div class="mb-4">
				<h2 id="account-selector-title" class="text-base font-semibold" style="color: var(--app-text);">Account selectors</h2>
				<p class="mt-1 text-xs" style="color: var(--app-muted);">
					Search filters the account list by full account path, account name, type, or currency. The submitted value remains the selected account id; free-text is never submitted as the final account reference. Placeholder/hidden accounts are excluded.
				</p>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div>
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="debit-account-search">Search source account</label>
					<input id="debit-account-search" data-account-filter="debit" type="search" bind:value={debitAccountQuery} autocomplete="off" placeholder="Filter by full account path" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="debit-account-select">Debit/source account</label>
					<select id="debit-account-select" name="debit_account_id" required value={currentDebitAccountId} onchange={handleDebitAccountChange} aria-invalid={debitAccountError ? 'true' : undefined} aria-describedby="debit-account-help debit-account-selected debit-account-error" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select source account</option>
						{#each debitAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentDebitAccountId} disabled={Boolean(currentCreditAccountId && account.id === currentCreditAccountId && account.id !== currentDebitAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="debit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Source must be a selectable account and cannot match destination.</p>
					<p id="debit-account-selected" class="mt-1 text-xs" style="color: var(--app-muted);">Selected source: {selectedDebitAccount?.full_name ?? 'none'}</p>
					{#if debitAccountError}
						<p id="debit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{debitAccountError}</p>
					{/if}
				</div>

				<div>
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="credit-account-search">Search destination account</label>
					<input id="credit-account-search" data-account-filter="credit" type="search" bind:value={creditAccountQuery} autocomplete="off" placeholder="Filter by full account path" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="credit-account-select">Credit/destination account</label>
					<select id="credit-account-select" name="credit_account_id" required value={currentCreditAccountId} onchange={handleCreditAccountChange} aria-invalid={creditAccountError ? 'true' : undefined} aria-describedby="credit-account-help credit-account-selected credit-account-error" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select destination account</option>
						{#each creditAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentCreditAccountId} disabled={Boolean(currentDebitAccountId && account.id === currentDebitAccountId && account.id !== currentCreditAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="credit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Destination must be a selectable account and cannot match source.</p>
					<p id="credit-account-selected" class="mt-1 text-xs" style="color: var(--app-muted);">Selected destination: {selectedCreditAccount?.full_name ?? 'none'}</p>
					{#if creditAccountError}
						<p id="credit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{creditAccountError}</p>
					{/if}
				</div>
			</div>
		</section>

		<div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
			<p class="text-sm" style="color: var(--app-muted);">Create/Submit mutation action is intentionally disabled in this preview slice.</p>
			<div class="flex flex-col gap-3 sm:flex-row">
				<button formaction="?/preview" formnovalidate class="rounded-xl px-4 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit">Preview transaction</button>
				<button class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled>Create disabled</button>
			</div>
		</div>
	</form>

	{#if preview}
		<section class="mt-6 rounded-2xl p-5" aria-label="Transaction preview" style="background: var(--app-panel); border: 1px solid var(--app-border);">
			<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
				<div>
					<h2 class="text-xl font-semibold" style="color: var(--app-text);">Normalized preview</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">Preview only / no write executed. Create remains disabled in this slice.</p>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" style="background: #dcfce7; color: #166534;">no mutation</span>
			</div>

			<dl class="mt-4 grid gap-3 md:grid-cols-2">
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">preview_only</dt><dd style="color: var(--app-text);">{String(preview.preview_only)}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">create_count</dt><dd style="color: var(--app-text);">{preview.create_count}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd style="color: var(--app-text);">{preview.date}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount + currency</dt><dd style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Source/debit account</dt><dd style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Destination/credit account</dt><dd style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd style="color: var(--app-text);">{preview.description}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
			</dl>
			<p class="mt-4 text-sm font-semibold" style="color: #92400e;">Create remains disabled in this slice.</p>

			{#if preview.warnings?.length}
				<ul class="mt-4 list-disc pl-5 text-sm" style="color: #92400e;">
					{#each preview.warnings as warning}
						<li>{warning}</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/if}
</main>
