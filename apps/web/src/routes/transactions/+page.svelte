<script lang="ts">
	import { goto } from '$app/navigation';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import TransactionFilters from '$lib/components/TransactionFilters.svelte';
	import Pagination from '$lib/components/Pagination.svelte';

	let { data } = $props();

	const txs = $derived(data.txs);
	const limit = $derived(txs.limit);
	const offset = $derived(txs.offset);
	const total = $derived(txs.total);

	function paramsToUrl(params: {
		query?: string;
		dateFrom?: string;
		dateTo?: string;
		accountId?: string;
		offset?: number;
	}) {
		const sp = new URLSearchParams();
		if (params.query) sp.set('query', params.query);
		if (params.dateFrom) sp.set('date_from', params.dateFrom);
		if (params.dateTo) sp.set('date_to', params.dateTo);
		if (params.accountId) sp.set('account_id', params.accountId);
		sp.set('limit', String(limit));
		sp.set('offset', String(params.offset ?? 0));
		return `/transactions?${sp.toString()}`;
	}

	function handleFilter(params: { query: string; dateFrom: string; dateTo: string; accountId: string }) {
		goto(paramsToUrl({ ...params, offset: 0 }));
	}

	function handlePageChange(newOffset: number) {
		goto(
			paramsToUrl({
				query: data.filters.query,
				dateFrom: data.filters.dateFrom,
				dateTo: data.filters.dateTo,
				accountId: data.filters.accountId,
				offset: newOffset
			})
		);
	}

	function handleSelect(id: string) {
		goto(`/transactions/${encodeURIComponent(id)}`);
	}
</script>

<svelte:head>
	<title>Transactions — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Transactions</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">Browse transactions</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">Book: {data.activeBook.name}</p>
			{/if}
		</div>
		{#if data.writesEnabled}
			<a class="rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href="/transactions/new">New transaction</a>
		{/if}
	</div>

	<TransactionFilters
		query={data.filters.query}
		dateFrom={data.filters.dateFrom}
		dateTo={data.filters.dateTo}
		accountId={data.filters.accountId}
		accounts={data.accounts}
		onChange={handleFilter}
	/>

	<div class="rounded-2xl p-4" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<TransactionTable transactions={txs.items} onSelect={handleSelect} />
		<TransactionCard transactions={txs.items} onSelect={handleSelect} />
		<Pagination {offset} {limit} {total} onChange={handlePageChange} />
	</div>
</main>
