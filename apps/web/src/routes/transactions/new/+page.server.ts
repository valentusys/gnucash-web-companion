import { env } from '$env/dynamic/private';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import { loadAccountOptions, type AccountOptionsLoadState } from '$lib/accounts/options.server';
import { getActiveBookContext, getAuthToken } from '$lib/api/server';
import { localeFromCookie } from '$lib/i18n';
import type {
	Book,
	TransactionCreateConfirmResult,
	TransactionCreateErrorEnvelope,
	TransactionCreatePreviewResponse,
	TransactionCreateRequest,
	TransactionCreateSettings,
	TransactionCreateSplitRequest
} from '$lib/api/types';
import type { PageServerLoad } from './$types';

type TransactionCreateFieldErrors = Partial<Record<'book_id' | 'date' | 'description' | 'currency' | 'splits', string>>;

type ApiJsonSuccess<T> = { ok: true; status: number; body: T };
type ApiJsonFailure = {
	ok: false;
	status: number;
	code: string;
	messageKey: string;
	fieldPath: string | null;
	retryable: boolean;
	recoveryRef: string | null;
	requestRef: string;
};
type ApiJsonResult<T> = ApiJsonSuccess<T> | ApiJsonFailure;

type PostJsonOptions = {
	body: unknown;
	headers?: Record<string, string>;
};

const FALLBACK_CREATE_SETTINGS: TransactionCreateSettings = {
	known: false,
	enabled: false,
	create_generation: 1,
	recovery_required: false,
	blocked_codes: []
};

const SUPPORTED_CREATE_CODES = new Set([
	'CREATE_DEPLOYMENT_DISABLED',
	'CREATE_BOOK_DISABLED',
	'CREATE_PERMISSION_DENIED',
	'PREVIEW_TOKEN_EXPIRED',
	'PREVIEW_TOKEN_INVALID',
	'PREVIEW_PAYLOAD_MISMATCH',
	'PREVIEW_STALE',
	'IDEMPOTENCY_PAYLOAD_MISMATCH',
	'CREATE_IN_PROGRESS',
	'BOOK_WRITE_BUSY',
	'CREATE_RECOVERY_REQUIRED',
	'INVALID_DATE',
	'DESCRIPTION_REQUIRED',
	'SPLIT_COUNT_OUT_OF_RANGE',
	'INVALID_DECIMAL',
	'ZERO_SPLIT',
	'UNBALANCED_SPLITS',
	'INSUFFICIENT_DISTINCT_ACCOUNTS',
	'ACCOUNT_NOT_FOUND',
	'ACCOUNT_NOT_POSTABLE',
	'UNSUPPORTED_ACCOUNT_TYPE',
	'UNSUPPORTED_COMMODITY',
	'COMMODITY_MISMATCH',
	'BACKUP_FAILED',
	'WRITE_FAILED',
	'CREATE_RESULT_UNKNOWN'
]);

const SUPPORTED_CREATE_MESSAGE_KEYS = new Set([
	'transactionCreate.error.generic',
	...Array.from(SUPPORTED_CREATE_CODES, (code) => `transactionCreate.error.${code}`)
]);

const SAFE_TRANSACTION_ID_RE = /^[A-Za-z0-9_-]{1,64}$/;
function safeOpaqueRef(value: unknown, pattern: RegExp, fallback: string | null): string | null {
	if (typeof value !== 'string') return fallback;
	const trimmed = value.trim();
	return pattern.test(trimmed) ? trimmed : fallback;
}
const REQUEST_REF_RE = /^req_[A-Za-z0-9_-]{8,64}$/;
const RECOVERY_REF_RE = /^rcv_[A-Za-z0-9_-]{8,64}$/;

function apiBase(): string {
	return env.API_INTERNAL_URL ?? 'http://localhost:8000';
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null;
}

function safeCode(value: unknown, fallback = 'CREATE_RESULT_UNKNOWN'): string {
	return typeof value === 'string' && SUPPORTED_CREATE_CODES.has(value) ? value : fallback;
}

