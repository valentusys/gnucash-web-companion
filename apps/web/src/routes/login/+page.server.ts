import { env } from '$env/dynamic/private';
import { localeFromCookie, t } from '$lib/i18n';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { HealthPayload } from '$lib/api/types';
import type { PageServerLoad } from './$types';

const AUTH_COOKIE = 'access_token';
const SELECTED_BOOK_COOKIE = 'selected_book_id';
const DEFAULT_COOKIE_MAX_AGE_SECONDS = 60 * 30;
const LOGIN_REASONS = new Set(['session_changed']);

type LoginReason = 'session_changed';

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

function authCookieMaxAgeSeconds(): number {
	const minutes = Number(env.JWT_TOKEN_EXPIRE_MINUTES ?? '30');
	if (!Number.isFinite(minutes) || minutes <= 0) {
		return DEFAULT_COOKIE_MAX_AGE_SECONDS;
	}
	return Math.floor(minutes * 60);
}

function safeLoginReason(value: string | null): LoginReason | null {
	return LOGIN_REASONS.has(value ?? '') ? (value as LoginReason) : null;
}

function loginLoadData(firstRun: HealthPayload['first_run'] | null, reason: LoginReason | null) {
	return { firstRun, loginReason: reason };
}

export const load: PageServerLoad = async ({ fetch, url }) => {
	const reason = safeLoginReason(url.searchParams.get('reason'));
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	try {
		const response = await fetch(`${apiBase}/health`);
		if (!response.ok) {
			return loginLoadData(null, reason);
		}
		const health = (await response.json()) as HealthPayload;
		return loginLoadData(health.first_run ?? null, reason);
	} catch {
		return loginLoadData(null, reason);
	}
};

export const actions: Actions = {
	default: async ({ cookies, fetch, request, url }) => {
		const locale = localeFromCookie(cookies);
		const form = await request.formData();
		const username = String(form.get('username') ?? '').trim();
		const password = String(form.get('password') ?? '');

		if (!username || !password) {
			return fail(400, { error: t(locale, 'login.error.missingCredentials'), username });
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
			return fail(502, { error: t(locale, 'login.error.serviceUnavailable'), username });
		}

		if (!response.ok) {
			if (response.status === 503) {
				return fail(503, { error: t(locale, 'login.error.operatorConfiguration'), username });
			}
			return fail(401, { error: t(locale, 'login.error.invalidCredentials'), username });
		}

		const data = (await response.json()) as LoginResponse;
		cookies.delete(SELECTED_BOOK_COOKIE, { path: '/' });
		cookies.set(AUTH_COOKIE, data.access_token, {
			httpOnly: true,
			secure: url.protocol === 'https:',
			sameSite: 'lax',
			path: '/',
			maxAge: authCookieMaxAgeSeconds()
		});

		throw redirect(303, safeNext(url.searchParams.get('next')));
	}
};
