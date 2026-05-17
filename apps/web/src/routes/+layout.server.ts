import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import { localeFromCookie } from '$lib/i18n';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook } = await getActiveBookContext(fetch, cookies, token);

	return {
		authenticated: true,
		pathname: url.pathname,
		locale: localeFromCookie(cookies),
		books,
		activeBook,
		showBookSelector: books.length > 1
	};
};
