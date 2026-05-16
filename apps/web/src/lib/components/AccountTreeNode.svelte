<script lang="ts">
	import AccountBalance from './AccountBalance.svelte';
	import type { AccountTreeNode } from '$lib/api/types';

	let { account, depth = 0 }: { account: AccountTreeNode; depth?: number } = $props();
	const muted = $derived(account.placeholder || account.hidden);
</script>

<a
	href={`/accounts/${account.id}`}
	class="grid grid-cols-1 gap-2 border-b px-4 py-3 hover:opacity-80 md:grid-cols-[1fr_8rem_10rem_5rem] md:items-center"
	style="border-color: var(--app-border); background-color: {muted ? 'var(--app-elevated-bg)' : 'var(--app-panel)'}; color: {muted ? 'var(--app-muted)' : 'var(--app-text)'};"
>
	<div class="min-w-0" style="padding-left: {depth * 1.25}rem">
		<div class="flex flex-wrap items-center gap-2">
			<span class="truncate font-medium">{account.name}</span>
			{#if account.placeholder}
				<span class="rounded-full px-2 py-0.5 text-xs font-medium" style="background-color: color-mix(in srgb, var(--app-accent) 15%, transparent); color: var(--app-accent);">placeholder</span>
			{/if}
			{#if account.hidden}
				<span class="rounded-full px-2 py-0.5 text-xs font-medium" style="background-color: var(--app-elevated-bg); color: var(--app-muted);">hidden</span>
			{/if}
		</div>
		<div class="truncate text-sm" style="color: var(--app-muted);">{account.full_name}</div>
	</div>
	<div class="text-sm uppercase" style="color: var(--app-muted);">{account.type}</div>
	<div class="text-sm md:text-right"><AccountBalance balance={account.balance} currency={account.currency} /></div>
	<div class="text-sm md:text-right" style="color: var(--app-muted);">{account.currency}</div>
</a>
