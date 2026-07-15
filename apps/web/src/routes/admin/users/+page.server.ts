import { fail, isHttpError, isRedirect } from '@sveltejs/kit';
import {
	adminApiMutationFetch,
	apiFetch,
	getAuthToken,
	getCurrentUser,
	isCurrentUserAdmin
} from '$lib/api/server';
import type { AdminProblemCode, AdminUserList, AdminUserStateFilter } from '$lib/api/types';
import type { Actions, PageServerLoad } from './$types';

const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 100;
const MAX_OFFSET = 100_000;
const STATE_FILTERS = new Set<AdminUserStateFilter>(['all', 'enabled', 'disabled']);
const SUCCESS_CODES = new Set([
	'user_created',
	'display_name_changed',
	'user_enabled',
	'user_disabled',
	'password_reset',
	'book_access_granted',
	'book_access_revoked'
]);

function emptyUsers(limit: number, offset: number): AdminUserList {
	return {
		items: [],
		total_count: 0,
		limit,
		offset,
		has_next: false
	};
}

function safeIntegerParam(params: URLSearchParams, name: string, fallback: number, min: number, max: number): number {
	const raw = params.get(name);
	if (!raw) return fallback;
	const value = Number(raw);
	if (!Number.isInteger(value) || value < min || value > max) return fallback;
	return value;
}

function safeStateParam(params: URLSearchParams): AdminUserStateFilter {
	const candidate = params.get('state');
	return STATE_FILTERS.has(candidate as AdminUserStateFilter) ? (candidate as AdminUserStateFilter) : 'all';
}

function safeAdminSuccess(params: URLSearchParams): string | null {
	const candidate = params.get('admin_success');
	return candidate && SUCCESS_CODES.has(candidate) ? candidate : null;
}

function loadProblemCode(reason: unknown): AdminProblemCode {
	if (isHttpError(reason)) {
		if (reason.status === 401) return 'session_changed';
		if (reason.status === 403) return 'admin_required';
	}
	return 'api_unavailable';
}

export const load: PageServerLoad = async ({ cookies, fetch, parent, url }) => {
	const token = getAuthToken(cookies);
	const layoutData = await parent();
	const currentUser = layoutData.currentUser;
	const limit = safeIntegerParam(url.searchParams, 'limit', DEFAULT_LIMIT, 1, MAX_LIMIT);
	const offset = safeIntegerParam(url.searchParams, 'offset', 0, 0, MAX_OFFSET);
	const state = safeStateParam(url.searchParams);
	const users = emptyUsers(limit, offset);
	const successCode = safeAdminSuccess(url.searchParams);

	if (!isCurrentUserAdmin(currentUser)) {
		return {
			isAdmin: false,
			users,
			filters: { limit, offset, state },
			loadErrorCode: null,
			successCode
		};
	}

	const params = new URLSearchParams({ limit: String(limit), offset: String(offset), state });
	try {
		return {
			isAdmin: true,
			users: await apiFetch<AdminUserList>(fetch, `/admin/users?${params.toString()}`, token, cookies),
			filters: { limit, offset, state },
			loadErrorCode: null,
			successCode
		};
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		return {
			isAdmin: true,
			users,
			filters: { limit, offset, state },
			loadErrorCode: loadProblemCode(reason),
			successCode
		};
	}
};

export const actions: Actions = {
	enableUser: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const currentUser = await getCurrentUser(fetch, token, cookies);
		if (!isCurrentUserAdmin(currentUser)) {
			return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		}
		const form = await request.formData();
		const userId = Number(form.get('user_id'));
		if (!Number.isInteger(userId) || userId <= 0) {
			return fail(404, { adminErrorCode: 'user_not_found' satisfies AdminProblemCode });
		}
		const result = await adminApiMutationFetch(fetch, token, `/admin/users/${userId}/enable`, 'POST', undefined, cookies);
		if (!result.ok) return fail(result.status, { adminErrorCode: result.message });
		return { adminSuccessCode: 'user_enabled' };
	}
};
