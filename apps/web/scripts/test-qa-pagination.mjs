import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
const source=readFileSync(new URL('../src/routes/transactions/+page.server.ts',import.meta.url),'utf8');
const exports={};
vm.runInNewContext(ts.transpileModule(source+'\nexport {explorerStatus};',{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,{exports,URL,URLSearchParams,require:n=>n==='$lib/i18n'?{t:(_l,k)=>k}:{}});
for(const locale of ['en','ru']) {
    for(const [count,hasMore,cursor,limited,exhausted,kind,key] of [
        [12,false,'opaque',false,true,'final_page','lastPageMessage'],
        [12,false,null,false,true,'final_page','lastPageMessage'],
        [20,true,null,false,false,'ok','readyMessage'],
        [0,false,null,false,true,'true_empty','trueEmptyMessage'],
        [0,false,'opaque',false,true,'end','endMessage'],
        [0,true,'opaque',true,false,'scan_window_empty','scanWindowEmptyMessage'],
        [12,false,'opaque',true,false,'scan_limited','scanLimitedMessage'],
        [0,false,'opaque',true,true,'scan_limited','scanLimitedMessage'],
        [12,true,'opaque',false,false,'ok','readyMessage']
    ]) {
        const page={items:Array(count).fill({id:'synthetic'}),has_more:hasMore,scan:{scan_limited:limited,exhausted}};
        const result=exports.explorerStatus(page,{cursor},locale);
        assert.equal(result.kind,kind,JSON.stringify({count,hasMore,cursor,limited,exhausted}));
        assert.equal(result.message,'transactions.explorer.'+key); assert.equal(result.role,'status');
    }
}
console.log('QA-10 final/empty/scan-limited/ready page states passed (EN/RU)');
assert.match(readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8'),/QA_SCENARIO=pagination node scripts\/test-qa-regressions-browser\.mjs/);
