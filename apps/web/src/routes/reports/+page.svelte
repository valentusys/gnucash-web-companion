<script lang="ts">
	import { navigating } from '$app/state';
	import { onMount } from 'svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import { compareDecimalStrings, decimalBarWidthPercent, isNonNegativeDecimalString } from '$lib/money.js';
	import type { PageData } from './$types';

	const EXPENSE_CHANGE_PREVIEW_LIMIT = 5;

	let { data }: { data: PageData } = $props();
	// Keep desktop/no-JS controls available in SSR; hydrate to the active viewport.
	let filterControlsOpen = $state(true);
	type ComparisonReport = NonNullable<PageData['comparisonReport']>;
	type SourceReport = ComparisonReport['primary'];
	type MoneyDeltaItem = NonNullable<ComparisonReport['cashflowDelta']>['inflow'];
	type SummaryDelta = NonNullable<ComparisonReport['summaryDelta']>;
	type CashflowDelta = NonNullable<ComparisonReport['cashflowDelta']>;
	type ExpenseChangeItem = ComparisonReport['expenseChanges'][number];
	type ComparableExpenseChangeItem = ExpenseChangeItem & { status: 'ok'; delta: string; absoluteDelta: string };

	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/reports');
	let comparisonReport = $derived(data.comparisonReport);
	let comparableExpenseChanges = $derived(comparisonReport?.expenseChanges.filter(isComparableExpenseChange) ?? []);
	let topExpenseChanges = $derived(comparisonReport?.expenseChanges.slice(0, EXPENSE_CHANGE_PREVIEW_LIMIT) ?? []);
	let remainingExpenseChanges = $derived(comparisonReport?.expenseChanges.slice(EXPENSE_CHANGE_PREVIEW_LIMIT) ?? []);
	let largestExpenseIncrease = $derived(
		comparableExpenseChanges.find((expense) => compareDecimalStrings(expense.delta, '0') > 0)
	);
	let largestExpenseDecrease = $derived(
		comparableExpenseChanges.find((expense) => compareDecimalStrings(expense.delta, '0') < 0)
	);
	let sectionWarnings = $derived(data.sectionWarnings);

	onMount(() => {
		const desktop = window.matchMedia('(min-width: 768px)');
		const syncFilterDisclosure = () => {
			filterControlsOpen = desktop.matches;
		};

		syncFilterDisclosure();
		desktop.addEventListener('change', syncFilterDisclosure);
		return () => desktop.removeEventListener('change', syncFilterDisclosure);
	});

	let hasComparisonData = $derived(
		Boolean(
			comparisonReport &&
				!comparisonReport.empty &&
				(sourceHasData(comparisonReport.primary) ||
					sourceHasData(comparisonReport.comparison) ||
					comparisonReport.summaryDelta ||
					comparisonReport.cashflowDelta ||
					comparisonReport.expenseChanges.length)
		)
	);

	function displayMoney(value: string | null | undefined): string {
		return value && value.trim() ? value : '—';
	}

	function sourceHasData(source: SourceReport | null | undefined): boolean {
		return Boolean(source && (source.summary || source.cashflow || source.cashflowMonthly.length || source.expensesByAccount.length));
	}

	function toneFor(value: string | null | undefined): string {
		if (!value) return 'var(--app-muted)';
		return isNonNegativeDecimalString(value) ? 'var(--app-success)' : 'var(--app-danger)';
	}

	function deltaTone(delta: MoneyDeltaItem): string {
		const comparison = compareDecimalStrings(delta.delta, '0');
		if (comparison === 0) return 'var(--app-muted)';
		return comparison > 0 ? 'var(--app-success)' : 'var(--app-danger)';
	}

	function expenseDeltaTone(delta: MoneyDeltaItem): string {
		const comparison = compareDecimalStrings(delta.delta, '0');
		if (comparison === 0) return 'var(--app-muted)';
		return comparison > 0 ? 'var(--app-danger)' : 'var(--app-success)';
	}

	function changeLabel(delta: MoneyDeltaItem, activeLocale: Locale): string {
		const comparison = compareDecimalStrings(delta.delta, '0');
		if (comparison === 0) return t(activeLocale, 'reports.comparison.unchanged');
		return comparison > 0 ? t(activeLocale, 'reports.comparison.increase') : t(activeLocale, 'reports.comparison.decrease');
	}

	function summaryItems(summary: NonNullable<SourceReport['summary']>, activeLocale: Locale) {
		return [
			{ label: t(activeLocale, 'reports.summary.income'), value: summary.income, tone: 'var(--app-success)' },
			{ label: t(activeLocale, 'reports.summary.expenses'), value: summary.expenses, tone: 'var(--app-danger)' },
			{ label: t(activeLocale, 'reports.summary.netPeriodResult'), value: summary.net, tone: toneFor(summary.net) },
			{ label: t(activeLocale, 'reports.summary.netWorth'), value: summary.netWorth, tone: toneFor(summary.netWorth) },
			{ label: t(activeLocale, 'reports.summary.assets'), value: summary.assets, tone: 'var(--app-success)' },
			{ label: t(activeLocale, 'reports.summary.liabilities'), value: summary.liabilities, tone: 'var(--app-danger)' }
		].filter((item) => item.value !== null && item.value !== undefined && item.value !== '');
	}

	function summaryDeltaItems(delta: SummaryDelta, activeLocale: Locale) {
		return [
			{ id: 'net-worth', label: t(activeLocale, 'reports.summary.netWorth'), delta: delta.netWorth },
			{ id: 'assets', label: t(activeLocale, 'reports.summary.assets'), delta: delta.assets },
			{ id: 'liabilities', label: t(activeLocale, 'reports.summary.liabilities'), delta: delta.liabilities }
		];
	}

	function cashflowDeltaItems(delta: CashflowDelta, activeLocale: Locale) {
		return [
			{ id: 'inflow', label: t(activeLocale, 'reports.cashflow.inflow'), delta: delta.inflow },
			{ id: 'outflow', label: t(activeLocale, 'reports.cashflow.outflow'), delta: delta.outflow },
			{ id: 'net', label: t(activeLocale, 'reports.cashflow.net'), delta: delta.net }
		];
	}

	function isComparableExpenseChange(expense: ExpenseChangeItem): expense is ComparableExpenseChangeItem {
		return expense.status === 'ok' && Boolean(expense.delta && expense.absoluteDelta);
	}

	function expenseDeltaItem(expense: ComparableExpenseChangeItem): MoneyDeltaItem {
		return {
			primary: expense.primaryTotal,
			comparison: expense.comparisonTotal,
			delta: expense.delta,
			absoluteDelta: expense.absoluteDelta,
			currency: expense.currency
		};
	}

	function expenseChangeBar(expense: ComparableExpenseChangeItem, allExpenses: ComparableExpenseChangeItem[]): string {
		return decimalBarWidthPercent(expense.absoluteDelta, allExpenses.map((item) => item.absoluteDelta));
	}

	function sourceName(source: 'primary' | 'comparison', activeLocale: Locale): string {
		return source === 'primary' ? t(activeLocale, 'reports.comparison.primarySide') : t(activeLocale, 'reports.comparison.comparisonSide');
	}
