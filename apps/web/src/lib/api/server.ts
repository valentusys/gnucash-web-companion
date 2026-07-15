import { error, isRedirect, redirect, type Cookies } from '@sveltejs/kit';
import type { AdminProblemCode, Book, BookProblemCode, CurrentUser } from '$lib/api/types';

const AUTH_COOKIE = 'access_token';
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

type ActiveBookContextOptions = {
	includeUnavailableBooks?: boolean;
};

type SelectedBookCookieState = {
	selectedBookId: number | null;
	invalid: boolean;
};

type ApiMutationMethod = 'POST' | 'PATCH' | 'PUT' | 'DELETE';

export type ApiMutationResult<T> =
	| { ok: true; payload: T }
	| { ok: false; status: number; message: BookProblemCode };

export type AdminApiMutationResult<T> =
	| { ok: true; payload: T }
	| { ok: false; status: number; message: AdminProblemCode };

const allowedBookProblemCodes = new Set<BookProblemCode>([
	'admin_required',
	'preflight_required',
	'preflight_rejected',
	'preflight_token_invalid',
	'missing_preflight_token',
	'invalid_preflight_token',
	'preflight_request_mismatch',
	'preflight_source_mismatch',
	'invalid_path',
	'unsupported_source',
	'outside_allowed_roots',
	'symlink_forbidden',
	'missing_file',
	'not_regular_file',
	'permission_denied',
	'unsupported_format',
	'invalid_gnucash_schema',
	'source_changed',
	'open_failed',
	'duplicate_canonical_path',
	'book_not_enabled',
	'book_not_healthy',
	'book_health_not_checked',
	'api_unavailable',
	'book_registry_failed',
	'unknown_book_problem'
]);

const allowedAdminProblemCodes = new Set<AdminProblemCode>([
	'username_invalid',
	'username_taken',
	'display_name_invalid',
	'password_policy',
	'user_not_found',
	'user_disabled',
	'session_changed',
	'self_disable_forbidden',
	'last_enabled_admin',
	'book_not_assignable',
	'admin_required',
	'api_unavailable',
	'unknown_admin_problem'
]);

export function clearAuthSessionCookies(cookies: Cookies): void {
	cookies.delete(AUTH_COOKIE, { path: '/' });
	cookies.delete(SELECTED_BOOK_COOKIE, { path: '/' });
}

export function redirectToSessionChanged(cookies: Cookies): never {
	clearAuthSessionCookies(cookies);
	throw redirect(303, '/login?reason=session_changed');
}

export function fixedBookProblemCode(payload: unknown, fallback: BookProblemCode): BookProblemCode {
	let candidate: unknown = null;
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		candidate = record.safe_code ?? record.code;
		if (!candidate && record.detail && typeof record.detail === 'object') {
			const detail = record.detail as Record<string, unknown>;
			candidate = detail.safe_code ?? detail.code;
		}
	}
	return typeof candidate === 'string' && allowedBookProblemCodes.has(candidate as BookProblemCode)
		? (candidate as BookProblemCode)
		: fallback;
}

export function fixedAdminProblemCode(payload: unknown, fallback: AdminProblemCode): AdminProblemCode {
	let candidate: unknown = null;
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		candidate = record.safe_code ?? record.code;
		if (!candidate && record.detail && typeof record.detail === 'object') {
			const detail = record.detail as Record<string, unknown>;
			candidate = detail.safe_code ?? detail.code;
		}
	}
	if (candidate === 'book_not_found') return 'book_not_assignable';
	return typeof candidate === 'string' && allowedAdminProblemCodes.has(candidate as AdminProblemCode)
		? (candidate as AdminProblemCode)
		: fallback;
}

function fallbackAdminProblemCode(status: number): AdminProblemCode {
	if (status === 401) return 'session_changed';
	if (status === 403) return 'admin_required';
	if (status === 404) return 'user_not_found';
	if (status === 409) return 'username_taken';
	if (status === 422) return 'display_name_invalid';
	return 'unknown_admin_problem';
}

async function safeJson(response: Response): Promise<unknown> {
	try {
		return await response.json();
	} catch {
		return null;
	}
}

