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
	class="mb-4 flex flex-col gap-3 rounded-xl p-4 sm:flex-row sm:items-end"
	style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
	onsubmit={handleSubmit}
>
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
			class="mt-1 block w-full rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		/>
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
			class="rounded-lg border px-4 py-2 text-sm font-medium transition-colors hover:opacity-80"
			style="border-color: var(--app-border); color: var(--app-text);"
			onclick={handleReset}
		>
			Reset
		</button>
	</div>
</form>
