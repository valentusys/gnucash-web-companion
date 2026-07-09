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
const browserSmoke = read('scripts', 'test-transaction-entry-preview-browser.mjs');

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
assert.equal(
	packageJson.scripts?.['test:transaction-entry-create-disposable-browser'],
	'node scripts/test-transaction-entry-preview-browser.mjs',
	'package.json must expose npm run test:transaction-entry-create-disposable-browser as the same deterministic synthetic/disposable browser smoke'
);

for (const requiredBrowserSmokeFragment of [
	'function assertDisabledButtonInert',
	'formAttribute',
	'controls outside the preview form must not attach to or target a form',
	'form button[type="button"][disabled]',
	'post-preview Future Create',
	'reviewed Future Create',
	'stale Future Create',
	'function assertReadinessShellsRemainPending',
	'function assertPreviewOnlyRuntimeTopology',
	'transaction preview form must be present',
	'function assertMobilePreviewUx',
	'mobile viewport must not have obvious horizontal overflow',
	'mobile confirmation status must keep Future Create disabled',
	'mobile preview review cards must be visible after successful preview',
	'mobile confirmation review steps must remain no-write',
	'function assertNoMutationRequestsObserved',
	'function transactionEntryAppSubmissionSearches',
	'function assertOrdinaryBrowserCannotReachExplicitTestMode',
	'ordinary browser cannot reach explicit test-mode execution path',
	'function assertPreviewValidationFailureUi',
	'validation failure UI',
	'normal explicit test-mode query attempt',
	'evidencePacketStatuses',
	'execution-evidence-packet-plan',
	'executionResultStatuses',
	'execution-result-shell',
	'execution-result-outcome-legend',
	'Result outcome legend (disabled)',
	'Do not infer success from preview or approval copy',
	'function assertExecutionResultShellRemainsPending',
	'failure-rollback-decision-ladder',
	'Failure and rollback decision ladder (disabled)',
	'Unknown after attempted CREATE: preserve target state and require owner recovery decision',
	'disabledProbeStatuses',
	'disabled-probe-readiness-matrix',
	'function assertApprovalPacketAbsent',
	'function assertApprovalPacketControls',
	'approval packet must remain outside the preview submission form',
	'copy approval template click must not submit or call a POST endpoint',
	'copy approval template click must not call a mutation boundary endpoint',
	'approval template clipboard shim must not write more than one placeholder template',
	'stale resets approval copy status',
	'unsafe active readiness details must stay clamped out of the UI',
	'pathWithSearch',
	'function isForbiddenBrowserBoundaryRequest',
	'function assertMutationRequestPredicates',
	'synthetic API boundary must block',
	'browser boundary must block',
	'next=%2Fbooks%2F1%2Ftransactions%2Fbatch',
	"create-preview', '?next=%2Fbooks%2F1%2Ftransactions%2Fbatch",
	'createReadinessStatusCalls.length >= 1',
	'previewPayloads',
	'explicitCreatePayloads',
	'function isExplicitSyntheticCreateHarnessRequest',
	'function assertExplicitSyntheticCreateHarnessPredicateRequiresDisposableProof',
	'function productCreatePayloadFromPreview',
	'function collectReviewedApprovalEvidence',
	'function assertExplicitSyntheticCreateHarnessReviewedEvidence',
	'source: \'browser-reviewed-approval-packet\'',
	'explicit CREATE harness requires reviewed browser approval evidence from the non-stale preview UI',
	'browser smoke must capture reviewed approval evidence before explicit test-mode CREATE harness',
	'function assertExplicitSyntheticCreateHarnessRejectsUserMode',
	'missing explicit harness header',
	'non-test APP_ENV synthetic CREATE probe',
	'writes-disabled explicit CREATE probe',
	'missing synthetic/disposable proof header',
	'explicit rejected CREATE probes must not be browser-driven',
	'function buildRedactedSyntheticCreateResultPanel',
	'function assertRedactedSyntheticCreateResultPanel',
	'redacted_result_panel',
	'issue51-redacted-create-result',
	'read_back_verification',
	'backup_state',
	'audit_state',
	'reset_default_disabled_probe_summary',
	'raw_book_paths',
	'raw_amounts',
	'explicit synthetic CREATE result panel must stay redacted',
	'reset/default-disabled probe summary must cover validate/preflight/CREATE/PATCH/DELETE/batch',
	'function runExplicitSyntheticCreateHarness',
	'function runProductRouteCreateDrill',
	'productCreateDrillScript',
	'spawnSync',
	'function assertBrowserToAppToApiBoundary',
	'function assertDisposableSyntheticApiTargetBoundary',
	'x-issue51-explicit-test-create',
	'x-issue51-synthetic-disposable-proof',
	'explicit_test_mode=issue51',
	'product CREATE route remains forbidden without explicit synthetic test harness',
	'explicit product-route CREATE drill must succeed through the backend product route',
	'explicit harness must not be browser-driven or activate default UI',
	'default/user-mode product CREATE route must be probed only by explicit Node harness and remain blocked',
	'browser-to-app boundary must not call synthetic API origin directly',
	'synthetic API must not receive requests for non-disposable book targets',
	'create-preview payload must contain only preview API fields',
	'browser must not issue CREATE/PATCH/DELETE/batch/validate/preflight/backup/audit/write-beta boundary requests',
	'synthetic API stub must observe zero validate/preflight/backup/audit/write-beta boundary requests',
	'function buildRedactedSyntheticFailureUiDrillPanels',
	'function assertRedactedSyntheticFailureUiDrillPanels',
	'function assertFailureUiDrillMatrix',
	'redacted_failure_ui_drills',
	'api_result_shaped_redacted_ui_evidence',
	'stale_preview_rejection',
	'target_preflight_rejection',
	'writes_disabled_rejection',
	'backup_failure',
	'lock_failure',
	'read_back_failure',
	'reset_probe_failure',
	'safe_recovery_copy',
	'failure drill evidence must stay redacted and fail closed'
]) {
	assert.ok(browserSmoke.includes(requiredBrowserSmokeFragment), `browser smoke missing required coverage marker: ${requiredBrowserSmokeFragment}`);
}
assert.match(browserSmoke, /\(\?:backups\?\|audit\|write-alpha\|owner-writebeta\)/, 'browser smoke must treat backup/audit/write-beta requests as forbidden boundary calls');
assert.match(browserSmoke, /isForbiddenBrowserBoundaryRequest[\s\S]*backups\?[\s\S]*audit[\s\S]*write-alpha[\s\S]*owner-writebeta/, 'browser smoke must reject browser-observed backup/audit/write-beta boundary requests');
assert.match(browserSmoke, /forbiddenBrowserMutationRequests[\s\S]*isForbiddenBrowserBoundaryRequest/, 'browser smoke forbidden request collector must use the shared browser boundary predicate');
assert.match(browserSmoke, /isForbiddenBrowserBoundaryRequest[\s\S]*validate[\s\S]*preflight[\s\S]*batch/, 'browser smoke must reject browser-observed validate/preflight/batch transaction boundaries');
assert.match(browserSmoke, /url\.search === '\?\/preview'/, 'browser smoke must allow only the exact ?/preview app submission target');
assert.match(browserSmoke, /mentionsTransactions[\s\S]*%2Ftransactions[\s\S]*next=%2Fbooks%2F1%2Ftransactions%2Fbatch/, 'browser smoke must reject encoded mutation route queries as boundary requests');
assert.match(browserSmoke, /assertMutationRequestPredicates[\s\S]*POST[\s\S]*\/books\/1\/transactions[\s\S]*PATCH[\s\S]*DELETE[\s\S]*backups[\s\S]*audit[\s\S]*owner-writebeta/, 'browser smoke must unit-check synthetic API mutation blocking predicates');
assert.match(browserSmoke, /isForbiddenTransactionMutation\(method, pathname, search = ''\)[\s\S]*querySmugglesMutationBoundary[\s\S]*transactions\(\?:\\\/\|%2F\)\(\?!create-preview/, 'synthetic API boundary must reject query-smuggled mutation routes while preserving exact create-preview');
assert.match(browserSmoke, /assertNoMutationRequestsObserved[\s\S]*request\.search \?\? ''/, 'browser smoke repeated mutation-boundary checks must include synthetic API query strings');
assert.match(browserSmoke, /create-preview', '\?next=%2Fbooks%2F1%2Ftransactions%2Fbatch/, 'browser smoke must unit-check query-smuggled API create-preview mutation boundaries');
assert.match(browserSmoke, /\?\/preview&next=%2Fbooks%2F1%2Ftransactions%2Fbatch/, 'browser smoke must reject smuggled mutation routes even when ?/preview appears in the query');
assert.match(browserSmoke, /isExplicitSyntheticCreateHarnessRequest[\s\S]*\/books\/1\/transactions[\s\S]*explicitSyntheticCreateHarnessSearch[\s\S]*x-issue51-explicit-test-create[\s\S]*x-issue51-synthetic-disposable-proof[\s\S]*x-app-env[\s\S]*x-gnucash-writes-enabled/, 'explicit synthetic CREATE harness must be header-gated, disposable-proof-gated, and product-route shaped');
assert.match(browserSmoke, /assertExplicitSyntheticCreateHarnessPredicateRequiresDisposableProof[\s\S]*\/books\/2\/transactions[\s\S]*missing synthetic\/disposable proof header[\s\S]*next=%2Fbooks%2F2%2Ftransactions%2Fbatch/s, 'explicit synthetic CREATE harness predicate must reject non-disposable targets, missing proof, and query-smuggled mutation routes');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*isForbiddenTransactionMutation\('POST', '\/books\/1\/transactions', ''\)[\s\S]*product CREATE route remains forbidden without explicit synthetic test harness[\s\S]*runProductRouteCreateDrill\(productCreatePayload\)/, 'explicit synthetic CREATE harness must prove default CREATE remains blocked before using the backend product-route drill');
assert.match(browserSmoke, /productCreatePayloadFromPreview[\s\S]*splits[\s\S]*account_id: previewPayload\.debit_account_id[\s\S]*amount: `-\$\{previewPayload\.amount\}`[\s\S]*account_id: previewPayload\.credit_account_id/, 'explicit synthetic CREATE harness must derive a product CREATE payload from the preview payload');
assert.match(browserSmoke, /assertExplicitSyntheticCreateHarnessRejectsUserMode[\s\S]*missing explicit harness header[\s\S]*missing synthetic\/disposable proof header[\s\S]*non-test APP_ENV synthetic CREATE probe[\s\S]*writes-disabled explicit CREATE probe[\s\S]*response\.status, 409[\s\S]*explicit rejected CREATE probes must not be browser-driven/, 'explicit synthetic CREATE harness must actively reject user-mode, missing-proof, or partially armed CREATE probes');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*assertExplicitSyntheticCreateHarnessReviewedEvidence\(reviewedApprovalEvidence\)[\s\S]*productCreatePayloadFromPreview\(previewPayload\)[\s\S]*assertExplicitSyntheticCreateHarnessRejectsUserMode\(api, browserRequests, productCreatePayload\)[\s\S]*runProductRouteCreateDrill\(productCreatePayload\)/, 'explicit synthetic CREATE harness must require reviewed approval evidence and run rejection probes before invoking the backend product-route drill');
assert.match(browserSmoke, /reviewedApprovalEvidence = await collectReviewedApprovalEvidence\(cdp, 'reviewed preview'\)[\s\S]*assertNoMutationRequestsObserved\(api, browserRequests, 'reviewed preview'\)[\s\S]*runExplicitSyntheticCreateHarness\(api, browserRequests, previewPayload, reviewedApprovalEvidence\)/, 'browser smoke must capture reviewed approval evidence before the explicit synthetic CREATE harness');
assert.match(browserSmoke, /function buildRedactedSyntheticCreateResultPanel\(\)[\s\S]*redacted_result_panel[\s\S]*create_count: 1[\s\S]*fixture_scope[\s\S]*private_or_only_copy_target: false[\s\S]*read_back_verification[\s\S]*backup_state[\s\S]*audit_state[\s\S]*reset_default_disabled_probe_summary/s, 'explicit synthetic CREATE harness must build a redacted result panel with fixture proof, count, read-back, backup/audit, and reset/probe summary');
assert.match(browserSmoke, /function assertRedactedSyntheticCreateResultPanel[\s\S]*syntheticDescription[\s\S]*syntheticMemo[\s\S]*syntheticAmount[\s\S]*explicit synthetic CREATE result panel must stay redacted/s, 'explicit synthetic CREATE result panel assertions must reject private/raw-like payload values');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*const responseBody = runProductRouteCreateDrill\(productCreatePayload\)[\s\S]*assertRedactedSyntheticCreateResultPanel\(responseBody, productCreatePayload, reviewedApprovalEvidence\)/s, 'explicit synthetic CREATE harness must assert the redacted result panel returned from the backend product-route drill');
assert.match(browserSmoke, /payload\.amount === validationFailureAmount[\s\S]*loc: \['body', 'amount'\][\s\S]*msg: 'amount must be positive'/s, 'browser smoke must drive failure UI through the preview endpoint, not a mutation endpoint');
assert.match(browserSmoke, /function assertPreviewValidationFailureUi[\s\S]*Preview validation failed safely[\s\S]*No CREATE\\\/PATCH\\\/DELETE\\\/batch executed[\s\S]*Future Create control must remain absent until a successful preview/s, 'browser smoke must assert safe failure UI before continuing');
assert.match(browserSmoke, /function assertOrdinaryBrowserCannotReachExplicitTestMode[\s\S]*transactionEntryAppSubmissionSearches[\s\S]*'\?\/preview'[\s\S]*request\.path === '\/books\/1\/transactions'[\s\S]*ordinary browser cannot reach explicit test-mode execution path/s, 'browser smoke must prove ordinary browser submissions cannot reach the explicit test-mode execution path');
assert.match(browserSmoke, /Page\.navigate', \{ url: `\$\{webBase\}\/transactions\/new\?explicit_test_mode=issue51` \}[\s\S]*normal explicit test-mode query attempt[\s\S]*assertOrdinaryBrowserCannotReachExplicitTestMode/s, 'browser smoke must attempt an ordinary explicit_test_mode query and still submit only preview');
assert.match(browserSmoke, /transactionEntryAppSubmissionSearches\(browserRequests\)[\s\S]*\['\?\/preview', '\?\/preview', '\?\/preview'\][\s\S]*including failure and explicit-mode query attempts/s, 'browser smoke must prove every ordinary transaction-entry POST targets only ?/preview');

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
	'Back to transactions list',
	'aria-label="Back to transactions list; no draft is saved"',
	'transaction-entry-workflow-nav',
	'Preview workflow',
	'1. Confirm no-write boundary',
	'2. Enter details',
	'3. Run preview',
	'4. Review disabled Future Create',
	'href="#transaction-preview-form"',
	'href="#normalized-preview"',
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
	'target-preflight-readiness',
	'Target preflight required',
	'Target readiness not checked',
	'UI/status shell only',
	'target_preflight.required:',
	'target_preflight.status:',
	'target_preflight.target_class:',
	'target-preflight-checklist',
	'Default state: all target readiness checks are pending / not checked / not armed',
	'Target class selected',
	'Target file exists/readable',
	'Target is outside repo',
	'GnuCash Desktop closed',
	'No concurrent writer/lock',
	'No .LCK/.LNK lock',
	'No Syncthing conflict copy before session if applicable',
	'Independent backup exists',
	'Restore proof available',
	'Reviewed non-stale preview',
	'Exact CREATE count = 1',
	'Writes reset/disabled probes required after session',
	'Manual Desktop verification required',
	'Future Create remains disabled until target preflight is passed',
	'execution-readiness-shell',
	'Backup/read-back/audit/reset/probes required',
	'Execution readiness not checked',
	'non-mutating readiness shell only',
	'execution_readiness.required:',
	'execution_readiness.status:',
	'backup_state:',
	'read_back_state:',
	'audit_state:',
	'reset_state:',
	'probe_state:',
	'execution-readiness-checklist',
	'Default state: backup, read-back, audit, reset, and probe readiness are pending / not checked / not armed',
	'Independent backup plan required',
	'Backup readable copy proof required',
	'Post-CREATE read-back required',
	'Redacted audit evidence required',
	'Writes reset to disabled required',
	'Disabled CREATE probe required',
	'Disabled validate/preflight probes required',
	'Disabled PATCH/DELETE/batch probes required',
	'execution-evidence-packet-plan',
	'Future evidence packet plan (pending)',
	'Default state: route backup, read-back, audit, reset, disabled-probe, and Desktop-verification evidence are pending and not collected',
	'execution-evidence-packet-list',
	'Backup evidence captured before CREATE',
	'Read-back evidence captured after CREATE',
	'Redacted audit evidence captured after CREATE',
	'Write-disable reset evidence captured',
	'Disabled-probe evidence captured after reset',
	'Manual Desktop verification evidence captured',
	'disabled-probe-readiness-matrix',
	'Disabled-write probe matrix (pending)',
	'Default state: validate/preflight/CREATE/PATCH/DELETE/batch probes are pending and not executed',
	'disabled-probe-readiness-list',
	'Validate probe after reset',
	'Preflight probe after reset',
	'CREATE probe after reset',
	'PATCH probe after reset',
	'DELETE probe after reset',
	'Batch probe after reset',
	'blocked_or_unavailable',
	'Manual Desktop verification record required',
	'execution-result-shell',
	'Execution-result UX shell (not run)',
	'Default state: no execution result exists, no success or failure result is claimed, and rollback/restore is not run',
	'execution-result-outcome-legend',
	'Result outcome legend (disabled)',
	'Do not infer success from preview or approval copy',
	'execution-result-triage-panel',
	'Disabled result triage',
	'Current state: no CREATE execution attempted; preview data is not a success result',
	'Success requires redacted CREATE reference and private read-back before any success copy',
	'Failure state keeps success blocked until a safe error is translated',
	'Rollback state remains owner-approved recovery only and is not run from this page',
	'Post-result reset/probe state stays pending until GNUCASH_WRITES_ENABLED=false is verified',
	'failure-rollback-decision-ladder',
	'Failure and rollback decision ladder (disabled)',
	'Stop before CREATE: show failure, keep success blocked, no rollback needed',
	'Unknown after attempted CREATE: preserve target state and require owner recovery decision',
	'Confirmed failed/no mutation: safe redacted error only; no success claim',
	'Confirmed mutated but rejected by post-checks: owner-approved restore decision before retry',
	'After any result: reset writes disabled and run disabled probes before reporting completion',
	'execution_result.status',
	'create_result_state',
	'success_state',
	'failure_state',
	'rollback_state',
	'execution-result-step-list',
	'Success result: CREATE reference recorded',
	'Success result: read-back verified',
	'Failure result: safe error translated',
	'Failure result: no success claim emitted',
	'Rollback result: restore decision recorded',
	'Post-result disabled probes verified',
	'redacted-create-result-contract',
	'Explicit synthetic CREATE result panel contract (inactive)',
	'create_count: pending',
	'read-back verification: pending',
	'backup_state: pending',
	'audit_state: pending',
	'reset/default-disabled probes: pending',
	'No raw book paths, account names, descriptions, memos, amounts, GUIDs, screenshots, tokens, or secrets',
	'Rollback is a future owner-approved recovery path only',
	'Rollback/restore: owner-approved recovery path only',
	'Future Create remains disabled until backup/read-back/audit/reset/probes readiness and execution-result reporting are completed',
	'failure-ui-drill-matrix',
	'Failure UI drills (redacted / fail-closed)',
	'failure-ui-drill-list',
	'stale_preview_rejection',
	'Target preflight rejection',
	'Writes-disabled rejection',
	'Backup failure',
	'Lock failure',
	'Read-back failure',
	'Reset/probe failure',
	'Safe recovery copy',
	'Failure drill evidence shape',
	'api_result_shaped_redacted_ui_evidence',
	'No raw target paths, backup paths, account names, descriptions, memos, amounts, GUIDs, screenshots, tokens, or secrets',
	'preview-reviewed checkbox alone is not enough',
	'Manual Desktop verification required for the first UI CREATE trial',
	'POST /books/&lbrace;book_id&rbrace;/transactions/create-preview',
	'No CREATE, PATCH, DELETE, or batch operation is executed',
	'preview-error-jump-list',
	'Preview field errors',
	'Jump to fields to fix:',
	'mobile-preview-path-card',
	'Mobile preview path',
	'Tap Preview transaction; this is the only submitting action',
	'The form stays preview-only and no-write on mobile',
	'preview-mobile-action-bar',
	'sticky bottom-0',
	'w-full rounded-xl px-4 py-2 font-semibold sm:w-auto',
	'debit-account-count',
	'credit-account-count',
	'visible selectable accounts',
	'debit-account-empty-filter',
	'No source accounts match this filter',
	'credit-account-empty-filter',
	'No destination accounts match this filter',
	'the filter is local UI only and no write was executed',
	'account type',
	'Preview transaction',
	'Create disabled',
	'preview-create-disabled-explanation',
	'only the preview action is available',
	'type="button" disabled',
	'Normalized preview',
	'preview_only',
	'create_count',
	'mobile-confirmation-status-card',
	'Mobile confirmation status',
	'mobile-preview-review-cards',
	'Mobile preview review',
	'Key normalized fields are repeated here for thumb-first review',
	'Review disabled confirmation shell',
	'Open placeholder approval packet',
	'mobile-confirmation-review-steps',
	'Mobile confirmation checklist',
	'Local checkbox does not submit, arm, or approve CREATE',
	'Preview state',
	'Current non-mutating preview response ready for local review',
	'Future Create: disabled',
	'Exact count 1 is informational only',
	'Copy helper: placeholders only',
	'Next safe action: review fields below',
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
	'redacted-create-readiness-state',
	'Redacted read-only readiness state',
	'writes_enabled status',
	'session_armed status',
	'allowed_create_count status',
	'target status',
	'preflight status',
	'backup status',
	'allowed execution status',
	'no mutation',
	'md:grid-cols-2',
	'min-w-0',
	'break-words',
	'max-w-full'
]) {
	assert.ok(page.includes(requiredPageFragment), `transaction-entry page missing required fragment: ${requiredPageFragment}`);
}

