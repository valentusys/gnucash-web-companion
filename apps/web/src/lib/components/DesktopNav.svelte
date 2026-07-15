<script lang="ts">
	import { page } from '$app/state';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import BookSwitcher from '$lib/components/BookSwitcher.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import type { Book } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		books,
		activeBook,
		locale = DEFAULT_LOCALE,
		currentPath = '/dashboard',
		returnTo = '/dashboard',
		isAdmin = undefined
	}: { books: Book[]; activeBook: Book | null; locale?: Locale; currentPath?: string; returnTo?: string; isAdmin?: boolean } = $props();

	const pageData = $derived(page.data as { isAdmin?: boolean });
	const showAdminUsers = $derived(isAdmin === true || (isAdmin === undefined && pageData.isAdmin === true));

	const navLinks = $derived([
		{ href: '/dashboard', label: t(locale, 'nav.dashboard') },
		{ href: '/accounts', label: t(locale, 'nav.accounts') },
		{ href: '/transactions', label: t(locale, 'nav.transactions') },
		{ href: '/scheduled', label: t(locale, 'nav.scheduled') },
		{ href: '/reports', label: t(locale, 'nav.reports') },
		{ href: '/books', label: t(locale, 'nav.books') },
		...(showAdminUsers ? [{ href: '/admin/users', label: t(locale, 'nav.adminUsers') }] : [])
	] as const);

	function isActivePath(href: string): boolean {
		return currentPath === href || currentPath.startsWith(`${href}/`);
	}
</script>

<header class="hidden sticky top-0 z-30 border-b md:block" style="background-color: var(--app-nav-bg); border-color: var(--app-nav-border);">
	<div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
		<a href="/dashboard" class="text-sm font-semibold" style="color: var(--app-text);">
			GnuCash Web Companion
		</a>

		<nav class="hidden items-center gap-1 md:flex" aria-label="Main navigation">
			{#each navLinks as link}
				{@const active = isActivePath(link.href)}
				<a
					href={link.href}
					aria-current={active ? 'page' : undefined}
					data-active-route={active ? 'true' : 'false'}
					class="rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--app-hover-bg)]"
					style={active
						? 'color: var(--app-accent); background: var(--app-hover-bg); box-shadow: inset 0 0 0 1px var(--app-accent);'
						: 'color: var(--app-muted);'}
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
