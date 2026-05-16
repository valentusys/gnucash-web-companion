<script lang="ts">
	import '../app.css';
	import DesktopNav from '$lib/components/DesktopNav.svelte';
	import MobileNav from '$lib/components/MobileNav.svelte';

	let { data, children }: { data: any; children: any } = $props();
	let showAppShell = $derived(data.authenticated && data.pathname !== '/login');
</script>

<div class="min-h-screen" style="background-color: var(--app-bg); color: var(--app-text);">
	{#if showAppShell}
		<DesktopNav />
		<MobileNav />
		<!-- Bottom nav spacer: prevents content from being hidden behind fixed bottom nav on mobile -->
		<div class="pb-16 md:pb-0">
			{@render children()}
		</div>
	{:else}
		{@render children()}
	{/if}
</div>
