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
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/dashboard'[\s\S]*'\/accounts'/, 'dashboard and accounts routes must be protected');
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
	"'safety.message'",
	'MVP по умолчанию работает только на чтение',
	"'dashboard.title': 'Dashboard'",
	"'dashboard.title': 'Обзор'",
	"'accounts.title': 'Дерево счетов'",
	"'transactions.title': 'Просмотр транзакций'"
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

const transactionListPage = read('src/routes/transactions/+page.svelte');
for (const filterParam of ['query', 'date_from', 'date_to', 'account_id', 'min_amount', 'max_amount']) {
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
const exportProxyRoute = read('src/routes/books/[bookId]/transactions/export/+server.ts');
assert.match(exportProxyRoute, /getAuthToken\(cookies\)/, 'CSV export proxy must read the httpOnly auth cookie on the server');
assert.match(exportProxyRoute, /authorization: `Bearer \$\{token\}`/, 'CSV export proxy must call the API with a bearer token');
assert.match(exportProxyRoute, /content-type.*text\/csv/is, 'CSV export proxy must stream CSV content back to the browser');
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
	/validateDateRange[\s\S]*Start date must be earlier than or equal to end date/,
	'transaction filters must reject inverted date ranges before navigation'
);
assert.match(
	transactionFilters,
	/validateAmountRange[\s\S]*Minimum amount must be less than or equal to maximum amount/,
	'transaction filters must reject inverted amount ranges before navigation'
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
