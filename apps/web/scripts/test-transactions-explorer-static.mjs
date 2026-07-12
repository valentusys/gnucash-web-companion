import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

function pathOf(...segments) {
	return join(root, ...segments);
}

function read(...segments) {
	return readFileSync(pathOf(...segments), 'utf8');
}

assert.ok(existsSync(pathOf('src', 'routes', 'transactions', '+page.server.ts')), '/transactions server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'transactions', '+page.svelte')), '/transactions page route must exist');
assert.ok(existsSync(pathOf('src', 'lib', 'transactions', 'explorer.ts')), 'canonical transactions explorer helper must exist');
assert.ok(existsSync(pathOf('src', 'lib', 'components', 'TransactionExplorerFilters.svelte')), 'explorer-specific filter form must exist');

const packageJson = JSON.parse(read('package.json'));
const explorer = read('src', 'lib', 'transactions', 'explorer.ts');
const apiTypes = read('src', 'lib', 'api', 'types.ts');
const server = read('src', 'routes', 'transactions', '+page.server.ts');
const page = read('src', 'routes', 'transactions', '+page.svelte');
const filters = read('src', 'lib', 'components', 'TransactionExplorerFilters.svelte');
const detailServer = read('src', 'routes', 'transactions', '[id]', '+page.server.ts');
const detailPage = read('src', 'routes', 'transactions', '[id]', '+page.svelte');
const reportsServer = read('src', 'routes', 'reports', '+page.server.ts');
const dashboardServer = read('src', 'routes', 'dashboard', '+page.server.ts');
const i18nMessages = read('src', 'lib', 'i18n', 'messages.ts');

assert.equal(packageJson.scripts?.['test:transactions-explorer'], 'node scripts/test-transactions-explorer-static.mjs', 'package.json must expose npm run test:transactions-explorer');
assert.equal(packageJson.scripts?.['test:transactions-explorer-browser'], 'npm run build && node scripts/test-transactions-explorer-browser.mjs', 'package.json must expose a build-backed transactions explorer browser smoke');

assert.match(apiTypes, /export type TransactionExplorerScan[\s\S]*candidate_rows[\s\S]*split_rows[\s\S]*query_count[\s\S]*scan_limited[\s\S]*exhausted/s, 'API types must model explorer scan diagnostics without legacy scan_limited top-level fields');
assert.match(apiTypes, /export type TransactionExplorerPage[\s\S]*items: TransactionListItem\[\][\s\S]*page_size[\s\S]*returned_count[\s\S]*has_more[\s\S]*previous_cursor[\s\S]*scan: TransactionExplorerScan[\s\S]*limitations: string\[\]/s, 'API types must model cursor-paginated explorer responses');
assert.match(apiTypes, /representative_amount\?: MoneyDTO[\s\S]*matched_amount\?: MoneyDTO \| null[\s\S]*amount_basis\?: 'selected_accounts' \| 'income' \| 'expense' \| 'representative_split' \| string/s, 'transaction list items must tolerate explorer exact amount DTOs while preserving old list rendering');

assert.match(explorer, /TRANSACTIONS_EXPLORER_DEFAULT_SORT = 'date_desc'/, 'canonical explorer default sort must be date_desc');
assert.match(explorer, /TRANSACTIONS_EXPLORER_DEFAULT_PAGE_SIZE = 50/, 'canonical explorer default page_size must be 50');
assert.match(explorer, /TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE = 100/, 'canonical explorer max page_size must match backend contract');
assert.match(explorer, /buildTransactionsExplorerSearchParams[\s\S]*date_from[\s\S]*date_to[\s\S]*account_ids[\s\S]*type[\s\S]*direction[\s\S]*min_amount[\s\S]*max_amount[\s\S]*query[\s\S]*transaction_state[\s\S]*sort[\s\S]*page_size[\s\S]*cursor/s, 'canonical URL builder must serialize query params in one stable contract order');
assert.match(explorer, /normalizeAccountIds\(input\.accountIds \?\? \[\]\)\.sort\(\)/, 'canonical URL builder must normalize and sort multi-account selections');
assert.match(explorer, /validateTransactionsExplorerUrl[\s\S]*rawParams\.has\('account_id'\)[\s\S]*Duplicate account_ids[\s\S]*value\.pageSize < 1 \|\| value\.pageSize > TRANSACTIONS_EXPLORER_MAX_PAGE_SIZE[\s\S]*daysInclusive\(value\.dateFrom, value\.dateTo\) > 366[\s\S]*amount_requires_scope[\s\S]*cursor_too_long/s, 'explorer validation must centralize legacy, account, date, Decimal, scope, page_size, and cursor guards');
assert.match(explorer, /safeTransactionsReturnTo[\s\S]*parsed\.origin !== 'http:\/\/127\.0\.0\.1'[\s\S]*parsed\.pathname !== '\/transactions'[\s\S]*return `\$\{parsed\.pathname\}\$\{parsed\.search\}`/s, 'return_to sanitizer must allow only same-origin /transactions URLs');
assert.match(explorer, /detailHrefWithReturnTo[\s\S]*encodeURIComponent\(safeReturnTo\)/s, 'detail links must URL-encode sanitized return_to');

assert.match(server, /getActiveBookContext\(fetch, cookies, token\)[\s\S]*`\$\{bookPrefix\}\/accounts\?limit=\$\{ACCOUNT_OPTION_LIMIT\}`[\s\S]*validateTransactionsExplorerUrl\(url\)[\s\S]*`\$\{bookPrefix\}\/transactions\/explorer\?\$\{explorerParams\.toString\(\)\}`/s, '/transactions SSR load must resolve active book, bounded account options, validate URL state, and call the explorer API');
assert.match(server, /hasBoundedExplorerDateRange[\s\S]*filters\.dateFrom[\s\S]*filters\.dateTo/s, '/transactions SSR load must have an explicit paired date-range gate before explorer API calls');
assert.match(server, /dateRangeRequiredStatus[\s\S]*transactions\.explorer\.dateRangeRequiredTitle[\s\S]*transactions\.explorer\.dateRangeRequiredMessage/s, 'bounded date range required state must use localized i18n copy');
assert.match(server, /if \(!hasBoundedExplorerDateRange\(filters\)\)[\s\S]*emptyExplorerPage\(filters\.sort, filters\.pageSize\)[\s\S]*dateRangeRequiredStatus\(locale\)[\s\S]*detailHrefs: \{\}[\s\S]*const explorerParams/s, 'no-date reset/default route must render a bounded date range required state before any explorer request');
assert.match(server, /legacyCanonicalExplorerHref[\s\S]*throw redirect\(303, canonicalLegacyHref\)[\s\S]*isLegacyCompatibilityUrl[\s\S]*mode: 'legacy'/s, 'legacy URLs must either redirect to canonical explorer URLs or remain bounded compatibility mode for offset/one-sided date semantics');
assert.match(server, /hasAdvancedFieldsWithLegacyOffset[\s\S]*'sort'[\s\S]*legacyOffsetConflict/s, 'legacy offset compatibility must reject advanced sort/page/cursor/account modes instead of silently dropping them');
assert.match(server, /params\.getAll\('account_id'\)\.length > 1 \|\| \(params\.has\('account_id'\) && params\.has\('account_ids'\)\)/, 'legacy account_id normalization must not silently discard duplicate or mixed account selector parameters');
assert.match(server, /normalizeExplorerItem[\s\S]*representative_amount[\s\S]*normalizeExplorerPage[\s\S]*body\.items\.map\(normalizeExplorerItem\)/s, 'server must normalize explorer item DTO variants before rendering');
assert.match(server, /normalizeExplorerPage[\s\S]*scan: \{[\s\S]*candidate_rows[\s\S]*scan_limited[\s\S]*exhausted/s, 'server must normalize nested scan diagnostics for SSR rendering');
assert.match(server, /currentTransactionsReturnTo[\s\S]*safeTransactionsReturnTo\(candidate\)[\s\S]*detailHrefs\(txs\.items, returnTo\)/s, 'server must propagate canonical explorer URLs into transaction detail return_to links');
assert.match(server, /legacyCsvParamsFromExplorer[\s\S]*filters\.cursor \|\| filters\.type \|\| filters\.direction \|\| filters\.query[\s\S]*explorerCsvState/s, 'CSV export must stay disabled when explorer filters cannot exactly map to legacy CSV semantics');
assert.doesNotMatch(server, /parseFloat\(|Number\([^)]*(?:amount|minAmount|maxAmount|total|balance)/, 'transactions server must not use float/Number conversion on money strings');

assert.match(filters, /method="GET"[\s\S]*action="\/transactions"[\s\S]*name="account_ids"[\s\S]*multiple[\s\S]*name="type"[\s\S]*name="direction"[\s\S]*name="page_size"/s, 'explorer form must submit canonical GET URL fields, including multi-account and cursor page_size state');
assert.match(filters, /disabled=\{hasTypeMode\}[\s\S]*disabled=\{hasAccountMode\}[\s\S]*disabled=\{!hasAccountMode\}/s, 'explorer form must prevent incompatible account/type/direction combinations in the browser');
assert.doesNotMatch(filters, /localStorage|sessionStorage|method="POST"/s, 'explorer form must remain SSR/URL-driven with no browser storage or write submission');

assert.match(page, /TransactionExplorerFilters[\s\S]*filters=\{data\.filters\}[\s\S]*resetHref=\{data\.resetHref\}[\s\S]*pageSizeOptions=\{data\.pageSizeOptions\}/s, '/transactions page must render the shared validated SSR explorer state');
assert.match(page, /detailHref = \(id: string\) => data\.detailHrefs\?\.\[id\][\s\S]*TransactionTable[\s\S]*detailHref=\{detailHref\}[\s\S]*TransactionCard[\s\S]*detailHref=\{detailHref\}/s, 'desktop and mobile transaction rows must share detail return_to links');
assert.match(page, /data\.pagination\?\.previousHref[\s\S]*data\.pagination\?\.nextHref[\s\S]*data\.pagination\?\.continueHref/s, 'explorer page must expose cursor previous/next/continue links from server data');
assert.doesNotMatch(page, /localStorage|sessionStorage|fetch\(|formaction="\?\/create"|method="POST"/s, '/transactions explorer page must remain SSR-first and read-only');

assert.match(detailServer, /safeTransactionsReturnTo\(url\.searchParams\.get\('return_to'\)\)/, 'transaction detail load must sanitize return_to from the query string');
assert.match(detailServer, /const returnTo = safeTransactionsReturnTo\(String\(formData\.get\('return_to'\) \?\? ''\)\)[\s\S]*throw redirect\(303, returnTo\)/s, 'post-MVP delete redirect must preserve the sanitized explorer return URL');
assert.match(detailPage, /href=\{data\.returnTo \?\? '\/transactions'\}[\s\S]*name="return_to" value=\{data\.returnTo \?\? '\/transactions'\}/s, 'transaction detail UI must use the same sanitized return URL for back and controlled-write fallback paths');

for (const [label, source] of [['reports', reportsServer], ['dashboard', dashboardServer]]) {
	assert.match(source, /import \{ buildTransactionsExplorerUrl \} from '\$lib\/transactions\/explorer'/, `${label} must use the shared canonical explorer URL builder`);
	assert.match(source, /transactionFilterHref[\s\S]*buildTransactionsExplorerUrl\([\s\S]*dateFrom: params\.date_from[\s\S]*dateTo: params\.date_to[\s\S]*accountIds[\s\S]*type: params\.type === 'income' \|\| params\.type === 'expense' \? params\.type : ''[\s\S]*pageSize: 50/s, `${label} drilldowns must map only exact explorer-supported filters`);
	assert.doesNotMatch(source, /new URLSearchParams\(\{ limit: '50', offset: '0' \}\)/, `${label} drilldowns must not mint legacy offset URLs`);
}
assert.match(dashboardServer, /incomeThisMonth: transactionFilterHref\(\{ date_from: dateFrom, date_to: dateTo, type: 'income' \}\)[\s\S]*expensesThisMonth: transactionFilterHref\(\{ date_from: dateFrom, date_to: dateTo, type: 'expense' \}\)/s, 'dashboard income/expense cards must map exactly to explorer type filters');

for (const key of [
	'transactions.explorer.formHelp',
	'transactions.explorer.dateRangeRequiredTitle',
	'transactions.explorer.dateRangeRequiredMessage',
	'transactions.explorer.scanLimitedTitle',
	'transactions.explorer.staleCursorTitle',
	'transactions.explorer.legacyOffsetConflict',
	'transactions.export.explorerDisabled',
	'transactions.export.explorerHonesty'
]) {
	assert.ok(i18nMessages.includes(`'${key}'`), `i18n messages must include ${key}`);
}

console.log('transactions explorer static checks passed');
