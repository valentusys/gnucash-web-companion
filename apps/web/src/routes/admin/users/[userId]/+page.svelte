<script lang="ts">
	import type { AdminBookAccessRole, AdminBookOptionList, AdminProblemCode, AdminUserDetail } from '$lib/api/types';
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
			currentUserId: number;
			user: AdminUserDetail | null;
			bookOptions: AdminBookOptionList;
			bookOptionsErrorCode: AdminProblemCode | null;
			loadErrorCode: AdminProblemCode | null;
			successCode: string | null;
		};
		form?: { adminErrorCode?: AdminProblemCode; adminSuccessCode?: AdminSuccessCode } | null;
	} = $props();

	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	let bookOptions = $derived(data.bookOptions.items);
	let bookRangeStart = $derived(bookOptions.length ? data.bookOptions.offset + 1 : 0);
	let bookRangeEnd = $derived(data.bookOptions.offset + bookOptions.length);
	let previousBookOffset = $derived(Math.max(0, data.bookOptions.offset - data.bookOptions.limit));
	let nextBookOffset = $derived(data.bookOptions.offset + data.bookOptions.limit);
	let isEmptyLaterBookPage = $derived(!data.bookOptionsErrorCode && bookOptions.length === 0 && data.bookOptions.total_count > 0 && data.bookOptions.offset > 0);
	const roles: AdminBookAccessRole[] = ['viewer', 'editor', 'owner'];

	function bookPageHref(offset: number): string {
		const params = new URLSearchParams({
			book_limit: String(data.bookOptions.limit),
			book_offset: String(Math.max(0, offset))
		});
		return `?${params.toString()}`;
	}

	function actionHref(actionName: string): string {
		const params = new URLSearchParams({
			book_limit: String(data.bookOptions.limit),
			book_offset: String(data.bookOptions.offset)
		});
		return `?/${actionName}&${params.toString()}`;
	}

	function problemMessage(code: AdminProblemCode | undefined | null): string {
		return t(locale, `adminUsers.problem.${code ?? 'unknown_admin_problem'}` as MessageKey);
	}

	function successMessage(code: string | undefined | null): string {
		return t(locale, `adminUsers.success.${code ?? 'display_name_changed'}` as MessageKey);
	}

	function statusLabel(enabled: boolean): string {
		return enabled ? t(locale, 'adminUsers.enabled') : t(locale, 'adminUsers.disabled');
	}

	function roleLabel(role: AdminBookAccessRole): string {
		return t(locale, `adminUsers.role.${role}` as MessageKey);
	}

	function roleCopy(role: AdminBookAccessRole): string {
		return t(locale, `adminUsers.roleCopy.${role}` as MessageKey);
	}

	function bookName(bookId: number, fallback: string): string {
		return data.bookOptions.items.find((book) => book.id === bookId)?.name ?? fallback;
	}
</script>

