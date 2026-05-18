<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import BookSwitcher from '$lib/components/BookSwitcher.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import type { Book } from '$lib/api/types';
import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		books,
		activeBook,
		locale = DEFAULT_LOCALE,
		returnTo = '/dashboard'
	}: { books: Book[]; activeBook: Book | null; locale?: Locale; returnTo?: string } = $props();

	const navLinks = $derived([
		{ href: '/dashboard', label: t(locale, 'nav.dashboard') },
		{ href: '/accounts', label: t(locale, 'nav.accounts') },
		{ href: '/transactions', label: t(locale, 'nav.transactions') },
		{ href: '/books', label: t(locale, 'nav.books') }
	] as const);
</script>

<header class="sticky top-0 z-30 border-b" style="background-color: var(--app-nav-bg); border-color: var(--app-nav-border);">
	<div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
		<a href="/dashboard" class="text-sm font-semibold" style="color: var(--app-text);">
			GnuCash Web Companion
		</a>

		<nav class="hidden items-center gap-1 md:flex" aria-label="Main navigation">
			{#each navLinks as link}
				<a
					href={link.href}
					class="rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--app-hover-bg)]"
					style="color: var(--app-muted);"
				>
					{link.label}
				</a>
			{/each}
		</nav>

		<div class="flex items-center gap-3">
			<BookSwitcher {books} {activeBook} />
			<LocaleSwitcher {locale} {returnTo} compact />
			<ThemeSwitcher />
			<form method="POST" action="/logout">
				<button
					type="submit"
					class="rounded-lg border px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--app-hover-bg)]"
					style="border-color: var(--app-border); color: var(--app-muted);"
				>
					{t(locale, 'nav.logout')}
				</button>
			</form>
		</div>
	</div>
</header>
