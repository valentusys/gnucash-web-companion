import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { WriteAlphaAuditSummary } from '$lib/api/types';
import type { PageServerLoad } from './$types';

const SAFE_ACTIONS = new Set(['transaction.create', 'transaction.patch', 'transaction.delete']);
const SAFE_RESULTS = new Set(['started', 'success', 'failed', 'unknown']);

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

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const params = new URLSearchParams({ limit: '25' });
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
		filters: { action, result, since, until }
	};
};
