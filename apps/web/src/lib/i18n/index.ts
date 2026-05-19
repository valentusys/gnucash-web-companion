import type { Cookies } from '@sveltejs/kit';
import { DEFAULT_LOCALE, LOCALE_COOKIE, messages, supportedLocales, type Locale, type MessageKey } from './messages';

export { DEFAULT_LOCALE, LOCALE_COOKIE, messages, supportedLocales };
export type { Locale, MessageKey };

export function isLocale(value: string | null | undefined): value is Locale {
	return supportedLocales.includes(value as Locale);
}

export function localeFromCookie(cookies: Cookies): Locale {
	const cookieLocale = cookies.get(LOCALE_COOKIE);
	return isLocale(cookieLocale) ? cookieLocale : DEFAULT_LOCALE;
}

export function t(locale: Locale, key: MessageKey, replacements: Record<string, string | number> = {}): string {
	const template = messages[locale]?.[key] ?? messages[DEFAULT_LOCALE][key];
	return Object.entries(replacements).reduce(
		(result, [name, value]) => result.replaceAll(`{${name}}`, String(value)),
		template
	);
}
