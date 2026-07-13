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

assert.ok(existsSync(pathOf('src', 'routes', 'accounts', '+page.server.ts')), '/accounts server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'accounts', '+page.svelte')), '/accounts page route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'accounts', '[id]', '+page.server.ts')), '/accounts/[id] server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'accounts', '[id]', '+page.svelte')), '/accounts/[id] page route must exist');
assert.ok(existsSync(pathOf('src', 'lib', 'accounts', 'explorer.ts')), 'canonical account explorer helper must exist');
assert.ok(existsSync(pathOf('scripts', 'test-accounts-explorer-browser.mjs')), 'accounts explorer browser smoke must exist');

const packageJson = JSON.parse(read('package.json'));
const browserScript = read('scripts', 'test-accounts-explorer-browser.mjs');
const helper = read('src', 'lib', 'accounts', 'explorer.ts');
const explorerServer = read('src', 'routes', 'accounts', '+page.server.ts');
const explorerPage = read('src', 'routes', 'accounts', '+page.svelte');
const detailServer = read('src', 'routes', 'accounts', '[id]', '+page.server.ts');
const detailPage = read('src', 'routes', 'accounts', '[id]', '+page.svelte');
const apiTypes = read('src', 'lib', 'api', 'types.ts');
const txHelper = read('src', 'lib', 'transactions', 'explorer.ts');
const i18nMessages = read('src', 'lib', 'i18n', 'messages.ts');
const ciWorkflow = read('..', '..', '.github', 'workflows', 'ci.yml');

assert.equal(packageJson.scripts?.['test:accounts-explorer'], 'node scripts/test-accounts-explorer-static.mjs', 'package.json must expose npm run test:accounts-explorer');
assert.equal(packageJson.scripts?.['test:accounts-explorer-browser'], 'npm run build && node scripts/test-accounts-explorer-browser.mjs', 'package.json must expose npm run test:accounts-explorer-browser');
assert.match(ciWorkflow, /npm run test:accounts-explorer\s+npm run test:transaction-entry-create-disposable-browser\s+npm run test:accounts-explorer-browser/s, 'CI must run account static and browser gates without weakening existing transaction/report browser gates');

assert.match(browserScript, /Account explorer loaded[\s\S]*exactly one bounded account explorer request[\s\S]*cursor[\s\S]*offset/s, 'browser smoke must cover canonical /accounts default request bounds');
assert.match(browserScript, /Invalid account explorer filters[\s\S]*zero explorer endpoint requests/s, 'browser smoke must cover invalid account explorer URL without API calls');
assert.match(browserScript, /Overview only[\s\S]*zero activity requests[\s\S]*Invalid account detail URL[\s\S]*zero activity endpoint requests/s, 'browser smoke must cover overview-only and invalid account detail request counters');
assert.match(browserScript, /account_ids=\$\{checkingAccountId\}[\s\S]*page_size[\s\S]*50[\s\S]*cursor[\s\S]*must not include cursor/s, 'browser smoke must cover exact account-to-transaction explorer link');
assert.match(browserScript, /unavailable_no_fx_scope[\s\S]*must not expose exact transaction explorer link/s, 'browser smoke must cover non-base/non-currency no-FX drilldown state');
assert.match(browserScript, /api_forbidden=\$\{api\.forbiddenRequests\.length\}[\s\S]*browser_forbidden=\$\{forbiddenBrowserMutationRequests\(browserRequests\)\.length\}[\s\S]*runtime_exceptions=\$\{runtimeExceptions\.length\}[\s\S]*console_errors=\$\{consoleErrors\.length\}/s, 'browser smoke must report console/network mutation guards');
assert.doesNotMatch(browserScript, /Syncthing|\.gnucash\.sqlite|localStorage\.setItem|sessionStorage\.setItem|method:\s*'POST'|method:\s*'PATCH'|method:\s*'DELETE'/s, 'accounts browser smoke must stay synthetic/read-only and avoid private books or write endpoints');

