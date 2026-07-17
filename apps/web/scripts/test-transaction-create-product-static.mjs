import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

function read(...segments) {
	return readFileSync(join(root, ...segments), 'utf8');
}

const packageJson = JSON.parse(read('package.json'));
const page = read('src', 'routes', 'transactions', 'new', '+page.svelte');
const server = read('src', 'routes', 'transactions', 'new', '+page.server.ts');
const types = read('src', 'lib', 'api', 'types.ts');
const messages = read('src', 'lib', 'i18n', 'messages.ts');
const bookSettingsServer = read('src', 'routes', 'books', '[bookId]', 'settings', '+page.server.ts');
const bookSettingsPage = read('src', 'routes', 'books', '[bookId]', 'settings', '+page.svelte');

assert.equal(
	packageJson.scripts?.['test:transaction-create-product-static'],
	'node scripts/test-transaction-create-product-static.mjs',
	'package.json must expose the #59 product static guard'
);
assert.equal(
	packageJson.scripts?.['test:transaction-create-product-browser'],
	'npm run build && node scripts/test-transaction-create-product-browser.mjs',
	'package.json must expose the #59 deterministic synthetic browser guard'
);

for (const fragment of [
	'TransactionCreateRequest',
	'TransactionCreateSplitRequest',
	'TransactionCreatePreviewResponse',
	'TransactionCreateConfirmResult',
	'confirm_allowed: boolean',
	'preview_token: string',
	'idempotency_key: string',
	'create_generation: number',
	'message_key: string',
	'backup_ref: string',
	'readback: {'
]) {
	assert.ok(types.includes(fragment), `typed API DTOs missing #59 fragment: ${fragment}`);
}
assert.doesNotMatch(types, /backup_path: string;/, 'frontend transaction CREATE result type must not expose backup_path');

assert.match(server, /export const actions: Actions = \{[\s\S]*preview:\s*async[\s\S]*confirm:\s*async/s, '/transactions/new must expose preview and confirm actions');
assert.match(server, /formToTransactionCreateRequest[\s\S]*splits:[\s\S]*account_id[\s\S]*amount[\s\S]*memo/s, 'server action must build the frozen transaction request DTO with splits');
assert.match(server, /apiPostJson<TransactionCreatePreviewResponse>[\s\S]*\/transactions\/create-preview/s, 'preview action must call only create-preview');
assert.match(server, /apiPostJson<TransactionCreateConfirmResult>[\s\S]*`\/books\/\$\{activeBook\.id\}\/transactions`[\s\S]*'Idempotency-Key': idempotencyKey/s, 'confirm action must call POST /transactions with Idempotency-Key from the preview');
assert.match(server, /body:\s*\{\s*preview_token: previewToken,\s*transaction\s*\}/s, 'confirm action must send {preview_token, transaction} exactly');
assert.match(server, /SUPPORTED_CREATE_MESSAGE_KEYS[\s\S]*transactionCreate\.error\.generic[\s\S]*safeMessageKey[\s\S]*SUPPORTED_CREATE_MESSAGE_KEYS\.has/s, 'server must accept only fixed transactionCreate message keys from the backend envelope');
assert.match(server, /function safeCreateRedirectPath[\s\S]*target\.origin !== 'http:\/\/frontend\.local'[\s\S]*pathname === '\/transactions'[\s\S]*pathname\.startsWith\('\/transactions\/'\)[\s\S]*searchParams\.set\('create_status'/s, 'confirm success redirect must clamp backend links to safe transaction routes');
assert.doesNotMatch(server, /detail\s*[:=]|return\s+detail|safeMessage\(detail\)/, 'server must not render arbitrary backend detail strings');
assert.doesNotMatch(server, /localStorage|sessionStorage|create_book_backup|write_lock|GnuCashWriteService|backup_path/, 'frontend server route must not persist drafts or call backend write helpers directly');

for (const fragment of [
	'id="transaction-create-form"',
	'name="date"',
	'name="description"',
	'name="currency"',
	'name="split_account_id"',
	'name="split_amount"',
	'name="split_memo"',
	'id="split-editor"',
	'Add split',
	'Remove split',
	'Move up',
	'Move down',
	'aria-live="polite"',
	'id="running-balance"',
	'Exact zero-sum',
	'2..50 split rows',
	'No transaction note field',
	'full path / type / currency',
	'formaction="?/preview"',
	'id="confirm-create-form"',
	'formaction="?/confirm"',
	'name="preview_token"',
	'name="idempotency_key"',
	'name="transaction_json"',
	'confirm_allowed',
	'previewIsStale',
	'Draft changed after preview',
	'created',
	'already_created',
	'320px no horizontal overflow'
]) {
	assert.ok(page.includes(fragment), `transaction create page missing #59 UI fragment: ${fragment}`);
}

assert.match(page, /function decimalStringToUnits[\s\S]*BigInt/s, 'running balance must use string/BigInt decimal logic');
assert.match(page, /isKnownMessageKey[\s\S]*messages\[DEFAULT_LOCALE\][\s\S]*transactionCreate\.error\.generic/s, 'page must map backend-provided message keys through the fixed EN/RU catalog');
assert.doesNotMatch(page, /parseFloat|parseInt\([^,)]*\)|Number\(/, 'transaction money UI must not use JS numeric parsing for amounts');
assert.doesNotMatch(page, /name="note"|transaction_note/i, 'transaction note field must not be submitted');
assert.doesNotMatch(page, /localStorage|sessionStorage/, 'transaction drafts and tokens must not be stored in browser storage');
assert.match(page, /{#if preview && preview\.confirm_allowed && !previewIsStale}[\s\S]*<form id="confirm-create-form"/s, 'confirm form must be separate and shown only for non-stale confirm_allowed preview');
assert.match(page, /onsubmit=\{handleConfirmSubmit\}[\s\S]*disabled=\{confirmSubmitting\}/s, 'confirm form must disable while submitting for double-submit suppression');

for (const key of [
	'transactionCreate.title',
	'transactionCreate.previewSubmit',
	'transactionCreate.confirmSubmit',
	'transactionCreate.balanceZero',
	'transactionCreate.previewStale',
	'transactionCreate.success.created',
	'transactionCreate.success.already_created',
	'transactionCreate.error.PREVIEW_STALE',
	'transactionCreate.error.BOOK_WRITE_BUSY',
	'books.transactionCreateSettingsTitle',
	'books.transactionCreateEnableAction',
	'books.transactionCreateDisableAction'
]) {
	assert.ok(messages.includes(`'${key}'`), `EN/RU catalog missing message key ${key}`);
}

assert.match(bookSettingsServer, /transaction-create-settings/s, 'book settings server must load the transaction-create settings endpoint');
assert.match(bookSettingsServer, /patchTransactionCreateSettings:\s*async[\s\S]*`\/books\/\$\{bookId\}\/transaction-create-settings`[\s\S]*'PATCH'/s, 'book settings server must PATCH only the metadata settings endpoint');
assert.doesNotMatch(bookSettingsServer, /\/transactions(?!-create-settings)/, 'book settings server must not call transaction write routes');
assert.match(bookSettingsPage, /id="transaction-create-settings"[\s\S]*\?\/patchTransactionCreateSettings/s, 'book settings page must render a visibly separate transaction-create settings form');
assert.match(bookSettingsPage, /data-normal-user-forbidden-toggle/s, 'book settings page must visibly keep normal-user toggle attempts forbidden');

console.log('ok - #59 transaction create product static guard passed');
