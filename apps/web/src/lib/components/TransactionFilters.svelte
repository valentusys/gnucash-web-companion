<script lang="ts">
	import type { Account } from '$lib/api/types';
	import { compareDecimalStrings } from '$lib/money.js';

	let {
		query,
		dateFrom,
		dateTo,
		accountId = '',
		minAmount = '',
		maxAmount = '',
		transactionState = '',
		accounts = [],
		datePresets = [],
		clearFiltersHref = '/transactions?limit=50&offset=0',
		lockedAccountLabel = '',
		onChange
	}: {
		query: string;
		dateFrom: string;
		dateTo: string;
		accountId?: string;
		minAmount?: string;
		maxAmount?: string;
		transactionState?: string;
		accounts?: Account[];
		datePresets?: { label: string; href: string; active: boolean }[];
		clearFiltersHref?: string;
		lockedAccountLabel?: string;
		onChange: (params: {
			query: string;
			dateFrom: string;
			dateTo: string;
			accountId: string;
			minAmount: string;
			maxAmount: string;
			transactionState: string;
		}) => void;
	} = $props();

	let dateError = $state('');
	let amountError = $state('');
	const hasActiveFilters = $derived(
		Boolean(query || dateFrom || dateTo || (!lockedAccountLabel && accountId) || minAmount || maxAmount || transactionState)
	);
	const activeFilterSummary = $derived.by(() => {
		const filters: string[] = [];
		const selectedAccount = accounts.find((account) => account.id === accountId);

		if (query) filters.push(`Search: ${query}`);
		if (lockedAccountLabel) filters.push(`Account scope: ${lockedAccountLabel}`);
		else if (selectedAccount) filters.push(`Account: ${selectedAccount.full_name}`);
		else if (accountId) filters.push(`Account ID: ${accountId}`);
		if (dateFrom && dateTo) filters.push(`Dates: ${dateFrom} to ${dateTo}`);
		else if (dateFrom) filters.push(`From: ${dateFrom}`);
		else if (dateTo) filters.push(`To: ${dateTo}`);
		if (minAmount && maxAmount) filters.push(`Amount: ${minAmount} to ${maxAmount}`);
		else if (minAmount) filters.push(`Min amount: ${minAmount}`);
		else if (maxAmount) filters.push(`Max amount: ${maxAmount}`);
		if (transactionState) filters.push(`State: ${transactionState}`);

		return filters;
	});

	function normalizeDecimal(value: FormDataEntryValue | null): string {
		return String(value ?? '').trim();
	}

	function validateDateRange(from: string, to: string): string {
		if (from && to && from > to) {
			return 'Start date must be earlier than or equal to end date.';
		}
		return '';
	}

	function validateAmountRange(min: string, max: string): string {
		if (min && max && compareDecimalStrings(min, max) > 0) {
			return 'Minimum amount must be less than or equal to maximum amount.';
		}
		return '';
	}

	function handleSubmit(e: Event) {
		e.preventDefault();
		const form = e.currentTarget as HTMLFormElement;
		if (!form.reportValidity()) return;
		const data = new FormData(form);
		const nextDateFrom = String(data.get('date_from') ?? '');
		const nextDateTo = String(data.get('date_to') ?? '');
		const nextMinAmount = normalizeDecimal(data.get('min_amount'));
		const nextMaxAmount = normalizeDecimal(data.get('max_amount'));
		dateError = validateDateRange(nextDateFrom, nextDateTo);
		amountError = validateAmountRange(nextMinAmount, nextMaxAmount);
		if (dateError || amountError) return;
		onChange({
			query: String(data.get('query') ?? ''),
			dateFrom: nextDateFrom,
			dateTo: nextDateTo,
			accountId: String(data.get('account_id') ?? ''),
			minAmount: nextMinAmount,
			maxAmount: nextMaxAmount,
			transactionState: String(data.get('transaction_state') ?? '')
		});
	}
</script>

<form
	class="mb-4 flex flex-col gap-3 rounded-xl p-4 sm:flex-row sm:flex-wrap sm:items-end"
	style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
	onsubmit={handleSubmit}
