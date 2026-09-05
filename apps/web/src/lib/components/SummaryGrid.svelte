<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type {
		CashflowData,
		DashboardDrilldownLinks,
		DashboardExpenseChange,
		DashboardUpcomingObligations,
		ReportSummary
	} from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import { compareDecimalStrings, decimalBarWidthPercent, isNonNegativeDecimalString } from '$lib/money.js';

	let {
		summary,
		drilldowns,
		monthCashflow = null,
		expenseChanges = [],
		upcomingObligations = { enabled_count: 0, unavailable_count: 0 },
		comparisonPeriod = { date_from: '', date_to: '' },
		changesUnavailable = false,
		obligationsUnavailable = false,
		locale = DEFAULT_LOCALE,
		settingsHref = '/books',
		isAdmin = false
	}: {
		summary: ReportSummary | null;
		drilldowns?: DashboardDrilldownLinks;
		monthCashflow?: CashflowData | null;
		expenseChanges?: DashboardExpenseChange[];
		upcomingObligations?: DashboardUpcomingObligations;
		comparisonPeriod?: { date_from: string; date_to: string };
		changesUnavailable?: boolean;
		obligationsUnavailable?: boolean;
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

	function changeTone(value: string): string {
		const comparison = compareDecimalStrings(value, '0');
		if (comparison === 0) return 'var(--app-muted)';
		return comparison > 0 ? 'var(--app-danger)' : 'var(--app-success)';
	}

	function changeLabel(value: string): string {
		const comparison = compareDecimalStrings(value, '0');
		if (comparison === 0) return t(locale, 'dashboard.changeUnchanged');
		return comparison > 0 ? t(locale, 'dashboard.changeIncrease') : t(locale, 'dashboard.changeDecrease');
	}

	function changeBarWidth(change: DashboardExpenseChange): string {
		return decimalBarWidthPercent(
			change.absolute_delta,
			expenseChanges.map((candidate) => candidate.absolute_delta)
		);
	}
</script>

{#if readySummary}
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
		<article
			data-dashboard-decision="position"
			class="min-w-0 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow);"
		>
			<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'dashboard.position')}</p>
			<p class="mt-2 min-w-0 text-2xl font-bold tabular-nums" style={`color: ${isNonNegativeDecimalString(readySummary.net_worth) ? 'var(--app-success)' : 'var(--app-danger)'};`}>
				<Money amount={readySummary.net_worth} currency={readySummary.currency} />
			</p>
			<p class="mt-2 text-xs" style="color: var(--app-muted);">
				{t(locale, 'dashboard.asOf')} <time data-dashboard-date class="whitespace-nowrap" datetime={readySummary.as_of_date}>{readySummary.as_of_date}</time>
			</p>
		</article>

		<article
			data-dashboard-decision="month-result"
			class="min-w-0 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow);"
		>
			<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'dashboard.monthResult')}</p>
			{#if monthCashflow}
				<p class="mt-2 min-w-0 text-2xl font-bold tabular-nums" style={`color: ${isNonNegativeDecimalString(monthCashflow.net) ? 'var(--app-success)' : 'var(--app-danger)'};`}>
					<Money amount={monthCashflow.net} currency={monthCashflow.currency} />
				</p>
				<dl class="mt-3 grid grid-cols-2 gap-2 text-xs">
					<div>
						<dt style="color: var(--app-muted);">{t(locale, 'dashboard.cashflowIn')}</dt>
						<dd class="mt-0.5 min-w-0 font-semibold tabular-nums"><Money amount={monthCashflow.inflow} currency={monthCashflow.currency} /></dd>
					</div>
					<div>
						<dt style="color: var(--app-muted);">{t(locale, 'dashboard.cashflowOut')}</dt>
						<dd class="mt-0.5 min-w-0 font-semibold tabular-nums"><Money amount={monthCashflow.outflow} currency={monthCashflow.currency} /></dd>
					</div>
				</dl>
			{:else}
				<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'dashboard.monthResultUnavailable')}</p>
			{/if}
		</article>

		<article
			data-dashboard-decision="largest-changes"
			class="min-w-0 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow);"
		>
			<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'dashboard.largestChanges')}</p>
			{#if changesUnavailable}
				<p class="mt-3 text-sm" style="color: var(--app-warning);">{t(locale, 'dashboard.largestChangesUnavailable')}</p>
			{:else if expenseChanges.length}
				<ul class="mt-2 space-y-2">
					{#each expenseChanges as change (change.account_id)}
						<li class="min-w-0 text-xs">
							<div class="flex min-w-0 items-baseline justify-between gap-2">
								<span class="truncate font-medium" title={change.account_name}>{change.account_name}</span>
								<span class="shrink-0 font-semibold tabular-nums" style={`color: ${changeTone(change.delta)};`}><Money amount={change.delta} currency={change.currency} /></span>
							</div>
							<div class="mt-1 h-1 overflow-hidden rounded-full" style="background: var(--app-elevated-bg);">
								<div class="h-full rounded-full" style={`width: ${changeBarWidth(change)}; background: ${changeTone(change.delta)};`}></div>
							</div>
							<span class="sr-only">{changeLabel(change.delta)}</span>
						</li>
					{/each}
				</ul>
				<p class="mt-2 text-[0.7rem]" style="color: var(--app-muted);">
					{t(locale, 'dashboard.comparedWith')}
					<time data-dashboard-date class="whitespace-nowrap" datetime={comparisonPeriod.date_from}>{comparisonPeriod.date_from}</time>–<time data-dashboard-date class="whitespace-nowrap" datetime={comparisonPeriod.date_to}>{comparisonPeriod.date_to}</time>
				</p>
			{:else}
				<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'dashboard.noLargestChanges')}</p>
			{/if}
		</article>

		<article
			data-dashboard-decision="upcoming-obligations"
			class="min-w-0 rounded-xl border p-4"
			style="border-color: var(--app-border); background: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow);"
		>
			<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'dashboard.upcomingObligations')}</p>
			{#if obligationsUnavailable}
				<p class="mt-3 text-sm" style="color: var(--app-warning);">{t(locale, 'dashboard.upcomingObligationsUnavailable')}</p>
			{:else}
				<p class="mt-2 text-2xl font-bold tabular-nums">{t(locale, 'dashboard.enabledSchedules', { count: upcomingObligations.enabled_count })}</p>
				<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'dashboard.nextDueUnavailable')}</p>
			{/if}
			<a class="mt-3 inline-flex text-sm font-semibold" style="color: var(--app-accent);" href="/scheduled">{t(locale, 'dashboard.reviewScheduled')}</a>
		</article>
	</div>

	<details
		data-dashboard-safety-details
		class="mt-3 rounded-xl border p-3 text-sm"
		style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);"
	>
		<summary class="cursor-pointer font-semibold">{t(locale, 'dashboard.calculationDetails')}</summary>
		<div class="mt-3 border-t pt-3" style="border-color: var(--app-border);">
			<p class="font-semibold">{t(locale, 'dashboard.conservativeTotals')}</p>
			<p class="mt-1" style="color: var(--app-muted);">
				{t(locale, 'dashboard.reportingCurrency')}: <strong style="color: var(--app-text);">{selectedCurrency}</strong>
				<span> · {reportingCurrencySource()}</span>
				<span> · {t(locale, 'dashboard.reportingBasis')}: <code>{readySummary.reporting_basis}</code></span>
				<span> · {t(locale, 'dashboard.currencyConversion')}: {readySummary.includes_currency_conversion ? t(locale, 'dashboard.currencyConversionIncluded') : t(locale, 'dashboard.currencyConversionNotIncluded')}</span>
			</p>
			<dl class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
				<div><dt style="color: var(--app-muted);">{t(locale, 'dashboard.assets')}</dt><dd class="font-semibold tabular-nums"><Money amount={readySummary.assets} currency={readySummary.currency} /></dd></div>
				<div><dt style="color: var(--app-muted);">{t(locale, 'dashboard.liabilities')}</dt><dd class="font-semibold tabular-nums"><Money amount={readySummary.liabilities} currency={readySummary.currency} /></dd></div>
				<div><dt style="color: var(--app-muted);">{t(locale, 'dashboard.incomeThisMonth')}</dt><dd class="font-semibold tabular-nums"><Money amount={readySummary.income_this_month} currency={readySummary.currency} /></dd></div>
				<div><dt style="color: var(--app-muted);">{t(locale, 'dashboard.expensesThisMonth')}</dt><dd class="font-semibold tabular-nums"><Money amount={readySummary.expenses_this_month} currency={readySummary.currency} /></dd></div>
			</dl>
			<div class="mt-3 flex flex-wrap gap-3">
				<a class="font-semibold" style="color: var(--app-accent);" href={drilldowns?.incomeThisMonth ?? '/transactions'}>{t(locale, 'dashboard.viewMonthlyFilter')}</a>
				<a class="font-semibold" style="color: var(--app-accent);" href={drilldowns?.expensesThisMonth ?? '/transactions'}>{t(locale, 'dashboard.viewMonthlyFilter')}</a>
			</div>
			{#if excludedCurrencies.length}
				<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'dashboard.excludedCurrencies', { currencies: excludedCurrencies.join(', ') })}</p>
			{/if}
			{#if reportingCurrency?.non_currency_commodities_excluded}
				<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'dashboard.nonCurrencyCommoditiesExcluded')}</p>
			{/if}
			<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'dashboard.drilldownSafety')}</p>
		</div>
	</details>
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
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
		{#each Array(4) as _}
			<div class="animate-pulse rounded-xl p-5" style="background-color: var(--app-elevated-bg);">
				<div class="h-3 w-24 rounded" style="background-color: var(--app-border);"></div>
				<div class="mt-3 h-7 w-32 rounded" style="background-color: var(--app-border);"></div>
			</div>
		{/each}
	</div>
{/if}
