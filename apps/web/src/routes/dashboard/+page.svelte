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

<main class="mx-auto max-w-5xl px-4 py-6 sm:py-10" style="color: var(--app-text);">
	<h1 class="text-2xl font-bold tracking-tight sm:text-3xl" style="color: var(--app-text);">Dashboard</h1>

	{#if data.loadError}
		<div
			class="mt-4 rounded-lg p-4 text-sm"
			style="background-color: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-danger); border: 1px solid var(--app-danger);"
			role="alert"
		>
			<p class="font-semibold">Failed to load dashboard data</p>
			<p class="mt-1">{data.loadError}</p>
		</div>
	{/if}

	<section class="mt-6" aria-labelledby="summary-heading">
		<h2 id="summary-heading" class="mb-3 text-sm font-medium uppercase tracking-wide" style="color: var(--app-muted);">Summary</h2>
		<SummaryGrid summary={data.summary} />
	</section>

	<div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
		<RecentTransactions transactions={data.recentTransactions} />
		<ExpensesByAccount expenses={data.expenses} />
	</div>

	<section class="mt-6" aria-labelledby="cashflow-heading">
		<h2 id="cashflow-heading" class="sr-only">Cashflow</h2>
		<CashflowSummary periods={data.cashflowPeriods} />
	</section>
</main>