</script>

<svelte:head>
	<title>{t(locale, 'reports.metaTitle')} — GnuCash Web Companion</title>
</svelte:head>

{#snippet expenseChangeRow(expense: ExpenseChangeItem)}
	<li data-expense-change-row class="rounded-xl p-3" style="background: var(--app-bg);">
		<div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
			<div class="min-w-0">
				<p class="truncate font-semibold">{expense.accountName}</p>
				{#if isComparableExpenseChange(expense)}
					{@const rowDelta = expenseDeltaItem(expense)}
					<p class="text-sm" style={`color: ${expenseDeltaTone(rowDelta)};`}>{changeLabel(rowDelta, locale)}</p>
				{:else}
					<p class="text-sm" style="color: var(--app-warning);">{t(locale, 'reports.comparison.rowNotComparable')}</p>
				{/if}
			</div>
			{#if isComparableExpenseChange(expense)}
				{@const rowDelta = expenseDeltaItem(expense)}
				<div class="text-left tabular-nums sm:text-right">
					<p class="text-lg font-bold" style={`color: ${expenseDeltaTone(rowDelta)};`}>{expense.delta}</p>
					<p class="text-xs" style="color: var(--app-muted);">{t(locale, 'reports.comparison.absoluteChange')}: {expense.absoluteDelta} {expense.currency}</p>
				</div>
			{:else}
				<div class="text-left tabular-nums sm:text-right">
					<p class="text-lg font-bold" style="color: var(--app-warning);">—</p>
					<p class="text-xs" style="color: var(--app-muted);">{expense.currency}</p>
				</div>
			{/if}
		</div>
		<div class="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
			<a class="rounded-lg border p-2 font-semibold" style="border-color: var(--app-border); color: var(--app-accent);" href={data.drilldowns.expenseChanges[expense.accountId]?.primary ?? data.drilldowns.primary.period}>
				{t(locale, 'reports.comparison.primarySide')}: <span class="tabular-nums">{expense.primaryTotal}</span>
			</a>
			<a class="rounded-lg border p-2 font-semibold" style="border-color: var(--app-border); color: var(--app-accent);" href={data.drilldowns.expenseChanges[expense.accountId]?.comparison ?? data.drilldowns.comparison.period}>
				{t(locale, 'reports.comparison.comparisonSide')}: <span class="tabular-nums">{expense.comparisonTotal}</span>
			</a>
		</div>
		{#if isComparableExpenseChange(expense)}
			<div class="mt-3 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
				<div
					class="h-full rounded-full"
					style={`width: ${expenseChangeBar(expense, comparableExpenseChanges)}; background: ${expenseDeltaTone(expenseDeltaItem(expense))};`}
				></div>
			</div>
		{/if}
	</li>
{/snippet}

<main class="mx-auto max-w-6xl px-4 py-6 md:py-8" style="color: var(--app-text);">
	<header class="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'reports.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold">{t(locale, 'reports.title')}</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.bookLabel', { name: data.activeBook.name })}</p>
			{/if}
		</div>
		<a
			class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
			style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);"
			href={data.drilldowns.primary.period}
		>
			{t(locale, 'reports.viewTransactionsPeriod')}
		</a>
	</header>

	<section class="mb-5 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-label={t(locale, 'reports.filters.title')}>
		<details id="reports-filter-controls" bind:open={filterControlsOpen}>
			<summary class="cursor-pointer font-semibold md:hidden">{t(locale, 'reports.filters.title')}</summary>
			<div class="reports-filter-content mt-4 md:mt-0">
		<div class="grid gap-4 lg:grid-cols-2">
			<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
				<legend id="report-period-heading" class="px-1 text-lg font-semibold">{t(locale, 'reports.period.title')}</legend>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.period.help', { dateFrom: data.period.dateFrom, dateTo: data.period.dateTo })}</p>
				<nav class="mt-3 flex flex-wrap gap-2" aria-label={t(locale, 'reports.period.presetsAria')}>
					{#each data.presetOptions as preset}
						<a
							href={preset.href}
							aria-current={preset.active ? 'page' : undefined}
							class="inline-flex min-h-11 items-center rounded-xl border px-3 py-2 text-sm font-semibold"
							style={preset.active
								? 'border-color: var(--app-accent); background: var(--app-accent); color: white;'
								: 'border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);'}
						>
							{preset.label}
						</a>
					{/each}
				</nav>
			</fieldset>

			<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
				<legend class="px-1 text-lg font-semibold">{t(locale, 'reports.comparison.title')}</legend>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.comparison.help', { dateFrom: data.comparisonPeriod.dateFrom, dateTo: data.comparisonPeriod.dateTo })}</p>
				<nav class="mt-3 flex flex-wrap gap-2" aria-label={t(locale, 'reports.comparison.modeAria')}>
					{#each data.comparisonModeOptions as mode}
						<a
							href={mode.href}
							aria-current={mode.active ? 'page' : undefined}
							class="inline-flex min-h-11 items-center rounded-xl border px-3 py-2 text-sm font-semibold"
							style={mode.active
								? 'border-color: var(--app-accent); background: var(--app-accent); color: white;'
								: 'border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);'}
						>
							{mode.label}
						</a>
					{/each}
				</nav>
			</fieldset>
		</div>

		<details id="reports-custom-ranges" class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background: var(--app-bg);">
			<summary class="cursor-pointer font-semibold">{t(locale, 'reports.filters.customTitle')}</summary>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.filters.customHelp')}</p>
			<div class="mt-4 grid gap-5 lg:grid-cols-2">
				<form method="GET" action="/reports" class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label={t(locale, 'reports.period.customAria')}>
					<input type="hidden" name="preset" value="custom" />
					<input type="hidden" name="comparison_mode" value={data.comparisonPeriod.mode} />
					<input type="hidden" name="comparison_date_from" value={data.comparisonPeriod.dateFrom} />
					<input type="hidden" name="comparison_date_to" value={data.comparisonPeriod.dateTo} />
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.period.dateFrom')}</span>
						<input class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" type="date" name="date_from" value={data.period.dateFrom} required />
					</label>
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.period.dateTo')}</span>
						<input class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" type="date" name="date_to" value={data.period.dateTo} required />
					</label>
					<button class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">{t(locale, 'reports.period.applyCustom')}</button>
				</form>

				<form method="GET" action="/reports" class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label={t(locale, 'reports.comparison.customAria')}>
					<input type="hidden" name="preset" value={data.selectedPreset} />
					<input type="hidden" name="date_from" value={data.period.dateFrom} />
					<input type="hidden" name="date_to" value={data.period.dateTo} />
					<input type="hidden" name="comparison_mode" value="custom" />
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.comparison.dateFrom')}</span>
						<input class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" type="date" name="comparison_date_from" value={data.comparisonPeriod.dateFrom} required />
					</label>
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.comparison.dateTo')}</span>
						<input class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-text);" type="date" name="comparison_date_to" value={data.comparisonPeriod.dateTo} required />
					</label>
					<button class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">{t(locale, 'reports.comparison.applyCustom')}</button>
				</form>
			</div>
		</details>
			</div>
		</details>
	</section>

	{#if isRouteLoading}
		<LoadingState variant="dashboard" message={t(locale, 'reports.loading')} />
	{:else if data.validationError}
		<section class="rounded-2xl border p-4" style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));" role="alert" aria-labelledby="reports-invalid-range-title">
			<h2 id="reports-invalid-range-title" class="text-lg font-semibold" style="color: var(--app-danger);">{t(locale, 'reports.validation.invalidTitle')}</h2>
			<p class="mt-1 text-sm">{data.validationError}</p>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.validation.invalidNoRequest')}</p>
		</section>
	{:else}
		{#if data.loadError}
			<section class="mb-5 rounded-2xl border p-4" style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));" role="alert" aria-labelledby="reports-load-error-title">
				<h2 id="reports-load-error-title" class="text-lg font-semibold" style="color: var(--app-danger);">{t(locale, 'reports.error.title')}</h2>
				<p class="mt-1 text-sm">{data.loadError}</p>
				<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.error.redactedHelp')}</p>
			</section>
		{/if}

		{#if !hasComparisonData && !data.loadError && !sectionWarnings.length}
			<EmptyState title={t(locale, 'reports.empty.title')} message={t(locale, 'reports.empty.message')} ariaLabel={t(locale, 'reports.empty.aria')} icon="📊">
				<a href={data.drilldowns.primary.period} class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);">{t(locale, 'reports.empty.action')}</a>
			</EmptyState>
		{:else if comparisonReport}
			{#if sectionWarnings.length}
				<section id="partial-error-report" class="mb-5 rounded-2xl border p-4" style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel));" role="alert" aria-labelledby="reports-partial-title">
					<h2 id="reports-partial-title" class="text-lg font-semibold">{t(locale, 'reports.partial.title')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.partial.help')}</p>
					<ul class="mt-3 list-disc space-y-1 pl-5 text-sm">
						{#each sectionWarnings as warning}
							<li><span class="font-semibold">{sourceName(warning.source, locale)} · {warning.section}</span>: {warning.message}</li>
						{/each}
					</ul>
				</section>
			{/if}

			<section class="mb-5 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-executive-title">
				<h2 id="reports-executive-title" class="text-xl font-semibold">{t(locale, 'reports.executive.title')}</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.executive.help', {
					primaryFrom: comparisonReport.primary.requestedPeriod.dateFrom,
					primaryTo: comparisonReport.primary.requestedPeriod.dateTo,
					comparisonFrom: comparisonReport.comparison.requestedPeriod.dateFrom,
					comparisonTo: comparisonReport.comparison.requestedPeriod.dateTo
				})}</p>
				<div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-bg);">
						<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'reports.executive.netCashChange')}</p>
						{#if comparisonReport.deltaSectionMessages.cashflow}
							<p class="mt-2 text-sm" style="color: var(--app-warning);">{comparisonReport.deltaSectionMessages.cashflow}</p>
						{:else if comparisonReport.cashflowDelta}
							<p class="mt-2 text-2xl font-bold tabular-nums" style={`color: ${deltaTone(comparisonReport.cashflowDelta.net)};`}>{comparisonReport.cashflowDelta.net.delta} {comparisonReport.cashflowDelta.net.currency}</p>
							<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.executive.netCashHelp')}</p>
						{:else}
							<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.executive.unavailable')}</p>
						{/if}
					</article>

					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-bg);">
						<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'reports.executive.largestIncrease')}</p>
						{#if comparisonReport.deltaSectionMessages.expenses_by_account}
							<p class="mt-2 text-sm" style="color: var(--app-warning);">{comparisonReport.deltaSectionMessages.expenses_by_account}</p>
						{:else if largestExpenseIncrease}
							<p class="mt-2 truncate font-semibold">{largestExpenseIncrease.accountName}</p>
							<p class="mt-1 text-2xl font-bold tabular-nums" style="color: var(--app-danger);">{largestExpenseIncrease.delta}</p>
							<p class="text-xs" style="color: var(--app-muted);">{largestExpenseIncrease.currency}</p>
						{:else}
							<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.executive.noIncrease')}</p>
						{/if}
					</article>

					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-bg);">
						<p class="text-sm font-semibold" style="color: var(--app-muted);">{t(locale, 'reports.executive.largestDecrease')}</p>
						{#if comparisonReport.deltaSectionMessages.expenses_by_account}
							<p class="mt-2 text-sm" style="color: var(--app-warning);">{comparisonReport.deltaSectionMessages.expenses_by_account}</p>
						{:else if largestExpenseDecrease}
							<p class="mt-2 truncate font-semibold">{largestExpenseDecrease.accountName}</p>
							<p class="mt-1 text-2xl font-bold tabular-nums" style="color: var(--app-success);">{largestExpenseDecrease.delta}</p>
							<p class="text-xs" style="color: var(--app-muted);">{largestExpenseDecrease.currency}</p>
						{:else}
							<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.executive.noDecrease')}</p>
						{/if}
					</article>
				</div>
			</section>

			<section class="mb-5 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-expense-changes-title">
				<h2 id="reports-expense-changes-title" class="text-xl font-semibold">{t(locale, 'reports.comparison.expenseChangesTitle')}</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.comparison.expenseChangesHelp')}</p>
				<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.comparison.topChangesHelp')}</p>
				{#if comparisonReport.deltaSectionMessages.expenses_by_account}
					<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{comparisonReport.deltaSectionMessages.expenses_by_account}</p>
				{:else if comparisonReport.expenseChanges.length}
					<ul data-expense-change-list="top" class="mt-4 space-y-3">
						{#each topExpenseChanges as expense (expense.accountId)}
							{@render expenseChangeRow(expense)}
						{/each}
					</ul>
					{#if remainingExpenseChanges.length}
						<details id="reports-expense-changes-more" class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border);">
							<summary class="cursor-pointer font-semibold" style="color: var(--app-accent);">{t(locale, 'reports.comparison.showRemaining', { count: remainingExpenseChanges.length })}</summary>
							<ul data-expense-change-list="remaining" class="mt-3 space-y-3">
								{#each remainingExpenseChanges as expense (expense.accountId)}
									{@render expenseChangeRow(expense)}
								{/each}
							</ul>
						</details>
					{/if}
				{:else}
					<p class="mt-4 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.comparison.noExpenseChanges')}</p>
				{/if}
			</section>

			<details id="reports-technical-contract" class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
				<summary class="cursor-pointer text-lg font-semibold">{t(locale, 'reports.technical.title')}</summary>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.technical.help')}</p>
				<ul class="mt-4 list-disc space-y-2 pl-5 text-sm" style="color: var(--app-muted);">
					<li>{t(locale, 'reports.comparison.zeroHint')}</li>
					<li>{t(locale, 'reports.technical.readOnly')}</li>
					<li>{comparisonReport.includesCurrencyConversion ? t(locale, 'reports.technical.currencyConversionIncluded') : t(locale, 'reports.technical.baseCurrencyNoFx')}</li>
					{#if comparisonReport.reportingBasis === 'unknown'}
						<li>{t(locale, 'reports.technical.unknownBasis')}</li>
					{/if}
					{#if comparisonReport.limitationsReported}
						<li>{t(locale, 'reports.technical.limitationsReported')}</li>
					{/if}
					<li>{t(locale, 'reports.technical.balanceSemantics')}</li>
					<li>{t(locale, 'reports.technical.exactDrilldowns')}</li>
				</ul>

				<section class="mt-5" aria-labelledby="reports-source-periods-title">
					<h2 id="reports-source-periods-title" class="text-lg font-semibold">{t(locale, 'reports.comparison.sourcePeriodsTitle')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.comparison.sourcePeriodsHelp')}</p>
					<div class="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
						{#each [
							{ id: 'primary', title: t(locale, 'reports.comparison.primarySide'), report: comparisonReport.primary, href: data.drilldowns.primary.period },
							{ id: 'comparison', title: t(locale, 'reports.comparison.comparisonSide'), report: comparisonReport.comparison, href: data.drilldowns.comparison.period }
						] as source (source.id)}
							<article class="rounded-xl border p-3" style="border-color: var(--app-border); background: var(--app-bg);">
								<div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
									<div>
										<h3 class="font-semibold">{source.title}</h3>
										<p class="whitespace-nowrap text-sm" style="color: var(--app-muted);">{source.report.requestedPeriod.dateFrom} → {source.report.requestedPeriod.dateTo}</p>
									</div>
									<a class="text-sm font-semibold" style="color: var(--app-accent);" href={source.href}>{t(locale, 'reports.summary.openFilter')}</a>
								</div>
								{#if source.report.summary}
									<div class="mt-3 grid grid-cols-2 gap-2">
										{#each summaryItems(source.report.summary, locale) as item}
											<div class="rounded-lg p-2" style="background: var(--app-panel);">
												<p class="text-xs" style="color: var(--app-muted);">{item.label}</p>
												<p class="font-bold tabular-nums" style={`color: ${item.tone};`}>{displayMoney(item.value)}</p>
											</div>
										{/each}
									</div>
								{:else}
									<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.summary.noTotals')}</p>
								{/if}
							</article>
						{/each}
					</div>
				</section>

				{#if comparisonReport.deltaSectionMessages.summary}
					<p class="mt-5 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{comparisonReport.deltaSectionMessages.summary}</p>
				{:else if comparisonReport.summaryDelta}
					<section class="mt-5" aria-labelledby="reports-summary-delta-title">
						<h2 id="reports-summary-delta-title" class="text-lg font-semibold">{t(locale, 'reports.comparison.summaryDeltaTitle')}</h2>
						<div class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
							{#each summaryDeltaItems(comparisonReport.summaryDelta, locale) as item (item.id)}
								<div class="rounded-xl border p-3" style="border-color: var(--app-border); background: var(--app-bg);">
									<p class="text-sm" style="color: var(--app-muted);">{item.label}</p>
									<p class="mt-1 font-bold tabular-nums" style={`color: ${deltaTone(item.delta)};`}>{item.delta.delta}</p>
									<p class="text-xs" style="color: var(--app-muted);">{item.delta.primary} / {item.delta.comparison} {item.delta.currency}</p>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				{#if comparisonReport.cashflowDelta}
					<section class="mt-5" aria-labelledby="reports-cashflow-delta-title">
						<h2 id="reports-cashflow-delta-title" class="text-lg font-semibold">{t(locale, 'reports.comparison.cashflowDeltaTitle')}</h2>
						<div class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
							{#each cashflowDeltaItems(comparisonReport.cashflowDelta, locale) as item (item.id)}
								<div class="rounded-xl border p-3" style="border-color: var(--app-border); background: var(--app-bg);">
									<p class="text-sm" style="color: var(--app-muted);">{item.label}</p>
									<p class="mt-1 font-bold tabular-nums" style={`color: ${deltaTone(item.delta)};`}>{item.delta.delta}</p>
									<p class="text-xs" style="color: var(--app-muted);">{item.delta.primary} / {item.delta.comparison} {item.delta.currency}</p>
								</div>
							{/each}
						</div>
					</section>
				{/if}
			</details>
		{/if}
	{/if}
</main>

<style>
	@media (min-width: 768px) {
		#reports-filter-controls > summary {
			display: none;
		}
	}
</style>