export function getAuthToken(cookies: Cookies): string {
	const token = cookies.get(AUTH_COOKIE);
	if (!token) {
		throw redirect(303, '/login');
	}
	return token;
}

export async function getCurrentUser(
	fetchFn: typeof fetch,
	token: string,
	cookies?: Cookies
): Promise<CurrentUser> {
	return apiFetch<CurrentUser>(fetchFn, '/auth/me', token, cookies);
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

export function clearSelectedBookCookieIfMatches(cookies: Cookies, bookId: number): void {
	const selected = getSelectedBookCookieState(cookies).selectedBookId;
	if (selected === bookId) {
		cookies.delete(SELECTED_BOOK_COOKIE, { path: '/' });
	}
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
	token: string,
	options: ActiveBookContextOptions = {}
): Promise<ActiveBookContext> {
	const apiBooks = await apiFetch<Book[]>(fetchFn, '/books', token, cookies);
	const openableBooks = apiBooks.filter((book) => book.can_open_read_only_views);
	const selectedCookie = getSelectedBookCookieState(cookies);
	const activeBook = resolveActiveBook(apiBooks, selectedCookie.selectedBookId);
	let recovery: BookContextRecovery | null = null;

	if (selectedCookie.invalid) {
		recovery = {
			reason: 'invalid_selected_book_cookie',
			selectedBookId: null,
			activeBookId: activeBook?.id ?? null
		};
	} else if (
		selectedCookie.selectedBookId !== null &&
		apiBooks.some((book) => book.id === selectedCookie.selectedBookId && !book.can_open_read_only_views)
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
	} else if (openableBooks.length === 0 || !activeBook) {
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
	const books = options.includeUnavailableBooks
		? recovery?.selectedBookId
			? apiBooks.filter((book) => book.id !== recovery.selectedBookId || book.can_open_read_only_views)
			: apiBooks
		: openableBooks;

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
	token: string,
	sessionCookies?: Cookies
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
		if (sessionCookies) {
			redirectToSessionChanged(sessionCookies);
		}
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

export async function apiMutationFetch<T>(
	fetchFn: typeof fetch,
	token: string,
	path: string,
	method: ApiMutationMethod,
	body?: Record<string, unknown>
): Promise<ApiMutationResult<T>> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	const headers: Record<string, string> = {
		authorization: `Bearer ${token}`
	};
	if (body !== undefined) {
		headers['content-type'] = 'application/json';
	}
	try {
		const response = await fetchFn(`${apiBase}${path}`, {
			method,
			headers,
			body: body !== undefined ? JSON.stringify(body) : undefined
		});
		const payload = await safeJson(response);
		if (!response.ok) {
			return {
				ok: false,
				status: response.status,
				message: fixedBookProblemCode(
					payload,
					response.status === 403 ? 'admin_required' : 'book_registry_failed'
				)
			};
		}
		return { ok: true, payload: payload as T };
	} catch {
		return {
			ok: false,
			status: 502,
			message: 'api_unavailable'
		};
	}
}

export async function adminApiMutationFetch<T>(
	fetchFn: typeof fetch,
	token: string,
	path: string,
	method: ApiMutationMethod,
	body?: Record<string, unknown>,
	sessionCookies?: Cookies
): Promise<AdminApiMutationResult<T>> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	const headers: Record<string, string> = {
		authorization: `Bearer ${token}`
	};
	if (body !== undefined) {
		headers['content-type'] = 'application/json';
	}
	try {
		const response = await fetchFn(`${apiBase}${path}`, {
			method,
			headers,
			body: body !== undefined ? JSON.stringify(body) : undefined
		});
		const payload = await safeJson(response);
		if (!response.ok) {
			const message = fixedAdminProblemCode(payload, fallbackAdminProblemCode(response.status));
			if (sessionCookies && (response.status === 401 || message === 'session_changed')) {
				redirectToSessionChanged(sessionCookies);
			}
			return {
				ok: false,
				status: response.status,
				message
			};
		}
		return { ok: true, payload: payload as T };
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		return {
			ok: false,
			status: 502,
			message: 'api_unavailable'
		};
	}
}
