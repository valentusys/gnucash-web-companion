<script lang="ts">
	import BalanceCard from '$lib/components/BalanceCard.svelte';
	import type { DashboardDrilldownLinks, ReportSummary } from '$lib/api/types';
	import { isNonNegativeDecimalString } from '$lib/money.js';

	let { summary, drilldowns }: { summary: ReportSummary | null; drilldowns?: DashboardDrilldownLinks } = $props();
</script>

{#if summary}
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<BalanceCard
			label="Net Worth"
			value={summary.net_worth}
			currency={summary.currency}
			trend={isNonNegativeDecimalString(summary.net_worth) ? 'up' : 'down'}
		/>
		<BalanceCard
			label="Assets"
			value={summary.assets}
			currency={summary.currency}
			trend="up"
		/>
		<BalanceCard
			label="Liabilities"
			value={summary.liabilities}
			currency={summary.currency}
			trend="down"
		/>
		<div class="space-y-2">
			<BalanceCard
				label="Income This Month"
				value={summary.income_this_month}
				currency={summary.currency}
				trend="up"
			/>
			<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={drilldowns?.incomeThisMonth ?? '/transactions?limit=50&offset=0'}>View this month's transaction filter</a>
		</div>
		<div class="space-y-2">
			<BalanceCard
				label="Expenses This Month"
				value={summary.expenses_this_month}
				currency={summary.currency}
				trend="down"
			/>
			<a class="inline-flex text-sm font-semibold" style="color: var(--app-accent);" href={drilldowns?.expensesThisMonth ?? '/transactions?limit=50&offset=0'}>View this month's transaction filter</a>
		</div>
	</div>
	<p class="mt-3 text-xs" style="color: var(--app-muted);">
		Drilldowns preserve the active book and use existing read-only transaction URL filters. Dashboard totals remain base-currency-only with no FX conversion; transaction filter views are evidence for the same period/account context, not invented recomputations.
	</p>
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
