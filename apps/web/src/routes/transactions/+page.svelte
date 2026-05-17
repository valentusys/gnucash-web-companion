<script lang="ts">
	import { goto } from '$app/navigation';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import TransactionFilters from '$lib/components/TransactionFilters.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

		let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	const txs = $derived(data.txs);
	const limit = $derived(txs.limit);
	const offset = $derived(txs.offset);
	const total = $derived(txs.total);

	const exportCsvUrl = $derived.by(() => {
		const bookId = data.activeBook?.id;
		if (!bookId) return '#';
		const sp = new URLSearchParams();
		if (data.filters.query) sp.set('query', data.filters.query);
		if (data.filters.dateFrom) sp.set('date_from', data.filters.dateFrom);
		if (data.filters.dateTo) sp.set('date_to', data.filters.dateTo);
		if (data.filters.accountId) sp.set('account_id', data.filters.accountId);
		if (data.filters.minAmount) sp.set('min_amount', data.filters.minAmount);
		if (data.filters.maxAmount) sp.set('max_amount', data.filters.maxAmount);
		const qs = sp.toString();
		return `/books/${bookId}/transactions/export${qs ? '?' + qs : ''}`;
	});

	const activeFilterCount = $derived(
		[
			data.filters.query,
			data.filters.dateFrom,
			data.filters.dateTo,
			data.filters.accountId,
			data.filters.minAmount,
			data.filters.maxAmount
		].filter(Boolean).length
	);
	const csvStatus = $derived(
		activeFilterCount
			? `Exports current filtered view, capped at 10,000 rows.`
			: 'Exports this read-only transaction list, capped at 10,000 rows.'
	);

	function paramsToUrl(params: {
		query?: string;
		dateFrom?: string;
		dateTo?: string;
		accountId?: string;
		minAmount?: string;
		maxAmount?: string;
		offset?: number;
	}) {
		const sp = new URLSearchParams();
		if (params.query) sp.set('query', params.query);
		if (params.dateFrom) sp.set('date_from', params.dateFrom);
		if (params.dateTo) sp.set('date_to', params.dateTo);
		if (params.accountId) sp.set('account_id', params.accountId);
		if (params.minAmount) sp.set('min_amount', params.minAmount);
		if (params.maxAmount) sp.set('max_amount', params.maxAmount);
		sp.set('limit', String(limit));
		sp.set('offset', String(params.offset ?? 0));
		return `/transactions?${sp.toString()}`;
	}

	function handleFilter(params: {
		query: string;
		dateFrom: string;
		dateTo: string;
		accountId: string;
		minAmount: string;
		maxAmount: string;
	}) {
		goto(paramsToUrl({ ...params, offset: 0 }));
	}

	function handlePageChange(newOffset: number) {
		goto(
			paramsToUrl({
				query: data.filters.query,
				dateFrom: data.filters.dateFrom,
				dateTo: data.filters.dateTo,
				accountId: data.filters.accountId,
				minAmount: data.filters.minAmount,
				maxAmount: data.filters.maxAmount,
				offset: newOffset
			})
		);
	}

	function handleSelect(id: string) {
		goto(`/transactions/${encodeURIComponent(id)}`);
	}
</script>

<svelte:head>
	<title>{t(locale, 'transactions.kicker')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'transactions.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'transactions.title')}</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">Book: {data.activeBook.name}</p>
			{/if}
		</div>
		<div class="flex flex-col gap-2 md:items-end">
			{#if data.activeBook}
				<a
					class="rounded-xl px-4 py-2 text-center text-sm font-semibold"
					style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);"
					href={exportCsvUrl}
					aria-describedby="csv-export-status"
					>Export CSV{#if activeFilterCount} ({activeFilterCount} filter{activeFilterCount === 1 ? '' : 's'}){/if}</a
				>
				<p id="csv-export-status" class="max-w-xs text-xs" style="color: var(--app-muted);">{csvStatus}</p>
			{/if}
			{#if data.writesEnabled}
				<div class="max-w-sm space-y-2">
					<p class="text-xs font-semibold" style="color: #b45309;">
						Experimental post-MVP write mode is enabled. MVP v0.1 remains read-only by default; use only disposable/test copies with backups.
					</p>
					<a class="inline-flex rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href="/transactions/new">New transaction</a>
				</div>
			{/if}
		</div>
	</div>

	{#if data.writesEnabled}
		<div class="mb-6">
			<WriteModeWarning compact />
		</div>
	{/if}

	<TransactionFilters
		query={data.filters.query}
		dateFrom={data.filters.dateFrom}
		dateTo={data.filters.dateTo}
		accountId={data.filters.accountId}
		minAmount={data.filters.minAmount}
		maxAmount={data.filters.maxAmount}
		accounts={data.accounts}
		onChange={handleFilter}
	/>

	<div class="rounded-2xl p-4" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<TransactionTable transactions={txs.items} onSelect={handleSelect} />
		<TransactionCard transactions={txs.items} onSelect={handleSelect} />
		<Pagination {offset} {limit} {total} onChange={handlePageChange} />
	</div>
</main>
