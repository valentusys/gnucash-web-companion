<script lang="ts">
	import TransactionSplits from '$lib/components/TransactionSplits.svelte';

	let { data } = $props();
	const tx = $derived(data.transaction);
</script>

<svelte:head>
	<title>Transaction {tx.id.slice(0, 8)} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/transactions" class="text-sm font-medium hover:underline" style="color: var(--app-accent);">
		← Back to transactions
	</a>

	<section class="mt-4 rounded-2xl p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Transaction</p>
				<h1 class="mt-1 text-2xl font-bold" style="color: var(--app-text);">{tx.description || '—'}</h1>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{tx.date}</p>
			</div>
			<div class="rounded-xl px-4 py-3" style="background-color: var(--app-elevated-bg);">
				<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">Currency</p>
				<p class="mt-1" style="color: var(--app-text);">{tx.currency}</p>
			</div>
		</div>

		<TransactionSplits splits={tx.splits} />
	</section>
</main>
