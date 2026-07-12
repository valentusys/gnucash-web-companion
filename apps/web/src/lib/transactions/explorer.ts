import { compareDecimalStrings } from '$lib/money.js';

export const TRANSACTIONS_EXPLORER_DEFAULT_SORT = 'date_desc' as const;
export const TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE = 50;
export const TRANSACTIONS_EXPLORER_PAGE_SIZES = [25, 50, 100] as const;
export const TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE = 100;
export const TRANSACTIONS_EXPLORER_MAX_CURSOR_LENGTH = 1024;

export type TransactionExplorerSort = 'date_desc' | 'date_asc';
export type TransactionExplorerAccountType = 'income' | 'expense';
export type TransactionExplorerDirection = 'increase' | 'decrease';
export type TransactionExplorerState = 'unreconciled' | 'cleared' | 'reconciled' | 'voided';

export type TransactionExplorerUrlInput = {
	dateFrom?: string;
	dateTo?: string;
	accountIds?: string[];
	type?: TransactionExplorerAccountType | '';
	direction?: TransactionExplorerDirection | '';
	minAmount?: string;
	maxAmount?: string;
	query?: string;
	transactionState?: TransactionExplorerState | '';
	sort?: TransactionExplorerSort;
	pageSize?: number;
	cursor?: string;
};

export type TransactionExplorerValidatedInput = Required<
	Pick<TransactionExplorerUrlInput, 'sort'>
> & {
	dateFrom: string;
	dateTo: string;
	accountIds: string[];
	type: TransactionExplorerAccountType | '';
	direction: TransactionExplorerDirection | '';
	minAmount: string;
	maxAmount: string;
	query: string;
	transactionState: TransactionExplorerState | '';
	pageSize: number;
	cursor: string;
};

export type TransactionExplorerValidationResult =
	| { ok: true; value: TransactionExplorerValidatedInput; canonicalHref: string }
	| { ok: false; code: string; message: string; value: TransactionExplorerValidatedInput; canonicalHref: string };

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const GUID_RE = /^[0-9a-f]{32}$/;
const DECIMAL_RE = /^(0|[1-9][0-9]{0,17})(\.[0-9]{1,8})?$/;
const SORTS: TransactionExplorerSort[] = ['date_desc', 'date_asc'];
const TYPES: TransactionExplorerAccountType[] = ['income', 'expense'];
const DIRECTIONS: TransactionExplorerDirection[] = ['increase', 'decrease'];
const STATES: TransactionExplorerState[] = ['unreconciled', 'cleared', 'reconciled', 'voided'];

function firstParam(params: URLSearchParams, key: string): string {
	return (params.get(key) ?? '').trim();
}

export function normalizeAccountIds(values: string[]): string[] {
	return values.map((value) => value.trim().toLowerCase()).filter(Boolean);
}

function parsePageSize(raw: string): number {
	if (!raw) return TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE;
	const parsed = Number(raw);
	if (!Number.isInteger(parsed)) return NaN;
	return parsed;
}

function parseSort(raw: string): TransactionExplorerSort {
	return SORTS.includes(raw as TransactionExplorerSort)
		? (raw as TransactionExplorerSort)
		: TRANSACTIONS_EXPLORER_DEFAULT_SORT;
}

function validatedValueFromUrl(url: URL): TransactionExplorerValidatedInput {
	const params = url.searchParams;
	return {
		dateFrom: firstParam(params, 'date_from'),
		dateTo: firstParam(params, 'date_to'),
		accountIds: normalizeAccountIds(params.getAll('account_ids')),
		type: TYPES.includes(firstParam(params, 'type') as TransactionExplorerAccountType)
			? (firstParam(params, 'type') as TransactionExplorerAccountType)
			: '',
		direction: DIRECTIONS.includes(firstParam(params, 'direction') as TransactionExplorerDirection)
			? (firstParam(params, 'direction') as TransactionExplorerDirection)
			: '',
		minAmount: firstParam(params, 'min_amount'),
		maxAmount: firstParam(params, 'max_amount'),
		query: firstParam(params, 'query'),
		transactionState: STATES.includes(firstParam(params, 'transaction_state') as TransactionExplorerState)
			? (firstParam(params, 'transaction_state') as TransactionExplorerState)
			: '',
		sort: parseSort(firstParam(params, 'sort')),
		pageSize: parsePageSize(firstParam(params, 'page_size')),
		cursor: firstParam(params, 'cursor')
	};
}

