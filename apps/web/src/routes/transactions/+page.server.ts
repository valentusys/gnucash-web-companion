import { env } from '$env/dynamic/private';
import { redirect } from '@sveltejs/kit';
import { loadAccountOptions } from '$lib/accounts/options.server';
import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import { getReportingDate } from '$lib/server/reporting-date';
import type { AccountOption, PaginatedTransactions, TransactionExplorerPage, TransactionListItem } from '$lib/api/types';
import {
	TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE,
	TRANSACTIONS_EXPLORER_DEFAULT_SORT,
	TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE,
	TRANSACTIONS_EXPLORER_PAGE_SIZES,
	buildTransactionsExplorerSearchParams,
	buildTransactionsExplorerUrl,
	buildTransactionsExplorerUrlFromValue,
	detailHrefWithReturnTo,
	explorerValueToUrlInput,
	safeTransactionsReturnTo,
	stripTransactionsExplorerCursor,
	validateTransactionsExplorerUrl,
	type TransactionExplorerSort,
	type TransactionExplorerValidatedInput,
	type TransactionExplorerUrlInput
} from '$lib/transactions/explorer';
import { localeFromCookie, t, type Locale } from '$lib/i18n';
import type { PageServerLoad } from './$types';

type LegacyFilters = {
	query: string;
	dateFrom: string;
	dateTo: string;
	accountId: string;
	minAmount: string;
	maxAmount: string;
	transactionState: string;
	limit: number;
	offset: number;
};

type ExplorerStatusKind =
	| 'ok'
	| 'date_range_required'
	| 'true_empty'
	| 'scan_window_empty'
	| 'scan_limited'
	| 'end'
	| 'invalid_filter'
	| 'stale_cursor'
	| 'load_failed'
	| 'unknown_failure';

type ExplorerStatus = {
	kind: ExplorerStatusKind;
	title: string;
	message: string;
	role: 'status' | 'alert';
};

type ActiveFilterChip = {
	key: string;
	label: string;
	href: string;
};

type ApiResult<T> = {
	ok: boolean;
	status: number;
	body: T | { detail?: unknown };
};

type ExportCsvState = {
	enabled: boolean;
	href: string;
	reason: string;
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
	const year = date.getUTCFullYear();
	const month = String(date.getUTCMonth() + 1).padStart(2, '0');
	const day = String(date.getUTCDate()).padStart(2, '0');
	return `${year}-${month}-${day}`;
}

function legacyTransactionUrl(filters: LegacyFilters, override: Partial<LegacyFilters> = {}): string {
	const next = { ...filters, ...override };
	const sp = new URLSearchParams({ limit: String(next.limit), offset: String(next.offset) });
	if (next.query) sp.set('query', next.query);
	if (next.dateFrom) sp.set('date_from', next.dateFrom);
	if (next.dateTo) sp.set('date_to', next.dateTo);
	if (next.accountId) sp.set('account_id', next.accountId);
	if (next.minAmount) sp.set('min_amount', next.minAmount);
	if (next.maxAmount) sp.set('max_amount', next.maxAmount);
	if (next.transactionState) sp.set('transaction_state', next.transactionState);
	return `/transactions?${sp.toString()}`;
}

function buildLegacyDatePresets(filters: LegacyFilters, asOfDate: string | null) {
	if (!asOfDate) return [];
	const now = new Date(`${asOfDate}T00:00:00Z`);
	const year = now.getUTCFullYear();
	const month = now.getUTCMonth();
	const presets: Array<{ label: string; dates: DatePresetDates }> = [
		{ label: 'This month', dates: { dateFrom: formatDate(new Date(Date.UTC(year, month, 1))), dateTo: formatDate(now) } },
		{ label: 'Last month', dates: { dateFrom: formatDate(new Date(Date.UTC(year, month - 1, 1))), dateTo: formatDate(new Date(Date.UTC(year, month, 0))) } },
		{ label: 'Year to date', dates: { dateFrom: formatDate(new Date(Date.UTC(year, 0, 1))), dateTo: formatDate(now) } },
		{ label: 'Clear dates', dates: { dateFrom: '', dateTo: '' } }
	];
	return presets.map((preset) => ({
		label: preset.label,
		href: legacyTransactionUrl(filters, { dateFrom: preset.dates.dateFrom, dateTo: preset.dates.dateTo, offset: 0 }),
		active: filters.dateFrom === preset.dates.dateFrom && filters.dateTo === preset.dates.dateTo
	}));
}

