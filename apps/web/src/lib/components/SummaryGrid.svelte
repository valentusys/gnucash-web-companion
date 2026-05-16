<script lang="ts">
	import BalanceCard from '$lib/components/BalanceCard.svelte';

	let { summary }: { summary: import('$lib/api/types').ReportSummary | null } = $props();
</script>

{#if summary}
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<BalanceCard
			label="Net Worth"
			value={summary.net_worth}
			currency={summary.currency}
			trend={Number(summary.net_worth) >= 0 ? 'up' : 'down'}
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
		<BalanceCard
			label="Income This Month"
			value={summary.income_this_month}
			currency={summary.currency}
			trend="up"
		/>
		<BalanceCard
			label="Expenses This Month"
			value={summary.expenses_this_month}
			currency={summary.currency}
			trend="down"
		/>
	</div>
{:else}
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each Array(5) as _}
			<div class="animate-pulse rounded-xl bg-gray-100 p-5">
				<div class="h-3 w-24 rounded bg-gray-200"></div>
				<div class="mt-3 h-7 w-32 rounded bg-gray-200"></div>
			</div>
		{/each}
	</div>
{/if}
