import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const repoRoot = join(root, '..', '..');

function pathOf(...segments) {
	return join(root, ...segments);
}

function read(...segments) {
	return readFileSync(pathOf(...segments), 'utf8');
}

function walk(dir, files = []) {
	for (const entry of readdirSync(dir)) {
		const full = join(dir, entry);
		if (statSync(full).isDirectory()) walk(full, files);
		else files.push(full);
	}
	return files;
}

const packageJson = JSON.parse(read('package.json'));
assert.equal(packageJson.scripts?.['test:admin-users'], 'node scripts/test-admin-users-static.mjs', 'package.json must expose npm run test:admin-users');

const requiredFiles = [
	['src', 'routes', 'admin', 'users', '+page.server.ts'],
	['src', 'routes', 'admin', 'users', '+page.svelte'],
	['src', 'routes', 'admin', 'users', 'new', '+page.server.ts'],
	['src', 'routes', 'admin', 'users', 'new', '+page.svelte'],
	['src', 'routes', 'admin', 'users', '[userId]', '+page.server.ts'],
	['src', 'routes', 'admin', 'users', '[userId]', '+page.svelte']
];
for (const segments of requiredFiles) {
	assert.ok(existsSync(pathOf(...segments)), `${segments.join('/')} must exist`);
}

const apiTypes = read('src', 'lib', 'api', 'types.ts');
const apiServer = read('src', 'lib', 'api', 'server.ts');
const desktopNav = read('src', 'lib', 'components', 'DesktopNav.svelte');
const mobileNav = read('src', 'lib', 'components', 'MobileNav.svelte');
const messages = read('src', 'lib', 'i18n', 'messages.ts');
const listServer = read('src', 'routes', 'admin', 'users', '+page.server.ts');
const listPage = read('src', 'routes', 'admin', 'users', '+page.svelte');
const newServer = read('src', 'routes', 'admin', 'users', 'new', '+page.server.ts');
const newPage = read('src', 'routes', 'admin', 'users', 'new', '+page.svelte');
const detailServer = read('src', 'routes', 'admin', 'users', '[userId]', '+page.server.ts');
const detailPage = read('src', 'routes', 'admin', 'users', '[userId]', '+page.svelte');

