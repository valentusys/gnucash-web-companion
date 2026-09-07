import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const page = readFileSync(new URL('../src/routes/transactions/new/+page.svelte', import.meta.url), 'utf8');
const script = page.match(/<script lang="ts">([\s\S]*?)<\/script>/)[1];
const ast = ts.createSourceFile('page.ts', script, ts.ScriptTarget.Latest, true);
const functions = ast.statements.filter(ts.isFunctionDeclaration).map(node => node.getText(ast)).join('\n');
const messagesSource = readFileSync(new URL('../src/lib/i18n/messages.ts', import.meta.url), 'utf8');
const catalog = { exports: {} };
vm.runInNewContext(ts.transpileModule(messagesSource, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, catalog);
const messages = catalog.exports.messages;
const summary = script.match(/const errorSummary = \$derived\(([^;]+)\);/)[1];
for (const locale of ['en', 'ru']) {
    const context = vm.createContext({ locale, DEFAULT_LOCALE: 'en', messages, t: (l, key) => messages[l][key], form: undefined });
    vm.runInContext(ts.transpileModule(functions, { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText, context);
    assert.equal(vm.runInContext(summary, context), '', 'QA-07 fresh GET must not invent an error');
    context.form = { preview: {}, fieldErrors: {} };
    assert.equal(vm.runInContext(summary, context), '', 'successful preview must not invent an error');
    for (const form of [{ errorKey: 'private-unrecognized' }, { errorCode: 'UNKNOWN' }]) {
        context.form = form;
        assert.equal(vm.runInContext(summary, context), messages[locale]['transactionCreate.error.generic'], 'unknown real failure retains safe fallback');
    }
    context.form = { errorKey: 'transactionCreate.error.INVALID_DECIMAL' };
    assert.equal(vm.runInContext(summary, context), messages[locale]['transactionCreate.error.INVALID_DECIMAL']);
    assert.equal(vm.runInContext('message(undefined)', context), '');
    assert.equal(vm.runInContext('message("")', context), '');
    assert.equal(vm.runInContext('message("private-path")', context), messages[locale]['transactionCreate.error.generic']);
    for (const code of ['CREATE_DEPLOYMENT_DISABLED', 'CREATE_BOOK_DISABLED', 'CREATE_RECOVERY_REQUIRED']) {
        context.warning = { code, message_key: `transaction_create.${code.toLowerCase()}` };
        assert.equal(vm.runInContext('warningMessage(warning)', context), messages[locale][`transactionCreate.error.${code}`], 'real snake_case warning must explain the blocked condition');
    }
    context.warning = { code: 'private-path', message_key: 'transactionCreate.success.created' };
    assert.equal(vm.runInContext('warningMessage(warning)', context), messages[locale]['transactionCreate.warningUnavailable']);
}
assert.doesNotMatch(page, /t\(locale, 'transactionCreate\.success\.(?:created|already_created)'\)/, 'form must not render example success outcomes');
assert.match(page, /warningMessage\(warning\)/);
assert.match(page, /\{#if errorSummary\}[\s\S]*role="alert"/);
assert.match(page, /\{#if preview && preview\.confirm_allowed && !previewIsStale\}[\s\S]*id="confirm-create-form"/);
assert.match(page, /<WriteModeWarning compact \{locale\} role="status"/);
const warningComponent = readFileSync(new URL('../src/lib/components/WriteModeWarning.svelte', import.meta.url),'utf8');
assert.match(warningComponent, /role = 'alert'/, 'other real write-warning callers retain alert by default');
assert.match(warningComponent, /\{role\}/);
const ci = readFileSync(new URL('../../../.github/workflows/ci.yml', import.meta.url),'utf8');
assert.match(ci, /npm run test:qa-form-states/);
assert.match(ci, /QA_FORM_STATES=1 QA_SCENARIO=/);
console.log('QA-07 form states pass: fresh/preview/error/unknown/blocked warnings, EN/RU, no fake success');
