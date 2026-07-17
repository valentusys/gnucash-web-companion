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
assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview'],
	'node scripts/test-transaction-entry-preview.mjs',
	'legacy transaction-entry static gate must keep its direct canonical script'
);
assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview-browser'],
	'npm run build && node scripts/test-transaction-entry-preview-browser.mjs',
	'legacy transaction-entry browser gate must keep the existing browser script'
);
assert.equal(
	packageJson.scripts?.['test:transaction-entry-create-disposable-browser'],
	'npm run build && node scripts/test-transaction-entry-preview-browser.mjs',
	'legacy disposable CREATE gate must keep the existing real synthetic/disposable browser drill'
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
	'transaction_create_generation?: number',
	'can_enable?: boolean',
	'blocked_codes?: string[]',
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
assert.match(server, /const SAFE_TRANSACTION_ID_RE[\s\S]*function safeOpaqueRef[\s\S]*REQUEST_REF_RE[\s\S]*RECOVERY_REF_RE/s, 'server must clamp request/recovery refs to fixed opaque formats before rendering');
assert.match(server, /function safeCreateRedirectPath[\s\S]*SAFE_TRANSACTION_ID_RE[\s\S]*target\.hash = ''[\s\S]*target\.search = ''[\s\S]*create_status/s, 'confirm success redirect must discard backend query/hash and add only trusted create_status');
assert.doesNotMatch(server, /return `\$\{target\.pathname\}\$\{target\.search\}\$\{target\.hash\}`/, 'confirm success redirect must never preserve backend query/hash');
assert.match(server, /function retryPreviewFromConfirmFailure[\s\S]*preview_token: previewToken[\s\S]*idempotency_key: idempotencyKey/s, 'retryable confirm failures must rebuild server-rendered retry state with the same token/key');
assert.match(server, /isSafeRetryableConfirmFailure[\s\S]*CREATE_IN_PROGRESS[\s\S]*BOOK_WRITE_BUSY/s, 'only typed safe retryable confirm failures may offer a mutation retry form');
assert.match(server, /result\.ok === false[\s\S]*retryPreviewFromConfirmFailure[\s\S]*preview: retryPreview/s, 'confirm failure action must preserve retry preview for safe retryable errors');
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
	'transactionCreate.addSplit',
	'transactionCreate.removeSplit',
	'transactionCreate.moveUp',
	'transactionCreate.moveDown',
	'aria-live="polite"',
	'id="running-balance"',
	'transactionCreate.balanceZero',
	'transactionCreate.splitEditorHelp',
	'transactionCreate.scopeCopy',
	'account.full_name',
	'formaction="?/preview"',
	'id="confirm-create-form"',
	'formaction="?/confirm"',
	'name="preview_token"',
	'name="idempotency_key"',
	'name="transaction_json"',
	'confirm_allowed',
	'previewIsStale',
	'transactionCreate.previewStaleTitle',
	'created',
	'already_created',
	'320px no horizontal overflow'
]) {
	assert.ok(page.includes(fragment), `transaction create page missing #59 UI fragment: ${fragment}`);
}

assert.match(page, /function decimalStringToParts[\s\S]*function scaleDecimalParts[\s\S]*BigInt[\s\S]*function decimalStringToUnits/s, 'running balance must use string/BigInt decimal logic');
assert.match(page, /function decimalStringToParts[\s\S]*function scaleDecimalParts[\s\S]*maxScale/s, 'running balance must align arbitrary decimal strings at the maximum fractional scale');
assert.doesNotMatch(page, /fraction\.length > 2|padEnd\(2|slice\(-2\)|\.00\b/, 'running balance must not hard-code a 2-decimal scale');
assert.match(page, /isKnownMessageKey[\s\S]*messages\[DEFAULT_LOCALE\][\s\S]*transactionCreate\.error\.generic/s, 'page must map backend-provided message keys through the fixed EN/RU catalog');
assert.doesNotMatch(page, /parseFloat|parseInt\([^,)]*\)|Number\(/, 'transaction money UI must not use JS numeric parsing for amounts');
assert.doesNotMatch(page, /name="note"|transaction_note/i, 'transaction note field must not be submitted');
assert.doesNotMatch(page, /localStorage|sessionStorage/, 'transaction drafts and tokens must not be stored in browser storage');
assert.match(page, /{#if preview && preview\.confirm_allowed && !previewIsStale}[\s\S]*<form id="confirm-create-form"/s, 'confirm form must be separate and shown only for non-stale confirm_allowed preview');
assert.match(page, /onsubmit=\{handleConfirmSubmit\}[\s\S]*disabled=\{confirmSubmitting\}/s, 'confirm form must disable while submitting for double-submit suppression');
assert.match(page, /function addSplit\(\)[\s\S]*splits\.length >= 50[\s\S]*disabled=\{splits\.length >= 50\}/s, 'add split control must be disabled at 50 rows in UI code');
assert.match(page, /disabled=\{splits\.length <= 2\}/s, 'remove split control must remain disabled at the 2-row lower bound');
assert.match(page, /transactionCreate\.policyTitle[\s\S]*transactionCreate\.dateLabel[\s\S]*transactionCreate\.safeResultsTitle/s, 'visible #59 labels must be catalog-backed instead of fixed English');
for (const forbiddenLiteral of [
	'CREATE policy',
	'Split editor',
	'Running balance:',
	'Draft changed after preview',
	'Normalized preview',
	'Confirm CREATE',
	'Confirm unavailable',
	'Safe result states',
	'Date',
	'Currency',
	'Description',
	'Account',
	'Amount',
	'Split memo'
]) {
	assert.ok(!page.includes(`>${forbiddenLiteral}<`) && !page.includes(`>${forbiddenLiteral}\n`), `visible literal must move to catalog: ${forbiddenLiteral}`);
}

for (const key of [
	'transactionCreate.title',
	'transactionCreate.previewSubmit',
	'transactionCreate.confirmSubmit',
	'transactionCreate.policyTitle',
	'transactionCreate.dateLabel',
	'transactionCreate.currencyLabel',
	'transactionCreate.descriptionLabel',
	'transactionCreate.splitEditorTitle',
	'transactionCreate.addSplit',
	'transactionCreate.removeSplit',
	'transactionCreate.safeResultsTitle',
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
for (const key of ['transactionCreate.policyTitle', 'transactionCreate.dateLabel', 'transactionCreate.safeResultsTitle']) {
	assert.match(messages, new RegExp(`'${key}': '[^']+'[\\s\\S]*ru: [\\s\\S]*'${key}': '[^']+'`), `message key ${key} must have EN and RU entries`);
}

assert.match(bookSettingsServer, /transaction-create-settings/s, 'book settings server must load the transaction-create settings endpoint');
assert.match(bookSettingsServer, /patchTransactionCreateSettings:\s*async[\s\S]*`\/books\/\$\{bookId\}\/transaction-create-settings`[\s\S]*'PATCH'/s, 'book settings server must PATCH only the metadata settings endpoint');
assert.doesNotMatch(bookSettingsServer, /\/transactions(?!-create-settings)/, 'book settings server must not call transaction write routes');
assert.match(bookSettingsPage, /id="transaction-create-settings"[\s\S]*\?\/patchTransactionCreateSettings/s, 'book settings page must render a visibly separate transaction-create settings form');
assert.match(bookSettingsPage, /data-normal-user-forbidden-toggle/s, 'book settings page must visibly keep normal-user toggle attempts forbidden');

console.log('ok - #59 transaction create product static guard passed');
