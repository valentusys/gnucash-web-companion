import { error, redirect } from '@sveltejs/kit';
import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { RequestHandler } from './$types';

const SELECTED_BOOK_MAX_AGE = 60 * 60 * 24 * 30;
const SAFE_NEXT_PATHS = ['/dashboard', '/accounts', '/transactions', '/reports', '/scheduled'];

function isSafeNextPath(pathname: string): boolean {
	return SAFE_NEXT_PATHS.some((safePath) => pathname === safePath || pathname.startsWith(`${safePath}/`));
}

function normalizeNext(rawNext: string | null): string {
	if (!rawNext) return '/dashboard';
	try {
		const parsed = new URL(rawNext, 'http://localhost');
		if (parsed.origin !== 'http://localhost' || !isSafeNextPath(parsed.pathname)) {
			return '/dashboard';
		}
		return `${parsed.pathname}${parsed.search}`;
	} catch {
		return '/dashboard';
	}
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
	if (!selectedBook.can_open_read_only_views) {
		throw redirect(303, '/books?book_context=unavailable_selected_book');
	}

	cookies.set('selected_book_id', String(selectedBook.id), {
		path: '/',
		maxAge: SELECTED_BOOK_MAX_AGE,
		sameSite: 'lax'
	});

	throw redirect(303, normalizeNext(url.searchParams.get('next')));
};
