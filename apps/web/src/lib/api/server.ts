import { error, redirect, type Cookies } from '@sveltejs/kit';
import type { Book, CurrentUser } from '$lib/api/types';

const SELECTED_BOOK_COOKIE = 'selected_book_id';
const SELECTED_BOOK_MAX_AGE = 60 * 60 * 24 * 30;

export type BookContextRecoveryReason =
	| 'invalid_selected_book_cookie'
	| 'stale_selected_book_cookie'
	| 'unavailable_selected_book'
	| 'no_accessible_books';

export type BookContextRecovery = {
	reason: BookContextRecoveryReason;
	selectedBookId: number | null;
	activeBookId: number | null;
};

export type ActiveBookContext = {
	books: Book[];
	activeBook: Book | null;
	bookPrefix: string;
	recovery: BookContextRecovery | null;
};

type SelectedBookCookieState = {
	selectedBookId: number | null;
	invalid: boolean;
};

export function getAuthToken(cookies: Cookies): string {
	const token = cookies.get('access_token');
	if (!token) {
		throw redirect(303, '/login');
	}
	return token;
}

export async function getCurrentUser(fetchFn: typeof fetch, token: string): Promise<CurrentUser> {
	return apiFetch<CurrentUser>(fetchFn, '/auth/me', token);
}

export function isCurrentUserAdmin(user: CurrentUser | null): boolean {
	return user?.is_admin === true;
}

function getSelectedBookCookieState(cookies: Cookies): SelectedBookCookieState {
	const raw = cookies.get(SELECTED_BOOK_COOKIE) ?? null;
	if (!raw) return { selectedBookId: null, invalid: false };
	const parsed = Number(raw);
	if (!Number.isInteger(parsed) || parsed <= 0) {
		return { selectedBookId: null, invalid: true };
	}
	return { selectedBookId: parsed, invalid: false };
}

export function getActiveBookId(cookies: Cookies): number | null {
	return getSelectedBookCookieState(cookies).selectedBookId;
}

export function resolveActiveBook(books: Book[], selectedBookId: number | null): Book | null {
	const openableBooks = books.filter((book) => book.can_open_read_only_views);
	return (
		openableBooks.find((book) => book.id === selectedBookId) ??
		openableBooks.find((book) => book.is_default) ??
		openableBooks[0] ??
		null
	);
}

export async function getActiveBookContext(
	fetchFn: typeof fetch,
	cookies: Cookies,
	token: string
): Promise<ActiveBookContext> {
	const books = await apiFetch<Book[]>(fetchFn, '/books', token);
	const selectedCookie = getSelectedBookCookieState(cookies);
	const activeBook = resolveActiveBook(books, selectedCookie.selectedBookId);
	let recovery: BookContextRecovery | null = null;

	if (selectedCookie.invalid) {
		recovery = {
			reason: 'invalid_selected_book_cookie',
			selectedBookId: null,
			activeBookId: activeBook?.id ?? null
		};
	} else if (
		selectedCookie.selectedBookId !== null &&
		books.some((book) => book.id === selectedCookie.selectedBookId && !book.can_open_read_only_views)
	) {
		recovery = {
			reason: 'unavailable_selected_book',
			selectedBookId: selectedCookie.selectedBookId,
			activeBookId: activeBook?.id ?? null
		};
	} else if (selectedCookie.selectedBookId !== null && activeBook?.id !== selectedCookie.selectedBookId) {
		recovery = {
			reason: 'stale_selected_book_cookie',
			selectedBookId: selectedCookie.selectedBookId,
			activeBookId: activeBook?.id ?? null
		};
	} else if (books.length === 0 || !activeBook) {
		recovery = {
			reason: 'no_accessible_books',
			selectedBookId: selectedCookie.selectedBookId,
			activeBookId: null
		};
	}

	if (recovery) {
		if (activeBook) {
			cookies.set(SELECTED_BOOK_COOKIE, String(activeBook.id), {
				path: '/',
				maxAge: SELECTED_BOOK_MAX_AGE,
				sameSite: 'lax'
			});
		} else {
			cookies.delete(SELECTED_BOOK_COOKIE, { path: '/' });
		}
	}

	return {
		books,
		activeBook,
		bookPrefix: activeBook ? `/books/${activeBook.id}` : '',
		recovery
	};
}

export async function apiFetch<T>(
	fetchFn: typeof fetch,
	path: string,
	token: string
): Promise<T> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	let response: Response;
	try {
		response = await fetchFn(`${apiBase}${path}`, {
			headers: { authorization: `Bearer ${token}` }
		});
	} catch {
		throw error(502, 'API service is unavailable.');
	}

	if (response.status === 401) {
		throw redirect(303, '/login');
	}
	if (response.status === 403) {
		throw error(403, 'You do not have access to this book.');
	}
	if (response.status === 404) {
		throw error(404, 'Requested item was not found.');
	}
	if (response.status === 503) {
		throw error(503, 'GnuCash book is not configured or cannot be read.');
	}
	if (!response.ok) {
		throw error(response.status, 'API request failed.');
	}
	return (await response.json()) as T;
}
