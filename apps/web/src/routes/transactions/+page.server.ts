import { env } from '$env/dynamic/private';
import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { Account, PaginatedTransactions } from '$lib/api/types';
import type { PageServerLoad } from './$types';

type TransactionFilters = {
	query: string;
	dateFrom: string;
	dateTo: string;
	accountId: string;
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

function buildTransactionFilterUrl(filters: TransactionFilters, dates: DatePresetDates): string {
	const sp = new URLSearchParams();
	if (filters.query) sp.set('query', filters.query);
	if (dates.dateFrom) sp.set('date_from', dates.dateFrom);
	if (dates.dateTo) sp.set('date_to', dates.dateTo);
	if (filters.accountId) sp.set('account_id', filters.accountId);
	if (filters.minAmount) sp.set('min_amount', filters.minAmount);
	if (filters.maxAmount) sp.set('max_amount', filters.maxAmount);
	if (filters.transactionState) sp.set('transaction_state', filters.transactionState);
	sp.set('limit', String(filters.limit));
	sp.set('offset', '0');
	return `/transactions?${sp.toString()}`;
}

function buildDatePresets(filters: TransactionFilters, now = new Date()) {
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
		href: buildTransactionFilterUrl(filters, preset.dates),
		active: filters.dateFrom === preset.dates.dateFrom && filters.dateTo === preset.dates.dateTo
	}));
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);

	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	const offset = positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER);
	const query = url.searchParams.get('query') ?? '';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const accountId = url.searchParams.get('account_id') ?? '';
	const minAmount = url.searchParams.get('min_amount') ?? '';
	const maxAmount = url.searchParams.get('max_amount') ?? '';
	const transactionState = url.searchParams.get('transaction_state') ?? '';
	const filters = { query, dateFrom, dateTo, accountId, minAmount, maxAmount, transactionState, limit };

	const transactionParams = new URLSearchParams({ limit: String(limit), offset: String(offset) });
	if (query) transactionParams.set('query', query);
	if (dateFrom) transactionParams.set('date_from', dateFrom);
	if (dateTo) transactionParams.set('date_to', dateTo);
	if (accountId) transactionParams.set('account_id', accountId);
	if (minAmount) transactionParams.set('min_amount', minAmount);
	if (maxAmount) transactionParams.set('max_amount', maxAmount);
	if (transactionState) transactionParams.set('transaction_state', transactionState);

	const [accounts, txs] = await Promise.all([
		apiFetch<Account[]>(fetch, `${bookPrefix}/accounts`, token),
		apiFetch<PaginatedTransactions>(fetch, `${bookPrefix}/transactions?${transactionParams.toString()}`, token)
	]);

	return {
		accounts,
		txs,
		activeBook,
		filters: { query, dateFrom, dateTo, accountId, minAmount, maxAmount, transactionState },
		datePresets: buildDatePresets(filters),
		writesEnabled: env.GNUCASH_WRITES_ENABLED === 'true'
	};
};
