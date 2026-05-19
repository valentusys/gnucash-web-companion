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
	| 'books.emptyTitle'
	| 'books.emptyMessage'
	| 'books.notConfigured'
	| 'books.unknown'
	| 'books.accessRole'
	| 'books.status'
	| 'books.openSafeViews'
	| 'books.viewAccounts'
	| 'books.browseTransactions'
	| 'books.viewScheduled'
	| 'books.dashboardSummary'
	| 'books.noManagementActions'
	| 'transactions.filters.title'
	| 'transactions.filters.subtitle'
	| 'transactions.filters.filteredView'
	| 'transactions.filters.datePresets'
	| 'transactions.filters.datePresetAria'
	| 'transactions.filters.datePresetHelp'
	| 'transactions.filters.activeSummaryTitle'
	| 'transactions.filters.search'
	| 'transactions.filters.searchPlaceholder'
	| 'transactions.filters.account'
	| 'transactions.filters.accountScope'
	| 'transactions.filters.accountId'
	| 'transactions.filters.lockedAccountHelp'
	| 'transactions.filters.allAccounts'
	| 'transactions.filters.customDateRange'
	| 'transactions.filters.from'
	| 'transactions.filters.to'
	| 'transactions.filters.startDateError'
	| 'transactions.filters.state'
	| 'transactions.filters.anyState'
	| 'transactions.filters.stateUnreconciled'
	| 'transactions.filters.stateCleared'
	| 'transactions.filters.stateReconciled'
	| 'transactions.filters.stateVoided'
	| 'transactions.filters.stateHelp'
	| 'transactions.filters.minAmount'
	| 'transactions.filters.maxAmount'
	| 'transactions.filters.amountError'
	| 'transactions.filters.submit'
	| 'transactions.filters.clear'
	| 'transactions.filters.summary.search'
	| 'transactions.filters.summary.account'
	| 'transactions.filters.summary.dates'
	| 'transactions.filters.summary.from'
	| 'transactions.filters.summary.to'
	| 'transactions.filters.summary.amount'
	| 'transactions.filters.summary.minAmount'
	| 'transactions.filters.summary.maxAmount'
	| 'transactions.filters.summary.state'
	| 'transactions.export.button'
	| 'transactions.export.buttonWithFilters'
	| 'transactions.export.statusFiltered'
	| 'transactions.export.statusUnfiltered'
	| 'transactions.export.accountButton'
	| 'transactions.export.accountButtonWithFilters'
	| 'transactions.export.accountStatus';

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
		'books.emptyTitle': 'No accessible books found',
		'books.emptyMessage':
			'No configured books are available to this account. Confirm the book registry and access metadata, then sign in again or ask the administrator to grant read-only access.',
		'books.notConfigured': 'Not configured',
		'books.unknown': 'Unknown',
		'books.accessRole': 'Access role',
		'books.status': 'Metadata status',
		'books.openSafeViews': 'Open safe views',
		'books.viewAccounts': 'View accounts',
		'books.browseTransactions': 'Browse transactions',
		'books.viewScheduled': 'View scheduled metadata',
		'books.dashboardSummary': 'Dashboard summary',
		'books.noManagementActions': 'No registry management actions are available on this read-only page.',
		'transactions.filters.title': 'Transaction filters',
		'transactions.filters.subtitle':
			'Narrow the read-only transaction list and CSV export; filters never modify your GnuCash book.',
		'transactions.filters.filteredView': 'Filtered view',
		'transactions.filters.datePresets': 'Date presets',
		'transactions.filters.datePresetAria': 'Transaction date range presets',
		'transactions.filters.datePresetHelp':
			'Presets update only the ordinary date_from/date_to filters; the list and CSV export stay read-only and use the same filtered view.',
		'transactions.filters.activeSummaryTitle': 'Active filters applied to list and CSV export',
		'transactions.filters.search': 'Search',
		'transactions.filters.searchPlaceholder': 'Description, notes, or split memo...',
		'transactions.filters.account': 'Account',
		'transactions.filters.accountScope': 'Account scope',
		'transactions.filters.accountId': 'Account ID',
		'transactions.filters.lockedAccountHelp':
			"This account detail view is fixed to this account; other filters narrow only this account's transactions.",
		'transactions.filters.allAccounts': 'All accounts',
		'transactions.filters.customDateRange': 'Custom date range',
		'transactions.filters.from': 'From',
		'transactions.filters.to': 'To',
		'transactions.filters.startDateError': 'Start date must be earlier than or equal to end date.',
		'transactions.filters.state': 'State',
		'transactions.filters.anyState': 'Any state',
		'transactions.filters.stateUnreconciled': 'Unreconciled',
		'transactions.filters.stateCleared': 'Cleared',
		'transactions.filters.stateReconciled': 'Reconciled',
		'transactions.filters.stateVoided': 'Voided',
		'transactions.filters.stateHelp':
			'Filters by the GnuCash split reconciliation state; it does not edit transactions.',
		'transactions.filters.minAmount': 'Min amount',
		'transactions.filters.maxAmount': 'Max amount',
		'transactions.filters.amountError': 'Minimum amount must be less than or equal to maximum amount.',
		'transactions.filters.submit': 'Filter',
		'transactions.filters.clear': 'Clear filters',
		'transactions.filters.summary.search': 'Search',
		'transactions.filters.summary.account': 'Account',
		'transactions.filters.summary.dates': 'Dates',
		'transactions.filters.summary.from': 'From',
		'transactions.filters.summary.to': 'To',
		'transactions.filters.summary.amount': 'Amount',
		'transactions.filters.summary.minAmount': 'Min amount',
		'transactions.filters.summary.maxAmount': 'Max amount',
		'transactions.filters.summary.state': 'State',
		'transactions.export.button': 'Export CSV',
		'transactions.export.buttonWithFilters': 'Export CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Exports the current read-only filtered view, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.statusUnfiltered':
			'Exports this read-only transaction list, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.accountButton': 'Export account CSV',
		'transactions.export.accountButtonWithFilters': 'Export account CSV ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Exports this account-scoped read-only filtered view with the same search/date/amount/state filters.'
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
		'books.emptyTitle': 'Нет доступных книг',
		'books.emptyMessage':
			'Для этой учётной записи нет настроенных доступных книг. Проверьте реестр книг и права доступа, затем войдите снова или попросите администратора выдать read-only доступ.',
		'books.notConfigured': 'Не настроено',
		'books.unknown': 'Неизвестно',
		'books.accessRole': 'Роль доступа',
		'books.status': 'Статус метаданных',
		'books.openSafeViews': 'Открыть безопасные разделы',
		'books.viewAccounts': 'Счета',
		'books.browseTransactions': 'Транзакции',
		'books.viewScheduled': 'Плановые метаданные',
		'books.dashboardSummary': 'Обзор',
		'books.noManagementActions': 'На этой read-only странице нет действий управления реестром книг.',
		'transactions.filters.title': 'Фильтры транзакций',
		'transactions.filters.subtitle':
			'Сужают read-only список транзакций и CSV export; фильтры никогда не изменяют вашу книгу GnuCash.',
		'transactions.filters.filteredView': 'Отфильтрованный вид',
		'transactions.filters.datePresets': 'Быстрые даты',
		'transactions.filters.datePresetAria': 'Быстрые диапазоны дат транзакций',
		'transactions.filters.datePresetHelp':
			'Быстрые даты меняют только обычные фильтры date_from/date_to; список и CSV export остаются read-only и используют тот же отфильтрованный вид.',
		'transactions.filters.activeSummaryTitle': 'Активные фильтры применяются к списку и CSV export',
		'transactions.filters.search': 'Поиск',
		'transactions.filters.searchPlaceholder': 'Описание, notes или split memo...',
		'transactions.filters.account': 'Счёт',
		'transactions.filters.accountScope': 'Область счёта',
		'transactions.filters.accountId': 'ID счёта',
		'transactions.filters.lockedAccountHelp':
			'Детальная страница счёта зафиксирована на этом счёте; остальные фильтры сужают только транзакции этого счёта.',
		'transactions.filters.allAccounts': 'Все счета',
		'transactions.filters.customDateRange': 'Свой диапазон дат',
		'transactions.filters.from': 'С',
		'transactions.filters.to': 'По',
		'transactions.filters.startDateError': 'Дата начала должна быть раньше даты окончания или равна ей.',
		'transactions.filters.state': 'Состояние',
		'transactions.filters.anyState': 'Любое состояние',
		'transactions.filters.stateUnreconciled': 'Не сверено',
		'transactions.filters.stateCleared': 'Очищено',
		'transactions.filters.stateReconciled': 'Сверено',
		'transactions.filters.stateVoided': 'Аннулировано',
		'transactions.filters.stateHelp':
			'Фильтрует по состоянию сверки split в GnuCash; транзакции не редактируются.',
		'transactions.filters.minAmount': 'Мин. сумма',
		'transactions.filters.maxAmount': 'Макс. сумма',
		'transactions.filters.amountError': 'Минимальная сумма должна быть меньше максимальной или равна ей.',
		'transactions.filters.submit': 'Фильтровать',
		'transactions.filters.clear': 'Сбросить фильтры',
		'transactions.filters.summary.search': 'Поиск',
		'transactions.filters.summary.account': 'Счёт',
		'transactions.filters.summary.dates': 'Даты',
		'transactions.filters.summary.from': 'С',
		'transactions.filters.summary.to': 'По',
		'transactions.filters.summary.amount': 'Сумма',
		'transactions.filters.summary.minAmount': 'Мин. сумма',
		'transactions.filters.summary.maxAmount': 'Макс. сумма',
		'transactions.filters.summary.state': 'Состояние',
		'transactions.export.button': 'Экспорт CSV',
		'transactions.export.buttonWithFilters': 'Экспорт CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Экспортирует текущий read-only отфильтрованный вид, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.statusUnfiltered':
			'Экспортирует этот read-only список транзакций, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.accountButton': 'Экспорт CSV по счёту',
		'transactions.export.accountButtonWithFilters': 'Экспорт CSV по счёту ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Экспортирует read-only отфильтрованный вид в рамках этого счёта с теми же фильтрами поиска/дат/сумм/состояния.'
	}
};
