import { getActiveBookId, getAuthToken, apiFetch } from '$lib/api/server';
import type { Book } from '$lib/api/types';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const books = await apiFetch<Book[]>(fetch, '/books', token);
	const selectedBookId = getActiveBookId(cookies);
	const activeBook =
		books.find((b) => b.id === selectedBookId) ??
		books.find((b) => b.is_default) ??
		books[0] ??
		null;

	return {
		authenticated: true,
		pathname: url.pathname,
		books,
		activeBook,
		showBookSelector: books.length > 1
	};
};
