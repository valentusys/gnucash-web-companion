import { isRedirect, redirect } from '@sveltejs/kit';
import type { AccountOption, AccountOptionsPurpose, AccountOptionsResponse } from '$lib/api/types';

export const ACCOUNT_OPTIONS_LIMIT = 200;

type AccountOptionsRequest = {
	purpose: 'transactions_filter' | 'transaction_create_preview';
	currency?: string;
};

export type AccountOptionsLoadState = {
	items: AccountOption[];
	available: boolean;
	limited: boolean;
	partialFailure: boolean;
	errorCode: string | null;
};

const SAFE_ERROR_CODE_RE = /^[a-z0-9_:-]{1,80}$/i;

function unavailable(errorCode: string): AccountOptionsLoadState {
	return {
		items: [],
		available: false,
		limited: false,
		partialFailure: false,
		errorCode
	};
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null;
}

function safeErrorCode(value: unknown, fallback: string): string {
	return typeof value === 'string' && SAFE_ERROR_CODE_RE.test(value) ? value : fallback;
}

function responseErrorCode(payload: unknown, fallback: string): string {
	if (!isRecord(payload)) return fallback;
	const detail = isRecord(payload.detail) ? payload.detail : null;
	return safeErrorCode(payload.error_code ?? detail?.code, fallback);
}

function normalizeAccountOption(value: unknown): AccountOption | null {
	if (!isRecord(value) || !isRecord(value.commodity)) return null;
	if (
		typeof value.id !== 'string' ||
		typeof value.name !== 'string' ||
		typeof value.full_name !== 'string' ||
		typeof value.type !== 'string' ||
		typeof value.currency !== 'string' ||
		typeof value.commodity.namespace !== 'string' ||
		typeof value.commodity.mnemonic !== 'string'
	) {
		return null;
	}
	return {
		id: value.id,
		parent_id: typeof value.parent_id === 'string' ? value.parent_id : null,
		name: value.name,
		display_name: typeof value.display_name === 'string' ? value.display_name : null,
		full_name: value.full_name,
		type: value.type,
		commodity: {
			namespace: value.commodity.namespace,
			mnemonic: value.commodity.mnemonic
		},
		currency: value.currency,
		hidden: value.hidden === true,
		placeholder: value.placeholder === true,
		selectable: value.selectable !== false
	};
}

function accountOptionsPath(bookPrefix: string, request: AccountOptionsRequest): string {
	const params = new URLSearchParams({
		purpose: request.purpose satisfies AccountOptionsPurpose,
		limit: String(ACCOUNT_OPTIONS_LIMIT)
	});
	if (request.currency?.trim()) params.set('currency', request.currency.trim().toUpperCase());
	return `${bookPrefix}/accounts/options?${params.toString()}`;
}

export async function loadAccountOptions(
	fetchFn: typeof fetch,
	bookPrefix: string,
	token: string,
	request: AccountOptionsRequest
): Promise<AccountOptionsLoadState> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	try {
		const response = await fetchFn(`${apiBase}${accountOptionsPath(bookPrefix, request)}`, {
			method: 'GET',
			headers: { authorization: `Bearer ${token}` }
		});
		if (response.status === 401) throw redirect(303, '/login');
		const payload = (await response.json().catch(() => null)) as AccountOptionsResponse | unknown;
		if (!response.ok) return unavailable(responseErrorCode(payload, `account_options_http_${response.status}`));
		if (!isRecord(payload) || !Array.isArray(payload.items)) return unavailable('invalid_account_options_response');
		const scan = isRecord(payload.scan) ? payload.scan : null;
		const items = payload.items
			.map(normalizeAccountOption)
			.filter((item): item is AccountOption => item !== null)
			.slice(0, ACCOUNT_OPTIONS_LIMIT);
		if (items.length !== payload.items.length) return unavailable('invalid_account_options_items');
		const partialFailure = payload.partial_failure === true;
		return {
			items,
			available: true,
			limited: Boolean(payload.next_cursor) || scan?.exhausted === false,
			partialFailure,
			errorCode: partialFailure ? safeErrorCode(payload.error_code, 'account_options_partial') : null
		};
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		return unavailable('account_options_unavailable');
	}
}
