import { redirect, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ cookies, fetch }) => {
	const token = cookies.get('access_token');
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';

	if (token) {
		try {
			await fetch(`${apiBase}/auth/logout`, {
				method: 'POST',
				headers: { authorization: `Bearer ${token}` }
			});
		} catch {
			// Logout is local-cookie driven. Backend notification is best effort.
		}
	}

	cookies.delete('access_token', { path: '/' });
	throw redirect(303, '/login');
};