assert.match(apiTypes, /export type AccountExplorerResponse[\s\S]*root_ids: string\[\][\s\S]*nodes: AccountExplorerNode\[\][\s\S]*returned_count[\s\S]*scan: AccountExplorerScan[\s\S]*includes_currency_conversion: boolean[\s\S]*limitations: string\[\]/s, 'API types must model bounded account explorer response');
assert.match(apiTypes, /export type AccountOverview[\s\S]*breadcrumbs[\s\S]*children_returned[\s\S]*children_truncated[\s\S]*balance_basis[\s\S]*includes_currency_conversion/s, 'API types must model account overview response');
assert.match(apiTypes, /export type AccountActivity[\s\S]*change: AccountCommodityAmount \| null[\s\S]*recent_transactions: AccountActivityRecentTransaction\[\][\s\S]*transaction_explorer_compatible[\s\S]*partial_failure/s, 'API types must model account activity response');

assert.match(helper, /ACCOUNT_EXPLORER_DEFAULT_MODE = 'tree'/, 'canonical /accounts default mode must be tree');
assert.match(helper, /ACCOUNT_EXPLORER_DEFAULT_HIDDEN = 'exclude'/, 'canonical /accounts default hidden mode must be exclude');
assert.match(helper, /ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER = 'include'/, 'canonical /accounts default placeholder mode must be include');
assert.match(helper, /buildAccountExplorerSearchParams[\s\S]*if \(mode === 'flat'\) params\.append\('mode'[\s\S]*if \(query\) params\.append\('query'[\s\S]*for \(const type of types\) params\.append\('type'[\s\S]*if \(hidden !== ACCOUNT_EXPLORER_DEFAULT_HIDDEN\)[\s\S]*if \(placeholder !== ACCOUNT_EXPLORER_DEFAULT_PLACEHOLDER\)/s, '/accounts URL builder must serialize non-default params in stable mode/query/type/hidden/placeholder order');
assert.match(helper, /return query \? `\/accounts\?\$\{query\}` : '\/accounts'/, 'default account explorer URL must be exactly /accounts');
assert.match(helper, /validateAccountExplorerUrl[\s\S]*unknownKeys[\s\S]*duplicate_type[\s\S]*too_many_types[\s\S]*invalid_hidden[\s\S]*invalid_placeholder/s, 'account explorer validation must reject unknown/cursor/offset-style params and invalid repeated filters before API calls');
assert.match(helper, /safeAccountExplorerReturnTo[\s\S]*value\.length > 2048[\s\S]*!value\.startsWith\('\/'\)[\s\S]*parsed\.pathname !== '\/accounts'[\s\S]*validateAccountExplorerUrl\(parsed\)[\s\S]*validation\.canonicalHref/s, 'account detail return_to must allow only canonical relative /accounts explorer URLs');
assert.match(helper, /safeAccountDetailReturnTo[\s\S]*\/\^\\\/accounts\\\/\(\[0-9a-f\]\{32\}\)\$\/[\s\S]*validateAccountDetailUrl\(parsed, match\[1\]\)/s, 'transaction detail return_to must allow only lowercase /accounts/{guid} detail URLs');
assert.match(helper, /buildAccountDetailSearchParams[\s\S]*date_from[\s\S]*date_to[\s\S]*limit !== ACCOUNT_DETAIL_DEFAULT_ACTIVITY_LIMIT[\s\S]*return_to/s, 'account detail URL builder must serialize paired dates, non-default limit, then safe return_to');
assert.match(helper, /validateAccountDetailUrl[\s\S]*date_pair_required[\s\S]*invalid_date_range[\s\S]*ACCOUNT_ACTIVITY_MAX_DAYS[\s\S]*invalid_limit[\s\S]*invalid_return_to/s, 'account detail validation must guard paired dates, 366-day bound, limit, and return_to');
assert.match(helper, /buildAccountTransactionExplorerUrl[\s\S]*date_from[\s\S]*date_to[\s\S]*account_ids[\s\S]*sort', 'date_desc'[\s\S]*page_size', '50'/s, 'compatible account drilldown must be exact /transactions explorer URL without cursor');
assert.match(helper, /buildBaseReportUrl[\s\S]*preset', 'custom'[\s\S]*comparison_mode', 'previous_equivalent'[\s\S]*comparison_date_from[\s\S]*comparison_date_to/s, 'account activity report link must be exact base-currency comparison report URL');

assert.match(explorerServer, /validateAccountExplorerUrl\(url\)[\s\S]*if \(!validation\.ok\)[\s\S]*accounts: emptyExplorerResponse[\s\S]*const explorerParams/s, '/accounts load must validate first and make zero explorer API calls for invalid state');
assert.match(explorerServer, /throw redirect\(303, validation\.canonicalHref\)/, '/accounts load must redirect valid non-canonical URLs to canonical order/default omission');
assert.match(explorerServer, /`\$\{bookPrefix\}\/accounts\/explorer\$\{query \? `\?\$\{query\}` : ''\}`/, '/accounts load must call only the bounded book-aware account explorer endpoint');
assert.doesNotMatch(explorerServer, /\/accounts\/tree|AccountTreeNode|localStorage|sessionStorage|\/accounts\?limit|\/accounts\$\{/, '/accounts load must not use legacy account tree/list API or browser storage');

assert.match(explorerPage, /<form[\s\S]*method="GET"[\s\S]*action="\/accounts"[\s\S]*name="mode"[\s\S]*name="query"[\s\S]*name="type"[\s\S]*name="hidden"[\s\S]*name="placeholder"/s, '/accounts page must submit canonical URL-backed controls');
assert.match(explorerPage, /href=\{nodeHref\(node\)\}/, '/accounts page rows must link to account detail URLs generated by the SSR loader');
assert.match(explorerPage, /#snippet renderTreeNode[\s\S]*<li[\s\S]*<details[\s\S]*<summary[\s\S]*<ul[\s\S]*renderTreeNode\(child\)/s, '/accounts page must render semantic nested lists for tree mode');
assert.match(explorerPage, /directBalance[\s\S]*recursiveBuckets[\s\S]*mixedCommodityWarning/s, '/accounts page must distinguish direct balance and recursive native-commodity buckets/no-FX warning');
assert.match(explorerPage, /aria-live=\{data\.status\.role === 'alert' \? 'assertive' : 'polite'\}/, '/accounts page must expose localized status via aria-live');
assert.match(explorerPage, /min-h-11/, '/accounts page must keep mobile targets >=44px');
assert.match(explorerPage, /break-words[\s\S]*break-all/s, '/accounts page must wrap long paths and IDs');
assert.match(explorerPage, /Math\.min\(node\.depth, 6\)/, '/accounts page must cap visual indentation');
assert.doesNotMatch(explorerPage, /localStorage|sessionStorage|fetch\(|method="POST"|formaction|aria-role="tree"|role="tree"|role="treeitem"/s, '/accounts page must remain SSR-first/read-only and not fake an ARIA tree');

assert.match(detailServer, /const activityRequestCounters = \{ overview: 0, activity: 0 \}/, '/accounts/[id] must initialize explicit SSR request counters at zero');
assert.match(detailServer, /validateAccountDetailUrl\(url, params\.id\)[\s\S]*if \(!validation\.ok\)[\s\S]*activityRequestCounters[\s\S]*activityRequestCounters\.overview = 1/s, '/accounts/[id] load must validate account detail URL before overview/activity calls');
assert.match(detailServer, /activityRequestCounters\.overview = 1[\s\S]*if \(!hasAccountActivityDateRange\(filters\)\)[\s\S]*activity: null[\s\S]*activityRequestCounters,[\s\S]*const apiParams = activityParams/s, '/accounts/[id] no-date state must load overview only and return before activity params/call');
assert.match(detailServer, /const activityEndpoint = `\$\{bookPrefix\}\/accounts\/\$\{encodeURIComponent\(filters\.accountId\)\}\/activity\?\$\{apiParams\.toString\(\)\}`/, '/accounts/[id] bounded activity endpoint must be book-aware and explicit');
assert.match(
	detailServer,
	/function sanitizeActivityForBrowser\(activity: AccountActivity\): AccountActivity[\s\S]*section_statuses: activity\.section_statuses\.map[\s\S]*detail: null[\s\S]*limitations: sanitizeLimitations\(activity\.limitations\)/s,
	'/accounts/[id] load must redact activity section diagnostics before returning browser-serialized page data'
);
assert.match(detailServer, /const activity = sanitizeActivityForBrowser\(activityResult\.body as AccountActivity\)/, '/accounts/[id] load must return only the sanitized AccountActivity payload');
assert.doesNotMatch(detailServer, /const activity = activityResult\.body as AccountActivity;\s*activity\.limitations = sanitizeLimitations\(activity\.limitations\);/, '/accounts/[id] load must not return the raw activity object with only limitations sanitized');
assert.match(detailServer, /transactionHrefs[\s\S]*`\/transactions\/\$\{encodeURIComponent\(tx\.id\)\}\?return_to=\$\{encodeURIComponent\(canonicalAccountDetailHref\)\}`/s, 'recent transaction rows must link to transaction detail with encoded canonical account detail return_to');
assert.match(detailServer, /transaction_explorer_compatible[\s\S]*buildAccountTransactionExplorerUrl\(filters\.accountId, filters\.dateFrom, filters\.dateTo\)[\s\S]*buildBaseReportUrl\(filters\.dateFrom, filters\.dateTo\)/s, 'account detail must build exact compatible transaction and base report links');
assert.doesNotMatch(detailServer, /PaginatedTransactions|\/accounts\/\$\{[^}]+\}\/transactions|\/transactions\?\$\{legacy|method: 'POST'|method: 'DELETE'|method: 'PATCH'/s, 'account detail must never call old unbounded account-transactions API or mutation endpoints');

assert.match(browserScript, /isPartialRecent[\s\S]*isPartialChange[\s\S]*privateAccountSentinel/s, 'accounts browser smoke must inject private diagnostics into both partial recent and partial change section details');
assert.match(browserScript, /partial account activity recent section redaction[\s\S]*assertPageSanitized[\s\S]*partial account activity change section redaction[\s\S]*assertPageSanitized/s, 'accounts browser smoke must prove partial section details are absent from SSR browser HTML');
assert.match(browserScript, /html_contains_private_sentinel=\$\{htmlContainsPrivateSentinel\}/, 'accounts browser smoke success evidence must report private sentinel serialization state');

assert.match(detailPage, /method="GET"[\s\S]*name="date_from"[\s\S]*name="date_to"[\s\S]*name="limit"[\s\S]*href=\{data\.resetActivityHref\}/s, 'account detail page must render URL-backed bounded activity controls and reset link');
assert.match(detailPage, /activity\.transaction_explorer_compatible[\s\S]*data\.transactionExplorerHref[\s\S]*unavailableNoFxScope[\s\S]*data\.reportHref/s, 'account detail page must distinguish compatible drilldown, no-FX unavailable state, and report link');
assert.match(detailPage, /recent_transactions[\s\S]*transactionHref\(tx\.id\)[\s\S]*matched_quantity/s, 'recent activity rows must use exact matched quantity and return-safe transaction detail links');
assert.match(detailPage, /aria-live=\{data\.status\.role === 'alert' \? 'assertive' : 'polite'\}[\s\S]*min-h-11[\s\S]*break-words/s, 'account detail page must expose accessible status, 44px targets, and wrapping long paths');
assert.doesNotMatch(detailPage, /localStorage|sessionStorage|fetch\(|method="POST"|formaction="\?\/create"|CREATE|PATCH|DELETE|batch/s, 'account detail page must remain SSR-first/read-only with no product mutation controls');

assert.match(txHelper, /import \{ safeAccountDetailReturnTo \} from '\$lib\/accounts\/explorer'/, 'transaction helper must use account detail return validator');
assert.match(txHelper, /safeTransactionsReturnTo[\s\S]*parsed\.hash[\s\S]*\/\^\\\/accounts\\\/\[0-9a-f\]\{32\}\$\/[\s\S]*safeAccountDetailReturnTo\(value, '\/transactions'\)/s, 'transaction detail return_to must reject fragments and permit sanitized account detail returns');

for (const key of [
	'accounts.explorer.formHelp',
	'accounts.explorer.invalidFilterTitle',
	'accounts.explorer.narrowFiltersTitle',
	'accounts.explorer.mixedCommodityWarning',
	'accounts.detail.overviewOnlyMessage',
	'accounts.detail.invalidFilterMessage',
	'accounts.detail.legacyNotice',
	'accounts.detail.unavailableNoFxScope',
	'accounts.detail.requestCounters'
]) {
	assert.ok(i18nMessages.includes(`'${key}'`), `i18n messages must include ${key}`);
}

console.log('accounts explorer static checks passed');
