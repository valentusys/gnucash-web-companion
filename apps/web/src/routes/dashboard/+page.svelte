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
		{#if data.loadError}
			<div
				class="mt-4 rounded-lg p-4 text-sm"
				style="background-color: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-danger); border: 1px solid var(--app-danger);"
				role="alert"
			>
				<p class="font-semibold">{t(locale, 'dashboard.loadFailed')}</p>
				<p class="mt-1">{data.loadError}</p>
			</div>
		{/if}

		<section class="mt-6" aria-labelledby="summary-heading">
			<h2 id="summary-heading" class="mb-3 text-sm font-medium uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'dashboard.summary')}</h2>
			{#if data.summary}
				<div
					class="mb-3 rounded-lg p-3 text-sm"
					style="background-color: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));"
				>
					<p class="font-semibold">{t(locale, 'dashboard.conservativeTotals')}</p>
					<p class="mt-1" style="color: var(--app-muted);">
						{t(locale, 'dashboard.reportingBasis')}: <code>{data.summary.reporting_basis}</code>. {t(locale, 'dashboard.currencyConversion')}:
						{data.summary.includes_currency_conversion ? t(locale, 'dashboard.currencyConversionIncluded') : t(locale, 'dashboard.currencyConversionNotIncluded')}.
					</p>
					{#if data.summary.limitations?.length}
						<ul class="mt-1 list-disc pl-5" style="color: var(--app-muted);">
							{#each data.summary.limitations as limitation}
								<li>{limitation}</li>
							{/each}
						</ul>
					{/if}
				</div>
			{/if}
			<SummaryGrid summary={data.summary} drilldowns={data.drilldowns} {locale} />
		</section>

		<div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
			<RecentTransactions transactions={data.recentTransactions} drilldownHref={data.drilldowns.recent} {locale} />
			<ExpensesByAccount expenses={data.expenses} drilldownHrefs={data.drilldowns.expensesByAccount} {locale} />
		</div>

		<section class="mt-6" aria-labelledby="cashflow-heading">
			<h2 id="cashflow-heading" class="sr-only">{t(locale, 'dashboard.cashflow')}</h2>
			<CashflowSummary periods={data.cashflowPeriods} drilldownHrefs={data.drilldowns.cashflowByMonth} {locale} />
		</section>
		{/if}
</main>
