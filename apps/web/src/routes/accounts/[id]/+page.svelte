<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import Money from '$lib/components/Money.svelte';
	import TransactionDirection from '$lib/components/TransactionDirection.svelte';
	import type { AccountActivitySectionStatus, AccountCommodityAmount, AccountOverviewChild } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data }: { data: any } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname?.startsWith('/accounts/'));
	const overview = $derived(data.overview);
	const activity = $derived(data.activity);
	const structureWarnings = $derived(overview ? [overview, ...(overview.children ?? [])].filter((node) => node.structure_status !== 'root' && node.structure_status !== 'normal') : []);
	const hasMixedCommodities = $derived(overview ? overview.recursive_balances.length > 1 || overview.children.some((child: AccountOverviewChild) => child.recursive_balances.length > 1) : false);
	const hasActivityDates = $derived(Boolean(data.filters?.dateFrom && data.filters?.dateTo));

	function commodityLabel(balance: AccountCommodityAmount): string {
		return balance.commodity.namespace === 'CURRENCY'
			? balance.commodity.mnemonic
			: `${balance.commodity.namespace}:${balance.commodity.mnemonic}`;
	}

	function activitySection(section: string): AccountActivitySectionStatus | undefined {
		return activity?.section_statuses?.find((item: AccountActivitySectionStatus) => item.section === section);
	}

	function childHref(child: AccountOverviewChild): string {
		return data.childHrefs?.[child.id] ?? `/accounts/${encodeURIComponent(child.id)}`;
	}

	function transactionHref(id: string): string {
		return data.transactionHrefs?.[id] ?? `/transactions/${encodeURIComponent(id)}`;
	}

	function accountLabel(account: { name: string; display_name?: string | null; full_path?: string }): string {
		return account.display_name || account.name || account.full_path || '';
	}
</script>

