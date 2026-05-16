import { fail, redirect, type Actions } from '@sveltejs/kit';

const AUTH_COOKIE = 'access_token';
const COOKIE_MAX_AGE_SECONDS = 60 * 30;

type LoginResponse = {
	access_token: string;
	token_type: 'bearer';
	user: {
		id: number;
		username: string;
		display_name: string;
	};
};

function safeNext(value: string | null): string {
	if (!value || !value.startsWith('/') || value.startsWith('//')) {
		return '/dashboard';
	}
	return value;
}

export const actions: Actions = {
	default: async ({ cookies, fetch, request, url }) => {
		const form = await request.formData();
		const username = String(form.get('username') ?? '').trim();
		const password = String(form.get('password') ?? '');

		if (!username || !password) {
			return fail(400, { error: 'Enter username and password.', username });
		}

		const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
		let response: Response;

		try {
			response = await fetch(`${apiBase}/auth/login`, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ username, password })
			});
		} catch {
			return fail(502, { error: 'Authentication service is unavailable.', username });
		}

		if (!response.ok) {
			return fail(401, { error: 'Invalid username or password.', username });
		}

		const data = (await response.json()) as LoginResponse;
		cookies.set(AUTH_COOKIE, data.access_token, {
			httpOnly: true,
			secure: url.protocol === 'https:',
			sameSite: 'lax',
			path: '/',
			maxAge: COOKIE_MAX_AGE_SECONDS
		});

		throw redirect(303, safeNext(url.searchParams.get('next')));
	}
};
