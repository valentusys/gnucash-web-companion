import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { WriteAlphaAuditSummary } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const auditSummary = activeBook
		? await apiFetch<WriteAlphaAuditSummary>(
				fetch,
				`${bookPrefix}/write-alpha-audit-summary?limit=25`,
				token
			)
		: null;

	return {
		books,
		activeBook,
		auditSummary
	};
};
