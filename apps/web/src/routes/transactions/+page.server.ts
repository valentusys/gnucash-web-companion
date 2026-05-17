import { env } from '$env/dynamic/private';
import { apiFetch, getAuthToken, getActiveBookId } from '$lib/api/server';
import type { Account, PaginatedTransactions } from '$lib/api/types';
import type { PageServerLoad } from './$types';

function positiveInt(value: string | null, fallback: number, max: number): number {
	const parsed = Number(value ?? fallback);
	if (!Number.isFinite(parsed) || parsed < 0) return fallback;
	return Math.min(Math.floor(parsed), max);
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const activeBookId = getActiveBookId(cookies);
	const bookPrefix = activeBookId ? `/books/${activeBookId}` : '';

	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	const offset = positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER);
	const query = url.searchParams.get('query') ?? '';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const accountId = url.searchParams.get('account_id') ?? '';
	const minAmount = url.searchParams.get('min_amount') ?? '';
	const maxAmount = url.searchParams.get('max_amount') ?? '';

	const transactionParams = new URLSearchParams({ limit: String(limit), offset: String(offset) });
	if (query) transactionParams.set('query', query);
	if (dateFrom) transactionParams.set('date_from', dateFrom);
	if (dateTo) transactionParams.set('date_to', dateTo);
	if (accountId) transactionParams.set('account_id', accountId);
	if (minAmount) transactionParams.set('min_amount', minAmount);
	if (maxAmount) transactionParams.set('max_amount', maxAmount);

	const [accounts, txs] = await Promise.all([
		apiFetch<Account[]>(fetch, `${bookPrefix}/accounts`, token),
		apiFetch<PaginatedTransactions>(fetch, `${bookPrefix}/transactions?${transactionParams.toString()}`, token)
	]);

	return {
		accounts,
		txs,
		filters: { query, dateFrom, dateTo, accountId, minAmount, maxAmount },
		writesEnabled: env.GNUCASH_WRITES_ENABLED === 'true'
	};
};
