<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type { TransactionSplit } from '$lib/api/types';

	let { splits }: { splits: TransactionSplit[] } = $props();
</script>

<div class="mt-4 rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
	<h3 class="text-sm font-semibold" style="color: var(--app-text);">Splits</h3>
	<div class="mt-3 overflow-x-auto">
		<table class="min-w-full text-left text-sm">
			<thead>
				<tr class="border-b text-xs font-semibold uppercase" style="border-color: var(--app-border); color: var(--app-muted);">
					<th class="px-3 py-2">Account</th>
					<th class="px-3 py-2">Memo</th>
					<th class="px-3 py-2 text-right">Amount</th>
				</tr>
			</thead>
			<tbody>
				{#each splits as split}
					<tr class="border-b last:border-0" style="border-color: var(--app-border);">
						<td class="px-3 py-2" style="color: var(--app-text);">{split.account_name}</td>
						<td class="px-3 py-2" style="color: var(--app-muted);">{split.memo || '—'}</td>
						<td class="px-3 py-2 text-right">
							<Money amount={split.amount} currency={split.currency} />
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
