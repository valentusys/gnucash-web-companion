<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import { compareDecimalStrings, decimalBarWidthPercent, isNonNegativeDecimalString } from '$lib/money.js';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	type ComparisonReport = NonNullable<PageData['comparisonReport']>;
	type SourceReport = ComparisonReport['primary'];
	type MoneyDeltaItem = NonNullable<ComparisonReport['cashflowDelta']>['inflow'];
	type SummaryDelta = NonNullable<ComparisonReport['summaryDelta']>;
	type CashflowDelta = NonNullable<ComparisonReport['cashflowDelta']>;
	type ExpenseChangeItem = ComparisonReport['expenseChanges'][number];

	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/reports');
	let comparisonReport = $derived(data.comparisonReport);
	let sectionWarnings = $derived(data.sectionWarnings);
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

	function changeLabel(delta: MoneyDeltaItem, locale: Locale): string {
		const comparison = compareDecimalStrings(delta.delta, '0');
		if (comparison === 0) return t(locale, 'reports.comparison.unchanged');
		return comparison > 0 ? t(locale, 'reports.comparison.increase') : t(locale, 'reports.comparison.decrease');
	}

	function summaryItems(summary: NonNullable<SourceReport['summary']>, locale: Locale) {
		return [
			{ label: t(locale, 'reports.summary.income'), value: summary.income, tone: 'var(--app-success)' },
			{ label: t(locale, 'reports.summary.expenses'), value: summary.expenses, tone: 'var(--app-danger)' },
			{ label: t(locale, 'reports.summary.netPeriodResult'), value: summary.net, tone: toneFor(summary.net) },
			{ label: t(locale, 'reports.summary.netWorth'), value: summary.netWorth, tone: toneFor(summary.netWorth) },
			{ label: t(locale, 'reports.summary.assets'), value: summary.assets, tone: 'var(--app-success)' },
			{ label: t(locale, 'reports.summary.liabilities'), value: summary.liabilities, tone: 'var(--app-danger)' }
		].filter((item) => item.value !== null && item.value !== undefined && item.value !== '');
	}

	function summaryDeltaItems(delta: SummaryDelta, locale: Locale) {
		return [
			{ id: 'net-worth', label: t(locale, 'reports.summary.netWorth'), delta: delta.netWorth },
			{ id: 'assets', label: t(locale, 'reports.summary.assets'), delta: delta.assets },
			{ id: 'liabilities', label: t(locale, 'reports.summary.liabilities'), delta: delta.liabilities }
		];
	}

	function cashflowDeltaItems(delta: CashflowDelta, locale: Locale) {
		return [
			{ id: 'inflow', label: t(locale, 'reports.cashflow.inflow'), delta: delta.inflow },
			{ id: 'outflow', label: t(locale, 'reports.cashflow.outflow'), delta: delta.outflow },
			{ id: 'net', label: t(locale, 'reports.cashflow.net'), delta: delta.net }
		];
	}

	function deltaBar(delta: MoneyDeltaItem, allDeltas: MoneyDeltaItem[]): string {
		return decimalBarWidthPercent(
			delta.absoluteDelta,
			allDeltas.map((item) => item.absoluteDelta)
		);
	}

	function expenseChangeBar(expense: ExpenseChangeItem): string {
		return decimalBarWidthPercent(
			expense.absoluteDelta,
			comparisonReport?.expenseChanges.map((item) => item.absoluteDelta) ?? []
		);
	}

	function sourceName(source: 'primary' | 'comparison', locale: Locale): string {
		return source === 'primary' ? t(locale, 'reports.comparison.primarySide') : t(locale, 'reports.comparison.comparisonSide');
	}
</script>

