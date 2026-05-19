<script lang="ts">
	import AccountTreeNode from './AccountTreeNode.svelte';
	import type { AccountTreeNode as AccountTreeNodeType } from '$lib/api/types';

	let { accounts }: { accounts: AccountTreeNodeType[] } = $props();
</script>

{#snippet renderNode(account: AccountTreeNodeType, depth: number)}
	<AccountTreeNode {account} {depth} />
	{#each account.children as child (child.id)}
		{@render renderNode(child, depth + 1)}
	{/each}
{/snippet}

<div class="overflow-hidden rounded-2xl" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<div class="hidden grid-cols-[minmax(0,1fr)_7rem_9rem_4rem] gap-3 px-4 py-2 text-xs font-semibold uppercase tracking-wide md:grid" style="background-color: var(--app-elevated-bg); color: var(--app-muted);">
		<div>Name</div>
		<div>Type</div>
		<div class="text-right">Balance</div>
		<div class="text-right">Currency</div>
	</div>
	{#if accounts.length === 0}
		<p class="px-4 py-8 text-center" style="color: var(--app-muted);">No accounts found.</p>
	{:else}
		{#each accounts as account (account.id)}
			{@render renderNode(account, 0)}
		{/each}
	{/if}
</div>
