<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import Money from '$lib/components/Money.svelte';
	import type { AccountCommodityAmount, AccountExplorerNode } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data }: { data: any } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/accounts');
	const accountTypes = ['ASSET', 'BANK', 'CASH', 'CREDIT', 'LIABILITY', 'EQUITY', 'INCOME', 'EXPENSE', 'RECEIVABLE', 'PAYABLE', 'STOCK', 'MUTUAL'];
	const nodes = $derived<AccountExplorerNode[]>(data.accounts?.nodes ?? []);
	const isFlat = $derived(data.filters?.mode === 'flat');
	const hasRows = $derived(nodes.length > 0);
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

	function commodityLabel(balance: AccountCommodityAmount): string {
		return balance.commodity.namespace === 'CURRENCY'
			? balance.commodity.mnemonic
			: `${balance.commodity.namespace}:${balance.commodity.mnemonic}`;
	}

	function nodeHref(node: AccountExplorerNode): string {
		return data.detailHrefs?.[node.id] ?? `/accounts/${encodeURIComponent(node.id)}`;
	}

	function depthStyle(node: AccountExplorerNode): string {
		return `padding-left: ${Math.min(node.depth, 6) * 0.75}rem;`;
	}

	function accountDisplayName(node: AccountExplorerNode): string {
		return node.display_name || node.name || node.full_path;
	}

	function childCountLabel(count: number): string {
		return t(locale, 'accounts.explorer.childCountShort', { count });
	}
</script>

