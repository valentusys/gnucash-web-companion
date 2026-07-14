<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import type { Book, BookCapabilityFlags, BookProblemCode } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';

	type ManageSuccessCode = 'set_default' | 'remove_registry';

	let { data, form }: {
		data: {
			locale?: Locale;
			books: Book[];
			activeBook: Book | null;
			isAdmin: boolean;
			bookContextNotice: string | null;
		};
		form?: {
			manageSuccessCode?: ManageSuccessCode;
			manageErrorCode?: BookProblemCode;
		} | null;
	} = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/books');

	const openLinkDefinitions: Array<{
		capability: keyof Pick<BookCapabilityFlags, 'can_open_accounts' | 'can_open_transactions' | 'can_open_reports'>;
		next: '/accounts' | '/transactions' | '/reports';
		labelKey: MessageKey;
	}> = [
		{ capability: 'can_open_accounts', next: '/accounts', labelKey: 'books.viewAccounts' },
		{ capability: 'can_open_transactions', next: '/transactions', labelKey: 'books.browseTransactions' },
		{ capability: 'can_open_reports', next: '/reports', labelKey: 'books.reportsLink' }
	];

	function formatBaseCurrency(currency: string | null): string {
		return currency?.trim() || t(locale, 'books.notConfigured');
	}

	function isBookEnabled(book: Book): boolean {
		return book.is_enabled !== false;
	}

	function bookHealthStatus(book: Book): string {
		return book.health?.status ?? book.status ?? 'unknown';
	}

	function bookCheckedAt(book: Book): string {
		return book.health?.checked_at ?? book.updated_at ?? book.created_at ?? t(locale, 'books.notChecked');
	}

	function statusLabel(status: string): string {
		return t(locale, `books.status.${status || 'unknown'}` as MessageKey);
	}

	function bookProblemMessage(locale: Locale, code: BookProblemCode | undefined): string {
		return t(locale, `books.problem.${code ?? 'unknown_book_problem'}` as MessageKey);
	}

	function successMessage(code: ManageSuccessCode | undefined): string {
		if (code === 'set_default') return t(locale, 'books.manageSuccessSetDefault');
		if (code === 'remove_registry') return t(locale, 'books.manageSuccessRemoveRegistry');
		return '';
	}

	function canOpenCapability(book: Book, capability: 'can_open_accounts' | 'can_open_transactions' | 'can_open_reports'): boolean {
		return isBookEnabled(book) && book.can_open_read_only_views && book.capabilities?.[capability] !== false;
	}

	function capabilityLinks(book: Book) {
		return openLinkDefinitions
			.filter((link) => isBookEnabled(book) && canOpenCapability(book, link.capability))
			.map((link) => ({
				...link,
				href: `/books/${book.id}/select?next=${link.next}`,
				label: t(locale, link.labelKey)
			}));
	}
</script>

