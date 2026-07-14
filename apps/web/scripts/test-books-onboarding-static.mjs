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
		if (statSync(full).isDirectory()) {
			walk(full, files);
		} else {
			files.push(full);
		}
	}
	return files;
}

const packageJson = JSON.parse(read('package.json'));
assert.equal(packageJson.scripts?.['test:books-onboarding'], 'node scripts/test-books-onboarding-static.mjs', 'package.json must expose npm run test:books-onboarding');

assert.ok(existsSync(pathOf('src', 'routes', 'books', '+page.server.ts')), '/books server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'books', '+page.svelte')), '/books page route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'books', 'new', '+page.server.ts')), '/books/new server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'books', 'new', '+page.svelte')), '/books/new page route must exist');

const apiTypes = read('src', 'lib', 'api', 'types.ts');
const apiServer = read('src', 'lib', 'api', 'server.ts');
const booksServer = read('src', 'routes', 'books', '+page.server.ts');
const booksPage = read('src', 'routes', 'books', '+page.svelte');
const newServer = read('src', 'routes', 'books', 'new', '+page.server.ts');
const newPage = read('src', 'routes', 'books', 'new', '+page.svelte');
const selectRoute = read('src', 'routes', 'books', '[bookId]', 'select', '+server.ts');
const i18nMessages = read('src', 'lib', 'i18n', 'messages.ts');

assert.match(apiTypes, /export type CurrentUser[\s\S]*is_admin:\s*boolean/s, 'API types must model authenticated admin authority from /auth/me.is_admin');
assert.match(apiTypes, /export type BookProblemCode[\s\S]*invalid_path[\s\S]*outside_allowed_roots[\s\S]*duplicate_canonical_path[\s\S]*unknown_book_problem/s, 'BookProblemCode must use the fixed backend safe-code union with a generic fallback');
const problemCodeBlock = apiTypes.slice(apiTypes.indexOf('export type BookProblemCode ='), apiTypes.indexOf('export type BookProblemDTO ='));
assert.doesNotMatch(problemCodeBlock, /'ready'|'source_ready'|'accounts_ready'/, 'BookProblemCode must not include readiness/status codes');
assert.match(apiTypes, /export type BookReadinessCode[\s\S]*'ready'[\s\S]*'source_ready'[\s\S]*'accounts_ready'[\s\S]*'reports_ready'/s, 'readiness codes must be modeled separately from BookProblemCode');
const sectionStatusBlock = apiTypes.slice(apiTypes.indexOf('export type BookSectionStatus = {'), apiTypes.indexOf('export type BookCapabilityFlags = {'));
assert.match(sectionStatusBlock, /status:[\s\S]*safe_code:\s*BookSectionStatusCode[\s\S]*message:\s*string \| null[\s\S]*retryable:\s*boolean/s, 'section statuses must model exact backend status/safe_code/message/retryable fields');
assert.doesNotMatch(sectionStatusBlock, /\bsection\b|\bcode\??:|safe_message/, 'section statuses must not require a frontend section field, legacy code field, or safe_message DTO');
assert.match(apiTypes, /export type BookPreflightRequest[\s\S]*base_currency:\s*string[\s\S]*make_default:\s*boolean/s, 'preflight request must require normalized uppercase base_currency');
assert.match(apiTypes, /export type BookCapabilityFlags[\s\S]*can_register_metadata[\s\S]*can_open_accounts[\s\S]*can_open_transactions[\s\S]*can_open_reports[\s\S]*can_upload:\s*false[\s\S]*can_edit:\s*false[\s\S]*can_delete:\s*false/s, 'capability flags must use exact B1 can_* fields and false mutation flags');
const preflightResponseBlock = apiTypes.slice(apiTypes.indexOf('export type BookPreflightResponse = {'), apiTypes.indexOf('export type Book = {'));
for (const requiredPreflightField of [
	"status: 'ready' | 'rejected'",
	'preflight_token: string',
	'registration_status: BookSectionStatus',
	'source_status: BookSectionStatus',
	'open_status: BookSectionStatus',
	'accounts: BookSectionStatus',
	'transactions: BookSectionStatus',
	'reports: BookSectionStatus',
	'capabilities: BookCapabilityFlags',
	'safe_code: BookPreflightSafeCode',
	'message?: string | null',
	'read_counters?: Record<string, number>'
]) {
	assert.ok(preflightResponseBlock.includes(requiredPreflightField), `preflight response must include ${requiredPreflightField}`);
}
assert.doesNotMatch(preflightResponseBlock, /\bstate\b|section_statuses/, 'preflight response must use exact B1 status fields, not legacy state/section_statuses');
assert.doesNotMatch(preflightResponseBlock, /safe_code: BookProblemCode|safe_message/, 'preflight safe_code may be readiness or problem code and must not pass backend safe_message through');
const bookHealthBlock = apiTypes.slice(apiTypes.indexOf('export type BookHealth = {'), apiTypes.indexOf('export type BookPreflightRequest = {'));
for (const requiredHealthField of [
	'status: string',
	'safe_code: string',
	'checked_at: string | null',
	'last_successful_at: string | null',
	'source_status: string',
	'open_status: string',
	'accounts_status: string',
	'transactions_status: string',
	'reports_status: string'
]) {
	assert.ok(bookHealthBlock.includes(requiredHealthField), `BookHealth must include cached public health field ${requiredHealthField}`);
}
assert.doesNotMatch(bookHealthBlock, /uri_or_path|registration_status|	source:\s*string|	open:\s*string|	accounts:\s*string|	transactions:\s*string|	reports:\s*string|BookSectionStatus/, 'BookHealth must match the cached public shape without raw paths, old short field names, or nested preflight DTOs');
assert.match(apiTypes, /export type Book[\s\S]*is_enabled\?: boolean[\s\S]*created_at\?: string[\s\S]*updated_at\?: string[\s\S]*health\?: BookHealth[\s\S]*capabilities\?: BookCapabilityFlags[\s\S]*management_actions/s, 'Book DTO must include enabled/timestamps/health/capabilities/management_actions fields');
const publicBookBlock = apiTypes.slice(apiTypes.indexOf('export type Book = {'), apiTypes.indexOf('export type Account = {'));
assert.doesNotMatch(publicBookBlock, /uri_or_path:\s*string/, 'public Book DTO must not expose raw uri_or_path');

