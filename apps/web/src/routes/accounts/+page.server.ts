import { redirect } from '@sveltejs/kit';
import { getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { AccountExplorerResponse } from '$lib/api/types';
import {
	ACCOUNT_EXPLORER_DEFAULT_HIDDEN,
	ACCOUNT_EXPLORER_DEFAULT_MODE,
	ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER,
	buildAccountDetailUrl,
	buildAccountExplorerSearchParams,
	buildAccountExplorerUrl,
	validateAccountExplorerUrl,
	type AccountExplorerValidatedInput
} from '$lib/accounts/explorer';
import { localeFromCookie, t, type Locale } from '$lib/i18n';
import type { PageServerLoad } from './$types';

type ApiResult<T> = {
	ok: boolean;
	status: number;
	body: T | { detail?: unknown };
};

type AccountExplorerStatus = {
	kind: 'ok' | 'no_accounts' | 'no_matches' | 'invalid_filter' | 'narrow_filters' | 'load_failed' | 'unknown_failure';
	title: string;
	message: string;
	role: 'status' | 'alert';
};

type ActiveAccountFilterChip = {
	key: string;
	label: string;
	href: string;
};

function emptyExplorerResponse(mode: 'tree' | 'flat' = ACCOUNT_EXPLORER_DEFAULT_MODE): AccountExplorerResponse {
	return {
		book_id: 0,
		mode,
		normalized_filters: {
			query: null,
			types: [],
			hidden: ACCOUNT_EXPLORER_DEFAULT_HIDDEN,
			placeholder: ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER
		},
		root_ids: [],
		nodes: [],
		returned_count: 0,
		scan: {
			candidate_accounts: 0,
			returned_nodes: 0,
			split_rows: 0,
			split_aggregate_rows: 0,
			query_count: 0,
			rollup_bucket_cells: 0,
			serialized_bytes: 0,
			exhausted: true,
			limits: {}
		},
		balance_basis: 'native_commodity_account_natural_sign',
		includes_currency_conversion: false,
		limitations: []
	};
}

async function apiJson<T>(fetchFn: typeof fetch, path: string, token: string): Promise<ApiResult<T>> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
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

function classifyExplorerFailure(status: number, body: unknown, locale: Locale): AccountExplorerStatus {
	const code = detailCode(body);
	if (code === 'result_too_large' || code === 'result_too_complex' || code === 'too_many_commodities' || code === 'result_too_deep') {
		return {
			kind: 'narrow_filters',
			title: t(locale, 'accounts.explorer.narrowFiltersTitle'),
			message: t(locale, 'accounts.explorer.narrowFiltersMessage'),
			role: 'alert'
		};
	}
	if (status === 400 || status === 422) {
		return {
			kind: 'invalid_filter',
			title: t(locale, 'accounts.explorer.invalidFilterTitle'),
			message: t(locale, 'accounts.explorer.invalidFilterMessage'),
			role: 'alert'
		};
	}
	if (status === 403 || status === 404 || status === 502 || status === 503 || status >= 500) {
		return {
			kind: 'load_failed',
			title: t(locale, 'accounts.explorer.loadFailedTitle'),
			message: t(locale, 'accounts.explorer.loadFailedMessage'),
			role: 'alert'
		};
	}
	return {
		kind: 'unknown_failure',
		title: t(locale, 'accounts.explorer.unknownFailureTitle'),
		message: t(locale, 'accounts.explorer.unknownFailureMessage'),
		role: 'alert'
	};
}

function hasActiveExplorerFilters(filters: AccountExplorerValidatedInput): boolean {
	return Boolean(
		filters.mode !== ACCOUNT_EXPLORER_DEFAULT_MODE ||
			filters.query ||
			filters.types.length ||
			filters.hidden !== ACCOUNT_EXPLORER_DEFAULT_HIDDEN ||
			filters.placeholder !== ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER
	);
}

function explorerStatus(page: AccountExplorerResponse, filters: AccountExplorerValidatedInput, locale: Locale): AccountExplorerStatus {
	if (page.nodes.length === 0 && hasActiveExplorerFilters(filters)) {
		return {
			kind: 'no_matches',
			title: t(locale, 'accounts.explorer.noMatchesTitle'),
			message: t(locale, 'accounts.explorer.noMatchesMessage'),
			role: 'status'
		};
	}
	if (page.nodes.length === 0) {
		return {
			kind: 'no_accounts',
			title: t(locale, 'accounts.emptyTitle'),
			message: t(locale, 'accounts.emptyMessage'),
			role: 'status'
		};
	}
	return {
		kind: 'ok',
		title: t(locale, 'accounts.explorer.readyTitle'),
		message: t(locale, 'accounts.explorer.readyMessage'),
		role: 'status'
	};
}

function activeExplorerChips(filters: AccountExplorerValidatedInput, locale: Locale): ActiveAccountFilterChip[] {
	const chips: ActiveAccountFilterChip[] = [];
	const base = { ...filters };
	if (filters.mode === 'flat') {
		chips.push({ key: 'mode', label: `${t(locale, 'accounts.explorer.mode')}: ${t(locale, 'accounts.explorer.modeFlat')}`, href: buildAccountExplorerUrl({ ...base, mode: 'tree' }) });
	}
	if (filters.query) {
		chips.push({ key: 'query', label: `${t(locale, 'accounts.explorer.query')}: ${filters.query}`, href: buildAccountExplorerUrl({ ...base, query: '' }) });
	}
	for (const type of filters.types) {
		chips.push({
			key: `type:${type}`,
			label: `${t(locale, 'accounts.explorer.type')}: ${type}`,
			href: buildAccountExplorerUrl({ ...base, types: filters.types.filter((candidate) => candidate !== type) })
		});
	}
	if (filters.hidden !== ACCOUNT_EXPLORER_DEFAULT_HIDDEN) {
		chips.push({ key: 'hidden', label: `${t(locale, 'accounts.explorer.hidden')}: ${filters.hidden}`, href: buildAccountExplorerUrl({ ...base, hidden: ACCOUNT_EXPLORER_DEFAULT_HIDDEN }) });
	}
	if (filters.placeholder !== ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER) {
		chips.push({ key: 'placeholder', label: `${t(locale, 'accounts.explorer.placeholder')}: ${filters.placeholder}`, href: buildAccountExplorerUrl({ ...base, placeholder: ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER }) });
	}
	return chips;
}

function detailHrefs(page: AccountExplorerResponse, explorerReturnTo: string): Record<string, string> {
	return Object.fromEntries(page.nodes.map((node) => [node.id, buildAccountDetailUrl(node.id, { returnTo: explorerReturnTo })]));
}

function sanitizeLimitations(limitations: unknown): string[] {
	if (!Array.isArray(limitations)) return [];
	return limitations
		.map((item) => (typeof item === 'string' ? item.trim() : ''))
		.filter(Boolean)
		.map((item) => (item.length > 180 || /[\\/]/.test(item) || /PRIVATE|SENTINEL|TOKEN|SECRET/i.test(item) ? 'Backend limitation detail redacted.' : item))
		.slice(0, 8);
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const locale = localeFromCookie(cookies);
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const validation = validateAccountExplorerUrl(url);
	const filters = validation.value;
	const resetHref = buildAccountExplorerUrl();
	const activeFilters = activeExplorerChips(filters, locale);

	if (!activeBook) {
		return {
			activeBook,
			locale,
			filters,
			activeFilters,
			resetHref,
			canonicalHref: resetHref,
			accounts: emptyExplorerResponse(filters.mode),
			status: { kind: 'load_failed', title: t(locale, 'accounts.explorer.loadFailedTitle'), message: t(locale, 'accounts.explorer.loadFailedMessage'), role: 'alert' } satisfies AccountExplorerStatus,
			detailHrefs: {}
		};
	}

	if (!validation.ok) {
		return {
			activeBook,
			locale,
			filters,
			activeFilters,
			resetHref,
			canonicalHref: validation.canonicalHref,
			accounts: emptyExplorerResponse(filters.mode),
			status: { kind: 'invalid_filter', title: t(locale, 'accounts.explorer.invalidFilterTitle'), message: validation.message, role: 'alert' } satisfies AccountExplorerStatus,
			detailHrefs: {}
		};
	}

	if (validation.canonicalHref !== `${url.pathname}${url.search}`) {
		throw redirect(303, validation.canonicalHref);
	}

	const explorerParams = buildAccountExplorerSearchParams(filters);
	const query = explorerParams.toString();
	const result = await apiJson<AccountExplorerResponse>(fetch, `${bookPrefix}/accounts/explorer${query ? `?${query}` : ''}`, token);
	if (!result.ok) {
		return {
			activeBook,
			locale,
			filters,
			activeFilters,
			resetHref,
			canonicalHref: validation.canonicalHref,
			accounts: emptyExplorerResponse(filters.mode),
			status: classifyExplorerFailure(result.status, result.body, locale),
			detailHrefs: {}
		};
	}

	const accounts = result.body as AccountExplorerResponse;
	accounts.limitations = sanitizeLimitations(accounts.limitations);
	return {
		activeBook,
		locale,
		filters,
		activeFilters,
		resetHref,
		canonicalHref: validation.canonicalHref,
		accounts,
		status: explorerStatus(accounts, filters, locale),
		detailHrefs: detailHrefs(accounts, validation.canonicalHref)
	};
};
