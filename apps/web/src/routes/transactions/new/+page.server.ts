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

type PreviewFormPayload = CreatePreviewPayload & { book_id: string };
type PreviewFieldName = keyof PreviewFormPayload;
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

function friendlyFieldMessage(field: PreviewFieldName, detail: unknown): string {
	const text = typeof detail === 'string' ? detail.toLowerCase() : '';
	if (field === 'book_id') {
		if (text.includes('no selectable accounts')) {
			return 'No selectable accounts are available for this book. Choose another book or add non-placeholder accounts in GnuCash Desktop. No write was executed.';
		}
		return 'Select an available book for this preview. No write was executed.';
	}
	if (field === 'date') {
		return text.includes('required')
			? 'Enter a transaction date. No write was executed.'
			: 'Use an explicit YYYY-MM-DD transaction date. No write was executed.';
	}
	if (field === 'debit_account_id' || field === 'credit_account_id') {
		if (text.includes('debit and credit accounts') || text.includes('different')) {
			return 'Choose two different selectable accounts. No write was executed.';
		}
		if (text.includes('not found') || text.includes('selectable')) {
			return 'Choose an account from the visible selector, not a hidden or placeholder account. No write was executed.';
		}
		return `Select a ${FIELD_LABELS[field]}. No write was executed.`;
	}
	if (field === 'amount') {
		return 'Enter a positive decimal amount using a dot, for example 320.00. No write was executed.';
	}
	if (field === 'currency') {
		return 'Use a supported three-letter currency that matches both selected accounts; no conversion is performed. No write was executed.';
	}
	if (field === 'description') {
		return 'Enter a description for the local preview. No write was executed.';
	}
	if (field === 'memo') {
		return 'Review the optional memo text. No write was executed.';
	}
	return fallbackFieldMessage(field);
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
	const errors: PreviewFieldErrors = {};
	if (text.includes('no selectable accounts')) {
		addFieldError(errors, 'book_id', friendlyFieldMessage('book_id', detail));
		return errors;
	}
	if (text.includes('debit and credit accounts')) {
		const message = friendlyFieldMessage('debit_account_id', detail);
		addFieldError(errors, 'debit_account_id', message);
		addFieldError(errors, 'credit_account_id', message);
		return errors;
	}
	if (text.includes('debit_account_id') || text.includes('debit account') || text.includes('source account')) {
		addFieldError(errors, 'debit_account_id', friendlyFieldMessage('debit_account_id', detail));
	}
	if (text.includes('credit_account_id') || text.includes('credit account') || text.includes('destination account')) {
		addFieldError(errors, 'credit_account_id', friendlyFieldMessage('credit_account_id', detail));
	}
	if (text.includes('amount')) addFieldError(errors, 'amount', friendlyFieldMessage('amount', detail));
	if (text.includes('currency')) addFieldError(errors, 'currency', friendlyFieldMessage('currency', detail));
	if (text.includes('date')) addFieldError(errors, 'date', friendlyFieldMessage('date', detail));
	if (text.includes('description')) addFieldError(errors, 'description', friendlyFieldMessage('description', detail));
	if (text.includes('memo')) addFieldError(errors, 'memo', friendlyFieldMessage('memo', detail));
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
			const message = friendlyFieldMessage(field, 'msg' in item ? item.msg : undefined);
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
		const returnedPayload: PreviewFormPayload = { ...payload, book_id: bookId };
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
					payload: returnedPayload,
					previewOnly: true
				};
			}
			return { preview: result.body as TransactionCreatePreview, payload: returnedPayload, fieldErrors: {}, previewOnly: true };
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return {
				error: 'API service is unavailable. No write was executed.',
				fieldErrors: {},
				payload: returnedPayload,
				previewOnly: true
			};
		}
	}
};
