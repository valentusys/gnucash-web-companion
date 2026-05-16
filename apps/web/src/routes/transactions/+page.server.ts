import { apiFetch, getAuthToken } from '$lib/api/server';
import type { Account, Book, PaginatedTransactions } from '$lib/api/types';
import type { PageServerLoad } from './$types';

function positiveInt(value: string | null, fallback: number, max: number): number {
	const parsed = Number(value ?? fallback);
	if (!Number.isFinite(parsed) || parsed < 0) return fallback;
	return Math.min(Math.floor(parsed), max);
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	const offset = positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER);
	const query = url.searchParams.get('query') ?? '';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const accountId = url.searchParams.get('account_id') ?? '';

	const transactionParams = new URLSearchParams({ limit: String(limit), offset: String(offset) });
	if (query) transactionParams.set('query', query);
	if (dateFrom) transactionParams.set('date_from', dateFrom);
	if (dateTo) transactionParams.set('date_to', dateTo);
	if (accountId) transactionParams.set('account_id', accountId);

	const [books, accounts, txs] = await Promise.all([
		apiFetch<Book[]>(fetch, '/books', token),
		apiFetch<Account[]>(fetch, '/accounts', token),
		apiFetch<PaginatedTransactions>(fetch, `/transactions?${transactionParams.toString()}`, token)
	]);

	return {
		books,
		accounts,
		txs,
		filters: { query, dateFrom, dateTo, accountId },
		showBookSelector: books.length > 1,
		activeBook: books.find((book) => book.is_default) ?? books[0] ?? null
	};
};
