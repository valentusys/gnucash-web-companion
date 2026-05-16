import { env } from '$env/dynamic/private';
import { redirect, type Actions } from '@sveltejs/kit';
import { apiFetch, getAuthToken } from '$lib/api/server';
import type {
	Account,
	Book,
	TransactionValidationResult,
	TransactionWriteResult
} from '$lib/api/types';
import type { PageServerLoad } from './$types';

type SplitPayload = {
	account_id: string;
	amount: string;
	currency: string;
	memo: string;
};

type CreatePayload = {
	date: string;
	description: string;
	splits: SplitPayload[];
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

function detailMessage(body: unknown): string {
	if (typeof body === 'object' && body !== null && 'detail' in body && typeof body.detail === 'string') {
		return body.detail;
	}
	return 'API request failed.';
}

function formToPayload(formData: FormData): CreatePayload {
	const amount = String(formData.get('amount') ?? '').trim();
	const currency = String(formData.get('currency') ?? 'SEK').trim().toUpperCase();
	return {
		date: String(formData.get('date') ?? '').trim(),
		description: String(formData.get('description') ?? '').trim(),
		splits: [
			{
				account_id: String(formData.get('from_account_id') ?? '').trim(),
				amount: amount ? `-${amount.replace(/^-/, '')}` : '',
				currency,
				memo: String(formData.get('from_memo') ?? '')
			},
			{
				account_id: String(formData.get('to_account_id') ?? '').trim(),
				amount: amount ? amount.replace(/^-/, '') : '',
				currency,
				memo: String(formData.get('to_memo') ?? '')
			}
		]
	};
}

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	if (env.GNUCASH_WRITES_ENABLED !== 'true') {
		throw redirect(303, '/transactions');
	}
	const token = getAuthToken(cookies);
	const [books, accounts] = await Promise.all([
		apiFetch<Book[]>(fetch, '/books', token),
		apiFetch<Account[]>(fetch, '/accounts', token)
	]);
	return {
		books,
		accounts: accounts.filter((account) => !account.placeholder && !account.hidden),
		activeBook: books.find((book) => book.is_default) ?? books[0] ?? null
	};
};

export const actions: Actions = {
	validate: async ({ cookies, fetch, request }) => {
		if (env.GNUCASH_WRITES_ENABLED !== 'true') {
			return { error: 'GnuCash writes are disabled. MVP v0.1 is read-only by default.' };
		}
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		const bookId = String(formData.get('book_id') ?? '');
		const payload = formToPayload(formData);
		try {
			const result = await apiPost<TransactionValidationResult>(
				fetch,
				`/books/${bookId}/transactions/validate`,
				token,
				payload
			);
			if (!result.ok) {
				return { error: detailMessage(result.body), payload };
			}
			return { validation: result.body as TransactionValidationResult, payload };
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return { error: 'API service is unavailable.', payload };
		}
	},
	create: async ({ cookies, fetch, request }) => {
		if (env.GNUCASH_WRITES_ENABLED !== 'true') {
			return { error: 'GnuCash writes are disabled. MVP v0.1 is read-only by default.' };
		}
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		const bookId = String(formData.get('book_id') ?? '');
		const payload = formToPayload(formData);
		try {
			const validationResult = await apiPost<TransactionValidationResult>(
				fetch,
				`/books/${bookId}/transactions/validate`,
				token,
				payload
			);
			if (!validationResult.ok) {
				return { error: detailMessage(validationResult.body), payload };
			}
			const validation = validationResult.body as TransactionValidationResult;
			if (!validation.valid) return { validation, payload };

			const createResult = await apiPost<TransactionWriteResult>(
				fetch,
				`/books/${bookId}/transactions`,
				token,
				payload
			);
			if (!createResult.ok) return { error: detailMessage(createResult.body), validation, payload };
			const result = createResult.body as TransactionWriteResult;
			throw redirect(303, `/transactions/${encodeURIComponent(result.transaction_id)}`);
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return { error: 'API service is unavailable.', payload };
		}
	}
};
