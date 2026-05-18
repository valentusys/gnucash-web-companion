import { error, redirect } from '@sveltejs/kit';
import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { RequestHandler } from './$types';

const SELECTED_BOOK_MAX_AGE = 60 * 60 * 24 * 30;
const SAFE_NEXT_PATHS = ['/dashboard', '/accounts', '/transactions', '/scheduled'];

function normalizeNext(rawNext: string | null): string {
	if (!rawNext) return '/dashboard';
	return SAFE_NEXT_PATHS.includes(rawNext) ? rawNext : '/dashboard';
}

export const GET: RequestHandler = async ({ cookies, fetch, params, url }) => {
	const bookId = Number(params.bookId);
	if (!Number.isInteger(bookId) || bookId <= 0) {
		throw error(404, 'Requested item was not found.');
	}

	const token = getAuthToken(cookies);
	const { books } = await getActiveBookContext(fetch, cookies, token);
	const selectedBook = books.find((book) => book.id === bookId);
	if (!selectedBook) {
		throw error(404, 'Requested item was not found.');
	}

	cookies.set('selected_book_id', String(selectedBook.id), {
		path: '/',
		maxAge: SELECTED_BOOK_MAX_AGE,
		sameSite: 'lax'
	});

	throw redirect(303, normalizeNext(url.searchParams.get('next')));
};
