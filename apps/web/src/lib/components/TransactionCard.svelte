<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type { TransactionListItem } from '$lib/api/types';

	let {
		transactions,
		onSelect
	}: {
		transactions: TransactionListItem[];
		onSelect: (id: string) => void;
	} = $props();
</script>

<div class="space-y-3 md:hidden">
	{#each transactions as tx (tx.id)}
		<div
			class="cursor-pointer rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-200"
			onclick={() => onSelect(tx.id)}
			onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
			role="button"
			tabindex="0"
		>
			<div class="flex items-start justify-between gap-3">
				<div class="min-w-0">
					<p class="truncate text-sm font-medium text-gray-900">{tx.description || '—'}</p>
					<p class="mt-1 text-xs text-gray-500">{tx.date}</p>
				</div>
				<div class="shrink-0 text-right">
					<p class="text-sm font-semibold"><Money amount={tx.amount} currency={tx.currency} /></p>
				</div>
			</div>
			<div class="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
				<span class="rounded bg-gray-100 px-2 py-0.5">{tx.account_name}</span>
				<span class="text-gray-400">→</span>
				<span class="rounded bg-gray-100 px-2 py-0.5">{tx.counter_account_name}</span>
			</div>
		</div>
	{:else}
		<p class="py-8 text-center text-sm text-gray-500">No transactions found.</p>
	{/each}
</div>
