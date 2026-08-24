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
const accountOptionsServer = read('src', 'lib', 'accounts', 'options.server.ts');

assert.doesNotMatch(
	browserSmoke,
	/await\s+import\('\.\/test-transaction-create-product-browser\.mjs'\)|delegated/,
	'legacy transaction-entry browser gate must not delegate to the mock-only #59 product smoke'
);
for (const productModeLegacyFragment of [
	'async function runProductCreateModeSmoke',
	'product-mode legacy browser gate must call create-preview exactly twice',
	'runExplicitSyntheticCreateHarness(api, browserRequests, previewPayload, reviewedApprovalEvidence)',
	'real issue-51 disposable CREATE drill executed',
	'normal product confirm route must not be called by this legacy real-disposable drill gate'
]) {
	assert.ok(browserSmoke.includes(productModeLegacyFragment), `legacy browser gate missing #59-adapted real disposable marker: ${productModeLegacyFragment}`);
}

const expectedBrowserSmokeScript = 'npm run build && node scripts/test-transaction-entry-preview-browser.mjs';
assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview'],
	'node scripts/test-transaction-entry-preview.mjs',
	'package.json must expose npm run test:transaction-entry-preview'
);
assert.equal(
	packageJson.scripts?.['test:transaction-entry-preview-browser'],
	expectedBrowserSmokeScript,
	'package.json must expose npm run test:transaction-entry-preview-browser as a self-contained build-backed browser smoke'
);
assert.equal(
	packageJson.scripts?.['test:transaction-entry-create-disposable-browser'],
	expectedBrowserSmokeScript,
	'package.json must expose npm run test:transaction-entry-create-disposable-browser as the same build-backed deterministic synthetic/disposable browser smoke'
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
	'function clickAndWaitForPageLoad',
	'validation failure preview submit load',
	'valid preview submit load',
	'normal explicit test-mode preview submit load',
	'function setCheckbox',
	'previewServerIndex',
	'Build output must exist before browser smoke',
	"viteBin, 'preview'",
	"'--headless'",
	'mobile confirmation status must keep Future Create disabled',
	'mobile preview review cards must be visible after successful preview',
	'mobile confirmation review steps must remain no-write',
	'function assertNoMutationRequestsObserved',
	'function transactionEntryAppSubmissionSearches',
	'function assertOrdinaryBrowserCannotReachExplicitTestMode',
	'ordinary browser cannot reach explicit test-mode execution path',
	'function assertPreviewValidationFailureUi',
	'validation failure UI',
	'privatePreviewErrorDetailSentinel',
	'function assertUnknownPreviewDetailRedactionUi',
	'unknown preview detail redaction UI',
	'Preview validation failed safely. No write was executed.',
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
	'function isNonDisposableSyntheticBookRequest',
	'syntheticNonDisposableBookId',
	'function assertNonDisposableBookTamperBlocked',
	'non-disposable book tamper',
	'browser-driven tamper must not reach a non-disposable create-preview API target',
	'function assertMutationRequestPredicates',
	'synthetic API boundary must block',
	'browser boundary must block',
	'next=%2Fbooks%2F1%2Ftransactions%2Fbatch',
	"create-preview', '?next=%2Fbooks%2F1%2Ftransactions%2Fbatch",
	'createReadinessStatusCalls.length >= 1',
	'previewPayloads',
	'explicitCreatePayloads',
	'function isExplicitSyntheticCreateHarnessRequest',
	'allowedProductDrillEnvKeys',
	'forbiddenProductDrillEnvKeys',
	'function productDrillEnvironment',
	'function assertProductDrillEnvironmentIsDisposableOnly',
	'ISSUE51_PRODUCT_DRILL_ENV_SCOPE',
	'explicit product-route drills must inherit only a minimal toolchain env',
	'explicit product-route drills must not inherit private/runtime env key',
	'function assertExplicitSyntheticCreateHarnessPredicateRequiresDisposableProof',
	'function productCreatePayloadFromPreview',
	'function previewPayloadRedactedFingerprint',
	'preview_payload_fingerprint',
	'wrong reviewed-preview fingerprint',
	'function collectReviewedApprovalEvidence',
	'function assertExplicitSyntheticCreateHarnessReviewedEvidenceRejectsUnreviewedOrUnlinkedEvidence',
	'function assertReviewedEvidenceMatchesPreviewPayload',
	'successful-browser-create-preview-response',
	'reviewed-before-stale-or-query-tamper',
	'unlinked query-tamper preview index',
	'explicit harness must bind reviewed approval evidence to the exact reviewed preview payload',
	'explicit harness must not reuse the later explicit-mode query preview payload',
	'stale preview approval evidence rejection',
	'explicit harness must reject stale current UI evidence before product-route drill',
	'function assertExplicitSyntheticCreateHarnessReviewedEvidence',
	'source: \'browser-reviewed-approval-packet\'',
	'explicit CREATE harness requires reviewed browser approval evidence from the non-stale preview UI',
	'browser smoke must capture reviewed approval evidence before explicit test-mode CREATE harness',
	'function assertExplicitSyntheticCreateHarnessRejectsUserMode',
	'missing explicit harness header',
	'non-test APP_ENV synthetic CREATE probe',
	'writes-disabled explicit CREATE probe',
	'missing synthetic/disposable proof header',
	'non-disposable synthetic book id',
	'header-smuggled explicit harness token',
	'comma-smuggled explicit harness token header',
	'comma-smuggled APP_ENV header',
	'comma-smuggled writes-enabled header',
	'query-only default CREATE smuggling without harness headers',
	'extra explicit query parameter',
	'duplicate explicit test-mode query',
	'query-smuggled explicit CREATE probe',
	'non-CREATE validate route rejects explicit harness query/header smuggling',
	'explicit rejected CREATE probes must not be browser-driven',
	'function buildRedactedSyntheticCreateResultPanel',
	'function assertRedactedSyntheticCreateResultPanel',
	'function assertRedactedCreateVisibleRows',
	'display_value_source',
	'resetDefaultDisabledProbeDisplayValue',
	'function assertResetDefaultDisabledProbeCoverage',
	'fixed_status_summary',
	'validate/preflight/CREATE/PATCH/DELETE/batch blocked_or_unavailable',
	'visible rows must use fixed status summaries and never render opaque refs or raw values',
	'function assertNoPrivateRawResultPanelLeak',
	'redacted_result_panel',
	'issue51-redacted-create-result',
	'read_back_verification',
	'backup_state',
	'audit_state',
	'reset_default_disabled_probe_summary',
	'result_panel_visible_rows',
	'raw_value_included',
	'private_raw_payload_rendered',
	'raw path-like artifact',
	'explicit synthetic CREATE result panel must not expose raw API result fields',
	'raw_book_paths',
	'raw_amounts',
	'explicit synthetic CREATE result panel must stay redacted',
	'reset/default-disabled probe summary must cover validate/preflight/CREATE/PATCH/DELETE/batch',
	'function runExplicitSyntheticCreateHarness',
	'function runProductRouteCreateDrill',
	'productCreateDrillScript',
	'productPatchDrillScript',
	'function buildRedactedSyntheticPatchResultPanel',
	'function runProductRoutePatchDrill',
	'function runExplicitSyntheticPatchHarness',
	'function assertRedactedSyntheticPatchResultPanel',
	'redacted_patch_result_panel',
	'issue51-redacted-patch-result',
	'metadata_only_scope',
	'ownership_state',
	'app_created_target',
	'ownership_rejection_summary',
	'non_owned_patch_rejected',
	'immutable_rejection_summary',
	'amount_changes_rejected',
	'account_changes_rejected',
	'split_changes_rejected',
	'date_changes_rejected',
	'currency_changes_rejected',
	'reset_default_disabled_patch_probe_summary',
	'explicit product-route metadata-only PATCH drill must succeed through the backend product route',
	'product PATCH route remains forbidden without explicit synthetic metadata-only test harness',
	'spawnSync',
	'function assertBrowserToAppToApiBoundary',
	'function assertDisposableSyntheticApiTargetBoundary',
	'function assertIssue51BrowserSmokeFollowupUiToRouteProofs',
	'issue #51 follow-up must prove UI-reviewed preview was the only normal browser submission path before CREATE rehearsal',
	'normal-mode browser submissions must never hit explicit product CREATE route',
	'redacted CREATE result panel must prove product-route rehearsal used a disposable copied-like fixture',
	'issue #51 CREATE follow-up: app-to-API requests never target non-disposable book',
	'const createResultPanel = await runExplicitSyntheticCreateHarness',
	'assertIssue51BrowserSmokeFollowupUiToRouteProofs({',
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
	'function failureResultPanelSummary',
	'function assertRedactedSyntheticFailureUiDrillPanels',
	'function assertFailureUiDrillMatrix',
	'expectedFailureDrillIds',
	'expectedFailureStages',
	'redacted_failure_ui_drills',
	'api_result_shaped_redacted_ui_evidence',
	'failure_stage',
	'stale_preview_guard',
	'target_preflight_gate',
	'write_gate_default_disabled',
	'backup_before_create',
	'lock_before_create',
	'post_create_read_back',
	'post_result_reset_probe',
	'owner_recovery_copy',
	'stale_preview_rejection',
	'target_preflight_rejection',
	'writes_disabled_rejection',
	'backup_failure',
	'lock_failure',
	'read_back_failure',
	'reset_probe_failure',
	'safe_recovery_copy',
	'create_count_state',
	'read_back_verification',
	'reset_default_disabled_probe_summary',
	'disabled_probe_families',
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
assert.match(browserSmoke, /isForbiddenTransactionMutation\(method, pathname, search = ''\)[\s\S]*isNonDisposableSyntheticBookRequest\(pathname\)/, 'synthetic API boundary must reject non-disposable book targets');
assert.match(browserSmoke, /querySmugglesMutationBoundary[\s\S]*transactions\(\?:\\\/\|%2F\)\(\?!create-preview/, 'synthetic API boundary must reject query-smuggled mutation routes while preserving exact create-preview');
assert.match(browserSmoke, /assertNonDisposableBookTamperBlocked[\s\S]*selectInjectedNonDisposableBook[\s\S]*browser-driven tamper must not reach a non-disposable create-preview API target[\s\S]*rejected book tamper may reload only active-book read\/status API requests, never non-disposable or preview targets/s, 'browser smoke must submit a tampered non-disposable book id and prove it never reaches non-disposable app-to-API book targets');
assert.match(browserSmoke, /assertNoMutationRequestsObserved[\s\S]*request\.search \?\? ''/, 'browser smoke repeated mutation-boundary checks must include synthetic API query strings');
assert.match(browserSmoke, /create-preview', '\?next=%2Fbooks%2F1%2Ftransactions%2Fbatch/, 'browser smoke must unit-check query-smuggled API create-preview mutation boundaries');
assert.match(browserSmoke, /\?\/preview&next=%2Fbooks%2F1%2Ftransactions%2Fbatch/, 'browser smoke must reject smuggled mutation routes even when ?/preview appears in the query');
assert.match(browserSmoke, /isExplicitSyntheticCreateHarnessRequest[\s\S]*\/books\/1\/transactions[\s\S]*explicitSyntheticCreateHarnessSearch[\s\S]*x-issue51-explicit-test-create[\s\S]*x-issue51-synthetic-disposable-proof[\s\S]*x-app-env[\s\S]*x-gnucash-writes-enabled/, 'explicit synthetic CREATE harness must be header-gated, disposable-proof-gated, and product-route shaped');
assert.match(browserSmoke, /assertExplicitSyntheticCreateHarnessPredicateRequiresDisposableProof[\s\S]*\/books\/2\/transactions[\s\S]*missing synthetic\/disposable proof header[\s\S]*next=%2Fbooks%2F2%2Ftransactions%2Fbatch/s, 'explicit synthetic CREATE harness predicate must reject non-disposable targets, missing proof, and query-smuggled mutation routes');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*isForbiddenTransactionMutation\('POST', '\/books\/1\/transactions', ''\)[\s\S]*product CREATE route remains forbidden without explicit synthetic test harness[\s\S]*runProductRouteCreateDrill\(productCreatePayload\)/, 'explicit synthetic CREATE harness must prove default CREATE remains blocked before using the backend product-route drill');
assert.match(browserSmoke, /productCreatePayloadFromPreview[\s\S]*splits[\s\S]*account_id: previewPayload\.debit_account_id[\s\S]*amount: `-\$\{previewPayload\.amount\}`[\s\S]*account_id: previewPayload\.credit_account_id/, 'explicit synthetic CREATE harness must derive a product CREATE payload from the preview payload');
assert.match(browserSmoke, /function previewPayloadRedactedFingerprint[\s\S]*createHash\('sha256'\)[\s\S]*preview_payload_fingerprint: previewPayloadRedactedFingerprint\(previewPayload\)/s, 'reviewed approval evidence must bind a redacted fingerprint to the exact preview payload without rendering raw values');
assert.match(browserSmoke, /assertReviewedEvidenceMatchesPreviewPayload[\s\S]*preview_payload_fingerprint[\s\S]*previewPayloadRedactedFingerprint\(previewPayload\)[\s\S]*exact reviewed preview payload fingerprint/s, 'explicit synthetic CREATE harness must reject reviewed evidence that is not fingerprint-bound to the reviewed preview payload');
assert.match(browserSmoke, /assertExplicitSyntheticCreateHarnessReviewedEvidenceRejectsUnreviewedOrUnlinkedEvidence[\s\S]*wrong reviewed-preview fingerprint/s, 'explicit synthetic CREATE harness must reject reviewed evidence with a mismatched preview-payload fingerprint');
assert.match(browserSmoke, /assertExplicitSyntheticCreateHarnessRejectsUserMode[\s\S]*missing explicit harness header[\s\S]*missing synthetic\/disposable proof header[\s\S]*non-test APP_ENV synthetic CREATE probe[\s\S]*writes-disabled explicit CREATE probe[\s\S]*testCase\.path[\s\S]*response\.status, 409[\s\S]*explicit rejected CREATE probes must not be browser-driven/, 'explicit synthetic CREATE harness must actively reject user-mode, missing-proof, or partially armed CREATE probes');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*assertReviewedEvidenceMatchesPreviewPayload\(api, previewPayload, reviewedApprovalEvidence\)[\s\S]*productCreatePayloadFromPreview\(previewPayload\)[\s\S]*assertExplicitSyntheticCreateHarnessRejectsUserMode\(api, browserRequests, productCreatePayload\)[\s\S]*runProductRouteCreateDrill\(productCreatePayload\)/, 'explicit synthetic CREATE harness must require reviewed approval evidence and run rejection probes before invoking the backend product-route drill');
assert.match(browserSmoke, /function assertIssue51BrowserSmokeFollowupUiToRouteProofs[\s\S]*transactionEntryAppSubmissionSearches\(browserRequests\)[\s\S]*assertBrowserToAppToApiBoundary\(browserRequests, webBase, apiUrl[\s\S]*assertDisposableSyntheticApiTargetBoundary\(api[\s\S]*syntheticNonDisposableBookId[\s\S]*redacted_result_panel[\s\S]*fixture_scope/s, 'browser smoke must aggregate the issue #51 follow-up proof: UI-reviewed preview to product-route rehearsal, no normal-mode execution, and no non-disposable app-to-API target');
assert.match(browserSmoke, /const createResultPanel = await runExplicitSyntheticCreateHarness\(api, browserRequests, previewPayload, reviewedApprovalEvidence\)[\s\S]*assertIssue51BrowserSmokeFollowupUiToRouteProofs\(\{[\s\S]*createResultPanel[\s\S]*webBase[\s\S]*apiUrl: api\.url/s, 'browser smoke must run the follow-up proof immediately after the explicit synthetic CREATE harness');
assert.match(browserSmoke, /reviewedPreviewPayload = api\.previewPayloads\[api\.previewPayloads\.length - 1\][\s\S]*reviewedApprovalEvidence = await collectReviewedApprovalEvidence\(cdp, 'reviewed preview', \{[\s\S]*previewPayloadIndex: api\.previewPayloads\.length - 1[\s\S]*assertReviewedEvidenceMatchesPreviewPayload\(api, reviewedPreviewPayload, reviewedApprovalEvidence\)[\s\S]*runExplicitSyntheticCreateHarness\(api, browserRequests, previewPayload, reviewedApprovalEvidence\)/, 'browser smoke must bind reviewed approval evidence to the reviewed create-preview payload before the explicit synthetic CREATE harness');
assert.match(browserSmoke, /function buildRedactedSyntheticCreateResultPanel\(\)[\s\S]*redacted_result_panel[\s\S]*create_count: 1[\s\S]*fixture_scope[\s\S]*private_or_only_copy_target: false[\s\S]*read_back_verification[\s\S]*backup_state[\s\S]*audit_state[\s\S]*reset_default_disabled_probe_summary/s, 'explicit synthetic CREATE harness must build a redacted result panel with fixture proof, count, read-back, backup/audit, and reset/probe summary');
assert.match(browserSmoke, /function assertRedactedSyntheticCreateResultPanel[\s\S]*syntheticDescription[\s\S]*syntheticMemo[\s\S]*syntheticAmount[\s\S]*explicit synthetic CREATE result panel must stay redacted/s, 'explicit synthetic CREATE result panel assertions must reject private/raw-like payload values');
assert.match(browserSmoke, /runExplicitSyntheticCreateHarness[\s\S]*const responseBody = runProductRouteCreateDrill\(productCreatePayload\)[\s\S]*assertRedactedSyntheticCreateResultPanel\(responseBody, productCreatePayload, reviewedApprovalEvidence\)/s, 'explicit synthetic CREATE harness must assert the redacted result panel returned from the backend product-route drill');
assert.match(browserSmoke, /function buildRedactedSyntheticPatchResultPanel\(\)[\s\S]*redacted_patch_result_panel[\s\S]*setup_create_count: 1[\s\S]*patch_count: 1[\s\S]*ownership_state[\s\S]*metadata_only_scope[\s\S]*ownership_rejection_summary[\s\S]*non_owned_patch_rejected[\s\S]*immutable_rejection_summary[\s\S]*reset_default_disabled_patch_probe_summary/s, 'explicit synthetic PATCH harness must build a redacted result panel for one app-owned metadata-only PATCH and a non-owned rejection probe');
assert.match(browserSmoke, /function assertRedactedSyntheticPatchResultPanel[\s\S]*metadata_only_scope\.rejected_fields[\s\S]*amount_changes_rejected[\s\S]*account_changes_rejected[\s\S]*split_changes_rejected[\s\S]*date_changes_rejected[\s\S]*currency_changes_rejected/s, 'explicit synthetic PATCH result assertions must reject immutable financial fields');
assert.match(browserSmoke, /runExplicitSyntheticPatchHarness[\s\S]*isForbiddenTransactionMutation\('PATCH', '\/books\/1\/transactions\/synthetic-id', ''\)[\s\S]*product PATCH route remains forbidden without explicit synthetic metadata-only test harness[\s\S]*runProductRoutePatchDrill\(productCreatePayload\)[\s\S]*assertRedactedSyntheticPatchResultPanel\(responseBody, productCreatePayload, reviewedApprovalEvidence\)/s, 'explicit synthetic PATCH harness must prove default PATCH remains blocked before using the backend product-route drill');
assert.match(browserSmoke, /runProductRouteCreateDrill[\s\S]*productCreateDrillScript[\s\S]*env: productDrillEnvironment\(\)[\s\S]*explicit product-route CREATE drill must succeed through the backend product route/s, 'explicit synthetic CREATE harness must run the backend product-route drill with the bounded synthetic/disposable test env helper');
assert.match(browserSmoke, /runProductRoutePatchDrill[\s\S]*productPatchDrillScript[\s\S]*env: productDrillEnvironment\(\)[\s\S]*explicit product-route metadata-only PATCH drill must succeed through the backend product route/s, 'explicit synthetic PATCH harness must run the backend product-route drill with the bounded synthetic/disposable test env helper');
assert.match(browserSmoke, /function buildRedactedSyntheticDeleteResultPanel\(\)[\s\S]*redacted_delete_result_panel[\s\S]*setup_create_count: 1[\s\S]*delete_count: 1[\s\S]*ownership_state[\s\S]*non_app_created_delete_allowed: false[\s\S]*non_disposable_delete_allowed: false[\s\S]*reset_default_disabled_delete_probe_summary/s, 'explicit synthetic DELETE harness must build a redacted result panel for one app-owned disposable DELETE and rejection probes');
assert.match(browserSmoke, /function assertRedactedSyntheticDeleteResultPanel[\s\S]*delete_scope[\s\S]*transaction_removed[\s\S]*account_balance_reverted[\s\S]*rejection_summary[\s\S]*non_owned_delete_rejected[\s\S]*non_disposable_delete_rejected[\s\S]*non_owned_rejection_audit_recorded[\s\S]*non_owned_rejection_audit_redacted/s, 'explicit synthetic DELETE result assertions must prove app-owned delete plus audited/redacted non-owned and non-disposable rejection');
assert.match(browserSmoke, /runExplicitSyntheticDeleteHarness[\s\S]*isForbiddenTransactionMutation\('DELETE', '\/books\/1\/transactions\/synthetic-id', ''\)[\s\S]*product DELETE route remains forbidden without explicit synthetic app-owned test harness[\s\S]*runProductRouteDeleteDrill\(productCreatePayload\)[\s\S]*assertRedactedSyntheticDeleteResultPanel\(responseBody, productCreatePayload, reviewedApprovalEvidence\)/s, 'explicit synthetic DELETE harness must prove default DELETE remains blocked before using the backend product-route drill');
assert.match(browserSmoke, /runProductRouteDeleteDrill[\s\S]*productDeleteDrillScript[\s\S]*env: productDrillEnvironment\(\)[\s\S]*explicit product-route app-owned DELETE drill must succeed through the backend product route/s, 'explicit synthetic DELETE harness must run the backend product-route drill with the bounded synthetic/disposable test env helper');
assert.match(browserSmoke, /runExplicitSyntheticPatchHarness\(api, browserRequests, previewPayload, reviewedApprovalEvidence\)[\s\S]*runExplicitSyntheticDeleteHarness\(api, browserRequests, previewPayload, reviewedApprovalEvidence\)/, 'browser smoke must run explicit DELETE rehearsal after create and metadata-only PATCH rehearsals');
assert.match(browserSmoke, /payload\.amount === validationFailureAmount[\s\S]*loc: \['body', 'amount'\][\s\S]*msg: 'amount must be positive'/s, 'browser smoke must drive failure UI through the preview endpoint, not a mutation endpoint');
assert.match(browserSmoke, /function assertPreviewValidationFailureUi[\s\S]*Preview validation failed safely[\s\S]*No CREATE\\\/PATCH\\\/DELETE\\\/batch executed[\s\S]*Future Create control must remain absent until a successful preview/s, 'browser smoke must assert safe failure UI before continuing');
assert.match(browserSmoke, /function assertOrdinaryBrowserCannotReachExplicitTestMode[\s\S]*transactionEntryAppSubmissionSearches[\s\S]*'\?\/preview'[\s\S]*request\.path === '\/books\/1\/transactions'[\s\S]*ordinary browser cannot reach explicit test-mode execution path/s, 'browser smoke must prove ordinary browser submissions cannot reach the explicit test-mode execution path');
assert.match(browserSmoke, /Page\.navigate', \{ url: `\$\{webBase\}\/transactions\/new\?explicit_test_mode=issue51` \}[\s\S]*normal explicit test-mode query attempt[\s\S]*assertOrdinaryBrowserCannotReachExplicitTestMode/s, 'browser smoke must attempt an ordinary explicit_test_mode query and still submit only preview');
assert.match(browserSmoke, /transactionEntryAppSubmissionSearches\(browserRequests\)[\s\S]*\['\?\/preview', '\?\/preview', '\?\/preview', '\?\/preview', '\?\/preview'\][\s\S]*including non-disposable book tamper, validation failure, unknown-detail redaction, and explicit-mode query attempts/s, 'browser smoke must prove every ordinary transaction-entry POST targets only ?/preview');


// #59 product CREATE replaces the old two-account preview-only shell while this
// canonical legacy command remains the umbrella transaction-entry guard. Keep the
// long browser-smoke issue-51 disposable route assertions above; update the
// route-local source assertions here to prove the new SSR preview+confirm product
// contract without weakening mutation/redaction boundaries.
for (const field of [
	'book_id',
	'date',
	'currency',
	'description',
	'split_account_id',
	'split_amount',
	'split_memo',
	'preview_token',
	'idempotency_key',
	'transaction_json'
]) {
	assert.match(page, new RegExp(`name="${field}"`), `transaction-entry product page must expose field: ${field}`);
}

for (const requiredProductFragment of [
	'id="transaction-create-form"',
	'id="confirm-create-form"',
	'transactionCreate.policyTitle',
	'transactionCreate.scopeCopy',
	'transactionCreate.previewHelp',
	'transactionCreate.dateLabel',
	'transactionCreate.currencyLabel',
	'transactionCreate.descriptionLabel',
	'transactionCreate.splitEditorTitle',
	'transactionCreate.accountLabel',
	'transactionCreate.amountLabel',
	'transactionCreate.memoLabel',
	'transactionCreate.addSplit',
	'transactionCreate.removeSplit',
	'transactionCreate.moveUp',
	'transactionCreate.moveDown',
	'transactionCreate.previewSubmit',
	'transactionCreate.confirmSubmit',
	'transactionCreate.previewStaleTitle',
	'transactionCreate.safeResultsTitle',
	'previewIsStale',
	'confirmSubmitting',
	'confirm_allowed',
	'account.full_name',
	'account.currency',
	'data-mobile-contract="320px no horizontal overflow"'
]) {
	assert.ok(page.includes(requiredProductFragment), `transaction-entry product page missing required fragment: ${requiredProductFragment}`);
}

assert.match(page, /function decimalStringToParts[\s\S]*function scaleDecimalParts[\s\S]*BigInt[\s\S]*maxScale/s, 'product running balance must use string/BigInt decimal scaling at max fractional scale');
assert.doesNotMatch(page, /parseFloat|Number\(|fraction\.length > 2|padEnd\(2|slice\(-2\)|\.00\b/, 'product amount UI must not use JS numeric parsing or fixed two-decimal scaling');
assert.doesNotMatch(page, /name="note"|transaction_note|localStorage|sessionStorage/, 'product route must not submit notes or persist private drafts/tokens in browser storage');
assert.match(page, /function addSplit\(\)[\s\S]*splits\.length >= 50[\s\S]*disabled=\{splits\.length >= 50\}/s, 'product split editor must disable add at the 50-row bound');
assert.match(page, /disabled=\{splits\.length <= 2\}/, 'product split editor must disable remove at the 2-row bound');
assert.match(page, /\{#if preview && preview\.confirm_allowed && !previewIsStale\}[\s\S]*id="confirm-create-form"[\s\S]*name="preview_token"[\s\S]*name="idempotency_key"[\s\S]*name="transaction_json"/s, 'product confirm form must appear only for fresh confirm_allowed previews and preserve token/key/payload');

const productFormTags = [...page.matchAll(/<form\b[^>]*>/g)].map((match) => match[0]);
assert.equal(productFormTags.length, 2, 'product transaction-entry page must expose exactly the draft preview form and explicit confirm form');
assert.match(productFormTags[0], /id="transaction-create-form"[\s\S]*method="POST"/, 'first product form must be the draft preview form');
assert.match(productFormTags[1], /id="confirm-create-form"[\s\S]*method="POST"[\s\S]*action="\?\/confirm"/, 'second product form must be the explicit confirm form');
const productFormActionAssignments = [...page.matchAll(/\bformaction\s*=\s*(?:"([^"]*)"|'([^']*)'|\{([^}]*)\})/g)].map((match) => match[1] ?? match[2] ?? `{${match[3]}}`);
assert.deepEqual([...new Set(productFormActionAssignments)].sort(), ['?/confirm', '?/preview'].sort(), 'product page must expose only preview and confirm SvelteKit action targets');

assert.match(server, /export const actions: Actions = \{[\s\S]*preview:\s*async[\s\S]*confirm:\s*async/s, '/transactions/new must expose preview and confirm actions only for product CREATE');
assert.match(server, /loadAccountOptions\([\s\S]*purpose: 'transaction_create_preview'[\s\S]*currency: activeBook\.base_currency[\s\S]*accountOptionsAvailable[\s\S]*accountOptionsPartialFailure/s, '/transactions/new must load bounded posting choices and expose safe availability state');
assert.doesNotMatch(server, /apiFetch<Account\[\]>|`\$\{bookPrefix\}\/accounts(?:\?|`)/, '/transactions/new must not load the legacy balance-bearing account list');
assert.match(accountOptionsServer, /purpose: 'transactions_filter' \| 'transaction_create_preview'/, 'shared account-options loader must accept only the two bounded UI purposes');
assert.match(page, /transaction-create-account-options-status[\s\S]*!data\.accountOptionsAvailable[\s\S]*href="\/diagnostics"/s, 'preview page must render account-option recovery without becoming a route-level 503');
assert.match(page, /name="split_account_id"[\s\S]*disabled=\{!data\.accountOptionsAvailable\}[\s\S]*formaction="\?\/preview"[\s\S]*disabled=\{!data\.accountOptionsAvailable\}/s, 'preview page must disable account selectors and preview submission when bounded posting choices are unavailable');
assert.deepEqual([...server.matchAll(/^\s*([A-Za-z0-9_]+):\s*async/gm)].map((match) => match[1]), ['preview', 'confirm'], '/transactions/new actions must be exactly preview and confirm');
assert.match(server, /apiPostJson<TransactionCreatePreviewResponse>[\s\S]*`\/books\/\$\{activeBook\.id\}\/transactions\/create-preview`[\s\S]*body: transaction/s, 'product preview action must post the normalized draft to create-preview for the active book');
assert.match(server, /apiPostJson<TransactionCreateConfirmResult>[\s\S]*`\/books\/\$\{activeBook\.id\}\/transactions`[\s\S]*body:\s*\{\s*preview_token: previewToken,\s*transaction\s*\}[\s\S]*'Idempotency-Key': idempotencyKey/s, 'product confirm action must post frozen token+transaction with the preview idempotency key');
assert.match(server, /safeCreateRedirectPath[\s\S]*SAFE_TRANSACTION_ID_RE[\s\S]*target\.hash = ''[\s\S]*target\.search = ''[\s\S]*create_status/s, 'product success redirect must clamp same-app transaction links and discard backend query/hash');
assert.match(server, /safeOpaqueRef[\s\S]*REQUEST_REF_RE[\s\S]*RECOVERY_REF_RE[\s\S]*recoveryRef: safeOpaqueRef[\s\S]*requestRef: safeOpaqueRef/s, 'product errors must clamp request/recovery refs before rendering');
assert.match(server, /isSafeRetryableConfirmFailure[\s\S]*CREATE_IN_PROGRESS[\s\S]*BOOK_WRITE_BUSY[\s\S]*retryPreviewFromConfirmFailure[\s\S]*preview_token: previewToken[\s\S]*idempotency_key: idempotencyKey/s, 'typed retryable confirm failures must preserve the same token/key/payload for retry');
assert.doesNotMatch(server, /backup_path|create_book_backup|write_lock|GnuCashWriteService|localStorage|sessionStorage|return detail;|safeMessage\(detail\)/, 'product frontend route must not render raw backend detail/path or call backend write helpers directly');
assert.doesNotMatch(server, /method:\s*['"`](?:PUT|PATCH|DELETE)['"`]|\/transactions\/(?:batch|import|delete|patch)|owner-writebeta|write-alpha/i, '/transactions/new server action must not reference PATCH/DELETE/batch/import/write-beta routes');
const productTransactionTargets = [...server.matchAll(/\/transactions(?:\/create-preview)?/g)].map((match) => match[0]);
assert.ok(productTransactionTargets.includes('/transactions/create-preview'), 'product server must include the preview endpoint');
assert.ok(productTransactionTargets.includes('/transactions'), 'product server must include the confirm endpoint');
assert.doesNotMatch(server, /`\/books\/\$\{bookId\}\/transactions(?:\/create-preview)?`/, '/transactions/new action must not trust submitted book_id as an API target');

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
