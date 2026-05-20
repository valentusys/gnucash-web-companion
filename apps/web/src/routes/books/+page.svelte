<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/books');

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
		return status ? status.replaceAll('_', ' ') : t(locale, 'books.unknown');
	}

	function formatStatusSeverity(severity: string): string {
		return severity ? severity.replaceAll('_', ' ') : t(locale, 'books.unknown');
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
					<a class="mt-3 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href="/books/write-alpha-audit">Write-alpha audit evidence</a>
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

		{#if isRouteLoading}
			<LoadingState variant="books" message="Loading accessible read-only books…" />
		{:else if data.books.length}
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

						<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5">
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
								<dd class="mt-1" style="color: var(--app-text);">{book.access_role_label || formatAccessRole(book.access_role)}</dd>
								<dd class="mt-1 text-xs" style="color: var(--app-muted);">{book.access_role_description}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.status')}</dt>
								<dd class="mt-1 capitalize" style="color: var(--app-text);">{formatStatus(book.status)}</dd>
								<dd class="mt-1 text-xs capitalize" style="color: var(--app-muted);">{formatStatusSeverity(book.status_severity)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.readonlyStatus')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{book.read_only ? t(locale, 'books.safetyNote') : t(locale, 'books.unknown')}</dd>
							</div>
						</dl>

						<section class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.storageDiagnostics')}>
							<h4 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.storageDiagnostics')}</h4>
							<p class="mt-2" style="color: var(--app-muted);">{book.storage_diagnostics.safe_summary}</p>
							<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'books.privatePathRedacted')}</p>
							{#if book.storage_diagnostics.safe_next_actions.length}
								<p class="mt-3 font-medium" style="color: var(--app-muted);">{t(locale, 'books.safeNextActions')}</p>
								<ul class="mt-2 list-disc space-y-1 pl-5" style="color: var(--app-muted);">
									{#each book.storage_diagnostics.safe_next_actions as action}
										<li>{action}</li>
									{/each}
								</ul>
							{/if}
						</section>

						<section class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.operatorGuidanceTitle')}>
							<h4 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.operatorGuidanceTitle')}</h4>
							<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'books.currentDefaultExplanation')}</p>
							<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'books.safeOperatorGuidance')}</p>
							<dl class="mt-3 grid gap-2 md:grid-cols-3">
								<div>
									<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.metadataSource')}</dt>
									<dd class="mt-1 font-mono text-xs" style="color: var(--app-text);">{book.operator_guidance.metadata_source}</dd>
								</div>
								<div>
									<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.dataAccess')}</dt>
									<dd class="mt-1 font-mono text-xs" style="color: var(--app-text);">{book.operator_guidance.data_access}</dd>
								</div>
								<div>
									<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.readOnlyDefault')}</dt>
									<dd class="mt-1" style="color: var(--app-text);">{book.operator_guidance.read_only_default ? 'true' : 'false'}</dd>
								</div>
							</dl>
							<div class="mt-3">
								<p class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.unsupportedActions')}</p>
								{#if book.operator_guidance.unsupported_management_actions.length}
									<ul class="mt-2 flex flex-wrap gap-2">
										{#each book.operator_guidance.unsupported_management_actions as action}
											<li class="rounded-full px-2 py-1 font-mono text-xs" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{action}</li>
										{/each}
									</ul>
								{:else}
									<p class="mt-1" style="color: var(--app-muted);">{t(locale, 'books.noUnsupportedActions')}</p>
								{/if}
							</div>
						</section>

						<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'books.openSafeViews')}</p>
							{#if book.can_open_read_only_views}
								<div class="mt-3 flex flex-wrap gap-2 text-sm">
									<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/accounts`}>{t(locale, 'books.viewAccounts')}</a>
									<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/transactions`}>{t(locale, 'books.browseTransactions')}</a>
									<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/scheduled`}>{t(locale, 'books.viewScheduled')}</a>
									<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/books/${book.id}/select?next=/dashboard`}>{t(locale, 'books.dashboardSummary')}</a>
								</div>
							{:else}
								<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'books.unavailableViews')}</p>
							{/if}
							<p class="mt-3 text-xs" style="color: var(--app-muted);">{t(locale, 'books.noManagementActions')}</p>
						</div>
					</article>
				{/each}
			</div>
		{:else}
			<EmptyState
				title={t(locale, 'books.emptyTitle')}
				message={t(locale, 'books.emptyMessage')}
				ariaLabel={t(locale, 'books.emptyTitle')}
				icon="📚"
			>
				<a
					href="/login"
					class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background-color: var(--app-accent);"
				>
					Sign in again
				</a>
			</EmptyState>
		{/if}
	</section>
</main>
