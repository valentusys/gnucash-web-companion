import { error, fail, redirect } from '@sveltejs/kit';
import {
	apiFetch,
	apiMutationFetch,
	clearSelectedBookCookieIfMatches,
	getAuthToken,
	getCurrentUser,
	isCurrentUserAdmin
} from '$lib/api/server';
import type { Book, BookPreflightRequest, BookPreflightResponse, TransactionCreateSettings } from '$lib/api/types';
import type { Actions, PageServerLoad } from './$types';

type LifecycleSuccessCode = 'recheck' | 'rename' | 'set_default' | 'disable' | 'enable' | 'transaction_create_settings';

const FALLBACK_TRANSACTION_CREATE_SETTINGS: TransactionCreateSettings = {
	enabled: false,
	effective_enabled: false,
	deployment_writes_enabled: false,
	user_can_create: false,
	create_generation: 1,
	recovery_required: false,
	reason_key: 'CREATE_DEPLOYMENT_DISABLED'
};

function bookIdFromParams(params: { bookId?: string }): number {
	const bookId = Number(params.bookId);
	if (!Number.isInteger(bookId) || bookId <= 0) {
		throw error(404, 'Requested item was not found.');
	}
	return bookId;
}

function textField(form: FormData, name: string): string {
	return String(form.get(name) ?? '').trim();
}

function enablePreflightRequest(book: Book, mountedPath: string, makeDefault: boolean): BookPreflightRequest {
	return {
		name: book.name,
		storage_type: 'sqlite',
		uri_or_path: mountedPath,
		base_currency: String(book.base_currency ?? '').trim().toUpperCase(),
		make_default: makeDefault
	};
}

async function loadBook(fetchFn: typeof globalThis.fetch, token: string, bookId: number): Promise<Book> {
	return apiFetch<Book>(fetchFn, `/books/${bookId}`, token);
}

async function loadTransactionCreateSettings(
	fetchFn: typeof globalThis.fetch,
	token: string,
	bookId: number
): Promise<TransactionCreateSettings> {
	try {
		return await apiFetch<TransactionCreateSettings>(fetchFn, `/books/${bookId}/transaction-create-settings`, token);
	} catch {
		return FALLBACK_TRANSACTION_CREATE_SETTINGS;
	}
}

export const load: PageServerLoad = async ({ cookies, fetch, params }) => {
	const bookId = bookIdFromParams(params);
	const token = getAuthToken(cookies);
	const [book, currentUser, transactionCreateSettings] = await Promise.all([
		loadBook(fetch, token, bookId),
		getCurrentUser(fetch, token),
		loadTransactionCreateSettings(fetch, token, bookId)
	]);
	return {
		book,
		isAdmin: isCurrentUserAdmin(currentUser),
		transactionCreateSettings
	};
};

export const actions: Actions = {
	recheckHealth: async ({ cookies, fetch, params }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const result = await apiMutationFetch(fetch, token, `/books/${bookId}/health/recheck`, 'POST');
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		return { lifecycleSuccessCode: 'recheck' satisfies LifecycleSuccessCode };
	},
	renameBook: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const name = textField(form, 'name');
		const baseCurrency = textField(form, 'base_currency').toUpperCase();
		if (!name || !baseCurrency) {
			return fail(400, { lifecycleErrorCode: 'book_registry_failed' });
		}
		const result = await apiMutationFetch<Book>(fetch, token, `/books/${bookId}`, 'PATCH', {
			name,
			base_currency: baseCurrency
		});
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		return { lifecycleSuccessCode: 'rename' satisfies LifecycleSuccessCode };
	},
	setDefaultBook: async ({ cookies, fetch, params }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const result = await apiMutationFetch<Book>(fetch, token, `/books/${bookId}/default`, 'POST');
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		return { lifecycleSuccessCode: 'set_default' satisfies LifecycleSuccessCode };
	},
	patchTransactionCreateSettings: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const enabled = textField(form, 'enabled') === 'true';
		const result = await apiMutationFetch<TransactionCreateSettings>(
			fetch,
			token,
			`/books/${bookId}/transaction-create-settings`,
			'PATCH',
			{ enabled }
		);
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		return {
			lifecycleSuccessCode: 'transaction_create_settings' satisfies LifecycleSuccessCode,
			transactionCreateSettings: result.payload
		};
	},
	disableBook: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		if (form.get('confirm_metadata_only') !== 'on') {
			return fail(400, { lifecycleErrorCode: 'preflight_required' });
		}
		const result = await apiMutationFetch<Book>(fetch, token, `/books/${bookId}/disable`, 'POST');
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		clearSelectedBookCookieIfMatches(cookies, bookId);
		return { lifecycleSuccessCode: 'disable' satisfies LifecycleSuccessCode };
	},
	enablePreflight: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const mountedPath = textField(form, 'mounted_path');
		const makeDefault = form.get('make_default') === 'on';
		if (!mountedPath) {
			return fail(400, {
				enablePreflightErrorCode: 'preflight_required',
				enableMakeDefault: makeDefault
			});
		}
		const book = await loadBook(fetch, token, bookId);
		const result = await apiMutationFetch<BookPreflightResponse>(
			fetch,
			token,
			'/books/preflight',
			'POST',
			enablePreflightRequest(book, mountedPath, makeDefault)
		);
		if (!result.ok) {
			return fail(result.status, {
				enablePreflightErrorCode: result.message,
				enableMakeDefault: makeDefault
			});
		}
		return {
			enablePreflight: result.payload,
			enableMakeDefault: makeDefault
		};
	},
	enableBook: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const preflightToken = textField(form, 'preflight_token');
		const makeDefault = form.get('make_default') === 'on';
		if (!preflightToken) {
			return fail(400, {
				lifecycleErrorCode: 'missing_preflight_token',
				enableMakeDefault: makeDefault
			});
		}
		const result = await apiMutationFetch<Book>(fetch, token, `/books/${bookId}/enable`, 'POST', {
			preflight_token: preflightToken,
			make_default: makeDefault
		});
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		return { lifecycleSuccessCode: 'enable' satisfies LifecycleSuccessCode };
	},
	removeBook: async ({ cookies, fetch, params, request }) => {
		const bookId = bookIdFromParams(params);
		const token = getAuthToken(cookies);
		const form = await request.formData();
		if (form.get('confirm_metadata_only') !== 'on') {
			return fail(400, { lifecycleErrorCode: 'preflight_required' });
		}
		const result = await apiMutationFetch(fetch, token, `/books/${bookId}`, 'DELETE');
		if (!result.ok) return fail(result.status, { lifecycleErrorCode: result.message });
		clearSelectedBookCookieIfMatches(cookies, bookId);
		throw redirect(303, '/books?manage_success=remove_registry');
	}
};