assert.match(page, /<form\b[\s\S]*aria-describedby=\{describedBy\('preview-no-write-warning', 'write-session-gate', 'target-preflight-readiness', 'execution-readiness-shell', 'execution-result-shell', 'preview-create-disabled-explanation'/s, 'preview form must be described by no-write, write-session gate, target preflight, execution readiness, execution result, and disabled-create explanations');
assert.match(page, /id="preview-error-summary"[\s\S]*role="alert"[\s\S]*No CREATE\/PATCH\/DELETE\/batch executed/s, 'error summary must be accessible and include no-write copy');
assert.match(page, /const fieldErrorLinks = \$derived[\s\S]*field: 'credit_account_id'[\s\S]*href: '#credit-account-select'[\s\S]*field: 'amount'[\s\S]*href: '#preview-amount'/s, 'preview field errors must build safe in-page jump links for mobile correction');
assert.match(page, /id="preview-error-jump-list"[\s\S]*aria-label="Preview field errors"[\s\S]*Jump to fields to fix:[\s\S]*href=\{item.href\}/s, 'preview error summary must render a field-level jump list without adding submission targets');
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
assert.match(page, /aria-describedby="preview-create-disabled-explanation preview-no-write-warning write-session-gate target-preflight-readiness execution-readiness-shell execution-result-shell"/, 'disabled Create button must be linked to its explanation, no-write warning, write-session gate, target preflight, execution readiness, and execution result');
assert.match(page, /let draftChangedAfterPreview = \$state\(false\)/, 'preview page must track local draft changes after a successful preview');
assert.match(page, /function handleDraftChange\(\)[\s\S]*draftChangedAfterPreview = true[\s\S]*previewReviewed = false/s, 'draft changes after preview must mark the current preview stale and reset local review state');
assert.match(page, /id="preview-reviewed-confirmation"[\s\S]*type="checkbox"[\s\S]*bind:checked=\{previewReviewed\}/s, 'confirmation shell must expose a local-only preview-reviewed checkbox');
assert.match(page, /id="future-create-disabled"[\s\S]*type="button"[\s\S]*disabled/s, 'future create control in the confirmation shell must remain disabled and non-submitting');
const previewFormStartIndex = page.indexOf('<form id="transaction-preview-form"');
const previewFormEndIndex = page.indexOf('</form>');
assert.notEqual(previewFormStartIndex, -1, 'transaction preview form must have the expected stable id');
assert.ok(previewFormEndIndex > previewFormStartIndex, 'transaction preview form must have a bounded source block');
const previewFormSource = page.slice(previewFormStartIndex, previewFormEndIndex + '</form>'.length);
const pageOutsidePreviewForm = page.slice(0, previewFormStartIndex) + page.slice(previewFormEndIndex + '</form>'.length);
const formTags = [...page.matchAll(/<form\b[^>]*>/g)].map((match) => match[0]);
assert.equal(formTags.length, 1, 'transaction-entry page must keep exactly one form: the preview form');
assert.match(formTags[0], /id="transaction-preview-form"/, 'the only form must be the transaction preview form');
assert.match(formTags[0], /method="POST"/, 'the preview form must be the only POSTing form');
assert.doesNotMatch(formTags[0], /\baction=/, 'the preview form must not set a page-level action target');
assert.doesNotMatch(formTags[0], /\bformaction=/, 'form-level source must not smuggle a secondary submission target');
const formActionAssignments = [...page.matchAll(/\bformaction\s*=\s*(?:"([^"]*)"|'([^']*)'|\{([^}]*)\})/g)].map((match) => match[1] ?? match[2] ?? `{${match[3]}}`);
assert.deepEqual(formActionAssignments, ['?/preview'], 'the entire transaction-entry page must expose exactly one literal formaction target: ?/preview');
assert.doesNotMatch(pageOutsidePreviewForm, /<(?:input|select|textarea|button)\b[^>]*\bname="/s, 'controls outside the preview form must not submit named values');
assert.doesNotMatch(pageOutsidePreviewForm, /<(?:button|input)\b[^>]*\b(?:form|formaction)="/s, 'controls outside the preview form must not attach to or target a form');
assert.doesNotMatch(pageOutsidePreviewForm, /\bformaction\s*=/, 'controls outside the preview form must not define any static or dynamic formaction target');
const submittedFieldNames = [...previewFormSource.matchAll(/\bname="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(
	[...new Set(submittedFieldNames)].sort(),
	['amount', 'book_id', 'credit_account_id', 'currency', 'date', 'debit_account_id', 'description', 'memo'].sort(),
	'preview form must submit only the bounded create-preview payload fields plus book_id'
);
for (const forbiddenFormField of [
	'previewReviewed',
	'approvalTemplateCopied',
	'writeSessionGate',
	'targetPreflight',
	'executionReadiness',
	'executionResult',
	'evidence_packet_plan',
	'disabled_probe_plan',
	'create_execution_allowed',
	'allowed_create_count',
	'target_class',
	'session_armed',
	'write_acknowledgement'
]) {
	assert.ok(!submittedFieldNames.includes(forbiddenFormField), `preview form must not submit local-only/future-create field: ${forbiddenFormField}`);
}
const futureCreateIndex = page.indexOf('id="future-create-disabled"');
assert.ok(previewFormEndIndex > 0 && futureCreateIndex > previewFormEndIndex, 'Future Create disabled control must remain outside the preview submission form');
const futureCreateButton = page.match(/<button\b(?=[^>]*id="future-create-disabled")(?=[^>]*type="button")(?=[^>]*disabled)[^>]*>/s)?.[0] ?? '';
assert.ok(futureCreateButton, 'Future Create disabled button must be statically present');
assert.doesNotMatch(futureCreateButton, /\b(?:form|formaction|name|value)=/, 'Future Create disabled button must not define submitted attributes or attach to a form');
assert.doesNotMatch(futureCreateButton, /\b(?:onclick|onsubmit|onmousedown|onmouseup|onkeydown|onkeyup|onpointerdown|onpointerup|on:click|on:submit)\s*=/, 'Future Create disabled button must not define event handlers');
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
assert.match(page, /id="debit-account-search"[\s\S]{0,420}debitAccountSearchEmpty && 'debit-account-empty-filter'/s, 'source account search must announce an empty filtered result');
assert.match(page, /id="credit-account-search"[\s\S]{0,420}creditAccountSearchEmpty && 'credit-account-empty-filter'/s, 'destination account search must announce an empty filtered result');
assert.match(page, /debitAccountSearchEmpty[\s\S]*No source accounts match this filter[\s\S]*No destination accounts match this filter/s, 'empty account-filter copy must keep users oriented without implying writes');
assert.match(page, /id="debit-account-select"[\s\S]{0,520}debitAccountSearchEmpty && 'debit-account-empty-filter'/s, 'source account select must be described by the local empty-filter status when shown');
assert.match(page, /id="credit-account-select"[\s\S]{0,520}creditAccountSearchEmpty && 'credit-account-empty-filter'/s, 'destination account select must be described by the local empty-filter status when shown');
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
assert.match(server, /function createTargetPreflight\(\)[\s\S]*required: true[\s\S]*status: 'not_checked'[\s\S]*target_class: targetClass[\s\S]*status: 'pending'/s, 'server target preflight shell must default to required/not_checked/pending');
assert.match(server, /function createExecutionReadiness\(\)[\s\S]*required: true[\s\S]*status: 'not_checked'[\s\S]*backup_state: 'pending'[\s\S]*read_back_state: 'pending'[\s\S]*audit_state: 'pending'[\s\S]*reset_state: 'pending'[\s\S]*probe_state: 'pending'[\s\S]*status: 'pending'/s, 'server execution readiness must default to required/not_checked/pending');
assert.match(server, /function createExecutionReadiness\(\)[\s\S]*evidence_packet_plan: \[[\s\S]*id: 'backup_before_create_evidence'[\s\S]*id: 'read_back_after_create_evidence'[\s\S]*id: 'audit_after_create_evidence'[\s\S]*id: 'reset_disabled_evidence'[\s\S]*id: 'disabled_probes_after_reset_evidence'[\s\S]*id: 'desktop_verification_evidence'/s, 'server execution readiness must include an explicit pending evidence packet plan');
assert.match(server, /function createExecutionReadiness\(\)[\s\S]*disabled_probe_plan: \[[\s\S]*id: 'validate_probe_after_reset'[\s\S]*id: 'preflight_probe_after_reset'[\s\S]*id: 'create_probe_after_reset'[\s\S]*id: 'patch_probe_after_reset'[\s\S]*id: 'delete_probe_after_reset'[\s\S]*id: 'batch_probe_after_reset'/s, 'server execution readiness must include an explicit pending disabled-probe plan');
assert.match(server, /function createExecutionResult\(\)[\s\S]*status: 'not_executed'[\s\S]*create_result_state: 'blocked'[\s\S]*success_state: 'pending'[\s\S]*failure_state: 'pending'[\s\S]*rollback_state: 'not_run'/s, 'server execution result shell must default to not_executed/blocked/pending/not_run');
assert.match(server, /function createExecutionResult\(\)[\s\S]*id: 'success_create_ref_recorded'[\s\S]*id: 'success_read_back_verified'[\s\S]*id: 'failure_error_translated'[\s\S]*id: 'failure_no_success_claim'[\s\S]*id: 'rollback_decision_recorded'[\s\S]*id: 'post_result_disabled_probes_verified'/s, 'server execution result shell must include pending success, failure, rollback, and post-result steps');
assert.match(page, /id="redacted-create-result-contract"[\s\S]*Explicit synthetic CREATE result panel contract \(inactive\)[\s\S]*create_count: pending[\s\S]*read-back verification: pending[\s\S]*backup_state: pending[\s\S]*audit_state: pending[\s\S]*reset\/default-disabled probes: pending/s, 'transaction-entry page must show the inactive redacted result-panel contract without executing CREATE');
assert.match(page, /id="redacted-create-result-contract"[\s\S]*No raw book paths, account names, descriptions, memos, amounts, GUIDs, screenshots, tokens, or secrets/s, 'redacted result-panel contract must state that raw/private evidence is forbidden');
assert.match(page, /id="failure-ui-drill-matrix"[\s\S]*stale_preview_rejection[\s\S]*target_preflight_rejection[\s\S]*writes_disabled_rejection[\s\S]*backup_failure[\s\S]*lock_failure[\s\S]*read_back_failure[\s\S]*reset_probe_failure[\s\S]*safe_recovery_copy/s, 'transaction-entry page must render every issue #51 failure drill state as redacted UI evidence');
assert.match(page, /id="failure-ui-drill-matrix"[\s\S]*Failure drill evidence shape[\s\S]*api_result_shaped_redacted_ui_evidence[\s\S]*No raw target paths, backup paths, account names, descriptions, memos, amounts, GUIDs, screenshots, tokens, or secrets/s, 'failure drill matrix must describe redacted API-result-shaped evidence and forbid raw/private values');
assert.doesNotMatch(page, /data-failure-drill-status="(?:success|passed|ready|ok)"/, 'failure drill matrix must not mark failures as successful or ready');
assert.match(browserSmoke, /function buildRedactedSyntheticFailureUiDrillPanels[\s\S]*stale_preview_rejection[\s\S]*target_preflight_rejection[\s\S]*writes_disabled_rejection[\s\S]*backup_failure[\s\S]*lock_failure[\s\S]*read_back_failure[\s\S]*reset_probe_failure[\s\S]*safe_recovery_copy/s, 'browser smoke must build API-result-shaped redacted failure drill panels for all required failure states');
assert.match(browserSmoke, /function assertRedactedSyntheticFailureUiDrillPanels[\s\S]*raw_target_paths[\s\S]*raw_backup_paths[\s\S]*raw_amounts[\s\S]*failure drill evidence must stay redacted and fail closed/s, 'browser smoke must reject raw/private values in failure drill evidence');
assert.match(browserSmoke, /function assertFailureUiDrillMatrix[\s\S]*failure-ui-drill-matrix[\s\S]*data-failure-drill[\s\S]*safe_recovery_copy/s, 'browser smoke must assert browser-visible failure drill matrix');
assert.doesNotMatch(page, /data-preflight-status="(?:checked|passed|ready|ok)"/, 'target preflight UI must not mark any default check as checked/passed/ready');
assert.doesNotMatch(page, /data-execution-readiness-status="(?:checked|passed|ready|ok)"/, 'execution readiness shell must not mark any default check as checked/passed/ready');
assert.doesNotMatch(page, /data-execution-evidence-status="(?:checked|passed|ready|ok)"/, 'execution evidence packet plan must not mark any default evidence step as checked/passed/ready');
assert.doesNotMatch(page, /data-disabled-probe-status="(?:checked|passed|ready|ok)"/, 'disabled-probe matrix must not mark any default probe as checked/passed/ready');
assert.doesNotMatch(page, /data-execution-result-status="(?:checked|passed|ready|ok|success|failed|rolled_back)"/, 'execution-result shell must not mark any default result step as checked/passed/ready/success/failed/rolled_back');
assert.doesNotMatch(server, /status:\s*['"](?:checked|passed|ready|ok)['"]/, 'server target preflight/readiness shells must not produce passed readiness by default');
assert.doesNotMatch(server, /from ['"]node:fs|existsSync|readFileSync|statSync|accessSync|create_book_backup|write_lock_service|_open_piecash_book_for_write|GnuCashWriteService/, 'target preflight shell must not probe files/books or call backup/lock/write helpers');

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
	'status.readiness_state.session_armed.armed',
	'status.readiness_state.allowed_create_count.count',
	'status.readiness_state.target.target_class',
	'create_execution_allowed: status.readiness_state.allowed_execution.allowed',
	'createReadinessStatus',
	'apiGetOptional<unknown>',
	'function sanitizeCreateReadinessStatus',
	'sanitizeCreateReadinessStatus(rawCreateReadinessStatus, defaultReadinessStatus)',
	'/transactions/create-readiness-status',
	'writeSessionGate: createWriteSessionGate(createReadinessStatus)',
	'type TargetPreflight',
	'function createTargetPreflight',
	"required: true",
	"status: 'not_checked'",
	"id: 'target_file_exists_readable'",
	"id: 'target_outside_repo'",
	"id: 'desktop_closed'",
	"id: 'no_concurrent_writer_lock'",
	"id: 'no_lck_lnk'",
	"id: 'no_syncthing_conflict_before'",
	"id: 'independent_backup_exists'",
	"id: 'restore_proof_available'",
	"id: 'reviewed_non_stale_preview'",
	"id: 'exact_create_count_one'",
	"id: 'reset_disabled_probes_required'",
	"id: 'manual_desktop_verification_required'",
	'targetPreflight: createTargetPreflight()',
	'type ExecutionReadiness',
	'type ExecutionEvidencePacketStep',
	'type DisabledProbePlanCheck',
	'evidence_packet_plan: ExecutionEvidencePacketStep[]',
	'disabled_probe_plan: DisabledProbePlanCheck[]',
	'function createExecutionReadiness',
	"backup_state: 'pending'",
	"read_back_state: 'pending'",
	"audit_state: 'pending'",
	"reset_state: 'pending'",
	"probe_state: 'pending'",
	"id: 'backup_plan_required'",
	"id: 'backup_readable_copy_required'",
	"id: 'post_create_read_back_required'",
	"id: 'redacted_audit_required'",
	"id: 'writes_reset_required'",
	"id: 'disabled_create_probe_required'",
	"id: 'disabled_validate_preflight_probe_required'",
	"id: 'disabled_patch_delete_batch_probes_required'",
	"id: 'manual_desktop_verification_record_required'",
	'evidence_packet_plan: [',
	"id: 'backup_before_create_evidence'",
	"id: 'read_back_after_create_evidence'",
	"id: 'audit_after_create_evidence'",
	"id: 'reset_disabled_evidence'",
	"id: 'disabled_probes_after_reset_evidence'",
	"id: 'desktop_verification_evidence'",
	'disabled_probe_plan: [',
	"id: 'validate_probe_after_reset'",
	"id: 'preflight_probe_after_reset'",
	"id: 'create_probe_after_reset'",
	"id: 'patch_probe_after_reset'",
	"id: 'delete_probe_after_reset'",
	"id: 'batch_probe_after_reset'",
	'executionReadiness: createExecutionReadiness()',
	'type ExecutionResult',
	'type ExecutionResultStep',
	'function createExecutionResult',
	"status: 'not_executed'",
	"create_result_state: 'blocked'",
	"success_state: 'pending'",
	"failure_state: 'pending'",
	"rollback_state: 'not_run'",
	"id: 'success_create_ref_recorded'",
	"id: 'success_read_back_verified'",
	"id: 'failure_error_translated'",
	"id: 'failure_no_success_claim'",
	"id: 'rollback_decision_recorded'",
	"id: 'post_result_disabled_probes_verified'",
	'executionResult: createExecutionResult()'
]) {
	assert.ok(server.includes(requiredServerFragment), `transaction-entry server action missing required fragment: ${requiredServerFragment}`);
}
const formActionTargets = [...previewFormSource.matchAll(/formaction="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual([...new Set(formActionTargets)], ['?/preview'], 'preview page form actions must be limited to the preview action');
const submitButtons = [...previewFormSource.matchAll(/<button\b(?=[^>]*type="submit")([^>]*)>([\s\S]*?)<\/button>/g)].map((match) => ({
	attrs: match[1],
	label: match[2].replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
}));
assert.deepEqual(submitButtons, [{ attrs: ' formaction="?/preview" formnovalidate class="w-full rounded-xl px-4 py-2 font-semibold sm:w-auto" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit"', label: 'Preview transaction' }], 'the preview submit button must be the only submit control and must target ?/preview');
assert.doesNotMatch(pageOutsidePreviewForm, /<button\b(?=[^>]*type="submit")/s, 'no submit controls may exist outside the preview form');
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
const transactionSubmissionTargets = [...server.matchAll(/\/transactions(?:\/create-readiness-status|\/create-preview|\/validate)?/g)].map((match) => match[0]);
assert.deepEqual([...new Set(transactionSubmissionTargets)], ['/transactions/create-readiness-status', '/transactions/create-preview'], 'read-only create-readiness-status and create-preview must be the only transaction targets in /transactions/new server code');
const actionsBlock = server.match(/export const actions: Actions = \{([\s\S]*?)\n\};/)?.[1] ?? '';
assert.ok(actionsBlock, '/transactions/new server route must define a bounded actions object');
assert.deepEqual([...actionsBlock.matchAll(/^\s*([A-Za-z0-9_]+):\s*async/gm)].map((match) => match[1]), ['preview'], '/transactions/new must expose preview as its only server action');
const apiPostTargets = [...server.matchAll(/(?:^|\n)\s*const\s+\w+\s*=\s*await\s+apiPost<[\s\S]*?>\(\s*fetch,\s*`([^`]+)`/g)].map((match) => match[1]);
assert.deepEqual(apiPostTargets, ['/books/${bookId}/transactions/create-preview'], 'create-preview must be the only server-side POST target reachable from the transaction-entry action');
assert.equal([...server.matchAll(/method:\s*['"`]POST['"`]/g)].length, 1, '/transactions/new server code must keep POST centralized in the preview JSON helper only');
assert.match(
	server,
	/function sanitizeCreateReadinessStatus\(value: unknown, fallback = createDefaultReadinessStatus\(\)\)[\s\S]*writesEnabledFromReadinessStatus\(value\)[\s\S]*return createDefaultReadinessStatus\(writesEnabled\)/,
	'/transactions/new must fail-close the displayed readiness status instead of trusting active execution fields from the status endpoint'
);
assert.doesNotMatch(
	server,
	/status\.session_armed|status\.create_execution_allowed|status\.allowed_create_count|status\.target_class/,
	'/transactions/new must derive armed/readiness UI from redacted nested safe defaults, not top-level active execution fields'
);
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
	'No CREATE/PATCH/DELETE/batch action is available.',
	'transactions-empty-preview-link',
	'Preview transaction entry (no write)',
	'transactions-empty-preview-note',
	'Opens the same preview-only form from the toolbar'
]) {
	assert.ok(transactionsList.includes(requiredListFragment), `transactions list missing preview-only entry copy: ${requiredListFragment}`);
}
assert.doesNotMatch(transactionsList, />\s*New transaction\s*</, 'transactions list must not label the preview entry as a normal New transaction write flow');

console.log('transaction-entry-preview-static: ok');
