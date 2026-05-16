import { redirect, type Handle } from '@sveltejs/kit';

const PROTECTED_PREFIXES = ['/dashboard', '/accounts', '/books', '/transactions'];

function isProtectedPath(pathname: string): boolean {
	return PROTECTED_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get('access_token');
	event.locals.authenticated = Boolean(token);

	if (isProtectedPath(event.url.pathname) && !token) {
		const next = `${event.url.pathname}${event.url.search}`;
		throw redirect(303, `/login?next=${encodeURIComponent(next)}`);
	}

	return resolve(event);
};
