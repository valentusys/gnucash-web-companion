<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import { decimalBarWidthPercent, isNonNegativeDecimalString } from '$lib/money.js';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	let isRouteLoading = $derived(navigating.to?.url.pathname === '/reports');
	let report = $derived(data.report);
	let sectionWarnings = $derived(data.sectionWarnings);
	let hasReportData = $derived(
		Boolean(report && !report.empty && (report.summary || report.cashflow || report.cashflowMonthly.length || report.expensesByAccount.length))
	);

	function displayMoney(value: string | null | undefined): string {
		return value && value.trim() ? value : '—';
	}

	function toneFor(value: string | null | undefined): string {
		if (!value) return 'var(--app-muted)';
		return isNonNegativeDecimalString(value) ? 'var(--app-success)' : 'var(--app-danger)';
	}

	function summaryItems(summary: NonNullable<NonNullable<PageData['report']>['summary']>, locale: Locale) {
		return [
			{ label: t(locale, 'reports.summary.income'), value: summary.income, tone: 'var(--app-success)' },
			{ label: t(locale, 'reports.summary.expenses'), value: summary.expenses, tone: 'var(--app-danger)' },
			{ label: t(locale, 'reports.summary.netPeriodResult'), value: summary.net, tone: toneFor(summary.net) },
			{ label: t(locale, 'reports.summary.netWorth'), value: summary.netWorth, tone: toneFor(summary.netWorth) },
			{ label: t(locale, 'reports.summary.assets'), value: summary.assets, tone: 'var(--app-success)' },
			{ label: t(locale, 'reports.summary.liabilities'), value: summary.liabilities, tone: 'var(--app-danger)' }
		].filter((item) => item.value !== null && item.value !== undefined && item.value !== '');
	}

	function expenseBar(total: string): string {
		return decimalBarWidthPercent(
			total,
			report?.expensesByAccount.map((expense) => expense.total) ?? []
		);
	}

	function monthlyOutflowBar(outflow: string): string {
		return decimalBarWidthPercent(
			outflow,
			report?.cashflowMonthly.map((period) => period.outflow) ?? []
		);
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
			href={data.drilldowns.period}
		>
			{t(locale, 'reports.viewTransactionsPeriod')}
		</a>
	</header>

	<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="report-period-heading">
		<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<h2 id="report-period-heading" class="text-lg font-semibold">{t(locale, 'reports.period.title')}</h2>
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
			</div>

			<form method="GET" action="/reports" class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label={t(locale, 'reports.period.customAria')}>
				<input type="hidden" name="preset" value="custom" />
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

		{#if !hasReportData && !data.loadError && !sectionWarnings.length}
			<EmptyState
				title={t(locale, 'reports.empty.title')}
				message={t(locale, 'reports.empty.message')}
				ariaLabel={t(locale, 'reports.empty.aria')}
				icon="📊"
			>
				<a
					href={data.drilldowns.period}
					class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background: var(--app-accent);"
				>
					{t(locale, 'reports.empty.action')}
				</a>
			</EmptyState>
		{:else if report}
			<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-limitations-title">
				<h2 id="reports-limitations-title" class="text-lg font-semibold">{t(locale, 'reports.limitations.title')}</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					{t(locale, 'reports.limitations.reportingBasis', { reportingBasis: report.reportingBasis || 'base_currency_only' })}
				</p>
				{#if report.limitations.length}
					<ul class="mt-3 list-disc space-y-1 pl-5 text-sm" style="color: var(--app-muted);">
						{#each report.limitations as limitation}
							<li>{limitation}</li>
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
							<li><span class="font-semibold">{warning.section}</span>: {warning.message}</li>
						{/each}
					</ul>
				</section>
			{/if}

			<section class="mb-6" aria-labelledby="reports-summary-title">
				<div class="mb-3 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
					<div>
						<h2 id="reports-summary-title" class="text-xl font-semibold">{t(locale, 'reports.summary.title')}</h2>
						<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.summary.help', { dateFrom: report.requestedPeriod.dateFrom, dateTo: report.requestedPeriod.dateTo })}</p>
					</div>
					<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={data.drilldowns.period}>{t(locale, 'reports.summary.openFilter')}</a>
				</div>
				{#if report.sectionErrors.summary}
					<p class="rounded-xl border p-4 text-sm" style="border-color: var(--app-warning); background: var(--app-panel);" role="alert">{report.sectionErrors.summary}</p>
				{:else if report.summary}
					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
						{#each summaryItems(report.summary, locale) as item}
							<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
								<p class="text-sm font-medium" style="color: var(--app-muted);">{item.label}</p>
								<p class="mt-2 text-2xl font-bold tabular-nums" style={`color: ${item.tone};`}>{displayMoney(item.value)}</p>
								<p class="mt-1 text-xs" style="color: var(--app-muted);">{report.summary.currency}</p>
							</article>
						{/each}
					</div>
				{:else}
					<p class="rounded-xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);" role="status">{t(locale, 'reports.summary.noTotals')}</p>
				{/if}
			</section>

			<section class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]" aria-labelledby="reports-cashflow-title">
				<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
					<h2 id="reports-cashflow-title" class="text-xl font-semibold">{t(locale, 'reports.cashflow.title')}</h2>
					{#if report.sectionErrors.cashflow}
						<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{report.sectionErrors.cashflow}</p>
					{:else if report.cashflow}
						<dl class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-1">
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.cashflow.inflow')}</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style="color: var(--app-success);">{report.cashflow.inflow} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.cashflow.outflow')}</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style="color: var(--app-danger);">{report.cashflow.outflow} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.cashflow.net')}</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style={`color: ${toneFor(report.cashflow.net)};`}>{report.cashflow.net} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
						</dl>
					{:else}
						<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.cashflow.noTotals')}</p>
					{/if}
				</article>

				<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
					<h2 class="text-xl font-semibold">{t(locale, 'reports.cashflow.monthlyTitle')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'reports.cashflow.monthlyHelp')}</p>
					{#if report.sectionErrors.monthly_cashflow}
						<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{report.sectionErrors.monthly_cashflow}</p>
					{:else if report.cashflowMonthly.length}
						<ul class="mt-4 space-y-3">
							{#each report.cashflowMonthly as period (period.month)}
								<li class="rounded-xl p-3" style="background: var(--app-bg);">
									<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
										<a class="font-semibold" style="color: var(--app-accent);" href={data.drilldowns.cashflowByMonth[period.month] ?? data.drilldowns.period}>{period.month}</a>
										<span class="text-sm tabular-nums" style={`color: ${toneFor(period.net)};`}>{t(locale, 'reports.cashflow.net')} {period.net}</span>
									</div>
									<div class="mt-3 grid grid-cols-3 gap-2 text-sm">
										<p><span style="color: var(--app-muted);">{t(locale, 'reports.cashflow.inflow')}</span><br /><span class="font-semibold tabular-nums" style="color: var(--app-success);">{period.inflow}</span></p>
										<p><span style="color: var(--app-muted);">{t(locale, 'reports.cashflow.outflow')}</span><br /><span class="font-semibold tabular-nums" style="color: var(--app-danger);">{period.outflow}</span></p>
										<p><span style="color: var(--app-muted);">{t(locale, 'reports.cashflow.net')}</span><br /><span class="font-semibold tabular-nums" style={`color: ${toneFor(period.net)};`}>{period.net}</span></p>
									</div>
									<div class="mt-3 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
										<div class="h-full rounded-full" style={`width: ${monthlyOutflowBar(period.outflow)}; background: var(--app-danger);`}></div>
									</div>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.cashflow.noMonthly')}</p>
					{/if}
				</article>
			</section>

			<section class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-expenses-title">
				<div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
					<div>
						<h2 id="reports-expenses-title" class="text-xl font-semibold">{t(locale, 'reports.expenses.title')}</h2>
						<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'reports.expenses.help')}</p>
					</div>
					<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={data.drilldowns.period}>{t(locale, 'reports.expenses.allPeriod')}</a>
				</div>
				{#if report.sectionErrors.expenses_by_account}
					<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{report.sectionErrors.expenses_by_account}</p>
				{:else if report.expensesByAccount.length}
					<ul class="mt-4 space-y-3">
						{#each report.expensesByAccount as expense (expense.account_id)}
							<li>
								<div class="flex items-center justify-between gap-3 text-sm">
									<a class="min-w-0 truncate font-semibold" style="color: var(--app-accent);" href={data.drilldowns.expensesByAccount[expense.account_id] ?? data.drilldowns.period}>{expense.account_name}</a>
									<span class="whitespace-nowrap tabular-nums">{expense.total} <span class="text-xs" style="color: var(--app-muted);">{expense.currency}</span></span>
								</div>
								<div class="mt-2 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
									<div class="h-full rounded-full" style={`width: ${expenseBar(expense.total)}; background: var(--app-danger);`}></div>
								</div>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-4 text-sm" style="color: var(--app-muted);" role="status">{t(locale, 'reports.expenses.noRows')}</p>
				{/if}
			</section>
		{/if}
	{/if}
</main>
