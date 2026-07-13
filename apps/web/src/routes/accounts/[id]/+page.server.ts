import { redirect } from '@sveltejs/kit';
import { getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { AccountActivity, AccountOverview } from '$lib/api/types';
import {
	ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT,
	buildAccountDetailUrl,
	buildAccountTransactionExplorerUrl,
	buildBaseReportUrl,
	hasAccountActivityDateRange,
	validateAccountDetailUrl
} from '$lib/accounts/explorer';
import { localeFromCookie, t, type Locale } from '$lib/i18n';
import type { PageServerLoad } from './$types';

type ApiResult<T> = {
	ok: boolean;
	status: number;
	body: T | { detail?: unknown };
};

type AccountDetailStatus = {
	kind: 'overview_only' | 'activity_loaded' | 'invalid_filter' | 'activity_empty' | 'partial_activity' | 'load_failed' | 'unknown_failure';
	title: string;
	message: string;
	role: 'status' | 'alert';
};

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

function classifyLoadFailure(status: number, locale: Locale): AccountDetailStatus {
	if (status === 403 || status === 404 || status === 502 || status === 503 || status >= 500) {
		return {
			kind: 'load_failed',
			title: t(locale, 'accounts.detail.loadFailedTitle'),
			message: t(locale, 'accounts.detail.loadFailedMessage'),
			role: 'alert'
		};
	}
	return {
		kind: 'unknown_failure',
		title: t(locale, 'accounts.detail.unknownFailureTitle'),
		message: t(locale, 'accounts.detail.unknownFailureMessage'),
		role: 'alert'
	};
}

function activityParams(dateFrom: string, dateTo: string, limit: number): URLSearchParams {
	const params = new URLSearchParams();
	params.append('date_from', dateFrom);
	params.append('date_to', dateTo);
	if (limit !== ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT) params.append('limit', String(limit));
	return params;
}

function activityStatus(activity: AccountActivity, locale: Locale): AccountDetailStatus {
	if (activity.partial_failure) {
		return {
			kind: 'partial_activity',
			title: t(locale, 'accounts.detail.partialActivityTitle'),
			message: t(locale, 'accounts.detail.partialActivityMessage'),
			role: 'alert'
		};
	}
	if (activity.returned_count === 0 && activity.section_statuses.every((item) => item.status === 'empty')) {
		return {
			kind: 'activity_empty',
			title: t(locale, 'accounts.detail.activityEmptyTitle'),
			message: t(locale, 'accounts.detail.activityEmptyMessage'),
			role: 'status'
		};
	}
	return {
		kind: 'activity_loaded',
		title: t(locale, 'accounts.detail.activityLoadedTitle'),
		message: t(locale, 'accounts.detail.activityLoadedMessage'),
		role: 'status'
	};
}

function overviewOnlyStatus(locale: Locale): AccountDetailStatus {
	return {
		kind: 'overview_only',
		title: t(locale, 'accounts.detail.overviewOnlyTitle'),
		message: t(locale, 'accounts.detail.overviewOnlyMessage'),
		role: 'status'
	};
}

function sanitizeLimitations(limitations: unknown): string[] {
	if (!Array.isArray(limitations)) return [];
	return limitations
		.map((item) => (typeof item === 'string' ? item.trim() : ''))
		.filter(Boolean)
		.map((item) => (item.length > 180 || /[\\/]/.test(item) || /PRIVATE|SENTINEL|TOKEN|SECRET/i.test(item) ? 'Backend limitation detail redacted.' : item))
		.slice(0, 8);
}

export const load: PageServerLoad = async ({ cookies, fetch, params, url }) => {
	const locale = localeFromCookie(cookies);
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const validation = validateAccountDetailUrl(url, params.id);
	const filters = validation.value;
	const activityRequestCounters = { overview: 0, activity: 0 };

	if (!activeBook) {
		return {
			activeBook,
			locale,
			filters,
			overview: null,
			activity: null,
			returnTo: filters.returnTo,
			resetActivityHref: buildAccountDetailUrl(filters.accountId, { returnTo: filters.returnTo }),
			status: classifyLoadFailure(503, locale),
			activityRequestCounters,
			legacyNotice: ''
		};
	}

	if (!validation.ok) {
		return {
			activeBook,
			locale,
			filters,
			overview: null,
			activity: null,
			returnTo: filters.returnTo,
			resetActivityHref: buildAccountDetailUrl(filters.accountId, { returnTo: filters.returnTo }),
			status: { kind: 'invalid_filter', title: t(locale, 'accounts.detail.invalidFilterTitle'), message: t(locale, 'accounts.detail.invalidFilterMessage'), role: 'alert' } satisfies AccountDetailStatus,
			activityRequestCounters,
			legacyNotice: ''
		};
	}

	if (filters.legacyKeys.length === 0 && validation.canonicalHref !== `${url.pathname}${url.search}`) {
		throw redirect(303, validation.canonicalHref);
	}

	activityRequestCounters.overview = 1;
	const overviewResult = await apiJson<AccountOverview>(fetch, `${bookPrefix}/accounts/${encodeURIComponent(filters.accountId)}/overview`, token);
	if (!overviewResult.ok) {
		return {
			activeBook,
			locale,
			filters,
			overview: null,
			activity: null,
			returnTo: filters.returnTo,
			resetActivityHref: buildAccountDetailUrl(filters.accountId, { returnTo: filters.returnTo }),
			status: classifyLoadFailure(overviewResult.status, locale),
			activityRequestCounters,
			legacyNotice: filters.legacyKeys.length ? t(locale, 'accounts.detail.legacyNotice') : ''
		};
	}

	const overview = overviewResult.body as AccountOverview;
	overview.limitations = sanitizeLimitations(overview.limitations);
	const resetActivityHref = buildAccountDetailUrl(filters.accountId, { returnTo: filters.returnTo });
	const canonicalAccountDetailHref = buildAccountDetailUrl(filters.accountId, filters);
	const childHrefs = Object.fromEntries(overview.children.map((child) => [child.id, buildAccountDetailUrl(child.id, { returnTo: filters.returnTo })]));

	if (!hasAccountActivityDateRange(filters)) {
		return {
			activeBook,
			locale,
			filters,
			overview,
			activity: null,
			returnTo: filters.returnTo,
			resetActivityHref,
			canonicalAccountDetailHref,
			childHrefs,
			transactionHrefs: {},
			transactionExplorerHref: '',
			reportHref: '',
			status: overviewOnlyStatus(locale),
			activityRequestCounters,
			legacyNotice: filters.legacyKeys.length ? t(locale, 'accounts.detail.legacyNotice') : ''
		};
	}

	const apiParams = activityParams(filters.dateFrom, filters.dateTo, filters.limit);
	activityRequestCounters.activity = 1;
	const activityEndpoint = `${bookPrefix}/accounts/${encodeURIComponent(filters.accountId)}/activity?${apiParams.toString()}`;
	const activityResult = await apiJson<AccountActivity>(fetch, activityEndpoint, token);
	if (!activityResult.ok) {
		return {
			activeBook,
			locale,
			filters,
			overview,
			activity: null,
			returnTo: filters.returnTo,
			resetActivityHref,
			canonicalAccountDetailHref,
			childHrefs,
			transactionHrefs: {},
			transactionExplorerHref: '',
			reportHref: '',
			status: classifyLoadFailure(activityResult.status, locale),
			activityRequestCounters,
			activityEndpoint,
			legacyNotice: filters.legacyKeys.length ? t(locale, 'accounts.detail.legacyNotice') : ''
		};
	}

	const activity = activityResult.body as AccountActivity;
	activity.limitations = sanitizeLimitations(activity.limitations);
	const transactionHrefs = Object.fromEntries(
		activity.recent_transactions.map((tx) => [
			tx.id,
			`/transactions/${encodeURIComponent(tx.id)}?return_to=${encodeURIComponent(canonicalAccountDetailHref)}`
		])
	);
	return {
		activeBook,
		locale,
		filters,
		overview,
		activity,
		returnTo: filters.returnTo,
		resetActivityHref,
		canonicalAccountDetailHref,
		childHrefs,
		transactionHrefs,
		transactionExplorerHref: activity.transaction_explorer_compatible
			? buildAccountTransactionExplorerUrl(filters.accountId, filters.dateFrom, filters.dateTo)
			: '',
		reportHref: buildBaseReportUrl(filters.dateFrom, filters.dateTo),
		status: activityStatus(activity, locale),
		activityRequestCounters,
		activityEndpoint,
		legacyNotice: filters.legacyKeys.length ? t(locale, 'accounts.detail.legacyNotice') : ''
	};
};
