<script lang="ts">
	import { navigating } from '$app/state';
	import SummaryGrid from '$lib/components/SummaryGrid.svelte';
	import RecentTransactions from '$lib/components/RecentTransactions.svelte';
	import ExpensesByAccount from '$lib/components/ExpensesByAccount.svelte';
	import CashflowSummary from '$lib/components/CashflowSummary.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data }: { data: any } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/dashboard');
	const summarySetupRequired = $derived(data.summary?.status === 'setup_required');
	const settingsHref = $derived(data.activeBook ? `/books/${encodeURIComponent(String(data.activeBook.id))}/settings` : '/books');
</script>

<svelte:head>
	<title>{t(locale, 'dashboard.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl px-4 py-6 sm:py-10" style="color: var(--app-text);">
	<h1 class="text-2xl font-bold tracking-tight sm:text-3xl" style="color: var(--app-text);">{t(locale, 'dashboard.title')}</h1>

	{#if isRouteLoading}
		<div class="mt-6">
			<LoadingState variant="dashboard" message={t(locale, 'dashboard.loading')} />
		</div>
	{:else}
		<section class="mt-6" aria-labelledby="summary-heading">
			<h2 id="summary-heading" class="mb-3 text-sm font-medium uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'dashboard.summary')}</h2>
			{#if data.sectionErrors.summary}
				<div
					data-dashboard-section-error="summary"
					role="alert"
					class="mb-3 rounded-lg p-4 text-sm"
					style="background-color: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));"
				>
					<p class="font-semibold">{t(locale, 'dashboard.sectionError.title')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.sectionError.redacted')}</p>
				</div>
			{/if}
			{#if !data.sectionErrors.summary}
				<SummaryGrid summary={data.summary} drilldowns={data.drilldowns} {locale} {settingsHref} isAdmin={data.isAdmin === true} />
			{/if}
		</section>

		<div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
			{#if data.sectionErrors.recentTransactions}
				<section
					data-dashboard-section-error="recentTransactions"
					role="alert"
					class="rounded-xl p-5 text-sm"
					style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));"
				>
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.recentTransactions')}</h2>
					<p class="mt-3 font-semibold" style="color: var(--app-warning);">{t(locale, 'dashboard.sectionError.title')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.sectionError.redacted')}</p>
				</section>
			{:else}
				<RecentTransactions transactions={data.recentTransactions} drilldownHref={data.drilldowns.recent} {locale} />
			{/if}

			{#if summarySetupRequired}
				<section class="rounded-xl p-5 text-sm" role="status" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border); color: var(--app-muted);">
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.expensesByAccount')}</h2>
					<p class="mt-3">{t(locale, 'dashboard.setupRequiredTitle')}</p>
				</section>
			{:else if data.sectionErrors.expenses}
				<section
					data-dashboard-section-error="expenses"
					role="alert"
					class="rounded-xl p-5 text-sm"
					style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));"
				>
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.expensesByAccount')}</h2>
					<p class="mt-3 font-semibold" style="color: var(--app-warning);">{t(locale, 'dashboard.sectionError.title')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.sectionError.redacted')}</p>
				</section>
			{:else}
				<ExpensesByAccount expenses={data.expenses} drilldownHrefs={data.drilldowns.expensesByAccount} {locale} />
			{/if}
		</div>

		<section class="mt-6" aria-labelledby="cashflow-heading">
			<h2 id="cashflow-heading" class="sr-only">{t(locale, 'dashboard.cashflow')}</h2>
			{#if summarySetupRequired}
				<div class="rounded-xl p-5 text-sm" role="status" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border); color: var(--app-muted);">
					<h3 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.cashflow')}</h3>
					<p class="mt-3">{t(locale, 'dashboard.setupRequiredTitle')}</p>
				</div>
			{:else if data.sectionErrors.cashflow}
				<div
					data-dashboard-section-error="cashflow"
					role="alert"
					class="rounded-xl p-5 text-sm"
					style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));"
				>
					<h3 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.cashflow')}</h3>
					<p class="mt-3 font-semibold" style="color: var(--app-warning);">{t(locale, 'dashboard.sectionError.title')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.sectionError.redacted')}</p>
				</div>
			{:else}
				<CashflowSummary periods={data.cashflowPeriods} drilldownHrefs={data.drilldowns.cashflowByMonth} {locale} />
			{/if}
		</section>
		{/if}
</main>
