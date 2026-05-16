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
	<a href="/accounts" class="text-sm font-medium text-blue-700 hover:text-blue-900">← Back to accounts</a>

	<section class="mt-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
		<div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<p class="text-sm font-medium uppercase tracking-wide text-blue-700">Account detail</p>
				<h1 class="mt-1 text-3xl font-bold text-gray-900">{account.name}</h1>
				<p class="mt-2 break-words text-gray-600">{account.full_name}</p>
			</div>
			<div class="rounded-xl bg-gray-50 px-4 py-3 text-right">
				<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Balance</p>
				<p class="mt-1 text-xl"><AccountBalance balance={account.balance} currency={account.currency} /></p>
			</div>
		</div>

		<dl class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div class="rounded-xl bg-gray-50 p-4">
				<dt class="text-xs font-semibold uppercase text-gray-500">Type</dt>
				<dd class="mt-1 text-gray-900">{account.type}</dd>
			</div>
			<div class="rounded-xl bg-gray-50 p-4">
				<dt class="text-xs font-semibold uppercase text-gray-500">Currency</dt>
				<dd class="mt-1 text-gray-900">{account.currency}</dd>
			</div>
			<div class="rounded-xl bg-gray-50 p-4">
				<dt class="text-xs font-semibold uppercase text-gray-500">Placeholder</dt>
				<dd class="mt-1 text-gray-900">{account.placeholder ? 'Yes' : 'No'}</dd>
			</div>
			<div class="rounded-xl bg-gray-50 p-4">
				<dt class="text-xs font-semibold uppercase text-gray-500">Hidden</dt>
				<dd class="mt-1 text-gray-900">{account.hidden ? 'Yes' : 'No'}</dd>
			</div>
		</dl>
	</section>

	<section class="mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
		<h2 class="text-lg font-semibold text-gray-900">Transactions</h2>
		<p class="mt-1 text-sm text-gray-500">{txs.total} transaction{txs.total !== 1 ? 's' : ''}</p>

		<div class="mt-4">
			<TransactionTable transactions={txs.items} onSelect={handleSelect} />
			<TransactionCard transactions={txs.items} onSelect={handleSelect} />
			<Pagination offset={txs.offset} limit={txs.limit} total={txs.total} onChange={handlePageChange} />
		</div>
	</section>
</main>
