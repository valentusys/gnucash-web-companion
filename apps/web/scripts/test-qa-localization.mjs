import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
function moduleAt(path,imports={},extra='') {
    const source=readFileSync(new URL('../src/'+path,import.meta.url),'utf8')+extra, exports={};
    vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,{exports,URL,URLSearchParams,Date,require:n=>imports[n]??{}});return exports;
}
const messages=moduleAt('lib/i18n/messages.ts');
const i18n=moduleAt('lib/i18n/index.ts',{'./messages':messages});
const explorer=moduleAt('lib/transactions/explorer.ts');
const server=moduleAt('routes/transactions/+page.server.ts',{'$lib/i18n':i18n,'$lib/transactions/explorer':explorer},'\nexport {buildExplorerDatePresets,buildLegacyDatePresets,activeExplorerChips};');
const accountExplorer=moduleAt('lib/accounts/explorer.ts');
const accountServer=moduleAt('routes/accounts/+page.server.ts',{'$lib/i18n':i18n,'$lib/accounts/explorer':accountExplorer,'$lib/api/server':{getAuthToken:()=> 'synthetic',getActiveBookContext:async()=>({activeBook:{id:1},bookPrefix:'/books/1'})}},'\nexport {activeExplorerChips};');
for (const locale of ['ru','en']) {
    for (const type of ['income','expense']) {
        const chips=server.activeExplorerChips({accountIds:[],type},[],locale);
        assert.equal(chips[0].label,i18n.t(locale,'transactions.explorer.type')+': '+i18n.t(locale,type==='income'?'transactions.explorer.typeIncome':'transactions.explorer.typeExpense'));
        assert.equal(new URL(chips[0].href,'http://test').searchParams.has('type'),false);
    }
    for (const direction of ['increase','decrease']) {
        const chips=server.activeExplorerChips({accountIds:[],direction},[],locale);
        assert.equal(chips[0].label,i18n.t(locale,'transactions.explorer.direction')+': '+i18n.t(locale,direction==='increase'?'transactions.explorer.directionIncrease':'transactions.explorer.directionDecrease'));
    }
    for (const [state,key] of [['unreconciled','stateUnreconciled'],['cleared','stateCleared'],['reconciled','stateReconciled'],['voided','stateVoided']]) {
        const chips=server.activeExplorerChips({accountIds:[],transactionState:state},[],locale);
        assert.equal(chips[0].label,i18n.t(locale,'transactions.filters.summary.state')+': '+i18n.t(locale,'transactions.filters.'+key));
    }
    for (const [field,modes] of [['hidden',['include','only']],['placeholder',['exclude','only']]]) for (const mode of modes) {
        const chips=accountServer.activeExplorerChips({mode:'tree',query:'',types:[],hidden:'exclude',placeholder:'include',[field]:mode},locale);
        assert.equal(chips[0].label,i18n.t(locale,'accounts.explorer.'+field)+': '+i18n.t(locale,'accounts.explorer.visibility'+mode[0].toUpperCase()+mode.slice(1)));
    }
    const invalid=await accountServer.load({cookies:{get:()=>locale},fetch:()=>{throw Error('Invalid filters must not fetch');},url:new URL('http://test/accounts?unknown=1')});
    assert.equal(invalid.status.role,'alert');
    if(locale==='ru') assert.doesNotMatch(invalid.status.message,/[a-z]/i,'Invalid account filter error localized');
}

for(const name of ['buildExplorerDatePresets','buildLegacyDatePresets']) for(const locale of ['en','ru']) {
    const presets=server[name]({accountIds:[],sort:'date_desc',pageSize:20},'2026-09-07',locale);
    assert.equal(presets[0].label,locale==='ru'?'Этот месяц':'This month');
    assert.equal(presets[1].label,locale==='ru'?'Прошлый месяц':'Last month');
    assert.equal(presets[3].label,locale==='ru'?'Убрать даты':'Clear dates');
}
for(const key of ['scopeLegend','type','typeAny','direction','amountPagingLegend','reset','cursorChip','dateRangeRequiredMessage','readyTitle','readyMessage','trueEmptyMessage','scanWindowEmptyTitle','scanWindowEmptyMessage','scanLimitedTitle','scanLimitedMessage','endTitle','endMessage','invalidFilterTitle','invalidFilterMessage','staleCursorTitle','staleCursorMessage','loadFailedTitle','loadFailedMessage','unknownFailureTitle','unknownFailureMessage','resetPagination','paginationLabel']) {
    assert.doesNotMatch(messages.messages.ru['transactions.explorer.'+key], /[a-z]/i, `Primary Russian explorer copy: ${key}`);
}
for (const [key, value] of Object.entries(messages.messages.ru)) {
    if (key.startsWith('accounts.explorer.') || key.startsWith('transactions.filters.') || key.startsWith('transactions.explorer.') || ['accounts.loading', 'accounts.emptyMessage'].includes(key)) {
        assert.doesNotMatch(value.replace(/\{[^}]+\}|Ctrl|Cmd|CSV|GnuCash|account_ids/g, ''), /[a-z]/i, `Russian primary/filter copy: ${key}`);
    }
}
const template=readFileSync(new URL('../src/app.html',import.meta.url),'utf8');
const hooks=moduleAt('hooks.server.ts',{'$lib/i18n':i18n,'@sveltejs/kit':{redirect:(status,path)=>({status,path}),error:(status,message)=>({status,message})}});
for(const raw of ['en','ru',null,'evil" onload="x']) {
    const result=await hooks.handle({event:{request:{method:'GET'},url:new URL('http://test/login'),locals:{},cookies:{get:name=>name==='ui_locale'?raw:null}},resolve:async(event,options)=>options?.transformPageChunk?options.transformPageChunk({html:template,done:true}):template});
    assert.match(result,new RegExp(`<html lang="${raw==='ru'?'ru':'en'}"`),'SSR HTML language must match validated locale, never raw cookie');
    assert.ok(!result.includes('evil'));
}
const ci=readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');
const pkg=JSON.parse(readFileSync(new URL('../package.json',import.meta.url),'utf8'));
assert.equal(pkg.scripts['test:qa-localization'],'node scripts/test-qa-localization.mjs');
assert.match(ci,/npm run test:qa-localization/);
assert.match(ci,/QA_UX=1 QA_SCENARIO=money node scripts\/test-qa-regressions-browser\.mjs/);
const page=readFileSync(new URL('../src/routes/transactions/+page.svelte',import.meta.url),'utf8');
assert.match(page,/data\.status\.kind !== 'ok' && data\.status\.kind !== 'final_page'/,'partial/error notices remain rendered');
assert.ok(page.indexOf('role={data.status.role}')<page.indexOf('<details data-technical-info'),'real notices remain before closed technical help');
const accounts=readFileSync(new URL('../src/routes/accounts/+page.svelte',import.meta.url),'utf8');
assert.match(accounts,/<details open=\{structureWarnings.length > 0\}/,'true structural warnings start expanded');
const form=readFileSync(new URL('../src/routes/transactions/new/+page.svelte',import.meta.url),'utf8');
assert.ok(form.indexOf('</details>')<form.indexOf('data.createSettings.recovery_required ||'),'recovery warning remains outside technical help');
assert.match(form,/data\.createSettings\.recovery_required \|\| data\.createSettings\.recovery\?\.required/);
console.log('QA-12 locale presets, safe SSR language, warning boundaries and CI wiring passed');
