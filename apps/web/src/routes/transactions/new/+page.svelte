<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import type { Account, Book } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	type PreviousPayload = {
		book_id?: string;
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
	const currentBookId = $derived(previous.book_id || String(data.activeBook?.id ?? ''));
	const selectedBook = $derived((data.books as Book[]).find((book) => String(book.id) === currentBookId) ?? data.activeBook);
	const selectableAccounts = $derived((data.accounts as Account[]).filter((account) => !account.placeholder && !account.hidden));
	let debitAccountQuery = $state('');
	let creditAccountQuery = $state('');
	let selectedDebitAccountId = $state('');
	let selectedCreditAccountId = $state('');
	let clientAccountError = $state('');
	let draftChangedAfterPreview = $state(false);
	let previewReviewed = $state(false);
	let approvalTemplateCopied = $state(false);
	const safeApprovalTemplate = `Owner approval request (redacted template)
Target book: <selected book in web UI>
CREATE count: 1
Source/debit account: <selected source account>
Destination/credit account: <selected destination account>
Amount/currency: <amount and currency>
Date: <YYYY-MM-DD>
Description: <description>
Memo: <memo or empty>
Safety checklist: preview reviewed; no stale preview; writes explicitly approved in same context with exact count; backup/read-back/audit/reset/probes required; no DELETE or batch.`;
	const currentDebitAccountId = $derived(selectedDebitAccountId || previous.debit_account_id || '');
	const currentCreditAccountId = $derived(selectedCreditAccountId || previous.credit_account_id || '');
	const previewIsStale = $derived(Boolean(preview) && draftChangedAfterPreview);
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
	const bookError = $derived(fieldErrors.book_id ?? '');
	const descriptionError = $derived(fieldErrors.description ?? '');
	const memoError = $derived(fieldErrors.memo ?? '');
	const selectedDebitAccount = $derived(selectableAccounts.find((account) => account.id === currentDebitAccountId));
	const selectedCreditAccount = $derived(selectableAccounts.find((account) => account.id === currentCreditAccountId));
	const noSelectableAccounts = $derived(selectableAccounts.length === 0);

	function describedBy(...ids: Array<string | false | null | undefined>): string | undefined {
		const value = ids.filter(Boolean).join(' ');
		return value || undefined;
	}

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

	function handleDraftChange() {
		if (!preview) return;
		draftChangedAfterPreview = true;
		previewReviewed = false;
		approvalTemplateCopied = false;
	}

	async function copySafeApprovalTemplate() {
		if (typeof navigator === 'undefined' || !navigator.clipboard) {
			approvalTemplateCopied = false;
			return;
		}
		try {
			await navigator.clipboard.writeText(safeApprovalTemplate);
			approvalTemplateCopied = true;
		} catch {
			approvalTemplateCopied = false;
		}
	}

	function handlePreviewSubmit(event: SubmitEvent) {
		const formElement = event.currentTarget as HTMLFormElement;
		const formData = new FormData(formElement);
		const debitAccountId = String(formData.get('debit_account_id') ?? '');
		const creditAccountId = String(formData.get('credit_account_id') ?? '');
		if (debitAccountId && creditAccountId && debitAccountId === creditAccountId) {
			event.preventDefault();
			clientAccountError = 'Source and destination accounts must be different. No write was executed.';
			handleDraftChange();
			return;
		}
		clientAccountError = '';
		draftChangedAfterPreview = false;
		previewReviewed = false;
		approvalTemplateCopied = false;
	}
</script>

<svelte:head>
	<title>Preview transaction — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl min-w-0 px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div class="min-w-0">
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">Transaction entry preview</h1>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">
				Owner-only browser/mobile form for validating one future CREATE. This slice is preview only; no write is executed.
			</p>
		</div>
		<a class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions">Back</a>
	</div>

	{#if form?.error}
		<div id="preview-error-summary" class="mb-4 rounded-2xl p-4 text-sm" role="alert" aria-live="assertive" aria-labelledby="preview-error-summary-title" style="border: 1px solid #fecaca; background: #fef2f2; color: #991b1b;">
			<p id="preview-error-summary-title" class="font-semibold">Preview validation failed safely</p>
			<p class="mt-1">{form.error}</p>
			<p class="mt-1 font-semibold">No CREATE/PATCH/DELETE/batch executed.</p>
			<p class="mt-1">Review the highlighted fields below. Raw private paths, secrets, and runtime internals are not shown.</p>
		</div>
	{/if}

	<div id="preview-no-write-warning" class="mb-4 rounded-2xl p-4 text-sm" role="status" aria-labelledby="preview-no-write-title" style="border: 1px solid #93c5fd; background: #eff6ff; color: #1e3a8a;">
		<p id="preview-no-write-title" class="font-semibold">Preview only / no write executed</p>
		<p class="mt-1">
			This page calls only POST /books/&lbrace;book_id&rbrace;/transactions/create-preview, a non-mutating backend preview endpoint.
			No CREATE, PATCH, DELETE, or batch operation is executed. A future CREATE still requires fresh owner approval,
			exact CREATE count, enabled write gates, backup/read-back/audit/reset/probes, and private verification.
		</p>
	</div>

	<div class="mb-4">
		<WriteModeWarning {locale} compact />
	</div>

	<form method="POST" onsubmit={handlePreviewSubmit} oninput={handleDraftChange} onchange={handleDraftChange} aria-describedby={describedBy('preview-no-write-warning', 'preview-create-disabled-explanation', form?.error && 'preview-error-summary')} class="min-w-0 space-y-5 rounded-2xl p-5" style="background: var(--app-panel); border: 1px solid var(--app-border); box-shadow: 0 1px 3px var(--app-panel-shadow);">
		<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
			<label for="preview-book">Book</label>
			<select id="preview-book" name="book_id" aria-invalid={bookError ? 'true' : undefined} aria-describedby={describedBy('book-help', 'preview-no-write-warning', bookError && 'preview-book-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
				{#each data.books as book}
					<option value={book.id} selected={String(book.id) === currentBookId}>{book.name}</option>
				{/each}
			</select>
			<p id="book-help" class="mt-1 text-xs" style="color: var(--app-muted);">Select the book context for this non-mutating preview only.</p>
			{#if bookError}
				<p id="preview-book-error" class="mt-1 text-xs" style="color: #dc2626;">{bookError}</p>
			{/if}
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-date">Date</label>
				<input id="preview-date" name="date" type="date" required value={previous.date ?? today} aria-invalid={dateError ? 'true' : undefined} aria-describedby={describedBy('date-help', dateError && 'preview-date-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="date-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use an explicit calendar date; the preview validates the submitted date before any future approval step.</p>
				{#if dateError}
					<p id="preview-date-error" class="mt-1 text-xs" style="color: #dc2626;">{dateError}</p>
				{/if}
			</div>
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-currency">Currency</label>
				<input id="preview-currency" name="currency" maxlength="3" pattern="[A-Za-z]{3}" autocomplete="off" spellcheck="false" required value={previous.currency ?? data.activeBook?.base_currency ?? 'SEK'} aria-invalid={currencyError ? 'true' : undefined} aria-describedby={describedBy('currency-help', currencyError && 'preview-currency-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2 uppercase" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="currency-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use a three-letter currency code; no currency conversion is performed.</p>
				{#if currencyError}
					<p id="preview-currency-error" class="mt-1 text-xs" style="color: #dc2626;">{currencyError}</p>
				{/if}
			</div>
		</div>

		<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
			<label for="preview-description">Description</label>
			<input id="preview-description" name="description" required value={previous.description ?? ''} aria-invalid={descriptionError ? 'true' : undefined} aria-describedby={describedBy('description-help', descriptionError && 'preview-description-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			<p id="description-help" class="mt-1 text-xs" style="color: var(--app-muted);">Required local description for the normalized preview; tracked/GitHub reports must remain redacted.</p>
			{#if descriptionError}
				<p id="preview-description-error" class="mt-1 text-xs" style="color: #dc2626;">{descriptionError}</p>
			{/if}
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-amount">Amount</label>
				<input id="preview-amount" name="amount" type="text" inputmode="decimal" pattern="[0-9]+(\.[0-9]+)?" required placeholder="320.00" value={previous.amount ?? ''} aria-invalid={amountError ? 'true' : undefined} aria-describedby={describedBy('amount-help', amountError && 'preview-amount-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="amount-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use a positive decimal string such as 320.00; zero is rejected by preview validation.</p>
				{#if amountError}
					<p id="preview-amount-error" class="mt-1 text-xs" style="color: #dc2626;">{amountError}</p>
				{/if}
			</div>
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-memo">Memo (optional)</label>
				<input id="preview-memo" name="memo" placeholder="Optional metadata only" value={previous.memo ?? ''} aria-invalid={memoError ? 'true' : undefined} aria-describedby={describedBy('memo-help', memoError && 'preview-memo-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="memo-help" class="mt-1 text-xs" style="color: var(--app-muted);">Optional metadata shown in preview only; this slice does not write it.</p>
				{#if memoError}
					<p id="preview-memo-error" class="mt-1 text-xs" style="color: #dc2626;">{memoError}</p>
				{/if}
			</div>
		</div>

		<section class="min-w-0 rounded-2xl border p-4" aria-labelledby="account-selector-title" aria-describedby="account-selector-help preview-no-write-warning" style="border-color: var(--app-border); background: var(--app-bg);">
			<div class="mb-4">
				<h2 id="account-selector-title" class="text-base font-semibold" style="color: var(--app-text);">Account selectors</h2>
				<p id="account-selector-help" class="mt-1 text-xs" style="color: var(--app-muted);">
					Search filters the account list by full account path, account name, type, or currency. The submitted value remains the selected account id; free-text is never submitted as the final account reference. Placeholder/hidden accounts are excluded.
				</p>
				{#if noSelectableAccounts}
					<p id="no-selectable-accounts-warning" class="mt-2 rounded-xl p-3 text-xs" role="status" style="border: 1px solid #fde68a; background: #fffbeb; color: #92400e;">
						No selectable accounts are available for this book. Choose another book or add non-placeholder accounts in GnuCash Desktop, then run preview again. No write was executed.
					</p>
				{/if}
			</div>

			<div class="grid min-w-0 gap-4 md:grid-cols-2">
				<div class="min-w-0">
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="debit-account-search">Search source account</label>
					<input id="debit-account-search" data-account-filter="debit" type="search" bind:value={debitAccountQuery} autocomplete="off" aria-describedby="debit-account-search-help debit-account-count account-selector-help" placeholder="Filter by full account path" class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<p id="debit-account-search-help" class="mt-1 text-xs" style="color: var(--app-muted);">Filters visible source accounts only; it is not submitted as account text.</p>
					<p id="debit-account-count" class="mt-1 text-xs" style="color: var(--app-muted);">Showing {debitAccountOptions.length} of {selectableAccounts.length} visible selectable accounts.</p>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="debit-account-select">Debit/source account</label>
					<select id="debit-account-select" name="debit_account_id" required value={currentDebitAccountId} onchange={handleDebitAccountChange} aria-invalid={debitAccountError ? 'true' : undefined} aria-describedby={describedBy('debit-account-help', 'debit-account-count', 'debit-account-selected', 'preview-no-write-warning', debitAccountError && 'debit-account-error')} class="mt-1 w-full min-w-0 max-w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select source account</option>
						{#each debitAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentDebitAccountId} disabled={Boolean(currentCreditAccountId && account.id === currentCreditAccountId && account.id !== currentDebitAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="debit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Source must be a selectable account and cannot match destination.</p>
					<p id="debit-account-selected" class="mt-1 break-words text-xs" style="color: var(--app-muted);">
						Selected source: {selectedDebitAccount?.full_name ?? 'none'}{#if selectedDebitAccount} · account type {selectedDebitAccount?.type} · {selectedDebitAccount?.currency}{/if}
					</p>
					{#if debitAccountError}
						<p id="debit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{debitAccountError}</p>
					{/if}
				</div>

				<div class="min-w-0">
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="credit-account-search">Search destination account</label>
					<input id="credit-account-search" data-account-filter="credit" type="search" bind:value={creditAccountQuery} autocomplete="off" aria-describedby="credit-account-search-help credit-account-count account-selector-help" placeholder="Filter by full account path" class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<p id="credit-account-search-help" class="mt-1 text-xs" style="color: var(--app-muted);">Filters visible destination accounts only; it is not submitted as account text.</p>
					<p id="credit-account-count" class="mt-1 text-xs" style="color: var(--app-muted);">Showing {creditAccountOptions.length} of {selectableAccounts.length} visible selectable accounts.</p>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="credit-account-select">Credit/destination account</label>
					<select id="credit-account-select" name="credit_account_id" required value={currentCreditAccountId} onchange={handleCreditAccountChange} aria-invalid={creditAccountError ? 'true' : undefined} aria-describedby={describedBy('credit-account-help', 'credit-account-count', 'credit-account-selected', 'preview-no-write-warning', creditAccountError && 'credit-account-error')} class="mt-1 w-full min-w-0 max-w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select destination account</option>
						{#each creditAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentCreditAccountId} disabled={Boolean(currentDebitAccountId && account.id === currentDebitAccountId && account.id !== currentCreditAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="credit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Destination must be a selectable account and cannot match source.</p>
					<p id="credit-account-selected" class="mt-1 break-words text-xs" style="color: var(--app-muted);">
						Selected destination: {selectedCreditAccount?.full_name ?? 'none'}{#if selectedCreditAccount} · account type {selectedCreditAccount?.type} · {selectedCreditAccount?.currency}{/if}
					</p>
					{#if creditAccountError}
						<p id="credit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{creditAccountError}</p>
					{/if}
				</div>
			</div>
		</section>

		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between">
			<p id="preview-create-disabled-explanation" class="text-sm" style="color: var(--app-muted);">Create/Submit mutation action is intentionally disabled in this preview slice; only the preview action is available.</p>
			<div class="flex min-w-0 flex-col gap-3 sm:flex-row">
				<button formaction="?/preview" formnovalidate class="rounded-xl px-4 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit">Preview transaction</button>
				<button class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled aria-describedby="preview-create-disabled-explanation preview-no-write-warning">Create disabled</button>
			</div>
		</div>
	</form>

	{#if previewIsStale}
		<div id="preview-stale-warning" class="mt-6 rounded-2xl p-4 text-sm" role="status" aria-live="polite" style="border: 1px solid #f59e0b; background: #fffbeb; color: #92400e;">
			<p class="font-semibold">Draft changed after preview</p>
			<p class="mt-1">
				Run Preview transaction again before any future approval step. The previous preview remains visible for comparison,
				but it is stale and cannot support a future owner-approved CREATE. No write was executed.
			</p>
		</div>
	{/if}

	{#if preview}
		<section class="mt-6 min-w-0 rounded-2xl p-5" aria-label="Transaction preview" aria-describedby={describedBy('preview-create-disabled-explanation', 'preview-no-write-warning', previewIsStale && 'preview-stale-warning')} style="background: var(--app-panel); border: 1px solid var(--app-border);">
			<div class="flex min-w-0 flex-col gap-2 md:flex-row md:items-start md:justify-between">
				<div class="min-w-0">
					<h2 class="text-xl font-semibold" style="color: var(--app-text);">Normalized preview</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">Preview only / no write executed. Create remains disabled in this slice.</p>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" style="background: #dcfce7; color: #166534;">no mutation</span>
			</div>

			<section id="preview-confirmation-shell" class="mt-4 min-w-0 rounded-2xl border p-4" aria-labelledby="preview-confirmation-shell-title" aria-describedby="preview-confirmation-shell-help preview-create-disabled-explanation" style="border-color: var(--app-border); background: var(--app-bg);">
				<div class="flex min-w-0 flex-col gap-4 md:flex-row md:items-start md:justify-between">
					<div class="min-w-0">
						<h3 id="preview-confirmation-shell-title" class="text-base font-semibold" style="color: var(--app-text);">Future confirmation shell</h3>
						<p id="preview-confirmation-shell-help" class="mt-1 text-sm" style="color: var(--app-muted);">
							Ready for future owner-approved CREATE review after fresh same-context approval only. This shell is local and non-mutating;
							the final Create control remains disabled in this slice.
						</p>
					</div>
					<a id="clear-preview-link" class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions/new">Clear preview / start over</a>
				</div>
				<div class="mt-4 flex min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between">
					<label class="flex min-w-0 items-start gap-2 text-sm" style="color: var(--app-text);" for="preview-reviewed-confirmation">
						<input id="preview-reviewed-confirmation" type="checkbox" bind:checked={previewReviewed} disabled={previewIsStale} aria-describedby="preview-reviewed-status preview-confirmation-shell-help" class="mt-1" />
						<span>I reviewed this local preview; no write is available from this checkbox.</span>
					</label>
					<button id="future-create-disabled" class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled aria-describedby="preview-create-disabled-explanation preview-no-write-warning preview-reviewed-status">Future Create disabled</button>
				</div>
				<p id="preview-reviewed-status" class="mt-3 text-sm" style="color: var(--app-muted);">
					{#if previewIsStale}
						Preview is stale because the draft changed. Run Preview transaction again before any future approval step.
					{:else if previewReviewed}
						Preview reviewed locally. Future owner-approved CREATE still requires a fresh approval prompt, enabled write gates, exact count, backup/read-back/audit/reset/probes, and private verification.
					{:else}
						Review the normalized fields below. Future CREATE remains disabled and cannot be executed from this page state.
					{/if}
				</p>
			</section>

			<section id="approval-packet" class="mt-4 min-w-0 rounded-2xl border p-4" aria-labelledby="approval-packet-title" aria-describedby="approval-packet-help approval-packet-copy-note preview-create-disabled-explanation" style="border-color: var(--app-border); background: var(--app-bg);">
				<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
					<div class="min-w-0">
						<h3 id="approval-packet-title" class="text-base font-semibold" style="color: var(--app-text);">Approval packet (no-write)</h3>
						<p id="approval-packet-help" class="mt-1 text-sm" style="color: var(--app-muted);">
							This panel shows exactly what a future same-context owner-approved CREATE would need. It is review-only;
							no approval is recorded, no write path exists here, and Future Create remains disabled.
						</p>
					</div>
					<button id="copy-approval-template" class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="button" onclick={copySafeApprovalTemplate} aria-describedby="approval-packet-copy-note">
						Copy redacted approval template
					</button>
				</div>
				<dl class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Target book</dt><dd class="break-words" style="color: var(--app-text);">{selectedBook?.name ?? 'selected book'}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Future CREATE count</dt><dd class="break-words" style="color: var(--app-text);">1</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Source/debit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Destination/credit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount/currency</dt><dd class="break-words" style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd class="break-words" style="color: var(--app-text);">{preview.date}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd class="break-words" style="color: var(--app-text);">{preview.description}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd class="break-words" style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
				</dl>
				<div class="mt-4 rounded-xl p-3 text-sm" style="border: 1px solid #fde68a; background: #fffbeb; color: #92400e;">
					<p class="font-semibold">Safety checklist before any future CREATE</p>
					<ul id="approval-packet-safety-checklist" class="mt-2 list-disc pl-5">
						<li>Fresh same-context owner approval with exact CREATE count = 1.</li>
						<li>Preview must be current, reviewed, and not stale.</li>
						<li>Write gates must be explicitly enabled only for an approved run; defaults stay disabled.</li>
						<li>Backup, read-back, audit, reset, and disabled-write probes are required for any future mutation.</li>
						<li>DELETE, batch, and balance-affecting PATCH remain forbidden.</li>
					</ul>
				</div>
				<p id="approval-packet-copy-note" class="mt-3 text-sm" style="color: var(--app-muted);">
					{#if approvalTemplateCopied}
						Redacted placeholder template copied. Fill private details only in an owner-private context, not GitHub or tracked reports.
					{:else}
						The copy button uses placeholders only; it does not copy account names, description, memo, amount, GUIDs, book paths, screenshots, or secrets.
					{/if}
				</p>
				<pre class="mt-3 max-w-full overflow-x-auto whitespace-pre-wrap rounded-xl p-3 text-xs" style="background: var(--app-panel); color: var(--app-muted); border: 1px solid var(--app-border);">{safeApprovalTemplate}</pre>
			</section>

			<dl class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">preview_only</dt><dd class="break-words" style="color: var(--app-text);">{String(preview.preview_only)}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">create_count</dt><dd class="break-words" style="color: var(--app-text);">{preview.create_count}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd class="break-words" style="color: var(--app-text);">{preview.date}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount + currency</dt><dd class="break-words" style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Source/debit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Destination/credit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd class="break-words" style="color: var(--app-text);">{preview.description}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd class="break-words" style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
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