function safeMessageKey(value: unknown, code: string): string {
	const candidate = typeof value === 'string' ? value : null;
	if (candidate && SUPPORTED_CREATE_MESSAGE_KEYS.has(candidate)) return candidate;
	const fallback = `transactionCreate.error.${safeCode(code)}`;
	return SUPPORTED_CREATE_MESSAGE_KEYS.has(fallback) ? fallback : 'transactionCreate.error.generic';
}

function safeCreateRedirectPath(result: TransactionCreateConfirmResult): string {
	const fallback = '/transactions';
	const status = result.status === 'already_created' ? 'already_created' : 'created';
	const link = result.links.transaction;
	try {
		const target = new URL(typeof link === 'string' ? link : fallback, 'http://frontend.local');
		if (target.origin !== 'http://frontend.local') return `${fallback}?create_status=${status}`;
		if (target.pathname !== '/transactions') {
			if (!target.pathname.startsWith('/transactions/')) return `${fallback}?create_status=${status}`;
			const transactionId = target.pathname.slice('/transactions/'.length);
			if (!SAFE_TRANSACTION_ID_RE.test(transactionId)) return `${fallback}?create_status=${status}`;
		}
		if (target.pathname.includes('\\')) return `${fallback}?create_status=${status}`;
		target.hash = '';
		target.search = '';
		target.searchParams.set('create_status', status);
		return `${target.pathname}${target.search}`;
	} catch {
		return `${fallback}?create_status=${status}`;
	}
}

function transactionCreateFailure(status: number, payload: unknown): ApiJsonFailure {
	const envelope = payload as Partial<TransactionCreateErrorEnvelope>;
	const errorPayload: Record<string, unknown> = isRecord(envelope.error) ? envelope.error : {};
	const code = safeCode(errorPayload.code, status === 403 ? 'CREATE_PERMISSION_DENIED' : 'CREATE_RESULT_UNKNOWN');
	return {
		ok: false,
		status,
		code,
		messageKey: safeMessageKey(errorPayload.message_key, code),
		fieldPath: typeof errorPayload.field_path === 'string' ? errorPayload.field_path : null,
		retryable: typeof errorPayload.retryable === 'boolean' ? errorPayload.retryable : false,
		recoveryRef: safeOpaqueRef(errorPayload.recovery_ref, RECOVERY_REF_RE, null),
		requestRef: safeOpaqueRef(errorPayload.request_ref, REQUEST_REF_RE, 'req_unavailable') ?? 'req_unavailable'
	};
}

async function apiGetOptionalJson<T>(fetchFn: typeof fetch, path: string, token: string, fallback: T): Promise<T> {
	try {
		const response = await fetchFn(`${apiBase()}${path}`, {
			headers: { authorization: `Bearer ${token}` }
		});
		if (response.status === 401) throw redirect(303, '/login');
		if (!response.ok) return fallback;
		return (await response.json()) as T;
	} catch (reason) {
		if (typeof reason === 'object' && reason !== null && 'status' in reason) throw reason;
		return fallback;
	}
}

async function apiPostJson<T>(
	fetchFn: typeof fetch,
	path: string,
	token: string,
	options: PostJsonOptions
): Promise<ApiJsonResult<T>> {
	try {
		const response = await fetchFn(`${apiBase()}${path}`, {
			method: 'POST',
			headers: {
				'content-type': 'application/json',
				authorization: `Bearer ${token}`,
				...(options.headers ?? {})
			},
			body: JSON.stringify(options.body)
		});
		if (response.status === 401) throw redirect(303, '/login');
		const payload = await response.json().catch(() => null);
		if (!response.ok) return transactionCreateFailure(response.status, payload);
		return { ok: true, status: response.status, body: payload as T };
	} catch (reason) {
		if (typeof reason === 'object' && reason !== null && 'status' in reason) throw reason;
		return transactionCreateFailure(503, {
			error: {
				code: 'WRITE_FAILED',
				message_key: 'transactionCreate.error.WRITE_FAILED',
				field_path: null,
				retryable: false,
				recovery_ref: null,
				request_ref: 'frontend-api-unavailable'
			}
		});
	}
}

function stringList(formData: FormData, name: string): string[] {
	return formData.getAll(name).map((value) => String(value ?? '').trim());
}

