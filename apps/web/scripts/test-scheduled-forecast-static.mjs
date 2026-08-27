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

assert.ok(existsSync(pathOf('src', 'routes', 'scheduled', '+page.server.ts')), '/scheduled server route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'scheduled', '+page.svelte')), '/scheduled page must exist');

const packageJson = JSON.parse(read('package.json'));
const apiTypes = read('src', 'lib', 'api', 'types.ts');
const server = read('src', 'routes', 'scheduled', '+page.server.ts');
const page = read('src', 'routes', 'scheduled', '+page.svelte');
const messages = read('src', 'lib', 'i18n', 'messages.ts');
const mobileNav = read('src', 'lib', 'components', 'MobileNav.svelte');
const layout = read('src', 'routes', '+layout.svelte');
const banner = read('src', 'lib', 'components', 'ReadOnlyStatusBanner.svelte');
const errorPage = read('src', 'routes', '+error.svelte');
const loginPage = read('src', 'routes', 'login', '+page.svelte');
const diagnosticsPage = read('src', 'routes', 'diagnostics', '+page.svelte');
const appHtml = read('src', 'app.html');

assert.equal(packageJson.scripts?.['test:scheduled-forecast'], 'node scripts/test-scheduled-forecast-static.mjs', 'package.json must expose the scheduled forecast static guard');
assert.equal(packageJson.scripts?.['test:scheduled-forecast-browser'], 'npm run build && node scripts/test-scheduled-forecast-browser.mjs', 'package.json must expose the build-backed scheduled forecast browser smoke');

assert.match(apiTypes, /export type ScheduledTransactionForecast[\s\S]*status: 'ready' \| 'disabled' \| 'exhausted'[\s\S]*as_of_date: string[\s\S]*next_due_date: string \| null[\s\S]*is_overdue: boolean[\s\S]*upcoming_7_days: string\[\][\s\S]*upcoming_30_days: string\[\]/s, 'frontend API types must model the bounded non-materializing forecast DTO');
assert.match(apiTypes, /export type ScheduledTransactionAmount[\s\S]*status: 'resolved' \| 'unresolved' \| 'not_available'[\s\S]*amount: string \| null[\s\S]*currency: string \| null[\s\S]*unresolved_formula_count: number[\s\S]*reason:/s, 'frontend API types must model resolved and fail-closed amount states');
assert.match(apiTypes, /export type ScheduledTransaction[\s\S]*forecast: ScheduledTransactionForecast[\s\S]*amount: ScheduledTransactionAmount[\s\S]*new_transactions_created: 0/s, 'scheduled transaction type must preserve the zero-materialization invariant');

assert.match(server, /type ScheduledForecastGroupKey = 'overdue' \| 'upcoming' \| 'next_30_days' \| 'later_or_inactive'/, 'server must use explicit forecast group keys');
assert.match(server, /function forecastGroupKey[\s\S]*forecast\.is_overdue[\s\S]*upcoming_7_days\.includes\(nextDue\)[\s\S]*upcoming_30_days\.includes\(nextDue\)[\s\S]*later_or_inactive/s, 'server must classify overdue, next-seven-day, next-thirty-day, and fallback schedules without client date arithmetic');
assert.match(server, /function groupScheduledTransactions[\s\S]*overdue:[\s\S]*upcoming:[\s\S]*next_30_days:[\s\S]*later_or_inactive:/s, 'server must return deterministic schedule groups');
assert.match(server, /ScheduledSort = 'next_due' \| 'name' \| 'enabled_first'[\s\S]*next_due_date/s, 'default scheduled sorting must be forecast-oriented');
assert.doesNotMatch(server, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]|formaction|export const actions|localStorage|sessionStorage/i, 'scheduled server load must remain read-only');

