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

<div class="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-gray-200">
	<div class="hidden grid-cols-[1fr_8rem_10rem_5rem] bg-gray-100 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-600 md:grid">
		<div>Name</div>
		<div>Type</div>
		<div class="text-right">Balance</div>
		<div class="text-right">Currency</div>
	</div>
	{#if accounts.length === 0}
		<p class="px-4 py-8 text-center text-gray-500">No accounts found.</p>
	{:else}
		{#each accounts as account (account.id)}
			{@render renderNode(account, 0)}
		{/each}
	{/if}
</div>
