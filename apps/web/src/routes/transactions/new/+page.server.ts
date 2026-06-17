import { env } from '$env/dynamic/private';
import { redirect, type Actions } from '@sveltejs/kit';
import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { Account, TransactionCreatePreview } from '$lib/api/types';
import type { PageServerLoad } from './$types';

type CreatePreviewPayload = {
	date: string;
	debit_account_id: string;
	credit_account_id: string;
	amount: string;
	currency: string;
	description: string;
	memo: string;
};

type ApiPostResult<T> = {
	ok: boolean;
	status: number;
	body: T | { detail?: unknown };
};

async function apiPost<T>(fetchFn: typeof fetch, path: string, token: string, payload: unknown): Promise<ApiPostResult<T>> {
	const apiBase = env.API_INTERNAL_URL ?? 'http://localhost:8000';
	const response = await fetchFn(`${apiBase}${path}`, {
		method: 'POST',
		headers: {
			'content-type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(payload)
	});

	if (response.status === 401) throw redirect(303, '/login');
	const body = await response.json().catch(() => ({}));
	return { ok: response.ok, status: response.status, body };
}

function detailMessage(body: unknown, fallback = 'Preview validation failed safely. No write was executed.'): string {
	if (typeof body === 'object' && body !== null && 'detail' in body && typeof body.detail === 'string') {
		const detail = body.detail.trim();
		if (detail && detail.length <= 180 && !/[\\/]/.test(detail)) {
			return detail;
		}
	}
	return fallback;
}

function formToPreviewPayload(formData: FormData): CreatePreviewPayload {
	return {
		date: String(formData.get('date') ?? '').trim(),
		debit_account_id: String(formData.get('debit_account_id') ?? '').trim(),
		credit_account_id: String(formData.get('credit_account_id') ?? '').trim(),
		amount: String(formData.get('amount') ?? '').trim(),
		currency: String(formData.get('currency') ?? '').trim().toUpperCase(),
		description: String(formData.get('description') ?? '').trim(),
		memo: String(formData.get('memo') ?? '')
	};
}

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const accounts = activeBook ? await apiFetch<Account[]>(fetch, `${bookPrefix}/accounts`, token) : [];
	return {
		books,
		accounts: accounts.filter((account) => !account.placeholder && !account.hidden),
		activeBook,
		previewOnly: true
	};
};

export const actions: Actions = {
	preview: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		const bookId = String(formData.get('book_id') ?? '');
		const payload = formToPreviewPayload(formData);
		try {
			const result = await apiPost<TransactionCreatePreview>(
				fetch,
				`/books/${bookId}/transactions/create-preview`,
				token,
				payload
			);
			if (!result.ok) {
				return {
					error: detailMessage(result.body),
					payload,
					previewOnly: true
				};
			}
			return { preview: result.body as TransactionCreatePreview, payload, previewOnly: true };
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return { error: 'API service is unavailable. No write was executed.', payload, previewOnly: true };
		}
	}
};
