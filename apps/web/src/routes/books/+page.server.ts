import { fail } from '@sveltejs/kit';
import { getActiveBookContext, getAuthToken, getCurrentUser, isCurrentUserAdmin } from '$lib/api/server';
import type { BookProblemCode } from '$lib/api/types';
import type { Actions, PageServerLoad } from './$types';

const BOOK_CONTEXT_NOTICE_KEYS = new Set([
	'invalid_selected_book_cookie',
	'stale_selected_book_cookie',
	'no_accessible_books',
	'unavailable_selected_book'
]);

const allowedBookProblemCodes = new Set<BookProblemCode>([
	'admin_required',
	'preflight_required',
	'preflight_rejected',
	'preflight_token_invalid',
	'invalid_path',
	'unsupported_source',
	'outside_allowed_roots',
	'symlink_forbidden',
	'missing_file',
	'not_regular_file',
	'permission_denied',
	'unsupported_format',
	'invalid_gnucash_schema',
	'source_changed',
	'open_failed',
	'duplicate_canonical_path',
	'api_unavailable',
	'book_registry_failed',
	'unknown_book_problem'
]);

function fixedBookProblemCode(payload: unknown, fallback: BookProblemCode): BookProblemCode {
	let candidate: unknown = null;
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		candidate = record.safe_code ?? record.code;
		if (!candidate && record.detail && typeof record.detail === 'object') {
			const detail = record.detail as Record<string, unknown>;
			candidate = detail.safe_code ?? detail.code;
		}
	}
	return typeof candidate === 'string' && allowedBookProblemCodes.has(candidate as BookProblemCode)
		? (candidate as BookProblemCode)
		: fallback;
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const [{ books, activeBook, recovery }, currentUser] = await Promise.all([
		getActiveBookContext(fetch, cookies, token),
		getCurrentUser(fetch, token)
	]);
	const queryNotice = url.searchParams.get('book_context');
	const bookContextNotice = BOOK_CONTEXT_NOTICE_KEYS.has(queryNotice ?? '')
		? queryNotice
		: recovery?.reason ?? null;

	return {
		books,
		activeBook,
		isAdmin: isCurrentUserAdmin(currentUser),
		bookContextNotice
	};
};

async function postBookManagementAction(
	fetch: typeof globalThis.fetch,
	token: string,
	path: string,
	method: 'POST' | 'DELETE'
): Promise<{ ok: true; payload: unknown } | { ok: false; status: number; message: BookProblemCode }> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	try {
		const response = await fetch(`${apiBase}${path}`, {
			method,
			headers: {
				authorization: `Bearer ${token}`
			}
		});
		if (!response.ok) {
			let payload: unknown = null;
			try {
				payload = await response.json();
			} catch {
				payload = null;
			}
			return {
				ok: false,
				status: response.status,
				message: fixedBookProblemCode(
					payload,
					response.status === 403 ? 'admin_required' : 'book_registry_failed'
				)
			};
		}
		return { ok: true, payload: await response.json() };
	} catch {
		return {
			ok: false,
			status: 502,
			message: 'api_unavailable'
		};
	}
}

export const actions: Actions = {
	setDefaultBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { manageErrorCode: 'book_registry_failed' });
		}
		const result = await postBookManagementAction(fetch, token, `/books/${bookId}/default`, 'POST');
		if (!result.ok) return fail(result.status, { manageErrorCode: result.message });
		return {
			manageSuccessCode: 'set_default'
		};
	},
	removeBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { manageErrorCode: 'book_registry_failed' });
		}
		if (form.get('confirm_metadata_only') !== 'on') {
			return fail(400, { manageErrorCode: 'preflight_required' });
		}
		const result = await postBookManagementAction(fetch, token, `/books/${bookId}`, 'DELETE');
		if (!result.ok) return fail(result.status, { manageErrorCode: result.message });
		cookies.delete('selected_book_id', { path: '/' });
		return {
			manageSuccessCode: 'remove_registry'
		};
	}
};
