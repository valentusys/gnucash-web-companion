import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { AccountTreeNode } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);

	const accounts = await apiFetch<AccountTreeNode[]>(fetch, `${bookPrefix}/accounts/tree`, token);

	return { accounts, activeBook };
};
