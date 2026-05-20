import { env } from '$env/dynamic/private';
import { redirect, type Actions } from '@sveltejs/kit';
import { apiFetch, getAuthToken, getActiveBookContext } from '$lib/api/server';
import type { TransactionDetail, TransactionWriteResult } from '$lib/api/types';
import { localeFromCookie } from '$lib/i18n';
import type { PageServerLoad } from './$types';

type ApiDeleteResult<T> = {
	ok: boolean;
	status: number;
	body: T | { detail?: unknown };
};

async function apiDelete<T>(fetchFn: typeof fetch, path: string, token: string): Promise<ApiDeleteResult<T>> {
	const apiBase = env.API_INTERNAL_URL ?? 'http://localhost:8000';
	const response = await fetchFn(`${apiBase}${path}`, {
		method: 'DELETE',
		headers: { authorization: `Bearer ${token}` }
	});
	if (response.status === 401) throw redirect(303, '/login');
	const body = await response.json().catch(() => ({}));
	return { ok: response.ok, status: response.status, body };
}

function detailMessage(body: unknown): string {
	if (typeof body === 'object' && body !== null && 'detail' in body && typeof body.detail === 'string') {
		const detail = body.detail.trim();
		if (detail && detail.length <= 180 && !/[\\/]/.test(detail)) {
			return detail;
		}
	}
	return 'Write-alpha request failed safely. Check local operator logs and redacted audit/backup/lock evidence before retrying.';
}

function hasDeleteAcknowledgement(formData: FormData): boolean {
	return String(formData.get('delete_acknowledgement') ?? '') === 'experimental-delete-acknowledged';
}

export const load: PageServerLoad = async ({ cookies, fetch, params }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);

	const transaction = await apiFetch<TransactionDetail>(
		fetch,
		`${bookPrefix}/transactions/${encodeURIComponent(params.id)}`,
		token
	);

	return { transaction, activeBook, locale: localeFromCookie(cookies), writesEnabled: env.GNUCASH_WRITES_ENABLED === 'true' };
};

export const actions: Actions = {
	delete: async ({ cookies, fetch, params, request }) => {
		if (env.GNUCASH_WRITES_ENABLED !== 'true') {
			return { error: 'GnuCash writes are disabled. MVP v0.1 is read-only by default.' };
		}
		const token = getAuthToken(cookies);
		const formData = await request.formData();
		if (!hasDeleteAcknowledgement(formData)) {
			return {
				error:
					'Explicit acknowledgement is required before deleting an experimental controlled-write transaction. Use only disposable/test copies with backups.'
			};
		}
		const bookId = String(formData.get('book_id') ?? '');
		const transactionId = params.id;
		if (!bookId || !transactionId) {
			return { error: 'Missing book or transaction identifier for delete request.' };
		}
		try {
			const result = await apiDelete<TransactionWriteResult>(
				fetch,
				`/books/${bookId}/transactions/${encodeURIComponent(transactionId)}`,
				token
			);
			if (!result.ok) return { error: detailMessage(result.body) };
			throw redirect(303, '/transactions');
		} catch (err) {
			if (typeof err === 'object' && err !== null && 'status' in err) throw err;
			return { error: 'API service is unavailable.' };
		}
	}
};
