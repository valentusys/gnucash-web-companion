<script lang="ts">
	import { page } from '$app/state';
	import BookSwitcher from '$lib/components/BookSwitcher.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
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

	let menuOpen = $state(false);
	const pageData = $derived(page.data as { isAdmin?: boolean });
	const showAdminUsers = $derived(isAdmin === true || (isAdmin === undefined && pageData.isAdmin === true));

	const navLinks = $derived([
		{ href: '/dashboard', label: t(locale, 'nav.dashboard'), icon: 'home' },
		{ href: '/accounts', label: t(locale, 'nav.accounts'), icon: 'accounts' },
		{ href: '/transactions', label: t(locale, 'nav.transactions'), icon: 'transactions' },
		{ href: '/scheduled', label: t(locale, 'nav.scheduled'), icon: 'scheduled' },
		{ href: '/reports', label: t(locale, 'nav.reports'), icon: 'reports' },
		{ href: '/books', label: t(locale, 'nav.books'), icon: 'books' },
		...(showAdminUsers ? [{ href: '/admin/users', label: t(locale, 'nav.adminUsers'), icon: 'admin-users' }] : [])
	] as const);

	function isActivePath(href: string): boolean {
		return currentPath === href || currentPath.startsWith(`${href}/`);
	}

	function toggleMenu() {
		menuOpen = !menuOpen;
	}

	function closeMenu() {
		menuOpen = false;
	}

	function iconFor(name: string, active: boolean) {
		const c = active ? 'var(--app-accent)' : 'var(--app-muted)';
		switch (name) {
			case 'home':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`;
			case 'accounts':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>`;
			case 'transactions':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`;
			case 'scheduled':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 15"/></svg>`;
			case 'reports':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="11" width="3" height="6" rx="1"/><rect x="12" y="7" width="3" height="10" rx="1"/><rect x="17" y="5" width="3" height="12" rx="1"/></svg>`;
			case 'books':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>`;
			case 'admin-users':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`;
			default:
				return '';
		}
	}
</script>

<nav
	class="fixed inset-x-0 bottom-0 z-40 max-w-full overflow-x-hidden border-t md:hidden"
	style="background-color: var(--app-nav-bg); border-color: var(--app-nav-border);"
	aria-label="Mobile navigation"
>
	{#if menuOpen}
		<div
			id="mobile-nav-menu"
			data-mobile-menu
			class="border-b px-3 py-3 shadow-lg"
			style="border-color: var(--app-nav-border); background-color: var(--app-nav-bg);"
		>
			<div class="mx-auto flex max-w-full flex-col gap-3">
				<div class="min-w-0">
					<BookSwitcher {books} {activeBook} compact />
				</div>
				<div class="flex max-w-full flex-wrap items-center gap-2">
					<LocaleSwitcher {locale} {returnTo} compact />
					<ThemeSwitcher />
					<form method="POST" action="/logout" class="min-w-0">
						<button
							type="submit"
							class="min-h-[44px] min-w-[44px] rounded-lg border px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--app-hover-bg)]"
							style="border-color: var(--app-border); color: var(--app-muted);"
						>
							{t(locale, 'nav.logout')}
						</button>
					</form>
				</div>
			</div>
		</div>
	{/if}

	<div class="flex max-w-full items-center justify-between gap-2 border-b px-3 py-2" style="border-color: var(--app-nav-border);">
		<div class="min-w-0 flex-1 truncate text-xs font-medium" style="color: var(--app-muted);">
			{#if activeBook}
				<span class="sr-only">Current book:</span>{activeBook.name}
			{:else}
				GnuCash Web Companion
			{/if}
		</div>
		<button
			type="button"
			class="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg border px-3 text-sm font-medium transition-colors hover:bg-[var(--app-hover-bg)]"
			style="border-color: var(--app-border); color: var(--app-text);"
			aria-expanded={menuOpen}
			aria-controls="mobile-nav-menu"
			onclick={toggleMenu}
		>
			<span aria-hidden="true">☰</span>
			<span class="sr-only">{menuOpen ? 'Close mobile menu' : 'Open mobile menu'}</span>
		</button>
	</div>

	<div class="safe-bottom flex max-w-full items-stretch justify-around">
		{#each navLinks as link}
			{@const active = isActivePath(link.href)}
			<a
				href={link.href}
				aria-current={active ? 'page' : undefined}
				data-active-route={active ? 'true' : 'false'}
				class="flex min-h-[44px] min-w-[44px] flex-1 flex-col items-center justify-center gap-0.5 px-1 py-2 text-[10px] font-medium transition-colors"
				style={active ? 'color: var(--app-accent); background: var(--app-hover-bg);' : 'color: var(--app-muted);'}
				onclick={closeMenu}
			>
				<span class="h-[22px] w-[22px]" aria-hidden="true">
					{@html iconFor(link.icon, active)}
				</span>
				<span class="max-w-full truncate">{link.label}</span>
			</a>
		{/each}
	</div>
</nav>
