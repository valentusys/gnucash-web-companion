<script lang="ts">
	import AccountBalance from './AccountBalance.svelte';
	import type { AccountTreeNode } from '$lib/api/types';

	let { account, depth = 0 }: { account: AccountTreeNode; depth?: number } = $props();
	const muted = $derived(account.placeholder || account.hidden);
</script>

<a
	href={`/accounts/${account.id}`}
	class={`grid grid-cols-1 gap-2 border-b border-gray-100 px-4 py-3 hover:bg-gray-50 md:grid-cols-[1fr_8rem_10rem_5rem] md:items-center ${muted ? 'bg-gray-50 text-gray-500' : 'bg-white text-gray-900'}`}
>
	<div class="min-w-0" style={`padding-left: ${depth * 1.25}rem`}>
		<div class="flex flex-wrap items-center gap-2">
			<span class="truncate font-medium">{account.name}</span>
			{#if account.placeholder}
				<span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">placeholder</span>
			{/if}
			{#if account.hidden}
				<span class="rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-700">hidden</span>
			{/if}
		</div>
		<div class="truncate text-sm text-gray-500">{account.full_name}</div>
	</div>
	<div class="text-sm uppercase text-gray-600">{account.type}</div>
	<div class="text-sm md:text-right"><AccountBalance balance={account.balance} currency={account.currency} /></div>
	<div class="text-sm text-gray-500 md:text-right">{account.currency}</div>
</a>
