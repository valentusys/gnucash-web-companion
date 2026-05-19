<script lang="ts">
	import AccountTreeNode from './AccountTreeNode.svelte';
	import type { AccountTreeNode as AccountTreeNodeType } from '$lib/api/types';

	let { accounts }: { accounts: AccountTreeNodeType[] } = $props();
	let accountQuery = $state('');
	const normalizedQuery = $derived(accountQuery.trim().toLowerCase());
	const totalAccountCount = $derived(countAccounts(accounts));
	const filteredAccounts = $derived.by(() => filterAccounts(accounts, normalizedQuery));
	const filteredAccountCount = $derived(countAccounts(filteredAccounts));
	const hasAccountFilter = $derived(normalizedQuery.length > 0);

	function countAccounts(nodes: AccountTreeNodeType[]): number {
		return nodes.reduce((total, node) => total + 1 + countAccounts(node.children), 0);
	}

	function accountMatches(account: AccountTreeNodeType, query: string): boolean {
		if (!query) return true;
		return [account.name, account.full_name, account.type, account.currency]
			.filter(Boolean)
			.some((value) => value.toLowerCase().includes(query));
	}

	function filterAccounts(nodes: AccountTreeNodeType[], query: string): AccountTreeNodeType[] {
		if (!query) return nodes;
		return nodes
			.map((node) => {
				const children = filterAccounts(node.children, query);
				if (accountMatches(node, query) || children.length > 0) {
					return { ...node, children };
				}
				return null;
			})
			.filter((node): node is AccountTreeNodeType => node !== null);
	}
</script>

{#snippet renderNode(account: AccountTreeNodeType, depth: number)}
	<AccountTreeNode {account} {depth} />
	{#each account.children as child (child.id)}
		{@render renderNode(child, depth + 1)}
	{/each}
{/snippet}

<div class="overflow-hidden rounded-2xl" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<div class="border-b px-4 py-4" style="border-color: var(--app-border); background-color: var(--app-elevated-bg);">
		<label class="block text-sm font-semibold" style="color: var(--app-text);" for="account-tree-filter">Filter accounts</label>
		<div class="mt-2 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<input
				id="account-tree-filter"
				type="search"
				bind:value={accountQuery}
				placeholder="Search by account name, full path, type, or currency"
				aria-describedby="account-tree-filter-status"
				class="min-h-11 w-full rounded-xl border px-3 py-2 text-sm md:max-w-md"
				style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
			/>
			<p id="account-tree-filter-status" class="text-sm" style="color: var(--app-muted);">
				{#if hasAccountFilter}
					Showing {filteredAccountCount} of {totalAccountCount} accounts. Matching descendants stay grouped with their parent path.
				{:else}
					Showing all {totalAccountCount} accounts. Use the filter to narrow large read-only account trees without changing the book.
				{/if}
			</p>
		</div>
	</div>
	<div class="hidden grid-cols-[minmax(0,1fr)_7rem_9rem_4rem] gap-3 px-4 py-2 text-xs font-semibold uppercase tracking-wide md:grid" style="background-color: var(--app-elevated-bg); color: var(--app-muted);">
		<div>Name</div>
		<div>Type</div>
		<div class="text-right">Balance</div>
		<div class="text-right">Currency</div>
	</div>
	{#if accounts.length === 0}
		<p class="px-4 py-8 text-center" style="color: var(--app-muted);">No accounts found.</p>
	{:else if filteredAccounts.length === 0}
		<div class="px-4 py-8 text-center">
			<p class="font-semibold" style="color: var(--app-text);">No accounts match this filter.</p>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">Clear the account filter to return to the full read-only account tree.</p>
		</div>
	{:else}
		{#each filteredAccounts as account (account.id)}
			{@render renderNode(account, 0)}
		{/each}
	{/if}
</div>
