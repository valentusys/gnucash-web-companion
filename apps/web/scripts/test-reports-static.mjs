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

assert.ok(existsSync(pathOf('src', 'routes', 'reports', '+page.server.ts')), '/reports server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'reports', '+page.svelte')), '/reports page route must exist');

const packageJson = JSON.parse(read('package.json'));
const server = read('src', 'routes', 'reports', '+page.server.ts');
const page = read('src', 'routes', 'reports', '+page.svelte');
const apiTypes = read('src', 'lib', 'api', 'types.ts');
const hooks = read('src', 'hooks.server.ts');
const desktopNav = read('src', 'lib', 'components', 'DesktopNav.svelte');
const mobileNav = read('src', 'lib', 'components', 'MobileNav.svelte');
const i18nMessages = read('src', 'lib', 'i18n', 'messages.ts');
const money = read('src', 'lib', 'money.js');

assert.equal(packageJson.scripts?.['test:reports'], 'node scripts/test-reports-static.mjs', 'package.json must expose npm run test:reports');
assert.equal(packageJson.scripts?.['test:reports-browser'], 'npm run build && node scripts/test-reports-browser.mjs', 'package.json must expose a bounded build-backed reports browser smoke');

assert.match(apiTypes, /export type PeriodReport[\s\S]*date_from[\s\S]*date_to[\s\S]*partial_failure[\s\S]*empty[\s\S]*section_statuses[\s\S]*monthly_cashflow[\s\S]*expenses_by_account/s, 'existing period report type must remain backward compatible');
assert.match(apiTypes, /export type ReportComparisonMode = 'previous_equivalent' \| 'same_period_last_year' \| 'custom'/, 'comparison mode type must use the frozen enum');
assert.match(apiTypes, /export type MoneyDelta[\s\S]*primary: string[\s\S]*comparison: string[\s\S]*delta: string[\s\S]*absolute_delta: string[\s\S]*currency: string/s, 'money deltas must expose Decimal-string primary/comparison/signed/absolute fields');
assert.match(apiTypes, /export type PeriodReportComparison[\s\S]*primary: PeriodReport[\s\S]*comparison: PeriodReport[\s\S]*delta_section_statuses[\s\S]*summary_delta[\s\S]*cashflow_delta[\s\S]*expense_changes/s, 'comparison response type must nest both period reports and typed deltas');
assert.match(apiTypes, /export type ExpenseAccountComparison[\s\S]*primary_total[\s\S]*comparison_total[\s\S]*delta: string \| null[\s\S]*absolute_delta: string \| null[\s\S]*status: 'ok' \| 'not_comparable'[\s\S]*detail: string \| null/s, 'expense change DTO must model backend nullable row-local comparison status and safe detail');

assert.match(desktopNav, /href: '\/reports'[\s\S]*nav\.reports[\s\S]*aria-current=\{active \? 'page'/s, 'desktop navigation must include Reports with active route state');
assert.match(mobileNav, /href: '\/reports'[\s\S]*icon: 'reports'[\s\S]*aria-current=\{active \? 'page'/s, 'mobile navigation must include Reports with active route state');
assert.match(i18nMessages, /'nav\.reports': 'Reports'[\s\S]*'reports\.comparison\.mode\.previousEquivalent'[\s\S]*'reports\.comparison\.notComparable'[\s\S]*'reports\.comparison\.rowNotComparable'[\s\S]*Exact 0\.00 values[\s\S]*Backend limitation/s, 'English catalog must include release-critical comparison/no-FX/row-not-comparable/zero copy');
assert.match(i18nMessages, /'nav\.reports': 'Отчёты'[\s\S]*'reports\.comparison\.mode\.previousEquivalent'[\s\S]*Unknown or mismatched currency\/no-FX limitations[\s\S]*'reports\.comparison\.rowNotComparable'[\s\S]*0\.00[\s\S]*Backend limitation/s, 'Russian catalog must include bounded technical comparison copy without claiming full localization');

assert.match(server, /getAuthToken\(cookies\)[\s\S]*getActiveBookContext\(fetch, cookies, token\)/s, '/reports must use authenticated active-book context');
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/reports'/, '/reports must be protected by the shared auth redirect hook');
assert.match(server, /COMPARISON_MODES = \['previous_equivalent', 'same_period_last_year', 'custom'\]/, 'server must define the frozen comparison modes');
assert.match(server, /function previousEquivalentRange[\s\S]*inclusiveDayCount\(period\.dateFrom, period\.dateTo\)[\s\S]*dateFrom: addDays\(period\.dateFrom, -days\)[\s\S]*dateTo: addDays\(period\.dateFrom, -1\)/s, 'previous-equivalent must use equal inclusive day count immediately before primary');
assert.match(server, /function shiftOneYearBackClamp[\s\S]*getUTCFullYear\(\) - 1[\s\S]*Math\.min\(source\.getUTCDate\(\), daysInMonth\(year, month\)\)/s, 'same-period-last-year must clamp leap/end-of-month dates');
assert.match(server, /comparison_mode: comparison\.mode[\s\S]*comparison_date_from: comparison\.dateFrom[\s\S]*comparison_date_to: comparison\.dateTo/s, 'comparison API query must include all five date/mode fields');
assert.match(server, /apiFetch<PeriodReportComparison>\(fetchFn, `\$\{bookPrefix\}\/reports\/comparison\?\$\{comparisonParams\.toString\(\)\}`/s, '/reports must call only the active-book comparison endpoint');
assert.doesNotMatch(server, /apiFetch<PeriodReport>\(fetchFn, `\$\{bookPrefix\}\/reports\?/, 'frontend must not call the old one-period endpoint for the comparison page');
assert.doesNotMatch(server, /\$\{bookPrefix\}\/reports\/(summary|cashflow|expenses-by-account)/, '/reports page must not reconstruct reports from old dashboard endpoints');
assert.match(server, /resolveComparisonPeriod[\s\S]*mode === 'custom'[\s\S]*comparison_date_from[\s\S]*comparison_date_to[\s\S]*validationError/s, 'custom comparison dates must be validated before API calls');
assert.match(server, /rawDateFrom !== expected\.dateFrom \|\| rawDateTo !== expected\.dateTo[\s\S]*reports\.comparison\.validation\.inconsistentRange/s, 'derived comparison modes must reject inconsistent supplied comparison dates before API calls');
assert.match(server, /if \(!validationError\)[\s\S]*loadComparisonReport/s, '/reports must skip API requests when primary or comparison validation fails');
assert.match(server, /transactionFilterHref\(\{[\s\S]*account_id: expense\.accountId[\s\S]*date_from: report\.primary\.requestedPeriod\.dateFrom[\s\S]*date_to: report\.primary\.requestedPeriod\.dateTo[\s\S]*comparison: transactionFilterHref/s, 'expense change drilldowns must include account_id and exact dates for both sides');
assert.match(server, /deltaSectionMessageFromStatus[\s\S]*reports\.comparison\.deltaError[\s\S]*not_comparable[\s\S]*reports\.comparison\.notComparable/s, 'delta section statuses must distinguish not_comparable and redacted errors');
assert.match(server, /normalizeExpenseChanges[\s\S]*status[\s\S]*not_comparable[\s\S]*delta[\s\S]*absoluteDelta/s, 'expense-change mapper must preserve row-local not_comparable rows without requiring nullable deltas');
assert.doesNotMatch(server, /detail:\s*stringValue\(expense\.detail\)|(?:^|\n)\s*deltaSectionStatuses,\s*(?:\n|$)|detail:\s*status\.detail/s, 'server load data must not serialize raw backend comparison detail into the rendered page');
assert.doesNotMatch(server, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income|delta)/, 'reports server must not use float/Number conversion on money strings');

assert.match(page, /fieldset[\s\S]*reports\.period\.title[\s\S]*fieldset[\s\S]*reports\.comparison\.title/s, '/reports page must render accessible primary and comparison controls');
assert.match(page, /name="comparison_mode"[\s\S]*name="comparison_date_from"[\s\S]*name="comparison_date_to"/s, '/reports page must preserve comparison URL fields in forms');
assert.match(page, /data\.comparisonModeOptions[\s\S]*previousEquivalent|comparisonModeOptions/s, '/reports page must expose comparison mode links');
assert.match(page, /reports\.comparison\.sourcePeriodsTitle[\s\S]*data\.drilldowns\.primary\.period[\s\S]*data\.drilldowns\.comparison\.period/s, '/reports page must link primary and comparison totals to exact /transactions filters');
assert.match(page, /reports\.comparison\.summaryDeltaTitle[\s\S]*reports\.comparison\.cashflowDeltaTitle[\s\S]*reports\.comparison\.expenseChangesTitle/s, '/reports page must render summary, cashflow and spending-change sections');
assert.match(page, /changeLabel[\s\S]*compareDecimalStrings\(delta\.delta, '0'\)[\s\S]*reports\.comparison\.unchanged/s, '/reports page must distinguish unchanged zero deltas with BigInt decimal helpers');
assert.match(page, /isComparableExpenseChange[\s\S]*expense\.status === 'ok'[\s\S]*expense\.delta[\s\S]*expense\.absoluteDelta/s, 'expense rows must explicitly narrow comparable rows before Decimal/BigInt helpers');
assert.match(page, /expenseChangeBar[\s\S]*ComparableExpenseChangeItem[\s\S]*allExpenses\.map\(\(item\) => item\.absoluteDelta\)/s, 'expense bars must use only comparable backend absolute_delta strings while preserving backend row order');
assert.match(page, /reports\.comparison\.rowNotComparable[\s\S]*expense\.primaryTotal[\s\S]*expense\.comparisonTotal/s, 'row-local not_comparable rows must show fixed redacted copy while preserving side totals/drilldowns');
assert.match(page, /data\.drilldowns\.expenseChanges\[expense\.accountId\]\?\.primary[\s\S]*data\.drilldowns\.expenseChanges\[expense\.accountId\]\?\.comparison/s, 'expense rows must expose paired exact side drilldowns');
assert.doesNotMatch(page, /changeLabel\(\{\s*primary: expense\.primaryTotal/s, 'expense rows must not pass row-local nullable deltas into Decimal comparison helpers');
assert.match(page, /role="alert"[\s\S]*reports\.validation\.invalidTitle|reports\.validation\.invalidTitle[\s\S]*role="alert"/s, '/reports page must render an accessible invalid-range alert');
assert.doesNotMatch(page, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income|delta)/, 'reports page must not use float/Number conversion on money strings');
assert.doesNotMatch(page, /localStorage|sessionStorage|formaction="\?\/create"|method="POST"/s, '/reports must not persist report state in browser storage or expose write submissions');
assert.match(money, /BigInt\([\s\S]*compareDecimalStrings[\s\S]*decimalBarWidthPercent/s, 'money helpers must keep Decimal-string decisions on BigInt helpers');

console.log('reports static checks passed');
