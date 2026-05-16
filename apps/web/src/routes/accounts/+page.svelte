<script lang="ts">
	import AccountTree from '$lib/components/AccountTree.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>Accounts — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide text-blue-700">Accounts</p>
			<h1 class="mt-1 text-3xl font-bold text-gray-900">Account tree</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm text-gray-600">Book: {data.activeBook.name}</p>
			{/if}
		</div>
		{#if data.showBookSelector}
			<label class="text-sm font-medium text-gray-700">
				Book
				<select class="mt-1 block rounded-lg border border-gray-300 bg-white px-3 py-2">
					{#each data.books as book (book.id)}
						<option selected={book.id === data.activeBook?.id}>{book.name}</option>
					{/each}
				</select>
			</label>
		{/if}
	</div>

	<AccountTree accounts={data.accounts} />
</main>
