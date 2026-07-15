<script lang="ts">
	import { navigating } from '$app/state';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import LoadingState from '$lib/components/LoadingState.svelte';
	import type { AdminProblemCode, AdminUserList, AdminUserStateFilter } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';

	type AdminSuccessCode =
		| 'user_created'
		| 'display_name_changed'
		| 'user_enabled'
		| 'user_disabled'
		| 'password_reset'
		| 'book_access_granted'
		| 'book_access_revoked';

	let {
		data,
		form
	}: {
		data: {
			locale?: Locale;
			isAdmin: boolean;
			users: AdminUserList;
			filters: { limit: number; offset: number; state: AdminUserStateFilter };
			loadErrorCode: AdminProblemCode | null;
			successCode: string | null;
		};
		form?: { adminErrorCode?: AdminProblemCode; adminSuccessCode?: AdminSuccessCode } | null;
	} = $props();

	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let isRouteLoading = $derived(navigating.to?.url.pathname === '/admin/users');

	function problemMessage(code: AdminProblemCode | undefined | null): string {
		return t(locale, `adminUsers.problem.${code ?? 'unknown_admin_problem'}` as MessageKey);
	}

	function successMessage(code: string | undefined | null): string {
		return t(locale, `adminUsers.success.${code ?? 'user_created'}` as MessageKey);
	}

	function stateHref(state: AdminUserStateFilter): string {
		const params = new URLSearchParams({ limit: String(data.filters.limit), offset: '0', state });
		return `/admin/users?${params.toString()}`;
	}

	function pageHref(offset: number): string {
		const params = new URLSearchParams({
			limit: String(data.filters.limit),
			offset: String(Math.max(0, offset)),
			state: data.filters.state
		});
		return `/admin/users?${params.toString()}`;
	}

	function statusLabel(enabled: boolean): string {
		return enabled ? t(locale, 'adminUsers.enabled') : t(locale, 'adminUsers.disabled');
	}
</script>

<svelte:head>
	<title>{t(locale, 'adminUsers.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'adminUsers.kicker')}</p>
		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div class="min-w-0">
				<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'adminUsers.title')}</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.subtitle')}</p>
			</div>
			{#if data.isAdmin}
				<a class="inline-flex min-h-11 w-fit items-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);" href="/admin/users/new">{t(locale, 'adminUsers.createUser')}</a>
			{/if}
		</div>
		<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'adminUsers.safeBoundaryBadge')}</span>
	</div>

	{#if !data.isAdmin}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" role="alert">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.adminRequiredTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.adminRequiredMessage')}</p>
		</section>
	{:else}
		{#if form?.adminSuccessCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(form.adminSuccessCode)}</p>
		{:else if data.successCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(data.successCode)}</p>
		{/if}
		{#if form?.adminErrorCode || data.loadErrorCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{problemMessage(form?.adminErrorCode ?? data.loadErrorCode)}</p>
		{/if}

		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
				<div class="min-w-0">
					<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.listTitle')}</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.listHelp')}</p>
				</div>
				<form method="GET" action="/admin/users" class="flex min-w-0 flex-wrap items-end gap-2">
					<label class="text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'adminUsers.stateFilter')}
						<select name="state" class="mt-1 min-h-11 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);">
							<option value="all" selected={data.filters.state === 'all'}>{t(locale, 'adminUsers.stateAll')}</option>
							<option value="enabled" selected={data.filters.state === 'enabled'}>{t(locale, 'adminUsers.stateEnabled')}</option>
							<option value="disabled" selected={data.filters.state === 'disabled'}>{t(locale, 'adminUsers.stateDisabled')}</option>
						</select>
					</label>
					<input type="hidden" name="limit" value={data.filters.limit} />
					<input type="hidden" name="offset" value="0" />
					<button type="submit" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'adminUsers.applyFilter')}</button>
				</form>
			</div>

			<div class="mt-3 flex flex-wrap gap-2 text-sm">
				<a class="rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={stateHref('all')}>{t(locale, 'adminUsers.stateAll')}</a>
				<a class="rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={stateHref('enabled')}>{t(locale, 'adminUsers.stateEnabled')}</a>
				<a class="rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={stateHref('disabled')}>{t(locale, 'adminUsers.stateDisabled')}</a>
			</div>

			{#if isRouteLoading}
				<div class="mt-4"><LoadingState message={t(locale, 'adminUsers.loading')} /></div>
			{:else if data.users.items.length === 0 && !data.loadErrorCode}
				<div class="mt-4">
					<EmptyState title={t(locale, 'adminUsers.emptyTitle')} message={t(locale, 'adminUsers.emptyMessage')} ariaLabel={t(locale, 'adminUsers.emptyTitle')} icon="👥">
						<a href="/admin/users/new" class="rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'adminUsers.createUser')}</a>
					</EmptyState>
				</div>
			{:else}
				<div class="mt-4 grid min-w-0 gap-3">
					{#each data.users.items as user (user.id)}
						<article class="min-w-0 rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
							<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
								<div class="min-w-0">
									<h3 class="break-words text-lg font-semibold" style="color: var(--app-text);">{user.display_name || user.username}</h3>
									<p class="mt-1 break-words text-sm font-mono" style="color: var(--app-muted);">{user.username}</p>
									<div class="mt-2 flex flex-wrap gap-2">
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{statusLabel(user.is_enabled)}</span>
										<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{user.is_admin ? t(locale, 'adminUsers.adminBadge') : t(locale, 'adminUsers.userBadge')}</span>
									</div>
								</div>
								<div class="flex flex-wrap gap-2">
									<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={`/admin/users/${user.id}`}>{t(locale, 'adminUsers.viewDetails')}</a>
									{#if !user.is_enabled}
										<form method="POST" action="?/enableUser">
											<input type="hidden" name="user_id" value={user.id} />
											<button type="submit" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'adminUsers.enableSubmit')}</button>
										</form>
									{/if}
								</div>
							</div>
							<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
								<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.assignmentCount')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{user.assignment_count}</dd></div>
								<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.createdAt')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{user.created_at}</dd></div>
								<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.updatedAt')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{user.updated_at}</dd></div>
								<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.status')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{statusLabel(user.is_enabled)}</dd></div>
							</dl>
						</article>
					{/each}
				</div>
				<div class="mt-4 flex flex-wrap items-center gap-2 text-sm">
					{#if data.filters.offset > 0}
						<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={pageHref(data.filters.offset - data.filters.limit)}>{t(locale, 'adminUsers.previousPage')}</a>
					{/if}
					{#if data.users.has_next}
						<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={pageHref(data.filters.offset + data.filters.limit)}>{t(locale, 'adminUsers.nextPage')}</a>
					{/if}
				</div>
			{/if}
		</section>
	{/if}
</main>
