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

assert.equal(packageJson.scripts?.['test:reports'], 'node scripts/test-reports-static.mjs', 'package.json must expose npm run test:reports');
assert.equal(packageJson.scripts?.['test:reports-browser'], 'npm run build && node scripts/test-reports-browser.mjs', 'package.json must expose a bounded build-backed reports browser smoke');

assert.match(apiTypes, /export type ReportSummary[\s\S]*income_this_month[\s\S]*expenses_this_month[\s\S]*reporting_basis[\s\S]*includes_currency_conversion[\s\S]*limitations/s, 'dashboard report summary type must preserve existing backend DTO names');
assert.match(apiTypes, /export type CashflowData[\s\S]*date_from[\s\S]*date_to[\s\S]*inflow[\s\S]*outflow[\s\S]*net/s, 'cashflow type must keep exact backend date/money string fields');
assert.match(apiTypes, /export type ExpenseByAccount[\s\S]*account_id[\s\S]*account_name[\s\S]*total[\s\S]*currency/s, 'expense report rows must expose exact account_id drilldown fields');
assert.match(apiTypes, /export type PeriodReportSummary[\s\S]*net_worth[\s\S]*assets[\s\S]*liabilities[\s\S]*as_of_date[\s\S]*limitations/s, 'period report summary must be balance-only and must not reuse dashboard month income fields');
assert.match(apiTypes, /export type PeriodReportSectionStatus[\s\S]*section: 'summary' \| 'cashflow' \| 'monthly_cashflow' \| 'expenses_by_account'[\s\S]*status: 'ok' \| 'empty' \| 'error'[\s\S]*detail/s, 'period report section statuses must match backend section_statuses contract');
assert.match(apiTypes, /export type PeriodReport[\s\S]*date_from[\s\S]*date_to[\s\S]*partial_failure[\s\S]*empty[\s\S]*section_statuses[\s\S]*monthly_cashflow[\s\S]*expenses_by_account/s, 'period report type must match the combined backend DTO fields');