function textField(formData: FormData, name: string): string {
	return String(formData.get(name) ?? '').trim();
}

function formToTransactionCreateRequest(formData: FormData): TransactionCreateRequest {
	const accountIds = stringList(formData, 'split_account_id');
	const amounts = stringList(formData, 'split_amount');
	const memos = formData.getAll('split_memo').map((value) => String(value ?? '').trim());
	const splits: TransactionCreateSplitRequest[] = accountIds.map((account_id, index) => ({
		account_id,
		amount: amounts[index] ?? '',
		memo: memos[index] ?? ''
	}));
	return {
		date: textField(formData, 'date'),
		description: textField(formData, 'description'),
		currency: textField(formData, 'currency').toUpperCase(),
		splits
	};
}

function fieldErrorsFromFailure(result: ApiJsonFailure): TransactionCreateFieldErrors {
	if (result.fieldPath?.startsWith('splits')) return { splits: result.messageKey };
	if (result.code === 'INVALID_DATE') return { date: result.messageKey };
	if (result.code === 'DESCRIPTION_REQUIRED') return { description: result.messageKey };
	if (result.code === 'COMMODITY_MISMATCH' || result.code === 'UNSUPPORTED_COMMODITY') return { currency: result.messageKey };
	if (
		result.code === 'SPLIT_COUNT_OUT_OF_RANGE' ||
		result.code === 'INVALID_DECIMAL' ||
		result.code === 'ZERO_SPLIT' ||
		result.code === 'UNBALANCED_SPLITS' ||
		result.code === 'INSUFFICIENT_DISTINCT_ACCOUNTS' ||
		result.code === 'ACCOUNT_NOT_FOUND' ||
		result.code === 'ACCOUNT_NOT_POSTABLE' ||
		result.code === 'UNSUPPORTED_ACCOUNT_TYPE'
	) {
		return { splits: result.messageKey };
	}
	return {};
}

function bookMismatchFailure(payload: TransactionCreateRequest, activeBook: Book | null) {
	return fail(403, {
		errorCode: 'CREATE_PERMISSION_DENIED',
		errorKey: 'transactionCreate.error.CREATE_PERMISSION_DENIED',
		requestRef: activeBook ? `book-${activeBook.id}` : 'no-active-book',
		fieldErrors: { book_id: 'transactionCreate.error.CREATE_PERMISSION_DENIED' } satisfies TransactionCreateFieldErrors,
		payload
	});
}

function isTransactionCreateSplit(value: unknown): value is TransactionCreateSplitRequest {
	return (
		isRecord(value) &&
		typeof value.account_id === 'string' &&
		typeof value.amount === 'string' &&
		typeof value.memo === 'string'
	);
}

function isTransactionCreateRequest(value: unknown): value is TransactionCreateRequest {
	return (
		isRecord(value) &&
		typeof value.date === 'string' &&
		typeof value.description === 'string' &&
		typeof value.currency === 'string' &&
		Array.isArray(value.splits) &&
		value.splits.every(isTransactionCreateSplit)
	);
}

function transactionFromJson(raw: string): TransactionCreateRequest | null {
	try {
		const parsed = JSON.parse(raw) as unknown;
		return isTransactionCreateRequest(parsed) ? parsed : null;
	} catch {
		return null;
	}
}

function isSafeRetryableConfirmFailure(result: ApiJsonFailure): boolean {
	return result.retryable === true && (result.code === 'CREATE_IN_PROGRESS' || result.code === 'BOOK_WRITE_BUSY');
}

