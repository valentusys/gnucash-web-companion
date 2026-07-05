import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

function pathOf(...segments) {
	return join(root, ...segments);
}

function read(...segments) {
	return readFileSync(pathOf(...segments), 'utf8');
}

assert.ok(existsSync(pathOf('src', 'routes', 'transactions', 'new', '+page.svelte')), '/transactions/new page route must exist');
assert.ok(existsSync(pathOf('src', 'routes', 'transactions', 'new', '+page.server.ts')), '/transactions/new server route must exist');

const packageJson = JSON.parse(read('package.json'));
const page = read('src', 'routes', 'transactions', 'new', '+page.svelte');
const server = read('src', 'routes', 'transactions', 'new', '+page.server.ts');
const transactionsList = read('src', 'routes', 'transactions', '+page.svelte');

assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview'],
	'node scripts/test-transaction-entry-preview.mjs',
	'package.json must expose npm run test:transaction-entry-preview'
);
assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview-browser'],
	'node scripts/test-transaction-entry-preview-browser.mjs',
	'package.json must expose npm run test:transaction-entry-preview-browser'
);

for (const field of [
	'book_id',
	'date',
	'debit_account_id',
	'credit_account_id',
	'amount',
	'currency',
	'description',
	'memo'
]) {
	assert.match(page, new RegExp(`name="${field}"`), `transaction-entry page must expose field: ${field}`);
}

for (const { id, label, name } of [
	{ id: 'preview-book', label: 'Book', name: 'book_id' },
	{ id: 'preview-date', label: 'Date', name: 'date' },
	{ id: 'debit-account-search', label: 'Search source account' },
	{ id: 'debit-account-select', label: 'Debit/source account', name: 'debit_account_id' },
	{ id: 'credit-account-search', label: 'Search destination account' },
	{ id: 'credit-account-select', label: 'Credit/destination account', name: 'credit_account_id' },
	{ id: 'preview-amount', label: 'Amount', name: 'amount' },
	{ id: 'preview-currency', label: 'Currency', name: 'currency' },
	{ id: 'preview-description', label: 'Description', name: 'description' },
	{ id: 'preview-memo', label: 'Memo (optional)', name: 'memo' }
]) {
	assert.match(page, new RegExp(`<label[^>]*for="${id}"[^>]*>\\s*${label.replace(/[()]/g, '\\$&')}\\s*</label>`), `${label} must have an explicit label bound to ${id}`);
	assert.match(page, new RegExp(`id="${id}"[\\s\\S]{0,360}aria-describedby=`), `${label} must expose aria-describedby linkage`);
	if (name) {
		assert.match(page, new RegExp(`id="${id}"[\\s\\S]{0,180}name="${name}"|name="${name}"[\\s\\S]{0,180}id="${id}"`), `${label} must keep the expected submitted field name`);
	}
}

for (const requiredPageFragment of [
	'Transaction entry preview',
	'Preview only / no write executed',
	'preview-no-write-warning',
	'write-session-gate',
	'Preview mode',
	'Write session not armed',
	'CREATE execution unavailable without fresh owner approval',
	'writes_enabled:',
	'session_armed:',
	'create_execution_allowed:',
	'allowed_create_count:',
	'target_class:',
	'armed-session-requirements',
	'Armed-session requirements panel (disabled placeholder)',
	'Target class required: test copy or owner-selected target only',
	'preview-reviewed checkbox alone is not enough',
	'Manual Desktop verification required for the first UI CREATE trial',
	'POST /books/&lbrace;book_id&rbrace;/transactions/create-preview',
	'No CREATE, PATCH, DELETE, or batch operation is executed',
	'debit-account-count',
	'credit-account-count',
	'visible selectable accounts',
	'account type',
	'Preview transaction',
	'Create disabled',
	'preview-create-disabled-explanation',
	'only the preview action is available',
	'type="button" disabled',
	'Normalized preview',
	'preview_only',
	'create_count',
	'Source/debit account',
	'Destination/credit account',
	'Amount + currency',
	'Create remains disabled in this slice',
	'preview-confirmation-shell',
	'Future confirmation shell',
	'Ready for future owner-approved CREATE',
	'I reviewed this local preview',
	'Future Create disabled',
	'future-create-readiness-list',
	'CREATE readiness gate: blocked',
	'Allowed CREATE count',
	'Preview-reviewed checkbox alone is not enough',
	'preview-stale-warning',
	'Draft changed after preview',
	'Clear preview / start over',
	'approval-packet',
	'Approval packet (no-write)',
	'Target book',
	'Future CREATE count',
	'Safety checklist before any future CREATE',
	'approval-packet-safety-checklist',
	'Copy redacted approval template',
	'Redacted placeholder template copied',
	'The copy button uses placeholders only',
	'no mutation',
	'md:grid-cols-2',
	'min-w-0',
	'break-words',
	'max-w-full'
]) {
	assert.ok(page.includes(requiredPageFragment), `transaction-entry page missing required fragment: ${requiredPageFragment}`);
}

