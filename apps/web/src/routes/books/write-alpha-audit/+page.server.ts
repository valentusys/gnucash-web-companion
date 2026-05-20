import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { WriteAlphaAuditSummary } from '$lib/api/types';
import type { PageServerLoad } from './$types';

const SAFE_ACTIONS = new Set(['transaction.create', 'transaction.patch', 'transaction.delete']);
const SAFE_RESULTS = new Set(['started', 'success', 'failed', 'unknown']);
const DEFAULT_LIMIT = 25;
const MAX_LIMIT = 100;
const MAX_OFFSET = 10000;

function safeParam(searchParams: URLSearchParams, key: string, allowed?: Set<string>): string | null {
	const value = searchParams.get(key)?.trim() ?? '';
	if (!value || value.length > 40 || value.includes('/') || value.includes('\\')) {
		return null;
	}
	if (allowed && !allowed.has(value)) {
		return null;
	}
	return value;
}

function safeIntegerParam(searchParams: URLSearchParams, key: string, fallback: number, min: number, max: number): number {
	const value = searchParams.get(key)?.trim() ?? '';
	if (!/^\d+$/.test(value)) {
		return fallback;
	}
	const parsed = Number(value);
	if (!Number.isSafeInteger(parsed) || parsed < min || parsed > max) {
		return fallback;
	}
	return parsed;
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const limit = safeIntegerParam(url.searchParams, 'limit', DEFAULT_LIMIT, 1, MAX_LIMIT);
	const offset = safeIntegerParam(url.searchParams, 'offset', 0, 0, MAX_OFFSET);
	const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
	const action = safeParam(url.searchParams, 'action', SAFE_ACTIONS);
	const result = safeParam(url.searchParams, 'result', SAFE_RESULTS);
	const since = safeParam(url.searchParams, 'since');
	const until = safeParam(url.searchParams, 'until');
	if (action) params.set('action', action);
	if (result) params.set('result', result);
	if (since) params.set('since', since);
	if (until) params.set('until', until);
	const auditSummary = activeBook
		? await apiFetch<WriteAlphaAuditSummary>(
				fetch,
				`${bookPrefix}/write-alpha-audit-summary?${params.toString()}`,
				token
			)
		: null;

	return {
		books,
		activeBook,
		auditSummary,
		filters: { action, result, since, until, limit, offset }
	};
};
