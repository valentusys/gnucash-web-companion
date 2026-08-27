<script lang="ts">
	import '../app.css';
	import DesktopNav from '$lib/components/DesktopNav.svelte';
	import MobileNav from '$lib/components/MobileNav.svelte';
	import ReadOnlyStatusBanner from '$lib/components/ReadOnlyStatusBanner.svelte';
	import type { Book } from '$lib/api/types';
	import { DEFAULT_LOCALE, type Locale } from '$lib/i18n';

	let { data, children }: { data: any; children: any } = $props();
	let showAppShell = $derived(data.authenticated && data.pathname !== '/login');
	let books = $derived<Book[]>(data.books ?? []);
	let activeBook = $derived<Book | null>(data.activeBook ?? null);
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isAdmin = $derived(data.isAdmin === true);
</script>

<div class="min-h-screen overflow-x-hidden max-w-full" style="background-color: var(--app-bg); color: var(--app-text);">
	{#if showAppShell}
		<DesktopNav {books} {activeBook} {locale} {isAdmin} currentPath={data.pathname} returnTo={data.pathname} />
		<ReadOnlyStatusBanner {locale} {activeBook} />
		<MobileNav {books} {activeBook} {locale} {isAdmin} currentPath={data.pathname} returnTo={data.pathname} />
		<!-- Bottom nav spacer: prevents content from being hidden behind the compact mobile tab bar -->
		<div class="pb-24 md:pb-0">
			{@render children()}
		</div>
	{:else}
		{@render children()}
	{/if}
</div>
