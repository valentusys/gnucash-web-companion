import { error, redirect, type Cookies } from '@sveltejs/kit';

export function getAuthToken(cookies: Cookies): string {
	const token = cookies.get('access_token');
	if (!token) {
		throw redirect(303, '/login');
	}
	return token;
}

export function getActiveBookId(cookies: Cookies): number | null {
	const raw = cookies.get('selected_book_id');
	if (!raw) return null;
	const parsed = Number(raw);
	return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export async function apiFetch<T>(
	fetchFn: typeof fetch,
	path: string,
	token: string
): Promise<T> {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	let response: Response;
	try {
		response = await fetchFn(`${apiBase}${path}`, {
			headers: { authorization: `Bearer ${token}` }
		});
	} catch {
		throw error(502, 'API service is unavailable.');
	}

	if (response.status === 401) {
		throw redirect(303, '/login');
	}
	if (response.status === 403) {
		throw error(403, 'You do not have access to this book.');
	}
	if (response.status === 404) {
		throw error(404, 'Requested item was not found.');
	}
	if (response.status === 503) {
		throw error(503, 'GnuCash book is not configured or cannot be read.');
	}
	if (!response.ok) {
		throw error(response.status, 'API request failed.');
	}
	return (await response.json()) as T;
}
