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

type PreviewFieldName = keyof CreatePreviewPayload | 'book_id';
type PreviewFieldErrors = Partial<Record<PreviewFieldName, string>>;

type ApiErrorBody = {
	detail?: unknown;
};

type ApiPostResult<T> = {
	ok: boolean;
	status: number;
	body: T | ApiErrorBody;
};

const PREVIEW_ERROR_FALLBACK = 'Preview validation failed safely. No write was executed.';
const PREVIEW_FIELD_ERROR_FALLBACK = 'Invalid value. No write was executed.';

const FIELD_LABELS: Record<PreviewFieldName, string> = {
	book_id: 'book',
	date: 'date',
	debit_account_id: 'source account',
	credit_account_id: 'destination account',
	amount: 'amount',
	currency: 'currency',
	description: 'description',
	memo: 'memo'
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

function safeMessage(value: unknown, fallback = PREVIEW_ERROR_FALLBACK): string {
	if (typeof value !== 'string') return fallback;
	const detail = value.trim();
	if (detail && detail.length <= 180 && !/[\\/]/.test(detail)) {
		return detail;
	}
	return fallback;
}

function fallbackFieldMessage(field: PreviewFieldName): string {
	return `Invalid ${FIELD_LABELS[field]}. No write was executed.`;
}

function fieldFromName(value: unknown): PreviewFieldName | null {
	if (typeof value !== 'string') return null;
	return value in FIELD_LABELS ? (value as PreviewFieldName) : null;
}

function fieldFromLoc(loc: unknown): PreviewFieldName | null {
	if (!Array.isArray(loc)) return null;
	for (let index = loc.length - 1; index >= 0; index -= 1) {
		const field = fieldFromName(loc[index]);
		if (field) return field;
	}
	return null;
}

function addFieldError(errors: PreviewFieldErrors, field: PreviewFieldName, message: string) {
	errors[field] = message;
}

function fieldErrorsFromString(detail: string): PreviewFieldErrors {
	const text = detail.toLowerCase();
	const safeDetail = safeMessage(detail, PREVIEW_FIELD_ERROR_FALLBACK);
	const errors: PreviewFieldErrors = {};
	if (text.includes('debit and credit accounts')) {
		addFieldError(errors, 'debit_account_id', safeDetail);
		addFieldError(errors, 'credit_account_id', safeDetail);
		return errors;
	}
	if (text.includes('debit_account_id') || text.includes('debit account') || text.includes('source account')) {
		addFieldError(errors, 'debit_account_id', safeDetail);
	}
	if (text.includes('credit_account_id') || text.includes('credit account') || text.includes('destination account')) {
		addFieldError(errors, 'credit_account_id', safeDetail);
	}
	if (text.includes('amount')) addFieldError(errors, 'amount', safeDetail);
	if (text.includes('currency')) addFieldError(errors, 'currency', safeDetail);
	if (text.includes('date')) addFieldError(errors, 'date', safeDetail);
	if (text.includes('description')) addFieldError(errors, 'description', safeDetail);
	if (text.includes('memo')) addFieldError(errors, 'memo', safeDetail);
	return errors;
}

function previewErrorDetails(body: unknown): { error: string; fieldErrors: PreviewFieldErrors } {
	const detail = typeof body === 'object' && body !== null && 'detail' in body ? (body as ApiErrorBody).detail : undefined;
	if (typeof detail === 'string') {
		const error = safeMessage(detail);
		return { error, fieldErrors: fieldErrorsFromString(detail) };
	}
	if (Array.isArray(detail)) {
		const fieldErrors: PreviewFieldErrors = {};
		for (const item of detail) {
			if (typeof item !== 'object' || item === null) continue;
			const field = fieldFromLoc('loc' in item ? item.loc : undefined);
			if (!field) continue;
			const message = safeMessage('msg' in item ? item.msg : undefined, fallbackFieldMessage(field));
			addFieldError(fieldErrors, field, message);
		}
		return {
			error: Object.keys(fieldErrors).length
				? 'Preview validation failed safely. Review the highlighted fields. No write was executed.'
				: PREVIEW_ERROR_FALLBACK,
			fieldErrors
		};
	}
	return { error: PREVIEW_ERROR_FALLBACK, fieldErrors: {} };
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
				const { error, fieldErrors } = previewErrorDetails(result.body);
				return {
					error,
					fieldErrors,
					payload,
					previewOnly: true
				};
			}
			return { preview: result.body as TransactionCreatePreview, payload, fieldErrors: {}, previewOnly: true };
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return {
				error: 'API service is unavailable. No write was executed.',
				fieldErrors: {},
				payload,
				previewOnly: true
			};
		}
	}
};
