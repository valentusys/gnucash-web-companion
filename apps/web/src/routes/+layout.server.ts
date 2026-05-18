import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import { localeFromCookie } from '$lib/i18n';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, locals, url }) => {
	const locale = localeFromCookie(cookies);

	if (!locals.authenticated) {
		return {
			authenticated: false,
			pathname: url.pathname,
			locale,
			books: [],
			activeBook: null,
			showBookSelector: false
		};
	}

	const token = getAuthToken(cookies);
	const { books, activeBook } = await getActiveBookContext(fetch, cookies, token);

	return {
		authenticated: locals.authenticated,
		pathname: url.pathname,
		locale,
		books,
		activeBook,
		showBookSelector: books.length > 1
	};
};
