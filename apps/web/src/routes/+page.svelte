<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import { DEFAULT_LOCALE, t } from '$lib/i18n';
</script>

<main class="flex min-h-screen flex-col items-center justify-center px-4 text-center" style="background-color: var(--app-bg);">
	<div class="absolute right-4 top-4">
		<ThemeSwitcher />
	</div>
	<h1 class="text-4xl font-bold" style="color: var(--app-text);">GnuCash Web Companion</h1>
	<p class="mt-4 max-w-xl text-lg" style="color: var(--app-muted);">
		{t(DEFAULT_LOCALE, 'home.subtitle')}
	</p>
	<div class="mt-8 flex flex-col gap-3 sm:flex-row">
		<a
			href="/login"
			class="rounded-xl px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:opacity-90"
			style="background-color: var(--app-accent);"
		>
			{t(DEFAULT_LOCALE, 'login.submit')}
		</a>
		<a
			href="/diagnostics"
			class="rounded-xl border px-5 py-3 text-sm font-semibold shadow-sm transition-colors hover:underline"
			style="border-color: var(--app-border); color: var(--app-accent);"
		>
			First-run diagnostics
		</a>
	</div>
</main>
