export const ACCOUNT_EXPLORER_DEFAULT_MODE = 'tree' as const;
export const ACCOUNT_EXPLORER_DEFAULT_HIDDEN = 'exclude' as const;
export const ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER = 'include' as const;
export const ACCOUNT_EXPLORER_MAX_QUERY_LENGTH = 120;
export const ACCOUNT_EXPLORER_MAX_TYPE_FILTERS = 20;
export const ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT = 10;
export const ACCOUNT_DETAIL_MAX_ACTIVITY_LIMIT = 20;
export const ACCOUNT_ACTIVITY_MAX_DAYS = 366;

export type AccountExplorerMode = 'tree' | 'flat';
export type AccountVisibility = 'exclude' | 'include' | 'only';

export type AccountExplorerUrlInput = {
	mode?: AccountExplorerMode;
	query?: string;
	types?: string[];
	hidden?: AccountVisibility;
	placeholder?: AccountVisibility;
};

export type AccountExplorerValidatedInput = {
	mode: AccountExplorerMode;
	query: string;
	types: string[];
	hidden: AccountVisibility;
	placeholder: AccountVisibility;
};

export type AccountExplorerValidationResult =
	| { ok: true; value: AccountExplorerValidatedInput; canonicalHref: string }
	| { ok: false; code: string; message: string; value: AccountExplorerValidatedInput; canonicalHref: string };

export type AccountDetailUrlInput = {
	dateFrom?: string;
	dateTo?: string;
	limit?: number;
	returnTo?: string;
};

export type AccountDetailValidatedInput = {
	accountId: string;
	dateFrom: string;
	dateTo: string;
	limit: number;
	returnTo: string;
	legacyKeys: string[];
};

export type AccountDetailValidationResult =
	| { ok: true; value: AccountDetailValidatedInput; canonicalHref: string }
	| { ok: false; code: string; message: string; value: AccountDetailValidatedInput; canonicalHref: string };

const GUID_RE = /^[0-9a-f]{32}$/;
const ACCOUNT_TYPE_RE = /^[A-Z][A-Z0-9_]{0,31}$/;
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const EXPLORER_KEYS = new Set(['mode', 'query', 'type', 'hidden', 'placeholder']);
const DETAIL_KEYS = new Set(['date_from', 'date_to', 'limit', 'return_to']);
const DETAIL_LEGACY_KEYS = new Set(['query', 'min_amount', 'max_amount', 'transaction_state', 'offset', 'account_id']);
const MODES: AccountExplorerMode[] = ['tree', 'flat'];
const VISIBILITY_MODES: AccountVisibility[] = ['exclude', 'include', 'only'];

function firstParam(params: URLSearchParams, key: string): string {
	return (params.get(key) ?? '').trim();
}

function invalidExplorer(
	code: string,
	message: string,
	value: AccountExplorerValidatedInput,
	canonicalHref = buildAccountExplorerUrl(value)
): AccountExplorerValidationResult {
	return { ok: false, code, message, value, canonicalHref };
}

function invalidDetail(
	code: string,
	message: string,
	value: AccountDetailValidatedInput,
	canonicalHref = buildAccountDetailUrl(value.accountId, value)
): AccountDetailValidationResult {
	return { ok: false, code, message, value, canonicalHref };
}

function normalizeType(value: string): string {
	return value.trim().toUpperCase();
}

function normalizeTypes(values: string[]): string[] {
	return values.map(normalizeType).filter(Boolean).sort();
}

function parseExplorerValue(url: URL): AccountExplorerValidatedInput {
	const modeRaw = firstParam(url.searchParams, 'mode').toLowerCase();
	const hiddenRaw = firstParam(url.searchParams, 'hidden').toLowerCase();
	const placeholderRaw = firstParam(url.searchParams, 'placeholder').toLowerCase();
	return {
		mode: MODES.includes(modeRaw as AccountExplorerMode) ? (modeRaw as AccountExplorerMode) : ACCOUNT_EXPLORER_DEFAULT_MODE,
		query: firstParam(url.searchParams, 'query'),
		types: normalizeTypes(url.searchParams.getAll('type')),
		hidden: VISIBILITY_MODES.includes(hiddenRaw as AccountVisibility) ? (hiddenRaw as AccountVisibility) : ACCOUNT_EXPLORER_DEFAULT_HIDDEN,
		placeholder: VISIBILITY_MODES.includes(placeholderRaw as AccountVisibility)
			? (placeholderRaw as AccountVisibility)
			: ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER
	};
}

