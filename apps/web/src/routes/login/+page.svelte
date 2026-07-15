<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';
	import type { PageData } from './$types';

	let { data, form }: { data: PageData; form: { error?: string; username?: string } | null } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	const firstRunLabels: Array<[
		'jwt_secret' | 'admin_bootstrap' | 'default_book' | 'cors' | 'write_mode',
		MessageKey
	]> = [
		['jwt_secret', 'login.firstRun.jwtSecret'],
		['admin_bootstrap', 'login.firstRun.adminBootstrap'],
		['default_book', 'login.firstRun.defaultBook'],
		['cors', 'login.firstRun.cors'],
		['write_mode', 'login.firstRun.writeMode']
	];

	function statusLabel(status: string): string {
		if (status === 'ok') return t(locale, 'login.firstRun.status.ok');
		if (status === 'warning') return t(locale, 'login.firstRun.status.warning');
		if (status === 'action_required') return t(locale, 'login.firstRun.status.actionRequired');
		return status.replaceAll('_', ' ');
	}
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
		{:else if data.loginReason === 'session_changed'}
			<div
				class="mb-4 rounded-xl border px-4 py-3 text-sm"
				style="border-color: var(--app-border); background-color: var(--app-card-bg); color: var(--app-text);"
				role="status"
			>
				{t(locale, 'login.notice.sessionChanged')}
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

		{#if data.firstRun}
			<section
				class="mt-6 min-w-0 rounded-2xl border p-4 text-sm"
				style="border-color: var(--app-border); background-color: var(--app-card-bg);"
				aria-label={t(locale, 'login.firstRun.title')}
			>
				<h2 class="text-base font-semibold" style="color: var(--app-text);">{t(locale, 'login.firstRun.title')}</h2>
				<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'login.firstRun.summary')}</p>
				<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'login.firstRun.safeDiagnostics')}</p>
				<ul class="mt-4 space-y-2">
					{#each firstRunLabels as [checkKey, labelKey]}
						{@const check = data.firstRun.checks[checkKey]}
						<li class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
							<div class="flex min-w-0 flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
								<p class="font-medium" style="color: var(--app-text);">{t(locale, labelKey)}</p>
								<span class="w-fit rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{statusLabel(check.status)}</span>
							</div>
							<p class="mt-2 break-words text-xs" style="color: var(--app-muted);">{check.message}</p>
							{#if check.safe_next_actions?.length}
								<ul class="mt-2 list-disc space-y-1 pl-4 text-xs" style="color: var(--app-muted);">
									{#each check.safe_next_actions as action}
										<li class="break-words">{action}</li>
									{/each}
								</ul>
							{/if}
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	</section>
</main>
