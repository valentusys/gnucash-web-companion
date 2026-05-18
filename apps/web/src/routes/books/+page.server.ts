import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook } = await getActiveBookContext(fetch, cookies, token);

	return {
		books,
		activeBook
	};
};
