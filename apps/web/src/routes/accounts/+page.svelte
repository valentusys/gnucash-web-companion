<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import Money from '$lib/components/Money.svelte';
	import type { AccountCommodityAmount, AccountExplorerNode } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	const ACCOUNT_TREE_PAGE_SIZE = 24;
	const ROOT_PAGE_KEY = '__roots__';
	const FLAT_PAGE_KEY = '__flat__';
	const accountTypes = ['ASSET', 'BANK', 'CASH', 'CREDIT', 'LIABILITY', 'EQUITY', 'INCOME', 'EXPENSE', 'RECEIVABLE', 'PAYABLE', 'STOCK', 'MUTUAL'];

	let { data }: { data: any } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/accounts');
	const nodes = $derived<AccountExplorerNode[]>(data.accounts?.nodes ?? []);
	const isFlat = $derived(data.filters?.mode === 'flat');
	const hasRows = $derived(nodes.length > 0);
	const advancedFiltersActive = $derived(Boolean(data.filters?.types?.length || data.filters?.hidden !== 'exclude' || data.filters?.placeholder !== 'include'));
	const childMap = $derived.by(() => {
		const map = new Map<string | null, AccountExplorerNode[]>();
		for (const node of nodes) {
			const key = node.parent_id ?? null;
			const siblings = map.get(key) ?? [];
			siblings.push(node);
			map.set(key, siblings);
		}
		return map;
	});
	const rootNodes = $derived.by(() => {
		const byId = new Map(nodes.map((node) => [node.id, node]));
		const roots = (data.accounts?.root_ids ?? [])
			.map((id: string) => byId.get(id))
			.filter((node: AccountExplorerNode | undefined): node is AccountExplorerNode => Boolean(node));
		return roots.length ? roots : (childMap.get(null) ?? nodes.filter((node) => !node.parent_id));
	});
	const structureWarnings = $derived(nodes.filter((node) => node.structure_status !== 'root' && node.structure_status !== 'normal'));
	const hasMixedCommodities = $derived(nodes.some((node) => node.recursive_balances.length > 1));
	const hasContextAncestors = $derived(nodes.some((node) => node.match_state === 'ancestor_context'));
	const hasHiddenRows = $derived(nodes.some((node) => node.hidden));
	const hasPlaceholderRows = $derived(nodes.some((node) => node.placeholder));

	function initialExpansionState(): Set<string> {
		return initialExpandedNodeIds(data.accounts?.nodes ?? [], data.filters?.query ?? '');
	}

	function initialCanonicalHref(): string {
		return data.canonicalHref ?? '';
	}

	let expandedNodeIds = $state<Set<string>>(initialExpansionState());
	let treePageByParent = $state<Record<string, number>>({});
	let activeExplorerHref = $state(initialCanonicalHref());

	$effect(() => {
		const canonicalHref = data.canonicalHref ?? '';
		if (canonicalHref === activeExplorerHref) return;
		activeExplorerHref = canonicalHref;
		treePageByParent = {};
		if (data.filters?.query) {
			const nextExpanded = new Set(expandedNodeIds);
			for (const id of initialExpandedNodeIds(nodes, data.filters.query)) nextExpanded.add(id);
			expandedNodeIds = nextExpanded;
		}
	});

	function initialExpandedNodeIds(sourceNodes: AccountExplorerNode[], query: string): Set<string> {
		if (!query.trim()) return new Set();
		return new Set(sourceNodes.filter((node) => node.match_state === 'ancestor_context').map((node) => node.id));
	}

	function commodityLabel(balance: AccountCommodityAmount): string {
		return balance.commodity.namespace === 'CURRENCY'
			? balance.commodity.mnemonic
			: `${balance.commodity.namespace}:${balance.commodity.mnemonic}`;
	}

	function nodeHref(node: AccountExplorerNode): string {
		return data.detailHrefs?.[node.id] ?? `/accounts/${encodeURIComponent(node.id)}`;
	}

	function depthStyle(node: AccountExplorerNode): string {
		return `margin-left: ${Math.min(node.depth, 6) * 0.5}rem;`;
	}

	function accountDisplayName(node: AccountExplorerNode): string {
		return node.display_name || node.name || node.full_path;
	}

	function childCountLabel(count: number): string {
		return t(locale, 'accounts.explorer.childCountShort', { count });
	}

	function childrenFor(parentId: string): AccountExplorerNode[] {
		return childMap.get(parentId) ?? [];
	}

	function isExpanded(nodeId: string): boolean {
		return expandedNodeIds.has(nodeId);
	}

	function toggleNode(nodeId: string): void {
		const next = new Set(expandedNodeIds);
		if (next.has(nodeId)) next.delete(nodeId);
		else next.add(nodeId);
		expandedNodeIds = next;
	}

	function pageFor(parentId: string, total: number): number {
		const lastPage = Math.max(0, Math.ceil(total / ACCOUNT_TREE_PAGE_SIZE) - 1);
		return Math.min(Math.max(treePageByParent[parentId] ?? 0, 0), lastPage);
	}

	function visibleChildren(parentId: string): AccountExplorerNode[] {
		const children = childrenFor(parentId);
		const page = pageFor(parentId, children.length);
		const start = page * ACCOUNT_TREE_PAGE_SIZE;
		return children.slice(start, start + ACCOUNT_TREE_PAGE_SIZE);
	}

	function setTreePage(parentId: string, page: number, total: number): void {
		const lastPage = Math.max(0, Math.ceil(total / ACCOUNT_TREE_PAGE_SIZE) - 1);
		treePageByParent = { ...treePageByParent, [parentId]: Math.min(Math.max(page, 0), lastPage) };
	}

	function visibleRootNodes(): AccountExplorerNode[] {
		const page = pageFor(ROOT_PAGE_KEY, rootNodes.length);
		const start = page * ACCOUNT_TREE_PAGE_SIZE;
		return rootNodes.slice(start, start + ACCOUNT_TREE_PAGE_SIZE);
	}

	function visibleFlatNodes(): AccountExplorerNode[] {
		const page = pageFor(FLAT_PAGE_KEY, nodes.length);
		const start = page * ACCOUNT_TREE_PAGE_SIZE;
		return nodes.slice(start, start + ACCOUNT_TREE_PAGE_SIZE);
	}

	function pageStatus(parentId: string, total: number): string {
		const page = pageFor(parentId, total);
		const start = total ? page * ACCOUNT_TREE_PAGE_SIZE + 1 : 0;
		const end = Math.min(total, start + ACCOUNT_TREE_PAGE_SIZE - 1);
		return t(locale, 'accounts.explorer.pageStatus', { start, end, total });
	}
