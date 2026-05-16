<script lang="ts">
	import type { Account } from '$lib/api/types';

	let {
		query,
		dateFrom,
		dateTo,
		accountId = '',
		accounts = [],
		onChange
	}: {
		query: string;
		dateFrom: string;
		dateTo: string;
		accountId?: string;
		accounts?: Account[];
		onChange: (params: { query: string; dateFrom: string; dateTo: string; accountId: string }) => void;
	} = $props();

	function handleSubmit(e: Event) {
		e.preventDefault();
		const form = e.currentTarget as HTMLFormElement;
		const data = new FormData(form);
		onChange({
			query: String(data.get('query') ?? ''),
			dateFrom: String(data.get('date_from') ?? ''),
			dateTo: String(data.get('date_to') ?? ''),
			accountId: String(data.get('account_id') ?? '')
		});
	}

	function handleReset() {
		onChange({ query: '', dateFrom: '', dateTo: '', accountId: '' });
	}
</script>

<form
	class="mb-4 flex flex-col gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-200 sm:flex-row sm:items-end"
	onsubmit={handleSubmit}
>
	<div class="flex-1">
		<label for="tx-query" class="block text-xs font-semibold uppercase text-gray-500">Search</label>
		<input
			id="tx-query"
			name="query"
			type="text"
			value={query}
			placeholder="Description..."
			class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
		/>
	</div>
	<div>
		<label for="tx-account" class="block text-xs font-semibold uppercase text-gray-500">Account</label>
		<select
			id="tx-account"
			name="account_id"
			class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
		>
			<option value="" selected={!accountId}>All accounts</option>
			{#each accounts as account (account.id)}
				<option value={account.id} selected={accountId === account.id}>{account.full_name}</option>
			{/each}
		</select>
	</div>
	<div>
		<label for="tx-date-from" class="block text-xs font-semibold uppercase text-gray-500">From</label>
		<input
			id="tx-date-from"
			name="date_from"
			type="date"
			value={dateFrom}
			class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
		/>
	</div>
	<div>
		<label for="tx-date-to" class="block text-xs font-semibold uppercase text-gray-500">To</label>
		<input
			id="tx-date-to"
			name="date_to"
			type="date"
			value={dateTo}
			class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
		/>
	</div>
	<div class="flex gap-2">
		<button
			type="submit"
			class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
		>
			Filter
		</button>
		<button
			type="button"
			class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
			onclick={handleReset}
		>
			Reset
		</button>
	</div>
</form>