function buildExplorerDatePresets(filters: TransactionExplorerValidatedInput, asOfDate: string | null) {
	if (!asOfDate) return [];
	const now = new Date(`${asOfDate}T00:00:00Z`);
	const year = now.getUTCFullYear();
	const month = now.getUTCMonth();
	const presets: Array<{ label: string; dates: DatePresetDates }> = [
		{ label: 'This month', dates: { dateFrom: formatDate(new Date(Date.UTC(year, month, 1))), dateTo: formatDate(now) } },
		{ label: 'Last month', dates: { dateFrom: formatDate(new Date(Date.UTC(year, month - 1, 1))), dateTo: formatDate(new Date(Date.UTC(year, month, 0))) } },
		{ label: 'Year to date', dates: { dateFrom: formatDate(new Date(Date.UTC(year, 0, 1))), dateTo: formatDate(now) } },
		{ label: 'Clear dates', dates: { dateFrom: '', dateTo: '' } }
	];
	return presets.map((preset) => ({
		label: preset.label,
		href: buildTransactionsExplorerUrlFromValue(filters, { dateFrom: preset.dates.dateFrom, dateTo: preset.dates.dateTo, cursor: '' }),
		active: filters.dateFrom === preset.dates.dateFrom && filters.dateTo === preset.dates.dateTo
	}));
}

function isLegacyCompatibilityUrl(url: URL): boolean {
	const params = url.searchParams;
	const offset = Number(params.get('offset') ?? '0');
	const hasNonzeroOffset = Number.isFinite(offset) && offset > 0;
	const hasOneSidedDate = params.has('date_from') !== params.has('date_to');
	return hasNonzeroOffset || hasOneSidedDate;
}

function hasAdvancedFieldsWithLegacyOffset(url: URL): boolean {
	const params = url.searchParams;
	const offset = Number(params.get('offset') ?? '0');
	if (!Number.isFinite(offset) || offset <= 0) return false;
	return ['account_ids', 'type', 'direction', 'sort', 'page_size', 'cursor'].some((key) => params.has(key));
}

function legacyCanonicalExplorerHref(url: URL): string | null {
	const params = url.searchParams;
	const offset = Number(params.get('offset') ?? '0');
	const hasNonzeroOffset = Number.isFinite(offset) && offset > 0;
	const hasOneSidedDate = params.has('date_from') !== params.has('date_to');
	if (hasNonzeroOffset || hasOneSidedDate) return null;
	if (params.getAll('account_id').length > 1 || (params.has('account_id') && params.has('account_ids'))) return null;
	if (!params.has('account_id') && !params.has('limit') && !params.has('offset')) return null;
	const rawLimit = Number(params.get('limit') ?? TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE);
	const pageSize = Number.isInteger(rawLimit)
		? Math.min(Math.max(rawLimit, 1), TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE)
		: TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE;
	return buildTransactionsExplorerUrl({
		dateFrom: params.get('date_from') ?? '',
		dateTo: params.get('date_to') ?? '',
		accountIds: params.get('account_id') ? [params.get('account_id') ?? ''] : params.getAll('account_ids'),
		minAmount: params.get('min_amount') ?? '',
		maxAmount: params.get('max_amount') ?? '',
		query: params.get('query') ?? '',
		transactionState: (params.get('transaction_state') as TransactionExplorerUrlInput['transactionState']) ?? '',
		sort: TRANSACTIONS_EXPLORER_DEFAULT_SORT,
		pageSize
	});
}

function legacyFiltersFromUrl(url: URL): LegacyFilters {
	const limit = positiveInt(url.searchParams.get('limit'), 50, 200) || 50;
	return {
		query: url.searchParams.get('query') ?? '',
		dateFrom: url.searchParams.get('date_from') ?? '',
		dateTo: url.searchParams.get('date_to') ?? '',
		accountId: url.searchParams.get('account_id') ?? '',
		minAmount: url.searchParams.get('min_amount') ?? '',
		maxAmount: url.searchParams.get('max_amount') ?? '',
		transactionState: url.searchParams.get('transaction_state') ?? '',
		limit,
		offset: positiveInt(url.searchParams.get('offset'), 0, Number.MAX_SAFE_INTEGER)
	};
}

