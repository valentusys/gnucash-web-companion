<script lang="ts">
	import { navigating } from '$app/state';
	import { goto } from '$app/navigation';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import TransactionFilters from '$lib/components/TransactionFilters.svelte';
	import TransactionExplorerFilters from '$lib/components/TransactionExplorerFilters.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	// The server loader intentionally returns legacy and explorer shapes during URL migration.
	// Keep the page template flexible while static/browser tests pin the public contract.
	let { data }: { data: any } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	const txs = $derived(data.txs);
	const isLegacy = $derived(data.mode === 'legacy');
	const isExplorer = $derived(data.mode === 'explorer');
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/transactions');

	const legacyLimit = $derived(isLegacy ? txs.limit : 50);
	const legacyOffset = $derived(isLegacy ? txs.offset : 0);
	const legacyTotal = $derived(isLegacy ? txs.total : 0);

	const activeFilterCount = $derived.by(() => {
		if (isLegacy) {
			return [
				data.filters.query,
				data.filters.dateFrom,
				data.filters.dateTo,
				data.filters.accountId,
				data.filters.minAmount,
				data.filters.maxAmount,
				data.filters.transactionState
			].filter(Boolean).length;
		}
		return (data.activeFilters ?? []).filter((chip: { key: string }) => chip.key !== 'cursor').length;
	});
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
		data.exportCsv?.enabled
			? activeFilterCount
				? t(locale, 'transactions.export.statusFiltered')
				: t(locale, 'transactions.export.statusUnfiltered')
			: (data.exportCsv?.reason ?? t(locale, 'transactions.export.explorerDisabled'))
	);
	const csvReliabilityStatus = $derived.by(() => {
		if (!data.exportCsv?.enabled) return t(locale, 'transactions.export.explorerHonesty');
		if (!isLegacy) return t(locale, 'transactions.export.explorerHonesty');
		if (legacyTotal === 0) return t(locale, 'transactions.export.emptyStatus');
		if (legacyTotal > 10000) return t(locale, 'transactions.export.truncatedStatus').replace('{total}', String(legacyTotal));
		return t(locale, 'transactions.export.countStatus').replace('{total}', String(legacyTotal));
	});
	const pageRangeStatus = $derived.by(() => {
		if (isLegacy) {
			const pageStart = legacyTotal > 0 ? legacyOffset + 1 : 0;
			const pageEnd = Math.min(legacyOffset + txs.items.length, legacyTotal);
			return txs.items.length
				? t(locale, 'transactions.listStatus.pageRange')
						.replace('{start}', String(pageStart))
						.replace('{end}', String(pageEnd))
						.replace('{total}', String(legacyTotal))
				: t(locale, 'transactions.listStatus.emptyPage');
		}
		return txs.items.length
			? t(locale, 'transactions.explorer.returnedStatus')
					.replace('{count}', String(txs.returned_count ?? txs.items.length))
					.replace('{pageSize}', String(txs.page_size ?? data.filters.pageSize))
			: data.status?.message;
	});
	const filterParityStatus = $derived(
		isLegacy
			? activeFilterCount
				? t(locale, 'transactions.listStatus.filtersApplied')
						.replace('{count}', String(activeFilterCount))
						.replace('{filterLabel}', filterLabel)
				: t(locale, 'transactions.listStatus.noFilters')
			: activeFilterCount
				? t(locale, 'transactions.explorer.filtersApplied')
						.replace('{count}', String(activeFilterCount))
						.replace('{filterLabel}', filterLabel)
				: t(locale, 'transactions.explorer.noFilters')
	);
	const writeAlphaOwnedVisibleCount = $derived(txs.items.filter((tx: { is_write_alpha_owned?: boolean }) => tx.is_write_alpha_owned).length);
	const writeAlphaHistoryHint = $derived(
		t(locale, 'transactions.listStatus.writeAlphaHint').replace('{count}', String(writeAlphaOwnedVisibleCount))
	);
	const hasActiveFilters = $derived(activeFilterCount > 0);
	const emptyTitle = $derived(isExplorer ? data.status?.title : hasActiveFilters ? 'No transactions match the current filters' : 'No transactions yet');
	const emptyMessage = $derived(
		isExplorer
			? data.status?.message
			: hasActiveFilters
				? 'The read-only API returned no transactions for this filter combination. Clear filters or broaden the search/date/account/amount/state criteria.'
				: 'The selected read-only book has no transactions available through the current adapter. Review the book in GnuCash Desktop or choose another accessible book.'
	);
	const detailHref = (id: string) => data.detailHrefs?.[id] ?? `/transactions/${encodeURIComponent(id)}`;

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
		sp.set('limit', String(legacyLimit));
		sp.set('offset', String(params.offset ?? 0));
		return `/transactions?${sp.toString()}`;
	}

	function handleLegacyFilter(params: {
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

	function handleLegacyPageChange(newOffset: number) {
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
		goto(detailHref(id));
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
					class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-center text-sm font-semibold"
					style="background: var(--app-accent); color: white;"
					href="/transactions/new"
					>Preview new transaction (no write)</a
				>
				<p class="max-w-xs text-xs" style="color: var(--app-muted);">
					Available while writes are disabled; opens the preview-only form. No CREATE/PATCH/DELETE/batch action is available.
				</p>
				{#if data.exportCsv?.enabled}
					<a
						class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-center text-sm font-semibold"
						style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);"
						href={data.exportCsv.href}
						aria-describedby="csv-export-status csv-export-reliability-status"
						>{exportButtonLabel}</a
					>
				{:else}
					<span
						class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-center text-sm font-semibold opacity-70"
						style="background: var(--app-panel); color: var(--app-muted); border: 1px solid var(--app-border);"
						aria-disabled="true"
						aria-describedby="csv-export-status csv-export-reliability-status"
						>{exportButtonLabel}</span
					>
				{/if}
				<p id="csv-export-status" class="max-w-xs text-xs" style="color: var(--app-muted);">{csvStatus}</p>
				<p id="csv-export-reliability-status" class="max-w-xs text-xs" style="color: var(--app-muted);">{csvReliabilityStatus}</p>
			{/if}
			{#if data.writesEnabled}
				<div class="max-w-sm space-y-2">
					<p class="text-xs font-semibold" style="color: #b45309;">
						Experimental post-MVP write mode is enabled. MVP v0.1 remains read-only by default; continue only in APP_ENV=test with an ignored disposable copy, backups, audit, and lock-release evidence.
					</p>
					<a class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href="/transactions/new">Preview transaction form</a>
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
		{#if isLegacy}
			<section class="mb-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);" role="status">
				{data.legacyNotice}
			</section>
			<TransactionFilters
				query={data.filters.query}
				dateFrom={data.filters.dateFrom}
				dateTo={data.filters.dateTo}
				accountId={data.filters.accountId}
				minAmount={data.filters.minAmount}
				maxAmount={data.filters.maxAmount}
				transactionState={data.filters.transactionState}
				accounts={data.accounts}
				accountOptionsAvailable={data.accountOptionsAvailable}
				datePresets={data.datePresets}
				clearFiltersHref={data.clearFiltersHref}
				{locale}
				onChange={handleLegacyFilter}
			/>
		{:else}
			<TransactionExplorerFilters
				filters={data.filters}
				accounts={data.accountOptions}
				accountOptionsAvailable={data.accountOptionsAvailable}
				accountOptionsLimited={data.accountOptionsLimited}
				datePresets={data.datePresets}
				activeFilters={data.activeFilters}
				resetHref={data.resetHref}
				pageSizeOptions={data.pageSizeOptions}
				{locale}
			/>
		{/if}

		{#if !data.accountOptionsAvailable || data.accountOptionsPartialFailure}
			<section
				id="transactions-account-options-status"
				class="mb-4 rounded-xl border p-4 text-sm"
				style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);"
				role={data.accountOptionsAvailable ? 'status' : 'alert'}
			>
				<p class="font-semibold">
					{data.accountOptionsAvailable
						? locale === 'ru' ? 'Список вариантов счетов ограничен' : 'Account choices are partially limited'
						: locale === 'ru' ? 'Фильтры по счетам временно недоступны' : 'Account-specific filters are temporarily unavailable'}
				</p>
				<p class="mt-1">
					{locale === 'ru'
						? 'Данные Transaction Explorer остаются доступны. Фильтры type, dates, state и search продолжают работать.'
						: 'Transaction Explorer data remains available. Type, date, state, and search filters continue to work.'}
				</p>
				<a class="mt-3 inline-flex min-h-11 items-center rounded-xl border px-4 py-2 font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href="/diagnostics">
					{locale === 'ru' ? 'Открыть redacted diagnostics' : 'Open redacted diagnostics'}
				</a>
			</section>
		{/if}

		<section
			class="mb-4 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel);"
			aria-label={t(locale, 'transactions.listStatus.title')}
		>
			<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div>
					<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.listStatus.title')}</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">{pageRangeStatus}</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">
						{isLegacy ? t(locale, 'transactions.listStatus.order') : t(locale, 'transactions.explorer.order', { sort: data.filters.sort ?? 'date_desc' })}
					</p>
				</div>
				<div class="max-w-xl text-xs" style="color: var(--app-muted);">
					<p>{filterParityStatus}</p>
					<p class="mt-1">{isLegacy ? t(locale, 'transactions.listStatus.exportParity') : t(locale, 'transactions.explorer.noTotal')}</p>
					{#if isExplorer && data.txs.limitations?.length}
						<p class="mt-2 font-semibold">{t(locale, 'transactions.explorer.limitationsTitle')}</p>
						<ul class="mt-1 list-disc pl-5">
							{#each data.txs.limitations as limitation}
								<li>{limitation}</li>
							{/each}
						</ul>
					{/if}
					{#if writeAlphaOwnedVisibleCount > 0}
						<p id="write-alpha-history-hint" class="mt-1 font-semibold" style="color: #92400e;">{writeAlphaHistoryHint}</p>
						<section
							id="write-alpha-history-followup"
							class="mt-3 rounded-xl px-3 py-2"
							style="background: #fffbeb; border: 1px solid #fcd34d; color: #92400e;"
							aria-labelledby="write-alpha-history-followup-title"
						>
							<p id="write-alpha-history-followup-title" class="font-semibold">{t(locale, 'transactions.listStatus.writeAlphaFollowupTitle')}</p>
							<p class="mt-1">{t(locale, 'transactions.listStatus.writeAlphaFollowupHelp')}</p>
							<a class="mt-2 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 font-semibold" style="border-color: #f59e0b; color: #92400e;" href="/books/write-alpha-audit">
								{t(locale, 'transactions.listStatus.writeAlphaAuditLink')}
							</a>
						</section>
					{/if}
				</div>
			</div>
		</section>

		{#if isExplorer && data.status && data.status.kind !== 'ok'}
			<section
				class="mb-4 rounded-xl border p-4 text-sm"
				style={data.status.role === 'alert'
					? 'border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-text);'
					: 'border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);'}
				role={data.status.role}
				aria-live={data.status.role === 'alert' ? 'assertive' : 'polite'}
			>
				<p class="font-semibold">{data.status.title}</p>
				<p class="mt-1">{data.status.message}</p>
				<div class="mt-3 flex flex-wrap gap-2">
					<a class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.resetPaginationHref}>{t(locale, 'transactions.explorer.resetPagination')}</a>
					<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetHref}>{t(locale, 'transactions.explorer.reset')}</a>
				</div>
			</section>
		{/if}

		<div class="rounded-2xl p-4" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
			{#if txs.items.length}
				<TransactionTable transactions={txs.items} onSelect={handleSelect} detailHref={detailHref} {locale} />
				<TransactionCard transactions={txs.items} onSelect={handleSelect} detailHref={detailHref} {locale} />
				{#if isLegacy}
					<Pagination offset={legacyOffset} limit={legacyLimit} total={legacyTotal} onChange={handleLegacyPageChange} />
				{:else}
					<nav class="flex flex-col gap-3 py-3 sm:flex-row sm:items-center sm:justify-between" aria-label={t(locale, 'transactions.explorer.paginationLabel')}>
						<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.cursorPagination')}</p>
						<div class="flex flex-wrap gap-2">
							{#if data.pagination?.previousHref}
								<a class="inline-flex min-h-11 items-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.pagination.previousHref}>{t(locale, 'transactions.explorer.previous')}</a>
							{/if}
							{#if data.pagination?.nextHref}
								<a class="inline-flex min-h-11 items-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.pagination.nextHref}>{t(locale, 'transactions.explorer.next')}</a>
							{/if}
							{#if data.pagination?.continueHref}
								<a class="inline-flex min-h-11 items-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.pagination.continueHref}>{t(locale, 'transactions.explorer.continue')}</a>
							{/if}
						</div>
					</nav>
				{/if}
			{:else}
				<EmptyState title={emptyTitle} message={emptyMessage} ariaLabel={emptyTitle} icon="🔎" role={isExplorer && data.status?.role === 'alert' ? 'alert' : 'status'}>
					{#if isLegacy && hasActiveFilters}
						<a
							href={data.clearFiltersHref}
							class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white"
							style="background-color: var(--app-accent);"
						>
							Clear filters
						</a>
					{/if}
					{#if isExplorer}
						<a
							href={data.resetPaginationHref}
							class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white"
							style="background-color: var(--app-accent);"
						>
							{t(locale, 'transactions.explorer.resetPagination')}
						</a>
						{#if data.pagination?.continueHref}
							<a
								href={data.pagination.continueHref}
								class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
								style="border-color: var(--app-border); color: var(--app-text);"
							>
								{t(locale, 'transactions.explorer.continue')}
							</a>
						{/if}
					{/if}
					<a
						href="/books"
						class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
						style="border-color: var(--app-border); color: var(--app-text);"
					>
						Review books
					</a>
					{#if data.activeBook}
						<a
							id="transactions-empty-preview-link"
							href="/transactions/new"
							aria-describedby="transactions-empty-preview-note"
							class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
							style="border-color: var(--app-border); color: var(--app-text);"
						>
							Preview transaction entry (no write)
						</a>
						<p id="transactions-empty-preview-note" class="max-w-xs text-xs" style="color: var(--app-muted);">
							Opens the same preview-only form from the toolbar; no CREATE/PATCH/DELETE/batch action is available.
						</p>
					{/if}
				</EmptyState>
			{/if}
		</div>
	{/if}
</main>
