import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
const path = new URL('./qa-request-policy.mjs', import.meta.url);
assert.ok(existsSync(path), 'preview acceptance needs an exact tested non-mutation classifier');
const { isReadOnlyQaRequest } = await import(path);
for (const method of ['GET', 'HEAD', 'OPTIONS']) assert.equal(isReadOnlyQaRequest({method, path:'/books/1/transactions', search:''}, 'api'), true);
for (const [boundary, path, search] of [['browser','/login',''],['browser','/logout',''],['api','/auth/login',''],['browser','/transactions/new','?/preview'],['api','/books/1/transactions/create-preview','']]) {
    assert.equal(isReadOnlyQaRequest({method:'POST',path,search},boundary), true);
    for(const method of ['PUT','PATCH','DELETE']) assert.equal(isReadOnlyQaRequest({method,path,search},boundary),false);
}
for (const [boundary,path,search] of [['browser','/transactions/new',''],['browser','/transactions/new','?/confirm'],['browser','/transactions/new','?/preview&/confirm'],['browser','/transactions/new','?/preview=confirm'],['api','/books/1/transactions',''],['api','/books/1/transactions/create-preview/',''],['api','/books/1/transactions/create-preview','?unsafe'],['api','/books/1/transaction-create-settings',''],['browser','/auth/login',''],['api','/login',''],['api','/transactions/new','?/preview'],['api','/books/1/transactions/validate','']]) {
    assert.equal(isReadOnlyQaRequest({method:'POST',path,search},boundary), false, `${boundary} ${path}${search} must fail closed`);
}
assert.equal(isReadOnlyQaRequest({method:'POST',path:'/books/1/transactions/create-preview'},'api'),false,'missing recorded query fails closed');
assert.equal(isReadOnlyQaRequest({method:'POST',path:'/login',search:''},'unknown'),false);
console.log('read-only QA request policy passed; only explicit preview POST, never confirm/write/settings');
