<script lang="ts">
	import SummaryGrid from '$lib/components/SummaryGrid.svelte';
	import RecentTransactions from '$lib/components/RecentTransactions.svelte';
	import ExpensesByAccount from '$lib/components/ExpensesByAccount.svelte';
	import CashflowSummary from '$lib/components/CashflowSummary.svelte';

	let { data }: { data: any } = $props();
</script>

<svelte:head>
	<title>Dashboard — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl px-4 py-6 sm:py-10">
	<h1 class="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">Dashboard</h1>

	{#if data.loadError}
		<div
			class="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-200"
			role="alert"
		>
			<p class="font-semibold">Failed to load dashboard data</p>
			<p class="mt-1">{data.loadError}</p>
		</div>
	{/if}

	<section class="mt-6">
		<h2 class="mb-3 text-sm font-medium uppercase tracking-wide text-gray-500">Summary</h2>
		<SummaryGrid summary={data.summary} />
	</section>

	<div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
		<RecentTransactions transactions={data.recentTransactions} />
		<ExpensesByAccount expenses={data.expenses} />
	</div>

	<section class="mt-6">
		<CashflowSummary periods={data.cashflowPeriods} />
	</section>
</main>
