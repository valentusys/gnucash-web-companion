import { redirect } from '@sveltejs/kit';
import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import { localeFromCookie } from '$lib/i18n';
import type { LayoutServerLoad } from './$types';

function shouldReviewBookContext(pathname: string): boolean {
	return pathname !== '/books' && !pathname.startsWith('/books/');
}

export const load: LayoutServerLoad = async ({ cookies, fetch, locals, url }) => {
	const locale = localeFromCookie(cookies);

	if (!locals.authenticated) {
		return {
			authenticated: false,
			pathname: url.pathname,
			locale,
			books: [],
			activeBook: null,
			showBookSelector: false,
			bookContextRecovery: null
		};
	}

	const token = getAuthToken(cookies);
	const { books, activeBook, recovery } = await getActiveBookContext(fetch, cookies, token);
	if (recovery && shouldReviewBookContext(url.pathname)) {
		throw redirect(303, `/books?book_context=${recovery.reason}`);
	}

	return {
		authenticated: locals.authenticated,
		pathname: url.pathname,
		locale,
		books,
		activeBook,
		showBookSelector: books.length > 1,
		bookContextRecovery: recovery
	};
};