export function buildAccountExplorerSearchParams(input: AccountExplorerUrlInput = {}): URLSearchParams {
	const params = new URLSearchParams();
	const mode = input.mode ?? ACCOUNT_EXPLORER_DEFAULT_MODE;
	const query = input.query?.trim() ?? '';
	const types = normalizeTypes(input.types ?? []);
	const hidden = input.hidden ?? ACCOUNT_EXPLORER_DEFAULT_HIDDEN;
	const placeholder = input.placeholder ?? ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER;
	if (mode === 'flat') params.append('mode', mode);
	if (query) params.append('query', query);
	for (const type of types) params.append('type', type);
	if (hidden !== ACCOUNT_EXPLORER_DEFAULT_HIDDEN) params.append('hidden', hidden);
	if (placeholder !== ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER) params.append('placeholder', placeholder);
	return params;
}

export function buildAccountExplorerUrl(input: AccountExplorerUrlInput = {}): string {
	const params = buildAccountExplorerSearchParams(input);
	const query = params.toString();
	return query ? `/accounts?${query}` : '/accounts';
}

export function validateAccountExplorerUrl(url: URL): AccountExplorerValidationResult {
	const value = parseExplorerValue(url);
	const canonicalHref = buildAccountExplorerUrl(value);
	const rawParams = url.searchParams;
	const unknownKeys = Array.from(rawParams.keys()).filter((key) => !EXPLORER_KEYS.has(key));
	const rawMode = firstParam(rawParams, 'mode').toLowerCase();
	const rawHidden = firstParam(rawParams, 'hidden').toLowerCase();
	const rawPlaceholder = firstParam(rawParams, 'placeholder').toLowerCase();
	const rawTypes = rawParams.getAll('type').map(normalizeType).filter(Boolean);

	if (unknownKeys.length) {
		return invalidExplorer('unsupported_account_explorer_param', 'Unsupported account explorer URL parameter. Reset filters and use the visible controls.', value, canonicalHref);
	}
	if (rawParams.getAll('mode').length > 1 || (rawMode && !MODES.includes(rawMode as AccountExplorerMode))) {
		return invalidExplorer('invalid_mode', 'mode must be tree or flat.', value, canonicalHref);
	}
	if (value.query.length > ACCOUNT_EXPLORER_MAX_QUERY_LENGTH) {
		return invalidExplorer('invalid_query', 'query must be at most 120 Unicode code points after trimming.', value, canonicalHref);
	}
	if (rawTypes.length !== new Set(rawTypes).size) {
		return invalidExplorer('duplicate_type', 'type filters must be unique after normalization.', value, canonicalHref);
	}
	if (rawTypes.length > ACCOUNT_EXPLORER_MAX_TYPE_FILTERS) {
		return invalidExplorer('too_many_types', 'type accepts at most 20 unique values.', value, canonicalHref);
	}
	if (rawTypes.some((type) => !ACCOUNT_TYPE_RE.test(type))) {
		return invalidExplorer('invalid_type', 'type filters must match [A-Z][A-Z0-9_]{0,31}.', value, canonicalHref);
	}
	if (rawParams.getAll('hidden').length > 1 || (rawHidden && !VISIBILITY_MODES.includes(rawHidden as AccountVisibility))) {
		return invalidExplorer('invalid_hidden', 'hidden must be exclude, include, or only.', value, canonicalHref);
	}
	if (
		rawParams.getAll('placeholder').length > 1 ||
		(rawPlaceholder && !VISIBILITY_MODES.includes(rawPlaceholder as AccountVisibility))
	) {
		return invalidExplorer('invalid_placeholder', 'placeholder must be exclude, include, or only.', value, canonicalHref);
	}
	return { ok: true, value, canonicalHref };
}

