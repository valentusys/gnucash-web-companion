<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
</script>

<main class="flex min-h-screen flex-col items-center justify-center px-4 text-center" style="background-color: var(--app-bg);">
	<div class="absolute right-4 top-4">
		<ThemeSwitcher />
	</div>
	<h1 class="text-4xl font-bold" style="color: var(--app-text);">GnuCash Web Companion</h1>
	<p class="mt-4 max-w-xl text-lg" style="color: var(--app-muted);">
		Modern self-hosted read-only companion for existing GnuCash books.
	</p>
	<a
		href="/login"
		class="mt-8 rounded-xl px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:opacity-90"
		style="background-color: var(--app-accent);"
	>
		Sign in
	</a>
</main>