function retryPreviewFromConfirmFailure(
	transaction: TransactionCreateRequest,
	previewToken: string,
	idempotencyKey: string,
	result: ApiJsonFailure
): TransactionCreatePreviewResponse | null {
	if (!previewToken || !idempotencyKey || !isSafeRetryableConfirmFailure(result)) return null;
	return {
		preview_only: true,
		confirm_allowed: true,
		create_count: 1,
		preview_token: previewToken,
		expires_at: '',
		idempotency_key: idempotencyKey,
		create_generation: 0,
		currency: transaction.currency,
		date: transaction.date,
		description: transaction.description,
		splits: transaction.splits.map((split, index) => ({
			index,
			account: {
				id: split.account_id,
				name: '',
				display_name: null,
				full_name: split.account_id,
				type: '',
				currency: transaction.currency
			},
			amount: split.amount,
			memo: split.memo
		})),
		warnings: []
	};
}

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	let accountOptionsState: AccountOptionsLoadState = {
		items: [],
		available: false,
		limited: false,
		partialFailure: false,
		errorCode: 'no_active_book'
	};
	let createSettings = FALLBACK_CREATE_SETTINGS;
	if (activeBook) {
		[accountOptionsState, createSettings] = await Promise.all([
			loadAccountOptions(fetch, bookPrefix, token, {
				purpose: 'transaction_create_preview',
				currency: activeBook.base_currency
			}),
			apiGetOptionalJson<TransactionCreateSettings>(
				fetch,
				`/books/${activeBook.id}/transaction-create-settings`,
				token,
				FALLBACK_CREATE_SETTINGS
			)
		]);
	}
	return {
		locale: localeFromCookie(cookies),
		books,
		activeBook,
		accounts: accountOptionsState.items,
		accountOptionsAvailable: accountOptionsState.available,
		accountOptionsLimited: accountOptionsState.limited,
		accountOptionsPartialFailure: accountOptionsState.partialFailure,
		accountOptionsErrorCode: accountOptionsState.errorCode,
		createSettings,
		previewOnly: false
	};
};

export const actions: Actions = {
	preview: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		const transaction = formToTransactionCreateRequest(formData);
		const bookId = textField(formData, 'book_id');
		const { activeBook } = await getActiveBookContext(fetch, cookies, token);
		if (!activeBook || bookId !== String(activeBook.id)) return bookMismatchFailure(transaction, activeBook);

		const result = await apiPostJson<TransactionCreatePreviewResponse>(
			fetch,
			`/books/${activeBook.id}/transactions/create-preview`,
			token,
			{ body: transaction }
		);
		if (result.ok === false) {
			return fail(result.status, {
				errorCode: result.code,
				errorKey: result.messageKey,
				requestRef: result.requestRef,
				fieldErrors: fieldErrorsFromFailure(result),
				payload: transaction
			});
		}
		return {
			preview: result.body,
			payload: transaction,
			fieldErrors: {}
		};
	},
	confirm: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		const previewToken = textField(formData, 'preview_token');
		const idempotencyKey = textField(formData, 'idempotency_key');
		const transaction = transactionFromJson(String(formData.get('transaction_json') ?? ''));
		const bookId = textField(formData, 'book_id');
		const { activeBook } = await getActiveBookContext(fetch, cookies, token);
		if (!transaction) {
			return fail(400, {
				errorCode: 'PREVIEW_PAYLOAD_MISMATCH',
				errorKey: 'transactionCreate.error.PREVIEW_PAYLOAD_MISMATCH',
				requestRef: 'invalid-transaction-json',
				fieldErrors: { splits: 'transactionCreate.error.PREVIEW_PAYLOAD_MISMATCH' } satisfies TransactionCreateFieldErrors,
				payload: null
			});
		}
		if (!activeBook || bookId !== String(activeBook.id)) return bookMismatchFailure(transaction, activeBook);

		const result = await apiPostJson<TransactionCreateConfirmResult>(
			fetch,
			`/books/${activeBook.id}/transactions`,
			token,
			{
				body: { preview_token: previewToken, transaction },
				headers: { 'Idempotency-Key': idempotencyKey }
			}
		);
		if (result.ok === false) {
			const retryPreview = retryPreviewFromConfirmFailure(transaction, previewToken, idempotencyKey, result);
			return fail(result.status, {
				errorCode: result.code,
				errorKey: result.messageKey,
				requestRef: result.requestRef,
				retryable: result.retryable,
				recoveryRef: result.recoveryRef,
				fieldErrors: fieldErrorsFromFailure(result),
				payload: transaction,
				preview: retryPreview
			});
		}
		throw redirect(303, safeCreateRedirectPath(result.body));
	}
};
