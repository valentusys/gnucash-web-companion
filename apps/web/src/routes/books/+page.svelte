<script lang="ts">
	let { data } = $props();

	function formatBaseCurrency(currency: string | null): string {
		return currency?.trim() || 'Not configured';
	}

	function formatStorageType(storageType: string): string {
		return storageType || 'Unknown';
	}
</script>

<svelte:head>
	<title>Book management — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Books</p>
		<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div>
				<h1 class="text-3xl font-bold" style="color: var(--app-text);">Book management</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">
					Read-only view/manage metadata only. This page shows already configured books
					that your account can access; it does not provide book data editing workflows.
				</p>
			</div>
			{#if data.activeBook}
				<div class="rounded-2xl border px-4 py-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
					<p class="font-semibold" style="color: var(--app-text);">Active/default book</p>
					<p class="mt-1" style="color: var(--app-muted);">{data.activeBook.name}</p>
				</div>
			{/if}
		</div>
	</div>

	<section class="rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">Configured books</h2>
				<p class="text-sm" style="color: var(--app-muted);">
					Archived and unauthorized books are hidden or blocked by the API.
				</p>
			</div>
			<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">
				No upload, deletion, or GnuCash data editing here
			</span>
		</div>

		{#if data.books.length}
			<div class="grid gap-3">
				{#each data.books as book (book.id)}
					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
						<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
							<div>
								<h3 class="text-lg font-semibold" style="color: var(--app-text);">{book.name}</h3>
								<div class="mt-2 flex flex-wrap gap-2">
									{#if book.id === data.activeBook?.id}
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">Current book</span>
									{/if}
									{#if book.is_default}
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">Active/default book</span>
									{/if}
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">Read-only</span>
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">Access status: Accessible</span>
								</div>
							</div>
						</div>

						<dl class="mt-4 grid gap-3 text-sm sm:grid-cols-3">
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Base currency</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatBaseCurrency(book.base_currency)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Storage type</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatStorageType(book.storage_type)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Read-only status</dt>
								<dd class="mt-1" style="color: var(--app-text);">GnuCash Desktop remains the authoritative editor.</dd>
							</div>
						</dl>
					</article>
				{/each}
			</div>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-sm" style="border-color: var(--app-border); color: var(--app-muted);">
				No accessible configured books are available for this account.
			</div>
		{/if}
	</section>
</main>
