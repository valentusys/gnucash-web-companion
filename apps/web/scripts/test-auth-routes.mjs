import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import assert from 'node:assert/strict';

const root = new URL('..', import.meta.url).pathname;

function read(relativePath) {
	return readFileSync(join(root, relativePath), 'utf8');
}

function walk(dir, files = []) {
	for (const entry of readdirSync(dir)) {
		const full = join(dir, entry);
		if (statSync(full).isDirectory()) {
			walk(full, files);
		} else {
			files.push(full);
		}
	}
	return files;
}

const hooks = read('src/hooks.server.ts');
const i18nMessages = read('src/lib/i18n/messages.ts');
const safetyGlossary = read('src/lib/i18n/safety-glossary.ts');
const emptyStateComponent = read('src/lib/components/EmptyState.svelte');
assert.match(emptyStateComponent, /role=\{role\}/, 'EmptyState must expose an overridable accessible status role');
assert.match(emptyStateComponent, /aria-label=\{ariaLabel\}/, 'EmptyState must expose an aria-label for screen-reader context');
const errorStateComponent = read('src/lib/components/ErrorState.svelte');
assert.match(errorStateComponent, /statusCode[\s\S]*403[\s\S]*404[\s\S]*defaultTitle/s, 'ErrorState must map 403, 404, and generic API/network failures to helpful copy');
assert.match(errorStateComponent, /locale = DEFAULT_LOCALE[\s\S]*error\.serviceMessage[\s\S]*error\.badgeWithCode/s, 'ErrorState default copy and badges must come from the localized catalog');
assert.match(i18nMessages, /check \/health for redacted first-run diagnostics[\s\S]*local \.env and book volume settings/s, 'ErrorState 5xx copy must give safe first-run operator next actions without private paths');
assert.match(errorStateComponent, /retryHref[\s\S]*backHref[\s\S]*aria-label/s, 'ErrorState must offer keyboard-focusable retry/back actions with labels');
const errorPage = read('src/routes/+error.svelte');
assert.match(errorPage, /import ErrorState/, 'global error page must reuse ErrorState');
assert.match(errorPage, /statusCode=\{page\.status\}[\s\S]*retryHref=\{page\.url\.pathname \+ page\.url\.search\}[\s\S]*page\.status === 503[\s\S]*'\/books'[\s\S]*error\.reviewBooks/s, 'global error page must pass status, retry, and localized /books recovery for unavailable read-only book errors');
const loadingStateComponent = read('src/lib/components/LoadingState.svelte');
assert.match(
	loadingStateComponent,
	/variant[\s\S]*dashboard[\s\S]*accounts[\s\S]*transactions[\s\S]*books/s,
	'LoadingState must expose structured skeleton variants for dashboard, accounts, transactions, and books'
);
assert.match(
	loadingStateComponent,
	/aria-busy="true"[\s\S]*data-skeleton-variant=\{variant\}[\s\S]*animate-pulse/s,
	'LoadingState skeletons must be accessible, animated, and identifiable by variant'
);
for (const [routeName, relativePath, variant] of [
	['dashboard', 'src/routes/dashboard/+page.svelte', 'dashboard'],
	['accounts', 'src/routes/accounts/+page.svelte', 'accounts'],
	['transactions', 'src/routes/transactions/+page.svelte', 'transactions'],
	['books', 'src/routes/books/+page.svelte', 'books']
]) {
	const routePage = read(relativePath);
	assert.match(routePage, /import \{ navigating \} from '\$app\/state';[\s\S]*import LoadingState/s, `${routeName} page must watch SvelteKit navigation and import LoadingState`);
	assert.match(routePage, new RegExp(`isRouteLoading[\\s\\S]*navigating\\.to[\\s\\S]*<LoadingState[\\s\\S]*variant="${variant}"`, 's'), `${routeName} page must show its ${variant} skeleton while route data is loading`);
}
const dashboardPage = read('src/routes/dashboard/+page.svelte');
assert.match(
	dashboardPage,
	/dashboard\.conservativeTotals[\s\S]*dashboard\.reportingBasis[\s\S]*data\.summary\.reporting_basis[\s\S]*dashboard\.currencyConversion[\s\S]*data\.summary\.includes_currency_conversion/s,
	'dashboard must show localized reporting_basis and whether currency conversion is included'
);
assert.match(
	dashboardPage,
	/data\.summary\.limitations[\s\S]*\{#each data\.summary\.limitations as limitation\}/s,
	'dashboard must render backend reporting limitations instead of implying converted totals'
);
assert.match(
	read('src/routes/dashboard/+page.server.ts'),
	/buildTransactionsExplorerUrl[\s\S]*dateFrom: params\.date_from[\s\S]*dateTo: params\.date_to[\s\S]*accountIds[\s\S]*type[\s\S]*cashflowByMonth[\s\S]*expensesByAccount/s,
	'dashboard server load must build canonical read-only explorer drilldown URLs from exact transaction filter parameters'
);
assert.doesNotMatch(
	read('src/routes/dashboard/+page.server.ts'),
	/Number\(/,
	'dashboard server load must not use Number() on reporting or drilldown values'
);
assert.match(
	read('src/routes/dashboard/+page.server.ts'),
	/expenses\.map\(\(expense\) => \[[\s\S]*transactionFilterHref\(\{ account_ids: expense\.account_id, date_from: dateFrom, date_to: dateTo \}\)/s,
	'dashboard expense drilldowns must preserve canonical explorer URL-filter parity with account_ids and the same date range'
);
assert.match(
	dashboardPage,
	/<SummaryGrid summary=\{data\.summary\} drilldowns=\{data\.drilldowns\}[\s\S]*<RecentTransactions transactions=\{data\.recentTransactions\} drilldownHref=\{data\.drilldowns\.recent\}[\s\S]*<ExpensesByAccount expenses=\{data\.expenses\} drilldownHrefs=\{data\.drilldowns\.expensesByAccount\}[\s\S]*<CashflowSummary periods=\{data\.cashflowPeriods\} drilldownHrefs=\{data\.drilldowns\.cashflowByMonth\}/s,
	'dashboard must pass active-book-preserving transaction drilldown URLs into report sections'
);
assert.match(
	read('src/lib/components/SummaryGrid.svelte'),
	/drilldowns\?\.incomeThisMonth[\s\S]*drilldowns\?\.expensesThisMonth[\s\S]*dashboard\.drilldownSafety/s,
	'summary cards must expose conservative no-conversion drilldown copy and URLs through the i18n catalog'
);
assert.match(
	read('src/lib/i18n/messages.ts'),
	/transaction URL filters[\s\S]*base-currency-only with no FX conversion/s,
	'summary drilldown i18n copy must preserve conservative no-conversion wording'
);
assert.match(
	read('src/lib/components/ExpensesByAccount.svelte'),
	/drilldownHrefs\[exp\.account_id\][\s\S]*account_id=\$\{encodeURIComponent\(exp\.account_id\)\}/s,
	'expense account rows must link to existing account_id transaction filters'
);
assert.match(
	read('src/lib/components/CashflowSummary.svelte'),
	/dashboard\.cashflowHelp[\s\S]*drilldownHrefs\[period\.month\]/s,
	'cashflow rows must link to existing date-range transaction filters through localized no-conversion copy'
);
assert.match(
	read('src/lib/i18n/messages.ts'),
	/date_from\/date_to transaction filters[\s\S]*No FX conversion/s,
	'cashflow i18n copy must preserve no-conversion wording'
);
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/dashboard'[\s\S]*'\/accounts'[\s\S]*'\/scheduled'/, 'dashboard, accounts, and scheduled routes must be protected');
assert.match(hooks, /redirect\(303, `\/login\?next=/, 'protected routes must redirect to /login');
assert.match(hooks, /cookies\.get\('access_token'\)/, 'protected routes must use the httpOnly cookie');
assert.match(hooks, /SAFE_METHODS[\s\S]*GET[\s\S]*HEAD[\s\S]*OPTIONS/, 'safe methods must be exempt from same-origin state-change checks');
assert.match(hooks, /headers\.get\('origin'\)[\s\S]*new URL\(origin\)\.origin === event\.url\.origin[\s\S]*Cross-origin state-changing requests are not allowed/s, 'unsafe state-changing app routes must reject mismatched Origin headers');

const loginServer = read('src/routes/login/+page.server.ts');
assert.match(loginServer, /cookies\.set\(AUTH_COOKIE, data\.access_token/, 'login must store token in cookie');
assert.match(loginServer, /httpOnly:\s*true/, 'auth cookie must be httpOnly');
assert.match(loginServer, /env\.JWT_TOKEN_EXPIRE_MINUTES[\s\S]*authCookieMaxAgeSeconds\(\)/s, 'auth cookie lifetime must follow the configured JWT session lifetime with a safe fallback');
assert.match(loginServer, /export const load[\s\S]*\/health[\s\S]*health\.first_run/s, 'login page load must fetch redacted /health first-run diagnostics without requiring auth');
assert.match(loginServer, /localeFromCookie\(cookies\)[\s\S]*response\.status === 503[\s\S]*login\.error\.operatorConfiguration/s, 'login must show localized safe first-run operator guidance for backend auth configuration failures');
assert.match(i18nMessages, /login\.error\.operatorConfiguration[\s\S]*JWT_SECRET[\s\S]*APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD[\s\S]*Вход настроен не полностью/s, 'login operator configuration guidance must preserve canonical English and Russian safety wording');
const loginPage = read('src/routes/login/+page.svelte');
assert.match(loginPage, /jwt_secret[\s\S]*admin_bootstrap[\s\S]*default_book[\s\S]*cors[\s\S]*write_mode[\s\S]*data\.firstRun[\s\S]*login\.firstRun\.title/s, 'login page must render mobile-safe redacted first-run health diagnostics for critical deployment states');
assert.match(loginPage, /min-w-0[\s\S]*statusLabel\(check\.status\)[\s\S]*break-words[\s\S]*safe_next_actions[\s\S]*list-disc/s, 'login first-run diagnostics must be mobile-safe, status-labelled, and show redacted next actions');
assert.doesNotMatch(loginPage, /localStorage|sessionStorage|JWT_SECRET=|APP_ADMIN_PASSWORD=/, 'login first-run diagnostics must not persist or display secret values');
assert.match(i18nMessages, /First-run read-only deployment checks[\s\S]*placeholder JWT secret[\s\S]*admin bootstrap[\s\S]*write-disabled status[\s\S]*Проверки first-run read-only deployment/s, 'login first-run diagnostics copy must be localized in EN/RU and cover critical deployment states');
assert.doesNotMatch(loginServer, /localStorage|sessionStorage/, 'login must not use browser storage');

const logoutServer = read('src/routes/logout/+server.ts');
assert.match(logoutServer, /cookies\.delete\('access_token'/, 'logout must delete auth cookie');

const layoutServer = read('src/routes/+layout.server.ts');
assert.match(layoutServer, /localeFromCookie\(cookies\)/, 'layout must resolve UI locale from cookie with English default fallback');
assert.match(
	layoutServer,
	/locals\.authenticated/,
	'root layout must use hook-provided authentication state so public routes like /login can render without an auth cookie'
);
assert.match(
	layoutServer,
	/if \(!locals\.authenticated\)[\s\S]*books:\s*\[\][\s\S]*activeBook:\s*null/s,
	'root layout must return a public unauthenticated state instead of redirecting /login to itself'
);
assert.match(
	layoutServer,
	/getAuthToken\(cookies\)[\s\S]*getActiveBookContext\(fetch, cookies, token\)/s,
	'authenticated layout loads must still resolve the token and book context after login'
);
assert.ok(
	layoutServer.indexOf('if (!locals.authenticated)') < layoutServer.indexOf('getAuthToken(cookies)'),
	'root layout must not read the required auth token until after the unauthenticated public-route branch'
);

const localeRoute = read('src/routes/locale/+server.ts');
assert.match(localeRoute, /LOCALE_COOKIE[\s\S]*httpOnly:\s*true[\s\S]*sameSite: 'lax'/, 'locale switch must use a sameSite cookie, not browser storage');
assert.doesNotMatch(localeRoute, /access_token/, 'locale route must not touch auth tokens');

const booksManagementServer = read('src/routes/books/+page.server.ts');
const booksManagementPage = read('src/routes/books/+page.svelte');
const booksNewServer = read('src/routes/books/new/+page.server.ts');
const booksNewPage = read('src/routes/books/new/+page.svelte');
const apiTypesForBooks = read('src/lib/api/types.ts');
const apiServerForBooks = read('src/lib/api/server.ts');
assert.match(apiTypesForBooks, /export type CurrentUser[\s\S]*is_admin:\s*boolean/s, '/auth/me CurrentUser fixture must include is_admin boolean');
assert.match(apiServerForBooks, /isCurrentUserAdmin\(user: CurrentUser \| null\)[\s\S]*user\?\.is_admin === true/s, 'admin fixture must fail closed unless /auth/me explicitly returns is_admin=true');
assert.doesNotMatch(apiServerForBooks.slice(apiServerForBooks.indexOf('export function isCurrentUserAdmin'), apiServerForBooks.indexOf('function getSelectedBookCookieState')), /username|display_name|books|management_actions/, 'admin fixture must not infer admin from usernames or book contents');
assert.doesNotMatch(booksManagementServer, /registerBook\s*:/, 'books list page must not keep the old one-step registration action');
assert.match(booksNewServer, /preflight:\s*async[\s\S]*\/books\/preflight[\s\S]*confirm:\s*async[\s\S]*preflight_token[\s\S]*\/books/s, '/books/new must split metadata registration into explicit preflight and confirm actions');
assert.match(booksNewPage, /books\.newStep1Title[\s\S]*method="POST" action="\?\/preflight"[\s\S]*name="mounted_path"[\s\S]*canConfirmRegistration\(preflight\)[\s\S]*name="preflight_token"/s, '/books/new must render safe admin preflight/confirm forms without upload widgets');
assert.match(booksNewPage, /canConfirmRegistration\(preflight: BookPreflightResponse\)[\s\S]*preflight\.status === 'ready'[\s\S]*preflight\.capabilities\.can_register_metadata === true[\s\S]*preflight\.registration_status\.status === 'available'[\s\S]*Boolean\(preflight\.preflight_token\)[\s\S]*!hasDuplicateRegistrationTarget\(preflight\)/s, '/books/new confirm fixture must withhold duplicate/unavailable/non-token preflights');
const adminNoBooksBlockForAuth = booksManagementPage.slice(booksManagementPage.indexOf('{:else if data.isAdmin}'), booksManagementPage.indexOf('{:else if !data.isAdmin}'));
const normalNoBooksBlockForAuth = booksManagementPage.slice(booksManagementPage.indexOf('{:else if !data.isAdmin}'), booksManagementPage.indexOf('{/if}', booksManagementPage.indexOf('{:else if !data.isAdmin}')));
assert.match(adminNoBooksBlockForAuth, /books\.firstRunAdminTitle[\s\S]*href="\/books\/new"[\s\S]*books\.addBookAction/s, 'auth route fixture must cover is_admin=true no-books Add book CTA');
assert.match(normalNoBooksBlockForAuth, /books\.firstRunUserTitle[\s\S]*books\.firstRunUserMessage/s, 'auth route fixture must cover false/missing admin no-books normal-user copy');
assert.doesNotMatch(normalNoBooksBlockForAuth, /href="\/books\/new"|books\.addBookAction/, 'false/missing admin no-books fixture must not expose Add book');
assert.doesNotMatch(`${booksManagementPage}\n${booksNewPage}`, /type="file"|<input[^>]+name="(?:amount|account_name|memo|description)"/, 'books registration UI must not upload books or collect private accounting data');

for (const phrase of [
	"DEFAULT_LOCALE = 'en'",
	"supportedLocales = ['en', 'ru']",
	"'login.title': 'Sign in'",
	"'login.title': 'Вход'",
	"'nav.books': 'Books'",
	"'nav.scheduled': 'Scheduled'",
	"'nav.books': 'Книги'",
	"'safety.message'",
	'MVP по умолчанию работает только на чтение',
	"'dashboard.title': 'Dashboard'",
	"'dashboard.title': 'Обзор'",
	"'dashboard.conservativeTotals': 'Conservative dashboard totals'",
	"'dashboard.conservativeTotals': 'Консервативные итоги dashboard'",
	"'dashboard.netWorth': 'Net Worth'",
	"'dashboard.netWorth': 'Чистая стоимость'",
	"'dashboard.recentTransactions': 'Recent Transactions'",
	"'dashboard.recentTransactions': 'Последние транзакции'",
	"'home.subtitle': 'Modern self-hosted read-only companion for existing GnuCash books.'",
	"'home.subtitle': 'Современный self-hosted read-only companion для существующих книг GnuCash.'",
	"'accounts.title': 'Дерево счетов'",
	"'accounts.filter.label': 'Filter accounts'",
	"'accounts.filter.label': 'Фильтр счетов'",
	"'transactions.title': 'Просмотр транзакций'",
	"'transactionDetail.helper': 'Read-only view of the selected GnuCash transaction",
	"'transactionDetail.helper': 'Read-only просмотр выбранной транзакции GnuCash",
	"'transactionSplits.helper': 'Read-only split metadata from GnuCash",
	"'transactionSplits.helper': 'Read-only metadata split из GnuCash",
	"'books.title': 'Book metadata'",
	"'books.title': 'Метаданные книг'",
	'Только read-only метаданные книг',
	"'transactions.filters.title': 'Transaction filters'",
	"'transactions.filters.title': 'Фильтры транзакций'",
	'Сужают read-only список транзакций и CSV export',
	"'transactions.filters.stateHelp'",
	'Фильтрует по состоянию сверки split в GnuCash; транзакции не редактируются.',
	"'transactions.export.statusFiltered'",
	'Экспортирует текущий read-only отфильтрованный вид',
	"'transactions.export.accountStatus'",
	"'scheduled.title': 'Scheduled transactions'",
	"'scheduled.title': 'Плановые транзакции'",
	"'scheduled.subtitle'",
	'GnuCash Desktop остаётся главным редактором',
	"'scheduled.noMatchesTitle'",
	"'scheduled.emptyTitle'"
]) {
	assert.ok(i18nMessages.includes(phrase), `i18n messages must include: ${phrase}`);
}

for (const glossaryTerm of [
	'read-only-default',
	'write-alpha-disposable-test-boundary',
	'not-production-ready',
	'not-security-audited',
	'no-currency-conversion',
	'desktop-authoritative-editor'
]) {
	assert.ok(safetyGlossary.includes(`id: '${glossaryTerm}'`), `safety glossary must catalog ${glossaryTerm}`);
}
for (const glossaryPhrase of [
	"canonicalEnglish: 'read-only by default; GNUCASH_WRITES_ENABLED=false'",
	"preferredRussian: 'read-only по умолчанию; GNUCASH_WRITES_ENABLED=false'",
	"canonicalEnglish: 'write-alpha is experimental and disposable/test-copy only'",
	"preferredRussian: 'write-alpha экспериментален и только для disposable/test copies'",
	"canonicalEnglish: 'not production-ready'",
	"preferredRussian: 'не production-ready'",
	"canonicalEnglish: 'not security-audited'",
	'не security-audited / не проходило security audit',
	"canonicalEnglish: 'no currency conversion / no FX conversion'",
	"preferredRussian: 'без конвертации валют / без FX-конвертации'",
	"canonicalEnglish: 'GnuCash Desktop remains the authoritative editor'",
	"preferredRussian: 'GnuCash Desktop остаётся главным редактором'"
]) {
	assert.ok(safetyGlossary.includes(glossaryPhrase), `safety glossary must include canonical phrase: ${glossaryPhrase}`);
}
for (const catalogPhrase of [
	'GNUCASH_WRITES_ENABLED=false is the safe default',
	'GnuCash Desktop remains the authoritative editor',
	'Not production-ready or security-audited',
	'outside-git copied/restorable test book',
	'not production-ready, not security-audited, and not a production audit log product',
	'Use only an outside-git copied/restorable test book in ignored runtime storage',
	'one small CREATE test transaction',
	'independent backup, restore plan, audit row, app backup evidence',
	'not for production use',
	'no currency conversion is performed',
	'GnuCash Desktop остаётся главным редактором',
	'не production-ready и не security-audited',
	'outside-git copied/restorable test book',
	'одной небольшой CREATE test transaction',
	'Это не для production use',
	'без FX-конвертации'
]) {
	assert.ok(i18nMessages.includes(catalogPhrase), `release-critical i18n catalog must preserve glossary phrase: ${catalogPhrase}`);
}
for (const [label, source] of [
	['i18n catalog', i18nMessages],
	['safety glossary', safetyGlossary]
]) {
	const normalizedSource = source
		.replace(/not-production-ready/gi, '')
		.replace(/not-security-audited/gi, '')
		.replace(/not production-ready or security-audited/gi, '')
		.replace(/not production-ready, not security-audited/gi, '')
		.replace(/not production-ready/gi, '')
		.replace(/not security-audited/gi, '')
		.replace(/не production-ready/gi, '')
		.replace(/не security-audited/gi, '')
		.replace(/не проходило security audit/gi, '')
		.replace(/production-ready and not safe for real\/private or only-copy books/gi, '')
		.replace(/safe default/gi, '')
		.replace(/safely moved/gi, '')
		.replace(/fail safely/gi, '');
	assert.doesNotMatch(normalizedSource, /\bproduction-ready\b/i, `${label} must not make an affirmative production-ready claim`);
	assert.doesNotMatch(normalizedSource, /\bsecurity-audited\b|security audit/i, `${label} must not make an affirmative security-audited claim`);
	assert.doesNotMatch(source, /safe(?:ly)?\s+(?:write|writes|writing)|production-safe write|real\/private-book write safety/i, `${label} must not claim safe writes`);
	assert.doesNotMatch(source, /localStorage|sessionStorage/, `${label} safety/localization slice must not introduce browser storage`);
}

const localeSwitcher = read('src/lib/components/LocaleSwitcher.svelte');
assert.match(localeSwitcher, /method="POST" action="\/locale"/, 'locale switcher must submit through the server cookie route');
assert.doesNotMatch(localeSwitcher, /localStorage|sessionStorage/, 'locale switcher must not use browser storage');

const transactionsServer = read('src/routes/transactions/+page.server.ts');
assert.match(
	transactionsServer,
	/const writesEnabled = env\.GNUCASH_WRITES_ENABLED === 'true'[\s\S]*writesEnabled/s,
	'transactions page must expose writesEnabled only when GNUCASH_WRITES_ENABLED is true'
);
for (const requiredPreset of ['This month', 'Last month', 'Year to date', 'Clear dates']) {
	assert.ok(
		transactionsServer.includes(requiredPreset),
		`transactions server load must expose the date preset label: ${requiredPreset}`
	);
}
assert.match(
	transactionsServer,
	/buildExplorerDatePresets[\s\S]*buildTransactionsExplorerUrlFromValue\(filters, \{ dateFrom[\s\S]*dateTo[\s\S]*cursor: '' \}\)/s,
	'canonical explorer date preset URLs must preserve existing non-date filters and reset cursor pagination'
);
assert.match(
	transactionsServer,
	/resetHref = buildTransactionsExplorerUrl\(\)[\s\S]*resetPaginationHref = buildTransactionsExplorerUrl\(\{ \.\.\.stripTransactionsExplorerCursor\(filters\), cursor: '' \}\)/s,
	'transactions server load must expose canonical reset URLs that clear filters or reset cursor pagination without private saved filters'
);
assert.match(
	transactionsServer,
	/datePresets:\s*buildExplorerDatePresets/,
	'transactions server load must return date preset URL data to the page'
);

const newTransactionServer = read('src/routes/transactions/new/+page.server.ts');
assert.match(
	newTransactionServer,
	/getActiveBookContext\(fetch, cookies, token\)[\s\S]*apiFetch<Account\[\]>\(fetch, `\$\{bookPrefix\}\/accounts`, token\)/s,
	'new transaction preview page must resolve books/accounts through the active accessible book context'
);
assert.match(
	newTransactionServer,
	/`\/books\/\$\{activeBook\.id\}\/transactions\/create-preview`/,
	'new transaction preview page must call only the non-mutating active-book create-preview endpoint'
);
assert.match(
	newTransactionServer,
	/export const actions: Actions = \{\s*preview:\s*async/s,
	'new transaction preview page must expose only a preview server action'
);
assert.doesNotMatch(
	newTransactionServer,
	/env\.GNUCASH_WRITES_ENABLED !== 'true'[\s\S]*redirect\(303, '\/transactions'\)|\/transactions\/validate|`\/books\/\$\{bookId\}\/transactions`|`\/books\/\$\{activeBook\.id\}\/transactions`|\b(?:create|validate)\s*:\s*async|hasWriteAcknowledgement/,
	'new transaction preview route must stay reachable with writes disabled and must not retain create/validate/write action code'
);

const booksPageServer = read('src/routes/books/+page.server.ts');
assert.match(booksPageServer, /getActiveBookContext\(fetch, cookies, token\)/, '/books page must resolve accessible book metadata and the current/default book through the authenticated API context');
assert.doesNotMatch(booksPageServer, /upload/i, '/books page server must not add GnuCash file upload handling');
assert.doesNotMatch(booksPageServer, /transactions|accounts|splits|commodities/i, '/books page server actions must stay app-metadata-only and avoid accounting data routes');
assert.match(booksPageServer, /removeBook[\s\S]*confirm_metadata_only[\s\S]*`\/books\/\$\{bookId\}`[\s\S]*'DELETE'/s, '/books registry remove action must require metadata-only confirmation and call only the registry DELETE endpoint');
assert.match(i18nMessages, /Removed the book from the app registry only\. The source GnuCash file is not deleted or modified/s, '/books registry remove copy must explicitly be registry-only and never file deletion');

const booksSelectRoute = read('src/routes/books/[bookId]/select/+server.ts');
assert.match(booksSelectRoute, /getActiveBookContext\(fetch, cookies, token\)/, 'book safe-link route must verify selected book against accessible API context before setting a cookie');
assert.match(booksSelectRoute, /selectedBook\.can_open_read_only_views[\s\S]*\/books\?book_context=unavailable_selected_book/s, 'book safe-link route must withhold direct navigation for accessible but unavailable/missing books');
assert.match(booksSelectRoute, /cookies\.set\('selected_book_id'[\s\S]*sameSite:\s*'lax'/s, 'book safe-link route must preserve active book context with the existing non-secret sameSite cookie');
assert.match(booksSelectRoute, /SAFE_NEXT_PATHS[\s\S]*'\/accounts'[\s\S]*'\/transactions'[\s\S]*'\/reports'[\s\S]*isSafeNextPath[\s\S]*parsed\.pathname[\s\S]*parsed\.search/s, 'book safe-link route must redirect only to approved read-only account/transaction/report views while preserving safe route query strings');
assert.doesNotMatch(booksSelectRoute, /upload|delete|registry|admin|write|edit/i, 'book safe-link route must not expose management workflows');

const booksPage = read('src/routes/books/+page.svelte');
for (const requiredPhrase of [
	'Book metadata',
	'Read-only book metadata only',
	'Configured books',
	'Base currency',
	'Metadata status',
	'Read-only',
	'Archived and unauthorized books are hidden or blocked by the API',
	'Open safe views',
	'View accounts',
	'Browse transactions',
	'View reports',
	'No registry management actions are available on this read-only page.',
	'Storage diagnostics',
	'Private filesystem path is intentionally not shown.',
	'No books are registered yet',
	'An administrator must register or assign a book',
	'Existing server-side GnuCash SQL SQLite only',
	'No browser upload, copy, import, XML, compressed XML, conversion, filesystem discovery, or source delete'
]) {
	assert.ok(i18nMessages.includes(requiredPhrase), `books i18n catalog must include canonical English phrase: ${requiredPhrase}`);
}
assert.match(booksPage, /import EmptyState/, '/books page must reuse the accessible EmptyState component for no accessible books');
assert.match(booksPage, /data\.isAdmin[\s\S]*books\.firstRunAdminTitle[\s\S]*href="\/books\/new"/s, '/books page must give first-run admins an Add book recovery action');
assert.match(booksPage, /!data\.isAdmin[\s\S]*books\.firstRunUserTitle[\s\S]*books\.firstRunUserMessage/s, '/books page must give normal no-books users role-safe fixed copy');
assert.match(booksPage, /DEFAULT_LOCALE[\s\S]*t\(locale, 'books\.title'\)[\s\S]*t\(locale, 'books\.noMutationBadge'\)/s, '/books page must render localized titles and read-only safety labels from the i18n catalog');
for (const requiredBookField of ['data.books', 'book.name', 'book.base_currency', 'book.health?.status', 'book.health?.checked_at', 'book.access_role']) {
	assert.ok(booksPage.includes(requiredBookField), `/books page must render or derive ${requiredBookField}`);
}
assert.match(booksPage, /book\.is_enabled[\s\S]*book\.is_default/s, '/books page must render enabled/default state diagnostics');
assert.match(booksPage, /book\.can_open_read_only_views[\s\S]*books\.unavailableViews/s, '/books page must hide read-only view links for unavailable or not-configured books');
assert.doesNotMatch(booksPage, /book\.operator_guidance\./, '/books page must not render arbitrary backend operator guidance copy');
assert.match(booksPage, /book\.storage_diagnostics\.safe_summary[\s\S]*books\.privatePathRedacted/s, '/books page must render safe storage diagnostics without private paths');
assert.doesNotMatch(booksPage, /uri_or_path|book\.operator_guidance\.message/, '/books page must not render private book paths or raw backend guidance copy');
assert.match(booksPage, /book\.is_default[\s\S]*t\(locale, 'books\.defaultBook'\)/s, '/books page must clearly mark the active/default book');
assert.match(booksPage, /can_open_accounts[\s\S]*next: '\/accounts'[\s\S]*can_open_transactions[\s\S]*next: '\/transactions'[\s\S]*can_open_reports[\s\S]*next: '\/reports'[\s\S]*\/books\/\$\{book\.id\}\/select\?next=\$\{link\.next\}/s, '/books page must expose capability-gated safe book-context links to read-only views');
assert.doesNotMatch(booksPage, /type="file"|Upload book|Delete book|collaborative|shared wallet|family wallet/i, '/books page must not offer upload/delete controls or collaborative/family-wallet framing');
assert.match(booksPage, /href="\/books\/write-alpha-audit"[\s\S]*books\.auditEvidence/s, '/books page must link operators to the localized safe write-alpha audit evidence view');

const writeAlphaAuditServer = read('src/routes/books/write-alpha-audit/+page.server.ts');
const writeAlphaAuditPage = read('src/routes/books/write-alpha-audit/+page.svelte');
assert.match(writeAlphaAuditServer, /getAuthToken\(cookies\)[\s\S]*getActiveBookContext\(fetch, cookies, token\)[\s\S]*safeIntegerParam[\s\S]*new URLSearchParams\(\{ limit: String\(limit\), offset: String\(offset\) \}\)[\s\S]*action[\s\S]*result[\s\S]*since[\s\S]*until[\s\S]*write-alpha-audit-summary\?\$\{params\.toString\(\)\}/s, 'write-alpha audit view must load only through authenticated active-book API context with safe URL filters and bounded pagination');
assert.match(writeAlphaAuditPage, /DEFAULT_LOCALE[\s\S]*audit\.bannerTitle[\s\S]*audit\.bannerMessage[\s\S]*audit\.redactionMessage/s, 'write-alpha audit page must use localized narrow disposable-run UX copy');
assert.match(i18nMessages, /Read-only app metadata summary[\s\S]*pre-alpha[\s\S]*not production-ready[\s\S]*not security-audited[\s\S]*not a production audit log product[\s\S]*Raw request payloads[\s\S]*amounts are not shown/s, 'write-alpha audit catalog must state redaction, pre-alpha, not-production, not-security-audited boundaries');
assert.match(writeAlphaAuditPage, /method="GET"[\s\S]*audit\.action[\s\S]*audit\.result[\s\S]*audit\.sinceIso[\s\S]*audit\.untilIso[\s\S]*audit\.limit[\s\S]*name="offset"[\s\S]*audit\.applyFilters[\s\S]*audit\.clearFilters/s, 'write-alpha audit page must expose localized safe URL-only action/result/time-window/limit filters');
assert.match(writeAlphaAuditPage, /total_count[\s\S]*returned_count[\s\S]*counts_by_action[\s\S]*counts_by_result[\s\S]*time_window\.requested_since[\s\S]*status_summary[\s\S]*pagination\.offset[\s\S]*pagination\.has_next/s, 'write-alpha audit page must render safe count/status/time-window/pagination metadata');
assert.match(writeAlphaAuditPage, /ownership_summary[\s\S]*write_alpha_created_count[\s\S]*non_owned_mutation_rejections_count[\s\S]*last_mutation_type/s, 'write-alpha audit page must render safe ownership metadata');
assert.match(writeAlphaAuditPage, /audit\.ownership[\s\S]*audit\.ownedCreated[\s\S]*audit\.nonOwnedRejected[\s\S]*audit\.lastMutation/s, 'write-alpha audit page must render localized ownership evidence without raw payloads');
assert.match(writeAlphaAuditPage, /item\.action[\s\S]*item\.result[\s\S]*item\.timestamp[\s\S]*item\.transaction_id_prefix[\s\S]*item\.backup_present[\s\S]*item\.error/s, 'write-alpha audit page must render only safe summary fields');
assert.match(writeAlphaAuditPage, /min-w-0[\s\S]*overflow-x-hidden[\s\S]*md:grid-cols-\[minmax\(0,10rem\)_7rem_minmax\(0,11rem\)_8rem_minmax\(0,1fr\)\]/s, 'write-alpha audit page must keep mobile layout bounded without horizontal overflow');
assert.doesNotMatch(writeAlphaAuditPage, /backup_path|request_summary|fields_updated|localStorage|sessionStorage|fetch\(|method="POST"/i, 'write-alpha audit page must not render raw audit payloads, persist evidence, or expose mutations');

const writeModeWarningComponent = read('src/lib/components/WriteModeWarning.svelte');
assert.match(writeModeWarningComponent, /writeMode\.title[\s\S]*writeMode\.message[\s\S]*writeMode\.disposableOnly[\s\S]*writeMode\.neverRealBook/s, 'write-mode warning must use localized safety copy');
assert.match(i18nMessages, /writeMode\.message[\s\S]*not production-ready or security-audited[\s\S]*APP_ENV=test disposable run[\s\S]*writeMode\.message[\s\S]*не production-ready и не security-audited/s, 'write-mode catalog must pin unsafe-claim guards in EN/RU');

const desktopNav = read('src/lib/components/DesktopNav.svelte');
const mobileNav = read('src/lib/components/MobileNav.svelte');
assert.match(desktopNav, /href: '\/scheduled'[\s\S]*label: t\(locale, 'nav\.scheduled'\)/, 'desktop nav must expose the localized /scheduled page');
assert.match(mobileNav, /href: '\/scheduled'[\s\S]*label: t\(locale, 'nav\.scheduled'\)/, 'mobile nav must expose the localized /scheduled page');
assert.match(desktopNav, /href: '\/books'[\s\S]*label: t\(locale, 'nav\.books'\)/, 'desktop nav must expose the localized /books management page');
assert.match(mobileNav, /href: '\/books'[\s\S]*label: t\(locale, 'nav\.books'\)/, 'mobile nav must expose the localized /books management page');
assert.match(desktopNav, /<header class="hidden[^"]*md:block/s, 'desktop header must be hidden below the md breakpoint so mobile navigation is not duplicated');
assert.match(mobileNav, /md:hidden[\s\S]*aria-label="Mobile navigation"/, 'mobile navigation must be the only app navigation below the md breakpoint');
assert.match(mobileNav, /let menuOpen = \$state\(false\)[\s\S]*aria-expanded=\{menuOpen\}[\s\S]*onclick=\{toggleMenu\}/s, 'mobile nav must expose a touch-friendly menu button that opens and closes the mobile menu');
assert.match(mobileNav, /data-mobile-menu[\s\S]*BookSwitcher[\s\S]*LocaleSwitcher[\s\S]*ThemeSwitcher[\s\S]*method="POST" action="\/logout"/s, 'mobile menu must contain book, locale, theme, and logout touch controls');
assert.match(mobileNav, /min-h-\[44px\][\s\S]*min-w-\[44px\]/s, 'mobile menu controls and nav links must declare at least 44px touch targets');
assert.doesNotMatch(mobileNav, /overflow-x-auto|min-w-full/, 'mobile navigation must not introduce horizontal scrolling at 320px widths');
const layoutPage = read('src/routes/+layout.svelte');
assert.match(layoutPage, /overflow-x-hidden[\s\S]*max-w-full[\s\S]*pb-32 md:pb-0/s, 'app shell must prevent mobile horizontal scroll and reserve enough space for the fixed mobile navigation');
assert.match(layoutPage, /<ReadOnlyStatusBanner \{locale\} \{activeBook\}/, 'app shell must pass the active book into the read-only runtime status banner');
const readOnlyStatusBanner = read('src/lib/components/ReadOnlyStatusBanner.svelte');
assert.match(readOnlyStatusBanner, /activeBook\?: Book \| null[\s\S]*activeBook\?\.name[\s\S]*safety\.currentBook/s, 'read-only status banner must show the current active book name');
assert.match(readOnlyStatusBanner, /href="\/books"[\s\S]*safety\.reviewBooks/s, 'read-only status banner must provide a safe link to review books');
assert.match(readOnlyStatusBanner, /safety\.releaseCritical/s, 'app shell safety banner must expose release-critical pre-alpha/not-production wording');
assert.match(i18nMessages, /Pre-alpha read-only MVP[\s\S]*GNUCASH_WRITES_ENABLED=false[\s\S]*Not production-ready or security-audited[\s\S]*outside-git copied\/restorable test books[\s\S]*originals untouched[\s\S]*Pre-alpha MVP[\s\S]*Не production-ready[\s\S]*outside-git copied\/restorable test books/s, 'localized safety copy must state pre-alpha, default-disabled, not-production, not-security-audited, and copied-book-only boundaries');
const bookSwitcherComponent = read('src/lib/components/BookSwitcher.svelte');
assert.match(bookSwitcherComponent, /compact = false[\s\S]*min-h-11[\s\S]*max-w-full[\s\S]*truncate/s, 'book switcher must support compact mobile rendering with 44px touch height and no overflow');
const localeSwitcherComponentForMobile = read('src/lib/components/LocaleSwitcher.svelte');
assert.match(localeSwitcherComponentForMobile, /min-h-11[\s\S]*min-w-\[44px\]/, 'locale switcher select must expose a 44px touch target');
const transactionSplitsComponent = read('src/lib/components/TransactionSplits.svelte');
assert.match(transactionSplitsComponent, /md:hidden[\s\S]*split\.account_name[\s\S]*Money[\s\S]*transactionSplits\.memo[\s\S]*reconcileLabel\(split\.reconcile_state\)/s, 'transaction detail splits must render localized mobile cards with account, amount, memo, and reconciliation metadata instead of forcing a horizontal table at 320px');
assert.match(transactionSplitsComponent, /hidden overflow-x-hidden md:block[\s\S]*table-fixed[\s\S]*transactionSplits\.reconciliation[\s\S]*reconcileLabel\(split\.reconcile_state\)/s, 'transaction detail split table must be desktop-only, bounded, and expose localized reconciliation state');
assert.match(transactionSplitsComponent, /splits\.length === 0[\s\S]*transactionSplits\.empty/s, 'transaction detail splits must show a safe localized empty state instead of inventing data');
assert.doesNotMatch(transactionSplitsComponent, /overflow-x-auto|min-w-full/, 'transaction detail splits must not introduce mobile horizontal scrolling');
assert.match(
	read('src/lib/components/Money.svelte'),
	/inline-flex max-w-full min-w-0 flex-wrap[\s\S]*break-all[\s\S]*shrink-0/s,
	'money display must keep long Decimal string amounts bounded on many-split mobile cards without coercing to Number()'
);

const scheduledServer = read('src/routes/scheduled/+page.server.ts');
assert.match(
	scheduledServer,
	/getActiveBookContext\(fetch, cookies, token\)[\s\S]*apiFetch<ScheduledTransaction\[\]>\(fetch, `\$\{bookPrefix\}\/scheduled-transactions`, token\)/s,
	'scheduled page must load safe scheduled metadata for the active accessible book through the API'
);
assert.match(
	scheduledServer,
	/scheduledFilterHref[\s\S]*status[\s\S]*template[\s\S]*sort[\s\S]*filterScheduledTransactions[\s\S]*has_template_account[\s\S]*sortScheduledTransactions/s,
	'scheduled server load must provide URL-only status/template filters and deterministic safe metadata sorting'
);
const scheduledPage = read('src/routes/scheduled/+page.svelte');
for (const scheduledPhrase of [
	'Scheduled transactions',
	'Read-only scheduled transaction awareness',
	'Use GnuCash Desktop as the authoritative editor',
	'Template split details and private raw SQL are not exposed',
	'Filters and sorting are URL-only display controls',
	'Status filter',
	'Template metadata filter',
	'Sort display',
	'No template split amounts, accounts, memos, transaction descriptions, or raw SQL are exposed',
	'No scheduled transactions are available through the safe read-only adapter'
]) {
	assert.ok(i18nMessages.includes(scheduledPhrase), `scheduled i18n catalog must include conservative copy: ${scheduledPhrase}`);
}
assert.match(scheduledPage, /DEFAULT_LOCALE[\s\S]*t\(locale, 'scheduled\.title'\)[\s\S]*t\(locale, 'scheduled\.metadataHelp'\)/s, 'scheduled page must render release-critical copy through the localized catalog');
assert.match(scheduledPage, /import EmptyState/, 'scheduled page must reuse EmptyState for no schedules');
assert.match(scheduledPage, /data\.scheduledSummary\.shown[\s\S]*data\.scheduledSummary\.total[\s\S]*data\.filters\.links\.clear/s, 'scheduled page must show filtered counts and clear URL-only scheduled filters');
assert.match(scheduledPage, /templateStatusLabel[\s\S]*present_redacted[\s\S]*scheduled\.templatePresentRedacted[\s\S]*scheduled\.templateNotPresentRedacted/s, 'scheduled page must render only redacted template-reference status, including no-template cases');
assert.match(scheduledPage, /min-w-0 rounded-xl border p-4[\s\S]*scheduled\.templateReferenceStatus[\s\S]*scheduled\.template_reference_status/s, 'scheduled cards must keep bounded layout and show safe template metadata status');
assert.match(scheduledPage, /<EmptyState[\s\S]*title=\{t\(locale, 'scheduled\.noMatchesTitle'\)\}[\s\S]*href=\{data\.filters\.links\.clear\}[\s\S]*scheduled\.clearFilters/s, 'scheduled filtered empty state must explain URL-only filters and offer a localized clear action');
assert.match(scheduledPage, /<EmptyState[\s\S]*title=\{t\(locale, 'scheduled\.emptyTitle'\)\}[\s\S]*href="\/transactions"[\s\S]*scheduled\.browseTransactions/s, 'scheduled empty state must include localized copy and keyboard-focusable navigation');
assert.doesNotMatch(
	scheduledPage,
	/<form|method="POST"|New scheduled|Edit scheduled|Delete scheduled|next occurrence|next-run|localStorage|sessionStorage/i,
	'scheduled page must not expose scheduling editor controls, browser persistence, or fake next-run copy'
);

const transactionTable = read('src/lib/components/TransactionTable.svelte');
const transactionCard = read('src/lib/components/TransactionCard.svelte');
assert.match(
	transactionTable,
	/<div class="hidden overflow-x-hidden md:block">[\s\S]*<table class="w-full table-fixed text-left text-sm">/s,
	'transaction table desktop layout must use fixed full-width columns without a needless horizontal scroll container'
);
for (const requiredClass of [
	'w-28 px-4 py-3',
	'w-[32%] px-4 py-3',
	'w-[22%] px-4 py-3',
	'w-[22%] px-4 py-3',
	'w-36 px-4 py-3 text-right',
	'truncate font-medium',
	'truncate text-sm',
	'whitespace-nowrap text-right'
]) {
	assert.ok(transactionTable.includes(requiredClass), `transaction table must include stable/truncating class: ${requiredClass}`);
}
assert.doesNotMatch(
	transactionTable,
	/min-w-full|overflow-x-auto/,
	'transaction table must not force desktop horizontal shifting with min-width or overflow-x-auto'
);
assert.match(
	transactionTable,
	/tx\.is_write_alpha_owned[\s\S]*transactions\.writeAlphaHistoryTitle[\s\S]*transactions\.writeAlphaHistoryBadge/s,
	'transaction table must mark write-alpha-created history rows with a bounded safe app-metadata badge'
);
assert.match(
	transactionCard,
	/tx\.is_write_alpha_owned[\s\S]*transactions\.writeAlphaHistoryTitle[\s\S]*transactions\.writeAlphaHistoryBadge/s,
	'transaction mobile card must mark write-alpha-created history rows with the same safe app-metadata badge'
);

const accountTree = read('src/lib/components/AccountTree.svelte');
const accountsPage = read('src/routes/accounts/+page.svelte');
assert.match(accountsPage, /<EmptyState[\s\S]*title=\{t\(locale, 'accounts\.emptyTitle'\)\}[\s\S]*href="\/books"[\s\S]*accounts\.emptyAction/s, 'accounts empty state must clearly explain unavailable accounts and link to books through localized copy');
const accountTreeNode = read('src/lib/components/AccountTreeNode.svelte');
assert.match(
	accountTree,
	/grid-cols-\[minmax\(0,1fr\)_7rem_9rem_4rem\]/,
	'account tree desktop header must use bounded columns that can shrink safely'
);
assert.match(
	accountTree,
	/id="account-tree-filter"[\s\S]*type="search"[\s\S]*bind:value=\{accountQuery\}[\s\S]*aria-describedby="account-tree-filter-status"/s,
	'account tree must expose an accessible URL-free search filter for large read-only trees'
);
assert.match(
	accountTree,
	/filterAccounts\(nodes: AccountTreeNodeType\[\], query: string\)[\s\S]*accountMatches\(node, query\)[\s\S]*children\.length > 0[\s\S]*return \{ \.\.\.node, children \}/s,
	'account tree filter must preserve parent paths when a descendant account matches'
);
assert.match(
	accountTree,
	/name, account\.full_name, account\.type, account\.currency[\s\S]*accounts\.filter\.filteredStatus[\s\S]*filteredAccountCount[\s\S]*totalAccountCount/s,
	'account tree filter must search names/full paths/type/currency and report localized filtered counts'
);
assert.match(
	accountTree,
	/accounts\.filter\.allStatus/s,
	'account tree filter helper copy must frame filtering as local read-only discoverability only through the i18n catalog'
);
assert.doesNotMatch(
	accountTree,
	/localStorage|sessionStorage|fetch\(|apiFetch|method="POST"/,
	'account tree filter must not persist private account searches or call write/API paths'
);
assert.match(
	accountTreeNode,
	/min-w-0 grid-cols-1[\s\S]*md:grid-cols-\[minmax\(0,1fr\)_7rem_9rem_4rem\]/,
	'account tree rows must allow the name column to shrink instead of causing desktop overflow'
);
assert.match(
	accountTreeNode,
	/visualDepth = \$derived\(Math\.min\(depth, 8\)\)[\s\S]*padding-left: \{visualDepth \* 1\.25\}rem[\s\S]*title=\{account\.full_name\}/,
	'deep account hierarchy indentation must be capped while preserving full-path hover text'
);
assert.match(
	accountTreeNode,
	/overflow-hidden[\s\S]*truncate font-medium[\s\S]*truncate text-sm/s,
	'account tree names and full names must truncate safely for narrow desktop layouts'
);

const transactionListPage = read('src/routes/transactions/+page.svelte');
assert.match(transactionListPage, /import EmptyState/, 'transactions page must reuse EmptyState for empty result sets');
assert.match(transactionListPage, /hasActiveFilters[\s\S]*No transactions match the current filters[\s\S]*No transactions yet/s, 'transactions page must distinguish no data from filters with no matches');
assert.match(
	transactionListPage,
	/writeAlphaOwnedVisibleCount[\s\S]*transactions\.listStatus\.writeAlphaHint[\s\S]*write-alpha-history-hint/s,
	'transactions page must summarize visible write-alpha-created synthetic/disposable rows as a history hint only'
);
assert.match(
	transactionListPage,
	/write-alpha-history-followup[\s\S]*transactions\.listStatus\.writeAlphaFollowupTitle[\s\S]*transactions\.listStatus\.writeAlphaFollowupHelp[\s\S]*href="\/books\/write-alpha-audit"[\s\S]*transactions\.listStatus\.writeAlphaAuditLink/s,
	'transactions page must explain how newly created synthetic/disposable rows appear in normal history and link to redacted audit evidence'
);
for (const historyCopyFragment of [
	"'transactions.writeAlphaHistoryBadge': 'write-alpha-created'",
	'Synthetic/disposable history hint only',
	'Backend ownership guards remain authoritative',
	'default writes stay disabled',
	'New synthetic CREATE follow-up',
	'newly created synthetic/disposable transaction appears in the normal newest-first history only after the read-only API returns it and app metadata marks its GUID',
	'badge is not a permission to write',
	'{count} строк(и) на этой странице отмечены app metadata как write-alpha-created',
	'writes по умолчанию отключены',
	'Новая synthetic CREATE follow-up',
	'только когда read-only API вернул строку, а app metadata пометила GUID',
	'badge не даёт разрешение на запись'
]) {
	assert.ok(i18nMessages.includes(historyCopyFragment), `transaction history write-alpha copy must include: ${historyCopyFragment}`);
}
assert.match(transactionListPage, /<EmptyState[\s\S]*href=\{data\.clearFiltersHref\}[\s\S]*Clear filters/s, 'filtered transaction empty state must offer a keyboard-focusable clear-filters action');
for (const filterParam of ['query', 'date_from', 'date_to', 'account_id', 'min_amount', 'max_amount', 'transaction_state']) {
	assert.ok(
		transactionListPage.includes(`sp.set('${filterParam}'`) ||
			transactionListPage.includes(`sp.set('${filterParam}',`),
		`transactions page URLs must preserve ${filterParam}`
	);
}
assert.ok(
	transactionListPage.includes('href={data.exportCsv.href}') && transactionListPage.includes('data.exportCsv?.enabled'),
	'CSV export URL must come from server-validated active filter/export state'
);
assert.match(
	transactionListPage,
	/inline-flex min-h-11 items-center justify-center rounded-xl[\s\S]*href=\{data\.exportCsv\.href\}[\s\S]*href=\{data\.clearFiltersHref\}[\s\S]*inline-flex min-h-11 items-center justify-center/s,
	'transactions page mobile CTA links must keep CSV export and legacy clear-filter actions at least 44px tall'
);

const accountDetailServer = read('src/routes/accounts/[id]/+page.server.ts');
assert.match(
	accountDetailServer,
	/validateAccountDetailUrl\(url, params\.id\)[\s\S]*if \(!validation\.ok\)[\s\S]*activityRequestCounters[\s\S]*activityRequestCounters\.overview = 1/s,
	'account detail server load must validate account/date/return filters before bounded overview/activity calls'
);
assert.match(
	accountDetailServer,
	/activityRequestCounters\.overview = 1[\s\S]*if \(!hasAccountActivityDateRange\(filters\)\)[\s\S]*activity: null[\s\S]*activityRequestCounters,[\s\S]*const apiParams = activityParams/s,
	'account detail no-date state must return overview only with zero bounded activity calls'
);
assert.match(
	accountDetailServer,
	/`\$\{bookPrefix\}\/accounts\/\$\{encodeURIComponent\(filters\.accountId\)\}\/activity\?\$\{apiParams\.toString\(\)\}`[\s\S]*buildAccountTransactionExplorerUrl\(filters\.accountId, filters\.dateFrom, filters\.dateTo\)[\s\S]*buildBaseReportUrl\(filters\.dateFrom, filters\.dateTo\)/s,
	'account detail activity must use bounded book-aware endpoint plus exact transaction/report links'
);

const accountDetailPage = read('src/routes/accounts/[id]/+page.svelte');
assert.match(
	accountDetailPage,
	/method="GET"[\s\S]*name="date_from"[\s\S]*name="date_to"[\s\S]*name="limit"[\s\S]*href=\{data\.resetActivityHref\}/s,
	'account detail page must expose URL-backed bounded activity controls and reset link'
);
assert.match(
	accountDetailPage,
	/activity\.transaction_explorer_compatible[\s\S]*data\.transactionExplorerHref[\s\S]*unavailableNoFxScope[\s\S]*data\.reportHref/s,
	'account detail page must distinguish compatible exact transaction drilldown, unavailable no-FX scope, and base report link'
);
assert.match(
	accountDetailPage,
	/recent_transactions[\s\S]*transactionHref\(tx\.id\)[\s\S]*matched_quantity/s,
	'account detail page must link recent bounded activity rows to transaction detail with exact matched quantities'
);
assert.match(
	accountDetailPage,
	/inline-flex min-h-11 items-center justify-center rounded-xl[\s\S]*href=\{data\.resetActivityHref\}/s,
	'account detail activity controls must keep touch-friendly 44px mobile targets'
);
assert.match(
	transactionListPage,
	/t\(locale, 'transactions\.export\.statusFiltered'\)[\s\S]*t\(locale, 'transactions\.export\.statusUnfiltered'\)[\s\S]*exportButtonLabel/s,
	'CSV export copy must come from the localized catalog while preserving filtered/unfiltered read-only status'
);
assert.match(
	transactionListPage,
	/csvReliabilityStatus[\s\S]*transactions\.export\.emptyStatus[\s\S]*transactions\.export\.truncatedStatus[\s\S]*transactions\.export\.countStatus[\s\S]*csv-export-reliability-status/s,
	'transactions page CSV export UX must explain empty, counted, and capped/truncated export states'
);
assert.doesNotMatch(
	transactionListPage,
	/Number\(|parseFloat\(|parseInt\(|localStorage|sessionStorage/,
	'transactions page export/filter UI must keep financial filters URL-only and must not coerce money strings in the browser'
);
for (const accountDetailCopyKey of [
	'accounts.detail.activityEmptyTitle',
	'accounts.detail.partialActivityTitle',
	'accounts.detail.requestCounters'
]) {
	assert.ok(
		(accountDetailServer + accountDetailPage).includes(accountDetailCopyKey),
		`account detail bounded activity UX must include ${accountDetailCopyKey}`
	);
}
assert.doesNotMatch(
	accountDetailPage,
	/Number\(|parseFloat\(|parseInt\(|localStorage|sessionStorage|\/transactions\/export|TransactionFilters/,
	'account detail activity UI must stay URL-only/bounded and must not reintroduce account-scoped export or browser money coercion'
);
assert.match(
	transactionListPage,
	/pageStart[\s\S]*pageEnd[\s\S]*transactions\.listStatus\.pageRange[\s\S]*transactions\.listStatus\.exportParity/s,
	'transactions page must show a read-only list status summary with page range, order, and CSV cap/parity copy'
);
assert.match(
	i18nMessages,
	/transactions\.listStatus\.title[\s\S]*Current read-only view[\s\S]*transactions\.listStatus\.exportParity[\s\S]*capped at 10,000 rows[\s\S]*Текущий read-only вид[\s\S]*ограничен 10 000 строк/s,
	'localized transaction list status copy must explain active view, filter/export parity, and CSV cap'
);
assert.match(
	i18nMessages,
	/transactions\.export\.emptyStatus[\s\S]*only the CSV header[\s\S]*transactions\.export\.countStatus[\s\S]*CSV amounts stay string values[\s\S]*transactions\.export\.truncatedStatus[\s\S]*first 10,000 rows/s,
	'localized CSV export status copy must explain empty exports, row counts, Decimal/string money, no conversion, and cap truncation'
);
const transactionFiltersComponent = read('src/lib/components/TransactionFilters.svelte');
assert.match(
	transactionFiltersComponent,
	/locale = DEFAULT_LOCALE[\s\S]*t\(locale, 'transactions\.filters\.subtitle'\)[\s\S]*t\(locale, 'transactions\.filters\.stateHelp'\)[\s\S]*t\(locale, 'transactions\.filters\.clear'\)/s,
	'transaction filter UI must render localized read-only/filter/state/reset copy from the i18n catalog'
);
assert.doesNotMatch(
	transactionFiltersComponent,
	/localStorage|sessionStorage/,
	'transaction filters must not persist private filter values in browser storage'
);
const exportProxyRoute = read('src/routes/books/[bookId]/transactions/export/+server.ts');
assert.match(exportProxyRoute, /getAuthToken\(cookies\)/, 'CSV export proxy must read the httpOnly auth cookie on the server');
assert.match(exportProxyRoute, /authorization: `Bearer \$\{token\}`/, 'CSV export proxy must call the API with a bearer token');
assert.match(exportProxyRoute, /content-type.*text\/csv/is, 'CSV export proxy must stream CSV content back to the browser');
for (const exportHeader of [
	'x-csv-export-limit',
	'x-csv-export-total',
	'x-csv-export-truncated',
	'x-csv-export-timeout-policy',
	'x-content-type-options'
]) {
	assert.ok(exportProxyRoute.includes(exportHeader), `CSV export proxy must forward ${exportHeader}`);
}
assert.match(
	transactionListPage,
	/paramsToUrl[\s\S]*sp\.set\('limit'[\s\S]*sp\.set\('offset'/,
	'transaction pagination/filter URLs must include limit and offset'
);
assert.match(
	transactionListPage,
	/data\.writesEnabled[\s\S]*Experimental post-MVP write mode[\s\S]*APP_ENV=test[\s\S]*lock-release evidence[\s\S]*Preview transaction form/,
	'transactions page must show disposable APP_ENV/test and evidence warning text without exposing an enabled write entry point'
);

const transactionDetailServer = read('src/routes/transactions/[id]/+page.server.ts');
const transactionDetailPage = read('src/routes/transactions/[id]/+page.svelte');
assert.match(
	transactionDetailServer,
	/writesEnabled:\s*env\.GNUCASH_WRITES_ENABLED === 'true'/,
	'transaction detail page must expose writesEnabled only when GNUCASH_WRITES_ENABLED is true'
);
assert.match(
	transactionDetailServer,
	/env\.GNUCASH_WRITES_ENABLED !== 'true'/,
	'transaction delete action must be server-gated by GNUCASH_WRITES_ENABLED'
);
assert.match(
	transactionDetailServer,
	/delete_acknowledgement[\s\S]*experimental-delete-acknowledged/,
	'transaction delete action must require explicit acknowledgement'
);
assert.match(
	transactionDetailPage,
	/id="transaction-detail-heading"[\s\S]*transactionDetail\.helper[\s\S]*splitCountLabel/s,
	'transaction detail page must expose a readable heading, read-only helper copy, and split count metadata'
);
assert.match(
	transactionDetailPage,
	/min-w-0 rounded-2xl[\s\S]*grid min-w-0 grid-cols-2[\s\S]*font-mono text-xs/s,
	'transaction detail page must use bounded responsive metadata layout with truncating transaction id'
);
assert.match(
	transactionDetailPage,
	/canShowWriteAlphaControls[\s\S]*data\.writesEnabled && data\.activeBook && tx\.is_write_alpha_owned[\s\S]*\{#if canShowWriteAlphaControls\}[\s\S]*action="\?\/delete"[\s\S]*confirm\(t\(locale, 'transactionDetail\.deleteConfirm'\)[\s\S]*transactionDetail\.deleteAcknowledgement/s,
	'transaction delete form must be hidden unless write mode is enabled and the transaction is write-alpha-owned, then require browser confirmation plus disposable/test acknowledgement'
);
assert.match(
	transactionDetailPage,
	/showNonOwnedWriteAlphaCopy[\s\S]*!tx\.is_write_alpha_owned[\s\S]*transactionDetail\.nonOwnedTitle[\s\S]*transactionDetail\.nonOwnedHelper/s,
	'transaction detail page must show safe explanatory copy instead of edit/delete controls for non-owned transactions when write mode is enabled'
);
assert.match(
	transactionDetailPage,
	/showWriteAlphaHistoryProvenance[\s\S]*tx\.is_write_alpha_owned[\s\S]*transactionDetail\.writeAlphaHistoryTitle[\s\S]*transactionDetail\.writeAlphaHistoryHelper[\s\S]*transactions\.writeAlphaHistoryBadge/s,
	'transaction detail page must show read-only write-alpha provenance for owned history rows without depending on enabled write controls'
);
assert.match(
	i18nMessages,
	/transactionDetail\.writeAlphaHistoryTitle[\s\S]*Created through write-alpha app metadata[\s\S]*transactionDetail\.writeAlphaHistoryHelper[\s\S]*read-only history provenance[\s\S]*Synthetic\/disposable[\s\S]*default writes remain disabled[\s\S]*Создано через app metadata write-alpha[\s\S]*read-only provenance/s,
	'localized transaction detail provenance copy must frame write-alpha history as synthetic/disposable metadata only with default writes disabled'
);
assert.match(
	i18nMessages,
	/transactionDetail\.nonOwnedHelper[\s\S]*Backend ownership guards remain authoritative[\s\S]*write-alpha-owned synthetic\/disposable transactions[\s\S]*transactionDetail\.deleteHelper[\s\S]*write-alpha-owned in app metadata[\s\S]*APP_ENV=test[\s\S]*transactionDetail\.deleteAcknowledgement[\s\S]*backup, audit, and lock-release checks[\s\S]*Экспериментальное удаление транзакции[\s\S]*APP_ENV=test/s,
	'localized delete write-alpha guardrails must mention ownership, backend authority, ignored disposable copies, APP_ENV=test, and backup/audit/lock-release checks'
);

const serverApi = read('src/lib/api/server.ts');
assert.match(
	serverApi,
	/export function resolveActiveBook[\s\S]*can_open_read_only_views[\s\S]*openableBooks\.find\(\(book\) => book\.id === selectedBookId\)[\s\S]*openableBooks\.find\(\(book\) => book\.is_default\)[\s\S]*openableBooks\[0\]/,
	'book context must prefer selected openable book, then openable default, then first openable book'
);
assert.match(
	serverApi,
	/invalid_selected_book_cookie[\s\S]*stale_selected_book_cookie[\s\S]*unavailable_selected_book[\s\S]*no_accessible_books/,
	'book context must classify invalid, stale, unavailable, and empty accessible-book recovery cases'
);
assert.match(
	serverApi,
	/cookies\.set\(SELECTED_BOOK_COOKIE[\s\S]*sameSite: 'lax'/,
	'invalid selected book cookies must be replaced with an accessible fallback cookie'
);
assert.match(
	serverApi,
	/cookies\.delete\(SELECTED_BOOK_COOKIE/,
	'book context must clear the selected-book cookie when no accessible fallback exists'
);
assert.match(
	layoutServer,
	/book_context=\$\{recovery\.reason\}/,
	'stale or invalid selected-book context must redirect users to /books for safe review'
);
assert.match(
	booksPageServer,
	/BOOK_CONTEXT_NOTICE_KEYS[\s\S]*invalid_selected_book_cookie[\s\S]*stale_selected_book_cookie[\s\S]*no_accessible_books/,
	'/books must accept only known book-context recovery notices'
);
assert.match(
	booksPageServer,
	/unavailable_selected_book/,
	'/books must accept a safe unavailable selected-book notice from the server-validated select route'
);
assert.match(
	booksPage,
	/books\.contextRecoveryTitle[\s\S]*books\.contextRecoveryNoBooks[\s\S]*books\.contextRecoveryUnavailable[\s\S]*books\.contextRecoveryStale/s,
	'/books must show a safe recovery notice for stale/invalid/unavailable selected-book cookies and no accessible books'
);
for (const routeFile of [
	'src/routes/+layout.server.ts',
	'src/routes/dashboard/+page.server.ts',
	'src/routes/accounts/+page.server.ts',
	'src/routes/accounts/[id]/+page.server.ts',
	'src/routes/scheduled/+page.server.ts',
	'src/routes/transactions/+page.server.ts',
	'src/routes/transactions/[id]/+page.server.ts'
]) {
	assert.match(
		read(routeFile),
		/getActiveBookContext/,
		`${routeFile} must resolve book-aware data routes from the accessible book context`
	);
}

const bookSwitcher = read('src/lib/components/BookSwitcher.svelte');
assert.match(bookSwitcher, /Current book:/, 'book switcher must label the current book clearly');
assert.match(
	bookSwitcher,
	/currentRouteNext\(\)[\s\S]*window\.location\.pathname[\s\S]*window\.location\.search[\s\S]*\/books\/\$\{encodeURIComponent\(bookId\)\}\/select\?next=\$\{encodeURIComponent\(currentRouteNext\(\)\)\}[\s\S]*goto\(safeBookSelectHref\(bookId\)\)/s,
	'book switcher must preserve the current route and query string through the server-validated safe-link route when switching books'
);
assert.doesNotMatch(
	bookSwitcher,
	/document\.cookie|selected_book_id\s*=/,
	'book switcher must not set selected-book cookies client-side'
);
assert.match(
	bookSwitcher,
	/independent read-only books/,
	'book switcher copy must frame multi-book as independent read-only books, not collaborative editing'
);
assert.doesNotMatch(
	bookSwitcher,
	/upload|collaborative|shared wallet|family wallet/i,
	'book switcher must not add upload or collaborative/family-wallet framing'
);

const transactionFilters = read('src/lib/components/TransactionFilters.svelte');
assert.match(
	transactionFilters,
	/validateDateRange[\s\S]*t\(locale, 'transactions\.filters\.startDateError'\)/,
	'transaction filters must reject inverted date ranges before navigation'
);
assert.match(
	transactionFilters,
	/validateAmountRange[\s\S]*t\(locale, 'transactions\.filters\.amountError'\)/,
	'transaction filters must reject inverted amount ranges before navigation'
);
assert.match(
	transactionFilters,
	/activeFilterSummary[\s\S]*transactions\.filters\.summary\.search[\s\S]*selectedAccount\.full_name[\s\S]*transactions\.filters\.summary\.amount/s,
	'transaction filters must build a readable active filter summary for search, account, date, and amount filters'
);
assert.match(
	transactionFilters,
	/transactionState[\s\S]*transactions\.filters\.summary\.state[\s\S]*name="transaction_state"[\s\S]*transactions\.filters\.stateUnreconciled[\s\S]*transactions\.filters\.stateCleared[\s\S]*transactions\.filters\.stateReconciled[\s\S]*transactions\.filters\.stateVoided/s,
	'transaction filters must expose a safe split reconciliation state selector and active summary'
);
assert.match(
	transactionFilters,
	/t\(locale, 'transactions\.filters\.activeSummaryTitle'\)[\s\S]*aria-label="Active transaction filters"/,
	'active filter summary must tell users the same filters apply to list and CSV export'
);
assert.match(
	transactionFilters,
	/t\(locale, 'transactions\.filters\.search'\)[\s\S]*t\(locale, 'transactions\.filters\.searchPlaceholder'\)/,
	'transaction search helper copy must honestly cover descriptions and split memos'
);
assert.match(
	transactionFilters,
	/t\(locale, 'transactions\.filters\.datePresets'\)[\s\S]*datePresets[\s\S]*preset\.href[\s\S]*transactions\.filters\.datePresetAria/s,
	'transaction filters must render accessible date preset links from server-provided query URLs'
);
assert.match(
	transactionFilters,
	/clearFiltersHref[\s\S]*href=\{clearFiltersHref\}[\s\S]*t\(locale, 'transactions\.filters\.clear'\)/,
	'transaction filters must render an explicit URL-based Clear filters link'
);
assert.match(
	transactionFilters,
	/t\(locale, 'transactions\.filters\.customDateRange'\)[\s\S]*id="tx-date-from"[\s\S]*type="date"[\s\S]*id="tx-date-to"[\s\S]*type="date"/s,
	'custom date inputs must remain visible alongside preset links'
);

const newTransactionPage = read('src/routes/transactions/new/+page.svelte');
assert.match(
	newTransactionPage,
	/WriteModeWarning/,
	'new transaction page must render prominent write-mode warning component'
);
assert.match(
	newTransactionPage,
	/Preview only \/ no write executed[\s\S]*POST \/books\/&lbrace;book_id&rbrace;\/transactions\/create-preview[\s\S]*No CREATE, PATCH, DELETE, or batch operation is executed/s,
	'new transaction page must state preview-only/no-write behavior and the exact non-mutating endpoint'
);

assert.match(writeModeWarningComponent, /writeMode\.title[\s\S]*writeMode\.message[\s\S]*writeMode\.desktop[\s\S]*writeMode\.disposableOnly[\s\S]*writeMode\.createOnlyDogfood[\s\S]*writeMode\.evidence[\s\S]*writeMode\.staleLock[\s\S]*writeMode\.neverRealBook/s, 'write warning component must render localized warning keys');
assert.match(
	newTransactionPage,
	/formaction="\?\/preview"[\s\S]*Preview transaction/s,
	'new transaction page must submit only through the preview action'
);
assert.match(
	newTransactionPage,
	/type="button" disabled[\s\S]*Create disabled|Create disabled[\s\S]*type="button" disabled/s,
	'new transaction page may show only an inert disabled Create control'
);
assert.doesNotMatch(
	newTransactionPage,
	/write_acknowledgement|experimental-write-mode-acknowledged|writeMode\.acknowledgement|writeMode\.finalConfirm|formaction="\?\/create"|Create transaction<\/button>/,
	'new transaction preview page must not retain final-write acknowledgement or active create controls'
);
assert.match(
	newTransactionServer,
	/if \(typeof detail === 'string'\) \{\s*const fieldErrors = fieldErrorsFromString\(detail\);\s*return \{ error: previewErrorSummary\(fieldErrors\), fieldErrors \};\s*\}/s,
	'new transaction preview server errors must map string API details through fixed summaries instead of rendering raw details'
);
assert.doesNotMatch(
	newTransactionServer,
	/function safeMessage|safeMessage\(detail\)|return detail;/,
	'new transaction preview server errors must avoid rendering raw path-like API details'
);
assert.ok(
	transactionDetailServer.includes('detail.length <= 180 && !/[\\\\/]/.test(detail)') &&
		transactionDetailServer.includes('Write-alpha request failed safely'),
	'transaction delete server errors must avoid rendering raw path-like API details'
);

for (const file of walk(join(root, 'src'))) {
	const content = readFileSync(file, 'utf8');
	// Theme-related files are allowed to use localStorage for theme preference only (not auth tokens)
	if (file.endsWith('app.html') || file.endsWith('theme.ts')) {
		assert.doesNotMatch(content, /access_token/, `${file} must not reference auth tokens`);
		continue;
	}
	assert.doesNotMatch(content, /localStorage|sessionStorage/, `${file} must not use localStorage/sessionStorage`);
}

console.log('auth route checks passed');
