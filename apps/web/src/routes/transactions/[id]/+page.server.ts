import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { TransactionDetail } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch, params }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);

	const transaction = await apiFetch<TransactionDetail>(
		fetch,
		`${bookPrefix}/transactions/${encodeURIComponent(params.id)}`,
		token
	);

	return { transaction, activeBook };
};
