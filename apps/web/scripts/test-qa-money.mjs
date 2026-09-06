import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import ts from 'typescript';
const sourceUrl = new URL('../src/lib/transactions/display-money.ts', import.meta.url);
const exports = {};
runInNewContext(ts.transpileModule(readFileSync(sourceUrl, 'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText, {exports});
const display = exports.transactionDisplayMoney;
const money = {amount:'-3.25',currency:'RUB'};
const neutral = {amount:'3.25',currency:'RUB'};
const base = {amount:'999',currency:'WRONG',representative_amount:money,matched_amount:{amount:'0.00',currency:'USD'},representative_account:{id:'a',name:'Synthetic account'},direction:{status:'composite'}};
let result = display({...base, amount_basis:'neutral_magnitude', representative_amount:neutral});
assert.deepEqual(JSON.parse(JSON.stringify(result.money)), neutral);
assert.equal(result.label,'transactions.amount.neutral');
result = display({...base, amount_basis:'selected_accounts',matched_account_ids:['a']});
assert.equal(result.money.amount,'0.00'); assert.equal(result.money.currency,'USD');
assert.equal(result.label,'transactions.amount.selectedAccount'); assert.equal(result.account,'Synthetic account');
result = display({...base, amount_basis:'selected_accounts',matched_account_ids:['a','b']});
assert.equal(result.label,'transactions.amount.selectedAccounts');
for (const type of ['income','expense']) {
 result = display({...base, amount_basis:type});
 assert.equal(result.money.amount,'0.00'); assert.equal(result.label,`transactions.amount.${type}`);
}
for (const basis of ['multiple_amounts','representative_split','unknown',undefined]) {
 result = display({...base,amount_basis:basis});
 assert.equal(result.money,null,'complex/legacy arbitrary splits cannot become a displayed amount');
}
result = display({amount:'-0.01',currency:'RUB'});
assert.equal(result.money.amount,'-0.01'); assert.equal(result.label,'transactions.amount.selectedAccount');
assert.equal(display({}).money,null);
for (const basis of ['neutral_magnitude','selected_accounts','income','expense']) {
 assert.equal(display({amount_basis:basis}).money,null,'missing explicit amount cannot fall back to arbitrary raw value');
}
for (const component of ['TransactionTable','TransactionCard']) {
 const source=readFileSync(new URL(`../src/lib/components/${component}.svelte`,import.meta.url),'utf8');
 assert.match(source,/transactionDisplayMoney\(tx\)/);
 assert.doesNotMatch(source,/representative_amount\s*\?\?|matched_amount\s*\?\?|<Money amount=\{tx.amount\}/);
 assert.match(source,/t\(locale, display.label/,'scope label must actually render');
}
console.log('QA-03 exact money presentation cases passed');