function extractAllowedAdminCodes(source) {
	const match = source.match(/const allowedAdminProblemCodes = new Set<AdminProblemCode>\(\[([\s\S]*?)\]\);/);
	assert.ok(match, 'server helper must declare allowlisted admin problem codes');
	return new Set([...match[1].matchAll(/'([^']+)'/g)].map((entry) => entry[1]));
}

function fixedAdminProblemCodeForTest(payload, fallback, allowedCodes) {
	let candidate = null;
	if (payload && typeof payload === 'object') {
		candidate = payload.safe_code ?? payload.code;
		if (!candidate && payload.detail && typeof payload.detail === 'object') {
			candidate = payload.detail.safe_code ?? payload.detail.code;
		}
	}
	return typeof candidate === 'string' && allowedCodes.has(candidate) ? candidate : fallback;
}

function fallbackAdminProblemCodeForTest(status) {
	if (status === 401) return 'session_changed';
	if (status === 403) return 'admin_required';
	if (status === 404) return 'user_not_found';
	if (status === 409) return 'username_taken';
	if (status === 422) return 'display_name_invalid';
	return 'unknown_admin_problem';
}

assert.match(apiTypes, /export type AdminProblemCode[\s\S]*username_invalid[\s\S]*username_taken[\s\S]*display_name_invalid[\s\S]*password_policy[\s\S]*user_not_found[\s\S]*book_not_assignable[\s\S]*unknown_admin_problem/s, 'AdminProblemCode must model fixed bounded #57 error codes');
assert.match(apiTypes, /export type AdminUserSummary[\s\S]*id: number[\s\S]*username: string[\s\S]*display_name: string[\s\S]*is_admin: boolean[\s\S]*is_enabled: boolean[\s\S]*assignment_count: number[\s\S]*created_at: string[\s\S]*updated_at: string/s, 'AdminUserSummary must use bounded list DTO fields');
assert.match(apiTypes, /export type AdminUserList[\s\S]*items: AdminUserSummary\[\][\s\S]*total_count[\s\S]*limit[\s\S]*offset[\s\S]*has_next/s, 'AdminUserList must model bounded pagination');
assert.match(apiTypes, /export type AdminBookAccessRole = 'owner' \| 'editor' \| 'viewer'/, 'book access roles must preserve owner/editor/viewer semantics');
assert.match(apiTypes, /export type AdminBookOption[\s\S]*id: number[\s\S]*name: string[\s\S]*is_default: boolean/s, 'book option DTO must expose only id/name/is_default');
assert.match(apiTypes, /export type AdminUserDetail = AdminUserSummary & \{[\s\S]*assignments: AdminBookAccess\[\]/s, 'detail DTO must include deterministic assignments');
const adminDtoBlock = apiTypes.slice(apiTypes.indexOf('export type AdminProblemCode'), apiTypes.indexOf('export type BookProblemCode'));
assert.doesNotMatch(adminDtoBlock, /password_hash|auth_version|JWT|cookie|uri_or_path|canonical_path|request_body|raw_/i, 'admin DTOs must not expose secrets, paths, auth internals, or raw audit payloads');

assert.match(apiServer, /allowedAdminProblemCodes[\s\S]*username_invalid[\s\S]*last_enabled_admin[\s\S]*unknown_admin_problem/s, 'server API helper must allow only fixed admin problem codes');
assert.match(apiServer, /fixedAdminProblemCode[\s\S]*record\.safe_code \?\? record\.code[\s\S]*allowedAdminProblemCodes/s, 'server API helper must reduce unknown backend payloads to fixed codes');
assert.match(apiServer, /fallbackAdminProblemCode[\s\S]*status === 401[\s\S]*session_changed[\s\S]*status === 403[\s\S]*admin_required[\s\S]*status === 404[\s\S]*user_not_found/s, 'server API helper must map standard auth/not-found statuses safely');
assert.match(apiServer, /adminApiMutationFetch[\s\S]*method: ApiMutationMethod[\s\S]*body !== undefined \? JSON\.stringify\(body\) : undefined[\s\S]*fixedAdminProblemCode/s, 'admin mutations must use a shared server-side safe-code helper');

assert.match(listServer, /getCurrentUser\(fetch, token\)[\s\S]*if \(!isCurrentUserAdmin\(currentUser\)\)[\s\S]*users,[\s\S]*loadErrorCode: null/s, '/admin/users load must call /auth/me first and return no admin payload for normal users');
assert.ok(listServer.indexOf('if (!isCurrentUserAdmin(currentUser))') < listServer.indexOf('apiFetch<AdminUserList>'), '/admin/users must not fetch admin user list before checking is_admin');
assert.match(listServer, /\/admin\/users\?\$\{params\.toString\(\)\}/, '/admin/users list must call frozen GET /admin/users with bounded query params');
assert.match(listPage, /adminUsers\.adminRequiredTitle[\s\S]*adminUsers\.adminRequiredMessage/s, '/admin/users page must render safe normal-user copy');
assert.match(listPage, /adminUsers\.emptyTitle[\s\S]*adminUsers\.createUser/s, '/admin/users page must render empty state and Create user CTA');
assert.match(listPage, /stateAll[\s\S]*stateEnabled[\s\S]*stateDisabled[\s\S]*has_next/s, '/admin/users page must render bounded state filters and pagination');
for (const field of ['user.username', 'user.display_name', 'user.is_enabled', 'user.is_admin', 'user.assignment_count']) {
	assert.ok(listPage.includes(field), `/admin/users page must render bounded summary field ${field}`);
}

assert.match(newServer, /if \(!\(await requireAdmin\(fetch, token\)\)\)[\s\S]*admin_required/s, '/admin/users/new action must check is_admin before create');
assert.match(newServer, /adminApiMutationFetch<AdminUserDetail>\(fetch, token, '\/admin\/users', 'POST'[\s\S]*username[\s\S]*display_name[\s\S]*password: initialPassword[\s\S]*is_admin/s, 'create action must call frozen POST /admin/users with exact create fields');
assert.doesNotMatch(newServer, /book_access|assignments|rollback|\/admin\/users\/\$\{.*\}\/book-access/s, 'create route must not mix initial assignments into ambiguous post-create rollback semantics');
assert.match(newServer, /function secretField[\s\S]*String\(form\.get\(name\) \?\? ''\)[\s\S]*const initialPassword = secretField\(form, 'initial_password'\)/s, 'create action must preserve exact submitted password text and not trim it');
assert.match(newPage, /name="initial_password" required type="password" autocomplete="new-password"/, 'create page password input must be new-password and server-form based');
assert.doesNotMatch(newPage, /initial_password[^>]+value=|password[^>]+value=\{previous|password[^>]+bind:value/s, 'create page must never repopulate password fields');
assert.ok(newPage.includes('adminUsers.zeroAccessDefault'), 'create page must explain zero access default');
assert.ok(newPage.includes('adminUsers.isAdminChoice') && newPage.includes('name="is_admin"'), 'create page must expose creation-only admin choice');

for (const [label, source, endpoint] of [
	['detail load', detailServer, '`/admin/users/${userId}`'],
	['book options', detailServer, "'/admin/book-access/books?limit=50&offset=0'"],
	['display name', detailServer, "`/admin/users/${userId}`"],
	['enable', detailServer, "`/admin/users/${userId}/enable`"],
	['disable', detailServer, "`/admin/users/${userId}/disable`"],
	['password reset', detailServer, "`/admin/users/${userId}/password-reset`"],
	['grant', detailServer, "`/admin/users/${userId}/book-access/${bookId}`"],
	['revoke', detailServer, "`/admin/users/${userId}/book-access/${bookId}`"]
]) {
	assert.ok(source.includes(endpoint), `${label} must use frozen endpoint ${endpoint}`);
}
assert.match(detailServer, /getCurrentUser\(fetchFn, token\)[\s\S]*isCurrentUserAdmin\(currentUser\)/s, 'detail route must derive authority from /auth/me');
assert.match(detailServer, /PATCH[\s\S]*display_name: displayName/s, 'detail update must PATCH display_name only');
assert.match(detailServer, /confirm_disable[\s\S]*\/disable/s, 'disable action must require explicit confirmation');
assert.ok(detailServer.includes("form.get('confirm_reset')") && detailServer.includes("secretField(form, 'new_password')") && detailServer.includes('password-reset'), 'reset action must require explicit confirmation and a new password');
assert.match(detailServer, /confirm_revoke[\s\S]*'DELETE'/s, 'revoke action must require explicit confirmation and call DELETE');
assert.match(detailServer, /cookies\.delete\('access_token'[\s\S]*cookies\.delete\('selected_book_id'[\s\S]*\/login\?reason=session_changed/s, 'self reset must clear cookies and redirect to a fixed session-changed login URL');
assert.match(detailServer, /const ACCESS_ROLES[\s\S]*owner[\s\S]*editor[\s\S]*viewer[\s\S]*return ACCESS_ROLES\.has[\s\S]*: 'viewer'/s, 'grant role parser must allow only owner/editor/viewer and default to viewer');
assert.match(detailServer, /function secretField[\s\S]*String\(form\.get\(name\) \?\? ''\)[\s\S]*const newPassword = secretField\(form, 'new_password'\)/s, 'reset action must preserve exact submitted password text and not trim it');

assert.match(detailPage, /action="\?\/updateDisplayName"[\s\S]*name="display_name"/s, 'detail page must expose display-name update');
assert.doesNotMatch(detailPage, /name="username"|name="is_admin"|promote|demote|hard delete|username edit|delete user/i, 'detail page must not expose username/admin mutation or delete wording');
assert.match(detailPage, /name="new_password" required type="password" autocomplete="new-password"/, 'detail reset field must use autocomplete=new-password');
assert.doesNotMatch(detailPage, /new_password[^>]+value=|password[^>]+bind:value/s, 'detail page must never repopulate password fields');
assert.match(detailPage, /confirmDisableCopy[\s\S]*disableSubmit[\s\S]*confirmResetCopy[\s\S]*resetPasswordSubmit[\s\S]*confirmRevokeCopy[\s\S]*revokeSubmit/s, 'detail page must render safe confirmations for disable/reset/revoke');
assert.match(detailPage, /const roles: AdminBookAccessRole\[\] = \['viewer', 'editor', 'owner'\][\s\S]*function roleCopy[\s\S]*adminUsers\.roleCopy\.\$\{role\}[\s\S]*roleBoundary/s, 'detail page must explain viewer/editor/owner honestly');
assert.match(detailPage, /<option value="viewer" selected>[\s\S]*adminUsers\.role\.viewer/s, 'new grants must default to viewer');
assert.match(detailPage, /data\.bookOptions\.length[\s\S]*adminUsers\.noBooksTitle[\s\S]*data\.user\.assignments\.length[\s\S]*adminUsers\.noAssignments/s, 'detail page must cover zero books and zero assignments');

assert.match(desktopNav, /page\.data as \{ isAdmin\?: boolean \}[\s\S]*showAdminUsers[\s\S]*href: '\/admin\/users'[\s\S]*nav\.adminUsers/s, 'desktop nav must show admin users only from server-provided page data/prop isAdmin');
assert.match(mobileNav, /page\.data as \{ isAdmin\?: boolean \}[\s\S]*showAdminUsers[\s\S]*href: '\/admin\/users'[\s\S]*nav\.adminUsers/s, 'mobile nav must show admin users only from server-provided page data/prop isAdmin');
assert.doesNotMatch(`${desktopNav}\n${mobileNav}`, /username|display_name|management_actions|books\.length/, 'nav admin visibility must not infer authority from usernames, display names, books, or actions');

for (const key of [
	'nav.adminUsers',
	'adminUsers.title',
	'adminUsers.adminRequiredMessage',
	'adminUsers.zeroAccessDefault',
	'adminUsers.passwordNotRepopulated',
	'adminUsers.roleCopy.viewer',
	'adminUsers.roleCopy.editor',
	'adminUsers.roleCopy.owner',
	'adminUsers.roleBoundary',
	'adminUsers.confirmDisableCopy',
	'adminUsers.confirmResetCopy',
	'adminUsers.confirmRevokeCopy',
	'adminUsers.problem.username_invalid',
	'adminUsers.problem.username_taken',
	'adminUsers.problem.display_name_invalid',
	'adminUsers.problem.password_policy',
	'adminUsers.problem.user_not_found',
	'adminUsers.problem.user_disabled',
	'adminUsers.problem.session_changed',
	'adminUsers.problem.self_disable_forbidden',
	'adminUsers.problem.last_enabled_admin',
	'adminUsers.problem.book_not_assignable',
	'adminUsers.problem.admin_required',
	'adminUsers.problem.api_unavailable',
	'adminUsers.problem.unknown_admin_problem',
	'adminUsers.success.user_created',
	'adminUsers.success.book_access_revoked'
]) {
	assert.ok(messages.includes(`'${key}'`), `i18n catalog must include ${key}`);
}
assert.match(messages, /User and book access administration[\s\S]*Управление users и доступом к книгам/s, 'admin-users catalog must include EN/RU route title');
assert.match(messages, /New users start with zero book access by default[\s\S]*Новые users начинают с нулевым доступом/s, 'admin-users catalog must localize zero-access default');
assert.match(messages, /Viewer: read-only views only[\s\S]*Viewer: только read-only views/s, 'admin-users catalog must localize viewer role truthfully');
assert.match(messages, /owner\/editor labels do not enable GnuCash writes or global admin[\s\S]*owner\/editor labels не включают GnuCash writes или global admin/s, 'role boundary copy must avoid implying writes/global admin');

const allowedAdminCodes = extractAllowedAdminCodes(apiServer);
for (const code of [
	'username_invalid',
	'username_taken',
	'display_name_invalid',
	'password_policy',
	'user_not_found',
	'user_disabled',
	'session_changed',
	'self_disable_forbidden',
	'last_enabled_admin',
	'book_not_assignable',
	'admin_required',
	'api_unavailable',
	'unknown_admin_problem'
]) {
	assert.ok(allowedAdminCodes.has(code), `admin problem allowlist must include ${code}`);
}
for (const [status, payload, expected] of [
	[401, {}, 'session_changed'],
	[403, {}, 'admin_required'],
	[404, {}, 'user_not_found'],
	[409, {}, 'username_taken'],
	[422, {}, 'display_name_invalid'],
	[409, { safe_code: 'username_taken', detail: 'duplicate username value' }, 'username_taken'],
	[422, { detail: { safe_code: 'password_policy', raw_message: 'too short' } }, 'password_policy'],
	[500, { safe_code: 'password_hash', detail: 'raw backend failure' }, 'unknown_admin_problem'],
	[418, { detail: { code: 'canonical_path', uri_or_path: '/secret/book.gnucash' } }, 'unknown_admin_problem']
]) {
	const fallback = fallbackAdminProblemCodeForTest(status);
	assert.equal(fixedAdminProblemCodeForTest(payload, fallback, allowedAdminCodes), expected, `mocked admin API status ${status} must map to ${expected}`);
}

for (const [name, source, endpoint, method, expectedBody] of [
	['create', newServer, "'/admin/users'", "'POST'", ['username:', 'display_name:', 'password: initialPassword', 'is_admin: formState.isAdmin']],
	['rename', detailServer, '`/admin/users/${userId}`', "'PATCH'", ['display_name: displayName']],
	['enable', detailServer, '`/admin/users/${userId}/enable`', "'POST'", []],
	['disable', detailServer, '`/admin/users/${userId}/disable`', "'POST'", []],
	['reset', detailServer, '`/admin/users/${userId}/password-reset`', "'POST'", ['new_password: newPassword']],
	['grant', detailServer, '`/admin/users/${userId}/book-access/${bookId}`', "'PUT'", ['role']],
	['revoke', detailServer, '`/admin/users/${userId}/book-access/${bookId}`', "'DELETE'", []]
]) {
	assert.ok(source.includes(endpoint), `mocked ${name} action contract must use ${endpoint}`);
	assert.ok(source.includes(method), `mocked ${name} action contract must use ${method}`);
	for (const bodyField of expectedBody) assert.ok(source.includes(bodyField), `mocked ${name} action body must include ${bodyField}`);
}
assert.match(detailPage, /data\.bookOptions\.length[\s\S]*option value=\{book\.id\}[\s\S]*data\.user\.assignments\.length/s, 'mocked access matrix coverage must include multiple book options and assignments');

const adminRouteFiles = walk(pathOf('src', 'routes', 'admin', 'users')).filter((file) => /\.(svelte|ts)$/.test(file));
for (const file of adminRouteFiles) {
	const source = readFileSync(file, 'utf8');
	const rel = relative(repoRoot, file);
	assert.doesNotMatch(source, /localStorage|sessionStorage|showOpenFilePicker|webkitdirectory|FileReader|DataTransfer|type="file"/i, `${rel} must not use browser storage or file APIs`);
	assert.doesNotMatch(source, /overflow-x-auto|min-w-full/, `${rel} must not force mobile horizontal scrolling`);
	if (file.endsWith('.svelte')) assert.match(source, /min-w-0|max-w-/, `${rel} must include bounded mobile layout classes`);
	assert.doesNotMatch(source, /password_hash|auth_version|raw audit|raw request|uri_or_path|canonical_path|\/home\/|Syncthing|only-copy|private sentinel/i, `${rel} must not render secret/path/private sentinels`);
}

for (const source of [listPage, newPage, detailPage]) {
	assert.doesNotMatch(source, /fetch\(|method="GET" action="\/admin\/users\/.*password|formaction="\?\/create"|localStorage|sessionStorage/i, 'admin UI must remain SSR form-first/minimal client state');
}

console.log('admin users static checks passed');
