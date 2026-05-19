<script lang="ts">
	import { navigating } from '$app/state';
	import { goto } from '$app/navigation';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import TransactionFilters from '$lib/components/TransactionFilters.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	const txs = $derived(data.txs);
	const limit = $derived(txs.limit);
	const offset = $derived(txs.offset);
	const total = $derived(txs.total);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/transactions');

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
		if (data.filters.transactionState) sp.set('transaction_state', data.filters.transactionState);
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
			data.filters.maxAmount,
			data.filters.transactionState
		].filter(Boolean).length
	);
	const filterLabel = $derived(
		locale === 'ru'
			? activeFilterCount === 1
				? 'фильтр'
				: activeFilterCount > 1 && activeFilterCount < 5
					? 'фильтра'
					: 'фильтров'
			: activeFilterCount === 1
				? 'filter'
				: 'filters'
	);
	const exportButtonLabel = $derived(
		activeFilterCount
			? t(locale, 'transactions.export.buttonWithFilters')
					.replace('{count}', String(activeFilterCount))
					.replace('{filterLabel}', filterLabel)
			: t(locale, 'transactions.export.button')
	);
	const csvStatus = $derived(
		activeFilterCount
			? t(locale, 'transactions.export.statusFiltered')
			: t(locale, 'transactions.export.statusUnfiltered')
	);
	const pageStart = $derived(total > 0 ? offset + 1 : 0);
	const pageEnd = $derived(Math.min(offset + txs.items.length, total));
	const pageRangeStatus = $derived(
		txs.items.length
			? t(locale, 'transactions.listStatus.pageRange')
					.replace('{start}', String(pageStart))
					.replace('{end}', String(pageEnd))
					.replace('{total}', String(total))
			: t(locale, 'transactions.listStatus.emptyPage')
	);
	const filterParityStatus = $derived(
		activeFilterCount
			? t(locale, 'transactions.listStatus.filtersApplied')
					.replace('{count}', String(activeFilterCount))
					.replace('{filterLabel}', filterLabel)
			: t(locale, 'transactions.listStatus.noFilters')
	);
	const hasActiveFilters = $derived(activeFilterCount > 0);
	const emptyTitle = $derived(
		hasActiveFilters ? 'No transactions match the current filters' : 'No transactions yet'
	);
	const emptyMessage = $derived(
		hasActiveFilters
			? 'The read-only API returned no transactions for this filter combination. Clear filters or broaden the search/date/account/amount/state criteria.'
			: 'The selected read-only book has no transactions available through the current adapter. Review the book in GnuCash Desktop or choose another accessible book.'
	);

	function paramsToUrl(params: {
		query?: string;
		dateFrom?: string;
		dateTo?: string;
		accountId?: string;
		minAmount?: string;
		maxAmount?: string;
		transactionState?: string;
		offset?: number;
	}) {
		const sp = new URLSearchParams();
		if (params.query) sp.set('query', params.query);
		if (params.dateFrom) sp.set('date_from', params.dateFrom);
		if (params.dateTo) sp.set('date_to', params.dateTo);
		if (params.accountId) sp.set('account_id', params.accountId);
		if (params.minAmount) sp.set('min_amount', params.minAmount);
		if (params.maxAmount) sp.set('max_amount', params.maxAmount);
		if (params.transactionState) sp.set('transaction_state', params.transactionState);
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
		transactionState: string;
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
				transactionState: data.filters.transactionState,
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
					>{exportButtonLabel}</a
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

	{#if isRouteLoading}
		<LoadingState variant="transactions" message="Loading transactions for the selected read-only book…" />
	{:else}
		<TransactionFilters
			query={data.filters.query}
			dateFrom={data.filters.dateFrom}
			dateTo={data.filters.dateTo}
			accountId={data.filters.accountId}
			minAmount={data.filters.minAmount}
			maxAmount={data.filters.maxAmount}
			transactionState={data.filters.transactionState}
			accounts={data.accounts}
			datePresets={data.datePresets}
			clearFiltersHref={data.clearFiltersHref}
			{locale}
			onChange={handleFilter}
		/>

		<section
			class="mb-4 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel);"
			aria-label={t(locale, 'transactions.listStatus.title')}
		>
			<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div>
					<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.listStatus.title')}</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">{pageRangeStatus}</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.listStatus.order')}</p>
				</div>
				<div class="max-w-xl text-xs" style="color: var(--app-muted);">
					<p>{filterParityStatus}</p>
					<p class="mt-1">{t(locale, 'transactions.listStatus.exportParity')}</p>
				</div>
			</div>
		</section>

		<div class="rounded-2xl p-4" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
			{#if txs.items.length}
				<TransactionTable transactions={txs.items} onSelect={handleSelect} />
				<TransactionCard transactions={txs.items} onSelect={handleSelect} />
				<Pagination {offset} {limit} {total} onChange={handlePageChange} />
			{:else}
				<EmptyState title={emptyTitle} message={emptyMessage} ariaLabel={emptyTitle} icon="🔎">
					{#if hasActiveFilters}
						<a
							href={data.clearFiltersHref}
							class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
							style="background-color: var(--app-accent);"
						>
							Clear filters
						</a>
					{/if}
					<a
						href="/books"
						class="rounded-xl border px-4 py-2 text-sm font-semibold"
						style="border-color: var(--app-border); color: var(--app-text);"
					>
						Review books
					</a>
				</EmptyState>
			{/if}
		</div>
	{/if}
</main>