function strictIsoDate(value: string): boolean {
	if (!ISO_DATE_RE.test(value)) return false;
	const date = new Date(`${value}T00:00:00Z`);
	return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

function inclusiveDays(dateFrom: string, dateTo: string): number {
	const from = Date.parse(`${dateFrom}T00:00:00Z`);
	const to = Date.parse(`${dateTo}T00:00:00Z`);
	return Math.floor((to - from) / (24 * 60 * 60 * 1000)) + 1;
}

function parseAccountLimit(value: string): number {
	if (!value) return ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT;
	const parsed = Number(value);
	return Number.isInteger(parsed) ? parsed : NaN;
}

function parseDetailValue(url: URL, rawAccountId: string): AccountDetailValidatedInput {
	const accountId = rawAccountId.trim().toLowerCase();
	const params = url.searchParams;
	return {
		accountId,
		dateFrom: firstParam(params, 'date_from'),
		dateTo: firstParam(params, 'date_to'),
		limit: parseAccountLimit(firstParam(params, 'limit')),
		returnTo: safeAccountExplorerReturnTo(params.get('return_to')),
		legacyKeys: Array.from(new Set(Array.from(params.keys()).filter((key) => DETAIL_LEGACY_KEYS.has(key)))).sort()
	};
}

export function buildAccountDetailSearchParams(input: AccountDetailUrlInput = {}): URLSearchParams {
	const params = new URLSearchParams();
	const dateFrom = input.dateFrom?.trim() ?? '';
	const dateTo = input.dateTo?.trim() ?? '';
	const limit = input.limit ?? ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT;
	const returnTo = safeAccountExplorerReturnTo(input.returnTo);
	if (dateFrom && dateTo) {
		params.append('date_from', dateFrom);
		params.append('date_to', dateTo);
	}
	if (limit !== ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT) params.append('limit', String(limit));
	if (returnTo !== '/accounts') params.append('return_to', returnTo);
	return params;
}

export function buildAccountDetailUrl(accountId: string, input: AccountDetailUrlInput = {}): string {
	const normalizedAccountId = accountId.trim().toLowerCase();
	const params = buildAccountDetailSearchParams(input);
	const query = params.toString();
	return `/accounts/${encodeURIComponent(normalizedAccountId)}${query ? `?${query}` : ''}`;
}

export function validateAccountDetailUrl(url: URL, rawAccountId: string): AccountDetailValidationResult {
	const value = parseDetailValue(url, rawAccountId);
	const canonicalHref = buildAccountDetailUrl(value.accountId, value);
	const params = url.searchParams;
	const unknownKeys = Array.from(params.keys()).filter((key) => !DETAIL_KEYS.has(key) && !DETAIL_LEGACY_KEYS.has(key));
	const hasDateFrom = params.has('date_from');
	const hasDateTo = params.has('date_to');

	if (!GUID_RE.test(value.accountId)) {
		return invalidDetail('invalid_account_id', 'Account id must be a lowercase 32-character GnuCash GUID.', value, canonicalHref);
	}
	if (unknownKeys.length) {
		return invalidDetail('unsupported_account_detail_param', 'Unsupported account detail URL parameter. Reset account activity filters.', value, canonicalHref);
	}
	if (params.getAll('date_from').length > 1 || params.getAll('date_to').length > 1 || hasDateFrom !== hasDateTo) {
		return invalidDetail('date_pair_required', 'date_from and date_to are required together.', value, canonicalHref);
	}
	if ((value.dateFrom && !strictIsoDate(value.dateFrom)) || (value.dateTo && !strictIsoDate(value.dateTo))) {
		return invalidDetail('invalid_date', 'Enter date_from/date_to as YYYY-MM-DD dates.', value, canonicalHref);
	}
	if (value.dateFrom && value.dateTo && value.dateFrom > value.dateTo) {
		return invalidDetail('invalid_date_range', 'date_from must be on or before date_to.', value, canonicalHref);
	}
	if (value.dateFrom && value.dateTo && inclusiveDays(value.dateFrom, value.dateTo) > ACCOUNT_ACTIVITY_MAX_DAYS) {
		return invalidDetail('date_range_too_wide', 'date_from/date_to may span at most 366 inclusive days.', value, canonicalHref);
	}
	if (params.getAll('limit').length > 1 || !Number.isInteger(value.limit) || value.limit < 1 || value.limit > ACCOUNT_DETAIL_MAX_ACTIVITY_LIMIT) {
		return invalidDetail('invalid_limit', 'limit must be an integer from 1 to 20.', value, canonicalHref);
	}
	if (
		params.getAll('return_to').length > 1 ||
		(params.has('return_to') && !isSafeAccountExplorerReturnTo(params.get('return_to') ?? ''))
	) {
		return invalidDetail('invalid_return_to', 'return_to must be one safe account explorer URL.', value, canonicalHref);
	}
	return { ok: true, value, canonicalHref };
}

export function hasAccountActivityDateRange(value: AccountDetailValidatedInput): boolean {
	return Boolean(value.dateFrom && value.dateTo);
}

function isSafeAccountExplorerReturnTo(value: string | null | undefined): boolean {
	if (!value || value.length > 2048 || !value.startsWith('/') || value.startsWith('//')) return false;
	try {
		const parsed = new URL(value, 'http://127.0.0.1');
		if (parsed.origin !== 'http://127.0.0.1' || parsed.hash || parsed.pathname !== '/accounts') return false;
		return validateAccountExplorerUrl(parsed).ok;
	} catch {
		return false;
	}
}

export function safeAccountExplorerReturnTo(value: string | null | undefined): string {
	if (!isSafeAccountExplorerReturnTo(value)) return '/accounts';
	try {
		const parsed = new URL(value as string, 'http://127.0.0.1');
		const validation = validateAccountExplorerUrl(parsed);
		return validation.canonicalHref;
	} catch {
		return '/accounts';
	}
}

export function safeAccountDetailReturnTo(value: string | null | undefined, fallback = '/transactions'): string {
	if (!value || value.length > 2048 || !value.startsWith('/') || value.startsWith('//')) return fallback;
	try {
		const parsed = new URL(value, 'http://127.0.0.1');
		if (parsed.origin !== 'http://127.0.0.1' || parsed.hash) return fallback;
		const match = /^\/accounts\/([0-9a-f]{32})$/.exec(parsed.pathname);
		if (!match) return fallback;
		const validation = validateAccountDetailUrl(parsed, match[1]);
		return validation.ok ? validation.canonicalHref : fallback;
	} catch {
		return fallback;
	}
}

export function buildAccountTransactionExplorerUrl(accountId: string, dateFrom: string, dateTo: string): string {
	const params = new URLSearchParams();
	params.append('date_from', dateFrom);
	params.append('date_to', dateTo);
	params.append('account_ids', accountId.trim().toLowerCase());
	params.append('sort', 'date_desc');
	params.append('page_size', '50');
	return `/transactions?${params.toString()}`;
}

function addDays(value: string, days: number): string {
	return new Date(Date.parse(`${value}T00:00:00Z`) + days * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
}

export function buildBaseReportUrl(dateFrom: string, dateTo: string): string {
	const days = inclusiveDays(dateFrom, dateTo);
	const comparisonDateFrom = addDays(dateFrom, -days);
	const comparisonDateTo = addDays(dateFrom, -1);
	const params = new URLSearchParams();
	params.append('preset', 'custom');
	params.append('date_from', dateFrom);
	params.append('date_to', dateTo);
	params.append('comparison_mode', 'previous_equivalent');
	params.append('comparison_date_from', comparisonDateFrom);
	params.append('comparison_date_to', comparisonDateTo);
	return `/reports?${params.toString()}`;
}
