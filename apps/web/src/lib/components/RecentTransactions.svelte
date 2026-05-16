<script lang="ts">
	type Transaction = import('$lib/api/types').TransactionListItem;

	let { transactions, loading = false }: { transactions: Transaction[]; loading?: boolean } = $props();
</script>

<section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
	<h2 class="text-lg font-semibold text-gray-900">Recent Transactions</h2>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(5) as _}
				<div class="animate-pulse flex items-center justify-between">
					<div class="space-y-2">
						<div class="h-4 w-40 rounded bg-gray-200"></div>
						<div class="h-3 w-24 rounded bg-gray-100"></div>
					</div>
					<div class="h-4 w-20 rounded bg-gray-200"></div>
				</div>
			{/each}
		</div>
	{:else if transactions.length === 0}
		<p class="mt-4 text-sm text-gray-500">No transactions found.</p>
	{:else}
		<ul class="mt-4 divide-y divide-gray-100">
			{#each transactions as tx (tx.id)}
				<li class="flex items-center justify-between py-3">
					<div class="min-w-0">
						<p class="truncate text-sm font-medium text-gray-900">{tx.description || '—'}</p>
						<p class="text-xs text-gray-500">{tx.date} · {tx.account_name}</p>
					</div>
					<span
						class="ml-4 whitespace-nowrap text-sm font-semibold tabular-nums"
						class:text-emerald-600={Number(tx.amount) >= 0}
						class:text-red-600={Number(tx.amount) < 0}
					>
						{tx.amount}
						<span class="ml-0.5 text-xs font-normal text-gray-400">{tx.currency}</span>
					</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>
