import { fail } from '@sveltejs/kit';
import {
	apiMutationFetch,
	clearSelectedBookCookieIfMatches,
	getActiveBookContext,
	getAuthToken,
	getCurrentUser,
	isCurrentUserAdmin
} from '$lib/api/server';
import type { Actions, PageServerLoad } from './$types';

const BOOK_CONTEXT_NOTICE_KEYS = new Set([
	'invalid_selected_book_cookie',
	'stale_selected_book_cookie',
	'no_accessible_books',
	'unavailable_selected_book'
]);

const MANAGE_SUCCESS_NOTICE_KEYS = new Set(['set_default', 'remove_registry']);

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
	const queryManageSuccess = url.searchParams.get('manage_success');
	const manageSuccessNotice = MANAGE_SUCCESS_NOTICE_KEYS.has(queryManageSuccess ?? '')
		? queryManageSuccess
		: null;

	return {
		books,
		activeBook,
		isAdmin: isCurrentUserAdmin(currentUser),
		bookContextNotice,
		manageSuccessNotice
	};
};

export const actions: Actions = {
	setDefaultBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { manageErrorCode: 'book_registry_failed' });
		}
		const result = await apiMutationFetch(fetch, token, `/books/${bookId}/default`, 'POST');
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
		const result = await apiMutationFetch(fetch, token, `/books/${bookId}`, 'DELETE');
		if (!result.ok) return fail(result.status, { manageErrorCode: result.message });
		clearSelectedBookCookieIfMatches(cookies, bookId);
		return {
			manageSuccessCode: 'remove_registry'
		};
	}
};
