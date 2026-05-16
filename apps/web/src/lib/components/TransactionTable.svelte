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

<div class="hidden overflow-x-auto md:block">
	<table class="min-w-full text-left text-sm">
		<thead>
			<tr class="border-b border-gray-200 text-xs font-semibold uppercase text-gray-500">
				<th class="px-4 py-3">Date</th>
				<th class="px-4 py-3">Description</th>
				<th class="px-4 py-3">Account</th>
				<th class="px-4 py-3">Counter account</th>
				<th class="px-4 py-3 text-right">Amount</th>
			</tr>
		</thead>
		<tbody>
			{#each transactions as tx (tx.id)}
				<tr
					class="cursor-pointer border-b border-gray-100 hover:bg-gray-50"
					onclick={() => onSelect(tx.id)}
					onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
					role="button"
					tabindex="0"
				>
					<td class="px-4 py-3 text-gray-600">{tx.date}</td>
					<td class="px-4 py-3 font-medium text-gray-900">{tx.description || '—'}</td>
					<td class="px-4 py-3 text-gray-600">{tx.account_name}</td>
					<td class="px-4 py-3 text-gray-600">{tx.counter_account_name}</td>
					<td class="px-4 py-3 text-right">
						<Money amount={tx.amount} currency={tx.currency} />
					</td>
				</tr>
			{:else}
				<tr>
					<td colspan="5" class="px-4 py-8 text-center text-gray-500">No transactions found.</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