function strictIsoDate(value: string): boolean {
	if (!ISO_DATE_RE.test(value)) return false;
	const date = new Date(`${value}T00:00:00Z`);
	return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

function nonNegativeDecimal(value: string): boolean {
	return DECIMAL_RE.test(value);
}

function daysInclusive(dateFrom: string, dateTo: string): number {
	const from = Date.parse(`${dateFrom}T00:00:00Z`);
	const to = Date.parse(`${dateTo}T00:00:00Z`);
	return Math.floor((to - from) / (24 * 60 * 60 * 1000)) + 1;
}

export function buildTransactionsExplorerSearchParams(input: TransactionExplorerUrlInput): URLSearchParams {
	const params = new URLSearchParams();
	const dateFrom = input.dateFrom?.trim() ?? '';
	const dateTo = input.dateTo?.trim() ?? '';
	if (dateFrom) params.append('date_from', dateFrom);
	if (dateTo) params.append('date_to', dateTo);
	for (const accountId of normalizeAccountIds(input.accountIds ?? []).sort()) {
		params.append('account_ids', accountId);
	}
	if (input.type) params.append('type', input.type);
	if (input.direction) params.append('direction', input.direction);
	if (input.minAmount?.trim()) params.append('min_amount', input.minAmount.trim());
	if (input.maxAmount?.trim()) params.append('max_amount', input.maxAmount.trim());
	if (input.query?.trim()) params.append('query', input.query.trim());
	if (input.transactionState) params.append('transaction_state', input.transactionState);
	params.append('sort', input.sort ?? TRANSACTIONS_EXPLORER_DEFAULT_SORT);
	params.append('page_size', String(input.pageSize ?? TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE));
	if (input.cursor?.trim()) params.append('cursor', input.cursor.trim());
	return params;
}

export function buildTransactionsExplorerUrl(input: TransactionExplorerUrlInput = {}): string {
	return `/transactions?${buildTransactionsExplorerSearchParams(input).toString()}`;
}

export function explorerValueToUrlInput(value: TransactionExplorerValidatedInput): TransactionExplorerUrlInput {
	return {
		dateFrom: value.dateFrom,
		dateTo: value.dateTo,
		accountIds: value.accountIds,
		type: value.type,
		direction: value.direction,
		minAmount: value.minAmount,
		maxAmount: value.maxAmount,
		query: value.query,
		transactionState: value.transactionState,
		sort: value.sort,
		pageSize: value.pageSize,
		cursor: value.cursor
	};
}

export function buildTransactionsExplorerUrlFromValue(
	value: TransactionExplorerValidatedInput,
	overrides: Partial<TransactionExplorerUrlInput> = {}
): string {
	return buildTransactionsExplorerUrl({ ...explorerValueToUrlInput(value), ...overrides });
}

export function stripTransactionsExplorerCursor(value: TransactionExplorerValidatedInput): TransactionExplorerUrlInput {
	return { ...explorerValueToUrlInput(value), cursor: '' };
}

export function isTransactionsExplorerResetHref(href: string): boolean {
	return href === buildTransactionsExplorerUrl();
}

export function validateTransactionsExplorerUrl(url: URL): TransactionExplorerValidationResult {
	const value = validatedValueFromUrl(url);
	const canonicalHref = buildTransactionsExplorerUrl(value);
	const rawParams = url.searchParams;
	const rawAccountIds = normalizeAccountIds(rawParams.getAll('account_ids'));
	const rawSort = firstParam(rawParams, 'sort');
	const rawType = firstParam(rawParams, 'type');
	const rawDirection = firstParam(rawParams, 'direction');
	const rawState = firstParam(rawParams, 'transaction_state');
	const hasAmount = Boolean(value.minAmount || value.maxAmount);

	function invalid(code: string, message: string): TransactionExplorerValidationResult {
		return { ok: false, code, message, value, canonicalHref };
	}

	if (rawParams.has('account_id')) {
		return invalid('legacy_account_id_mixed', 'Use account_ids for the canonical explorer; legacy account_id URLs are handled separately.');
	}
	if (rawAccountIds.length !== new Set(rawAccountIds).size) {
		return invalid('duplicate_account_ids', 'Duplicate account_ids are rejected before requesting the explorer API.');
	}
	if (rawAccountIds.length > 20) {
		return invalid('too_many_account_ids', 'Select at most 20 accounts for one explorer request.');
	}
	if (rawAccountIds.some((accountId) => !GUID_RE.test(accountId))) {
		return invalid('invalid_account_ids', 'account_ids must be lowercase 32-character GnuCash GUIDs.');
	}
	if (rawType && !TYPES.includes(rawType as TransactionExplorerAccountType)) {
		return invalid('invalid_type', 'Choose income or expense, or clear transaction type.');
	}
	if (rawDirection && !DIRECTIONS.includes(rawDirection as TransactionExplorerDirection)) {
		return invalid('invalid_direction', 'Choose increase or decrease, or clear direction.');
	}
	if (rawState && !STATES.includes(rawState as TransactionExplorerState)) {
		return invalid('invalid_transaction_state', 'Choose a supported reconciliation state, or clear state.');
	}
	if (rawSort && !SORTS.includes(rawSort as TransactionExplorerSort)) {
		return invalid('invalid_sort', 'Choose date_desc or date_asc sorting.');
	}
	if (!Number.isInteger(value.pageSize) || value.pageSize < 1 || value.pageSize > TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE) {
		return invalid('invalid_page_size', 'Choose a supported page_size from 1 to 100.');
	}
	if ((value.dateFrom && !strictIsoDate(value.dateFrom)) || (value.dateTo && !strictIsoDate(value.dateTo))) {
		return invalid('invalid_date', 'Enter date_from/date_to as YYYY-MM-DD dates.');
	}
	if (value.dateFrom && value.dateTo && value.dateFrom > value.dateTo) {
		return invalid('invalid_date_range', 'date_from must be on or before date_to.');
	}
	if (value.dateFrom && value.dateTo && daysInclusive(value.dateFrom, value.dateTo) > 366) {
		return invalid('date_range_too_wide', 'date_from/date_to may span at most 366 inclusive days.');
	}
	if (value.accountIds.length && value.type) {
		return invalid('account_type_conflict', 'Use either selected accounts or income/expense type mode, not both.');
	}
	if (value.direction && value.accountIds.length === 0) {
		return invalid('direction_requires_accounts', 'Direction requires one or more selected account_ids.');
	}
	if (value.minAmount && !nonNegativeDecimal(value.minAmount)) {
		return invalid('invalid_min_amount', 'min_amount must be a non-negative decimal string.');
	}
	if (value.maxAmount && !nonNegativeDecimal(value.maxAmount)) {
		return invalid('invalid_max_amount', 'max_amount must be a non-negative decimal string.');
	}
	if (value.minAmount && value.maxAmount && compareDecimalStrings(value.minAmount, value.maxAmount) > 0) {
		return invalid('invalid_amount_range', 'min_amount must be less than or equal to max_amount.');
	}
	if (hasAmount && value.accountIds.length === 0 && !value.type) {
		return invalid('amount_requires_scope', 'Amount filters require selected account_ids or income/expense type mode so the matched amount is exact.');
	}
	if (value.query.length > 120) {
		return invalid('query_too_long', 'Search text is limited to 120 characters.');
	}
	if (value.cursor.length > TRANSACTIONS_EXPLORER_MAX_CURSOR_LENGTH) {
		return invalid('cursor_too_long', 'Cursor is too long or stale. Reset pagination and retry.');
	}
	return { ok: true, value, canonicalHref };
}

export function safeTransactionsReturnTo(value: string | null | undefined): string {
	if (!value || value.length > 2048) return '/transactions';
	try {
		const parsed = new URL(value, 'http://127.0.0.1');
		if (parsed.origin !== 'http://127.0.0.1') return '/transactions';
		if (parsed.pathname !== '/transactions') return '/transactions';
		return `${parsed.pathname}${parsed.search}` || '/transactions';
	} catch {
		return '/transactions';
	}
}

export function detailHrefWithReturnTo(transactionId: string, returnTo: string): string {
	const safeReturnTo = safeTransactionsReturnTo(returnTo);
	return `/transactions/${encodeURIComponent(transactionId)}?return_to=${encodeURIComponent(safeReturnTo)}`;
}
