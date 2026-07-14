import { fail } from '@sveltejs/kit';
import { getAuthToken, getCurrentUser, isCurrentUserAdmin } from '$lib/api/server';
import type { Book, BookPreflightRequest, BookPreflightResponse, BookProblemCode } from '$lib/api/types';
import type { Actions, PageServerLoad } from './$types';

const allowedBookProblemCodes = new Set<BookProblemCode>([
	'admin_required',
	'preflight_required',
	'preflight_rejected',
	'preflight_token_invalid',
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
	'api_unavailable',
	'book_registry_failed',
	'unknown_book_problem'
]);

type SafeFormState = {
	name: string;
	mountedPath: string;
	baseCurrency: string;
	makeDefault: boolean;
};

function textField(form: FormData, name: string): string {
	return String(form.get(name) ?? '').trim();
}

function safeFormState(form: FormData): SafeFormState {
	return {
		name: textField(form, 'name'),
		mountedPath: textField(form, 'mounted_path'),
		baseCurrency: textField(form, 'base_currency').toUpperCase(),
		makeDefault: form.get('make_default') === 'on'
	};
}

function toPreflightRequest(state: SafeFormState): BookPreflightRequest {
	return {
		name: state.name,
		storage_type: 'sqlite',
		uri_or_path: state.mountedPath,
		base_currency: state.baseCurrency,
		make_default: state.makeDefault
	};
}

function bookProblemCodeFromPayload(payload: unknown, fallback: BookProblemCode): BookProblemCode {
	let candidate: unknown = null;
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		candidate = record.safe_code ?? record.code;
		if (!candidate && record.detail && typeof record.detail === 'object') {
			const nested = record.detail as Record<string, unknown>;
			candidate = nested.safe_code ?? nested.code;
		}
	}
	return typeof candidate === 'string' && allowedBookProblemCodes.has(candidate as BookProblemCode)
		? (candidate as BookProblemCode)
		: fallback;
}

async function safeJson(response: Response): Promise<unknown> {
	try {
		return await response.json();
	} catch {
		return null;
	}
}

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = getAuthToken(cookies);
	const currentUser = await getCurrentUser(fetch, token);
	return {
		isAdmin: isCurrentUserAdmin(currentUser)
	};
};

export const actions: Actions = {
	preflight: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const formState = safeFormState(form);
		if (!formState.name || !formState.mountedPath || !formState.baseCurrency) {
			return fail(400, {
				preflightErrorCode: 'preflight_required',
				preflightRequest: formState
			});
		}

		const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
		let response: Response;
		try {
			response = await fetch(`${apiBase}/books/preflight`, {
				method: 'POST',
				headers: {
					authorization: `Bearer ${token}`,
					'content-type': 'application/json'
				},
				body: JSON.stringify(toPreflightRequest(formState))
			});
		} catch {
			return fail(502, {
				preflightErrorCode: 'api_unavailable',
				preflightRequest: formState
			});
		}

		const payload = await safeJson(response);
		if (!response.ok) {
			return fail(response.status, {
				preflightErrorCode: bookProblemCodeFromPayload(
					payload,
					response.status === 403 ? 'admin_required' : 'unknown_book_problem'
				),
				preflightRequest: formState
			});
		}

		const preflight = payload as BookPreflightResponse;
		return {
			preflight,
			preflightRequest: formState
		};
	},
	confirm: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		const form = await request.formData();
		const formState = safeFormState(form);
		const preflightToken = textField(form, 'preflight_token');
		if (!formState.name || !formState.mountedPath || !formState.baseCurrency || !preflightToken) {
			return fail(400, {
				registrationErrorCode: 'preflight_required',
				preflightRequest: formState
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
					...toPreflightRequest(formState),
					preflight_token: preflightToken
				})
			});
		} catch {
			return fail(502, {
				registrationErrorCode: 'api_unavailable',
				preflightRequest: formState
			});
		}

		const payload = await safeJson(response);
		if (!response.ok) {
			return fail(response.status, {
				registrationErrorCode: bookProblemCodeFromPayload(
					payload,
					response.status === 403 ? 'admin_required' : 'book_registry_failed'
				),
				preflightRequest: formState
			});
		}

		const registered = payload as Book;
		return {
			registrationSuccessCode: 'registered',
			registeredBookId: registered.id ?? null,
			registeredBookName: registered.name ?? formState.name
		};
	}
};
