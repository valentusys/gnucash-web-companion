<script lang="ts">
	import { goto } from '$app/navigation';
	import AccountBalance from '$lib/components/AccountBalance.svelte';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import TransactionFilters from '$lib/components/TransactionFilters.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	const account = $derived(data.account);
	const txs = $derived(data.txs);
	const limit = $derived(txs.limit);
	const offset = $derived(txs.offset);
	const total = $derived(txs.total);
	const accountPath = $derived.by(() =>
		account.full_name
			.split(':')
			.map((part: string) => part.trim())
			.filter(Boolean)
	);

	const activeFilterCount = $derived(
		[
			data.filters.query,
			data.filters.dateFrom,
			data.filters.dateTo,
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
	const accountExportButtonLabel = $derived(
		activeFilterCount
			? t(locale, 'transactions.export.accountButtonWithFilters')
					.replace('{count}', String(activeFilterCount))
					.replace('{filterLabel}', filterLabel)
			: t(locale, 'transactions.export.accountButton')
	);
	const accountCsvReliabilityStatus = $derived(
		total === 0
			? t(locale, 'transactions.export.emptyStatus')
			: total > 10000
				? t(locale, 'transactions.export.truncatedStatus').replace('{total}', String(total))
				: t(locale, 'transactions.export.countStatus').replace('{total}', String(total))
	);
	const exportCsvUrl = $derived.by(() => {
		const bookId = data.activeBook?.id;
		if (!bookId) return '#';
		const sp = new URLSearchParams({ account_id: account.id });
		if (data.filters.query) sp.set('query', data.filters.query);
		if (data.filters.dateFrom) sp.set('date_from', data.filters.dateFrom);
		if (data.filters.dateTo) sp.set('date_to', data.filters.dateTo);
		if (data.filters.minAmount) sp.set('min_amount', data.filters.minAmount);
		if (data.filters.maxAmount) sp.set('max_amount', data.filters.maxAmount);
		if (data.filters.transactionState) sp.set('transaction_state', data.filters.transactionState);
		return `/books/${bookId}/transactions/export?${sp.toString()}`;
	});
	const transactionStatus = $derived(
		activeFilterCount
			? `${txs.total} transaction${txs.total !== 1 ? 's' : ''} match the active filters for this account.`
			: `${txs.total} transaction${txs.total !== 1 ? 's' : ''} for this account.`
	);

	function paramsToUrl(params: {
		query?: string;
		dateFrom?: string;
		dateTo?: string;
		minAmount?: string;
		maxAmount?: string;
		transactionState?: string;
		offset?: number;
	}) {
		const sp = new URLSearchParams();
		if (params.query) sp.set('query', params.query);
		if (params.dateFrom) sp.set('date_from', params.dateFrom);
		if (params.dateTo) sp.set('date_to', params.dateTo);
		if (params.minAmount) sp.set('min_amount', params.minAmount);
		if (params.maxAmount) sp.set('max_amount', params.maxAmount);
		if (params.transactionState) sp.set('transaction_state', params.transactionState);
		sp.set('limit', String(limit));
		sp.set('offset', String(params.offset ?? 0));
		return `/accounts/${encodeURIComponent(account.id)}?${sp.toString()}`;
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

	function handleSelect(id: string) {
		goto(`/transactions/${encodeURIComponent(id)}`);
	}

	function handlePageChange(newOffset: number) {
		goto(
			paramsToUrl({
				query: data.filters.query,
				dateFrom: data.filters.dateFrom,
				dateTo: data.filters.dateTo,
				minAmount: data.filters.minAmount,
				maxAmount: data.filters.maxAmount,
				transactionState: data.filters.transactionState,
				offset: newOffset
			})
		);
	}
</script>

<svelte:head>
	<title>{account.name} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<nav class="text-sm font-medium" aria-label="Account breadcrumb">
		<ol class="flex flex-wrap items-center gap-2">
			<li><a href="/accounts" class="hover:underline" style="color: var(--app-accent);">Accounts</a></li>
			{#each accountPath as part, index}
				<li aria-hidden="true" style="color: var(--app-muted);">/</li>
				<li style={index === accountPath.length - 1 ? 'color: var(--app-text);' : 'color: var(--app-muted);'} aria-current={index === accountPath.length - 1 ? 'page' : undefined}>{part}</li>
			{/each}
		</ol>
	</nav>

	<section class="mt-4 rounded-2xl p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Account detail</p>
				<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{account.name}</h1>
				<p class="mt-2 break-words" style="color: var(--app-muted);">{account.full_name}</p>
			</div>
			<div class="rounded-xl px-4 py-3 text-right" style="background-color: var(--app-elevated-bg);">
				<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">Balance</p>
				<p class="mt-1 text-xl"><AccountBalance balance={account.balance} currency={account.currency} /></p>
			</div>
		</div>

		<dl class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Type</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.type}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Currency</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.currency}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Placeholder</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.placeholder ? 'Yes' : 'No'}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Hidden</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.hidden ? 'Yes' : 'No'}</dd>
			</div>
		</dl>
	</section>

	<section class="mt-6 rounded-2xl p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">Transactions</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{transactionStatus}</p>
				{#if activeFilterCount && txs.total === 0}
					<p class="mt-1 text-sm" style="color: var(--app-muted);">
						No transactions match these filters for this account. Clear filters to return to the full read-only account transaction list.
					</p>
				{/if}
			</div>
			{#if data.activeBook}
				<div class="flex flex-col gap-1 md:items-end">
					<a
						class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-center text-sm font-semibold"
						style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);"
						href={exportCsvUrl}
						aria-describedby="account-csv-export-status account-csv-export-reliability-status"
						>{accountExportButtonLabel}</a
					>
					<p id="account-csv-export-status" class="max-w-xs text-xs" style="color: var(--app-muted);">
						{t(locale, 'transactions.export.accountStatus')}
					</p>
					<p id="account-csv-export-reliability-status" class="max-w-xs text-xs" style="color: var(--app-muted);">
						{accountCsvReliabilityStatus}
					</p>
				</div>
			{/if}
		</div>

		<div class="mt-4">
			<TransactionFilters
				query={data.filters.query}
				dateFrom={data.filters.dateFrom}
				dateTo={data.filters.dateTo}
				accountId={account.id}
				minAmount={data.filters.minAmount}
				maxAmount={data.filters.maxAmount}
				transactionState={data.filters.transactionState}
				datePresets={data.datePresets}
				clearFiltersHref={data.clearFiltersHref}
				lockedAccountLabel={account.full_name}
				{locale}
				onChange={handleFilter}
			/>
			<TransactionTable transactions={txs.items} onSelect={handleSelect} />
			<TransactionCard transactions={txs.items} onSelect={handleSelect} />
			<Pagination {offset} {limit} {total} onChange={handlePageChange} />
		</div>
	</section>
</main>
