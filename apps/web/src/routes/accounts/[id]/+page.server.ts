import { apiFetch, getAuthToken, getActiveBookId } from '$lib/api/server';
import type { Account, PaginatedTransactions } from '$lib/api/types';
import type { PageServerLoad } from './$types';

function positiveInt(value: string | null, fallback: number, max: number): number {
	const parsed = Number(value ?? fallback);
	if (!Number.isFinite(parsed) || parsed < 0) return fallback;
	return Math.min(Math.floor(parsed), max);
}

export const load: PageServerLoad = async ({ cookies, fetch, params, url }) => {
	const token = getAuthToken(cookies);
	const activeBookId = getActiveBookId(cookies);
	const bookPrefix = activeBookId ? `/books/${activeBookId}` : '';

	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	const offset = positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER);
	const accountId = encodeURIComponent(params.id);

	const [account, txs] = await Promise.all([
		apiFetch<Account>(fetch, `${bookPrefix}/accounts/${accountId}`, token),
		apiFetch<PaginatedTransactions>(
			fetch,
			`${bookPrefix}/accounts/${accountId}/transactions?limit=${limit}&offset=${offset}`,
			token
		)
	]);

	return { account, txs };
};
