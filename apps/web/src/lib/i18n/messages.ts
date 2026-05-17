export const DEFAULT_LOCALE = 'en';
export const LOCALE_COOKIE = 'ui_locale';

export const supportedLocales = ['en', 'ru'] as const;

export type Locale = (typeof supportedLocales)[number];

export type MessageKey =
	| 'locale.english'
	| 'locale.russian'
	| 'locale.switcherLabel'
	| 'login.title'
	| 'login.subtitle'
	| 'login.username'
	| 'login.password'
	| 'login.submit'
	| 'nav.dashboard'
	| 'nav.accounts'
	| 'nav.transactions'
	| 'nav.logout'
	| 'safety.statusLabel'
	| 'safety.badge'
	| 'safety.message'
	| 'dashboard.title'
	| 'accounts.kicker'
	| 'accounts.title'
	| 'transactions.kicker'
	| 'transactions.title';

export const messages: Record<Locale, Record<MessageKey, string>> = {
	en: {
		'locale.english': 'English',
		'locale.russian': 'Russian',
		'locale.switcherLabel': 'Language',
		'login.title': 'Sign in',
		'login.subtitle': 'Use the configured admin account to continue.',
		'login.username': 'Username',
		'login.password': 'Password',
		'login.submit': 'Sign in',
		'nav.dashboard': 'Dashboard',
		'nav.accounts': 'Accounts',
		'nav.transactions': 'Transactions',
		'nav.logout': 'Logout',
		'safety.statusLabel': 'Read-only safety status',
		'safety.badge': 'Read-only by default',
		'safety.message':
			'Read-only MVP by default. GnuCash Desktop remains the authoritative editor; web writes require an explicit post-MVP feature flag.',
		'dashboard.title': 'Dashboard',
		'accounts.kicker': 'Accounts',
		'accounts.title': 'Account tree',
		'transactions.kicker': 'Transactions',
		'transactions.title': 'Browse transactions'
	},
	ru: {
		'locale.english': 'Английский',
		'locale.russian': 'Русский',
		'locale.switcherLabel': 'Язык',
		'login.title': 'Вход',
		'login.subtitle': 'Используйте настроенную учётную запись администратора.',
		'login.username': 'Имя пользователя',
		'login.password': 'Пароль',
		'login.submit': 'Войти',
		'nav.dashboard': 'Обзор',
		'nav.accounts': 'Счета',
		'nav.transactions': 'Транзакции',
		'nav.logout': 'Выйти',
		'safety.statusLabel': 'Статус безопасности read-only режима',
		'safety.badge': 'Read-only по умолчанию',
		'safety.message':
			'MVP по умолчанию работает только на чтение. GnuCash Desktop остаётся главным редактором; любые web-записи требуют отдельного post-MVP feature flag.',
		'dashboard.title': 'Обзор',
		'accounts.kicker': 'Счета',
		'accounts.title': 'Дерево счетов',
		'transactions.kicker': 'Транзакции',
		'transactions.title': 'Просмотр транзакций'
	}
};
