import { apiFetch, getAuthToken } from '$lib/api/server';
import type { Account, Book } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch, params }) => {
	const token = getAuthToken(cookies);
	const [books, account] = await Promise.all([
		apiFetch<Book[]>(fetch, '/books', token),
		apiFetch<Account>(fetch, `/accounts/${encodeURIComponent(params.id)}`, token)
	]);

	return {
		books,
		account,
		showBookSelector: books.length > 1,
		activeBook: books.find((book) => book.is_default) ?? books[0] ?? null
	};
};
