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

assert.equal(packageJson.scripts?.['test:reports'], 'node scripts/test-reports-static.mjs', 'package.json must expose npm run test:reports');

assert.match(apiTypes, /export type PeriodReportResponse/, 'API types must include the combined period reports contract');
assert.match(apiTypes, /requested_period[\s\S]*reporting_basis[\s\S]*limitations[\s\S]*summary[\s\S]*cashflow[\s\S]*expenses_by_account[\s\S]*section_errors/s, 'period report type must model requested period, limitations, sections, and explicit section errors');

assert.match(server, /getAuthToken\(cookies\)[\s\S]*getActiveBookContext\(fetch, cookies, token\)/s, '/reports must use authenticated active-book context');
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/reports'/, '/reports must be protected by the shared auth redirect hook');
assert.match(server, /apiFetch<PeriodReportResponse>\(fetch,[\s\S]*`\$\{bookPrefix\}\/reports\?\$\{reportParams\.toString\(\)\}`,[\s\S]*token\)/s, '/reports must call the active-book combined reports endpoint with date_from/date_to');
assert.doesNotMatch(server, /reports\/summary|expenses-by-account|by_month=true|recent-transactions/, '/reports must not stitch dashboard legacy endpoints');
assert.match(server, /ISO_DATE_RE[\s\S]*date_from[\s\S]*date_to[\s\S]*validationError/s, '/reports must validate custom date_from/date_to before calling the API');
assert.match(server, /this-month[\s\S]*last-month[\s\S]*year-to-date[\s\S]*custom/s, '/reports must expose URL-backed period presets and custom mode');
assert.match(server, /new URLSearchParams\(\{ limit: '50', offset: '0' \}\)[\s\S]*period: transactionFilterHref\(\{ date_from: period\.dateFrom, date_to: period\.dateTo \}\)/s, 'period drilldowns must preserve date filters and pagination defaults');
assert.match(server, /account_id: expense\.account_id[\s\S]*date_from: period\.dateFrom[\s\S]*date_to: period\.dateTo/s, 'expense drilldowns must include account_id and exact selected dates');
assert.match(server, /REDACTED_SECTION_ERROR[\s\S]*Reports API returned a section error/s, 'section errors must have a fixed redacted copy string');
assert.match(server, /section_errors[\s\S]*redactSectionError/s, 'section errors must be redacted before rendering');
assert.doesNotMatch(server, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income)/, 'reports server must not use float/Number conversion on money strings');

assert.match(page, /import \{ navigating \} from '\$app\/state';[\s\S]*LoadingState/s, '/reports page must expose accessible route loading state');
assert.match(server, /This month[\s\S]*Last month[\s\S]*Year to date/s, '/reports server must expose canonical preset labels');
assert.match(page, /data\.presetOptions[\s\S]*name="date_from"[\s\S]*name="date_to"/s, '/reports page must render preset links and custom date inputs');
assert.match(page, /role="alert"[\s\S]*invalid range|invalid range[\s\S]*role="alert"/s, '/reports page must render an accessible invalid-range alert');
assert.match(page, /partial report|partial-error|partial errors|sectionWarnings/s, '/reports page must distinguish partial section errors from empty results');
assert.match(page, /base_currency_only[\s\S]*No FX conversion|No FX conversion[\s\S]*base_currency_only/s, '/reports page must show base-currency-only/no-FX limitations');
assert.match(page, /href=\{data\.drilldowns\.period\}[\s\S]*\/transactions|\/transactions[\s\S]*href=\{data\.drilldowns\.period\}/s, '/reports page must link the selected period to /transactions');
assert.match(page, /data\.drilldowns\.expensesByAccount\[expense\.account_id\]/s, 'expense rows must use exact account drilldown URLs');
assert.match(page, /data\.drilldowns\.cashflowByMonth\[period\.month\]/s, 'monthly cashflow rows must use exact period drilldown URLs');
assert.match(page, /EmptyState[\s\S]*No report data|No report data[\s\S]*EmptyState/s, '/reports page must render a genuine empty state separately from API errors');
assert.doesNotMatch(page, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income)/, 'reports page must not use float/Number conversion on money strings');

console.log('reports static checks passed');
