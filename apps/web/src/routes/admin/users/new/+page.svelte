<script lang="ts">
	import type { AdminProblemCode } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';

	type SafeCreateForm = {
		username: string;
		displayName: string;
		isAdmin: boolean;
	};

	let {
		data,
		form
	}: {
		data: { locale?: Locale; isAdmin: boolean };
		form?: { adminErrorCode?: AdminProblemCode; createRequest?: SafeCreateForm } | null;
	} = $props();

	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let previous = $derived<SafeCreateForm>(form?.createRequest ?? { username: '', displayName: '', isAdmin: false });

	function problemMessage(code: AdminProblemCode | undefined | null): string {
		return t(locale, `adminUsers.problem.${code ?? 'unknown_admin_problem'}` as MessageKey);
	}
</script>

<svelte:head>
	<title>{t(locale, 'adminUsers.newTitle')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/admin/users" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'adminUsers.backToUsers')}</a>

	<div class="mt-6 space-y-2">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'adminUsers.kicker')}</p>
		<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'adminUsers.newTitle')}</h1>
		<p class="max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.newSubtitle')}</p>
		<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'adminUsers.safeBoundaryBadge')}</span>
	</div>

	{#if !data.isAdmin}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" role="alert">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.adminRequiredTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.adminRequiredMessage')}</p>
		</section>
	{:else}
		{#if form?.adminErrorCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{problemMessage(form.adminErrorCode)}</p>
		{/if}

		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.createTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.zeroAccessDefault')}</p>
			<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.limitedActionsNote')}</p>

			<form method="POST" action="?/create" class="mt-4 grid min-w-0 gap-4 md:grid-cols-2">
				<label class="text-sm font-medium" style="color: var(--app-text);">
					{t(locale, 'adminUsers.username')}
					<input name="username" required minlength="3" maxlength="64" autocomplete="username" value={previous.username} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 font-mono text-sm" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
					<span class="mt-1 block text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.usernameHelp')}</span>
				</label>
				<label class="text-sm font-medium" style="color: var(--app-text);">
					{t(locale, 'adminUsers.displayName')}
					<input name="display_name" required maxlength="100" autocomplete="name" value={previous.displayName} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
					<span class="mt-1 block text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.displayNameHelp')}</span>
				</label>
				<label class="text-sm font-medium md:col-span-2" style="color: var(--app-text);">
					{t(locale, 'adminUsers.initialPassword')}
					<input name="initial_password" required type="password" autocomplete="new-password" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
					<span class="mt-1 block text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.passwordHelp')}</span>
				</label>
				<label class="flex min-h-11 items-start gap-3 rounded-xl border p-3 text-sm md:col-span-2" style="border-color: var(--app-border); color: var(--app-muted);">
					<input name="is_admin" type="checkbox" checked={previous.isAdmin} class="mt-1" />
					<span><span class="font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.isAdminChoice')}</span><br />{t(locale, 'adminUsers.isAdminHelp')}</span>
				</label>
				<div class="md:col-span-2">
					<p class="mb-3 text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.passwordNotRepopulated')}</p>
					<button type="submit" class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'adminUsers.createSubmit')}</button>
				</div>
			</form>
		</section>
	{/if}
</main>
