<script lang="ts">
	import AccountTree from '$lib/components/AccountTree.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
</script>

<svelte:head>
	<title>{t(locale, 'accounts.kicker')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'accounts.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'accounts.title')}</h1>
			{#if data.activeBook}
				<p class="mt-2 text-sm" style="color: var(--app-muted);">Book: {data.activeBook.name}</p>
			{/if}
		</div>
		{#if data.showBookSelector}
			<label class="text-sm font-medium" style="color: var(--app-text);">
				Book
				<select
					class="mt-1 block rounded-lg border px-3 py-2"
					style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
				>
					{#each data.books as book (book.id)}
						<option selected={book.id === data.activeBook?.id}>{book.name}</option>
					{/each}
				</select>
			</label>
		{/if}
	</div>

	{#if data.accounts.length}
		<AccountTree accounts={data.accounts} />
	{:else}
		<EmptyState
			title="No accounts available"
			message="Verify the selected test-copy GnuCash book path and reload this read-only view."
		/>
	{/if}
</main>
