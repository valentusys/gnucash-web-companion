<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';
	import type { BookPreflightResponse, BookProblemCode, BookSectionStatus } from '$lib/api/types';

	type SafeFormState = {
		name: string;
		mountedPath: string;
		baseCurrency: string;
		makeDefault: boolean;
	};

	type PageForm = {
		preflight?: BookPreflightResponse;
		preflightRequest?: SafeFormState;
		preflightErrorCode?: BookProblemCode;
		registrationErrorCode?: BookProblemCode;
		registrationSuccessCode?: 'registered';
		registeredBookId?: number | null;
		registeredBookName?: string;
	} | null;

	let { data, form }: { data: { locale?: Locale; isAdmin: boolean }; form?: PageForm } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let previous = $derived<SafeFormState>(
		form?.preflightRequest ?? { name: '', mountedPath: '', baseCurrency: '', makeDefault: false }
	);
	let preflight = $derived(form?.preflight ?? null);
	let safeCode = $derived(preflight?.safe_code ?? form?.preflightErrorCode ?? form?.registrationErrorCode ?? null);

	const checklistSections: Array<{
		section: 'source' | 'open' | 'accounts' | 'transactions' | 'reports';
		field: 'source_status' | 'open_status' | 'accounts' | 'transactions' | 'reports';
	}> = [
		{ section: 'source', field: 'source_status' },
		{ section: 'open', field: 'open_status' },
		{ section: 'accounts', field: 'accounts' },
		{ section: 'transactions', field: 'transactions' },
		{ section: 'reports', field: 'reports' }
	];

	function bookProblemMessage(locale: Locale, safe_code: BookProblemCode | null | undefined): string {
		return t(locale, `books.problem.${safe_code ?? 'unknown_book_problem'}` as MessageKey);
	}

	function fixedSafeMessage(locale: Locale, safe_code: BookProblemCode | null | undefined): string {
		return bookProblemMessage(locale, safe_code);
	}

	function statusLabel(status: string | null | undefined): string {
		if (!status) return t(locale, 'books.statusUnknown');
		const key = `books.status.${status}` as MessageKey;
		return t(locale, key) || status.replaceAll('_', ' ');
	}

	function sectionLabel(section: string): string {
		const key = `books.section.${section}` as MessageKey;
		return t(locale, key) || section;
	}

	function sectionStatus(
		preflight: BookPreflightResponse,
		field: 'source_status' | 'open_status' | 'accounts' | 'transactions' | 'reports'
	): BookSectionStatus {
		return preflight[field];
	}

	function safeOpenLinks(bookId: number) {
		return [
			{ href: `/books/${bookId}/select?next=/accounts`, label: t(locale, 'books.viewAccounts') },
			{ href: `/books/${bookId}/select?next=/transactions`, label: t(locale, 'books.browseTransactions') },
			{ href: `/books/${bookId}/select?next=/reports`, label: t(locale, 'books.reportsLink') }
		];
	}
</script>

