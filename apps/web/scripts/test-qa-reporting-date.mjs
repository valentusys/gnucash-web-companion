import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import ts from 'typescript';

class FrozenDate extends Date {
    constructor(...args) { super(...(args.length ? args : ['2026-09-05T15:30:00Z'])); }
}
function moduleAt(relative, imports={}, extra='') {
    const source = readFileSync(new URL('../src/'+relative, import.meta.url),'utf8')+extra;
    const { outputText } = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}});
    const exports = {};
    runInNewContext(outputText,{exports,URL,URLSearchParams,Date:FrozenDate,require:name=>imports[name] ?? {}});
    return exports;
}
const reports = moduleAt('routes/reports/+page.server.ts', {'$lib/i18n':{t:(_locale,key)=>key}}, '\nexport {resolvePeriod,presetRange,buildComparisonModeOptions};');
for (const asOf of ['2026-09-06','2026-09-05','2026-01-01','2024-03-01','2024-02-29','2026-03-08']) {
    const result = reports.resolvePeriod(new URL('http://test/reports'), 'en', asOf);
    assert.equal(result.period.dateTo,asOf,'QA-04 report must use API reporting date, not UTC instant');
    assert.equal(result.period.dateFrom,asOf.slice(0,7)+'-01');
}
const leap = reports.resolvePeriod(new URL('http://test/reports?preset=last-month'), 'en', '2024-03-01');
assert.equal(leap.period.dateFrom,'2024-02-01');
assert.equal(leap.period.dateTo,'2024-02-29');
const custom = reports.resolvePeriod(new URL('http://test/reports?preset=custom&date_from=2020-01-01&date_to=2020-02-01'), 'en', null);
assert.equal(custom.validationError,null,'Explicit valid dates do not require current clock availability');
assert.equal(custom.period.dateTo,'2020-02-01');
const unavailable = reports.resolvePeriod(new URL('http://test/reports'), 'en', null);
assert.ok(unavailable.validationError,'No silent UTC fallback if authoritative reporting date is unavailable');
assert.equal(unavailable.period.dateTo,'');
assert.equal(reports.buildComparisonModeOptions(unavailable.period,{mode:'previous_equivalent'},'en').length,0,'Unavailable date must not throw while building comparison links');

let requests = 0;
let reply = {as_of_date:'2026-09-06'};
const redirect = {redirect:true};
const clock = moduleAt('lib/server/reporting-date.ts', {
    '$lib/api/server':{apiFetch:async()=>{requests++; if(reply instanceof Error || reply===redirect) throw reply; return reply;}},
    '@sveltejs/kit':{isRedirect:reason=>reason===redirect},
});
assert.equal(await clock.getReportingDate(()=>{},'/books/1','token','2024-02-29'),'2024-02-29');
assert.equal(requests,0,'Valid summary.as_of_date has priority and avoids another clock read');
assert.equal(await clock.getReportingDate(()=>{},'/books/1','token'),'2026-09-06');
for (const invalid of [null, {}, {as_of_date:'2026-02-30'}, {as_of_date:'2026-99-99'}, {as_of_date:'2026-9-6'}, {as_of_date:'2026-09-06T00:00Z'}, new Error('unavailable')]) {
    reply=invalid;
    assert.equal(await clock.getReportingDate(()=>{},'/books/1','token'),null);
}
reply=redirect;
await assert.rejects(clock.getReportingDate(()=>{},'/books/1','token'),reason=>reason===redirect);
for (const authority of ['2026-09-06', null]) {
    const dashboard = moduleAt('routes/dashboard/+page.server.ts', {
        '$lib/api/server':{getAuthToken:()=> 'synthetic',getActiveBookContext:async()=>({activeBook:{id:1},bookPrefix:'/books/1'}),apiFetch:async(_fetch,path)=>{if(path.includes('/summary'))throw new Error('summary unavailable'); return []; }},
        '$lib/server/reporting-date':{getReportingDate:async()=>authority},
        '$lib/money.js':{compareDecimalStrings:()=>0},
        '$lib/transactions/explorer':{buildTransactionsExplorerUrl:()=>'/transactions'},
        '@sveltejs/kit':{isRedirect:()=>false},
    });
    const data = await dashboard.load({cookies:{},fetch:()=>{}});
    assert.equal(data.reportingDate,authority,'Summary failure uses authoritative date or explicit unavailable state, never UTC today');
}
const explorerHelpers = moduleAt('lib/transactions/explorer.ts');
const txLoader = moduleAt('routes/transactions/+page.server.ts',{'$lib/transactions/explorer':explorerHelpers,'$env/dynamic/private':{env:{}}},'\nexport {buildExplorerDatePresets,buildLegacyDatePresets};');
const filters = {accountIds:['a'.repeat(32)],direction:'decrease',type:'',transactionState:'reconciled',query:'SYNTHETIC',sort:'date_asc',pageSize:20,cursor:'stale'};
for (const asOf of ['2026-09-06','2024-03-01','2026-01-01']) {
    const options = txLoader.buildExplorerDatePresets(filters,asOf);
    const current = new URL(options[0].href,'http://test');
    assert.equal(current.searchParams.get('date_to'),asOf);
    assert.equal(current.searchParams.get('account_ids'),'a'.repeat(32));
    assert.equal(current.searchParams.get('page_size'),'20');
    assert.equal(current.searchParams.get('direction'),'decrease');
    assert.equal(current.searchParams.get('cursor'),null);
    const legacy = txLoader.buildLegacyDatePresets({accountId:'synthetic',limit:20,offset:40},asOf);
    assert.equal(new URL(legacy[0].href,'http://test').searchParams.get('date_to'),asOf);
}
assert.equal(txLoader.buildExplorerDatePresets(filters,null).length,0);
assert.equal(txLoader.buildLegacyDatePresets({},null).length,0);
let scheduledPath;
const scheduledLoader = moduleAt('routes/scheduled/+page.server.ts',{'$lib/api/server':{getAuthToken:()=> 'token',getActiveBookContext:async()=>({activeBook:{id:1},books:[],bookPrefix:'/books/1'}),apiFetch:async(_f,path)=>{scheduledPath=path;return [];}}});
const scheduledData = await scheduledLoader.load({cookies:{},fetch:()=>{},url:new URL('http://test/scheduled?as_of_date=2024-02-29')});
assert.equal(new URL(scheduledPath,'http://test').searchParams.get('as_of_date'),'2024-02-29');
assert.equal(new URL(scheduledData.filters.links.enabled,'http://test').searchParams.get('as_of_date'),'2024-02-29');
const ci = readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');
assert.match(ci,/npm run test:qa-reporting-date/);
for (const instant of ['2026-09-05T15:30:00+00:00','2026-09-06T02:30:00+00:00','2025-12-31T15:00:00+00:00']) assert.ok(ci.includes('QA_REPORTING_INSTANT='+instant),'CI must retain cross-zone clock cases');
console.log('QA-04 reporting date authority, rollover, explicit dates and unavailable cases passed');
