<script lang="ts">
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
		{ href: '/dashboard', label: t(locale, 'nav.dashboard'), icon: 'home' },
		{ href: '/accounts', label: t(locale, 'nav.accounts'), icon: 'accounts' },
		{ href: '/transactions', label: t(locale, 'nav.transactions'), icon: 'transactions' },
		{ href: '/books', label: t(locale, 'nav.books'), icon: 'books' }
	] as const);

	function iconFor(name: string, active: boolean) {
		const c = active ? 'var(--app-accent)' : 'var(--app-muted)';
		switch (name) {
			case 'home':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`;
			case 'accounts':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>`;
			case 'transactions':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`;
			case 'books':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>`;
			default:
				return '';
		}
	}
</script>

<nav
	class="fixed bottom-0 left-0 right-0 z-40 border-t md:hidden"
	style="background-color: var(--app-nav-bg); border-color: var(--app-nav-border);"
	aria-label="Mobile navigation"
>
	<!-- Book switcher row above the nav links on mobile -->
	<div class="flex items-center justify-center gap-3 border-b px-3 py-2" style="border-color: var(--app-nav-border);">
		<BookSwitcher {books} {activeBook} />
		<LocaleSwitcher {locale} {returnTo} compact />
	</div>
	<div class="flex items-stretch justify-around safe-bottom">
		{#each navLinks as link}
			<a
				href={link.href}
				class="flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] font-medium transition-colors"
				style="color: var(--app-muted);"
			>
				<span class="h-[22px] w-[22px]" aria-hidden="true">
					{@html iconFor(link.icon, false)}
				</span>
				<span>{link.label}</span>
			</a>
		{/each}
	</div>
</nav>
