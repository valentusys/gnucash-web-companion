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
const emptyStateComponent = read('src/lib/components/EmptyState.svelte');
assert.match(emptyStateComponent, /role=\{role\}/, 'EmptyState must expose an overridable accessible status role');
assert.match(emptyStateComponent, /aria-label=\{ariaLabel\}/, 'EmptyState must expose an aria-label for screen-reader context');
const errorStateComponent = read('src/lib/components/ErrorState.svelte');
assert.match(errorStateComponent, /statusCode[\s\S]*403[\s\S]*404[\s\S]*defaultTitle/s, 'ErrorState must map 403, 404, and generic API/network failures to helpful copy');
assert.match(errorStateComponent, /retryHref[\s\S]*backHref[\s\S]*aria-label/s, 'ErrorState must offer keyboard-focusable retry/back actions with labels');
const errorPage = read('src/routes/+error.svelte');
assert.match(errorPage, /import ErrorState/, 'global error page must reuse ErrorState');
assert.match(errorPage, /statusCode=\{page\.status\}[\s\S]*retryHref=\{page\.url\.pathname \+ page\.url\.search\}[\s\S]*backHref="\/dashboard"/s, 'global error page must pass status and retry/back actions');
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
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/dashboard'[\s\S]*'\/accounts'[\s\S]*'\/scheduled'/, 'dashboard, accounts, and scheduled routes must be protected');
assert.match(hooks, /redirect\(303, `\/login\?next=/, 'protected routes must redirect to /login');
assert.match(hooks, /cookies\.get\('access_token'\)/, 'protected routes must use the httpOnly cookie');

const loginServer = read('src/routes/login/+page.server.ts');
assert.match(loginServer, /cookies\.set\(AUTH_COOKIE, data\.access_token/, 'login must store token in cookie');
assert.match(loginServer, /httpOnly:\s*true/, 'auth cookie must be httpOnly');
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

const i18nMessages = read('src/lib/i18n/messages.ts');
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
	"'accounts.title': 'Дерево счетов'",
	"'transactions.title': 'Просмотр транзакций'",
	"'books.title': 'Book management'",
	"'books.title': 'Управление книгами'",
	'Книги доступны только для просмотра метаданных',
	"'transactions.filters.title': 'Transaction filters'",
	"'transactions.filters.title': 'Фильтры транзакций'",
	'Сужают read-only список транзакций и CSV export',
	"'transactions.filters.stateHelp'",
	'Фильтрует по состоянию сверки split в GnuCash; транзакции не редактируются.',
	"'transactions.export.statusFiltered'",
	'Экспортирует текущий read-only отфильтрованный вид',
	"'transactions.export.accountStatus'"
]) {
	assert.ok(i18nMessages.includes(phrase), `i18n messages must include: ${phrase}`);
}

const localeSwitcher = read('src/lib/components/LocaleSwitcher.svelte');
assert.match(localeSwitcher, /method="POST" action="\/locale"/, 'locale switcher must submit through the server cookie route');
assert.doesNotMatch(localeSwitcher, /localStorage|sessionStorage/, 'locale switcher must not use browser storage');

const transactionsServer = read('src/routes/transactions/+page.server.ts');
assert.match(
	transactionsServer,
	/writesEnabled:\s*env\.GNUCASH_WRITES_ENABLED === 'true'/,
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
	/buildTransactionFilterUrl[\s\S]*date_from[\s\S]*date_to[\s\S]*account_id[\s\S]*min_amount[\s\S]*max_amount[\s\S]*transaction_state/s,
	'date preset URLs must preserve existing non-date transaction filters, including state, while using date_from/date_to query params'
);
assert.match(
	transactionsServer,
	/buildClearFiltersUrl[\s\S]*limit[\s\S]*offset[\s\S]*clearFiltersHref:\s*buildClearFiltersUrl/,
	'transactions server load must expose a clear-all filter URL that resets to the first page without private saved filters'
);
assert.match(
	transactionsServer,
	/datePresets:\s*buildDatePresets/,
	'transactions server load must return date preset URL data to the page'
);

const newTransactionServer = read('src/routes/transactions/new/+page.server.ts');
assert.match(
	newTransactionServer,
	/env\.GNUCASH_WRITES_ENABLED !== 'true'[\s\S]*redirect\(303, '\/transactions'\)/,
	'new transaction page must redirect when frontend writes are disabled'
);
assert.match(
	newTransactionServer,
	/hasWriteAcknowledgement\(formData\)[\s\S]*experimental controlled-write transaction/,
	'final create action must require explicit write acknowledgement'
);
assert.ok(
	newTransactionServer.indexOf('hasWriteAcknowledgement(formData)') <
		newTransactionServer.indexOf('`/books/${bookId}/transactions/validate`', newTransactionServer.indexOf('create:')),
	'write acknowledgement must be checked before final create validation/write API calls'
);

const booksPageServer = read('src/routes/books/+page.server.ts');
assert.match(booksPageServer, /getActiveBookContext\(fetch, cookies, token\)/, '/books page must resolve accessible book metadata and the current/default book through the authenticated API context');
assert.doesNotMatch(booksPageServer, /upload|delete|write|edit/i, '/books page server load must stay metadata/read-only only');

const booksSelectRoute = read('src/routes/books/[bookId]/select/+server.ts');
assert.match(booksSelectRoute, /getActiveBookContext\(fetch, cookies, token\)/, 'book safe-link route must verify selected book against accessible API context before setting a cookie');
assert.match(booksSelectRoute, /cookies\.set\('selected_book_id'[\s\S]*sameSite:\s*'lax'/s, 'book safe-link route must preserve active book context with the existing non-secret sameSite cookie');
assert.match(booksSelectRoute, /SAFE_NEXT_PATHS[\s\S]*'\/dashboard'[\s\S]*'\/accounts'[\s\S]*'\/transactions'[\s\S]*'\/scheduled'/s, 'book safe-link route must redirect only to approved read-only views');
assert.doesNotMatch(booksSelectRoute, /upload|delete|registry|admin|write|edit/i, 'book safe-link route must not expose management workflows');

const booksPage = read('src/routes/books/+page.svelte');
for (const requiredPhrase of [
	'Book management',
	'Read-only view/manage metadata only',
	'Active/default book',
	'Base currency',
	'Storage type',
	'Read-only',
	'Access status: Accessible',
	'Archived and unauthorized books are hidden or blocked by the API',
	'Open safe views',
	'View accounts',
	'Browse transactions',
	'View scheduled metadata',
	'Dashboard summary',
	'No registry management actions are available on this read-only page.'
]) {
	assert.ok(i18nMessages.includes(requiredPhrase), `books i18n catalog must include canonical English phrase: ${requiredPhrase}`);
}
assert.match(booksPage, /import EmptyState/, '/books page must reuse the accessible EmptyState component for no accessible books');
assert.match(booksPage, /<EmptyState[\s\S]*title=\{t\(locale, 'books\.emptyTitle'\)\}[\s\S]*message=\{t\(locale, 'books\.emptyMessage'\)\}[\s\S]*href="\/login"[\s\S]*Sign in again/s, '/books page must give no-books users clear copy and a keyboard-focusable recovery action');
assert.match(booksPage, /DEFAULT_LOCALE[\s\S]*t\(locale, 'books\.title'\)[\s\S]*t\(locale, 'books\.readonlyStatus'\)/s, '/books page must render localized titles and read-only safety labels from the i18n catalog');
assert.match(booksPage, /t\(locale, 'books\.safetyNote'\)/, '/books page must render localized read-only safety note');
assert.match(booksPage, /data\.books[\s\S]*book\.name[\s\S]*book\.base_currency[\s\S]*book\.storage_type[\s\S]*book\.access_role[\s\S]*book\.status/s, '/books page must render book name, base currency, storage type, access role, and status');
assert.match(booksPage, /book\.is_default[\s\S]*t\(locale, 'books\.defaultBook'\)/s, '/books page must clearly mark the active/default book');
assert.match(booksPage, /\/books\/\$\{book\.id\}\/select\?next=\/accounts[\s\S]*\/books\/\$\{book\.id\}\/select\?next=\/transactions[\s\S]*\/books\/\$\{book\.id\}\/select\?next=\/scheduled[\s\S]*\/books\/\$\{book\.id\}\/select\?next=\/dashboard/s, '/books page must expose safe book-context links to read-only views');
assert.doesNotMatch(booksPage, /<form|<input|type="file"|method="POST"|Upload book|Delete book|collaborative|shared wallet|family wallet/i, '/books page must not offer upload/delete controls or collaborative/family-wallet framing');

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
assert.match(i18nMessages, /GNUCASH_WRITES_ENABLED=false[\s\S]*safety\.currentBook[\s\S]*safety\.reviewBooks/s, 'localized safety copy must state the default-disabled write flag and expose current-book/books labels');
const bookSwitcherComponent = read('src/lib/components/BookSwitcher.svelte');
assert.match(bookSwitcherComponent, /compact = false[\s\S]*min-h-11[\s\S]*max-w-full[\s\S]*truncate/s, 'book switcher must support compact mobile rendering with 44px touch height and no overflow');
const localeSwitcherComponentForMobile = read('src/lib/components/LocaleSwitcher.svelte');
assert.match(localeSwitcherComponentForMobile, /min-h-11[\s\S]*min-w-\[44px\]/, 'locale switcher select must expose a 44px touch target');
const transactionSplitsComponent = read('src/lib/components/TransactionSplits.svelte');
assert.match(transactionSplitsComponent, /md:hidden[\s\S]*split\.account_name[\s\S]*Money[\s\S]*split\.memo[\s\S]*reconcileLabel\(split\.reconcile_state\)/s, 'transaction detail splits must render mobile cards with account, amount, memo, and reconciliation metadata instead of forcing a horizontal table at 320px');
assert.match(transactionSplitsComponent, /hidden overflow-x-hidden md:block[\s\S]*table-fixed[\s\S]*Reconciliation[\s\S]*reconcileLabel\(split\.reconcile_state\)/s, 'transaction detail split table must be desktop-only, bounded, and expose reconciliation state');
assert.match(transactionSplitsComponent, /splits\.length === 0[\s\S]*No split rows were returned[\s\S]*does not invent balancing data/s, 'transaction detail splits must show a safe empty state instead of inventing data');
assert.doesNotMatch(transactionSplitsComponent, /overflow-x-auto|min-w-full/, 'transaction detail splits must not introduce mobile horizontal scrolling');

const scheduledServer = read('src/routes/scheduled/+page.server.ts');
assert.match(
	scheduledServer,
	/getActiveBookContext\(fetch, cookies, token\)[\s\S]*apiFetch<ScheduledTransaction\[\]>\(fetch, `\$\{bookPrefix\}\/scheduled-transactions`, token\)/s,
	'scheduled page must load safe scheduled metadata for the active accessible book through the API'
);
const scheduledPage = read('src/routes/scheduled/+page.svelte');
for (const scheduledPhrase of [
	'Scheduled transactions',
	'Read-only scheduled transaction awareness',
	'Use GnuCash Desktop as the authoritative editor',
	'Template split details and private raw SQL are not exposed',
	'No scheduled transactions are available through the safe read-only adapter'
]) {
	assert.ok(scheduledPage.includes(scheduledPhrase), `scheduled page must include conservative copy: ${scheduledPhrase}`);
}
assert.match(scheduledPage, /import EmptyState/, 'scheduled page must reuse EmptyState for no schedules');
assert.match(scheduledPage, /<EmptyState[\s\S]*title="No scheduled transactions found"[\s\S]*href="\/transactions"[\s\S]*Browse transactions/s, 'scheduled empty state must include clear copy and keyboard-focusable navigation');
assert.doesNotMatch(
	scheduledPage,
	/<form|method="POST"|New scheduled|Edit scheduled|Delete scheduled|next occurrence|next-run/i,
	'scheduled page must not expose scheduling editor controls or fake next-run copy'
);

const transactionTable = read('src/lib/components/TransactionTable.svelte');
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

const accountTree = read('src/lib/components/AccountTree.svelte');
const accountsPage = read('src/routes/accounts/+page.svelte');
assert.match(accountsPage, /<EmptyState[\s\S]*title="No accounts found"[\s\S]*href="\/books"[\s\S]*Review available books/s, 'accounts empty state must clearly explain unavailable accounts and link to books');
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
	/name, account\.full_name, account\.type, account\.currency[\s\S]*Showing \{filteredAccountCount\} of \{totalAccountCount\} accounts/s,
	'account tree filter must search names/full paths/type/currency and report filtered counts'
);
assert.match(
	accountTree,
	/Use the filter to narrow large read-only account trees without changing the book/s,
	'account tree filter helper copy must frame filtering as local read-only discoverability only'
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
	/overflow-hidden[\s\S]*truncate font-medium[\s\S]*truncate text-sm/s,
	'account tree names and full names must truncate safely for narrow desktop layouts'
);

const transactionListPage = read('src/routes/transactions/+page.svelte');
assert.match(transactionListPage, /import EmptyState/, 'transactions page must reuse EmptyState for empty result sets');
assert.match(transactionListPage, /hasActiveFilters[\s\S]*No transactions match the current filters[\s\S]*No transactions yet/s, 'transactions page must distinguish no data from filters with no matches');
assert.match(transactionListPage, /<EmptyState[\s\S]*href=\{data\.clearFiltersHref\}[\s\S]*Clear filters/s, 'filtered transaction empty state must offer a keyboard-focusable clear-filters action');
for (const filterParam of ['query', 'date_from', 'date_to', 'account_id', 'min_amount', 'max_amount', 'transaction_state']) {
	assert.ok(
		transactionListPage.includes(`sp.set('${filterParam}'`) ||
			transactionListPage.includes(`sp.set('${filterParam}',`),
		`transactions page URLs must preserve ${filterParam}`
	);
}
assert.ok(
	transactionListPage.includes("/books/${bookId}/transactions/export${qs ? '?' + qs : ''}"),
	'CSV export URL must include the active filter query string'
);

const accountDetailServer = read('src/routes/accounts/[id]/+page.server.ts');
assert.match(
	accountDetailServer,
	/appendAccountTransactionFilters[\s\S]*query[\s\S]*date_from[\s\S]*date_to[\s\S]*min_amount[\s\S]*max_amount[\s\S]*transaction_state/s,
	'account detail server load must forward the approved account-scoped transaction filters'
);
assert.match(
	accountDetailServer,
	/buildAccountFilterUrl[\s\S]*sp\.set\('offset', '0'\)[\s\S]*\/accounts\/\$\{encodeURIComponent\(accountId\)\}/s,
	'account detail date presets must build account-scoped URLs and reset to the first page'
);
assert.match(
	accountDetailServer,
	/buildClearFiltersUrl[\s\S]*\/accounts\/\$\{encodeURIComponent\(accountId\)\}[\s\S]*clearFiltersHref:\s*buildClearFiltersUrl/s,
	'account detail clear-filters URL must stay on the account page without saved browser state'
);

const accountDetailPage = read('src/routes/accounts/[id]/+page.svelte');
assert.match(
	accountDetailPage,
	/TransactionFilters[\s\S]*lockedAccountLabel=\{account\.full_name\}[\s\S]*onChange=\{handleFilter\}/s,
	'account detail page must reuse transaction filters with a locked account scope'
);
assert.match(
	accountDetailPage,
	/new URLSearchParams\(\{ account_id: account\.id \}\)[\s\S]*query[\s\S]*date_from[\s\S]*date_to[\s\S]*min_amount[\s\S]*max_amount[\s\S]*transaction_state[\s\S]*\/books\/\$\{bookId\}\/transactions\/export/s,
	'account detail CSV export URL must include the fixed account_id and the active filters'
);
assert.match(
	accountDetailPage,
	/No transactions match these filters for this account[\s\S]*Clear filters[\s\S]*TransactionTable[\s\S]*onSelect=\{handleSelect\}/s,
	'account detail page must explain filtered empty states and keep transaction detail links'
);
assert.match(
	transactionListPage,
	/t\(locale, 'transactions\.export\.statusFiltered'\)[\s\S]*t\(locale, 'transactions\.export\.statusUnfiltered'\)[\s\S]*exportButtonLabel/s,
	'CSV export copy must come from the localized catalog while preserving filtered/unfiltered read-only status'
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
	'x-csv-export-timeout-policy'
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
	/data\.writesEnabled[\s\S]*Experimental post-MVP write mode[\s\S]*New transaction/,
	'transactions page must show warning text near the enabled write entry point'
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
	/id="transaction-detail-heading"[\s\S]*Read-only view of the selected GnuCash transaction[\s\S]*splitCountLabel/s,
	'transaction detail page must expose a readable heading, read-only helper copy, and split count metadata'
);
assert.match(
	transactionDetailPage,
	/min-w-0 rounded-2xl[\s\S]*grid min-w-0 grid-cols-2[\s\S]*font-mono text-xs/s,
	'transaction detail page must use bounded responsive metadata layout with truncating transaction id'
);
assert.match(
	transactionDetailPage,
	/data\.writesEnabled && data\.activeBook[\s\S]*action="\?\/delete"[\s\S]*confirm\([\s\S]*experimental DELETE is for disposable\/test copies only/s,
	'transaction delete form must be hidden by default and require browser confirmation plus disposable/test acknowledgement'
);

const serverApi = read('src/lib/api/server.ts');
assert.match(
	serverApi,
	/export function resolveActiveBook[\s\S]*books\.find\(\(book\) => book\.id === selectedBookId\)[\s\S]*books\.find\(\(book\) => book\.is_default\)[\s\S]*books\[0\]/,
	'book context must prefer selected accessible book, then accessible default, then first accessible book'
);
assert.match(
	serverApi,
	/cookies\.set\(SELECTED_BOOK_COOKIE[\s\S]*sameSite: 'lax'/,
	'invalid selected book cookies must be replaced with an accessible fallback cookie'
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
	/goto\(`\$\{window\.location\.pathname\}\$\{window\.location\.search\}`\)/,
	'book switcher must preserve the current route and query string when switching books'
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
	/name="write_acknowledgement"[\s\S]*experimental-write-mode-acknowledged[\s\S]*required/,
	'new transaction final create form must include a required acknowledgement checkbox'
);

const writeModeWarning = read('src/lib/components/WriteModeWarning.svelte');
for (const phrase of [
	'experimental post-MVP',
	'MVP v0.1 remains read-only by default',
	'GNUCASH_WRITES_ENABLED=false',
	'GnuCash Desktop remains the authoritative editor',
	'disposable/test copies',
	'Never use this experimental path with your only real financial book'
]) {
	assert.ok(writeModeWarning.includes(phrase), `write warning must include: ${phrase}`);
}

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