>
	<div class="basis-full">
		<div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<p class="text-sm font-semibold" style="color: var(--app-text);">Transaction filters</p>
				<p class="text-xs" style="color: var(--app-muted);">
					Narrow the read-only transaction list and CSV export; filters never modify your GnuCash book.
				</p>
			</div>
			{#if hasActiveFilters}
				<p class="text-xs font-medium" style="color: var(--app-accent);">Filtered view</p>
			{/if}
		</div>
		{#if datePresets.length}
			<div class="mt-3">
				<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">Date presets</p>
				<div class="mt-2 flex flex-wrap gap-2" aria-label="Transaction date range presets">
					{#each datePresets as preset}
						<a
							href={preset.href}
							class="rounded-full border px-3 py-1.5 text-xs font-semibold"
							style={preset.active
								? 'border-color: var(--app-accent); color: var(--app-accent); background: var(--app-bg);'
								: 'border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);'}
							aria-label={`Apply transaction date preset: ${preset.label}`}
							aria-current={preset.active ? 'true' : undefined}
						>
							{preset.label}
						</a>
					{/each}
				</div>
				<p class="mt-2 text-xs" style="color: var(--app-muted);">
					Presets update only the ordinary date_from/date_to filters; the list and CSV export stay read-only and use the same filtered view.
				</p>
			</div>
		{/if}
		{#if activeFilterSummary.length}
			<div
				class="mt-3 rounded-lg border px-3 py-2"
				style="border-color: var(--app-border); background: var(--app-bg);"
				aria-live="polite"
			>
				<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">
					Active filters applied to list and CSV export
				</p>
				<ul class="mt-2 flex flex-wrap gap-2" aria-label="Active transaction filters">
					{#each activeFilterSummary as filter}
						<li
							class="rounded-full border px-2.5 py-1 text-xs font-medium"
							style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);"
						>
							{filter}
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>
	<div class="flex-1">
		<label for="tx-query" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Search</label>
		<input
			id="tx-query"
			name="query"
			type="text"
			value={query}
			placeholder="Description or split memo..."
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
	</div>
	<div>
		<label for="tx-account" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Account</label>
		{#if lockedAccountLabel}
			<input id="tx-account" type="hidden" name="account_id" value={accountId} />
			<p
				class="mt-1 rounded-lg border px-3 py-2 text-sm"
				style="border-color: var(--app-input-border); background-color: var(--app-elevated-bg); color: var(--app-text);"
			>
				{lockedAccountLabel}
			</p>
			<p class="mt-1 max-w-xs text-xs" style="color: var(--app-muted);">
				This account detail view is fixed to this account; other filters narrow only this account's transactions.
			</p>
		{:else}
			<select
				id="tx-account"
				name="account_id"
				class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
				style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
			>
				<option value="" selected={!accountId}>All accounts</option>
				{#each accounts as account (account.id)}
					<option value={account.id} selected={accountId === account.id}>{account.full_name}</option>
				{/each}
			</select>
		{/if}
	</div>
	<div>
		<p class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Custom date range</p>
		<label for="tx-date-from" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">From</label>
		<input
			id="tx-date-from"
			name="date_from"
			type="date"
			value={dateFrom}
			aria-invalid={dateError ? 'true' : undefined}
			aria-describedby={dateError ? 'tx-date-error' : undefined}
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
	</div>
	<div>
		<label for="tx-date-to" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">To</label>
		<input
			id="tx-date-to"
			name="date_to"
			type="date"
			value={dateTo}
			aria-invalid={dateError ? 'true' : undefined}
			aria-describedby={dateError ? 'tx-date-error' : undefined}
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
		{#if dateError}
			<p id="tx-date-error" class="mt-1 text-xs" style="color: #dc2626;">{dateError}</p>
		{/if}
	</div>

	<div>
		<label for="tx-state" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">State</label>
		<select
			id="tx-state"
			name="transaction_state"
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
			aria-describedby="tx-state-help"
		>
			<option value="" selected={!transactionState}>Any state</option>
			<option value="unreconciled" selected={transactionState === 'unreconciled'}>Unreconciled</option>
			<option value="cleared" selected={transactionState === 'cleared'}>Cleared</option>
			<option value="reconciled" selected={transactionState === 'reconciled'}>Reconciled</option>
			<option value="voided" selected={transactionState === 'voided'}>Voided</option>
		</select>
		<p id="tx-state-help" class="mt-1 max-w-xs text-xs" style="color: var(--app-muted);">Filters by the GnuCash split reconciliation state; it does not edit transactions.</p>
	</div>
	<div>
		<label for="tx-min-amount" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Min amount</label>
		<input
			id="tx-min-amount"
			name="min_amount"
			type="number"
			step="any"
			inputmode="decimal"
			value={minAmount}
			placeholder="0.00"
			aria-invalid={amountError ? 'true' : undefined}
			aria-describedby={amountError ? 'tx-amount-error' : undefined}
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
	</div>
	<div>
		<label for="tx-max-amount" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Max amount</label>
		<input
			id="tx-max-amount"
			name="max_amount"
			type="number"
			step="any"
			inputmode="decimal"
			value={maxAmount}
			placeholder="1000.00"
			aria-invalid={amountError ? 'true' : undefined}
			aria-describedby={amountError ? 'tx-amount-error' : undefined}
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
		{#if amountError}
			<p id="tx-amount-error" class="mt-1 text-xs" style="color: #dc2626;">{amountError}</p>
		{/if}
	</div>
	<div class="flex gap-2">
		<button
			type="submit"
			class="rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors hover:opacity-90"
			style="background-color: var(--app-accent);"
		>
			Filter
		</button>
		<a
			class="rounded-lg border px-4 py-2 text-sm font-medium transition-colors hover:opacity-80"
			style={hasActiveFilters
				? 'border-color: var(--app-border); color: var(--app-text);'
				: 'border-color: var(--app-border); color: var(--app-muted); pointer-events: none; opacity: 0.5;'}
			href={clearFiltersHref}
			aria-disabled={!hasActiveFilters ? 'true' : undefined}
		>
			Clear filters
		</a>
	</div>
</form>