{#snippet amountBadge(balance: AccountCommodityAmount)}
	<span class="inline-flex max-w-full min-w-0 items-center rounded-lg border px-2 py-1 text-xs" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" title={commodityLabel(balance)}>
		<Money amount={balance.amount} currency={balance.commodity.mnemonic} />
	</span>
{/snippet}

{#snippet balanceBlock(node: AccountExplorerNode)}
	<div class="grid gap-2 sm:grid-cols-2">
		<div class="min-w-0 rounded-xl p-3" style="background: var(--app-elevated-bg);">
			<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.directBalance')}</p>
			<p class="mt-1">{@render amountBadge(node.direct_balance)}</p>
		</div>
		<div class="min-w-0 rounded-xl p-3" style="background: var(--app-elevated-bg);">
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
{/snippet}

{#snippet nodeBadges(node: AccountExplorerNode)}
	<div class="mt-2 flex flex-wrap gap-2 text-xs">
		<span class="rounded-full px-2 py-1" style="background: var(--app-elevated-bg); color: var(--app-muted);">{node.type}</span>
		<span class="rounded-full px-2 py-1" style="background: var(--app-elevated-bg); color: var(--app-muted);">{commodityLabel(node.direct_balance)}</span>
		{#if node.hidden}
			<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-warning) 14%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.hiddenBadge')}</span>
		{/if}
		{#if node.placeholder}
			<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-success) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.groupBadge')}</span>
			<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-accent) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.placeholderBadge')}</span>
		{/if}
		{#if node.match_state === 'ancestor_context'}
			<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-warning) 12%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.contextBadge')}</span>
		{/if}
		{#if node.structure_status !== 'root' && node.structure_status !== 'normal'}
			<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-danger) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.repairedBadge')}: {node.structure_status}</span>
		{/if}
	</div>
{/snippet}

{#snippet accountRow(node: AccountExplorerNode)}
	<div class="min-w-0 rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-panel); {depthStyle(node)}">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
			<div class="min-w-0">
				<a class="break-words text-base font-semibold hover:underline" style="color: var(--app-accent);" href={nodeHref(node)} title={node.full_path}>{accountDisplayName(node)}</a>
				<p class="mt-1 break-words break-all text-sm" style="color: var(--app-muted);">{node.full_path}</p>
				{#if node.placeholder}
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.nonPostableGroup')} · {childCountLabel(node.child_count)}</p>
				{/if}
				{@render nodeBadges(node)}
			</div>
			{#if !node.placeholder}
				<div class="min-w-0 lg:w-[28rem]">
					{@render balanceBlock(node)}
				</div>
			{/if}
		</div>
	</div>
{/snippet}

{#snippet renderTreeNode(node: AccountExplorerNode)}
	<li class="min-w-0">
		{#if (childMap.get(node.id) ?? []).length}
			<details open class="min-w-0">
				<summary class="min-h-11 cursor-pointer list-none rounded-xl focus:outline-none focus:ring-2" style="--tw-ring-color: var(--app-accent);">
					{@render accountRow(node)}
				</summary>
				<ul class="mt-3 space-y-3 border-l pl-3" style="border-color: var(--app-border);">
					{#each childMap.get(node.id) ?? [] as child (child.id)}
						{@render renderTreeNode(child)}
					{/each}
				</ul>
			</details>
		{:else}
			{@render accountRow(node)}
		{/if}
	</li>
{/snippet}

<svelte:head>
	<title>{t(locale, 'accounts.kicker')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-7xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'accounts.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'accounts.title')}</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.bookLabel')}: {data.activeBook.name}</p>
			{/if}
		</div>
		<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
	</div>

	{#if isRouteLoading}
		<LoadingState variant="accounts" message={t(locale, 'accounts.loading')} />
	{:else}
		<form method="GET" action="/accounts" class="mb-4 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-describedby="accounts-explorer-help">
			<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div>
					<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.explorer.filtersTitle')}</p>
					<p id="accounts-explorer-help" class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.formHelp')}</p>
				</div>
				<div class="flex flex-wrap gap-2">
					<button class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">{t(locale, 'transactions.filters.submit')}</button>
					<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
				</div>
			</div>

			<div class="mt-4 grid gap-4 lg:grid-cols-4">
				<label class="text-sm font-medium" for="account-mode">
					<span>{t(locale, 'accounts.explorer.mode')}</span>
					<select id="account-mode" name="mode" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);">
						<option value="tree" selected={data.filters.mode === 'tree'}>{t(locale, 'accounts.explorer.modeTree')}</option>
						<option value="flat" selected={data.filters.mode === 'flat'}>{t(locale, 'accounts.explorer.modeFlat')}</option>
					</select>
				</label>
				<label class="text-sm font-medium lg:col-span-3" for="account-query">
					<span>{t(locale, 'accounts.explorer.query')}</span>
					<input id="account-query" name="query" type="search" maxlength="120" value={data.filters.query} placeholder={t(locale, 'accounts.filter.placeholder')} class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);" />
				</label>
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
		</form>

		{#if data.activeFilters?.length}
			<section class="mb-4 rounded-xl border px-3 py-3" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="accounts-active-filters-title" aria-live="polite">
				<p id="accounts-active-filters-title" class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactions.filters.activeSummaryTitle')}</p>
				<ul class="mt-2 flex flex-wrap gap-2">
					{#each data.activeFilters as chip (chip.key)}
						<li><a class="inline-flex min-h-11 items-center rounded-full border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);" href={chip.href}>{chip.label}<span class="ml-2" aria-hidden="true">×</span></a></li>
					{/each}
				</ul>
			</section>
		{/if}

		<section class="mb-4 rounded-xl border p-4" style={data.status.role === 'alert' ? 'border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-text);' : 'border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);'} role={data.status.role} aria-live={data.status.role === 'alert' ? 'assertive' : 'polite'}>
			<p class="font-semibold">{data.status.title}</p>
			<p class="mt-1 text-sm">{data.status.message}</p>
			<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.statusCounts', { returned: data.accounts.returned_count ?? 0, candidates: data.accounts.scan?.candidate_accounts ?? 0 })}</p>
			{#if data.status.role === 'alert'}
				<a class="mt-3 inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.resetHref}>{t(locale, 'accounts.explorer.reset')}</a>
			{/if}
		</section>

		{#if hasContextAncestors || hasHiddenRows || hasPlaceholderRows || structureWarnings.length || hasMixedCommodities || data.accounts.limitations?.length}
			<section class="mb-4 rounded-xl border p-4 text-sm" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);" aria-labelledby="accounts-warnings-title">
				<p id="accounts-warnings-title" class="font-semibold">{t(locale, 'accounts.explorer.warningsTitle')}</p>
				<ul class="mt-2 list-disc space-y-1 pl-5">
					{#if hasContextAncestors}<li>{t(locale, 'accounts.explorer.contextWarning')}</li>{/if}
					{#if hasHiddenRows}<li>{t(locale, 'accounts.explorer.hiddenWarning')}</li>{/if}
					{#if hasPlaceholderRows}<li>{t(locale, 'accounts.explorer.placeholderWarning')}</li>{/if}
					{#if structureWarnings.length}<li>{t(locale, 'accounts.explorer.repairedWarning')}</li>{/if}
					{#if hasMixedCommodities}<li>{t(locale, 'accounts.explorer.mixedCommodityWarning')}</li>{/if}
					{#each data.accounts.limitations ?? [] as limitation}<li>{limitation}</li>{/each}
				</ul>
			</section>
		{/if}

		{#if hasRows}
			<section class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-elevated-bg);" aria-label={t(locale, 'accounts.explorer.resultsLabel')}>
				{#if isFlat}
					<ul class="space-y-3">
						{#each nodes as node (node.id)}
							<li>{@render accountRow(node)}</li>
						{/each}
					</ul>
				{:else}
					<ul class="space-y-3">
						{#each rootNodes as node (node.id)}
							{@render renderTreeNode(node)}
						{/each}
					</ul>
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
