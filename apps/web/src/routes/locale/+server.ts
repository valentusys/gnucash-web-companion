import { redirect, type RequestHandler } from '@sveltejs/kit';
import { isLocale, LOCALE_COOKIE } from '$lib/i18n';

function safeReturnTo(value: FormDataEntryValue | null): string {
	if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) {
		return '/dashboard';
	}
	return value;
}

export const POST: RequestHandler = async ({ cookies, request }) => {
	const formData = await request.formData();
	const locale = formData.get('locale');
	const returnTo = safeReturnTo(formData.get('returnTo'));

	if (typeof locale === 'string' && isLocale(locale)) {
		cookies.set(LOCALE_COOKIE, locale, {
			path: '/',
			httpOnly: true,
			sameSite: 'lax',
			secure: false,
			maxAge: 60 * 60 * 24 * 365
		});
	}

	throw redirect(303, returnTo);
};
