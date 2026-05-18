import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { Account, PaginatedTransactions } from '$lib/api/types';
import type { PageServerLoad } from './$types';

type AccountTransactionFilters = {
	query: string;
	dateFrom: string;
	dateTo: string;
	minAmount: string;
	maxAmount: string;
	transactionState: string;
	limit: number;
};

type DatePresetDates = {
	dateFrom: string;
	dateTo: string;
};

function positiveInt(value: string | null, fallback: number, max: number): number {
	const parsed = Number(value ?? fallback);
	if (!Number.isFinite(parsed) || parsed < 0) return fallback;
	return Math.min(Math.floor(parsed), max);
}

function formatDate(date: Date): string {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, '0');
	const day = String(date.getDate()).padStart(2, '0');
	return `${year}-${month}-${day}`;
}

function appendAccountTransactionFilters(sp: URLSearchParams, filters: AccountTransactionFilters) {
	if (filters.query) sp.set('query', filters.query);
	if (filters.dateFrom) sp.set('date_from', filters.dateFrom);
	if (filters.dateTo) sp.set('date_to', filters.dateTo);
	if (filters.minAmount) sp.set('min_amount', filters.minAmount);
	if (filters.maxAmount) sp.set('max_amount', filters.maxAmount);
	if (filters.transactionState) sp.set('transaction_state', filters.transactionState);
}

function buildAccountFilterUrl(accountId: string, filters: AccountTransactionFilters, dates: DatePresetDates): string {
	const sp = new URLSearchParams();
	appendAccountTransactionFilters(sp, { ...filters, dateFrom: dates.dateFrom, dateTo: dates.dateTo });
	sp.set('limit', String(filters.limit));
	sp.set('offset', '0');
	return `/accounts/${encodeURIComponent(accountId)}?${sp.toString()}`;
}

function buildClearFiltersUrl(accountId: string, limit: number): string {
	const sp = new URLSearchParams({ limit: String(limit), offset: '0' });
	return `/accounts/${encodeURIComponent(accountId)}?${sp.toString()}`;
}

function buildDatePresets(accountId: string, filters: AccountTransactionFilters, now = new Date()) {
	const year = now.getFullYear();
	const month = now.getMonth();
	const thisMonth = {
		dateFrom: formatDate(new Date(year, month, 1)),
		dateTo: formatDate(now)
	};
	const lastMonth = {
		dateFrom: formatDate(new Date(year, month - 1, 1)),
		dateTo: formatDate(new Date(year, month, 0))
	};
	const yearToDate = {
		dateFrom: formatDate(new Date(year, 0, 1)),
		dateTo: formatDate(now)
	};
	const clearDates = { dateFrom: '', dateTo: '' };

	return [
		{ label: 'This month', dates: thisMonth },
		{ label: 'Last month', dates: lastMonth },
		{ label: 'Year to date', dates: yearToDate },
		{ label: 'Clear dates', dates: clearDates }
	].map((preset) => ({
		label: preset.label,
		href: buildAccountFilterUrl(accountId, filters, preset.dates),
		active: filters.dateFrom === preset.dates.dateFrom && filters.dateTo === preset.dates.dateTo
	}));
}

export const load: PageServerLoad = async ({ cookies, fetch, params, url }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);

	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	const offset = positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER);
	const accountId = encodeURIComponent(params.id);
	const query = url.searchParams.get('query') ?? '';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const minAmount = url.searchParams.get('min_amount') ?? '';
	const maxAmount = url.searchParams.get('max_amount') ?? '';
	const transactionState = url.searchParams.get('transaction_state') ?? '';
	const filters = { query, dateFrom, dateTo, minAmount, maxAmount, transactionState, limit };

	const transactionParams = new URLSearchParams({ limit: String(limit), offset: String(offset) });
	appendAccountTransactionFilters(transactionParams, filters);

	const [account, txs] = await Promise.all([
		apiFetch<Account>(fetch, `${bookPrefix}/accounts/${accountId}`, token),
		apiFetch<PaginatedTransactions>(
			fetch,
			`${bookPrefix}/accounts/${accountId}/transactions?${transactionParams.toString()}`,
			token
		)
	]);

	return {
		account,
		txs,
		activeBook,
		filters: { query, dateFrom, dateTo, minAmount, maxAmount, transactionState },
		datePresets: buildDatePresets(params.id, filters),
		clearFiltersHref: buildClearFiltersUrl(params.id, limit)
	};
};