assert.match(desktopNav, /href: '\/reports'[\s\S]*nav\.reports[\s\S]*aria-current=\{active \? 'page'/s, 'desktop navigation must include Reports with active route state');
assert.match(mobileNav, /href: '\/reports'[\s\S]*icon: 'reports'[\s\S]*aria-current=\{active \? 'page'/s, 'mobile navigation must include Reports with active route state');
assert.match(i18nMessages, /'nav\.reports': 'Reports'[\s\S]*'reports\.metaTitle': 'Period reports'[\s\S]*'reports\.limitations\.reportingBasis'[\s\S]*No FX conversion[\s\S]*base_currency_only/s, 'English reports catalog must include release-critical Reports and no-FX copy');
assert.match(i18nMessages, /'nav\.reports': 'Отчёты'[\s\S]*'reports\.metaTitle': 'Отчёты за период'[\s\S]*'reports\.limitations\.reportingBasis'[\s\S]*No FX conversion[\s\S]*base_currency_only[\s\S]*без FX-конвертации/s, 'Russian reports catalog must include release-critical Reports and no-FX copy without claiming full localization');
assert.match(i18nMessages, /Period income\/expenses\/net come from cashflow[\s\S]*balance totals are as of date_to[\s\S]*Доходы\/расходы\/итог берутся из cashflow[\s\S]*date_to/s, 'summary copy must not mislabel date_to month dashboard fields as arbitrary-period totals');

assert.match(server, /getAuthToken\(cookies\)[\s\S]*getActiveBookContext\(fetch, cookies, token\)/s, '/reports must use authenticated active-book context');
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/reports'/, '/reports must be protected by the shared auth redirect hook');
assert.match(server, /apiFetch<PeriodReport>\(fetchFn, `\$\{bookPrefix\}\/reports\?\$\{rangeParams\.toString\(\)\}`/s, '/reports must call the combined active-book period report endpoint with date_from/date_to');
assert.doesNotMatch(server, /\$\{bookPrefix\}\/reports\/(summary|cashflow|expenses-by-account)/, '/reports page must not reconstruct the milestone from old dashboard endpoints');
assert.match(server, /ISO_DATE_RE[\s\S]*date_from[\s\S]*date_to[\s\S]*reports\.validation\.invalidDateRange[\s\S]*!validationError/s, '/reports must validate custom date_from/date_to before report API calls');
assert.match(server, /this-month[\s\S]*last-month[\s\S]*year-to-date[\s\S]*custom[\s\S]*reports\.preset\.thisMonth[\s\S]*reports\.preset\.lastMonth[\s\S]*reports\.preset\.yearToDate/s, '/reports must expose URL-backed period presets through i18n labels and custom mode');
assert.match(server, /new URLSearchParams\(\{ limit: '50', offset: '0' \}\)[\s\S]*period: transactionFilterHref\(\{ date_from: period\.dateFrom, date_to: period\.dateTo \}\)/s, 'period drilldowns must preserve date filters and pagination defaults');
assert.match(server, /account_id: expense\.account_id[\s\S]*date_from: period\.dateFrom[\s\S]*date_to: period\.dateTo/s, 'expense drilldowns must include account_id and exact selected dates');
assert.match(server, /function monthRange[\s\S]*date_from: maxIsoDate\(monthStart, period\.dateFrom\)[\s\S]*date_to: minIsoDate\(monthEnd, period\.dateTo\)/s, 'monthly drilldowns must clamp to the selected period');
assert.match(server, /function sectionErrorFromStatus[\s\S]*reports\.sectionError\.redacted[\s\S]*function sectionErrorsFromStatuses[\s\S]*monthly_cashflow/s, 'section errors must come from backend section_statuses and use fixed localized redacted copy');
assert.match(server, /periodReport\.empty[\s\S]*section_statuses[\s\S]*safeLoadError/s, 'empty reports, partial section statuses, and whole-request failures must stay distinct');
assert.doesNotMatch(server, /income_this_month|expenses_this_month/, 'period report frontend must not read dashboard month-of-date_to income/expense fields');
assert.doesNotMatch(server, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income)/, 'reports server must not use float/Number conversion on money strings');

assert.match(page, /import \{ navigating \} from '\$app\/state';[\s\S]*LoadingState/s, '/reports page must expose accessible route loading state');
assert.match(page, /DEFAULT_LOCALE[\s\S]*t\(locale, 'reports\.metaTitle'[\s\S]*reports\.localizationNotice/s, '/reports page must use the existing i18n catalog for release-critical copy without claiming full localization');
assert.match(page, /data\.presetOptions[\s\S]*name="date_from"[\s\S]*name="date_to"/s, '/reports page must render preset links and custom date inputs');
assert.match(page, /role="alert"[\s\S]*reports\.validation\.invalidTitle|reports\.validation\.invalidTitle[\s\S]*role="alert"/s, '/reports page must render an accessible invalid-range alert');
assert.match(page, /reports\.partial\.title|partial-error|sectionWarnings/s, '/reports page must distinguish partial section errors from empty results');
assert.match(page, /report\.sectionErrors\.monthly_cashflow[\s\S]*reports\.cashflow\.noMonthly/s, '/reports page must distinguish monthly cashflow section errors from true empty monthly rows');
assert.match(page, /reports\.limitations\.reportingBasis[\s\S]*reports\.limitations\.none/s, '/reports page must show base-currency-only/no-FX limitations through i18n copy');
assert.match(page, /href=\{data\.drilldowns\.period\}[\s\S]*reports\.viewTransactionsPeriod[\s\S]*href=\{data\.drilldowns\.period\}[\s\S]*reports\.summary\.openFilter/s, '/reports page must link the selected period to /transactions');
assert.match(page, /data\.drilldowns\.expensesByAccount\[expense\.account_id\]/s, 'expense rows must use exact account drilldown URLs');
assert.match(page, /data\.drilldowns\.cashflowByMonth\[period\.month\]/s, 'monthly cashflow rows must use exact period drilldown URLs');
assert.match(page, /EmptyState[\s\S]*reports\.empty\.title[\s\S]*reports\.empty\.message/s, '/reports page must render a genuine empty state separately from API errors');
assert.doesNotMatch(page, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income)/, 'reports page must not use float/Number conversion on money strings');
assert.doesNotMatch(page, /localStorage|sessionStorage|formaction="\?\/create"|method="POST"/s, '/reports must not persist report state in browser storage or expose write submissions');

console.log('reports static checks passed');