<svelte:head>
	<title>{data.user?.username ?? t(locale, 'adminUsers.detailTitle')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl px-4 py-8">
	<a href="/admin/users" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'adminUsers.backToUsers')}</a>

	<div class="mt-6 space-y-2">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'adminUsers.kicker')}</p>
		<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{data.user?.display_name ?? t(locale, 'adminUsers.detailTitle')}</h1>
		<p class="max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.detailSubtitle')}</p>
		<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'adminUsers.safeBoundaryBadge')}</span>
	</div>

	{#if !data.isAdmin}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" role="alert">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.adminRequiredTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.adminRequiredMessage')}</p>
		</section>
	{:else if data.loadErrorCode || !data.user}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-danger); background-color: var(--app-card-bg);" role="alert">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.detailTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{problemMessage(data.loadErrorCode)}</p>
		</section>
	{:else}
		{#if form?.adminSuccessCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(form.adminSuccessCode)}</p>
		{:else if data.successCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(data.successCode)}</p>
		{/if}
		{#if form?.adminErrorCode}
			<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{problemMessage(form.adminErrorCode)}</p>
		{/if}

		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.summaryTitle')}</h2>
			<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
				<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.username')}</dt><dd class="mt-1 break-words font-mono" style="color: var(--app-text);">{data.user.username}</dd></div>
				<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.status')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{statusLabel(data.user.is_enabled)}</dd></div>
				<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.assignmentCount')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{data.user.assignment_count}</dd></div>
				<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'adminUsers.updatedAt')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{data.user.updated_at}</dd></div>
			</dl>
			<div class="mt-3 flex flex-wrap gap-2">
				<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{statusLabel(data.user.is_enabled)}</span>
				<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{data.user.is_admin ? t(locale, 'adminUsers.adminBadge') : t(locale, 'adminUsers.userBadge')}</span>
			</div>
			<p class="mt-3 text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.limitedActionsNote')}</p>
		</section>

		<section class="mt-4 grid min-w-0 gap-4 lg:grid-cols-2">
			<form method="POST" action={actionHref('updateDisplayName')} class="min-w-0 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.updateDisplayNameTitle')}</h2>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.updateDisplayNameHelp')}</p>
				<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);">
					{t(locale, 'adminUsers.displayName')}
					<input name="display_name" required maxlength="100" autocomplete="name" value={data.user.display_name} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
				</label>
				<button type="submit" class="mt-3 min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'adminUsers.updateDisplayNameSubmit')}</button>
			</form>

			<section class="min-w-0 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
				{#if data.user.is_enabled}
					<form method="POST" action={actionHref('disableUser')}>
						<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.disableTitle')}</h2>
						<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.disableHelp')}</p>
						<label class="mt-3 flex items-start gap-2 text-xs" style="color: var(--app-muted);">
							<input required type="checkbox" name="confirm_disable" class="mt-1" />
							<span>{t(locale, 'adminUsers.confirmDisableCopy')}</span>
						</label>
						<button type="submit" class="mt-3 min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'adminUsers.disableSubmit')}</button>
					</form>
				{:else}
					<form method="POST" action={actionHref('enableUser')}>
						<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.enableTitle')}</h2>
						<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.enableHelp')}</p>
						<button type="submit" class="mt-3 min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'adminUsers.enableSubmit')}</button>
					</form>
				{/if}
			</section>
		</section>

		<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.resetPasswordTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.resetPasswordHelp')}</p>
			<form method="POST" action={actionHref('resetPassword')} class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
				<label class="text-sm font-medium md:col-span-2" style="color: var(--app-text);">
					{t(locale, 'adminUsers.newPassword')}
					<input name="new_password" required type="password" autocomplete="new-password" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
				</label>
				<label class="flex min-h-11 items-start gap-2 text-xs md:col-span-2" style="color: var(--app-muted);">
					<input required type="checkbox" name="confirm_reset" class="mt-1" />
					<span>{t(locale, 'adminUsers.confirmResetCopy')}</span>
				</label>
				<div class="md:col-span-2">
					<p class="mb-3 text-xs" style="color: var(--app-muted);">{t(locale, 'adminUsers.passwordNotRepopulated')}</p>
					<button type="submit" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'adminUsers.resetPasswordSubmit')}</button>
				</div>
			</form>
		</section>

		<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.accessTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.accessHelp')}</p>
			<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.roleBoundary')}</p>

			<div class="mt-4 grid min-w-0 gap-3 md:grid-cols-3">
				{#each roles as role}
					<div class="min-w-0 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-bg);">
						<p class="font-semibold" style="color: var(--app-text);">{roleLabel(role)}</p>
						<p class="mt-1" style="color: var(--app-muted);">{roleCopy(role)}</p>
					</div>
				{/each}
			</div>

			{#if !data.bookOptionsErrorCode}
				<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
					<p class="text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'adminUsers.bookOptionsRange', { start: bookRangeStart, end: bookRangeEnd, total: data.bookOptions.total_count })}
					</p>
					<p class="mt-1 text-xs" style="color: var(--app-muted);">
						{t(locale, 'adminUsers.bookOptionsPageStatus', { limit: data.bookOptions.limit, offset: data.bookOptions.offset })}
					</p>
					<nav class="mt-3 flex min-w-0 flex-wrap items-center gap-2 text-sm" aria-label={t(locale, 'adminUsers.bookOptionsPagerLabel')}>
						{#if data.bookOptions.offset > 0}
							<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={bookPageHref(previousBookOffset)} rel="prev">{t(locale, 'adminUsers.previousBookOptions')}</a>
						{:else}
							<span class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 opacity-60" style="border-color: var(--app-border); color: var(--app-muted);" aria-disabled="true">{t(locale, 'adminUsers.previousBookOptions')}</span>
						{/if}
						{#if data.bookOptions.has_next}
							<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={bookPageHref(nextBookOffset)} rel="next">{t(locale, 'adminUsers.nextBookOptions')}</a>
						{:else}
							<span class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 opacity-60" style="border-color: var(--app-border); color: var(--app-muted);" aria-disabled="true">{t(locale, 'adminUsers.nextBookOptions')}</span>
						{/if}
					</nav>
				</div>
			{/if}

			{#if data.bookOptionsErrorCode}
				<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-danger); background-color: var(--app-bg);" role="alert">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.bookOptionsUnavailableTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.bookOptionsUnavailableMessage')}</p>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{problemMessage(data.bookOptionsErrorCode)}</p>
				</div>
			{:else if bookOptions.length}
				<form method="POST" action={actionHref('grantAccess')} class="mt-4 grid min-w-0 gap-3 md:grid-cols-[minmax(0,1fr)_12rem_auto]">
					<label class="text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'adminUsers.book')}
						<select name="book_id" required class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);">
							{#each bookOptions as book (book.id)}
								<option value={book.id}>{book.name}</option>
							{/each}
						</select>
					</label>
					<label class="text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'adminUsers.role')}
						<select name="role" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);">
							<option value="viewer" selected>{t(locale, 'adminUsers.role.viewer')}</option>
							<option value="editor">{t(locale, 'adminUsers.role.editor')}</option>
							<option value="owner">{t(locale, 'adminUsers.role.owner')}</option>
						</select>
					</label>
					<div class="flex items-end">
						<button type="submit" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'adminUsers.grantSubmit')}</button>
					</div>
				</form>
			{:else if isEmptyLaterBookPage}
				<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);" role="status">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.emptyBookOptionsPageTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.emptyBookOptionsPageMessage')}</p>
					<div class="mt-3 flex flex-wrap gap-2 text-sm">
						<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={bookPageHref(previousBookOffset)} rel="prev">{t(locale, 'adminUsers.previousBookOptions')}</a>
						<a class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2" style="border-color: var(--app-border); color: var(--app-text);" href={bookPageHref(0)}>{t(locale, 'adminUsers.firstBookOptions')}</a>
					</div>
				</div>
			{:else}
				<div class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'adminUsers.noBooksTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'adminUsers.noBooksMessage')}</p>
				</div>
			{/if}

			{#if data.user.assignments.length}
				<div class="mt-4 grid min-w-0 gap-3">
					{#each data.user.assignments as assignment (assignment.book_id)}
						<article class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
							<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
								<div class="min-w-0">
									<h3 class="break-words font-semibold" style="color: var(--app-text);">{bookName(assignment.book_id, assignment.book_name)}</h3>
									<p class="mt-1 text-sm" style="color: var(--app-muted);">{roleLabel(assignment.role)} — {roleCopy(assignment.role)}</p>
								</div>
								<form method="POST" action={actionHref('revokeAccess')} class="min-w-0 rounded-lg border p-3" style="border-color: var(--app-border);">
									<input type="hidden" name="book_id" value={assignment.book_id} />
									<label class="flex items-start gap-2 text-xs" style="color: var(--app-muted);">
										<input required type="checkbox" name="confirm_revoke" class="mt-1" />
										<span>{t(locale, 'adminUsers.confirmRevokeCopy')}</span>
									</label>
									<button type="submit" class="mt-3 min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'adminUsers.revokeSubmit')}</button>
								</form>
							</div>
						</article>
					{/each}
				</div>
			{:else}
				<p class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); color: var(--app-muted); background-color: var(--app-bg);">{t(locale, 'adminUsers.noAssignments')}</p>
			{/if}
		</section>
	{/if}
</main>