assert.match(page, /import Money from '\$lib\/components\/Money\.svelte'/, 'scheduled rows must reuse exact string money rendering');
assert.match(page, /scheduled\.group\.overdue[\s\S]*scheduled\.group\.upcoming[\s\S]*scheduled\.group\.next30[\s\S]*data\.scheduledGroups[\s\S]*data-schedule-group/s, 'scheduled page must render forecast groups with testable landmarks');
assert.match(page, /function hasResolvedAmount[\s\S]*amount\.status === 'resolved'[\s\S]*amount\.amount !== null[\s\S]*amount\.currency !== null/s, 'amount rendering must fail closed unless the backend reports a complete resolved amount');
assert.match(page, /hasResolvedAmount\(scheduled\.amount\)[\s\S]*<Money amount=\{scheduled\.amount\.amount\} currency=\{scheduled\.amount\.currency\}/s, 'only resolved amount strings may reach Money');
assert.match(page, /<details[\s\S]*scheduled\.details\.summary[\s\S]*scheduled\.forecast\.asOf[\s\S]*scheduled\.recurrence/s, 'technical recurrence and forecast details must be behind a native keyboard-accessible disclosure');
assert.doesNotMatch(page, /scheduled\.limitations|parseFloat\(|Number\([^)]*(?:amount|currency)|<form|method="POST"|localStorage|sessionStorage|fetch\(/s, 'scheduled page must not render raw backend limitations, coerce money, persist data, or expose writes');

assert.match(mobileNav, /const primaryLinks = \$derived\(\[[\s\S]*\/dashboard[\s\S]*\/accounts[\s\S]*\/transactions[\s\S]*\/scheduled/s, 'mobile bottom navigation must keep four meaningful primary destinations');
assert.match(mobileNav, /const secondaryLinks = \$derived\(\[[\s\S]*\/reports[\s\S]*\/books/s, 'secondary destinations must move into the mobile More menu');
assert.match(mobileNav, /data-mobile-primary[\s\S]*data-mobile-more[\s\S]*nav\.mobileMore/s, 'mobile primary navigation and More control must expose stable accessible landmarks');
assert.doesNotMatch(mobileNav, /max-w-full truncate|text-overflow:\s*ellipsis|overflow-x-auto|min-w-full/s, 'mobile navigation labels must wrap or fit rather than truncate or scroll horizontally');
assert.match(layout, /pb-24 md:pb-0/, 'app shell must reserve only the compact single-row mobile navigation height');

assert.match(banner, /data-read-only-banner[\s\S]*flex min-w-0 items-center[\s\S]*whitespace-nowrap[\s\S]*<details/s, 'healthy read-only status must collapse to one line with optional details');
assert.match(banner, /href="\/books"[\s\S]*safety\.reviewBooks/s, 'collapsed safety details must retain the books recovery action');

assert.match(errorPage, /const errorTitle = \$derived[\s\S]*page\.status === 403[\s\S]*error\.forbiddenTitle[\s\S]*page\.status === 404[\s\S]*error\.notFoundTitle[\s\S]*page\.status >= 500[\s\S]*error\.serviceTitle/s, 'error document titles must match 403, 404, and 5xx content');
assert.match(errorPage, /page\.status === 403 \|\| page\.status === 503[\s\S]*'\/books'[\s\S]*page\.status >= 500[\s\S]*href="\/diagnostics"/s, 'error pages must expose context-appropriate books and diagnostics actions');

assert.match(loginPage, /const firstRunAllGreen = \$derived[\s\S]*\.status === 'ok'[\s\S]*action_required\.length === 0[\s\S]*<details[^>]*open=\{!firstRunAllGreen\}/s, 'all-green login first-run diagnostics must be collapsed by default');
assert.match(diagnosticsPage, /let allChecksGreen = \$derived[\s\S]*check\.status === 'ok'[\s\S]*<details[^>]*open=\{!allChecksGreen\}/s, 'all-green public diagnostics must be collapsed by default');

assert.match(appHtml, /<link rel="icon" href="\/icon\.svg" type="image\/svg\+xml" \/>/, 'app shell must include the SVG favicon');
assert.match(appHtml, /<meta name="mobile-web-app-capable" content="yes" \/>/, 'app shell must include the modern mobile web-app capability meta tag');

for (const phrase of [
	"'scheduled.group.overdue': 'Overdue'",
	"'scheduled.group.upcoming': 'Next 7 days'",
	"'scheduled.group.next30': 'Next 30 days'",
	"'scheduled.amount.unavailable': 'Amount unavailable'",
	"'scheduled.group.overdue': 'Просрочено'",
	"'scheduled.group.upcoming': 'Ближайшие 7 дней'",
	"'scheduled.group.next30': 'Ближайшие 30 дней'",
	"'scheduled.amount.unavailable': 'Сумма недоступна'",
	"'nav.mobileMore': 'More'",
	"'nav.mobileMore': 'Ещё'"
]) {
	assert.ok(messages.includes(phrase), `localized catalog must include ${phrase}`);
}

console.log('scheduled forecast static checks passed');
