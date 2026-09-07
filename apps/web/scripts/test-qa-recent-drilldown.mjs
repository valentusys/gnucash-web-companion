import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import ts from 'typescript';

function moduleAt(path, imports = {}, extra = '') {
    const source = readFileSync(new URL('../src/' + path, import.meta.url), 'utf8') + extra;
    const exports = {};
    runInNewContext(ts.transpileModule(source, {
        compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
    }).outputText, { exports, URL, URLSearchParams, require: name => imports[name] ?? {} });
    return exports;
}
const extra = '\nexport const recentPeriodHelper = typeof boundedRecentPeriods === "function" ? boundedRecentPeriods : undefined;';
const { recentPeriodHelper } = moduleAt('routes/dashboard/+page.server.ts', {}, extra);
assert.equal(typeof recentPeriodHelper, 'function', 'QA-09 dashboard must derive bounded periods from recent dates');
const periods = (dates, asof = '2026-09-06') => JSON.parse(JSON.stringify(recentPeriodHelper(dates.map(date => ({ date })), asof)));
assert.deepEqual(periods(['2026-08-01', '2026-08-31']), [{ date_from: '2026-08-01', date_to: '2026-08-31' }], 'Use shown dates, not current month');
assert.deepEqual(periods(['2010-01-01', '2026-09-06', '2024-02-29', '2026-09-01', '2026-09-01']), [
    { date_from: '2026-09-01', date_to: '2026-09-06' },
    { date_from: '2024-02-29', date_to: '2024-02-29' },
    { date_from: '2010-01-01', date_to: '2010-01-01' },
]);
assert.equal(periods(['2024-01-01', '2024-12-31']).length, 1, '366 inclusive days remain allowed');
assert.equal(periods(['2023-12-31', '2024-12-31']).length, 2, 'A wider span is split');
assert.deepEqual(periods([], '2024-02-29'), [{ date_from: '2024-02-01', date_to: '2024-02-29' }]);
for (const date of [null, 'bad', '2026-02-30']) assert.deepEqual(periods([], date), [], 'Never guess an unavailable date');
assert.deepEqual(periods(['bad', '2026-99-01', '2026-02-30'], null), []);
assert.deepEqual(periods(['2010-01-01'], null), [{ date_from: '2010-01-01', date_to: '2010-01-01' }], 'Shown dates work without current clock');

const explorer = moduleAt('lib/transactions/explorer.ts');
for (const [dates, asof] of [[['2026-08-01', '2010-01-01'], '2026-09-06'], [[], '2024-02-29'], [[], null]]) {
    const calls = [];
    const dashboard = moduleAt('routes/dashboard/+page.server.ts', {
        '$lib/api/server': {
            getAuthToken: () => 'synthetic',
            getActiveBookContext: async () => ({ activeBook: { id: 7 }, bookPrefix: '/books/7' }),
            apiFetch: async (_fetch, path, token) => {
                calls.push({ path, token });
                if (path.endsWith('/reports/summary')) return { status: 'setup_required', as_of_date: asof };
                if (path.includes('/reports/recent-transactions')) return dates.map(date => ({ date }));
                if (path.includes('/scheduled-transactions')) return [];
                throw new Error('Unexpected path ' + path);
            },
        },
        '$lib/server/reporting-date': { getReportingDate: async () => asof },
        '$lib/transactions/explorer': explorer,
        '@sveltejs/kit': { isRedirect: () => false },
    });
    const data = await dashboard.load({ cookies: {}, fetch: () => {} });
    const expected = periods(dates, asof);
    assert.equal(data.drilldowns.recentPeriods?.length, expected.length, 'All bounded periods must reach UI');
    assert.equal(data.drilldowns.recent, data.drilldowns.recentPeriods[0]?.href ?? null);
    data.drilldowns.recentPeriods.forEach((period, index) => {
        const url = new URL(period.href, 'http://synthetic');
        assert.equal(url.pathname, '/transactions');
        assert.equal(url.searchParams.get('date_from'), expected[index].date_from);
        assert.equal(url.searchParams.get('date_to'), expected[index].date_to);
        assert.equal(url.searchParams.get('sort'), 'date_desc');
        assert.equal(url.searchParams.get('page_size'), '50');
        assert.equal(url.searchParams.get('cursor'), null);
    });
    assert.equal(data.activeBook.id, 7);
    assert.ok(calls.every(({ path, token }) => path.startsWith('/books/7/') && token === 'synthetic'));
}
const component = readFileSync(new URL('../src/lib/components/RecentTransactions.svelte', import.meta.url), 'utf8');
const page = readFileSync(new URL('../src/routes/dashboard/+page.svelte', import.meta.url), 'utf8');
assert.match(component, /data-recent-period/);
assert.match(component, /dashboard\.recentOlderPeriod/);
assert.match(component, /#if drilldownHref/);
assert.doesNotMatch(component, /drilldownHref = '\/transactions'/, 'No unbounded fallback');
assert.match(page, /recentPeriods=\{data\.drilldowns\.recentPeriods\}/);
const ci = readFileSync(new URL('../../../.github/workflows/ci.yml', import.meta.url), 'utf8');
assert.match(ci, /npm run test:qa-recent-drilldown/);
assert.match(ci, /for scenario in scheduled_partial scheduled_valid scheduled_invalid empty money recent_sparse account_groups; do/);
console.log('QA-09 recent bounds, sparse/old/empty/invalid dates, real loader wiring and UI guards passed');
