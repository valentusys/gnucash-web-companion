<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type { TransactionSplit } from '$lib/api/types';

	let { splits }: { splits: TransactionSplit[] } = $props();
</script>

<div class="mt-4 rounded-xl bg-gray-50 p-4">
	<h3 class="text-sm font-semibold text-gray-700">Splits</h3>
	<table class="mt-3 min-w-full text-left text-sm">
		<thead>
			<tr class="border-b border-gray-200 text-xs font-semibold uppercase text-gray-500">
				<th class="px-3 py-2">Account</th>
				<th class="px-3 py-2">Memo</th>
				<th class="px-3 py-2 text-right">Amount</th>
			</tr>
		</thead>
		<tbody>
			{#each splits as split}
				<tr class="border-b border-gray-100 last:border-0">
					<td class="px-3 py-2 text-gray-900">{split.account_name}</td>
					<td class="px-3 py-2 text-gray-600">{split.memo || '—'}</td>
					<td class="px-3 py-2 text-right">
						<Money amount={split.amount} currency={split.currency} />
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
