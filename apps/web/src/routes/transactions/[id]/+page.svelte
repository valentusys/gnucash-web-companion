<script lang="ts">
	import TransactionSplits from '$lib/components/TransactionSplits.svelte';

	let { data } = $props();
	const tx = $derived(data.transaction);
</script>

<svelte:head>
	<title>Transaction {tx.id.slice(0, 8)} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/transactions" class="text-sm font-medium text-blue-700 hover:text-blue-900">
		← Back to transactions
	</a>

	<section class="mt-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
		<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wide text-blue-700">Transaction</p>
				<h1 class="mt-1 text-2xl font-bold text-gray-900">{tx.description || '—'}</h1>
				<p class="mt-2 text-sm text-gray-500">{tx.date}</p>
			</div>
			<div class="rounded-xl bg-gray-50 px-4 py-3">
				<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Currency</p>
				<p class="mt-1 text-gray-900">{tx.currency}</p>
			</div>
		</div>

		<TransactionSplits splits={tx.splits} />
	</section>
</main>
