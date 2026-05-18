import { error, redirect, type RequestHandler } from '@sveltejs/kit';
import { getAuthToken } from '$lib/api/server';

export const GET: RequestHandler = async ({ cookies, fetch, params, url }) => {
	const token = getAuthToken(cookies);
	const bookId = Number(params.bookId);
	if (!Number.isInteger(bookId) || bookId <= 0) {
		throw error(404, 'Requested item was not found.');
	}

	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	const query = url.search;
	let response: Response;
	try {
		response = await fetch(`${apiBase}/books/${bookId}/transactions/export${query}`, {
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
	if (!response.ok) {
		throw error(response.status, 'CSV export failed.');
	}

	const csv = await response.text();
	const responseHeaders: Record<string, string> = {
		'content-type': response.headers.get('content-type') ?? 'text/csv; charset=utf-8',
		'content-disposition':
			response.headers.get('content-disposition') ?? `attachment; filename="book-${bookId}-transactions.csv"`
	};
	for (const header of [
		'x-csv-export-limit',
		'x-csv-export-total',
		'x-csv-export-truncated',
		'x-csv-export-timeout-policy'
	]) {
		const value = response.headers.get(header);
		if (value) responseHeaders[header] = value;
	}
	return new Response(csv, {
		status: 200,
		headers: responseHeaders
	});
};
