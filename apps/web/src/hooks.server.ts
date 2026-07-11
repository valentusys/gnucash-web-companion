import { error, redirect, type Handle } from '@sveltejs/kit';

const PROTECTED_PREFIXES = ['/dashboard', '/accounts', '/books', '/scheduled', '/transactions', '/reports'];
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

function isProtectedPath(pathname: string): boolean {
	return PROTECTED_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

function hasTrustedOrigin(event: Parameters<Handle>[0]['event']): boolean {
	if (SAFE_METHODS.has(event.request.method.toUpperCase())) return true;

	const origin = event.request.headers.get('origin');
	if (!origin) return true;

	try {
		return new URL(origin).origin === event.url.origin;
	} catch {
		return false;
	}
}

export const handle: Handle = async ({ event, resolve }) => {
	if (!hasTrustedOrigin(event)) {
		throw error(403, 'Cross-origin state-changing requests are not allowed for this pre-alpha local/LAN app.');
	}

	const token = event.cookies.get('access_token');
	event.locals.authenticated = Boolean(token);

	if (isProtectedPath(event.url.pathname) && !token) {
		const next = `${event.url.pathname}${event.url.search}`;
		throw redirect(303, `/login?next=${encodeURIComponent(next)}`);
	}

	return resolve(event);
};