<svelte:head>
	<title>{t(locale, 'reports.metaTitle')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8" style="color: var(--app-text);">
	<header class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'reports.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold">{t(locale, 'reports.title')}</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.bookLabel', { name: data.activeBook.name })}</p>
			{/if}
			<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.localizationNotice')}</p>
		</div>
		<a
			class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
			style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);"
			href={data.drilldowns.primary.period}
		>
			{t(locale, 'reports.viewTransactionsPeriod')}
		</a>
	</header>

	<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="report-period-heading">
		<div class="grid gap-5 lg:grid-cols-2">
			<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
				<legend id="report-period-heading" class="px-1 text-lg font-semibold">{t(locale, 'reports.period.title')}</legend>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					{t(locale, 'reports.period.urlBackedHelp', { dateFrom: data.period.dateFrom, dateTo: data.period.dateTo })}
				</p>
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

				<form method="GET" action="/reports" class="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label={t(locale, 'reports.period.customAria')}>
					<input type="hidden" name="preset" value="custom" />
					<input type="hidden" name="comparison_mode" value={data.comparisonPeriod.mode} />
					<input type="hidden" name="comparison_date_from" value={data.comparisonPeriod.dateFrom} />
					<input type="hidden" name="comparison_date_to" value={data.comparisonPeriod.dateTo} />
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.period.dateFrom')}</span>
						<input
							class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
							style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);"
							type="date"
							name="date_from"
							value={data.period.dateFrom}
							required
						/>
					</label>
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.period.dateTo')}</span>
						<input
							class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
							style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);"
							type="date"
							name="date_to"
							value={data.period.dateTo}
							required
						/>
					</label>
					<button class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">
						{t(locale, 'reports.period.applyCustom')}
					</button>
				</form>
			</fieldset>

			<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
				<legend class="px-1 text-lg font-semibold">{t(locale, 'reports.comparison.title')}</legend>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					{t(locale, 'reports.comparison.urlBackedHelp', { dateFrom: data.comparisonPeriod.dateFrom, dateTo: data.comparisonPeriod.dateTo })}
				</p>
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

				<form method="GET" action="/reports" class="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label={t(locale, 'reports.comparison.customAria')}>
					<input type="hidden" name="preset" value={data.selectedPreset} />
					<input type="hidden" name="date_from" value={data.period.dateFrom} />
					<input type="hidden" name="date_to" value={data.period.dateTo} />
					<input type="hidden" name="comparison_mode" value="custom" />
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.comparison.dateFrom')}</span>
						<input
							class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
							style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);"
							type="date"
							name="comparison_date_from"
							value={data.comparisonPeriod.dateFrom}
							required
						/>
					</label>
					<label class="text-sm font-medium">
						<span>{t(locale, 'reports.comparison.dateTo')}</span>
						<input
							class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
							style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-text);"
							type="date"
							name="comparison_date_to"
							value={data.comparisonPeriod.dateTo}
							required
						/>
					</label>
					<button class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">
						{t(locale, 'reports.comparison.applyCustom')}
					</button>
				</form>
			</fieldset>
		</div>
	</section>

	{#if isRouteLoading}
		<LoadingState variant="dashboard" message={t(locale, 'reports.loading')} />
	{:else if data.validationError}
		<section
			class="rounded-2xl border p-4"
			style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
			role="alert"
			aria-labelledby="reports-invalid-range-title"
		>
			<h2 id="reports-invalid-range-title" class="text-lg font-semibold" style="color: var(--app-danger);">{t(locale, 'reports.validation.invalidTitle')}</h2>
			<p class="mt-1 text-sm" style="color: var(--app-text);">{data.validationError}</p>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.validation.invalidNoRequest')}</p>
		</section>
	{:else}
		{#if data.loadError}
			<section
				class="mb-6 rounded-2xl border p-4"
				style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
				role="alert"
				aria-labelledby="reports-load-error-title"
			>
				<h2 id="reports-load-error-title" class="text-lg font-semibold" style="color: var(--app-danger);">{t(locale, 'reports.error.title')}</h2>
				<p class="mt-1 text-sm">{data.loadError}</p>
				<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.error.redactedHelp')}</p>
			</section>
		{/if}

		{#if !hasComparisonData && !data.loadError && !sectionWarnings.length}
			<EmptyState
				title={t(locale, 'reports.empty.title')}
				message={t(locale, 'reports.empty.message')}
				ariaLabel={t(locale, 'reports.empty.aria')}
				icon="📊"
			>
				<a
					href={data.drilldowns.primary.period}
					class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background: var(--app-accent);"
				>
					{t(locale, 'reports.empty.action')}
				</a>
			</EmptyState>
		{:else if comparisonReport}
			<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-limitations-title">
				<h2 id="reports-limitations-title" class="text-lg font-semibold">{t(locale, 'reports.limitations.title')}</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					{t(locale, 'reports.limitations.reportingBasis', { reportingBasis: comparisonReport.reportingBasis || 'base_currency_only' })}
				</p>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">
					{t(locale, 'reports.comparison.zeroHint')}
				</p>
				{#if comparisonReport.limitations.length}
					<ul class="mt-3 list-disc space-y-1 pl-5 text-sm" style="color: var(--app-muted);">
						{#each comparisonReport.limitations as limitation}
							<li>{t(locale, 'reports.comparison.technicalLimitation', { limitation })}</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.limitations.none')}</p>
				{/if}
			</section>

			{#if sectionWarnings.length}
				<section
					id="partial-error-report"
					class="mb-6 rounded-2xl border p-4"
					style="border-color: var(--app-warning); background: color-mix(in srgb, var(--app-warning) 10%, var(--app-panel));"
					role="alert"
					aria-labelledby="reports-partial-title"
				>
					<h2 id="reports-partial-title" class="text-lg font-semibold">{t(locale, 'reports.partial.title')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.partial.help')}</p>
					<ul class="mt-3 list-disc space-y-1 pl-5 text-sm">
						{#each sectionWarnings as warning}
							<li><span class="font-semibold">{sourceName(warning.source, locale)} · {warning.section}</span>: {warning.message}</li>
						{/each}
					</ul>
				</section>
			{/if}

			<section class="mb-6" aria-labelledby="reports-source-periods-title">
				<h2 id="reports-source-periods-title" class="text-xl font-semibold">{t(locale, 'reports.comparison.sourcePeriodsTitle')}</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.comparison.sourcePeriodsHelp')}</p>
				<div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
					{#each [
						{ id: 'primary', title: t(locale, 'reports.comparison.primarySide'), report: comparisonReport.primary, href: data.drilldowns.primary.period },
						{ id: 'comparison', title: t(locale, 'reports.comparison.comparisonSide'), report: comparisonReport.comparison, href: data.drilldowns.comparison.period }
					] as source (source.id)}
						<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
							<div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
								<div>
									<h3 class="text-lg font-semibold">{source.title}</h3>
									<p class="text-sm" style="color: var(--app-muted);">{source.report.requestedPeriod.dateFrom} → {source.report.requestedPeriod.dateTo}</p>
								</div>
								<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={source.href}>{t(locale, 'reports.summary.openFilter')}</a>
							</div>
							{#if source.report.summary}
								<div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
									{#each summaryItems(source.report.summary, locale) as item}
										<div class="rounded-xl p-3" style="background: var(--app-bg);">
											<p class="text-xs font-medium uppercase tracking-wide" style="color: var(--app-muted);">{item.label}</p>
											<p class="mt-1 text-lg font-bold tabular-nums" style={`color: ${item.tone};`}>{displayMoney(item.value)}</p>
											<p class="text-xs" style="color: var(--app-muted);">{source.report.summary.currency}</p>
										</div>
									{/each}
								</div>
							{:else}
								<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); color: var(--app-muted);" role="status">{t(locale, 'reports.summary.noTotals')}</p>
							{/if}
						</article>
					{/each}
				</div>
			</section>

			<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-summary-delta-title">
				<h2 id="reports-summary-delta-title" class="text-xl font-semibold">{t(locale, 'reports.comparison.summaryDeltaTitle')}</h2>
				{#if comparisonReport.deltaSectionMessages.summary}
					<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{comparisonReport.deltaSectionMessages.summary}</p>
				{:else if comparisonReport.summaryDelta}
					<div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
						{#each summaryDeltaItems(comparisonReport.summaryDelta, locale) as item (item.id)}
							<article class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-bg);">
								<p class="text-sm font-medium" style="color: var(--app-muted);">{item.label}</p>
								<p class="mt-2 text-2xl font-bold tabular-nums" style={`color: ${deltaTone(item.delta)};`}>{item.delta.delta}</p>
								<p class="mt-1 text-sm font-semibold" style={`color: ${deltaTone(item.delta)};`}>{changeLabel(item.delta, locale)}</p>
								<dl class="mt-3 grid grid-cols-2 gap-2 text-xs">
									<div><dt style="color: var(--app-muted);">{t(locale, 'reports.comparison.primarySide')}</dt><dd class="tabular-nums">{item.delta.primary}</dd></div>
									<div><dt style="color: var(--app-muted);">{t(locale, 'reports.comparison.comparisonSide')}</dt><dd class="tabular-nums">{item.delta.comparison}</dd></div>
								</dl>
								<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'reports.comparison.absoluteChange')}: {item.delta.absoluteDelta} {item.delta.currency}</p>
							</article>
						{/each}
					</div>
				{:else}
					<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.comparison.emptyDelta')}</p>
				{/if}
			</section>

			<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-cashflow-delta-title">
				<h2 id="reports-cashflow-delta-title" class="text-xl font-semibold">{t(locale, 'reports.comparison.cashflowDeltaTitle')}</h2>
				{#if comparisonReport.deltaSectionMessages.cashflow}
					<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{comparisonReport.deltaSectionMessages.cashflow}</p>
				{:else if comparisonReport.cashflowDelta}
					{@const cashflowItems = cashflowDeltaItems(comparisonReport.cashflowDelta, locale)}
					<div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
						{#each cashflowItems as item (item.id)}
							<article class="rounded-xl border p-4" style="border-color: var(--app-border); background: var(--app-bg);">
								<p class="text-sm font-medium" style="color: var(--app-muted);">{item.label}</p>
								<p class="mt-2 text-2xl font-bold tabular-nums" style={`color: ${deltaTone(item.delta)};`}>{item.delta.delta}</p>
								<p class="mt-1 text-sm font-semibold" style={`color: ${deltaTone(item.delta)};`}>{changeLabel(item.delta, locale)}</p>
								<dl class="mt-3 grid grid-cols-2 gap-2 text-xs">
									<div><dt style="color: var(--app-muted);">{t(locale, 'reports.comparison.primarySide')}</dt><dd class="tabular-nums">{item.delta.primary}</dd></div>
									<div><dt style="color: var(--app-muted);">{t(locale, 'reports.comparison.comparisonSide')}</dt><dd class="tabular-nums">{item.delta.comparison}</dd></div>
								</dl>
								<div class="mt-3 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
									<div class="h-full rounded-full" style={`width: ${deltaBar(item.delta, cashflowItems.map((entry) => entry.delta))}; background: var(--app-accent);`}></div>
								</div>
							</article>
						{/each}
					</div>
				{:else}
					<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.comparison.emptyDelta')}</p>
				{/if}
			</section>

			<section class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-expense-changes-title">
				<div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
					<div>
						<h2 id="reports-expense-changes-title" class="text-xl font-semibold">{t(locale, 'reports.comparison.expenseChangesTitle')}</h2>
						<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.comparison.expenseChangesHelp')}</p>
					</div>
				</div>
				{#if comparisonReport.deltaSectionMessages.expenses_by_account}
					<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{comparisonReport.deltaSectionMessages.expenses_by_account}</p>
				{:else if comparisonReport.expenseChanges.length}
					<ul class="mt-4 space-y-3">
						{#each comparisonReport.expenseChanges as expense (expense.accountId)}
							<li class="rounded-xl p-3" style="background: var(--app-bg);">
								<div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
									<div class="min-w-0">
										<p class="truncate font-semibold">{expense.accountName}</p>
										<p class="text-sm" style="color: var(--app-muted);">{changeLabel({ primary: expense.primaryTotal, comparison: expense.comparisonTotal, delta: expense.delta, absoluteDelta: expense.absoluteDelta, currency: expense.currency }, locale)}</p>
									</div>
									<div class="text-right tabular-nums">
										<p class="text-lg font-bold" style={`color: ${toneFor(expense.delta)};`}>{expense.delta}</p>
										<p class="text-xs" style="color: var(--app-muted);">{t(locale, 'reports.comparison.absoluteChange')}: {expense.absoluteDelta} {expense.currency}</p>
									</div>
								</div>
								<div class="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
									<a class="rounded-lg border p-2 font-semibold" style="border-color: var(--app-border); color: var(--app-accent);" href={data.drilldowns.expenseChanges[expense.accountId]?.primary ?? data.drilldowns.primary.period}>
										{t(locale, 'reports.comparison.primarySide')}: <span class="tabular-nums">{expense.primaryTotal}</span>
									</a>
									<a class="rounded-lg border p-2 font-semibold" style="border-color: var(--app-border); color: var(--app-accent);" href={data.drilldowns.expenseChanges[expense.accountId]?.comparison ?? data.drilldowns.comparison.period}>
										{t(locale, 'reports.comparison.comparisonSide')}: <span class="tabular-nums">{expense.comparisonTotal}</span>
									</a>
								</div>
								<div class="mt-3 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
									<div class="h-full rounded-full" style={`width: ${expenseChangeBar(expense)}; background: var(--app-danger);`}></div>
								</div>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-4 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.comparison.noExpenseChanges')}</p>
				{/if}
			</section>
		{/if}
	{/if}
</main>
