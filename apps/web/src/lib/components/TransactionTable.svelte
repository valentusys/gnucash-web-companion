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
			<tr class="border-b text-xs font-semibold uppercase" style="border-color: var(--app-border); color: var(--app-muted);">
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
					class="cursor-pointer border-b hover:opacity-80"
					style="border-color: var(--app-border);"
					onclick={() => onSelect(tx.id)}
					onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
					role="button"
					tabindex="0"
				>
					<td class="px-4 py-3" style="color: var(--app-muted);">{tx.date}</td>
					<td class="px-4 py-3 font-medium" style="color: var(--app-text);">{tx.description || '—'}</td>
					<td class="px-4 py-3" style="color: var(--app-muted);">{tx.account_name}</td>
					<td class="px-4 py-3" style="color: var(--app-muted);">{tx.counter_account_name}</td>
					<td class="px-4 py-3 text-right">
						<Money amount={tx.amount} currency={tx.currency} />
					</td>
				</tr>
			{:else}
				<tr>
					<td colspan="5" class="px-4 py-10 text-center">
						<p class="font-medium" style="color: var(--app-text);">No transactions match this view</p>
						<p class="mt-1 text-sm" style="color: var(--app-muted);">Try resetting filters or choose another account.</p>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