assert.match(page, /<form\b[\s\S]*aria-describedby=\{describedBy\('preview-no-write-warning', 'write-session-gate', 'preview-create-disabled-explanation'/s, 'preview form must be described by no-write, write-session gate, and disabled-create explanations');
assert.match(page, /id="preview-error-summary"[\s\S]*role="alert"[\s\S]*No CREATE\/PATCH\/DELETE\/batch executed/s, 'error summary must be accessible and include no-write copy');
assert.ok(
	page.includes('id="preview-amount"') &&
		page.includes('type="text" inputmode="decimal"') &&
		page.includes('pattern="[0-9]+(\\.[0-9]+)?"'),
	'amount input must use text+decimal inputmode with a decimal-string pattern marker'
);
assert.ok(
	page.includes('id="preview-currency"') &&
		page.includes('maxlength="3"') &&
		page.includes('pattern="[A-Za-z]{3}"'),
	'currency input must stay conservative and three-letter code oriented'
);
assert.match(page, /aria-describedby="preview-create-disabled-explanation preview-no-write-warning write-session-gate"/, 'disabled Create button must be linked to its explanation, no-write warning, and write-session gate');
assert.match(page, /let draftChangedAfterPreview = \$state\(false\)/, 'preview page must track local draft changes after a successful preview');
assert.match(page, /function handleDraftChange\(\)[\s\S]*draftChangedAfterPreview = true[\s\S]*previewReviewed = false/s, 'draft changes after preview must mark the current preview stale and reset local review state');
assert.match(page, /id="preview-reviewed-confirmation"[\s\S]*type="checkbox"[\s\S]*bind:checked=\{previewReviewed\}/s, 'confirmation shell must expose a local-only preview-reviewed checkbox');
assert.match(page, /id="future-create-disabled"[\s\S]*type="button"[\s\S]*disabled/s, 'future create control in the confirmation shell must remain disabled and non-submitting');
assert.match(page, /id="approval-packet"[\s\S]*no approval is recorded[\s\S]*Future Create remains disabled/s, 'approval packet must stay no-write and cannot record approval');
assert.match(page, /safeApprovalTemplate = `[\s\S]*Target book: <selected book in web UI>[\s\S]*Source\/debit account: <selected source account>[\s\S]*Description: <description>/s, 'approval template must be placeholder-only and redacted');
assert.match(page, /navigator\.clipboard\.writeText\(safeApprovalTemplate\)/, 'copy button must copy only the safe redacted approval template');
assert.doesNotMatch(page, /clipboard\.writeText\([^)]*preview\./, 'approval template copy must not write private preview values to clipboard');
assert.match(page, /href="\/transactions\/new"[\s\S]*Clear preview \/ start over/s, 'preview panel must expose a clear-preview/start-over action without local persistence');
assert.doesNotMatch(page, /localStorage|sessionStorage/, 'preview draft safety must not persist private transaction details in browser storage');

assert.match(page, /<form\b[\s\S]*method="POST"[\s\S]*formaction="\?\/preview"[\s\S]*Preview transaction/s, 'preview form must submit through the preview action');
assert.doesNotMatch(page, /formaction="\?\/create"|Create transaction<\/button>|type="submit"[^>]*>\s*Create\b/i, 'preview page must not expose an active Create submit control');
assert.doesNotMatch(page, /write_acknowledgement|experimental-write-mode-acknowledged|writeMode\.acknowledgement|writeMode\.finalConfirm/, 'preview page must not retain final-write acknowledgement UI');

assert.match(page, /data-account-filter="debit"[\s\S]*type="search"|type="search"[\s\S]*data-account-filter="debit"/, 'source account selector must have a search/filter input');
assert.match(page, /data-account-filter="credit"[\s\S]*type="search"|type="search"[\s\S]*data-account-filter="credit"/, 'destination account selector must have a search/filter input');
assert.match(page, /free-text is never submitted as the final account reference/, 'account search text must not be represented as the submitted account value');
assert.match(page, /debit-account-search-help[\s\S]*not submitted as account text[\s\S]*credit-account-search-help/s, 'account search inputs must explain that search text is not submitted');
assert.match(page, /selectableAccounts[\s\S]*!account\.placeholder && !account\.hidden/, 'UI logic must exclude placeholder and hidden accounts from account selectors');
assert.match(page, /Placeholder\/hidden accounts are excluded/, 'UI must explain placeholder/hidden account exclusion');
assert.match(page, /Source and destination accounts must be different[\s\S]*handlePreviewSubmit/s, 'preview form must prevent same-account client submission');
assert.match(page, /disabled=\{Boolean\(currentCreditAccountId && account\.id === currentCreditAccountId && account\.id !== currentDebitAccountId\)\}/, 'source selector must disable the chosen destination account');
assert.match(page, /disabled=\{Boolean\(currentDebitAccountId && account\.id === currentDebitAccountId && account\.id !== currentCreditAccountId\)\}/, 'destination selector must disable the chosen source account');
assert.match(page, /account\.full_name[\s\S]*account\.currency/, 'account selector must show full account path and currency');
assert.match(page, /debitAccountOptions\.length[\s\S]*selectableAccounts\.length[\s\S]*creditAccountOptions\.length/s, 'account selector helpers must show filtered option counts for source and destination');
assert.match(page, /selectedDebitAccount\?\.type[\s\S]*selectedCreditAccount\?\.type/s, 'selected account summaries must include account type as well as path/currency');

assert.match(page, /Preview validation failed safely[\s\S]*No CREATE\/PATCH\/DELETE\/batch executed[\s\S]*Raw private paths, secrets, and runtime internals are not shown/s, 'preview errors must show a safe summary and no-write copy');
assert.match(page, /fieldErrors[\s\S]*aria-invalid/s, 'preview form must derive field-level errors and mark invalid fields');
assert.match(page, /noSelectableAccounts[\s\S]*No selectable accounts are available for this book/s, 'preview form must explain the no-selectable-accounts case without implying writes');
for (const fieldErrorId of [
	'preview-book-error',
	'preview-date-error',
	'preview-amount-error',
	'preview-currency-error',
	'preview-description-error',
	'preview-memo-error',
	'debit-account-error',
	'credit-account-error'
]) {
	assert.ok(page.includes(fieldErrorId), `preview form must render field-level error near field: ${fieldErrorId}`);
}
assert.ok(
	server.includes('function previewErrorDetails') &&
		server.includes('fieldErrors') &&
		server.includes('function safeMessage') &&
		server.includes('function friendlyFieldMessage') &&
		server.includes('No selectable accounts are available for this book') &&
		server.includes('Use a supported three-letter currency') &&
		server.includes('!/[\\\\/]/.test(detail)'),
	'server action must derive user-friendly field errors using safe redacted messages'
);
assert.match(server, /Preview validation failed safely\. Review the highlighted fields\. No write was executed\./, 'server action must provide a safe field-error summary fallback');

assert.ok(server.includes('apiFetch<Account[]>(fetch, `${bookPrefix}/accounts`, token)'), '/transactions/new must load accounts read-only through the active book context');
assert.ok(server.includes('accounts.filter((account) => !account.placeholder && !account.hidden)'), '/transactions/new must filter placeholder/hidden accounts server-side');
assert.match(server, /export const actions: Actions = \{\s*preview:\s*async/s, '/transactions/new must expose only a preview action');
for (const requiredServerFragment of [
	'/transactions/create-preview',
	'formToPreviewPayload',
	'debit_account_id',
	'credit_account_id',
	'No write was executed',
	'previewOnly: true',
	'type WriteSessionGate',
	'function createWriteSessionGate',
	'const sessionArmed = false',
	'const allowedCreateCount = 0',
	'const targetClass = null',
	'create_execution_allowed: false',
	'writeSessionGate: createWriteSessionGate()'
]) {
	assert.ok(server.includes(requiredServerFragment), `transaction-entry server action missing required fragment: ${requiredServerFragment}`);
}
const formActionTargets = [...page.matchAll(/formaction="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual([...new Set(formActionTargets)], ['?/preview'], 'preview page form actions must be limited to the preview action');
assert.doesNotMatch(
	server,
	/method:\s*['"`](?:PUT|PATCH|DELETE)['"`]|\/transactions\/(?:batch|import|delete|patch)|owner-writebeta|write-alpha/i,
	'/transactions/new server action must not reference mutation HTTP methods, batch/import routes, or write-beta routes'
);
assert.match(
	server,
	/fetchFn\(`\$\{apiBase\}\$\{path\}`,[\s\S]*method:\s*'POST'[\s\S]*body:\s*JSON\.stringify\(payload\)/,
	'/transactions/new server action must use the JSON POST helper only for the preview request'
);
const transactionSubmissionTargets = [...server.matchAll(/\/transactions(?:\/create-preview|\/validate)?/g)].map((match) => match[0]);
assert.deepEqual([...new Set(transactionSubmissionTargets)], ['/transactions/create-preview'], 'create-preview must be the only transaction submission target in /transactions/new server code');
assert.doesNotMatch(server, /\b(?:create|validate)\s*:\s*async/, '/transactions/new must not define active create or validate actions');
assert.doesNotMatch(server, /\/transactions\/validate|`\/books\/\$\{bookId\}\/transactions`|hasWriteAcknowledgement/, '/transactions/new must not call validate/write API paths');
assert.doesNotMatch(server, /GNUCASH_WRITES_ENABLED[\s\S]{0,160}redirect\(303, '\/transactions'\)/, '/transactions/new must remain reachable when writes are disabled');

const previewLinkIndex = transactionsList.indexOf('href="/transactions/new"');
const writesEnabledBlockIndex = transactionsList.indexOf('{#if data.writesEnabled}');
assert.notEqual(previewLinkIndex, -1, 'transactions list must link to /transactions/new');
assert.notEqual(writesEnabledBlockIndex, -1, 'transactions list must keep write-mode warning gated separately');
assert.ok(
	previewLinkIndex < writesEnabledBlockIndex,
	'transactions list preview entry point must be outside the writesEnabled-only block'
);
for (const requiredListFragment of [
	'Preview new transaction (no write)',
	'Available while writes are disabled',
	'preview-only form',
	'No CREATE/PATCH/DELETE/batch action is available.'
]) {
	assert.ok(transactionsList.includes(requiredListFragment), `transactions list missing preview-only entry copy: ${requiredListFragment}`);
}
assert.doesNotMatch(transactionsList, />\s*New transaction\s*</, 'transactions list must not label the preview entry as a normal New transaction write flow');

console.log('transaction-entry-preview-static: ok');