assert.match(apiServer, /getCurrentUser\(fetchFn: typeof fetch, token: string\)[\s\S]*apiFetch<CurrentUser>\(fetchFn, '\/auth\/me', token\)/s, 'frontend must derive admin authority from authenticated API user data');
assert.match(apiServer, /isCurrentUserAdmin\(user: CurrentUser \| null\)[\s\S]*user\?\.is_admin === true/s, 'admin derivation must fail closed unless API explicitly says is_admin=true');
const adminHelperBlock = apiServer.slice(apiServer.indexOf('export function isCurrentUserAdmin'), apiServer.indexOf('function getSelectedBookCookieState'));
assert.doesNotMatch(adminHelperBlock, /username|display_name|books|management_actions/, 'admin derivation must not infer authority from username, display name, book contents, or management actions');

assert.match(booksServer, /getCurrentUser\(fetch, token\)[\s\S]*isCurrentUserAdmin\(currentUser\)/s, '/books load must derive admin state from authenticated server data');
assert.doesNotMatch(booksServer, /registerBook\s*:/, '/books must not keep the old one-step registration action');
assert.doesNotMatch(booksServer, /\/books\/preflight|method:\s*'POST'[\s\S]*body:\s*JSON\.stringify\(\{[\s\S]*uri_or_path/s, '/books list route must not run preflight or registration');

assert.match(booksPage, /data\.isAdmin[\s\S]*books\.firstRunAdminTitle[\s\S]*href="\/books\/new"/s, 'admin/no-books state must explain first run and link to Add book');
assert.match(booksPage, /!data\.isAdmin[\s\S]*books\.firstRunUserTitle[\s\S]*books\.firstRunUserMessage/s, 'normal-user/no-books state must be distinct and ask an administrator to register/assign a book');
const adminNoBooksBlock = booksPage.slice(booksPage.indexOf('{:else if data.isAdmin}'), booksPage.indexOf('{:else if !data.isAdmin}'));
const normalNoBooksBlock = booksPage.slice(booksPage.indexOf('{:else if !data.isAdmin}'), booksPage.indexOf('{/if}', booksPage.indexOf('{:else if !data.isAdmin}')));
assert.match(adminNoBooksBlock, /books\.firstRunAdminTitle[\s\S]*href="\/books\/new"[\s\S]*books\.addBookAction/s, 'is_admin=true empty-state fixture must expose the Add book admin CTA');
assert.match(normalNoBooksBlock, /books\.firstRunUserTitle[\s\S]*books\.firstRunUserMessage/s, 'is_admin=false or missing empty-state fixture must show normal-user no-books copy');
assert.doesNotMatch(normalNoBooksBlock, /href="\/books\/new"|books\.addBookAction/, 'normal-user no-books fixture must not expose Add book');
assert.doesNotMatch(booksPage, /href="\/login"|Sign in again|name="mounted_path"|GITHUB|GNUCASH_DEFAULT_BOOK_PATH/, '/books empty state must not dead-end into login or expose path/environment guidance to normal users');
assert.match(booksPage, /capabilityLinks\(book\)[\s\S]*\/books\/\$\{book\.id\}\/select\?next=\$\{link\.next\}/s, 'book cards must build open links through the capability allowlist helper');
assert.match(booksPage, /can_open_accounts[\s\S]*next: '\/accounts'[\s\S]*can_open_transactions[\s\S]*next: '\/transactions'[\s\S]*can_open_reports[\s\S]*next: '\/reports'/s, 'book cards must include Accounts, Transactions, and Reports safe links gated by exact capability names');
assert.doesNotMatch(booksPage, /next: '\/scheduled'|next: '\/dashboard'|viewScheduled|dashboardSummary/, 'book cards must not expose non-contract scheduled/dashboard open links');
assert.match(booksPage, /isBookEnabled\(book\)[\s\S]*canOpenCapability\(book, link\.capability\)/s, 'disabled/unavailable cards must not expose open links');
for (const requiredBookField of ['book.health?.status', 'book.health?.checked_at', 'book.is_enabled']) {
	assert.ok(booksPage.includes(requiredBookField), `book cards must show typed health/check/enabled field: ${requiredBookField}`);
}
assert.match(booksPage, /books\.statusDetailsTitle[\s\S]*books\.renameFuture[\s\S]*books\.disableFuture[\s\S]*books\.recheckFuture/s, 'book cards must include an accessible detail pattern ready for rename/disable/recheck wiring');
assert.match(booksPage, /name="confirm_metadata_only"[\s\S]*books\.removeMetadataConfirm[\s\S]*books\.removeRegistryAction/s, 'unregister UI must require explicit metadata-only/no-source-delete confirmation');
assert.doesNotMatch(booksPage, /book\.storage_diagnostics\.safe_next_actions|book\.operator_guidance\.message|uri_or_path|mounted_path|preflight_token/, 'book cards/normal pages must not render backend guidance passthrough, raw path, or preflight token');
assert.doesNotMatch(booksPage, /overflow-x-auto|min-w-full/, '/books page must not introduce fixed mobile horizontal overflow hazards');

assert.match(newServer, /toPreflightRequest[\s\S]*storage_type:\s*'sqlite'[\s\S]*uri_or_path/s, '/books/new must normalize the typed sqlite preflight request');
assert.match(newServer, /preflight:\s*async[\s\S]*\/books\/preflight[\s\S]*method:\s*'POST'[\s\S]*JSON\.stringify\(toPreflightRequest\(formState\)\)/s, '/books/new preflight action must POST only the typed preflight request');
assert.match(newServer, /confirm:\s*async[\s\S]*preflight_token[\s\S]*\/books[\s\S]*method:\s*'POST'/s, '/books/new confirm action must POST /books with the opaque preflight token in a separate action');
assert.ok(newServer.indexOf("preflight: async") < newServer.indexOf("confirm: async"), 'preflight and confirm actions must be distinct and ordered');
const preflightAction = newServer.slice(newServer.indexOf('preflight: async'), newServer.indexOf('confirm: async'));
assert.doesNotMatch(preflightAction, /`\$\{apiBase\}\/books`|path:\s*'\/books'|registerBook|confirm/s, 'preflight action must not call POST /books or silently register');
assert.match(newServer, /bookProblemCodeFromPayload[\s\S]*allowedBookProblemCodes[\s\S]*unknown_book_problem/s, 'book onboarding errors must be reduced to fixed safe codes with a generic fallback');
assert.doesNotMatch(newServer, /return .*detail|message:\s*redactedApiError|safe_summary|safe_next_actions|exception|traceback/i, 'server actions must not pass arbitrary backend detail into rendered errors');
assert.doesNotMatch(newServer, /\/accounts|\/transactions|\/splits|\/commodities|piecash|fs\.|glob|readdir|FileSystem/s, '/books/new server actions must stay registry-metadata-only and not inspect accounting data or client files');

assert.match(newPage, /method="POST" action="\?\/preflight"[\s\S]*name="name"[\s\S]*name="mounted_path"[\s\S]*name="base_currency"[\s\S]*name="make_default"/s, '/books/new must render the Step 2 server form fields');
assert.match(newPage, /canConfirmRegistration\(preflight: BookPreflightResponse\)[\s\S]*preflight\.status === 'ready'[\s\S]*preflight\.capabilities\.can_register_metadata === true[\s\S]*preflight\.registration_status\.status === 'available'[\s\S]*Boolean\(preflight\.preflight_token\)[\s\S]*!hasDuplicateRegistrationTarget\(preflight\)/s, '/books/new must gate Confirm registration on ready + capability + available registration + token + non-duplicate target');
assert.match(newPage, /preflight && canConfirmRegistration\(preflight\)[\s\S]*method="POST" action="\?\/confirm"[\s\S]*name="mounted_path" value=\{previous\.mountedPath\}[\s\S]*name="preflight_token"/s, '/books/new must render a separate explicit confirm form only after a confirmable preflight');
assert.match(newPage, /books\.newStep1Title[\s\S]*books\.newStep2Title[\s\S]*books\.newStep3Title[\s\S]*books\.newStep4Title/s, '/books/new must present the four explicit onboarding steps');
assert.match(newPage, /source_status[\s\S]*open_status[\s\S]*accounts[\s\S]*transactions[\s\S]*reports/s, 'preflight checklist must render source/open/Accounts/Transactions/Reports typed status objects');
assert.match(newPage, /safeCode = \$derived\(form\?\.preflightErrorCode \?\? form\?\.registrationErrorCode \?\? null\)/s, 'successful ready preflight safe_code must not be promoted into the problem alert state');
assert.doesNotMatch(newPage, /safeCode = \$derived\([^\n]*preflight\?\.safe_code/s, 'successful ready safe_code must not render a problem alert');
assert.match(newPage, /problemCodeFromSafeCode[\s\S]*preflight\.status !== 'ready'[\s\S]*fixedSafeMessage/s, 'rejected preflight results must still render fixed local problem copy');
assert.match(newPage, /registrationStatusMessage\(preflight\)[\s\S]*sectionStatusMessage\(itemDefinition\.section, item\.status\)/s, 'preflight checklist must render local EN/RU status copy mapped by section/status');
assert.match(newPage, /duplicateRegistrationCodes[\s\S]*already_registered[\s\S]*duplicate_canonical_path[\s\S]*hasDuplicateRegistrationTarget/s, 'duplicate canonical targets must be detected before rendering Confirm registration');
assert.match(newPage, /statusLabel\(item\.status, item\.safe_code\)/s, 'preflight UI may render section safe_code only as a fixed local status label');
assert.doesNotMatch(newPage, /item\.message|registration_status\.message|source_status\.message|safe_message|problemCodeFromSafeCode\(item\.safe_code\)/, 'preflight UI must not render arbitrary backend message/safe_message or treat section safe_code as a problem code');
assert.match(newPage, /checked_at[\s\S]*books\.preflightTokenOpaque[\s\S]*preflight_token/s, 'preflight UI must show checked time and describe token as opaque without placing it in URL');
assert.doesNotMatch(newPage, /type="file"|webkitdirectory|showOpenFilePicker|FileSystem|DataTransfer|localStorage|sessionStorage|fetch\(/i, '/books/new must not expose upload/client-filesystem/browser-persistence UI');
assert.doesNotMatch(newPage, /overflow-x-auto|min-w-full/, '/books/new must not introduce fixed mobile horizontal overflow hazards');

assert.match(selectRoute, /SAFE_NEXT_PATHS[\s\S]*'\/accounts'[\s\S]*'\/transactions'[\s\S]*'\/reports'/s, 'book safe-link route must allow Accounts/Transactions/Reports');
assert.match(selectRoute, /selectedBook\.can_open_read_only_views[\s\S]*\/books\?book_context=unavailable_selected_book/s, 'book safe-link route must withhold unavailable books before redirecting');

for (const key of [
	'books.firstRunAdminTitle',
	'books.firstRunAdminMessage',
	'books.firstRunUserTitle',
	'books.firstRunUserMessage',
	'books.addBookAction',
	'books.newTitle',
	'books.newStep1Title',
	'books.newStep2Title',
	'books.newStep3Title',
	'books.newStep4Title',
	'books.preflightSubmit',
	'books.confirmRegisterSubmit',
	'books.preflightReady',
	'books.problem.preflight_rejected',
	'books.problem.invalid_path',
	'books.problem.unsupported_source',
	'books.problem.outside_allowed_roots',
	'books.problem.symlink_forbidden',
	'books.problem.missing_file',
	'books.problem.not_regular_file',
	'books.problem.permission_denied',
	'books.problem.invalid_gnucash_schema',
	'books.problem.source_changed',
	'books.problem.open_failed',
	'books.problem.duplicate_canonical_path',
	'books.problem.unknown_book_problem',
	'books.removeMetadataConfirm',
	'books.reportsLink',
	'books.statusDetailsTitle',
	'books.statusCode.source_ready',
	'books.statusCode.accounts_ready',
	'books.statusCode.registration_available',
	'books.statusCode.already_registered',
	'books.registrationStatus.available',
	'books.registrationStatus.alreadyRegistered',
	'books.registrationStatus.unavailable',
	'books.sectionStatus.source.ready',
	'books.sectionStatus.accounts.ready',
	'books.sectionStatus.transactions.ready',
	'books.sectionStatus.reports.ready'
]) {
	assert.ok(i18nMessages.includes(`'${key}'`), `books onboarding i18n catalog must include ${key}`);
}
assert.match(i18nMessages, /Existing server-side GnuCash SQL SQLite only[\s\S]*Существующая server-side GnuCash SQL SQLite/s, 'supported-format explanation must be localized in EN/RU');
assert.match(i18nMessages, /administrator must register or assign a book[\s\S]*администратор должен зарегистрировать или назначить книгу/is, 'normal-user no-books copy must be localized and role-safe');
assert.match(i18nMessages, /The source GnuCash file is not deleted or modified[\s\S]*Файл GnuCash не удаляется и не изменяется/s, 'unregister confirmation must localize metadata-only/no-source-delete safety copy');

const booksRouteFiles = walk(pathOf('src', 'routes', 'books'));
for (const file of booksRouteFiles) {
	const source = readFileSync(file, 'utf8');
	assert.doesNotMatch(source, /localStorage|sessionStorage/, `${relative(repoRoot, file)} must not use browser storage`);
	assert.doesNotMatch(source, /showOpenFilePicker|webkitdirectory|<input[^>]+type="file"|DataTransfer|FileReader/, `${relative(repoRoot, file)} must not use browser file APIs`);
}

const allWebSources = walk(pathOf('src')).filter((file) => /\.(svelte|ts)$/.test(file));
for (const file of allWebSources) {
	const source = readFileSync(file, 'utf8');
	assert.doesNotMatch(source, /(?:localStorage|sessionStorage)\.(?:setItem|getItem)\(['"](?:access_token|auth|token)/, `${relative(repoRoot, file)} must not persist auth tokens in browser storage`);
}

console.log('books onboarding static checks passed');