{#snippet amountBadge(balance: AccountCommodityAmount | null)}
	{#if balance}
		<span class="inline-flex max-w-full min-w-0 items-center rounded-lg border px-2 py-1 text-sm" style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);" title={commodityLabel(balance)}>
			<Money amount={balance.amount} currency={balance.commodity.mnemonic} />
		</span>
	{:else}
		<span class="text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.notAvailable')}</span>
	{/if}
{/snippet}

{#snippet balancePanel(title: string, balances: AccountCommodityAmount[])}
	<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);">
		<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{title}</p>
		<div class="mt-2 flex flex-wrap gap-2">
			{#each balances as balance, index (`${title}-${balance.commodity.namespace}-${balance.commodity.mnemonic}-${index}`)}
				{@render amountBadge(balance)}
			{:else}
				<span class="text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.noRecursiveBuckets')}</span>
			{/each}
		</div>
	</div>
{/snippet}

<svelte:head>
	<title>{overview ? accountLabel(overview) : t(locale, 'accounts.detail.kicker')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	{#if isRouteLoading}
		<LoadingState variant="accounts" message={t(locale, 'accounts.detail.loading')} />
	{:else if !overview}
		<section class="rounded-xl border p-4" style={data.status.role === 'alert' ? 'border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-text);' : 'border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);'} role={data.status.role} aria-live={data.status.role === 'alert' ? 'assertive' : 'polite'}>
			<p class="font-semibold">{data.status.title}</p>
			<p class="mt-1 text-sm">{data.status.message}</p>
			<a class="mt-3 inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.returnTo ?? '/accounts'}>{t(locale, 'accounts.detail.backToExplorer')}</a>
		</section>
	{:else}
		<nav class="text-sm font-medium" aria-label={t(locale, 'accounts.detail.breadcrumbAria')}>
			<ol class="flex flex-wrap items-center gap-2">
				<li><a href={data.returnTo} class="hover:underline" style="color: var(--app-accent);">{t(locale, 'accounts.kicker')}</a></li>
				{#each [...overview.breadcrumbs, { id: overview.id, name: overview.name, display_name: overview.display_name }] as segment, index}
					<li aria-hidden="true" style="color: var(--app-muted);">/</li>
					<li>
						{#if index === overview.breadcrumbs.length}
							<span style="color: var(--app-text);" aria-current="page">{accountLabel(segment)}</span>
						{:else}
							<span style="color: var(--app-muted);">{accountLabel(segment)}</span>
						{/if}
					</li>
				{/each}
			</ol>
		</nav>

		<section class="mt-4 rounded-2xl border p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border-color: var(--app-border);">
			<div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
				<div class="min-w-0">
					<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'accounts.detail.kicker')}</p>
					<h1 class="mt-1 break-words text-3xl font-bold" style="color: var(--app-text);">{accountLabel(overview)}</h1>
					<p class="mt-2 break-words" style="color: var(--app-muted);">{overview.full_path}</p>
					<div class="mt-3 flex flex-wrap gap-2 text-xs">
						<span class="rounded-full px-2 py-1" style="background: var(--app-elevated-bg); color: var(--app-muted);">{overview.type}</span>
						<span class="rounded-full px-2 py-1" style="background: var(--app-elevated-bg); color: var(--app-muted);">{overview.commodity.namespace}:{overview.commodity.mnemonic}</span>
						{#if overview.hidden}<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-warning) 14%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.hiddenBadge')}</span>{/if}
						{#if overview.placeholder}<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-success) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.groupBadge')}</span><span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-accent) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.placeholderBadge')}</span>{/if}
						{#if overview.structure_status !== 'root' && overview.structure_status !== 'normal'}<span class="rounded-full px-2 py-1" style="background: color-mix(in srgb, var(--app-danger) 10%, var(--app-panel)); color: var(--app-text);">{t(locale, 'accounts.explorer.repairedBadge')}: {overview.structure_status}</span>{/if}
					</div>
				</div>
				{#if overview.placeholder}
					<div class="min-w-0 rounded-xl p-4 lg:w-[28rem]" style="background: var(--app-elevated-bg); color: var(--app-muted);">
						<p class="font-medium" style="color: var(--app-text);">{t(locale, 'accounts.explorer.nonPostableGroup')}</p>
						<p class="mt-1 text-sm">{t(locale, 'accounts.explorer.childCountShort', { count: overview.child_count })}</p>
					</div>
				{:else}
					<div class="grid min-w-0 gap-3 sm:grid-cols-2 lg:w-[36rem]">
						<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);">
							<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'accounts.explorer.directBalance')}</p>
							<p class="mt-2">{@render amountBadge(overview.direct_balance)}</p>
						</div>
						{@render balancePanel(t(locale, 'accounts.explorer.recursiveBuckets'), overview.recursive_balances)}
					</div>
				{/if}
			</div>
			<dl class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
				<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'accounts.detail.subtreeCount')}</dt><dd class="mt-1" style="color: var(--app-text);">{overview.subtree_account_count}</dd></div>
				<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'accounts.detail.childCount')}</dt><dd class="mt-1" style="color: var(--app-text);">{overview.child_count}</dd></div>
				<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'accounts.detail.childrenReturned')}</dt><dd class="mt-1" style="color: var(--app-text);">{overview.children_returned}{overview.children_truncated ? ` / ${overview.child_count}` : ''}</dd></div>
			</dl>
		</section>

		{#if data.legacyNotice || structureWarnings.length || hasMixedCommodities || overview.children_truncated || overview.limitations?.length}
			<section class="mt-4 rounded-xl border p-4 text-sm" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);" aria-labelledby="account-detail-warnings-title">
				<p id="account-detail-warnings-title" class="font-semibold">{t(locale, 'accounts.explorer.warningsTitle')}</p>
				<ul class="mt-2 list-disc space-y-1 pl-5">
					{#if data.legacyNotice}<li>{data.legacyNotice}</li>{/if}
					{#if structureWarnings.length}<li>{t(locale, 'accounts.explorer.repairedWarning')}</li>{/if}
					{#if hasMixedCommodities}<li>{t(locale, 'accounts.explorer.mixedCommodityWarning')}</li>{/if}
					{#if overview.children_truncated}<li>{t(locale, 'accounts.detail.childrenTruncated')}</li>{/if}
					{#each overview.limitations ?? [] as limitation}<li>{limitation}</li>{/each}
				</ul>
			</section>
		{/if}

		<section class="mt-6 rounded-2xl border p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border-color: var(--app-border);">
			<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div>
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.detail.childrenTitle')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.childrenHelp')}</p>
				</div>
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.returnTo}>{t(locale, 'accounts.detail.backToExplorer')}</a>
			</div>
			{#if overview.children.length}
				<ul class="mt-4 space-y-3">
					{#each overview.children as child (child.id)}
						<li class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-elevated-bg);">
							<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
								<div class="min-w-0">
									<a class="break-words font-semibold hover:underline" style="color: var(--app-accent);" href={childHref(child)} title={child.full_path}>{accountLabel(child)}</a>
									<p class="mt-1 break-words text-sm" style="color: var(--app-muted);">{child.full_path}</p>
									<p class="mt-1 text-xs" style="color: var(--app-muted);">{child.type} · {child.child_count} {t(locale, 'accounts.detail.childrenTitle')}</p>
								</div>
								<div class="min-w-0 md:w-80">{@render balancePanel(t(locale, 'accounts.explorer.recursiveBuckets'), child.recursive_balances)}</div>
							</div>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="mt-4 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.noChildren')}</p>
			{/if}
		</section>

		{#if !overview.placeholder}
		<section class="mt-6 rounded-2xl border p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border-color: var(--app-border);">
			<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div>
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.detail.activityTitle')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.activityHelp')}</p>
				</div>
				<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetActivityHref}>{t(locale, 'accounts.detail.resetActivity')}</a>
			</div>

			<form method="GET" action={`/accounts/${overview.id}`} class="mt-4 rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-elevated-bg);" aria-describedby="account-activity-form-help">
				{#if data.returnTo && data.returnTo !== '/accounts'}<input type="hidden" name="return_to" value={data.returnTo} />{/if}
				<p id="account-activity-form-help" class="text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.detail.activityFormHelp')}</p>
				<div class="mt-3 grid gap-3 sm:grid-cols-3">
					<label class="text-sm font-medium" for="account-date-from"><span>{t(locale, 'transactions.filters.from')}</span><input id="account-date-from" name="date_from" type="date" value={data.filters.dateFrom} class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);" /></label>
					<label class="text-sm font-medium" for="account-date-to"><span>{t(locale, 'transactions.filters.to')}</span><input id="account-date-to" name="date_to" type="date" value={data.filters.dateTo} class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);" /></label>
					<label class="text-sm font-medium" for="account-limit"><span>{t(locale, 'accounts.detail.limit')}</span><select id="account-limit" name="limit" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background: var(--app-input-bg); color: var(--app-text);"><option value="5" selected={data.filters.limit === 5}>5</option><option value="10" selected={data.filters.limit === 10}>10</option><option value="20" selected={data.filters.limit === 20}>20</option></select></label>
				</div>
				<div class="mt-4 flex flex-wrap gap-2">
					<button class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">{t(locale, 'accounts.detail.applyActivity')}</button>
					<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.resetActivityHref}>{t(locale, 'accounts.detail.resetActivity')}</a>
				</div>
			</form>

			<section class="mt-4 rounded-xl border p-4" style={data.status.role === 'alert' ? 'border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-text);' : 'border-color: var(--app-border); background: var(--app-elevated-bg); color: var(--app-text);'} role={data.status.role} aria-live={data.status.role === 'alert' ? 'assertive' : 'polite'}>
				<p class="font-semibold">{data.status.title}</p>
				<p class="mt-1 text-sm">{data.status.message}</p>
				<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'accounts.detail.requestCounters', { overview: data.activityRequestCounters?.overview ?? 0, activity: data.activityRequestCounters?.activity ?? 0 })}</p>
			</section>

			{#if activity}
				<div class="mt-4 grid gap-4 lg:grid-cols-3">
					<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><p class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'accounts.detail.exactChange')}</p><p class="mt-2">{@render amountBadge(activity.change)}</p><p class="mt-1 text-xs" style="color: var(--app-muted);">{activitySection('change')?.status ?? ''}</p></div>
					<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><p class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'reports.cashflow.inflow')} / {t(locale, 'reports.cashflow.outflow')}</p><p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.flowNotApplicable')}</p></div>
					<div class="rounded-xl p-4" style="background: var(--app-elevated-bg);"><p class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'accounts.detail.recentReturned')}</p><p class="mt-2 text-xl font-semibold" style="color: var(--app-text);">{activity.returned_count}{activity.has_more ? '+' : ''}</p><p class="mt-1 text-xs" style="color: var(--app-muted);">{activitySection('recent_transactions')?.status ?? ''}</p></div>
				</div>

				<div class="mt-4 flex flex-wrap gap-2">
					{#if activity.transaction_explorer_compatible && data.transactionExplorerHref}
						<a class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={data.transactionExplorerHref}>{t(locale, 'accounts.detail.openTransactionExplorer')}</a>
					{:else}
						<span class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-muted);" aria-disabled="true">{t(locale, 'accounts.detail.unavailableNoFxScope')}</span>
					{/if}
					{#if hasActivityDates && data.reportHref}
						<a class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);" href={data.reportHref}>{t(locale, 'accounts.detail.openBaseReport')}</a>
					{/if}
				</div>

				{#if activity.limitations?.length}
					<section class="mt-4 rounded-xl border p-4 text-sm" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);">
						<p class="font-semibold">{t(locale, 'transactions.explorer.limitationsTitle')}</p>
						<ul class="mt-2 list-disc space-y-1 pl-5">{#each activity.limitations as limitation}<li>{limitation}</li>{/each}</ul>
					</section>
				{/if}

				<section class="mt-4" aria-labelledby="account-recent-title">
					<h3 id="account-recent-title" class="text-base font-semibold" style="color: var(--app-text);">{t(locale, 'accounts.detail.recentTitle')}</h3>
					{#if activity.recent_transactions.length}
						<ul class="mt-3 space-y-3">
							{#each activity.recent_transactions as tx (tx.id)}
								<li class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-elevated-bg);">
									<div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
										<div class="min-w-0">
											<a class="break-words font-semibold hover:underline" style="color: var(--app-accent);" href={transactionHref(tx.id)}>{tx.description || t(locale, 'transactionDetail.noDescription')}</a>
											<p class="mt-1 text-sm" style="color: var(--app-muted);">{tx.date}</p>
											<div class="mt-2 min-w-0"><TransactionDirection direction={tx.direction ?? null} {locale} compact /></div>
											{#if tx.is_write_alpha_owned}<span class="mt-2 inline-flex rounded-full px-2 py-1 text-xs font-semibold" style="background: #fffbeb; color: #92400e; border: 1px solid #fcd34d;">{t(locale, 'transactions.writeAlphaHistoryBadge')}</span>{/if}
										</div>
										<div>{@render amountBadge(tx.matched_quantity)}</div>
									</div>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'accounts.detail.noRecentTransactions')}</p>
					{/if}
				</section>
			{/if}
		</section>
		{/if}
	{/if}
</main>
