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
	| 'nav.scheduled'
	| 'nav.books'
	| 'nav.logout'
	| 'safety.statusLabel'
	| 'safety.badge'
	| 'safety.message'
	| 'dashboard.title'
	| 'accounts.kicker'
	| 'accounts.title'
	| 'transactions.kicker'
	| 'transactions.title'
	| 'books.kicker'
	| 'books.title'
	| 'books.subtitle'
	| 'books.activeDefault'
	| 'books.configuredTitle'
	| 'books.hiddenPolicy'
	| 'books.noMutationBadge'
	| 'books.currentBook'
	| 'books.defaultBook'
	| 'books.readOnlyBadge'
	| 'books.accessibleBadge'
	| 'books.baseCurrency'
	| 'books.storageType'
	| 'books.readonlyStatus'
	| 'books.safetyNote'
	| 'books.noBooks'
	| 'books.notConfigured'
	| 'books.unknown'
	| 'books.accessRole'
	| 'books.status'
	| 'books.openSafeViews'
	| 'books.viewAccounts'
	| 'books.browseTransactions'
	| 'books.viewScheduled'
	| 'books.dashboardSummary'
	| 'books.noManagementActions';

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
		'nav.scheduled': 'Scheduled',
		'nav.books': 'Books',
		'nav.logout': 'Logout',
		'safety.statusLabel': 'Read-only safety status',
		'safety.badge': 'Read-only by default',
		'safety.message':
			'Read-only MVP by default. GnuCash Desktop remains the authoritative editor; web writes require an explicit post-MVP feature flag.',
		'dashboard.title': 'Dashboard',
		'accounts.kicker': 'Accounts',
		'accounts.title': 'Account tree',
		'transactions.kicker': 'Transactions',
		'transactions.title': 'Browse transactions',
		'books.kicker': 'Books',
		'books.title': 'Book management',
		'books.subtitle':
			'Read-only view/manage metadata only. This page shows already configured books that your account can access; it does not provide book data editing workflows.',
		'books.activeDefault': 'Active/default book',
		'books.configuredTitle': 'Configured books',
		'books.hiddenPolicy': 'Archived and unauthorized books are hidden or blocked by the API.',
		'books.noMutationBadge': 'No upload, deletion, or GnuCash data editing here',
		'books.currentBook': 'Current book',
		'books.defaultBook': 'Active/default book',
		'books.readOnlyBadge': 'Read-only',
		'books.accessibleBadge': 'Access status: Accessible',
		'books.baseCurrency': 'Base currency',
		'books.storageType': 'Storage type',
		'books.readonlyStatus': 'Read-only status',
		'books.safetyNote': 'GnuCash Desktop remains the authoritative editor.',
		'books.noBooks': 'No accessible configured books are available for this account.',
		'books.notConfigured': 'Not configured',
		'books.unknown': 'Unknown',
		'books.accessRole': 'Access role',
		'books.status': 'Metadata status',
		'books.openSafeViews': 'Open safe views',
		'books.viewAccounts': 'View accounts',
		'books.browseTransactions': 'Browse transactions',
		'books.viewScheduled': 'View scheduled metadata',
		'books.dashboardSummary': 'Dashboard summary',
		'books.noManagementActions': 'No registry management actions are available on this read-only page.'
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
		'nav.scheduled': 'Плановые',
		'nav.books': 'Книги',
		'nav.logout': 'Выйти',
		'safety.statusLabel': 'Статус безопасности read-only режима',
		'safety.badge': 'Read-only по умолчанию',
		'safety.message':
			'MVP по умолчанию работает только на чтение. GnuCash Desktop остаётся главным редактором; любые web-записи требуют отдельного post-MVP feature flag.',
		'dashboard.title': 'Обзор',
		'accounts.kicker': 'Счета',
		'accounts.title': 'Дерево счетов',
		'transactions.kicker': 'Транзакции',
		'transactions.title': 'Просмотр транзакций',
		'books.kicker': 'Книги',
		'books.title': 'Управление книгами',
		'books.subtitle':
			'Книги доступны только для просмотра метаданных. Эта страница показывает уже настроенные книги, доступные вашей учётной записи; она не добавляет редактирование данных GnuCash.',
		'books.activeDefault': 'Активная/основная книга',
		'books.configuredTitle': 'Настроенные книги',
		'books.hiddenPolicy': 'Архивные и недоступные книги скрываются или блокируются API.',
		'books.noMutationBadge': 'Без загрузки, удаления и редактирования данных GnuCash',
		'books.currentBook': 'Текущая книга',
		'books.defaultBook': 'Активная/основная книга',
		'books.readOnlyBadge': 'Только чтение',
		'books.accessibleBadge': 'Статус доступа: доступна',
		'books.baseCurrency': 'Базовая валюта',
		'books.storageType': 'Тип хранения',
		'books.readonlyStatus': 'Read-only статус',
		'books.safetyNote': 'GnuCash Desktop остаётся главным редактором.',
		'books.noBooks': 'Для этой учётной записи нет доступных настроенных книг.',
		'books.notConfigured': 'Не настроено',
		'books.unknown': 'Неизвестно',
		'books.accessRole': 'Роль доступа',
		'books.status': 'Статус метаданных',
		'books.openSafeViews': 'Открыть безопасные разделы',
		'books.viewAccounts': 'Счета',
		'books.browseTransactions': 'Транзакции',
		'books.viewScheduled': 'Плановые метаданные',
		'books.dashboardSummary': 'Обзор',
		'books.noManagementActions': 'На этой read-only странице нет действий управления реестром книг.'
	}
};
