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
	| 'login.error.missingCredentials'
	| 'login.error.serviceUnavailable'
	| 'login.error.invalidCredentials'
	| 'login.error.operatorConfiguration'
	| 'nav.dashboard'
	| 'nav.accounts'
	| 'nav.transactions'
	| 'nav.scheduled'
	| 'nav.books'
	| 'nav.logout'
	| 'safety.statusLabel'
	| 'safety.badge'
	| 'safety.message'
	| 'safety.currentBook'
	| 'safety.noActiveBook'
	| 'safety.reviewBooks'
	| 'error.badgeWithCode'
	| 'error.badgeNetwork'
	| 'error.forbiddenTitle'
	| 'error.forbiddenMessage'
	| 'error.notFoundTitle'
	| 'error.notFoundMessage'
	| 'error.serviceTitle'
	| 'error.serviceMessage'
	| 'error.genericTitle'
	| 'error.genericMessage'
	| 'error.retry'
	| 'error.retryPage'
	| 'error.backDashboard'
	| 'dashboard.title'
	| 'accounts.kicker'
	| 'accounts.title'
	| 'accounts.bookLabel'
	| 'accounts.loading'
	| 'accounts.filter.label'
	| 'accounts.filter.placeholder'
	| 'accounts.filter.filteredStatus'
	| 'accounts.filter.allStatus'
	| 'accounts.filter.noMatchesTitle'
	| 'accounts.filter.noMatchesMessage'
	| 'accounts.column.name'
	| 'accounts.column.type'
	| 'accounts.column.balance'
	| 'accounts.column.currency'
	| 'accounts.emptyTitle'
	| 'accounts.emptyMessage'
	| 'accounts.emptyAction'
	| 'dashboard.loading'
	| 'dashboard.loadFailed'
	| 'dashboard.summary'
	| 'dashboard.conservativeTotals'
	| 'dashboard.reportingBasis'
	| 'dashboard.currencyConversion'
	| 'dashboard.currencyConversionIncluded'
	| 'dashboard.currencyConversionNotIncluded'
	| 'dashboard.netWorth'
	| 'dashboard.assets'
	| 'dashboard.liabilities'
	| 'dashboard.incomeThisMonth'
	| 'dashboard.expensesThisMonth'
	| 'dashboard.viewMonthlyFilter'
	| 'dashboard.drilldownSafety'
	| 'dashboard.recentTransactions'
	| 'dashboard.recentTransactionsHelp'
	| 'dashboard.viewTransactions'
	| 'dashboard.noRecentTransactions'
	| 'dashboard.expensesByAccount'
	| 'dashboard.expensesByAccountHelp'
	| 'dashboard.noExpenses'
	| 'dashboard.cashflow'
	| 'dashboard.cashflowHelp'
	| 'dashboard.noCashflow'
	| 'dashboard.cashflowIn'
	| 'dashboard.cashflowOut'
	| 'dashboard.cashflowNet'
	| 'home.subtitle'
	| 'transactions.kicker'
	| 'transactions.title'
	| 'transactionDetail.back'
	| 'transactionDetail.kicker'
	| 'transactionDetail.noDescription'
	| 'transactionDetail.helper'
	| 'transactionDetail.date'
	| 'transactionDetail.currency'
	| 'transactionDetail.splits'
	| 'transactionDetail.id'
	| 'transactionDetail.splitSingular'
	| 'transactionDetail.splitPlural'
	| 'transactionDetail.deleteTitle'
	| 'transactionDetail.deleteHelper'
	| 'transactionDetail.deleteAcknowledgement'
	| 'transactionDetail.deleteButton'
	| 'transactionDetail.deleteConfirm'
	| 'transactionSplits.title'
	| 'transactionSplits.helper'
	| 'transactionSplits.empty'
	| 'transactionSplits.splitAccount'
	| 'transactionSplits.memo'
	| 'transactionSplits.noMemo'
	| 'transactionSplits.reconciliation'
	| 'transactionSplits.accountId'
	| 'transactionSplits.caption'
	| 'transactionSplits.stateNotProvided'
	| 'transactionSplits.stateUnknown'
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
	| 'books.storageDiagnostics'
	| 'books.safeNextActions'
	| 'books.privatePathRedacted'
	| 'books.openSafeViews'
	| 'books.viewAccounts'
	| 'books.browseTransactions'
	| 'books.viewScheduled'
	| 'books.dashboardSummary'
	| 'books.noManagementActions'
	| 'books.operatorGuidanceTitle'
	| 'books.metadataSource'
	| 'books.dataAccess'
	| 'books.readOnlyDefault'
	| 'books.unsupportedActions'
	| 'books.noUnsupportedActions'
	| 'books.currentDefaultExplanation'
	| 'books.safeOperatorGuidance'
	| 'books.contextRecoveryTitle'
	| 'books.contextRecoveryStale'
	| 'books.contextRecoveryNoBooks'
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
	| 'transactions.listStatus.title'
	| 'transactions.listStatus.order'
	| 'transactions.listStatus.pageRange'
	| 'transactions.listStatus.emptyPage'
	| 'transactions.listStatus.filtersApplied'
	| 'transactions.listStatus.noFilters'
	| 'transactions.listStatus.exportParity'
	| 'transactions.export.button'
	| 'transactions.export.buttonWithFilters'
	| 'transactions.export.statusFiltered'
	| 'transactions.export.statusUnfiltered'
	| 'transactions.export.emptyStatus'
	| 'transactions.export.countStatus'
	| 'transactions.export.truncatedStatus'
	| 'transactions.export.accountButton'
	| 'transactions.export.accountButtonWithFilters'
	| 'transactions.export.accountStatus'
	| 'scheduled.title'
	| 'scheduled.kicker'
	| 'scheduled.subtitle'
	| 'scheduled.activeBook'
	| 'scheduled.recurringMetadata'
	| 'scheduled.metadataHelp'
	| 'scheduled.readOnlyBadge'
	| 'scheduled.statusFilter'
	| 'scheduled.templateFilter'
	| 'scheduled.sortDisplay'
	| 'scheduled.all'
	| 'scheduled.enabled'
	| 'scheduled.disabled'
	| 'scheduled.templatePresent'
	| 'scheduled.noTemplateReference'
	| 'scheduled.startDate'
	| 'scheduled.endDate'
	| 'scheduled.lastOccurred'
	| 'scheduled.name'
	| 'scheduled.enabledFirst'
	| 'scheduled.shownStatus'
	| 'scheduled.clearFilters'
	| 'scheduled.unnamed'
	| 'scheduled.templateAccount'
	| 'scheduled.occurrences'
	| 'scheduled.occurrencesValue'
	| 'scheduled.autoCreateNotify'
	| 'scheduled.advanceDays'
	| 'scheduled.advanceDaysValue'
	| 'scheduled.recurrenceMetadata'
	| 'scheduled.noRecurrenceMetadata'
	| 'scheduled.noMatchesTitle'
	| 'scheduled.noMatchesMessage'
	| 'scheduled.noMatchesAria'
	| 'scheduled.emptyTitle'
	| 'scheduled.emptyMessage'
	| 'scheduled.emptyAria'
	| 'scheduled.browseTransactions'
	| 'scheduled.reviewBooks'
	| 'scheduled.notConfigured'
	| 'scheduled.yes'
	| 'scheduled.no'
	| 'scheduled.recurrenceEvery'
	| 'scheduled.recurrenceFrom'
	| 'scheduled.recurrenceWeekend'
	| 'scheduled.recurrenceUnavailable';

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
		'login.error.missingCredentials': 'Enter username and password.',
		'login.error.serviceUnavailable': 'Authentication service is unavailable.',
		'login.error.invalidCredentials': 'Invalid username or password.',
		'login.error.operatorConfiguration':
			'Login is not fully configured. Check JWT_SECRET and APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD in your local .env/deployment environment, restart the service, and keep GnuCash data read-only.',
		'nav.dashboard': 'Dashboard',
		'nav.accounts': 'Accounts',
		'nav.transactions': 'Transactions',
		'nav.scheduled': 'Scheduled',
		'nav.books': 'Books',
		'nav.logout': 'Logout',
		'safety.statusLabel': 'Read-only safety status',
		'safety.badge': 'Read-only by default',
		'safety.message':
			'Read-only MVP by default. GNUCASH_WRITES_ENABLED=false is the safe default; GnuCash Desktop remains the authoritative editor.',
		'safety.currentBook': 'Current book',
		'safety.noActiveBook': 'No active book selected',
		'safety.reviewBooks': 'Review books',
		'error.badgeWithCode': 'Error {statusCode}',
		'error.badgeNetwork': 'API/network error',
		'error.forbiddenTitle': 'Access denied',
		'error.forbiddenMessage': 'Your account cannot access this read-only view or book. Check the selected book or sign in with an account that has access.',
		'error.notFoundTitle': 'Page or book not found',
		'error.notFoundMessage': 'The requested page, book, account, or transaction was not found. It may be unavailable, archived, or hidden by access rules.',
		'error.serviceTitle': 'Service temporarily unavailable',
		'error.serviceMessage':
			'The API or network request failed while loading this read-only view. Verify the service is running, check /health for redacted first-run diagnostics, then review local .env and book volume settings before trying again.',
		'error.genericTitle': 'Something went wrong',
		'error.genericMessage': 'An unexpected API or network error occurred. Please try again or return to a safe read-only page.',
		'error.retry': 'Retry',
		'error.retryPage': 'Retry this page',
		'error.backDashboard': 'Back to dashboard',
		'dashboard.title': 'Dashboard',
		'accounts.kicker': 'Accounts',
		'accounts.title': 'Account tree',
		'accounts.bookLabel': 'Book',
		'accounts.loading': 'Loading account tree for the selected read-only book…',
		'accounts.filter.label': 'Filter accounts',
		'accounts.filter.placeholder': 'Search by account name, full path, type, or currency',
		'accounts.filter.filteredStatus': 'Showing {filtered} of {total} accounts. Matching descendants stay grouped with their parent path.',
		'accounts.filter.allStatus': 'Showing all {total} accounts. Use the filter to narrow large read-only account trees without changing the book.',
		'accounts.filter.noMatchesTitle': 'No accounts match this filter.',
		'accounts.filter.noMatchesMessage': 'Clear the account filter to return to the full read-only account tree.',
		'accounts.column.name': 'Name',
		'accounts.column.type': 'Type',
		'accounts.column.balance': 'Balance',
		'accounts.column.currency': 'Currency',
		'accounts.emptyTitle': 'No accounts found',
		'accounts.emptyMessage': 'The selected read-only book did not return any accounts. Verify the active test-copy book and accessible book metadata before relying on this view.',
		'accounts.emptyAction': 'Review available books',
		'dashboard.loading': 'Loading dashboard summary for the selected read-only book…',
		'dashboard.loadFailed': 'Failed to load dashboard data',
		'dashboard.summary': 'Summary',
		'dashboard.conservativeTotals': 'Conservative dashboard totals',
		'dashboard.reportingBasis': 'Reporting basis',
		'dashboard.currencyConversion': 'Currency conversion',
		'dashboard.currencyConversionIncluded': 'included',
		'dashboard.currencyConversionNotIncluded': 'not included',
		'dashboard.netWorth': 'Net Worth',
		'dashboard.assets': 'Assets',
		'dashboard.liabilities': 'Liabilities',
		'dashboard.incomeThisMonth': 'Income This Month',
		'dashboard.expensesThisMonth': 'Expenses This Month',
		'dashboard.viewMonthlyFilter': "View this month's transaction filter",
		'dashboard.drilldownSafety':
			'Drilldowns preserve the active book and use existing read-only transaction URL filters. Dashboard totals remain base-currency-only with no FX conversion; transaction filter views are evidence for the same period/account context, not invented recomputations.',
		'dashboard.recentTransactions': 'Recent Transactions',
		'dashboard.recentTransactionsHelp': 'Same read-only transaction list, newest first; CSV export uses matching filters.',
		'dashboard.viewTransactions': 'View transactions',
		'dashboard.noRecentTransactions': 'No transactions found.',
		'dashboard.expensesByAccount': 'Expenses by Account',
		'dashboard.expensesByAccountHelp': 'Base-currency-only reporting; account links open the same read-only date/account filter used for CSV parity.',
		'dashboard.noExpenses': 'No expenses found for the selected period.',
		'dashboard.cashflow': 'Cashflow',
		'dashboard.cashflowHelp': 'Monthly drilldowns use date_from/date_to transaction filters for the active book. No FX conversion is inferred.',
		'dashboard.noCashflow': 'No cashflow data for the selected period.',
		'dashboard.cashflowIn': 'In',
		'dashboard.cashflowOut': 'Out',
		'dashboard.cashflowNet': 'Net',
		'home.subtitle': 'Modern self-hosted read-only companion for existing GnuCash books.',
		'transactions.kicker': 'Transactions',
		'transactions.title': 'Browse transactions',
		'transactionDetail.back': 'Back to transactions',
		'transactionDetail.kicker': 'Transaction detail',
		'transactionDetail.noDescription': 'No description',
		'transactionDetail.helper': 'Read-only view of the selected GnuCash transaction. Split rows below show memo and reconciliation metadata when available.',
		'transactionDetail.date': 'Date',
		'transactionDetail.currency': 'Currency',
		'transactionDetail.splits': 'Splits',
		'transactionDetail.id': 'ID',
		'transactionDetail.splitSingular': 'split',
		'transactionDetail.splitPlural': 'splits',
		'transactionDetail.deleteTitle': 'Experimental delete transaction',
		'transactionDetail.deleteHelper': 'This button is hidden unless write mode is explicitly enabled. Use only ignored copied/disposable test books in APP_ENV=test; GnuCash Desktop remains the authoritative editor.',
		'transactionDetail.deleteAcknowledgement': 'I acknowledge this experimental DELETE is for ignored disposable/test copies only and requires backup, audit, and lock-release checks.',
		'transactionDetail.deleteButton': 'Delete transaction',
		'transactionDetail.deleteConfirm': 'Delete this transaction from the disposable/test GnuCash book? This experimental write-alpha action creates a backup first and cannot be undone here.',
		'transactionSplits.title': 'Splits',
		'transactionSplits.helper': 'Read-only split metadata from GnuCash: account, memo, reconciliation state, and amount.',
		'transactionSplits.empty': 'No split rows were returned for this transaction. The read-only detail view does not invent balancing data.',
		'transactionSplits.splitAccount': 'Split {index} account',
		'transactionSplits.memo': 'Memo',
		'transactionSplits.noMemo': 'No memo',
		'transactionSplits.reconciliation': 'Reconciliation',
		'transactionSplits.accountId': 'Account ID',
		'transactionSplits.caption': 'Transaction split rows with account, memo, reconciliation state, and amount',
		'transactionSplits.stateNotProvided': 'Not provided',
		'transactionSplits.stateUnknown': 'State {state}',
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
			'No configured books are available to this account. Confirm the book registry and access metadata, then sign in again or ask the administrator to grant read-only access. For first run, also verify GNUCASH_DEFAULT_BOOK_PATH points to a mounted readable test-copy book and check /health for redacted diagnostics.',
		'books.notConfigured': 'Not configured',
		'books.unknown': 'Unknown',
		'books.accessRole': 'Access role',
		'books.status': 'Metadata status',
		'books.storageDiagnostics': 'Storage diagnostics',
		'books.safeNextActions': 'Safe next actions',
		'books.privatePathRedacted': 'Private filesystem path is intentionally not shown.',
		'books.openSafeViews': 'Open safe views',
		'books.viewAccounts': 'View accounts',
		'books.browseTransactions': 'Browse transactions',
		'books.viewScheduled': 'View scheduled metadata',
		'books.dashboardSummary': 'Dashboard summary',
		'books.noManagementActions': 'No registry management actions are available on this read-only page.',
		'books.operatorGuidanceTitle': 'Self-hosting operator guidance',
		'books.metadataSource': 'Metadata source',
		'books.dataAccess': 'Listing data access',
		'books.readOnlyDefault': 'Read-only default',
		'books.unsupportedActions': 'Unsupported MVP management actions',
		'books.noUnsupportedActions': 'No management actions are exposed for this book.',
		'books.currentDefaultExplanation':
			'Current marks the book selected for this browser session; default marks the configured fallback book. Both are read-only context labels, not management controls.',
		'books.safeOperatorGuidance':
			'Use the host configuration and app metadata database to change registered books. This page intentionally does not expose upload, delete, default-changing, or registry-edit actions in the MVP.',
		'books.contextRecoveryTitle': 'Book context reviewed',
		'books.contextRecoveryStale':
			'The selected-book cookie was invalid or no longer accessible, so this browser session was safely moved to an accessible read-only book. Review the current/default labels before opening a view.',
		'books.contextRecoveryNoBooks':
			'No accessible configured books are available for this account. The selected-book cookie was cleared; archived and unauthorized books remain hidden or blocked.',
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
		'transactions.listStatus.title': 'Current read-only view',
		'transactions.listStatus.order': 'Sorted newest first by transaction date.',
		'transactions.listStatus.pageRange': 'Showing {start}–{end} of {total} matching transactions on this page.',
		'transactions.listStatus.emptyPage': 'No matching transactions on this page.',
		'transactions.listStatus.filtersApplied': '{count} active {filterLabel}; the list, pagination, and CSV export use the same URL filters.',
		'transactions.listStatus.noFilters': 'No transaction filters are active; CSV export uses the current unfiltered read-only view.',
		'transactions.listStatus.exportParity': 'CSV export ignores page offset, starts from the first matching row, and is capped at 10,000 rows.',
		'transactions.export.button': 'Export CSV',
		'transactions.export.buttonWithFilters': 'Export CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Exports the current read-only filtered view, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.statusUnfiltered':
			'Exports this read-only transaction list, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.emptyStatus':
			'The current export would contain only the CSV header because no matching transactions are visible.',
		'transactions.export.countStatus':
			'Current matching rows before the cap: {total}. CSV amounts stay string values; no currency conversion is performed.',
		'transactions.export.truncatedStatus':
			'Current matching rows before the cap: {total}; export will include only the first 10,000 rows. Narrow filters for a complete subset.',
		'transactions.export.accountButton': 'Export account CSV',
		'transactions.export.accountButtonWithFilters': 'Export account CSV ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Exports this account-scoped read-only filtered view with the same search/date/amount/state filters.',
		'scheduled.title': 'Scheduled transactions',
		'scheduled.kicker': 'Read-only scheduled transaction awareness',
		'scheduled.subtitle':
			'Safe summary metadata from the active GnuCash book. This pre-alpha page does not create, edit, delete, or calculate upcoming schedule predictions for scheduled transactions. Use GnuCash Desktop as the authoritative editor.',
		'scheduled.activeBook': 'Active book',
		'scheduled.recurringMetadata': 'Recurring metadata',
		'scheduled.metadataHelp':
			'Only safe schedule fields are shown. Template split details and private raw SQL are not exposed. Filters and sorting are URL-only display controls; they do not save scheduled metadata in browser storage.',
		'scheduled.readOnlyBadge': 'Read-only · no scheduling editor',
		'scheduled.statusFilter': 'Status filter',
		'scheduled.templateFilter': 'Template metadata filter',
		'scheduled.sortDisplay': 'Sort display',
		'scheduled.all': 'All',
		'scheduled.enabled': 'Enabled',
		'scheduled.disabled': 'Disabled',
		'scheduled.templatePresent': 'Template present',
		'scheduled.noTemplateReference': 'No template reference',
		'scheduled.startDate': 'Start date',
		'scheduled.endDate': 'End date',
		'scheduled.lastOccurred': 'Last occurred',
		'scheduled.name': 'Name',
		'scheduled.enabledFirst': 'Enabled first',
		'scheduled.shownStatus':
			'Showing {shown} of {total} safe scheduled metadata rows. No template split amounts, accounts, memos, transaction descriptions, or raw SQL are exposed.',
		'scheduled.clearFilters': 'Clear scheduled filters',
		'scheduled.unnamed': 'Unnamed scheduled transaction',
		'scheduled.templateAccount': 'Template account',
		'scheduled.occurrences': 'Occurrences',
		'scheduled.occurrencesValue': 'total {total} · remaining {remaining}',
		'scheduled.autoCreateNotify': 'Auto-create / notify',
		'scheduled.advanceDays': 'Advance days',
		'scheduled.advanceDaysValue': 'create {create} · notify {notify}',
		'scheduled.recurrenceMetadata': 'Recurrence metadata',
		'scheduled.noRecurrenceMetadata': 'No safe recurrence metadata is available through the adapter.',
		'scheduled.noMatchesTitle': 'No scheduled transactions match these display filters',
		'scheduled.noMatchesMessage':
			'The active book has scheduled metadata, but the current URL-only scheduled filters hide every row. Clear filters to return to the full safe read-only metadata view.',
		'scheduled.noMatchesAria': 'No scheduled transactions match display filters',
		'scheduled.emptyTitle': 'No scheduled transactions found',
		'scheduled.emptyMessage':
			'No scheduled transactions are available through the safe read-only adapter for this book. If the book uses scheduled transactions, manage and review them in GnuCash Desktop.',
		'scheduled.emptyAria': 'No scheduled transactions found',
		'scheduled.browseTransactions': 'Browse transactions',
		'scheduled.reviewBooks': 'Review books',
		'scheduled.notConfigured': 'Not configured',
		'scheduled.yes': 'Yes',
		'scheduled.no': 'No',
		'scheduled.recurrenceEvery': 'every {count}',
		'scheduled.recurrenceFrom': 'from {date}',
		'scheduled.recurrenceWeekend': 'weekend: {value}',
		'scheduled.recurrenceUnavailable': 'Raw recurrence metadata unavailable'
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
		'login.error.missingCredentials': 'Введите имя пользователя и пароль.',
		'login.error.serviceUnavailable': 'Сервис аутентификации недоступен.',
		'login.error.invalidCredentials': 'Неверное имя пользователя или пароль.',
		'login.error.operatorConfiguration':
			'Вход настроен не полностью. Проверьте JWT_SECRET и APP_ADMIN_PASSWORD_HASH или APP_ADMIN_PASSWORD в локальном .env/deployment окружении, перезапустите сервис и оставьте данные GnuCash в read-only режиме.',
		'nav.dashboard': 'Обзор',
		'nav.accounts': 'Счета',
		'nav.transactions': 'Транзакции',
		'nav.scheduled': 'Плановые',
		'nav.books': 'Книги',
		'nav.logout': 'Выйти',
		'safety.statusLabel': 'Статус безопасности read-only режима',
		'safety.badge': 'Read-only по умолчанию',
		'safety.message':
			'MVP по умолчанию работает только на чтение. GNUCASH_WRITES_ENABLED=false — безопасное значение по умолчанию; GnuCash Desktop остаётся главным редактором.',
		'safety.currentBook': 'Текущая книга',
		'safety.noActiveBook': 'Активная книга не выбрана',
		'safety.reviewBooks': 'Проверить книги',
		'error.badgeWithCode': 'Ошибка {statusCode}',
		'error.badgeNetwork': 'Ошибка API/сети',
		'error.forbiddenTitle': 'Доступ запрещён',
		'error.forbiddenMessage': 'Эта учётная запись не может открыть этот read-only раздел или книгу. Проверьте выбранную книгу или войдите под учётной записью с доступом.',
		'error.notFoundTitle': 'Страница или книга не найдена',
		'error.notFoundMessage': 'Запрошенная страница, книга, счёт или транзакция не найдены. Объект может быть недоступен, архивирован или скрыт правилами доступа.',
		'error.serviceTitle': 'Сервис временно недоступен',
		'error.serviceMessage':
			'API или сетевой запрос не сработал при загрузке этого read-only раздела. Убедитесь, что сервис запущен, проверьте /health для редактированной first-run диагностики, затем проверьте локальный .env и volume с книгой перед повторной попыткой.',
		'error.genericTitle': 'Что-то пошло не так',
		'error.genericMessage': 'Произошла неожиданная ошибка API или сети. Повторите попытку или вернитесь к безопасной read-only странице.',
		'error.retry': 'Повторить',
		'error.retryPage': 'Повторить эту страницу',
		'error.backDashboard': 'Назад к обзору',
		'dashboard.title': 'Обзор',
		'accounts.kicker': 'Счета',
		'accounts.title': 'Дерево счетов',
		'accounts.bookLabel': 'Книга',
		'accounts.loading': 'Загрузка дерева счетов для выбранной read-only книги…',
		'accounts.filter.label': 'Фильтр счетов',
		'accounts.filter.placeholder': 'Поиск по названию счёта, полному пути, типу или валюте',
		'accounts.filter.filteredStatus': 'Показано {filtered} из {total} счетов. Совпадающие дочерние счета остаются вместе с родительским путём.',
		'accounts.filter.allStatus': 'Показаны все счета: {total}. Используйте фильтр, чтобы сузить большое read-only дерево счетов без изменения книги.',
		'accounts.filter.noMatchesTitle': 'Нет счетов по этому фильтру.',
		'accounts.filter.noMatchesMessage': 'Очистите фильтр счетов, чтобы вернуться к полному read-only дереву счетов.',
		'accounts.column.name': 'Название',
		'accounts.column.type': 'Тип',
		'accounts.column.balance': 'Баланс',
		'accounts.column.currency': 'Валюта',
		'accounts.emptyTitle': 'Счета не найдены',
		'accounts.emptyMessage': 'Выбранная read-only книга не вернула счета. Проверьте активную test-copy книгу и доступные метаданные книги, прежде чем полагаться на этот вид.',
		'accounts.emptyAction': 'Проверить доступные книги',
		'dashboard.loading': 'Загрузка dashboard summary для выбранной read-only книги…',
		'dashboard.loadFailed': 'Не удалось загрузить данные обзора',
		'dashboard.summary': 'Сводка',
		'dashboard.conservativeTotals': 'Консервативные итоги dashboard',
		'dashboard.reportingBasis': 'База отчёта',
		'dashboard.currencyConversion': 'Конвертация валют',
		'dashboard.currencyConversionIncluded': 'включена',
		'dashboard.currencyConversionNotIncluded': 'не включена',
		'dashboard.netWorth': 'Чистая стоимость',
		'dashboard.assets': 'Активы',
		'dashboard.liabilities': 'Обязательства',
		'dashboard.incomeThisMonth': 'Доходы за месяц',
		'dashboard.expensesThisMonth': 'Расходы за месяц',
		'dashboard.viewMonthlyFilter': 'Открыть фильтр транзакций за месяц',
		'dashboard.drilldownSafety':
			'Drilldown-ссылки сохраняют активную книгу и используют существующие read-only URL-фильтры транзакций. Итоги обзора остаются только в базовой валюте без FX-конвертации; виды транзакций — это evidence для того же периода/счёта, а не заново рассчитанные итоги.',
		'dashboard.recentTransactions': 'Последние транзакции',
		'dashboard.recentTransactionsHelp': 'Тот же read-only список транзакций, новые сначала; CSV export использует совпадающие фильтры.',
		'dashboard.viewTransactions': 'Открыть транзакции',
		'dashboard.noRecentTransactions': 'Транзакции не найдены.',
		'dashboard.expensesByAccount': 'Расходы по счетам',
		'dashboard.expensesByAccountHelp': 'Отчёт только в базовой валюте; ссылки по счетам открывают тот же read-only фильтр даты/счёта для parity с CSV.',
		'dashboard.noExpenses': 'За выбранный период расходы не найдены.',
		'dashboard.cashflow': 'Денежный поток',
		'dashboard.cashflowHelp': 'Месячные drilldown-ссылки используют фильтры транзакций date_from/date_to для активной книги. FX-конвертация не предполагается.',
		'dashboard.noCashflow': 'За выбранный период нет данных денежного потока.',
		'dashboard.cashflowIn': 'Вход',
		'dashboard.cashflowOut': 'Выход',
		'dashboard.cashflowNet': 'Итого',
		'home.subtitle': 'Современный self-hosted read-only companion для существующих книг GnuCash.',
		'transactions.kicker': 'Транзакции',
		'transactions.title': 'Просмотр транзакций',
		'transactionDetail.back': 'Назад к транзакциям',
		'transactionDetail.kicker': 'Детали транзакции',
		'transactionDetail.noDescription': 'Без описания',
		'transactionDetail.helper': 'Read-only просмотр выбранной транзакции GnuCash. Строки split ниже показывают memo и metadata сверки, если они доступны.',
		'transactionDetail.date': 'Дата',
		'transactionDetail.currency': 'Валюта',
		'transactionDetail.splits': 'Splits',
		'transactionDetail.id': 'ID',
		'transactionDetail.splitSingular': 'split',
		'transactionDetail.splitPlural': 'splits',
		'transactionDetail.deleteTitle': 'Экспериментальное удаление транзакции',
		'transactionDetail.deleteHelper': 'Эта кнопка скрыта, если write mode явно не включён. Используйте только ignored скопированные/disposable тестовые книги в APP_ENV=test; GnuCash Desktop остаётся главным редактором.',
		'transactionDetail.deleteAcknowledgement': 'Я понимаю, что экспериментальный DELETE предназначен только для ignored disposable/test копий и требует backup, audit и lock-release checks.',
		'transactionDetail.deleteButton': 'Удалить транзакцию',
		'transactionDetail.deleteConfirm': 'Удалить эту транзакцию из disposable/test книги GnuCash? Это экспериментальное write-alpha действие сначала создаёт backup и не может быть отменено здесь.',
		'transactionSplits.title': 'Splits',
		'transactionSplits.helper': 'Read-only metadata split из GnuCash: счёт, memo, состояние сверки и сумма.',
		'transactionSplits.empty': 'Для этой транзакции не вернулись строки split. Read-only просмотр деталей не придумывает балансирующие данные.',
		'transactionSplits.splitAccount': 'Split {index}: счёт',
		'transactionSplits.memo': 'Memo',
		'transactionSplits.noMemo': 'Нет memo',
		'transactionSplits.reconciliation': 'Сверка',
		'transactionSplits.accountId': 'ID счёта',
		'transactionSplits.caption': 'Строки split транзакции со счётом, memo, состоянием сверки и суммой',
		'transactionSplits.stateNotProvided': 'Не указано',
		'transactionSplits.stateUnknown': 'Состояние {state}',
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
			'Для этой учётной записи нет настроенных доступных книг. Проверьте реестр книг и права доступа, затем войдите снова или попросите администратора выдать read-only доступ. При первом запуске также проверьте, что GNUCASH_DEFAULT_BOOK_PATH указывает на смонтированную читаемую test-copy книгу, и используйте /health для redacted diagnostics.',
		'books.notConfigured': 'Не настроено',
		'books.unknown': 'Неизвестно',
		'books.accessRole': 'Роль доступа',
		'books.status': 'Статус метаданных',
		'books.storageDiagnostics': 'Диагностика хранения',
		'books.safeNextActions': 'Безопасные следующие действия',
		'books.privatePathRedacted': 'Приватный путь файловой системы намеренно не показан.',
		'books.openSafeViews': 'Открыть безопасные разделы',
		'books.viewAccounts': 'Счета',
		'books.browseTransactions': 'Транзакции',
		'books.viewScheduled': 'Плановые метаданные',
		'books.dashboardSummary': 'Обзор',
		'books.noManagementActions': 'На этой read-only странице нет действий управления реестром книг.',
		'books.operatorGuidanceTitle': 'Подсказки для self-hosting оператора',
		'books.metadataSource': 'Источник метаданных',
		'books.dataAccess': 'Доступ к данным при списке',
		'books.readOnlyDefault': 'Read-only по умолчанию',
		'books.unsupportedActions': 'Неподдерживаемые действия управления в MVP',
		'books.noUnsupportedActions': 'Для этой книги не показаны действия управления.',
		'books.currentDefaultExplanation':
			'Текущая книга выбрана для этой браузерной сессии; основная книга — настроенный fallback. Оба статуса являются read-only метками контекста, а не элементами управления.',
		'books.safeOperatorGuidance':
			'Меняйте зарегистрированные книги через конфигурацию хоста и app metadata database. Эта MVP-страница намеренно не даёт загрузку, удаление, смену основной книги или редактирование реестра.',
		'books.contextRecoveryTitle': 'Контекст книги проверен',
		'books.contextRecoveryStale':
			'Cookie выбранной книги был некорректным или больше недоступен, поэтому браузерная сессия безопасно переключена на доступную read-only книгу. Проверьте метки текущей/основной книги перед открытием разделов.',
		'books.contextRecoveryNoBooks':
			'Для этой учётной записи нет доступных настроенных книг. Cookie выбранной книги очищен; архивные и неавторизованные книги остаются скрыты или заблокированы.',
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
		'transactions.listStatus.title': 'Текущий read-only вид',
		'transactions.listStatus.order': 'Сортировка: новые транзакции сначала по дате.',
		'transactions.listStatus.pageRange': 'Показаны {start}–{end} из {total} подходящих транзакций на этой странице.',
		'transactions.listStatus.emptyPage': 'На этой странице нет подходящих транзакций.',
		'transactions.listStatus.filtersApplied': '{count} активных {filterLabel}; список, пагинация и CSV export используют те же URL-фильтры.',
		'transactions.listStatus.noFilters': 'Активных фильтров транзакций нет; CSV export использует текущий нефильтрованный read-only вид.',
		'transactions.listStatus.exportParity': 'CSV export игнорирует page offset, начинает с первой подходящей строки и ограничен 10 000 строк.',
		'transactions.export.button': 'Экспорт CSV',
		'transactions.export.buttonWithFilters': 'Экспорт CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Экспортирует текущий read-only отфильтрованный вид, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.statusUnfiltered':
			'Экспортирует этот read-only список транзакций, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.emptyStatus':
			'Текущий export содержал бы только CSV header, потому что подходящие транзакции не видны.',
		'transactions.export.countStatus':
			'Текущих подходящих строк до ограничения: {total}. CSV amounts остаются string values; currency conversion не выполняется.',
		'transactions.export.truncatedStatus':
			'Текущих подходящих строк до ограничения: {total}; export включит только первые 10 000 строк. Сузьте фильтры для полного поднабора.',
		'transactions.export.accountButton': 'Экспорт CSV по счёту',
		'transactions.export.accountButtonWithFilters': 'Экспорт CSV по счёту ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Экспортирует read-only отфильтрованный вид в рамках этого счёта с теми же фильтрами поиска/дат/сумм/состояния.',
		'scheduled.title': 'Плановые транзакции',
		'scheduled.kicker': 'Read-only просмотр плановых транзакций',
		'scheduled.subtitle':
			'Безопасные сводные метаданные из активной книги GnuCash. Эта pre-alpha страница не создаёт, не редактирует, не удаляет и не рассчитывает будущие выполнения плановых транзакций. GnuCash Desktop остаётся главным редактором.',
		'scheduled.activeBook': 'Активная книга',
		'scheduled.recurringMetadata': 'Recurring metadata',
		'scheduled.metadataHelp':
			'Показываются только безопасные поля расписаний. Детали template split и приватный raw SQL не раскрываются. Фильтры и сортировка — только URL display controls; они не сохраняют scheduled metadata в browser storage.',
		'scheduled.readOnlyBadge': 'Read-only · без редактора расписаний',
		'scheduled.statusFilter': 'Фильтр статуса',
		'scheduled.templateFilter': 'Фильтр template metadata',
		'scheduled.sortDisplay': 'Сортировка отображения',
		'scheduled.all': 'Все',
		'scheduled.enabled': 'Включено',
		'scheduled.disabled': 'Выключено',
		'scheduled.templatePresent': 'Template есть',
		'scheduled.noTemplateReference': 'Без ссылки на template',
		'scheduled.startDate': 'Дата начала',
		'scheduled.endDate': 'Дата окончания',
		'scheduled.lastOccurred': 'Последнее выполнение',
		'scheduled.name': 'Название',
		'scheduled.enabledFirst': 'Включённые первыми',
		'scheduled.shownStatus':
			'Показано {shown} из {total} безопасных строк scheduled metadata. Template split amounts, accounts, memos, transaction descriptions и raw SQL не раскрываются.',
		'scheduled.clearFilters': 'Сбросить фильтры плановых',
		'scheduled.unnamed': 'Плановая транзакция без названия',
		'scheduled.templateAccount': 'Template account',
		'scheduled.occurrences': 'Повторы',
		'scheduled.occurrencesValue': 'всего {total} · осталось {remaining}',
		'scheduled.autoCreateNotify': 'Auto-create / notify',
		'scheduled.advanceDays': 'Advance days',
		'scheduled.advanceDaysValue': 'создать {create} · уведомить {notify}',
		'scheduled.recurrenceMetadata': 'Recurrence metadata',
		'scheduled.noRecurrenceMetadata': 'Безопасные recurrence metadata недоступны через adapter.',
		'scheduled.noMatchesTitle': 'Плановые транзакции не подходят под эти display filters',
		'scheduled.noMatchesMessage':
			'В активной книге есть scheduled metadata, но текущие URL-only фильтры скрывают все строки. Сбросьте фильтры, чтобы вернуться к полному безопасному read-only виду метаданных.',
		'scheduled.noMatchesAria': 'Плановые транзакции не подходят под display filters',
		'scheduled.emptyTitle': 'Плановые транзакции не найдены',
		'scheduled.emptyMessage':
			'Для этой книги через безопасный read-only adapter не доступны плановые транзакции. Если книга использует плановые транзакции, управляйте ими и проверяйте их в GnuCash Desktop.',
		'scheduled.emptyAria': 'Плановые транзакции не найдены',
		'scheduled.browseTransactions': 'Открыть транзакции',
		'scheduled.reviewBooks': 'Проверить книги',
		'scheduled.notConfigured': 'Не настроено',
		'scheduled.yes': 'Да',
		'scheduled.no': 'Нет',
		'scheduled.recurrenceEvery': 'каждые {count}',
		'scheduled.recurrenceFrom': 'с {date}',
		'scheduled.recurrenceWeekend': 'выходные: {value}',
		'scheduled.recurrenceUnavailable': 'Raw recurrence metadata недоступны'
	}
};
