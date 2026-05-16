<script lang="ts">
	import { onMount } from 'svelte';
	import { getInitialTheme, applyTheme, storeTheme, toggleTheme, type Theme } from '$lib/theme';

	let theme = $state<Theme>('light');

	onMount(() => {
		theme = getInitialTheme();
		applyTheme(theme);
	});

	function handleToggle() {
		theme = toggleTheme(theme);
		applyTheme(theme);
		storeTheme(theme);
	}

	const isDark = $derived(theme === 'dark');
</script>

<button
	type="button"
	class="inline-flex items-center justify-center rounded-lg border px-2 py-2 text-sm transition-colors hover:bg-[var(--app-hover-bg)] focus-visible:ring-2 focus-visible:ring-[var(--app-accent)] focus-visible:ring-offset-2"
	style="border-color: var(--app-border);"
	aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
	title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
	onclick={handleToggle}
>
	<span class="sr-only">{isDark ? 'Switch to light mode' : 'Switch to dark mode'}</span>
	{#if isDark}
		<!-- Sun icon -->
		<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
			<circle cx="12" cy="12" r="5"/>
			<line x1="12" y1="1" x2="12" y2="3"/>
			<line x1="12" y1="21" x2="12" y2="23"/>
			<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
			<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
			<line x1="1" y1="12" x2="3" y2="12"/>
			<line x1="21" y1="12" x2="23" y2="12"/>
			<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
			<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
		</svg>
	{:else}
		<!-- Moon icon -->
		<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
			<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
		</svg>
	{/if}
</button>
