import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
const server = readFileSync(new URL('../src/routes/transactions/new/+page.server.ts', import.meta.url), 'utf8');
const page = readFileSync(new URL('../src/routes/transactions/new/+page.svelte', import.meta.url), 'utf8');
async function load(summary, activeBook = { id: 1, base_currency: null }, status=200) {
    const exports={}; const reads=[]; const options=[];
    vm.runInNewContext(ts.transpileModule(server,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,{
        exports, URL, URLSearchParams,
        require:(name)=>{
            if(name==='$env/dynamic/private')return{env:{API_INTERNAL_URL:'http://synthetic'}};
            if(name==='@sveltejs/kit')return{redirect:(status,location)=>({status,location}),fail:(status,data)=>({status,data})};
            if(name==='$lib/api/server')return{getAuthToken:()=> 'synthetic',getActiveBookContext:async()=>({books:activeBook?[activeBook]:[],activeBook,bookPrefix:`/books/${activeBook?.id}`})};
            if(name==='$lib/i18n')return{localeFromCookie:()=> 'en'};
            if(name==='$lib/accounts/options.server')return{loadAccountOptions:async(_f,p,_t,opts)=>{options.push({p,...opts});return{items:[],available:true,limited:false,partialFailure:false,errorCode:null};}};
            throw Error(name);
        },
    });
    const fetch=async(url)=>{reads.push(url); if(url.endsWith('/reports/summary')){if(summary instanceof Error)throw summary;return{ok:status===200,status,json:async()=>summary};} return{ok:true,status:200,json:async()=>({known:true,enabled:false})};};
    const data=await exports.load({cookies:{},fetch});return{data,reads,options};
}
const ready=(currency)=>({status:'ready',reporting_currency:{status:'ready',selected_currency:currency}});
for (const currency of ['RUB','EUR','USD']) {
    const {data,reads,options}=await load(ready(currency));
    assert.equal(data.reportingCurrency,currency,'QA-08 form loader must use the same resolved currency as Summary');
    assert.equal(options[0].currency,undefined,'QA-08 inferred default must not lock selectors to that currency');
    assert.equal(options[0].purpose,'transaction_create_preview','only eligible preview account IDs');
    assert.equal(reads.filter(p=>p.endsWith('/reports/summary')).length,1);
    assert.ok(reads.every(p=>p.startsWith('http://synthetic/books/1/')));
}
for(const summary of [null, {status:'setup_required',reporting_currency:{status:'setup_required',selected_currency:null}}, ready('XXX'),ready('TOOLONG'),ready('eur'), new Error('offline')]) {
    const {data,options}=await load(summary,{id:2,base_currency:'SEK'});
    assert.equal(data.reportingCurrency,null,'unavailable/ambiguous/invalid resolution must not invent a configured fallback');
    assert.equal(options[0].currency,undefined);
}
for (const base_currency of [null,'RUB']) {
    const {data,options}=await load(ready('RUB'),{id:1,base_currency});
    assert.equal(data.reportingCurrency,'RUB');
    assert.equal(options[0].currency,undefined,'configured metadata must not lock an editable draft either');
}
const missing=await load(null,null); assert.equal(missing.data.reportingCurrency,null);assert.equal(missing.reads.length,0);assert.equal(missing.options.length,0);
await assert.rejects(load(null,undefined,401),e=>e.status===303 && e.location==='/login');
const functions=ts.createSourceFile('page.ts',page.match(/<script lang="ts">([\s\S]*?)<\/script>/)[1],ts.ScriptTarget.Latest,true).statements.filter(ts.isFunctionDeclaration).map(n=>n.getText()).join('\n');
const c=vm.createContext({data:{reportingCurrency:'RUB'},form:null});
vm.runInContext(ts.transpileModule(functions,{compilerOptions:{target:ts.ScriptTarget.ES2022}}).outputText,c);
assert.equal(vm.runInContext('initialCurrency()',c),'RUB');
for(const currency of ['EUR','USD']){c.form={payload:{currency}};assert.equal(vm.runInContext('initialCurrency()',c),currency,'returned valid explicit choice wins');}
for(const currency of ['', 'XXX','USD<script>']){c.form={payload:{currency}};assert.equal(vm.runInContext('initialCurrency()',c),'RUB');}
c.data.reportingCurrency=null;c.form=null;assert.equal(vm.runInContext('initialCurrency()',c),'');
assert.doesNotMatch(page,/base_currency \?\? 'SEK'/);
assert.match(page,/draftBookId[\s\S]*\$effect[\s\S]*initialDraftSplits\(null, data.accounts\)/,'book switch must discard private draft/account selection from previous book');
const script = page.match(/<script lang="ts">([\s\S]*?)<\/script>/)[1];
const effect = script.match(/\$effect\(\(\) => \{([\s\S]*?)\n\t\}\);/)[1];
Object.assign(c,{selectedBook:{id:1},draftBookId:undefined,date:'2026-09-01',description:'SYNTHETIC draft',currency:'USD',splits:[{account_id:'old'}],splitOrdinal:9,confirmSubmitting:true});
c.data.accounts=[{id:'new-debit'},{id:'new-credit'}];
vm.runInContext(`{${effect}}`,c);
assert.equal(c.draftBookId,1);assert.equal(c.description,'SYNTHETIC draft','initial mount preserves returned payload');
vm.runInContext(`{${effect}}`,c);assert.equal(c.currency,'USD','same book rerender preserves explicit input');
c.selectedBook={id:2};c.data.reportingCurrency='EUR';vm.runInContext(`{${effect}}`,c);
assert.equal(c.currency,'EUR');assert.equal(c.description,'');assert.equal(c.date,'');assert.equal(c.splits[0].account_id,'new-debit');assert.equal(c.splits[0].amount,'');assert.equal(c.splitOrdinal,3);assert.equal(c.confirmSubmitting,false);
c.selectedBook=null;c.data.reportingCurrency=null;c.data.accounts=[];vm.runInContext(`{${effect}}`,c);
assert.equal(c.currency,'');assert.equal(c.splits[0].account_id,'');
const switcher=readFileSync(new URL('../src/lib/components/BookSwitcher.svelte',import.meta.url),'utf8');
assert.match(switcher,/window\.location\.assign\(safeBookSelectHref\(bookId\)\)/,'QA-08 select is a server endpoint, not a Svelte page: do not goto a missing route');
assert.doesNotMatch(switcher,/goto\(/);
const switchScript=switcher.match(/<script lang="ts">([\s\S]*?)<\/script>/)[1];
const switchFunctions=ts.createSourceFile('switch.ts',switchScript,ts.ScriptTarget.Latest,true).statements.filter(ts.isFunctionDeclaration).map(n=>n.getText()).join('\n');
const navigations=[];
const switchContext=vm.createContext({window:{location:{pathname:'/transactions/new',search:'?safe=1',assign:p=>navigations.push(p)}}});
vm.runInContext(ts.transpileModule(switchFunctions,{compilerOptions:{target:ts.ScriptTarget.ES2022}}).outputText,switchContext);
vm.runInContext('handleChange({target:{value:""}})',switchContext);assert.equal(navigations.length,0);
vm.runInContext('handleChange({target:{value:"2"}})',switchContext);assert.deepEqual(navigations,['/books/2/select?next=%2Ftransactions%2Fnew%3Fsafe%3D1']);
console.log('QA-08 currency loader/default checks passed: resolver, no guessing, explicit choice, auth/unavailable, switch reset');
const ci=readFileSync(new URL('../../../.github/workflows/ci.yml',import.meta.url),'utf8');
assert.match(ci,/for scenario in money currency_eur currency_tie empty; do\s+QA_FORM_CURRENCY=1 QA_SCENARIO=/);
