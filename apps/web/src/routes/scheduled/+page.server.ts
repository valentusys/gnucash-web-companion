import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { ScheduledTransaction } from '$lib/api/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const scheduledTransactions = activeBook
		? await apiFetch<ScheduledTransaction[]>(fetch, `${bookPrefix}/scheduled-transactions`, token)
		: [];

	return {
		books,
		activeBook,
		scheduledTransactions
	};
};
