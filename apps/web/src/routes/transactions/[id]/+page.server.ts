import { apiFetch, getAuthToken } from '$lib/api/server';
import type { Book, TransactionDetail } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch, params }) => {
	const token = getAuthToken(cookies);
	const [books, transaction] = await Promise.all([
		apiFetch<Book[]>(fetch, '/books', token),
		apiFetch<TransactionDetail>(
			fetch,
			`/transactions/${encodeURIComponent(params.id)}`,
			token
		)
	]);

	return {
		books,
		transaction,
		showBookSelector: books.length > 1,
		activeBook: books.find((book) => book.is_default) ?? books[0] ?? null
	};
};
