import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';
import ts from 'typescript';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
// Run the actual SSR loader with transport dependencies substituted, not a parallel algorithm.
function loader(path, apiFetch, activeBook = { id: 1 }) {
    const exports = {};
    const source = readFileSync(resolve(root, path), 'utf8');
    const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } });
    runInNewContext(outputText, {
        exports, URLSearchParams, URL, require: (name) => {
            if (name === '$lib/api/server') return { apiFetch, getAuthToken: () => 'synthetic', getActiveBookContext: async () => ({ books: activeBook ? [activeBook] : [], activeBook, bookPrefix: '/books/1' }) };
            if (name === '@sveltejs/kit') return { isRedirect: () => false };
            if (name === '$lib/server/reporting-date') return { getReportingDate: async (_fetch, _prefix, _token, summaryAsOf) => summaryAsOf ?? '2026-09-06' };
            if (name === '$lib/money.js') return { compareDecimalStrings: () => { throw new Error('unexpected money comparison'); } };
            if (name === '$lib/transactions/explorer') return { buildTransactionsExplorerUrl: () => '/transactions' };
            throw new Error(`Unexpected import ${name}`);
        },
    });
    return exports.load;
}
const item = (id, status, enabled = true) => ({
    id, name: `SYNTHETIC ${id}`, enabled, has_template_account: true,
    forecast: { status, next_due_date: status === 'ready' ? '2026-09-06' : null, is_overdue: false, upcoming_7_days: status === 'ready' ? ['2026-09-06'] : [], upcoming_30_days: status === 'ready' ? ['2026-09-06'] : [] },
});
const items = [item('valid', 'ready'), item('invalid', 'unavailable'), item('disabled', 'disabled', false), item('exhausted', 'exhausted')];
const args = (query = '') => ({ cookies: {}, fetch: () => {}, url: new URL(`http://synthetic/scheduled${query}`) });
const scheduled = loader('src/routes/scheduled/+page.server.ts', async () => items);
const full = await scheduled(args());
assert.equal(full.scheduledSummary.unavailable, 1, 'QA-01 summary must count unavailable forecasts');
assert.equal(full.scheduledGroups.find((group) => group.key === 'unavailable')?.count, 1);
assert.equal(full.scheduledSummary.upcoming, 1);
assert.equal(full.scheduledSummary.laterOrInactive, 2, 'unavailable is not an ordinary inactive schedule');
const filtered = await scheduled(args('?status=disabled'));
assert.equal(filtered.scheduledTransactions.length, 1);
assert.equal(filtered.scheduledSummary.unavailable, 1, 'filter cannot erase global incompleteness warning');
const allInvalid = await loader('src/routes/scheduled/+page.server.ts', async () => [item('bad', 'unavailable')])(args());
assert.equal(allInvalid.scheduledSummary.unavailable, 1);
assert.equal(allInvalid.scheduledSummary.upcoming, 0);
const empty = await loader('src/routes/scheduled/+page.server.ts', async () => [], null)(args());
assert.equal(empty.scheduledSummary.unavailable, 0);
assert.equal(empty.scheduledGroups.length, 0);
await assert.rejects(loader('src/routes/scheduled/+page.server.ts', async () => { throw new Error('global read failure'); })(args()), /global read failure/);
for (const [values, expected] of [[items, 1], [[item('bad', 'unavailable')], 1], [[], 0]]) {
    const dashboard = loader('src/routes/dashboard/+page.server.ts', async (_fetch, path) => {
        if (path.endsWith('/reports/summary')) return { status: 'setup_required', as_of_date: '2026-09-06' };
        if (path.includes('/reports/recent-transactions')) return [];
        if (path.split('?')[0].endsWith('/scheduled-transactions')) return values;
        throw new Error(`Unexpected request ${path}`);
    });
    const data = await dashboard(args());
    assert.equal(data.upcomingObligations.unavailable_count, expected, 'Dashboard must disclose incomplete schedule data');
    assert.equal(data.sectionErrors.upcomingObligations, false, 'partial success is distinct from global read failure');
}
console.log('QA SSR loader checks passed (partial/all-invalid/empty/filter/global failure/dashboard)');
