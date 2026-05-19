<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type { TransactionSplit } from '$lib/api/types';

	let { splits }: { splits: TransactionSplit[] } = $props();
</script>

<div class="mt-4 rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
	<h3 class="text-sm font-semibold" style="color: var(--app-text);">Splits</h3>

	<div class="mt-3 space-y-3 md:hidden">
		{#each splits as split}
			<div class="min-w-0 rounded-lg border p-3" style="border-color: var(--app-border); background-color: var(--app-panel);">
				<div class="flex min-w-0 items-start justify-between gap-3">
					<div class="min-w-0">
						<div class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Account</div>
						<div class="truncate text-sm font-medium" style="color: var(--app-text);" title={split.account_name}>{split.account_name}</div>
					</div>
					<div class="shrink-0 text-right text-sm font-semibold">
						<Money amount={split.amount} currency={split.currency} />
					</div>
				</div>
				<div class="mt-2 min-w-0">
					<div class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Memo</div>
					<div class="break-words text-sm" style="color: var(--app-muted);">{split.memo || '—'}</div>
				</div>
			</div>
		{/each}
	</div>

	<div class="mt-3 hidden md:block overflow-x-hidden">
		<table class="w-full table-fixed text-left text-sm">
			<thead>
				<tr class="border-b text-xs font-semibold uppercase" style="border-color: var(--app-border); color: var(--app-muted);">
					<th class="w-[42%] px-3 py-2">Account</th>
					<th class="w-[34%] px-3 py-2">Memo</th>
					<th class="w-[24%] px-3 py-2 text-right">Amount</th>
				</tr>
			</thead>
			<tbody>
				{#each splits as split}
					<tr class="border-b last:border-0" style="border-color: var(--app-border);">
						<td class="truncate px-3 py-2" style="color: var(--app-text);" title={split.account_name}>{split.account_name}</td>
						<td class="truncate px-3 py-2" style="color: var(--app-muted);" title={split.memo || '—'}>{split.memo || '—'}</td>
						<td class="px-3 py-2 text-right">
							<Money amount={split.amount} currency={split.currency} />
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
