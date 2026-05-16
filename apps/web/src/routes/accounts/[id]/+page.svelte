<script lang="ts">
	import { goto } from '$app/navigation';
	import AccountBalance from '$lib/components/AccountBalance.svelte';
	import TransactionTable from '$lib/components/TransactionTable.svelte';
	import TransactionCard from '$lib/components/TransactionCard.svelte';
	import Pagination from '$lib/components/Pagination.svelte';

	let { data } = $props();
	const account = $derived(data.account);
	const txs = $derived(data.txs);

	function handleSelect(id: string) {
		goto(`/transactions/${encodeURIComponent(id)}`);
	}

	function handlePageChange(newOffset: number) {
		const sp = new URLSearchParams();
		sp.set('limit', String(txs.limit));
		sp.set('offset', String(newOffset));
		goto(`/accounts/${encodeURIComponent(account.id)}?${sp.toString()}`);
	}
</script>

<svelte:head>
	<title>{account.name} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/accounts" class="text-sm font-medium hover:underline" style="color: var(--app-accent);">← Back to accounts</a>

	<section class="mt-4 rounded-2xl p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Account detail</p>
				<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{account.name}</h1>
				<p class="mt-2 break-words" style="color: var(--app-muted);">{account.full_name}</p>
			</div>
			<div class="rounded-xl px-4 py-3 text-right" style="background-color: var(--app-elevated-bg);">
				<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">Balance</p>
				<p class="mt-1 text-xl"><AccountBalance balance={account.balance} currency={account.currency} /></p>
			</div>
		</div>

		<dl class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Type</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.type}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Currency</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.currency}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Placeholder</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.placeholder ? 'Yes' : 'No'}</dd>
			</div>
			<div class="rounded-xl p-4" style="background-color: var(--app-elevated-bg);">
				<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">Hidden</dt>
				<dd class="mt-1" style="color: var(--app-text);">{account.hidden ? 'Yes' : 'No'}</dd>
			</div>
		</dl>
	</section>

	<section class="mt-6 rounded-2xl p-6" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">Transactions</h2>
		<p class="mt-1 text-sm" style="color: var(--app-muted);">{txs.total} transaction{txs.total !== 1 ? 's' : ''}</p>

		<div class="mt-4">
			<TransactionTable transactions={txs.items} onSelect={handleSelect} />
			<TransactionCard transactions={txs.items} onSelect={handleSelect} />
			<Pagination offset={txs.offset} limit={txs.limit} total={txs.total} onChange={handlePageChange} />
		</div>
	</section>
</main>
