<script lang="ts">
	import BalanceCard from '$lib/components/BalanceCard.svelte';
	import type { DashboardDrilldownLinks, ReportSummary } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import { isNonNegativeDecimalString } from '$lib/money.js';

	let {
		summary,
		drilldowns,
		locale = DEFAULT_LOCALE,
		settingsHref = '/books',
		isAdmin = false
	}: {
		summary: ReportSummary | null;
		drilldowns?: DashboardDrilldownLinks;
		locale?: Locale;
		settingsHref?: string;
		isAdmin?: boolean;
	} = $props();

	const readySummary = $derived(summary?.status === 'ready' ? summary : null);
	const setupSummary = $derived(summary?.status === 'setup_required' ? summary : null);
	const reportingCurrency = $derived(summary?.reporting_currency ?? null);
	const selectedCurrency = $derived(reportingCurrency?.selected_currency ?? readySummary?.currency ?? null);
	const excludedCurrencies = $derived(reportingCurrency?.excluded_currencies ?? []);

	function reportingCurrencySource(): string {
		if (!reportingCurrency) return t(locale, 'dashboard.reportingCurrencyNone');
		if (reportingCurrency.source === 'configured') return t(locale, 'dashboard.reportingCurrencyConfigured');
		if (reportingCurrency.source === 'detected') return t(locale, 'dashboard.reportingCurrencyDetected');
		return t(locale, 'dashboard.reportingCurrencyNone');
	}

	function setupReason(): string {
		return reportingCurrency?.reason === 'dominance_tie'
			? t(locale, 'dashboard.setupReason.dominance_tie')
			: t(locale, 'dashboard.setupReason.no_eligible_currency');
	}
</script>

{#if readySummary}
	<div class="mb-3 rounded-lg p-3 text-sm" style="background-color: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text); border: 1px solid color-mix(in srgb, var(--app-warning) 55%, var(--app-border));">
		<p class="font-semibold">{t(locale, 'dashboard.conservativeTotals')}</p>
		<p class="mt-1" style="color: var(--app-muted);">
			{t(locale, 'dashboard.reportingCurrency')}: <strong style="color: var(--app-text);">{selectedCurrency}</strong>
			<span> · {reportingCurrencySource()}</span>
			<span> · {t(locale, 'dashboard.reportingBasis')}: <code>{readySummary.reporting_basis}</code></span>
			<span> · {t(locale, 'dashboard.currencyConversion')}: {readySummary.includes_currency_conversion ? t(locale, 'dashboard.currencyConversionIncluded') : t(locale, 'dashboard.currencyConversionNotIncluded')}</span>
		</p>
		{#if excludedCurrencies.length}
			<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.excludedCurrencies', { currencies: excludedCurrencies.join(', ') })}</p>
		{/if}
		{#if reportingCurrency?.non_currency_commodities_excluded}
			<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.nonCurrencyCommoditiesExcluded')}</p>
		{/if}
	</div>
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<BalanceCard
			label={t(locale, 'dashboard.netWorth')}
			value={readySummary.net_worth}
			currency={readySummary.currency}
			trend={isNonNegativeDecimalString(readySummary.net_worth) ? 'up' : 'down'}
		/>
		<BalanceCard
			label={t(locale, 'dashboard.assets')}
			value={readySummary.assets}
			currency={readySummary.currency}
			trend="up"
		/>
		<BalanceCard
			label={t(locale, 'dashboard.liabilities')}
			value={readySummary.liabilities}
			currency={readySummary.currency}
			trend="down"
		/>
		<div class="space-y-2">
			<BalanceCard
				label={t(locale, 'dashboard.incomeThisMonth')}
				value={readySummary.income_this_month}
				currency={readySummary.currency}
				trend="up"
			/>
			<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={drilldowns?.incomeThisMonth ?? '/transactions?limit=50&offset=0'}>{t(locale, 'dashboard.viewMonthlyFilter')}</a>
		</div>
		<div class="space-y-2">
			<BalanceCard
				label={t(locale, 'dashboard.expensesThisMonth')}
				value={readySummary.expenses_this_month}
				currency={readySummary.currency}
				trend="down"
			/>
			<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={drilldowns?.expensesThisMonth ?? '/transactions?limit=50&offset=0'}>{t(locale, 'dashboard.viewMonthlyFilter')}</a>
		</div>
	</div>
	<p class="mt-3 text-xs" style="color: var(--app-muted);">
		{t(locale, 'dashboard.drilldownSafety')}
	</p>
{:else if setupSummary}
	<section class="rounded-2xl border p-4" role="status" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel)); color: var(--app-text);">
		<p class="font-semibold">{t(locale, 'dashboard.setupRequiredTitle')}</p>
		<p class="mt-2 text-sm" style="color: var(--app-muted);">{isAdmin ? t(locale, 'dashboard.setupRequiredAdmin') : t(locale, 'dashboard.setupRequiredUser')}</p>
		<p class="mt-2 text-sm" style="color: var(--app-muted);">{setupReason()}</p>
		<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'dashboard.configuredCurrencyStatus', { status: reportingCurrency?.configured_currency_status ?? 'unknown' })}</p>
		{#if reportingCurrency?.candidates?.length}
			<ul class="mt-3 flex flex-wrap gap-2 text-xs" aria-label={t(locale, 'dashboard.reportingCurrency')}>
				{#each reportingCurrency.candidates as candidate (candidate.currency)}
					<li class="rounded-full border px-2 py-1" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);">{candidate.currency}</li>
				{/each}
			</ul>
		{/if}
		{#if isAdmin}
			<a class="mt-3 inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" href={settingsHref}>{t(locale, 'dashboard.setupAction')}</a>
		{/if}
	</section>
{:else}
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each Array(5) as _}
			<div class="animate-pulse rounded-xl p-5" style="background-color: var(--app-elevated-bg);">
				<div class="h-3 w-24 rounded" style="background-color: var(--app-border);"></div>
				<div class="mt-3 h-7 w-32 rounded" style="background-color: var(--app-border);"></div>
			</div>
		{/each}
	</div>
{/if}
