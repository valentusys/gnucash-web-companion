import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { PageServerLoad } from './$types';

const BOOK_CONTEXT_NOTICE_KEYS = new Set([
	'invalid_selected_book_cookie',
	'stale_selected_book_cookie',
	'no_accessible_books',
	'unavailable_selected_book'
]);

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, recovery } = await getActiveBookContext(fetch, cookies, token);
	const queryNotice = url.searchParams.get('book_context');
	const bookContextNotice = BOOK_CONTEXT_NOTICE_KEYS.has(queryNotice ?? '')
		? queryNotice
		: recovery?.reason ?? null;

	return {
		books,
		activeBook,
		bookContextNotice
	};
};
