import { error, fail, isHttpError, isRedirect, redirect } from '@sveltejs/kit';
import {
	adminApiMutationFetch,
	apiFetch,
	getAuthToken,
	getCurrentUser,
	isCurrentUserAdmin,
	redirectToSessionChanged
} from '$lib/api/server';
import type {
	AdminBookAccess,
	AdminBookOptionList,
	AdminBookAccessRole,
	AdminBookOption,
	AdminPasswordResetResult,
	AdminProblemCode,
	AdminUserDetail
} from '$lib/api/types';
import type { Cookies } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const ACCESS_ROLES = new Set<AdminBookAccessRole>(['owner', 'editor', 'viewer']);
const SUCCESS_CODES = new Set([
	'user_created',
	'display_name_changed',
	'user_enabled',
	'user_disabled',
	'password_reset',
	'book_access_granted',
	'book_access_revoked'
]);

type AdminActor = { id: number; isAdmin: boolean };

function userIdFromParams(params: { userId?: string }): number {
	const userId = Number(params.userId);
	if (!Number.isInteger(userId) || userId <= 0) {
		throw error(404, 'Requested item was not found.');
	}
	return userId;
}

function textField(form: FormData, name: string): string {
	return String(form.get(name) ?? '').trim();
}

function secretField(form: FormData, name: string): string {
	return String(form.get(name) ?? '');
}

function safeRole(form: FormData): AdminBookAccessRole {
	const role = String(form.get('role') ?? 'viewer');
	return ACCESS_ROLES.has(role as AdminBookAccessRole) ? (role as AdminBookAccessRole) : 'viewer';
}

async function adminActor(fetchFn: typeof fetch, token: string, cookies: Cookies): Promise<AdminActor> {
	const currentUser = await getCurrentUser(fetchFn, token, cookies);
	return { id: currentUser.id, isAdmin: isCurrentUserAdmin(currentUser) };
}

function adminActorFromLayout(currentUser: Awaited<ReturnType<typeof getCurrentUser>> | null): AdminActor {
	return { id: currentUser?.id ?? 0, isAdmin: isCurrentUserAdmin(currentUser) };
}

function loadProblemCode(reason: unknown): AdminProblemCode {
	if (isHttpError(reason)) {
		if (reason.status === 401) return 'session_changed';
		if (reason.status === 403) return 'admin_required';
		if (reason.status === 404) return 'user_not_found';
	}
	return 'api_unavailable';
}

function safeAdminSuccess(searchParams: URLSearchParams): string | null {
	const candidate = searchParams.get('admin_success');
	return candidate && SUCCESS_CODES.has(candidate) ? candidate : null;
}

export const load: PageServerLoad = async ({ cookies, fetch, parent, params, url }) => {
	const token = getAuthToken(cookies);
	const userId = userIdFromParams(params);
	const layoutData = await parent();
	const actor = adminActorFromLayout(layoutData.currentUser);
	const successCode = safeAdminSuccess(url.searchParams);

	if (!actor.isAdmin) {
		return {
			isAdmin: false,
			currentUserId: actor.id,
			user: null,
			bookOptions: [] as AdminBookOption[],
			bookOptionsErrorCode: null,
			loadErrorCode: null,
			successCode
		};
	}

	try {
		const user = await apiFetch<AdminUserDetail>(fetch, `/admin/users/${userId}`, token, cookies);
		let bookOptions: AdminBookOption[] = [];
		let bookOptionsErrorCode: AdminProblemCode | null = null;
		try {
			const bookOptionPage = await apiFetch<AdminBookOptionList>(fetch, '/admin/book-access/books?limit=50&offset=0', token, cookies);
			bookOptions = bookOptionPage.items;
		} catch (reason) {
			if (isRedirect(reason)) throw reason;
			bookOptions = [];
			bookOptionsErrorCode = 'api_unavailable';
		}
		return {
			isAdmin: true,
			currentUserId: actor.id,
			user,
			bookOptions,
			bookOptionsErrorCode,
			loadErrorCode: null,
			successCode
		};
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		return {
			isAdmin: true,
			currentUserId: actor.id,
			user: null,
			bookOptions: [] as AdminBookOption[],
			bookOptionsErrorCode: null,
			loadErrorCode: loadProblemCode(reason),
			successCode
		};
	}
};

export const actions: Actions = {
	updateDisplayName: async ({ cookies, fetch, params, request }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const userId = userIdFromParams(params);
		const form = await request.formData();
		const displayName = textField(form, 'display_name');
		if (!displayName) return fail(400, { adminErrorCode: 'display_name_invalid' satisfies AdminProblemCode });
		const result = await adminApiMutationFetch<AdminUserDetail>(fetch, token, `/admin/users/${userId}`, 'PATCH', {
			display_name: displayName
		}, cookies);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'display_name_changed' };
	},
	enableUser: async ({ cookies, fetch, params }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const userId = userIdFromParams(params);
		const result = await adminApiMutationFetch<AdminUserDetail>(fetch, token, `/admin/users/${userId}/enable`, 'POST', undefined, cookies);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'user_enabled' };
	},
	disableUser: async ({ cookies, fetch, params, request }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const form = await request.formData();
		if (form.get('confirm_disable') !== 'on') {
			return fail(400, { adminErrorCode: 'self_disable_forbidden' satisfies AdminProblemCode });
		}
		const userId = userIdFromParams(params);
		const result = await adminApiMutationFetch<AdminUserDetail>(fetch, token, `/admin/users/${userId}/disable`, 'POST', undefined, cookies);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'user_disabled' };
	},
	resetPassword: async ({ cookies, fetch, params, request }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const form = await request.formData();
		const newPassword = secretField(form, 'new_password');
		if (!newPassword || form.get('confirm_reset') !== 'on') {
			return fail(400, { adminErrorCode: 'password_policy' satisfies AdminProblemCode });
		}
		const userId = userIdFromParams(params);
		const result = await adminApiMutationFetch<AdminPasswordResetResult>(
			fetch,
			token,
			`/admin/users/${userId}/password-reset`,
			'POST',
			{ new_password: newPassword },
			cookies
		);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		if (result.payload.session_invalidated && result.payload.subject_user_id === actor.id) {
			redirectToSessionChanged(cookies);
		}
		return { adminSuccessCode: 'password_reset' };
	},
	grantAccess: async ({ cookies, fetch, params, request }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const userId = userIdFromParams(params);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { adminErrorCode: 'book_not_assignable' satisfies AdminProblemCode });
		}
		const role = safeRole(form);
		const result = await adminApiMutationFetch<AdminBookAccess>(
			fetch,
			token,
			`/admin/users/${userId}/book-access/${bookId}`,
			'PUT',
			{ role },
			cookies
		);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'book_access_granted' };
	},
	revokeAccess: async ({ cookies, fetch, params, request }) => {
		const token = getAuthToken(cookies);
		const actor = await adminActor(fetch, token, cookies);
		if (!actor.isAdmin) return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		const userId = userIdFromParams(params);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0 || form.get('confirm_revoke') !== 'on') {
			return fail(400, { adminErrorCode: 'book_not_assignable' satisfies AdminProblemCode });
		}
		const result = await adminApiMutationFetch<null>(fetch, token, `/admin/users/${userId}/book-access/${bookId}`, 'DELETE', undefined, cookies);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'book_access_revoked' };
	}
};
