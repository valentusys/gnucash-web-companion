import { apiFetch, getAuthToken, getActiveBookId } from '$lib/api/server';
import type { AccountTreeNode } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const activeBookId = getActiveBookId(cookies);
	const bookPrefix = activeBookId ? `/books/${activeBookId}` : '';

	const accounts = await apiFetch<AccountTreeNode[]>(fetch, `${bookPrefix}/accounts/tree`, token);

	return { accounts };
};
