import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

function read(...segments) {
	return readFileSync(join(root, ...segments), 'utf8');
}

const packageJson = JSON.parse(read('package.json'));
const layoutServer = read('src', 'routes', '+layout.server.ts');
const layoutSvelte = read('src', 'routes', '+layout.svelte');
const apiServer = read('src', 'lib', 'api', 'server.ts');
const desktopNav = read('src', 'lib', 'components', 'DesktopNav.svelte');
const mobileNav = read('src', 'lib', 'components', 'MobileNav.svelte');
const bookSwitcher = read('src', 'lib', 'components', 'BookSwitcher.svelte');
const loginServer = read('src', 'routes', 'login', '+page.server.ts');
const loginPage = read('src', 'routes', 'login', '+page.svelte');
const messages = read('src', 'lib', 'i18n', 'messages.ts');
const listServer = read('src', 'routes', 'admin', 'users', '+page.server.ts');
const newServer = read('src', 'routes', 'admin', 'users', 'new', '+page.server.ts');
const detailServer = read('src', 'routes', 'admin', 'users', '[userId]', '+page.server.ts');
const browserSmoke = read('scripts', 'test-admin-users-browser.mjs');

assert.equal(
	packageJson.scripts?.['test:admin-users-auth-hardening'],
	'node scripts/test-admin-users-auth-hardening.mjs',
	'package.json must expose the deterministic admin auth hardening gate'
);