</script>

{#snippet amountBadge(balance: AccountCommodityAmount)}
	<span class="inline-flex max-w-full min-w-0 items-center rounded-lg border px-2 py-1 text-xs" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" title={commodityLabel(balance)}>
		<Money amount={balance.amount} currency={balance.commodity.mnemonic} />
	</span>
{/snippet}

{#snippet balanceBlock(node: AccountExplorerNode)}
	<div class="mt-2 grid gap-2 sm:grid-cols-2">
		<div class="min-w-0 rounded-lg p-2" style="background: var(--app-elevated-bg);">
			<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.directBalance')}</p>
			<p class="mt-1">{@render amountBadge(node.direct_balance)}</p>
		</div>
		<div class="min-w-0 rounded-lg p-2" style="background: var(--app-elevated-bg);">
			<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.recursiveBuckets')}</p>
			<div class="mt-1 flex flex-wrap gap-2">
				{#each node.recursive_balances as balance, index (`${node.id}-${balance.commodity.namespace}-${balance.commodity.mnemonic}-${index}`)}
					{@render amountBadge(balance)}
				{:else}
					<span class="text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.noRecursiveBuckets')}</span>
				{/each}
			</div>
		</div>
	</div>
	<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.balanceDetailsHelp')}</p>
{/snippet}

{#snippet nodeBadges(node: AccountExplorerNode)}
	<div class="mt-1 flex flex-wrap gap-1 text-xs">
		<span class="rounded-full px-2 py-0.5" style="background: var(--app-elevated-bg); color: var(--app-muted);">{node.type}</span>
		<span class="rounded-full px-2 py-0.5" style="background: var(--app-elevated-bg); color: var(--app-muted);">{commodityLabel(node.direct_balance)}</span>
		{#if node.hidden}
			<span class="rounded-full px-2 py-0.5" style="background: color-mix(in srgb, var(--app-warning) 14%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.hiddenBadge')}</span>
		{/if}
		{#if node.placeholder}
			<span class="rounded-full px-2 py-0.5" style="background: color-mix(in srgb, var(--app-success) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.groupBadge')}</span>
			<span class="rounded-full px-2 py-0.5" style="background: color-mix(in srgb, var(--app-accent) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.placeholderBadge')}</span>
		{/if}
		{#if node.match_state === 'ancestor_context'}
			<span class="rounded-full px-2 py-0.5" style="background: color-mix(in srgb, var(--app-warning) 12%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.contextBadge')}</span>
		{/if}
		{#if node.structure_status !== 'root' && node.structure_status !== 'normal'}
			<span class="rounded-full px-2 py-0.5" style="background: color-mix(in srgb, var(--app-danger) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.repairedBadge')}: {node.structure_status}</span>
		{/if}
	</div>
{/snippet}

{#snippet accountRow(node: AccountExplorerNode, hasChildren: boolean)}
	<div data-account-row={node.id} class="min-w-0 rounded-xl border p-3" style={`border-color: var(--app-border); background: var(--app-panel); ${depthStyle(node)}`}>
		<div class="flex min-w-0 items-start gap-2">
			{#if hasChildren}
				<button
					type="button"
					data-account-toggle={node.id}
					class="inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center rounded-lg border text-lg focus:outline-none focus:ring-2"
					style="border-color: var(--app-border); color: var(--app-accent); --tw-ring-color: var(--app-accent);"
					aria-expanded={isExpanded(node.id)}
					aria-controls={`account-children-${node.id}`}
					aria-label={isExpanded(node.id) ? t(locale, 'accounts.explorer.collapseGroup', { name: accountDisplayName(node) }) : t(locale, 'accounts.explorer.expandGroup', { name: accountDisplayName(node) })}
					onclick={() => toggleNode(node.id)}
				>
					<span aria-hidden="true">{isExpanded(node.id) ? '−' : '+'}</span>
				</button>
			{/if}
			<div class="min-w-0 flex-1">
				<div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
					<div class="min-w-0">
						<a class="break-words text-sm font-semibold hover:underline sm:text-base" style="color: var(--app-accent);" href={nodeHref(node)} title={node.full_path}>{accountDisplayName(node)}</a>
						<p class="mt-0.5 break-words break-all text-xs" style="color: var(--app-muted);">{node.full_path}</p>
						{#if node.placeholder}
							<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.nonPostableGroup')} · {childCountLabel(node.child_count)}</p>
						{/if}
						{@render nodeBadges(node)}
					</div>
					{#if !node.placeholder}
						<div class="flex shrink-0 flex-wrap items-start gap-2 sm:max-w-[30rem] sm:justify-end">
							{@render amountBadge(node.direct_balance)}
							<details data-account-balance-details={node.id} class="min-w-[11rem] rounded-lg border px-2" style="border-color: var(--app-border); background: var(--app-bg);">
								<summary class="flex min-h-11 cursor-pointer items-center text-xs font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.explorer.balanceDetails')}</summary>
								{@render balanceBlock(node)}
							</details>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/snippet}

{#snippet pageControls(parentId: string, total: number)}
	{#if total > ACCOUNT_TREE_PAGE_SIZE}
		{@const currentPage = pageFor(parentId, total)}
		<nav class="mt-2 flex flex-col gap-2 rounded-lg border p-2 sm:flex-row sm:items-center sm:justify-between" style="border-color: var(--app-border); background: var(--app-panel);" aria-label={t(locale, 'accounts.explorer.childPagination')}>
			<button type="button" data-account-page-previous={parentId} class="min-h-11 rounded-lg border px-3 py-2 text-sm font-semibold disabled:opacity-50" style="border-color: var(--app-border); color: var(--app-text);" disabled={currentPage === 0} onclick={() => setTreePage(parentId, currentPage - 1, total)}>{t(locale, 'accounts.explorer.previousPage')}</button>
			<p class="text-center text-xs" style="color: var(--app-muted);" aria-live="polite">{pageStatus(parentId, total)}</p>
			<button type="button" data-account-page-next={parentId} class="min-h-11 rounded-lg border px-3 py-2 text-sm font-semibold disabled:opacity-50" style="border-color: var(--app-border); color: var(--app-text);" disabled={(currentPage + 1) * ACCOUNT_TREE_PAGE_SIZE >= total} onclick={() => setTreePage(parentId, currentPage + 1, total)}>{t(locale, 'accounts.explorer.nextPage')}</button>
		</nav>
	{/if}
{/snippet}

{#snippet renderTreeNode(node: AccountExplorerNode)}
	{@const children = childrenFor(node.id)}
	<li class="min-w-0">
		{@render accountRow(node, children.length > 0)}
		{#if children.length > 0 && isExpanded(node.id)}
			<div id={`account-children-${node.id}`} class="mt-2 border-l pl-2 sm:pl-3" style="border-color: var(--app-border);">
				<ul class="space-y-2">
					{#each visibleChildren(node.id) as child (child.id)}
						{@render renderTreeNode(child)}
					{/each}
				</ul>
				{@render pageControls(node.id, children.length)}
			</div>
		{/if}
	</li>
{/snippet}

<svelte:head>
	<title>{t(locale, 'accounts.kicker')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-7xl px-3 py-6 sm:px-4 sm:py-8">
	<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'accounts.kicker')}</p>
			<h1 class="mt-1 text-2xl font-bold sm:text-3xl" style="color: var(--app-text);">{t(locale, 'accounts.title')}</h1>
			{#if data.activeBook}
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.bookLabel')}: {data.activeBook.name}</p>
			{/if}
		</div>
	</div>

	{#if isRouteLoading}
		<LoadingState variant="accounts" message={t(locale, 'accounts.loading')} />
	{:else}
		<div class="sticky top-0 z-20 mb-3 pt-1">
			<form method="GET" action="/accounts" class="rounded-2xl border p-3 shadow-sm" style="border-color: var(--app-border); background: color-mix(in srgb, var(--app-panel) 96%, transparent); backdrop-filter: blur(8px);" aria-describedby="accounts-explorer-help">
				<div class="grid gap-2 md:grid-cols-[11rem_minmax(12rem,1fr)_auto] md:items-end">
					<label class="text-xs font-medium" for="account-mode">
						<span>{t(locale, 'accounts.explorer.mode')}</span>
						<select id="account-mode" name="mode" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2 text-sm" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);">
							<option value="tree" selected={data.filters.mode === 'tree'}>{t(locale, 'accounts.explorer.modeTree')}</option>
							<option value="flat" selected={data.filters.mode === 'flat'}>{t(locale, 'accounts.explorer.modeFlat')}</option>
						</select>
					</label>
					<label class="text-xs font-medium" for="account-query">
						<span>{t(locale, 'accounts.explorer.query')}</span>
						<input id="account-query" name="query" type="search" maxlength="120" value={data.filters.query} placeholder={t(locale, 'accounts.filter.placeholder')} class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2 text-sm" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);" />
					</label>
					<div class="grid grid-cols-2 gap-2 md:flex">
						<button class="inline-flex min-h-11 items-center justify-center rounded-xl px-3 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">{t(locale, 'transactions.filters.submit')}</button>
						<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-3 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
					</div>
				</div>

				<details class="mt-2 rounded-xl border px-3" style="border-color: var(--app-border);">
					<summary class="flex min-h-11 cursor-pointer items-center text-sm font-semibold" style="color: var(--app-text);">{advancedFiltersActive ? t(locale, 'accounts.explorer.advancedFiltersActive') : t(locale, 'accounts.explorer.advancedFilters')}</summary>
					<p id="accounts-explorer-help" class="text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.formHelp')}</p>
					<div class="mt-3 grid gap-3 lg:grid-cols-4">
						<fieldset class="rounded-xl border p-3 lg:col-span-2" style="border-color: var(--app-border);">
							<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.explorer.typesLegend')}</legend>
							<div class="mt-2 flex flex-wrap gap-2">
								{#each accountTypes as type}
									<label class="inline-flex min-h-11 items-center gap-2 rounded-xl border px-3 py-2 text-sm" style="border-color: var(--app-border); color: var(--app-text);">
										<input type="checkbox" name="type" value={type} checked={data.filters.types.includes(type)} />
										<span>{type}</span>
									</label>
								{/each}
							</div>
						</fieldset>
						<label class="text-sm font-medium" for="account-hidden">
							<span>{t(locale, 'accounts.explorer.hidden')}</span>
							<select id="account-hidden" name="hidden" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);">
								<option value="exclude" selected={data.filters.hidden === 'exclude'}>{t(locale, 'accounts.explorer.visibilityExclude')}</option>
								<option value="include" selected={data.filters.hidden === 'include'}>{t(locale, 'accounts.explorer.visibilityInclude')}</option>
								<option value="only" selected={data.filters.hidden === 'only'}>{t(locale, 'accounts.explorer.visibilityOnly')}</option>
							</select>
						</label>
						<label class="text-sm font-medium" for="account-placeholder">
							<span>{t(locale, 'accounts.explorer.placeholder')}</span>
							<select id="account-placeholder" name="placeholder" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);">
								<option value="include" selected={data.filters.placeholder === 'include'}>{t(locale, 'accounts.explorer.visibilityInclude')}</option>
								<option value="exclude" selected={data.filters.placeholder === 'exclude'}>{t(locale, 'accounts.explorer.visibilityExclude')}</option>
								<option value="only" selected={data.filters.placeholder === 'only'}>{t(locale, 'accounts.explorer.visibilityOnly')}</option>
							</select>
						</label>
					</div>
				</details>
			</form>
		</div>

		{#if data.activeFilters?.length}
			<section class="mb-3 rounded-xl border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="accounts-active-filters-title" aria-live="polite">
				<p id="accounts-active-filters-title" class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactions.filters.activeSummaryTitle')}</p>
				<ul class="mt-1 flex flex-wrap gap-2">
					{#each data.activeFilters as chip (chip.key)}
						<li><a class="inline-flex min-h-11 items-center rounded-full border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);" href={chip.href}>{chip.label}<span class="ml-2" aria-hidden="true">×</span></a></li>
					{/each}
				</ul>
			</section>
		{/if}

		<section class="mb-3 rounded-xl border px-3 py-2" style={data.status.role === 'alert' ? 'border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-text);' : 'border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);'} role={data.status.role} aria-live={data.status.role === 'alert' ? 'assertive' : 'polite'}>
			<p class="font-semibold">{data.status.title}</p>
			<p class="mt-0.5 text-sm">{data.status.message}</p>
			<p class="mt-0.5 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.statusCounts', { returned: data.accounts.returned_count ?? 0, candidates: data.accounts.scan?.candidate_accounts ?? 0 })}</p>
			{#if data.status.role === 'alert'}
				<a class="mt-2 inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
			{/if}
		</section>

		{#if hasContextAncestors || hasHiddenRows || hasPlaceholderRows || structureWarnings.length || hasMixedCommodities || data.accounts.limitations?.length}
			<details class="mb-3 rounded-xl border px-3" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);">
				<summary id="accounts-warnings-title" class="flex min-h-11 cursor-pointer items-center font-semibold">{t(locale, 'accounts.explorer.warningsTitle')}</summary>
				<ul class="mb-3 list-disc space-y-1 pl-5 text-sm">
					{#if hasContextAncestors}<li>{t(locale, 'accounts.explorer.contextWarning')}</li>{/if}
					{#if hasHiddenRows}<li>{t(locale, 'accounts.explorer.hiddenWarning')}</li>{/if}
					{#if hasPlaceholderRows}<li>{t(locale, 'accounts.explorer.placeholderWarning')}</li>{/if}
					{#if structureWarnings.length}<li>{t(locale, 'accounts.explorer.repairedWarning')}</li>{/if}
					{#if hasMixedCommodities}<li>{t(locale, 'accounts.explorer.mixedCommodityWarning')}</li>{/if}
					{#each data.accounts.limitations ?? [] as limitation}<li>{limitation}</li>{/each}
				</ul>
			</details>
		{/if}

		{#if hasRows}
			<section class="rounded-2xl border p-2 sm:p-3" style="border-color: var(--app-border); background: var(--app-elevated-bg);" aria-label={t(locale, 'accounts.explorer.resultsLabel')}>
				{#if isFlat}
					<ul class="space-y-2">
						{#each visibleFlatNodes() as node (node.id)}
							<li>{@render accountRow(node, false)}</li>
						{/each}
					</ul>
					{@render pageControls(FLAT_PAGE_KEY, nodes.length)}
				{:else}
					<ul class="space-y-2">
						{#each visibleRootNodes() as node (node.id)}
							{@render renderTreeNode(node)}
						{/each}
					</ul>
					{@render pageControls(ROOT_PAGE_KEY, rootNodes.length)}
				{/if}
			</section>
		{:else if data.status.kind === 'no_accounts'}
			<EmptyState title={t(locale, 'accounts.emptyTitle')} message={t(locale, 'accounts.emptyMessage')} ariaLabel={t(locale, 'accounts.emptyTitle')} icon="🧾" role="status">
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href="/books">{t(locale, 'accounts.emptyAction')}</a>
			</EmptyState>
		{:else}
			<EmptyState title={data.status.title} message={data.status.message} ariaLabel={data.status.title} icon="🧾" role={data.status.role}>
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href="/books">{t(locale, 'accounts.emptyAction')}</a>
			</EmptyState>
		{/if}
	{/if}
</main>