function legacyApiParams(filters: LegacyFilters): URLSearchParams {
	const sp = new URLSearchParams({ limit: String(filters.limit), offset: String(filters.offset) });
	if (filters.query) sp.set('query', filters.query);
	if (filters.dateFrom) sp.set('date_from', filters.dateFrom);
	if (filters.dateTo) sp.set('date_to', filters.dateTo);
	if (filters.accountId) sp.set('account_id', filters.accountId);
	if (filters.minAmount) sp.set('min_amount', filters.minAmount);
	if (filters.maxAmount) sp.set('max_amount', filters.maxAmount);
	if (filters.transactionState) sp.set('transaction_state', filters.transactionState);
	return sp;
}

async function apiJson<T>(fetchFn: typeof fetch, path: string, token: string): Promise<ApiResult<T>> {
	const apiBase = env.API_INTERNAL_URL ?? 'http://localhost:8000';
	let response: Response;
	try {
		response = await fetchFn(`${apiBase}${path}`, {
			headers: { authorization: `Bearer ${token}` }
		});
	} catch {
		return { ok: false, status: 502, body: {} };
	}
	if (response.status === 401) throw redirect(303, '/login');
	const body = await response.json().catch(() => ({}));
	return { ok: response.ok, status: response.status, body: body as T | { detail?: unknown } };
}

function detailCode(body: unknown): string {
	if (typeof body !== 'object' || body === null || !('detail' in body)) return '';
	const detail = body.detail;
	if (typeof detail === 'object' && detail !== null && 'code' in detail && typeof detail.code === 'string') return detail.code;
	if (typeof detail === 'string' && /^[a-z0-9_:-]{1,80}$/i.test(detail)) return detail;
	return '';
}

function classifyExplorerFailure(status: number, body: unknown, locale: Locale): ExplorerStatus {
	const code = detailCode(body);
	if (code.includes('cursor')) {
		return {
			kind: 'stale_cursor',
			title: t(locale, 'transactions.explorer.staleCursorTitle'),
			message: t(locale, 'transactions.explorer.staleCursorMessage'),
			role: 'alert'
		};
	}
	if (status === 400 || status === 422) {
		return {
			kind: 'invalid_filter',
			title: t(locale, 'transactions.explorer.invalidFilterTitle'),
			message: t(locale, 'transactions.explorer.invalidFilterMessage'),
			role: 'alert'
		};
	}
	if (status === 403 || status === 404 || status === 502 || status === 503 || status >= 500) {
		return {
			kind: 'load_failed',
			title: t(locale, 'transactions.explorer.loadFailedTitle'),
			message: t(locale, 'transactions.explorer.loadFailedMessage'),
			role: 'alert'
		};
	}
	return {
		kind: 'unknown_failure',
		title: t(locale, 'transactions.explorer.unknownFailureTitle'),
		message: t(locale, 'transactions.explorer.unknownFailureMessage'),
		role: 'alert'
	};
}

function stringValue(value: unknown): string | null {
	return typeof value === 'string' && value.trim() ? value : null;
}

