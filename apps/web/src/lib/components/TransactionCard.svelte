<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
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
			class="cursor-pointer rounded-xl p-4"
			style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
			onclick={() => onSelect(tx.id)}
			onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
			role="button"
			tabindex="0"
		>
			<div class="flex items-start justify-between gap-3">
				<div class="min-w-0">
					<p class="truncate text-sm font-medium" style="color: var(--app-text);">{tx.description || 'No description'}</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">{tx.date}</p>
				</div>
				<div class="shrink-0 text-right">
					<p class="text-sm font-semibold"><Money amount={tx.amount} currency={tx.currency} /></p>
				</div>
			</div>
			<div class="mt-2 flex flex-wrap gap-2 text-xs" style="color: var(--app-muted);">
				<span class="rounded px-2 py-0.5" style="background-color: var(--app-elevated-bg);">{tx.account_name}</span>
				<span style="color: var(--app-border);">→</span>
				<span class="rounded px-2 py-0.5" style="background-color: var(--app-elevated-bg);">{tx.counter_account_name}</span>
			</div>
		</div>
	{:else}
		<EmptyState
			title="No transactions match this view"
			message="Try resetting filters or choose another account. This screen is read-only."
		/>
	{/each}
</div>
