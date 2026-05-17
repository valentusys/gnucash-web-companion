<script lang="ts">
	import type { Account } from '$lib/api/types';

	let {
		query,
		dateFrom,
		dateTo,
		accountId = '',
		minAmount = '',
		maxAmount = '',
		accounts = [],
		onChange
	}: {
		query: string;
		dateFrom: string;
		dateTo: string;
		accountId?: string;
		minAmount?: string;
		maxAmount?: string;
		accounts?: Account[];
		onChange: (params: {
			query: string;
			dateFrom: string;
			dateTo: string;
			accountId: string;
			minAmount: string;
			maxAmount: string;
		}) => void;
	} = $props();

	let dateError = $state('');
	let amountError = $state('');
	const hasActiveFilters = $derived(
		Boolean(query || dateFrom || dateTo || accountId || minAmount || maxAmount)
	);

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
		if (min && max && Number(min) > Number(max)) {
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
			maxAmount: nextMaxAmount
		});
	}

	function handleReset() {
		dateError = '';
		amountError = '';
		onChange({ query: '', dateFrom: '', dateTo: '', accountId: '', minAmount: '', maxAmount: '' });
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
	</div>
	<div class="flex-1">
		<label for="tx-query" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Search</label>
		<input
			id="tx-query"
			name="query"
			type="text"
			value={query}
			placeholder="Description..."
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
	</div>
	<div>
		<label for="tx-account" class="block text-xs font-semibold uppercase" style="color: var(--app-muted);">Account</label>
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
	</div>
	<div>
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
		<button
			type="button"
			class="rounded-lg border px-4 py-2 text-sm font-medium transition-colors hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50"
			style="border-color: var(--app-border); color: var(--app-text);"
			onclick={handleReset}
			disabled={!hasActiveFilters}
			aria-label="Reset all transaction filters"
		>
			Reset filters
		</button>
	</div>
</form>
