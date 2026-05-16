import { apiFetch, getAuthToken } from '$lib/api/server';
import type { AccountTreeNode, Book } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const [books, accounts] = await Promise.all([
		apiFetch<Book[]>(fetch, '/books', token),
		apiFetch<AccountTreeNode[]>(fetch, '/accounts/tree', token)
	]);

	return {
		books,
		accounts,
		showBookSelector: books.length > 1,
		activeBook: books.find((book) => book.is_default) ?? books[0] ?? null
	};
};
