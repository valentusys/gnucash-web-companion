<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	function formatBaseCurrency(currency: string | null): string {
		return currency?.trim() || t(locale, 'books.notConfigured');
	}

	function formatStorageType(storageType: string): string {
		return storageType || t(locale, 'books.unknown');
	}

	function formatAccessRole(role: string | null): string {
		return role || t(locale, 'books.unknown');
	}

	function formatStatus(status: string): string {
		return status || t(locale, 'books.unknown');
	}
</script>

<svelte:head>
	<title>{t(locale, 'books.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'books.kicker')}</p>
		<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div>
				<h1 class="text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'books.title')}</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">
					{t(locale, 'books.subtitle')}
				</p>
			</div>
			{#if data.activeBook}
				<div class="rounded-2xl border px-4 py-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
					<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.activeDefault')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{data.activeBook.name}</p>
				</div>
			{/if}
		</div>
	</div>

	<section class="rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.configuredTitle')}</h2>
				<p class="text-sm" style="color: var(--app-muted);">
					{t(locale, 'books.hiddenPolicy')}
				</p>
			</div>
			<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">
				{t(locale, 'books.noMutationBadge')}
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
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{t(locale, 'books.currentBook')}</span>
									{/if}
									{#if book.is_default}
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{t(locale, 'books.defaultBook')}</span>
									{/if}
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{t(locale, 'books.readOnlyBadge')}</span>
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{t(locale, 'books.accessibleBadge')}</span>
								</div>
							</div>
						</div>

						<dl class="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5">
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.baseCurrency')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatBaseCurrency(book.base_currency)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.storageType')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatStorageType(book.storage_type)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.accessRole')}</dt>
								<dd class="mt-1 capitalize" style="color: var(--app-text);">{formatAccessRole(book.access_role)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.status')}</dt>
								<dd class="mt-1 capitalize" style="color: var(--app-text);">{formatStatus(book.status)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.readonlyStatus')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{book.read_only ? t(locale, 'books.safetyNote') : t(locale, 'books.unknown')}</dd>
							</div>
						</dl>

						<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'books.openSafeViews')}</p>
							<div class="mt-3 flex flex-wrap gap-2 text-sm">
								<a class="rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/accounts`}>{t(locale, 'books.viewAccounts')}</a>
								<a class="rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/transactions`}>{t(locale, 'books.browseTransactions')}</a>
								<a class="rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/scheduled`}>{t(locale, 'books.viewScheduled')}</a>
								<a class="rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/dashboard`}>{t(locale, 'books.dashboardSummary')}</a>
							</div>
							<p class="mt-3 text-xs" style="color: var(--app-muted);">{t(locale, 'books.noManagementActions')}</p>
						</div>
					</article>
				{/each}
			</div>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-sm" style="border-color: var(--app-border); color: var(--app-muted);">
				{t(locale, 'books.noBooks')}
			</div>
		{/if}
	</section>
</main>