function numberValue(value: unknown, fallback: number): number {
	return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function booleanValue(value: unknown): boolean {
	return value === true;
}

function emptyExplorerPage(
	sort: TransactionExplorerSort = TRANSACTIONS_EXPLORER_DEFAULT_SORT,
	pageSize = TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE
): TransactionExplorerPage {
	return {
		items: [],
		sort,
		page_size: pageSize,
		returned_count: 0,
		has_more: false,
		has_previous: false,
		next_cursor: null,
		previous_cursor: null,
		scan: { candidate_rows: 0, split_rows: 0, query_count: 0, scan_limited: false, exhausted: true },
		limitations: []
	};
}

function hasBoundedExplorerDateRange(filters: TransactionExplorerValidatedInput): boolean {
	return Boolean(filters.dateFrom && filters.dateTo);
}

function dateRangeRequiredStatus(locale: Locale): ExplorerStatus {
	return {
		kind: 'date_range_required',
		title: t(locale, 'transactions.explorer.dateRangeRequiredTitle'),
		message: t(locale, 'transactions.explorer.dateRangeRequiredMessage'),
		role: 'status'
	};
}

function sanitizeLimitations(limitations: unknown): string[] {
	if (!Array.isArray(limitations)) return [];
	return limitations
		.map((limitation) => (typeof limitation === 'string' ? limitation.trim() : ''))
		.filter(Boolean)
		.map((limitation) => {
			if (limitation.length > 180 || /[\\/]/.test(limitation) || /PRIVATE|SENTINEL|TOKEN|SECRET/i.test(limitation)) {
				return 'Backend limitation detail redacted.';
			}
			return limitation;
		})
		.slice(0, 6);
}

function normalizeExplorerItem(item: TransactionListItem): TransactionListItem {
	const raw = item as TransactionListItem & {
		representative_amount?: { amount?: unknown; currency?: unknown } | null;
		representative_account?: { id?: unknown; name?: unknown } | null;
	};
	return {
		...item,
		amount: stringValue(raw.amount) ?? stringValue(raw.representative_amount?.amount) ?? '',
		currency: stringValue(raw.currency) ?? stringValue(raw.representative_amount?.currency) ?? '',
		account_id: stringValue(raw.account_id) ?? stringValue(raw.representative_account?.id) ?? '',
		account_name: stringValue(raw.account_name) ?? stringValue(raw.representative_account?.name) ?? '',
		counter_account_name: stringValue(raw.counter_account_name) ?? ''
	};
}

function normalizeExplorerPage(payload: TransactionExplorerPage, request: TransactionExplorerValidatedInput): TransactionExplorerPage {
	const body = payload && typeof payload === 'object' ? payload : ({} as TransactionExplorerPage);
	const items = Array.isArray(body.items) ? body.items.map(normalizeExplorerItem) : [];
	const rawScan = body.scan && typeof body.scan === 'object' ? body.scan : emptyExplorerPage(request.sort, request.pageSize).scan;
	return {
		items,
		sort: stringValue(body.sort) ?? request.sort,
		page_size: numberValue(body.page_size, request.pageSize),
		returned_count: numberValue(body.returned_count, items.length),
		has_more: booleanValue(body.has_more),
		has_previous: booleanValue(body.has_previous),
		next_cursor: stringValue(body.next_cursor),
		previous_cursor: stringValue(body.previous_cursor),
		scan: {
			candidate_rows: numberValue(rawScan.candidate_rows, 0),
			split_rows: numberValue(rawScan.split_rows, 0),
			query_count: numberValue(rawScan.query_count, 0),
			scan_limited: booleanValue(rawScan.scan_limited),
			exhausted: booleanValue(rawScan.exhausted)
		},
		limitations: sanitizeLimitations(body.limitations)
	};
}

function isScanLimited(page: TransactionExplorerPage): boolean {
	return Boolean(page.scan.scan_limited);
}

function explorerStatus(page: TransactionExplorerPage, request: TransactionExplorerValidatedInput, locale: Locale): ExplorerStatus {
	const scanLimited = isScanLimited(page);
	if (page.items.length === 0 && scanLimited && !page.scan.exhausted) {
		return {
			kind: 'scan_window_empty',
			title: t(locale, 'transactions.explorer.scanWindowEmptyTitle'),
			message: t(locale, 'transactions.explorer.scanWindowEmptyMessage'),
			role: 'status'
		};
	}
	if (page.items.length === 0 && request.cursor) {
		return {
			kind: 'end',
			title: t(locale, 'transactions.explorer.endTitle'),
			message: t(locale, 'transactions.explorer.endMessage'),
			role: 'status'
		};
	}
	if (page.items.length === 0) {
		return {
			kind: 'true_empty',
			title: t(locale, 'transactions.explorer.trueEmptyTitle'),
			message: t(locale, 'transactions.explorer.trueEmptyMessage'),
			role: 'status'
		};
	}
	if (scanLimited) {
		return {
			kind: 'scan_limited',
			title: t(locale, 'transactions.explorer.scanLimitedTitle'),
			message: t(locale, 'transactions.explorer.scanLimitedMessage'),
			role: 'status'
		};
	}
	if (!page.has_more && request.cursor) {
		return {
			kind: 'end',
			title: t(locale, 'transactions.explorer.endTitle'),
			message: t(locale, 'transactions.explorer.endMessage'),
			role: 'status'
		};
	}
	return {
		kind: 'ok',
		title: t(locale, 'transactions.explorer.readyTitle'),
		message: t(locale, 'transactions.explorer.readyMessage'),
		role: 'status'
	};
}

function accountLabel(accounts: AccountOption[], accountId: string): string {
	const account = accounts.find((candidate) => candidate.id.toLowerCase() === accountId.toLowerCase());
	return account?.full_name || account?.name || accountId;
}

function activeExplorerChips(filters: TransactionExplorerValidatedInput, accounts: AccountOption[], locale: Locale): ActiveFilterChip[] {
	const chips: ActiveFilterChip[] = [];
	const withoutCursor = stripTransactionsExplorerCursor(filters);
	if (filters.dateFrom && filters.dateTo) {
		chips.push({
			key: 'dates',
			label: `${t(locale, 'transactions.filters.summary.dates')}: ${filters.dateFrom} – ${filters.dateTo}`,
			href: buildTransactionsExplorerUrl({ ...withoutCursor, dateFrom: '', dateTo: '' })
		});
	}
	for (const accountId of filters.accountIds) {
		chips.push({
			key: `account:${accountId}`,
			label: `${t(locale, 'transactions.filters.summary.account')}: ${accountLabel(accounts, accountId)}`,
			href: buildTransactionsExplorerUrl({
				...withoutCursor,
				accountIds: filters.accountIds.filter((candidate) => candidate !== accountId),
				direction: filters.accountIds.length === 1 ? '' : filters.direction
			})
		});
	}
	if (filters.type) {
		chips.push({ key: 'type', label: `Type: ${filters.type}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, type: '' }) });
	}
	if (filters.direction) {
		chips.push({ key: 'direction', label: `Direction: ${filters.direction}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, direction: '' }) });
	}
	if (filters.minAmount) {
		chips.push({ key: 'min', label: `${t(locale, 'transactions.filters.summary.minAmount')}: ${filters.minAmount}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, minAmount: '' }) });
	}
	if (filters.maxAmount) {
		chips.push({ key: 'max', label: `${t(locale, 'transactions.filters.summary.maxAmount')}: ${filters.maxAmount}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, maxAmount: '' }) });
	}
	if (filters.query) {
		chips.push({ key: 'query', label: `${t(locale, 'transactions.filters.summary.search')}: ${filters.query}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, query: '' }) });
	}
	if (filters.transactionState) {
		chips.push({ key: 'state', label: `${t(locale, 'transactions.filters.summary.state')}: ${filters.transactionState}`, href: buildTransactionsExplorerUrl({ ...withoutCursor, transactionState: '' }) });
	}
	if (filters.cursor) {
		chips.push({ key: 'cursor', label: t(locale, 'transactions.explorer.cursorChip'), href: buildTransactionsExplorerUrl({ ...withoutCursor, cursor: '' }) });
	}
	return chips;
}

function currentTransactionsReturnTo(url: URL, fallback: TransactionExplorerUrlInput = {}): string {
	const candidate = `${url.pathname}${url.search}`;
	if (url.pathname === '/transactions' && candidate.length <= 2048) return safeTransactionsReturnTo(candidate);
	return buildTransactionsExplorerUrl(fallback);
}

function detailHrefs(items: TransactionListItem[], returnTo: string): Record<string, string> {
	return Object.fromEntries(items.map((item) => [item.id, detailHrefWithReturnTo(item.id, returnTo)]));
}

function legacyCsvParamsFromExplorer(filters: TransactionExplorerValidatedInput): URLSearchParams | null {
	if (filters.cursor || filters.type || filters.direction || filters.query || filters.accountIds.length > 1) return null;
	if ((filters.minAmount || filters.maxAmount) && filters.accountIds.length !== 1) return null;
	const params = new URLSearchParams();
	if (filters.accountIds[0]) params.set('account_id', filters.accountIds[0]);
	if (filters.dateFrom) params.set('date_from', filters.dateFrom);
	if (filters.dateTo) params.set('date_to', filters.dateTo);
	if (filters.transactionState) params.set('transaction_state', filters.transactionState);
	if (filters.minAmount) params.set('min_amount', filters.minAmount);
	if (filters.maxAmount) params.set('max_amount', filters.maxAmount);
	return params;
}

function explorerCsvState(activeBookId: number | undefined, filters: TransactionExplorerValidatedInput, locale: Locale): ExportCsvState {
	const params = legacyCsvParamsFromExplorer(filters);
	if (!activeBookId || !params) {
		return { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') };
	}
	const qs = params.toString();
	return { enabled: true, href: `/books/${activeBookId}/transactions/export${qs ? `?${qs}` : ''}`, reason: '' };
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const locale = localeFromCookie(cookies);
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const writesEnabled = env.GNUCASH_WRITES_ENABLED === 'true';

	if (!activeBook) {
		const resetHref = buildTransactionsExplorerUrl();
		const resetValidation = validateTransactionsExplorerUrl(new URL(resetHref, url.origin));
		return {
			mode: 'explorer' as const,
			accounts: [],
			accountOptions: [],
			accountOptionsAvailable: false,
			accountOptionsLimited: false,
			accountOptionsPartialFailure: false,
			accountOptionsErrorCode: 'no_active_book',
			activeBook,
			writesEnabled,
			filters: resetValidation.ok ? resetValidation.value : null,
			pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
			datePresets: [],
			activeFilters: [],
			resetHref,
			resetPaginationHref: resetHref,
			exportCsv: { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') },
			txs: emptyExplorerPage(),
			status: { kind: 'load_failed', title: t(locale, 'transactions.explorer.loadFailedTitle'), message: t(locale, 'transactions.explorer.loadFailedMessage'), role: 'alert' } satisfies ExplorerStatus,
			detailHrefs: {}
		};
	}

	const canonicalLegacyHref = legacyCanonicalExplorerHref(url);
	if (canonicalLegacyHref && canonicalLegacyHref !== `${url.pathname}${url.search}`) {
		throw redirect(303, canonicalLegacyHref);
	}

	const reportingDate = await getReportingDate(fetch, bookPrefix, token);
	const accountOptionsState = await loadAccountOptions(fetch, bookPrefix, token, {
		purpose: 'transactions_filter',
		currency: activeBook.base_currency
	});
	const accountOptions = accountOptionsState.items;
	const accounts = accountOptions;
	const accountOptionsPageState = {
		reportingDateUnavailable: reportingDate === null,
		accountOptions,
		accountOptionsAvailable: accountOptionsState.available,
		accountOptionsLimited: accountOptionsState.limited,
		accountOptionsPartialFailure: accountOptionsState.partialFailure,
		accountOptionsErrorCode: accountOptionsState.errorCode
	};

	if (hasAdvancedFieldsWithLegacyOffset(url)) {
		const fallback = validateTransactionsExplorerUrl(new URL(buildTransactionsExplorerUrl(), url.origin)).value;
		return {
			mode: 'explorer' as const,
			accounts,
			...accountOptionsPageState,
			activeBook,
			writesEnabled,
			filters: fallback,
			pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
			datePresets: buildExplorerDatePresets(fallback, reportingDate),
			activeFilters: [],
			resetHref: buildTransactionsExplorerUrl(),
			resetPaginationHref: buildTransactionsExplorerUrl(),
			exportCsv: { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') },
			txs: emptyExplorerPage(fallback.sort, fallback.pageSize),
			status: { kind: 'invalid_filter', title: t(locale, 'transactions.explorer.invalidFilterTitle'), message: t(locale, 'transactions.explorer.legacyOffsetConflict'), role: 'alert' } satisfies ExplorerStatus,
			detailHrefs: {}
		};
	}

	if (isLegacyCompatibilityUrl(url)) {
		const filters = legacyFiltersFromUrl(url);
		const transactionParams = legacyApiParams(filters);
		const txs = await apiFetch<PaginatedTransactions>(fetch, `${bookPrefix}/transactions?${transactionParams.toString()}`, token);
		const returnTo = currentTransactionsReturnTo(url);
		return {
			mode: 'legacy' as const,
			accounts,
			...accountOptionsPageState,
			activeBook,
			writesEnabled,
			filters,
			datePresets: buildLegacyDatePresets(filters, reportingDate),
			clearFiltersHref: '/transactions?sort=date_desc&page_size=50',
			legacyNotice: t(locale, 'transactions.explorer.legacyCompatibility'),
			exportCsv: {
				enabled: true,
				href: activeBook ? `/books/${activeBook.id}/transactions/export?${legacyApiParams({ ...filters, offset: 0 }).toString()}` : '#',
				reason: ''
			},
			txs,
			detailHrefs: detailHrefs(txs.items, returnTo)
		};
	}

	const validation = validateTransactionsExplorerUrl(url);
	const filters = validation.value;
	const resetHref = buildTransactionsExplorerUrl();
	const resetPaginationHref = buildTransactionsExplorerUrl({ ...stripTransactionsExplorerCursor(filters), cursor: '' });
	const activeFilters = activeExplorerChips(filters, accountOptions, locale);

	if (!validation.ok) {
		return {
			mode: 'explorer' as const,
			accounts,
			...accountOptionsPageState,
			activeBook,
			writesEnabled,
			filters,
			pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
			datePresets: buildExplorerDatePresets(filters, reportingDate),
			activeFilters,
			resetHref,
			resetPaginationHref,
			exportCsv: { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') },
			txs: emptyExplorerPage(filters.sort, filters.pageSize),
			status: { kind: 'invalid_filter', title: t(locale, 'transactions.explorer.invalidFilterTitle'), message: validation.message, role: 'alert' } satisfies ExplorerStatus,
			detailHrefs: {}
		};
	}

	if (!hasBoundedExplorerDateRange(filters)) {
		return {
			mode: 'explorer' as const,
			accounts,
			...accountOptionsPageState,
			activeBook,
			writesEnabled,
			filters,
			pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
			datePresets: buildExplorerDatePresets(filters, reportingDate),
			activeFilters,
			resetHref,
			resetPaginationHref,
			exportCsv: { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') },
			txs: emptyExplorerPage(filters.sort, filters.pageSize),
			status: dateRangeRequiredStatus(locale),
			detailHrefs: {}
		};
	}

	const explorerParams = buildTransactionsExplorerSearchParams(explorerValueToUrlInput(filters));
	const result = await apiJson<TransactionExplorerPage>(fetch, `${bookPrefix}/transactions/explorer?${explorerParams.toString()}`, token);
	if (!result.ok) {
		return {
			mode: 'explorer' as const,
			accounts,
			...accountOptionsPageState,
			activeBook,
			writesEnabled,
			filters,
			pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
			datePresets: buildExplorerDatePresets(filters, reportingDate),
			activeFilters,
			resetHref,
			resetPaginationHref,
			exportCsv: { enabled: false, href: '#', reason: t(locale, 'transactions.export.explorerDisabled') },
			txs: emptyExplorerPage(filters.sort, filters.pageSize),
			status: classifyExplorerFailure(result.status, result.body, locale),
			detailHrefs: {}
		};
	}

	const txs = normalizeExplorerPage(result.body as TransactionExplorerPage, filters);
	const returnTo = currentTransactionsReturnTo(url, explorerValueToUrlInput(filters));
	return {
		mode: 'explorer' as const,
		accounts,
		...accountOptionsPageState,
		activeBook,
		writesEnabled,
		filters,
		pageSizeOptions: TRANSACTIONS_EXPLORER_PAGE_SIZES,
		datePresets: buildExplorerDatePresets(filters, reportingDate),
		activeFilters,
		resetHref,
		resetPaginationHref,
		exportCsv: explorerCsvState(activeBook.id, filters, locale),
		txs,
		status: explorerStatus(txs, filters, locale),
		pagination: {
			previousHref: txs.previous_cursor ? buildTransactionsExplorerUrlFromValue(filters, { cursor: txs.previous_cursor }) : '',
			nextHref: txs.next_cursor ? buildTransactionsExplorerUrlFromValue(filters, { cursor: txs.next_cursor }) : '',
			continueHref: txs.has_more && txs.next_cursor ? buildTransactionsExplorerUrlFromValue(filters, { cursor: txs.next_cursor }) : ''
		},
		detailHrefs: detailHrefs(txs.items, returnTo)
	};
};
