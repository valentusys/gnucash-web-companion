<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
</script>

<svelte:head>
	<title>{t(locale, 'login.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="flex min-h-screen items-center justify-center px-4 py-12" style="background-color: var(--app-bg);">
	<section class="w-full max-w-md rounded-2xl p-6 shadow-sm sm:p-8" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow);">
		<div class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight" style="color: var(--app-text);">{t(locale, 'login.title')}</h1>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'login.subtitle')}</p>
			</div>
			<div class="flex items-center gap-2">
				<LocaleSwitcher {locale} returnTo="/login" compact />
				<ThemeSwitcher />
			</div>
		</div>

		{#if form?.error}
			<div
				class="mb-4 rounded-xl border px-4 py-3 text-sm"
				style="border-color: var(--app-danger); background-color: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel)); color: var(--app-danger);"
				role="alert"
			>
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-5">
			<label class="block">
				<span class="text-sm font-medium" style="color: var(--app-text);">{t(locale, 'login.username')}</span>
				<input
					name="username"
					type="text"
					autocomplete="username"
					required
					value={form?.username ?? 'admin'}
					class="mt-2 block w-full rounded-xl border px-4 py-3 text-base shadow-sm focus:outline-none focus:ring-2"
					style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text); --tw-ring-color: var(--app-ring);"
				/>
			</label>

			<label class="block">
				<span class="text-sm font-medium" style="color: var(--app-text);">{t(locale, 'login.password')}</span>
				<input
					name="password"
					type="password"
					autocomplete="current-password"
					required
					class="mt-2 block w-full rounded-xl border px-4 py-3 text-base shadow-sm focus:outline-none focus:ring-2"
					style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text); --tw-ring-color: var(--app-ring);"
				/>
			</label>

			<button
				type="submit"
				class="w-full rounded-xl px-4 py-3 text-base font-semibold text-white shadow-sm transition-colors hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2"
				style="background-color: var(--app-accent); --tw-ring-color: var(--app-accent);"
			>
				{t(locale, 'login.submit')}
			</button>
		</form>
	</section>
</main>
