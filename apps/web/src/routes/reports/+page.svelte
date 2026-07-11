<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { decimalBarWidthPercent, isNonNegativeDecimalString } from '$lib/money.js';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let isRouteLoading = $derived(navigating.to?.url.pathname === '/reports');
	let report = $derived(data.report);
	let sectionWarnings = $derived(data.sectionWarnings);
	let hasReportData = $derived(
		Boolean(report?.summary || report?.cashflow || report?.cashflowMonthly.length || report?.expensesByAccount.length)
	);

	function displayMoney(value: string | null | undefined): string {
		return value && value.trim() ? value : '—';
	}

	function toneFor(value: string | null | undefined): string {
		if (!value) return 'var(--app-muted)';
		return isNonNegativeDecimalString(value) ? 'var(--app-success)' : 'var(--app-danger)';
	}

	function summaryItems(summary: NonNullable<NonNullable<PageData['report']>['summary']>) {
		return [
			{ label: 'Income', value: summary.income, tone: 'var(--app-success)' },
			{ label: 'Expenses', value: summary.expenses, tone: 'var(--app-danger)' },
			{ label: 'Net period result', value: summary.net, tone: toneFor(summary.net) },
			{ label: 'Net worth', value: summary.netWorth, tone: toneFor(summary.netWorth) },
			{ label: 'Assets', value: summary.assets, tone: 'var(--app-success)' },
			{ label: 'Liabilities', value: summary.liabilities, tone: 'var(--app-danger)' }
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
	<title>Period reports — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8" style="color: var(--app-text);">
	<header class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Read-only reports</p>
			<h1 class="mt-1 text-3xl font-bold">Period reports explorer</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">Book: {data.activeBook.name}</p>
			{/if}
		</div>
		<a
			class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
			style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);"
			href={data.drilldowns.period}
		>
			View /transactions for this period
		</a>
	</header>

	<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="report-period-heading">
		<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<h2 id="report-period-heading" class="text-lg font-semibold">Report period</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					URL-backed range: <code>{data.period.dateFrom}</code> to <code>{data.period.dateTo}</code>. Presets and custom dates only change read-only query parameters.
				</p>
				<nav class="mt-3 flex flex-wrap gap-2" aria-label="Report period presets">
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

			<form method="GET" action="/reports" class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" aria-label="Custom report period">
				<input type="hidden" name="preset" value="custom" />
				<label class="text-sm font-medium">
					<span>Date from</span>
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
					<span>Date to</span>
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
					Apply custom range
				</button>
			</form>
		</div>
	</section>

	{#if isRouteLoading}
		<LoadingState variant="dashboard" message="Loading read-only period reports…" />
	{:else if data.validationError}
		<section
			class="rounded-2xl border p-4"
			style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
			role="alert"
			aria-labelledby="reports-invalid-range-title"
		>
			<h2 id="reports-invalid-range-title" class="text-lg font-semibold" style="color: var(--app-danger);">Invalid range</h2>
			<p class="mt-1 text-sm" style="color: var(--app-text);">{data.validationError}</p>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">No reports API request was made for this invalid range.</p>
		</section>
	{:else}
		{#if data.loadError}
			<section
				class="mb-6 rounded-2xl border p-4"
				style="border-color: var(--app-danger); background: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
				role="alert"
				aria-labelledby="reports-load-error-title"
			>
				<h2 id="reports-load-error-title" class="text-lg font-semibold" style="color: var(--app-danger);">Report request failed</h2>
				<p class="mt-1 text-sm">{data.loadError}</p>
				<p class="mt-2 text-xs" style="color: var(--app-muted);">Unknown API details are redacted; genuine empty report sections are shown separately below when available.</p>
			</section>
		{/if}

		{#if !hasReportData && !data.loadError}
			<EmptyState
				title="No report data"
				message="The reports API returned no summary, cashflow, monthly, or expense rows for this read-only period. Try another date range or inspect transactions for the same filters."
				ariaLabel="No report data for the selected period"
				icon="📊"
			>
				<a
					href={data.drilldowns.period}
					class="inline-flex min-h-11 items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background: var(--app-accent);"
				>
					Open matching /transactions filter
				</a>
			</EmptyState>
		{:else if report}
			<section class="mb-6 rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-limitations-title">
				<h2 id="reports-limitations-title" class="text-lg font-semibold">Reporting limitations</h2>
				<p class="mt-1 text-sm" style="color: var(--app-muted);">
					Reporting basis: <code>{report.reportingBasis || 'base_currency_only'}</code>. No FX conversion is performed; totals are base_currency_only and should not be interpreted as converted multi-currency totals.
				</p>
				{#if report.limitations.length}
					<ul class="mt-3 list-disc space-y-1 pl-5 text-sm" style="color: var(--app-muted);">
						{#each report.limitations as limitation}
							<li>{limitation}</li>
						{/each}
					</ul>
				{:else}
					<p class="mt-3 text-sm" style="color: var(--app-muted);">No additional limitations were reported by the API; keep treating this as base_currency_only with No FX conversion.</p>
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
					<h2 id="reports-partial-title" class="text-lg font-semibold">Partial report</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">One or more sections returned an explicit error state; unaffected sections remain visible.</p>
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
						<h2 id="reports-summary-title" class="text-xl font-semibold">Summary totals</h2>
						<p class="text-sm" style="color: var(--app-muted);">Read-only totals for {report.requestedPeriod.dateFrom} through {report.requestedPeriod.dateTo}.</p>
					</div>
					<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={data.drilldowns.period}>Open matching transaction filter</a>
				</div>
				{#if report.sectionErrors.summary}
					<p class="rounded-xl border p-4 text-sm" style="border-color: var(--app-warning); background: var(--app-panel);" role="alert">{report.sectionErrors.summary}</p>
				{:else if report.summary}
					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
						{#each summaryItems(report.summary) as item}
							<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
								<p class="text-sm font-medium" style="color: var(--app-muted);">{item.label}</p>
								<p class="mt-2 text-2xl font-bold tabular-nums" style={`color: ${item.tone};`}>{displayMoney(item.value)}</p>
								<p class="mt-1 text-xs" style="color: var(--app-muted);">{report.summary.currency}</p>
							</article>
						{/each}
					</div>
				{:else}
					<p class="rounded-xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);" role="status">No summary totals were returned for this period.</p>
				{/if}
			</section>

			<section class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]" aria-labelledby="reports-cashflow-title">
				<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
					<h2 id="reports-cashflow-title" class="text-xl font-semibold">Cashflow totals</h2>
					{#if report.sectionErrors.cashflow}
						<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-warning);" role="alert">{report.sectionErrors.cashflow}</p>
					{:else if report.cashflow}
						<dl class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-1">
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">Inflow</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style="color: var(--app-success);">{report.cashflow.inflow} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">Outflow</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style="color: var(--app-danger);">{report.cashflow.outflow} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
							<div class="rounded-xl p-3" style="background: var(--app-bg);">
								<dt class="text-sm" style="color: var(--app-muted);">Net</dt>
								<dd class="mt-1 text-xl font-bold tabular-nums" style={`color: ${toneFor(report.cashflow.net)};`}>{report.cashflow.net} <span class="text-xs" style="color: var(--app-muted);">{report.cashflow.currency}</span></dd>
							</div>
						</dl>
					{:else}
						<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">No cashflow totals were returned for this period.</p>
					{/if}
				</article>

				<article class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);">
					<h2 class="text-xl font-semibold">Monthly cashflow</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">Each month links to /transactions with matching date_from/date_to filters.</p>
					{#if report.cashflowMonthly.length}
						<ul class="mt-4 space-y-3">
							{#each report.cashflowMonthly as period (period.month)}
								<li class="rounded-xl p-3" style="background: var(--app-bg);">
									<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
										<a class="font-semibold" style="color: var(--app-accent);" href={data.drilldowns.cashflowByMonth[period.month] ?? data.drilldowns.period}>{period.month}</a>
										<span class="text-sm tabular-nums" style={`color: ${toneFor(period.net)};`}>Net {period.net}</span>
									</div>
									<div class="mt-3 grid grid-cols-3 gap-2 text-sm">
										<p><span style="color: var(--app-muted);">In</span><br /><span class="font-semibold tabular-nums" style="color: var(--app-success);">{period.inflow}</span></p>
										<p><span style="color: var(--app-muted);">Out</span><br /><span class="font-semibold tabular-nums" style="color: var(--app-danger);">{period.outflow}</span></p>
										<p><span style="color: var(--app-muted);">Net</span><br /><span class="font-semibold tabular-nums" style={`color: ${toneFor(period.net)};`}>{period.net}</span></p>
									</div>
									<div class="mt-3 h-2 w-full overflow-hidden rounded-full" style="background: var(--app-elevated-bg);" aria-hidden="true">
										<div class="h-full rounded-full" style={`width: ${monthlyOutflowBar(period.outflow)}; background: var(--app-danger);`}></div>
									</div>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="mt-3 text-sm" style="color: var(--app-muted);" role="status">No monthly cashflow rows were returned for this period.</p>
					{/if}
				</article>
			</section>

			<section class="rounded-2xl border p-4" style="border-color: var(--app-border); background: var(--app-panel);" aria-labelledby="reports-expenses-title">
				<div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
					<div>
						<h2 id="reports-expenses-title" class="text-xl font-semibold">Expenses by account</h2>
						<p class="text-sm" style="color: var(--app-muted);">Account rows link to exact /transactions filters for the selected date range and account_id.</p>
					</div>
					<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={data.drilldowns.period}>All period transactions</a>
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
					<p class="mt-4 text-sm" style="color: var(--app-muted);" role="status">No expense account rows were returned for this period.</p>
				{/if}
			</section>
		{/if}
	{/if}
</main>