assert.match(
	apiServer,
	/const AUTH_COOKIE = 'access_token'[\s\S]*const SELECTED_BOOK_COOKIE = 'selected_book_id'[\s\S]*clearAuthSessionCookies[\s\S]*cookies\.delete\(AUTH_COOKIE, \{ path: '\/' \}\)[\s\S]*cookies\.delete\(SELECTED_BOOK_COOKIE, \{ path: '\/' \}\)[\s\S]*redirectToSessionChanged[\s\S]*\/login\?reason=session_changed/s,
	'server helpers must centrally clear access_token and selected_book_id at path=/ before fixed session_changed redirect'
);
assert.match(
	apiServer,
	/apiFetch<T>\([\s\S]*sessionCookies\?: Cookies[\s\S]*response\.status === 401[\s\S]*redirectToSessionChanged\(sessionCookies\)[\s\S]*throw redirect\(303, '\/login'\)/s,
	'apiFetch must preserve missing-token login behavior while authenticated 401s with cookies clear the session'
);
assert.match(
	apiServer,
	/adminApiMutationFetch<T>\([\s\S]*sessionCookies\?: Cookies[\s\S]*response\.status === 401 \|\| message === 'session_changed'[\s\S]*redirectToSessionChanged\(sessionCookies\)[\s\S]*isRedirect\(reason\)[\s\S]*throw reason/s,
	'admin mutations must redirect/clear on 401 or session_changed safe-code and must not swallow redirects'
);

assert.match(
	layoutServer,
	/getAuthToken\(cookies\)[\s\S]*getCurrentUser\(fetch, token, cookies\)[\s\S]*isCurrentUserAdmin\(currentUser\)[\s\S]*getActiveBookContext\(fetch, cookies, token, \{ includeUnavailableBooks: true \}\)[\s\S]*currentUser,[\s\S]*isAdmin,/s,
	'root authenticated layout must obtain /auth/me server-side and expose only safe currentUser/isAdmin data'
);
assert.match(
	layoutSvelte,
	/isAdmin = \$derived\(data\.isAdmin === true\)[\s\S]*<DesktopNav[^>]*\{isAdmin\}[\s\S]*<MobileNav[^>]*\{isAdmin\}/s,
	'root layout must pass server-derived isAdmin into both nav components'
);
for (const [label, source] of [['desktop', desktopNav], ['mobile', mobileNav]]) {
	assert.match(source, /isAdmin = false[\s\S]*showAdminUsers = \$derived\(isAdmin === true\)[\s\S]*href: '\/admin\/users'/s, `${label} nav must show admin users only from the server-provided isAdmin prop`);
	assert.doesNotMatch(source, /\$app\/state|page\.data|localStorage|sessionStorage|jwt|token/i, `${label} nav must not infer authority from client state, storage, JWTs, or tokens`);
}

assert.match(
	apiServer,
	/const apiBooks = await apiFetch<Book\[\]>\(fetchFn, '\/books', token, cookies\)[\s\S]*const openableBooks = apiBooks\.filter\(\(book\) => book\.can_open_read_only_views\)[\s\S]*resolveActiveBook\(apiBooks, selectedCookie\.selectedBookId\)[\s\S]*apiBooks\.some\(\(book\) => book\.id === selectedCookie\.selectedBookId && !book\.can_open_read_only_views\)[\s\S]*options\.includeUnavailableBooks[\s\S]*book\.id !== recovery\.selectedBookId \|\| book\.can_open_read_only_views[\s\S]*: openableBooks[\s\S]*return \{[\s\S]*books,/s,
	'active-book context must recover from unavailable selected books using API truth, keep full book data only when requested, and remove stale selected metadata from returned layout/page data'
);
assert.match(layoutServer, /getActiveBookContext\(fetch, cookies, token, \{ includeUnavailableBooks: true \}\)/, 'root layout must request full registered book data while select routes keep the default openable-only context');
assert.match(
	bookSwitcher,
	/openableBooks = \$derived\(books\.filter\(\(book\) => book\.can_open_read_only_views\)\)[\s\S]*openableBooks\.length > 1[\s\S]*#each openableBooks as book/s,
	'BookSwitcher must not render stale unavailable/revoked book options'
);

assert.match(loginServer, /const LOGIN_REASONS = new Set\(\['session_changed'\]\)[\s\S]*safeLoginReason[\s\S]*url\.searchParams\.get\('reason'\)/s, 'login load must allowlist URL reasons and never echo arbitrary query strings');
assert.match(loginServer, /const SELECTED_BOOK_COOKIE = 'selected_book_id'[\s\S]*cookies\.delete\(SELECTED_BOOK_COOKIE, \{ path: '\/' \}\)[\s\S]*cookies\.set\(AUTH_COOKIE, data\.access_token/s, 'login success must clear stale selected_book_id before establishing a new authenticated session');
assert.match(loginPage, /data\.loginReason === 'session_changed'[\s\S]*login\.notice\.sessionChanged/s, 'login page must render fixed session_changed copy only from the allowlisted reason');
assert.match(messages, /'login\.notice\.sessionChanged': 'Session changed\. Sign in again to continue\.'[\s\S]*'login\.notice\.sessionChanged': 'Сессия изменилась\. Войдите заново, чтобы продолжить\.'/s, 'i18n must include fixed EN/RU session-changed copy');
assert.doesNotMatch(loginPage, /URLSearchParams|location\.search|safe_message|raw_backend|raw_|detail\./i, 'login page must not parse or echo raw query/backend detail strings client-side');

assert.match(listServer, /parent\(\)[\s\S]*currentUser = layoutData\.currentUser[\s\S]*apiFetch<AdminUserList>\(fetch, `\/admin\/users\?\$\{params\.toString\(\)\}`, token, cookies\)/s, 'admin list load must reuse session-hardened parent /auth/me and harden admin payload fetch');
assert.match(newServer, /load: PageServerLoad = async \(\{ cookies, parent \}\)[\s\S]*parent\(\)[\s\S]*isCurrentUserAdmin\(layoutData\.currentUser\)/s, 'admin create load must reuse parent /auth/me');
assert.match(newServer, /getCurrentUser\(fetchFn, token, cookies\)[\s\S]*adminApiMutationFetch<AdminUserDetail>[\s\S]*'POST'[\s\S]*\}, cookies\)/s, 'admin create action must session-harden live /auth/me and mutation calls');
assert.match(detailServer, /adminActorFromLayout[\s\S]*parent\(\)[\s\S]*apiFetch<AdminUserDetail>\(fetch, `\/admin\/users\/\$\{userId\}`, token, cookies\)[\s\S]*apiFetch<AdminBookOptionList>\(fetch, '\/admin\/book-access\/books\?limit=50&offset=0', token, cookies\)/s, 'admin detail load must reuse parent /auth/me and parse paginated book options');
assert.match(detailServer, /getCurrentUser\(fetchFn, token, cookies\)[\s\S]*redirectToSessionChanged\(cookies\)[\s\S]*adminApiMutationFetch<null>[\s\S]*'DELETE', undefined, cookies\)/s, 'admin detail actions must session-harden live /auth/me, self reset, and mutations');

for (const snippet of [
	'zeroBooksToken',
	'revoked selected_book_id must recover to the default openable book cookie',
	'zero accessible books must delete selected_book_id cookie',
	'other assigned openable selected_book_id must persist without fallback',
	'direct revoked book URL must render a fixed safe 404 state',
	'401 admin mutation must clear access_token cookie',
	'expired 401 layout load must clear selected_book_id cookie',
	"location.search === '?reason=session_changed'"
]) {
	assert.ok(browserSmoke.includes(snippet), `browser smoke must cover ${snippet}`);
}

console.log('admin users auth hardening static checks passed');
