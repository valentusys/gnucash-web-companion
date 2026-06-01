import { fail } from '@sveltejs/kit';
import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { Actions, PageServerLoad } from './$types';

const BOOK_CONTEXT_NOTICE_KEYS = new Set([
	'invalid_selected_book_cookie',
	'stale_selected_book_cookie',
	'no_accessible_books',
	'unavailable_selected_book'
]);

function redactedApiError(payload: unknown): string {
	if (payload && typeof payload === 'object' && 'detail' in payload) {
		const detail = (payload as { detail: unknown }).detail;
		if (typeof detail === 'string') return detail;
	}
	return 'Book registry metadata update failed. Check the mounted copied/test book path on the host.';
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, recovery } = await getActiveBookContext(fetch, cookies, token);
	const queryNotice = url.searchParams.get('book_context');
	const bookContextNotice = BOOK_CONTEXT_NOTICE_KEYS.has(queryNotice ?? '')
		? queryNotice
		: recovery?.reason ?? null;

	return {
		books,
		activeBook,
		bookContextNotice
	};
};

async function postBookManagementAction(
	fetch: typeof globalThis.fetch,
	token: string | null,
	path: string,
	method: 'POST' | 'DELETE'
): Promise<{ ok: true; payload: unknown } | { ok: false; status: number; message: string }> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	try {
		const response = await fetch(`${apiBase}${path}`, {
			method,
			headers: {
				authorization: `Bearer ${token}`
			}
		});
		if (!response.ok) {
			let payload: unknown = null;
			try {
				payload = await response.json();
			} catch {
				payload = null;
			}
			return { ok: false, status: response.status, message: redactedApiError(payload) };
		}
		return { ok: true, payload: await response.json() };
	} catch {
		return {
			ok: false,
			status: 502,
			message: 'API service is unavailable. No book registry metadata was changed.'
		};
	}
}

export const actions: Actions = {
	registerBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const name = String(form.get('name') ?? '').trim();
		const uriOrPath = String(form.get('mounted_path') ?? '').trim();
		const baseCurrency = String(form.get('base_currency') ?? '').trim();
		const makeDefault = form.get('make_default') === 'on';

		if (!name || !uriOrPath) {
			return fail(400, {
				registerError: 'Book name and mounted local SQLite path are required.',
				registerName: name,
				registerBaseCurrency: baseCurrency
			});
		}

		const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
		let response: Response;
		try {
			response = await fetch(`${apiBase}/books`, {
				method: 'POST',
				headers: {
					authorization: `Bearer ${token}`,
					'content-type': 'application/json'
				},
				body: JSON.stringify({
					name,
					storage_type: 'sqlite',
					uri_or_path: uriOrPath,
					base_currency: baseCurrency || null,
					make_default: makeDefault
				})
			});
		} catch {
			return fail(502, {
				registerError: 'API service is unavailable. No book metadata was registered.',
				registerName: name,
				registerBaseCurrency: baseCurrency
			});
		}

		if (!response.ok) {
			let payload: unknown = null;
			try {
				payload = await response.json();
			} catch {
				payload = null;
			}
			return fail(response.status, {
				registerError: redactedApiError(payload),
				registerName: name,
				registerBaseCurrency: baseCurrency
			});
		}

		const registered = (await response.json()) as { name?: string };
		return {
			registerSuccess: `Registered ${registered.name ?? 'book'} in app metadata only. No GnuCash accounting data was changed.`
		};
	},
	setDefaultBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { manageError: 'Book registry metadata update failed.' });
		}
		const result = await postBookManagementAction(fetch, token, `/books/${bookId}/default`, 'POST');
		if (!result.ok) return fail(result.status, { manageError: result.message });
		const book = result.payload as { name?: string };
		return {
			manageSuccess: `Set ${book.name ?? 'book'} as the default metadata entry. No GnuCash accounting data was changed.`
		};
	},
	removeBook: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const bookId = Number(form.get('book_id'));
		if (!Number.isInteger(bookId) || bookId <= 0) {
			return fail(400, { manageError: 'Book registry metadata update failed.' });
		}
		const result = await postBookManagementAction(fetch, token, `/books/${bookId}`, 'DELETE');
		if (!result.ok) return fail(result.status, { manageError: result.message });
		cookies.delete('selected_book_id', { path: '/' });
		return {
			manageSuccess: 'Removed the book from the app registry only. The underlying GnuCash file was not deleted.'
		};
	}
};