<svelte:head>
	<title>{t(locale, 'books.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	{#if data.bookContextNotice}
		<section class="mb-6 rounded-2xl border p-4 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.contextRecoveryTitle')}>
			<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.contextRecoveryTitle')}</p>
			<p class="mt-1" style="color: var(--app-muted);">
				{#if data.bookContextNotice === 'no_accessible_books'}
					{t(locale, 'books.contextRecoveryNoBooks')}
				{:else if data.bookContextNotice === 'unavailable_selected_book'}
					{t(locale, 'books.contextRecoveryUnavailable')}
				{:else}
					{t(locale, 'books.contextRecoveryStale')}
				{/if}
			</p>
		</section>
	{/if}

	<div class="mb-6 space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'books.kicker')}</p>
		<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div class="min-w-0">
				<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'books.title')}</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'books.subtitle')}</p>
			</div>
			<div class="flex flex-wrap gap-2">
				{#if data.isAdmin}
					<a class="inline-flex min-h-11 items-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);" href="/books/new">{t(locale, 'books.addBookAction')}</a>
				{/if}
				{#if data.activeBook}
					<a class="inline-flex min-h-11 items-center rounded-xl border px-4 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);" href="/books/write-alpha-audit">{t(locale, 'books.auditEvidence')}</a>
				{/if}
			</div>
		</div>
	</div>

	{#if form?.manageSuccessCode}
		<p class="mb-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(form.manageSuccessCode)}</p>
	{/if}
	{#if form?.manageErrorCode}
		<p class="mb-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{bookProblemMessage(locale, form.manageErrorCode)}</p>
	{/if}

	<section class="rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.configuredTitle')}</h2>
				<p class="text-sm" style="color: var(--app-muted);">{t(locale, 'books.hiddenPolicy')}</p>
			</div>
			<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'books.noMutationBadge')}</span>
		</div>

		{#if isRouteLoading}
			<LoadingState variant="books" message={t(locale, 'books.loading')} />
		{:else if data.books.length}
			<div class="grid gap-3">
				{#each data.books as book (book.id)}
					{@const links = capabilityLinks(book)}
					<article class="min-w-0 rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
						<div class="flex min-w-0 flex-col gap-2 md:flex-row md:items-start md:justify-between">
							<div class="min-w-0">
								<h3 class="break-words text-lg font-semibold" style="color: var(--app-text);">{book.name}</h3>
								<div class="mt-2 flex flex-wrap gap-2">
									{#if book.id === data.activeBook?.id}<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{t(locale, 'books.currentBook')}</span>{/if}
									{#if book.is_default}<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{t(locale, 'books.defaultBook')}</span>{/if}
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{isBookEnabled(book) ? t(locale, 'books.enabledBook') : t(locale, 'books.disabledBook')}</span>
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{t(locale, 'books.readOnlyBadge')}</span>
								</div>
							</div>
						</div>

						<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
							<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.baseCurrency')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{formatBaseCurrency(book.base_currency)}</dd></div>
							<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.status')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{statusLabel(bookHealthStatus(book))}</dd></div>
							<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightCheckedAt')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{bookCheckedAt(book)}</dd></div>
							<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.accessRole')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{book.access_role_label || book.access_role || t(locale, 'books.unknown')}</dd></div>
						</dl>

						<section class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.storageDiagnostics')}>
							<h4 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.storageDiagnostics')}</h4>
							<p class="mt-2 break-words" style="color: var(--app-muted);">{book.storage_diagnostics.safe_summary}</p>
							<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'books.privatePathRedacted')}</p>
						</section>

						<details class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<summary class="min-h-11 cursor-pointer font-semibold" style="color: var(--app-text);">{t(locale, 'books.statusDetailsTitle')}</summary>
							<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'books.statusDetailsHelp')}</p>
							<ul class="mt-2 list-disc space-y-1 pl-5" style="color: var(--app-muted);">
								<li>{t(locale, 'books.renameFuture')}</li>
								<li>{t(locale, 'books.disableFuture')}</li>
								<li>{t(locale, 'books.recheckFuture')}</li>
							</ul>
						</details>

						<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'books.openSafeViews')}</p>
							{#if links.length}
								<div class="mt-3 flex flex-wrap gap-2 text-sm">
									{#each links as link}
										<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=${link.next}`}>{link.label}</a>
									{/each}
								</div>
							{:else}
								<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'books.unavailableViews')}</p>
							{/if}

							{#if data.isAdmin && (book.management_actions.includes('set_default') || book.management_actions.includes('remove_from_registry'))}
								<div class="mt-4 border-t pt-3" style="border-color: var(--app-border);">
									<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'books.registryManagement')}</p>
									<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'books.registryManagementSafety')}</p>
									<div class="mt-3 grid gap-3 md:grid-cols-2">
										{#if book.management_actions.includes('set_default') && !book.is_default}
											<form method="POST" action="?/setDefaultBook">
												<input type="hidden" name="book_id" value={book.id} />
												<button type="submit" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'books.setDefaultAction')}</button>
											</form>
										{/if}
										{#if book.management_actions.includes('remove_from_registry')}
											<form method="POST" action="?/removeBook" class="min-w-0 rounded-lg border p-3" style="border-color: var(--app-border);">
												<input type="hidden" name="book_id" value={book.id} />
												<label class="flex items-start gap-2 text-xs" style="color: var(--app-muted);">
													<input required type="checkbox" name="confirm_metadata_only" class="mt-1" />
													<span>{t(locale, 'books.removeMetadataConfirm')}</span>
												</label>
												<button type="submit" class="mt-3 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'books.removeRegistryAction')}</button>
											</form>
										{/if}
									</div>
								</div>
							{:else}
								<p class="mt-3 text-xs" style="color: var(--app-muted);">{t(locale, 'books.noManagementActions')}</p>
							{/if}
						</div>
					</article>
				{/each}
			</div>
		{:else if data.isAdmin}
			<EmptyState title={t(locale, 'books.firstRunAdminTitle')} message={t(locale, 'books.firstRunAdminMessage')} ariaLabel={t(locale, 'books.firstRunAdminTitle')} icon="📚">
				<a href="/books/new" class="rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'books.addBookAction')}</a>
			</EmptyState>
		{:else if !data.isAdmin}
			<EmptyState title={t(locale, 'books.firstRunUserTitle')} message={t(locale, 'books.firstRunUserMessage')} ariaLabel={t(locale, 'books.firstRunUserTitle')} icon="📚" role="note" />
		{/if}
	</section>
</main>