<svelte:head>
	<title>{t(locale, 'books.newTitle')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/books" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'books.backToBooks')}</a>

	<div class="mt-6 space-y-2">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'books.kicker')}</p>
		<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'books.newTitle')}</h1>
		<p class="max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'books.newSubtitle')}</p>
	</div>

	{#if !data.isAdmin}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" role="alert">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.adminRequiredTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.firstRunUserMessage')}</p>
		</section>
	{:else}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.newStep1Title')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.supportedFormat')}</p>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.unsupportedFormatWarning')}</p>
		</section>

		<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.newStep2Title')}>
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.newStep2Title')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.registerSafety')}</p>

			{#if safeCode}
				<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">
					{bookProblemMessage(locale, safeCode)}
				</p>
			{/if}

			<form method="POST" action="?/preflight" class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
				<label class="text-sm font-medium" style="color: var(--app-text);">
					{t(locale, 'books.registerName')}
					<input name="name" required maxlength="256" value={previous.name} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
				</label>
				<label class="text-sm font-medium" style="color: var(--app-text);">
					{t(locale, 'books.registerCurrency')}
					<input name="base_currency" required maxlength="16" value={previous.baseCurrency} placeholder="USD" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 uppercase" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
				</label>
				<label class="text-sm font-medium md:col-span-2" style="color: var(--app-text);">
					{t(locale, 'books.registerPath')}
					<input name="mounted_path" required autocomplete="off" value={previous.mountedPath} placeholder="/data/books/copied-test-book.gnucash.sqlite" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 font-mono text-sm" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
				</label>
				<label class="flex min-h-11 items-start gap-3 text-sm md:col-span-2" style="color: var(--app-muted);">
					<input name="make_default" type="checkbox" checked={previous.makeDefault} class="mt-1" />
					<span>{t(locale, 'books.registerMakeDefault')}</span>
				</label>
				<div class="md:col-span-2">
					<button type="submit" class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'books.preflightSubmit')}</button>
				</div>
			</form>
		</section>

		{#if preflight}
			<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-live={preflight.status === 'ready' ? 'polite' : 'assertive'}>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.newStep3Title')}</h2>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">
					{preflight.status === 'ready' ? t(locale, 'books.preflightReady') : t(locale, 'books.preflightRejected')}
				</p>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{fixedSafeMessage(locale, preflight.registration_status.safe_code ?? preflight.safe_code)}</p>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{fixedSafeMessage(locale, preflight.safe_code)}</p>
				<dl class="mt-3 grid gap-3 text-sm md:grid-cols-2">
					<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);">
						<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightFormat')}</dt>
						<dd class="mt-1 break-words" style="color: var(--app-text);">{preflight.format}</dd>
					</div>
					<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);">
						<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightCheckedAt')}</dt>
						<dd class="mt-1 break-words" style="color: var(--app-text);">{preflight.checked_at}</dd>
					</div>
				</dl>

				<ul class="mt-4 grid gap-2">
					{#each checklistSections as itemDefinition}
						{@const item = sectionStatus(preflight, itemDefinition.field)}
						<li class="min-w-0 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-bg);">
							<div class="flex min-w-0 flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
								<span class="font-semibold" style="color: var(--app-text);">{sectionLabel(itemDefinition.section)}</span>
								<span class="w-fit rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{statusLabel(item.status)}</span>
							</div>
							<p class="mt-2 break-words" style="color: var(--app-muted);">{fixedSafeMessage(locale, item.safe_code ?? preflight.safe_code)}</p>
						</li>
					{/each}
				</ul>

				<p class="mt-4 text-xs" style="color: var(--app-muted);">{t(locale, 'books.preflightTokenOpaque')}</p>
			</section>
		{/if}

		{#if preflight?.status === 'ready'}
			<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.newStep4Title')}</h2>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.confirmRegisterHelp')}</p>
				<form method="POST" action="?/confirm" class="mt-4">
					<input type="hidden" name="name" value={previous.name} />
					<input type="hidden" name="mounted_path" value={previous.mountedPath} />
					<input type="hidden" name="base_currency" value={previous.baseCurrency} />
					{#if previous.makeDefault}<input type="hidden" name="make_default" value="on" />{/if}
					<input type="hidden" name="preflight_token" value={preflight.preflight_token} />
					<button type="submit" class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'books.confirmRegisterSubmit')}</button>
				</form>
			</section>
		{/if}

		{#if form?.registrationSuccessCode === 'registered'}
			<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-accent); background-color: var(--app-accent-soft);" role="status">
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.registrationSuccessTitle')}</h2>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.registrationSuccessMessage')}</p>
				{#if form.registeredBookId}
					<div class="mt-3 flex flex-wrap gap-2 text-sm">
						{#each safeOpenLinks(form.registeredBookId) as link}
							<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={link.href}>{link.label}</a>
						{/each}
					</div>
				{/if}
			</section>
		{/if}
	{/if}
</main>
