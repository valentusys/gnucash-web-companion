import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
function resolveChromiumBin() {
	if (process.env.CHROMIUM_BIN) return process.env.CHROMIUM_BIN;
	for (const candidate of [
		'/snap/bin/chromium',
		'/usr/bin/chromium',
		'/usr/bin/chromium-browser',
		'/usr/bin/google-chrome',
		'/usr/bin/google-chrome-stable'
	]) {
		if (existsSync(candidate)) return candidate;
	}
	return '/snap/bin/chromium';
}

const chromiumBin = resolveChromiumBin();
const syntheticToken = 'synthetic-smoke-token';
const syntheticDescription = 'Synthetic browser smoke preview';
const syntheticMemo = 'Synthetic browser smoke memo';
const syntheticAmount = '12.34';

const syntheticBook = {
	id: 1,
	name: 'Synthetic Smoke Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for browser smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic local test fixture.',
		safe_next_actions: []
	},
	management_actions: [],
	operator_guidance: {
		metadata_source: 'synthetic',
		data_access: 'stubbed',
		read_only_default: true,
		private_path_redacted: true,
		storage_type_label: 'Synthetic',
		unsupported_management_actions: [],
		message: 'Synthetic local smoke fixture; no private book is used.'
	}
};

const syntheticAccounts = [
	{
		id: 'smoke-source',
		name: 'Smoke Source',
		full_name: 'Synthetic Source',
		type: 'ASSET',
		currency: 'SEK',
		balance: '100.00',
		placeholder: false,
		hidden: false,
		parent_id: null
	},
	{
		id: 'smoke-destination',
		name: 'Smoke Destination',
		full_name: 'Synthetic Destination',
		type: 'EXPENSE',
		currency: 'SEK',
		balance: '0.00',
		placeholder: false,
		hidden: false,
		parent_id: null
	},
	{
		id: 'smoke-hidden',
		name: 'Smoke Hidden',
		full_name: 'Synthetic Hidden',
		type: 'EXPENSE',
		currency: 'SEK',
		balance: '0.00',
		placeholder: false,
		hidden: true,
		parent_id: null
	},
	{
		id: 'smoke-placeholder',
		name: 'Smoke Placeholder',
		full_name: 'Synthetic Placeholder',
		type: 'EXPENSE',
		currency: 'SEK',
		balance: '0.00',
		placeholder: true,
		hidden: false,
		parent_id: null
	}
];

function readSource(...segments) {
	return readFileSync(join(root, ...segments), 'utf8');
}

function assertSourceSafety() {
	const packageJson = JSON.parse(readSource('package.json'));
	const page = readSource('src', 'routes', 'transactions', 'new', '+page.svelte');
	const server = readSource('src', 'routes', 'transactions', 'new', '+page.server.ts');

	assert.equal(
		packageJson.scripts?.['test:transaction-entry-preview-browser'],
		'node scripts/test-transaction-entry-preview-browser.mjs',
		'package.json must expose npm run test:transaction-entry-preview-browser'
	);
	assert.match(page, /id="write-session-gate"[\s\S]*Preview mode[\s\S]*Write session not armed[\s\S]*CREATE execution unavailable without fresh owner approval/s, 'write-session gate must default to preview mode and not armed');
	assert.match(page, /writes_enabled:[\s\S]*session_armed:[\s\S]*create_execution_allowed:[\s\S]*allowed_create_count:[\s\S]*target_class:/s, 'write-session gate must expose safe redacted status fields');
	assert.match(page, /id="mobile-preview-path-card"[\s\S]*Mobile preview path[\s\S]*Tap Preview transaction; this is the only submitting action[\s\S]*The form stays preview-only and no-write on mobile/s, 'mobile preview path card must guide the safe preview-only flow');
	assert.match(page, /id="preview-mobile-action-bar"[\s\S]*sticky bottom-0[\s\S]*formaction="\?\/preview"[\s\S]*Preview transaction[\s\S]*Create disabled/s, 'mobile action bar must keep the preview submit target and disabled create control together');
	assert.match(page, /id="mobile-confirmation-status-card"[\s\S]*Mobile confirmation status[\s\S]*Preview state[\s\S]*Future Create: disabled[\s\S]*Copy helper: placeholders only[\s\S]*No write path is enabled/s, 'mobile confirmation status card must summarize preview state without adding write controls');
	assert.match(page, /id="redacted-create-readiness-state"[\s\S]*Redacted read-only readiness state[\s\S]*writes_enabled status[\s\S]*allowed execution status/s, 'page must expose the redacted read-only readiness object fields');
	assert.match(page, /id="armed-session-requirements"[\s\S]*Target class required[\s\S]*Exact CREATE count required[\s\S]*preview-reviewed checkbox alone is not enough/s, 'armed-session requirements panel must remain disabled placeholder guidance');
	assert.match(page, /id="target-preflight-readiness"[\s\S]*Target preflight required[\s\S]*Target readiness not checked[\s\S]*Default state: all target readiness checks are pending \/ not checked \/ not armed/s, 'target preflight shell must default to not checked/pending');
	assert.match(page, /id="target-preflight-checklist"/, 'target preflight checklist must be rendered');
	assert.match(page, /id="execution-readiness-shell"[\s\S]*Backup\/read-back\/audit\/reset\/probes required[\s\S]*Execution readiness not checked[\s\S]*Default state: backup, read-back, audit, reset, and probe readiness are pending \/ not checked \/ not armed/s, 'execution readiness shell must default to not checked/pending');
	assert.match(page, /execution_readiness.required:[\s\S]*execution_readiness.status:[\s\S]*backup_state:[\s\S]*read_back_state:[\s\S]*audit_state:[\s\S]*reset_state:[\s\S]*probe_state:/s, 'execution readiness shell must expose safe redacted status fields');
	assert.match(page, /id="execution-evidence-packet-plan"[\s\S]*Future evidence packet plan \(pending\)[\s\S]*Default state: route backup, read-back, audit, reset, disabled-probe, and Desktop-verification evidence are pending and not collected/s, 'execution evidence packet plan must default to pending/not collected');
	assert.match(page, /id="disabled-probe-readiness-matrix"[\s\S]*Disabled-write probe matrix \(pending\)[\s\S]*Default state: validate\/preflight\/CREATE\/PATCH\/DELETE\/batch probes are pending and not executed/s, 'disabled-probe matrix must default to pending/not executed');
	assert.match(page, /id="execution-result-shell"[\s\S]*Execution-result UX shell \(not run\)[\s\S]*Default state: no execution result exists, no success or failure result is claimed, and rollback\/restore is not run/s, 'execution-result shell must default to not run/no success/no failure/no rollback');
	assert.match(page, /id="execution-result-outcome-legend"[\s\S]*Result outcome legend \(disabled\)[\s\S]*Do not infer success from preview or approval copy[\s\S]*Rollback\/restore: owner-approved recovery path only/s, 'execution-result shell must explain disabled success/failure/rollback outcomes');
	assert.match(page, /id="execution-result-triage-panel"[\s\S]*Disabled result triage[\s\S]*Current state: no CREATE execution attempted; preview data is not a success result[\s\S]*Success requires redacted CREATE reference and private read-back before any success copy[\s\S]*Failure state keeps success blocked until a safe error is translated[\s\S]*Rollback state remains owner-approved recovery only and is not run from this page[\s\S]*Post-result reset\/probe state stays pending until GNUCASH_WRITES_ENABLED=false is verified/s, 'execution-result triage panel must clarify disabled success/failure/rollback/reset outcomes');
	for (const targetPreflightLabel of ['Target file exists/readable', 'Target is outside repo', 'GnuCash Desktop closed', 'No .LCK/.LNK lock', 'Manual Desktop verification required']) {
		assert.ok(page.includes(targetPreflightLabel), `target preflight checklist missing label: ${targetPreflightLabel}`);
	}
	for (const executionReadinessLabel of ['Independent backup plan required', 'Backup readable copy proof required', 'Post-CREATE read-back required', 'Redacted audit evidence required', 'Writes reset to disabled required', 'Disabled CREATE probe required', 'Disabled validate/preflight probes required', 'Disabled PATCH/DELETE/batch probes required', 'Manual Desktop verification record required']) {
		assert.ok(page.includes(executionReadinessLabel), `execution readiness checklist missing label: ${executionReadinessLabel}`);
	}
	for (const evidencePacketLabel of ['Backup evidence captured before CREATE', 'Read-back evidence captured after CREATE', 'Redacted audit evidence captured after CREATE', 'Write-disable reset evidence captured', 'Disabled-probe evidence captured after reset', 'Manual Desktop verification evidence captured']) {
		assert.ok(page.includes(evidencePacketLabel), `execution evidence packet plan missing label: ${evidencePacketLabel}`);
	}
	for (const disabledProbeLabel of ['Validate probe after reset', 'Preflight probe after reset', 'CREATE probe after reset', 'PATCH probe after reset', 'DELETE probe after reset', 'Batch probe after reset']) {
		assert.ok(page.includes(disabledProbeLabel), `disabled-probe matrix missing label: ${disabledProbeLabel}`);
	}
	for (const executionResultLabel of ['Success result: CREATE reference recorded', 'Success result: read-back verified', 'Failure result: safe error translated', 'Failure result: no success claim emitted', 'Rollback result: restore decision recorded', 'Post-result disabled probes verified']) {
		assert.ok(page.includes(executionResultLabel), `execution-result shell missing label: ${executionResultLabel}`);
	}
	assert.doesNotMatch(page, /data-preflight-status="(?:checked|passed|ready|ok)"/, 'target preflight shell must not mark checks passed by default');
	assert.doesNotMatch(page, /data-execution-readiness-status="(?:checked|passed|ready|ok)"/, 'execution readiness shell must not mark checks passed by default');
	assert.doesNotMatch(page, /data-execution-evidence-status="(?:checked|passed|ready|ok)"/, 'execution evidence packet plan must not mark evidence passed by default');
	assert.doesNotMatch(page, /data-disabled-probe-status="(?:checked|passed|ready|ok)"/, 'disabled-probe matrix must not mark probes passed by default');
	assert.doesNotMatch(page, /data-execution-result-status="(?:checked|passed|ready|ok|success|failed|rolled_back)"/, 'execution-result shell must not mark result steps passed by default');
	assert.match(page, /id="approval-packet"[\s\S]*Future Create remains disabled/s, 'approval packet must stay visible and no-write');
	assert.match(page, /id="preview-stale-warning"[\s\S]*stale and cannot support a future owner-approved CREATE/s, 'stale-preview warning must remain present');
	assert.match(page, /id="future-create-disabled"[\s\S]*type="button"[\s\S]*disabled/s, 'Future Create must remain disabled and non-submitting');
	const previewFormStartIndex = page.indexOf('<form id="transaction-preview-form"');
	const previewFormEndIndex = page.indexOf('</form>');
	assert.notEqual(previewFormStartIndex, -1, 'transaction preview form must have a stable source block');
	assert.ok(previewFormEndIndex > previewFormStartIndex, 'transaction preview form must have a bounded source block');
	const previewFormSource = page.slice(previewFormStartIndex, previewFormEndIndex + '</form>'.length);
	const pageOutsidePreviewForm = page.slice(0, previewFormStartIndex) + page.slice(previewFormEndIndex + '</form>'.length);
	const formTags = [...page.matchAll(/<form\b[^>]*>/g)].map((match) => match[0]);
	assert.equal(formTags.length, 1, 'transaction-entry page must keep exactly one form: the preview form');
	assert.match(formTags[0], /id="transaction-preview-form"/, 'the only form must be the transaction preview form');
	assert.match(formTags[0], /method="POST"/, 'the preview form must be the only POSTing form');
	assert.doesNotMatch(formTags[0], /\baction=/, 'the preview form must not set a page-level action target');
	assert.deepEqual([...new Set([...previewFormSource.matchAll(/formaction="([^"]+)"/g)].map((match) => match[1]))], ['?/preview'], 'preview form actions must stay limited to ?/preview');
	assert.doesNotMatch(pageOutsidePreviewForm, /<(?:input|select|textarea|button)\b[^>]*\bname="/s, 'controls outside the preview form must not submit named values');
	assert.doesNotMatch(pageOutsidePreviewForm, /<(?:button|input)\b[^>]*\b(?:form|formaction)="/s, 'controls outside the preview form must not attach to or target a form');
	assert.deepEqual(
		[...new Set([...previewFormSource.matchAll(/\bname="([^"]+)"/g)].map((match) => match[1]))].sort(),
		['amount', 'book_id', 'credit_account_id', 'currency', 'date', 'debit_account_id', 'description', 'memo'].sort(),
		'preview form must submit only the bounded create-preview payload fields plus book_id'
	);
	const futureCreateIndex = page.indexOf('id="future-create-disabled"');
	assert.ok(previewFormEndIndex > 0 && futureCreateIndex > previewFormEndIndex, 'Future Create disabled control must remain outside the preview submission form');
	const futureCreateButton = page.match(/<button\b(?=[^>]*id="future-create-disabled")(?=[^>]*type="button")(?=[^>]*disabled)[^>]*>/s)?.[0] ?? '';
	assert.ok(futureCreateButton, 'Future Create disabled button must be statically present');
	assert.doesNotMatch(futureCreateButton, /\b(?:form|formaction|name|value)=/, 'Future Create disabled button must not define submitted attributes or attach to a form');
	assert.doesNotMatch(futureCreateButton, /\b(?:onclick|onsubmit|onmousedown|onmouseup|onkeydown|onkeyup|onpointerdown|onpointerup|on:click|on:submit)\s*=/, 'Future Create disabled button must not define event handlers');
	assert.match(page, /navigator\.clipboard\.writeText\(safeApprovalTemplate\)/, 'copy button must use the static placeholder-only approval template');
	assert.doesNotMatch(page, /clipboard\.writeText\([^)]*preview\./, 'copy button must not copy private preview values');
	assert.doesNotMatch(page, /localStorage|sessionStorage/, 'preview smoke requires no browser storage persistence');
	assert.match(server, /export const actions: Actions = \{\s*preview:\s*async/s, '/transactions/new must expose only the preview action');
	assert.deepEqual(
		[...new Set([...server.matchAll(/\/transactions(?:\/create-readiness-status|\/create-preview|\/validate)?/g)].map((match) => match[0]))],
		['/transactions/create-readiness-status', '/transactions/create-preview'],
		'read-only create-readiness-status and create-preview must remain the only transaction targets in /transactions/new server code'
	);
	assert.doesNotMatch(server, /\b(?:create|validate)\s*:\s*async/, '/transactions/new must not define active create or validate actions');
	assert.doesNotMatch(server, /\/transactions\/validate|`\/books\/\$\{bookId\}\/transactions`|hasWriteAcknowledgement/, '/transactions/new must not call validate/write API paths');
	assert.match(server, /function createWriteSessionGate\(status = createDefaultReadinessStatus\(\)\)[\s\S]*status\.readiness_state\.session_armed\.armed[\s\S]*status\.readiness_state\.allowed_create_count\.count[\s\S]*create_execution_allowed: status\.readiness_state\.allowed_execution\.allowed/s, 'server write-session gate must derive from redacted readiness status and stay CREATE-disabled');
	assert.match(server, /function sanitizeCreateReadinessStatus\(value: unknown, fallback = createDefaultReadinessStatus\(\)\)[\s\S]*return createDefaultReadinessStatus\(writesEnabled\)/s, 'server load must clamp any endpoint readiness status into fail-closed defaults before rendering');
	assert.match(server, /apiGetOptional<unknown>[\s\S]*sanitizeCreateReadinessStatus\(rawCreateReadinessStatus, defaultReadinessStatus\)/s, 'server load must fetch readiness as unknown and sanitize it before UI use');
	assert.match(server, /function createTargetPreflight\(\)[\s\S]*required: true[\s\S]*status: 'not_checked'[\s\S]*target_class: targetClass[\s\S]*status: 'pending'/s, 'server target preflight must default to required/not_checked/pending');
	assert.match(server, /function createExecutionReadiness\(\)[\s\S]*required: true[\s\S]*status: 'not_checked'[\s\S]*backup_state: 'pending'[\s\S]*read_back_state: 'pending'[\s\S]*audit_state: 'pending'[\s\S]*reset_state: 'pending'[\s\S]*probe_state: 'pending'[\s\S]*status: 'pending'/s, 'server execution readiness must default to required/not_checked/pending');
	assert.match(server, /function createExecutionReadiness\(\)[\s\S]*evidence_packet_plan: \[[\s\S]*id: 'backup_before_create_evidence'[\s\S]*id: 'read_back_after_create_evidence'[\s\S]*id: 'audit_after_create_evidence'[\s\S]*id: 'reset_disabled_evidence'[\s\S]*id: 'disabled_probes_after_reset_evidence'[\s\S]*id: 'desktop_verification_evidence'/s, 'server execution readiness must include an explicit pending evidence packet plan');
	assert.match(server, /function createExecutionReadiness\(\)[\s\S]*disabled_probe_plan: \[[\s\S]*id: 'validate_probe_after_reset'[\s\S]*id: 'preflight_probe_after_reset'[\s\S]*id: 'create_probe_after_reset'[\s\S]*id: 'patch_probe_after_reset'[\s\S]*id: 'delete_probe_after_reset'[\s\S]*id: 'batch_probe_after_reset'/s, 'server execution readiness must include an explicit pending disabled-probe plan');
	assert.match(server, /function createExecutionResult\(\)[\s\S]*status: 'not_executed'[\s\S]*create_result_state: 'blocked'[\s\S]*success_state: 'pending'[\s\S]*failure_state: 'pending'[\s\S]*rollback_state: 'not_run'/s, 'server execution result shell must default to not_executed/blocked/pending/not_run');
	assert.match(server, /function createExecutionResult\(\)[\s\S]*id: 'success_create_ref_recorded'[\s\S]*id: 'success_read_back_verified'[\s\S]*id: 'failure_error_translated'[\s\S]*id: 'failure_no_success_claim'[\s\S]*id: 'rollback_decision_recorded'[\s\S]*id: 'post_result_disabled_probes_verified'/s, 'server execution result shell must include pending success/failure/rollback/post-result steps');
	assert.doesNotMatch(server, /from ['"]node:fs|existsSync|readFileSync|statSync|accessSync|create_book_backup|write_lock_service|_open_piecash_book_for_write|GnuCashWriteService/, 'target preflight shell must not probe files/books or call backup/lock/write helpers');
}

function jsonResponse(res, status, body) {
	const payload = Buffer.from(JSON.stringify(body));
	res.writeHead(status, {
		'content-type': 'application/json',
		'content-length': String(payload.length)
	});
	res.end(payload);
}

function readBody(req) {
	return new Promise((resolve, reject) => {
		const chunks = [];
		req.on('data', (chunk) => chunks.push(chunk));
		req.on('end', () => {
			const raw = Buffer.concat(chunks).toString('utf8');
			if (!raw) return resolve({});
			try {
				resolve(JSON.parse(raw));
			} catch (error) {
				reject(error);
			}
		});
		req.on('error', reject);
	});
}

function isForbiddenTransactionMutation(method, pathname, search = '') {
	const upper = method.toUpperCase();
	const actionTarget = `${pathname}${search}`;
	const querySmugglesMutationBoundary = /(?:\/|%2F)(?:backups?|audit|write-alpha|owner-writebeta)(?:\/|$|[?&=])/i.test(search)
		|| /(?:\/|%2F)transactions(?:\/|%2F)(?!create-preview(?:$|[?&=]))/i.test(search)
		|| /(?:\/|%2F|[?&=])(?:validate|preflight|batch|delete|patch)(?:\/|%2F|$|[?&=])/i.test(search);
	if (/(?:\/|%2F)(?:backups?|audit|write-alpha|owner-writebeta)(?:\/|$|[?&=])/i.test(actionTarget)) return true;
	if (querySmugglesMutationBoundary) return true;
	const mentionsTransactions = pathname.includes('/transactions') || search.includes('/transactions') || /%2Ftransactions/i.test(search);
	if (!mentionsTransactions) return false;
	if (upper === 'PATCH' || upper === 'DELETE') return true;
	if (/\/transactions\/(?:validate|preflight|batch)(?:\/|$)/i.test(pathname)) return true;
	if (upper !== 'POST') return false;
	return !(pathname.endsWith('/transactions/create-preview') && search === '');
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	const previewPayloads = [];
	const server = createServer(async (req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });
		if (isForbiddenTransactionMutation(req.method ?? 'GET', url.pathname, url.search)) {
			forbiddenRequests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });
			return jsonResponse(res, 409, { detail: 'Synthetic smoke blocked a mutation endpoint.' });
		}

		try {
			if (req.method === 'GET' && url.pathname === '/health') {
				return jsonResponse(res, 200, { status: 'ok', first_run: null });
			}
			if (req.method === 'GET' && url.pathname === '/books') {
				return jsonResponse(res, 200, [syntheticBook]);
			}
			if (req.method === 'GET' && url.pathname === '/books/1/accounts') {
				return jsonResponse(res, 200, syntheticAccounts);
			}
			if (req.method === 'GET' && url.pathname === '/books/1/transactions/create-readiness-status') {
				return jsonResponse(res, 200, {
					preview_only: true,
					status: 'ready',
					writes_enabled: true,
					session_armed: true,
					create_execution_allowed: true,
					create_execution_reason: 'Synthetic unsafe status should be clamped by the web route.',
					allowed_create_count: 99,
					target_class: 'owner_selected_target',
					readiness_required: true,
					readiness_status: 'ready',
					readiness_state: {
						writes_enabled: { enabled: true, status: 'enabled_but_blocked', redacted: true },
						session_armed: { armed: true, status: 'armed', redacted: true },
						allowed_create_count: { count: 99, status: 'ready', redacted: true },
						target: { target_class: 'owner_selected_target', status: 'selected', private_target_probed: true, redacted: true },
						preflight: { required: true, status: 'ready', private_target_probed: true, redacted: true },
						backup: { required: true, status: 'ready', backup_helper_called: true, redacted: true },
						allowed_execution: { allowed: true, status: 'ready', reason: 'Synthetic unsafe status should be clamped by the web route.', redacted: true }
					}
				});
			}
			if (req.method === 'POST' && url.pathname === '/books/1/transactions/create-preview') {
				const payload = await readBody(req);
				previewPayloads.push(payload);
				if (payload.debit_account_id === payload.credit_account_id) {
					return jsonResponse(res, 422, { detail: 'debit and credit accounts must be different' });
				}
				return jsonResponse(res, 200, {
					preview_only: true,
					writes_enabled_required_for_create: true,
					create_count: 1,
					date: payload.date,
					amount: payload.amount,
					currency: payload.currency,
					description: payload.description,
					memo: payload.memo ?? '',
					debit_account: {
						id: 'smoke-source',
						name: 'Smoke Source',
						full_name: 'Synthetic Source',
						currency: 'SEK'
					},
					credit_account: {
						id: 'smoke-destination',
						name: 'Smoke Destination',
						full_name: 'Synthetic Destination',
						currency: 'SEK'
					},
					splits: [
						{ account_id: 'smoke-source', amount: `-${payload.amount}`, currency: 'SEK', memo: payload.memo ?? '' },
						{ account_id: 'smoke-destination', amount: payload.amount, currency: 'SEK', memo: payload.memo ?? '' }
					],
					warnings: ['Preview only: synthetic smoke executed no GnuCash write.']
				});
			}
			return jsonResponse(res, 404, { detail: 'Synthetic smoke endpoint not found.' });
		} catch {
			return jsonResponse(res, 500, { detail: 'Synthetic smoke stub failed safely.' });
		}
	});

	await new Promise((resolve, reject) => {
		server.once('error', reject);
		server.listen(0, '127.0.0.1', resolve);
	});
	const address = server.address();
	return {
		url: `http://127.0.0.1:${address.port}`,
		requests,
		forbiddenRequests,
		previewPayloads,
		close: () => new Promise((resolve) => server.close(resolve))
	};
}

function getFreePort() {
	return new Promise((resolve, reject) => {
		const server = net.createServer();
		server.once('error', reject);
		server.listen(0, '127.0.0.1', () => {
			const address = server.address();
			server.close(() => resolve(address.port));
		});
	});
}

function waitForHttp(url, timeoutMs = 30000) {
	const started = Date.now();
	return new Promise((resolve, reject) => {
		async function tick() {
			try {
				const response = await fetch(url);
				if (response.status < 500) return resolve();
			} catch {
				// keep polling until timeout
			}
			if (Date.now() - started > timeoutMs) {
				return reject(new Error(`Timed out waiting for ${url}`));
			}
			setTimeout(tick, 250);
		}
		tick();
	});
}

function spawnLogged(command, args, options) {
	const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
	let output = '';
	for (const stream of [child.stdout, child.stderr]) {
		stream.on('data', (chunk) => {
			output += chunk.toString('utf8');
			output = output.slice(-12000);
		});
	}
	child.outputTail = () => output;
	return child;
}

async function stopProcess(child) {
	if (!child || child.exitCode !== null || child.killed) return;
	await new Promise((resolve) => {
		child.once('exit', resolve);
		child.kill('SIGTERM');
		setTimeout(() => {
			if (child.exitCode === null && !child.killed) child.kill('SIGKILL');
		}, 3000).unref();
	});
}

class CdpClient {
	constructor(wsUrl) {
		this.wsUrl = wsUrl;
		this.nextId = 1;
		this.pending = new Map();
		this.handlers = new Map();
	}

	async connect() {
		this.ws = new WebSocket(this.wsUrl);
		await new Promise((resolve, reject) => {
			this.ws.addEventListener('open', resolve, { once: true });
			this.ws.addEventListener('error', reject, { once: true });
		});
		this.ws.addEventListener('message', (event) => {
			const message = JSON.parse(event.data);
			if (message.id) {
				const pending = this.pending.get(message.id);
				if (!pending) return;
				this.pending.delete(message.id);
				if (message.error) pending.reject(new Error(`${message.error.message}: ${JSON.stringify(message.error.data ?? '')}`));
				else pending.resolve(message.result ?? {});
				return;
			}
			const handlers = this.handlers.get(message.method) ?? [];
			for (const handler of handlers) handler(message.params ?? {});
		});
	}

	on(method, handler) {
		const handlers = this.handlers.get(method) ?? [];
		handlers.push(handler);
		this.handlers.set(method, handlers);
	}

	send(method, params = {}) {
		const id = this.nextId++;
		this.ws.send(JSON.stringify({ id, method, params }));
		return new Promise((resolve, reject) => {
			this.pending.set(id, { resolve, reject });
			setTimeout(() => {
				if (!this.pending.has(id)) return;
				this.pending.delete(id);
				reject(new Error(`CDP command timed out: ${method}`));
			}, 10000).unref();
		});
	}

	close() {
		this.ws?.close();
	}
}

async function connectCdp(debugPort) {
	await waitForHttp(`http://127.0.0.1:${debugPort}/json/list`, 30000);
	const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
	const target = targets.find((item) => item.type === 'page') ?? targets[0];
	assert.ok(target?.webSocketDebuggerUrl, 'Chromium CDP page target must expose a websocket URL');
	const cdp = new CdpClient(target.webSocketDebuggerUrl);
	await cdp.connect();
	return cdp;
}

async function evaluate(cdp, expression, options = {}) {
	const result = await cdp.send('Runtime.evaluate', {
		expression,
		awaitPromise: options.awaitPromise ?? false,
		returnByValue: true,
		userGesture: true
	});
	if (result.exceptionDetails) {
		throw new Error(`Browser evaluation failed: ${JSON.stringify(result.exceptionDetails)}`);
	}
	return result.result?.value;
}

async function waitForExpression(cdp, expression, label, timeoutMs = 10000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		if (await evaluate(cdp, expression)) return;
		await new Promise((resolve) => setTimeout(resolve, 150));
	}
	throw new Error(`Timed out waiting for browser condition: ${label}`);
}

function jsString(value) {
	return JSON.stringify(value);
}

async function setInput(cdp, selector, value) {
	await evaluate(cdp, `(() => {
		const element = document.querySelector(${jsString(selector)});
		if (!element) throw new Error('missing input ' + ${jsString(selector)});
		element.value = ${jsString(value)};
		element.dispatchEvent(new Event('input', { bubbles: true }));
		element.dispatchEvent(new Event('change', { bubbles: true }));
		return true;
	})()`);
}

async function setSelect(cdp, selector, value) {
	await evaluate(cdp, `(() => {
		const element = document.querySelector(${jsString(selector)});
		if (!element) throw new Error('missing select ' + ${jsString(selector)});
		element.value = ${jsString(value)};
		element.dispatchEvent(new Event('change', { bubbles: true }));
		return true;
	})()`);
}

async function click(cdp, selector) {
	await evaluate(cdp, `(() => {
		const element = document.querySelector(${jsString(selector)});
		if (!element) throw new Error('missing clickable ' + ${jsString(selector)});
		element.click();
		return true;
	})()`);
}

async function assertDisabledButtonInert(cdp, selector, expectedText, browserRequests, label) {
	const state = await evaluate(cdp, `(() => {
		const button = document.querySelector(${jsString(selector)});
		if (!button) return null;
		return {
			disabled: button.disabled,
			type: button.type,
			text: button.textContent.replace(/\\s+/g, ' ').trim(),
			formAttribute: button.getAttribute('form'),
			formaction: button.getAttribute('formaction'),
			name: button.getAttribute('name'),
			valueAttribute: button.getAttribute('value'),
			ariaDescribedBy: button.getAttribute('aria-describedby') ?? ''
		};
	})()`);
	assert.ok(state, `${label} disabled button must be rendered`);
	assert.equal(state.disabled, true, `${label} disabled button must stay disabled`);
	assert.equal(state.type, 'button', `${label} disabled button must stay non-submitting`);
	assert.equal(state.formAttribute, null, `${label} disabled button must not attach to a form by attribute`);
	assert.equal(state.formaction, null, `${label} disabled button must not expose a form action`);
	assert.equal(state.name, null, `${label} disabled button must not expose a submitted name`);
	assert.equal(state.valueAttribute, null, `${label} disabled button must not expose a submitted value`);
	assert.equal(state.text, expectedText, `${label} disabled button label must remain explicit`);
	assert.match(state.ariaDescribedBy, /preview-no-write-warning/, `${label} disabled button must reference the no-write boundary`);
	assert.match(state.ariaDescribedBy, /write-session-gate/, `${label} disabled button must reference the write-session gate`);
	assert.match(state.ariaDescribedBy, /target-preflight-readiness/, `${label} disabled button must reference the target preflight shell`);
	assert.match(state.ariaDescribedBy, /execution-readiness-shell/, `${label} disabled button must reference the execution readiness shell`);
	assert.match(state.ariaDescribedBy, /execution-result-shell/, `${label} disabled button must reference the execution result shell`);

	const previewPostCountBefore = browserRequests.filter((request) => request.method === 'POST' && new URL(request.url).pathname === '/transactions/new').length;
	const forbiddenCountBefore = forbiddenBrowserMutationRequests(browserRequests).length;
	await click(cdp, selector);
	await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 250))`, { awaitPromise: true });
	assert.equal(
		browserRequests.filter((request) => request.method === 'POST' && new URL(request.url).pathname === '/transactions/new').length,
		previewPostCountBefore,
		`${label} disabled button click must not submit the preview action`
	);
	assert.equal(forbiddenBrowserMutationRequests(browserRequests).length, forbiddenCountBefore, `${label} disabled button click must not issue mutation-capable browser requests`);
}

async function assertPreviewOnlyRuntimeTopology(cdp, label) {
	const topology = await evaluate(cdp, `(() => {
		const previewForm = document.querySelector('#transaction-preview-form');
		const featureControls = ['#copy-approval-template', '#future-create-disabled', '#preview-reviewed-confirmation'].map((selector) => {
			const control = document.querySelector(selector);
			return {
				selector,
				present: Boolean(control),
				closestFormId: control?.closest('form')?.id ?? null,
				formAttribute: control?.getAttribute('form') ?? null,
				formAction: control?.getAttribute('formaction') ?? null,
				name: control?.getAttribute('name') ?? null,
				value: control?.getAttribute('value') ?? null,
				type: control?.getAttribute('type') ?? null
			};
		});
		return {
			previewFormPresent: Boolean(previewForm),
			previewFormMethod: previewForm?.method.toLowerCase() ?? null,
			previewFormAction: previewForm?.getAttribute('action') ?? null,
			previewSubmitTargets: Array.from(previewForm?.querySelectorAll('button[type="submit"]') ?? []).map((button) => ({
				text: button.textContent.replace(/\\s+/g, ' ').trim(),
				formAction: button.getAttribute('formaction'),
				closestFormId: button.closest('form')?.id ?? null,
				name: button.getAttribute('name'),
				value: button.getAttribute('value')
			})),
			featureControls
		};
	})()`);
	assert.equal(topology.previewFormPresent, true, `${label}: transaction preview form must be present`);
	assert.equal(topology.previewFormMethod, 'post', `${label}: the transaction preview form must be POST`);
	assert.equal(topology.previewFormAction, null, `${label}: preview form must not define a page-level action`);
	assert.deepEqual(topology.previewSubmitTargets, [{ text: 'Preview transaction', formAction: '?/preview', closestFormId: 'transaction-preview-form', name: null, value: null }], `${label}: the only preview-form submit control must target the preview action`);
	for (const control of topology.featureControls) {
		if (!control.present) continue;
		assert.equal(control.closestFormId, null, `${label}: ${control.selector} must remain outside the preview submission form`);
		assert.equal(control.formAttribute, null, `${label}: ${control.selector} must not attach to a form`);
		assert.equal(control.formAction, null, `${label}: ${control.selector} must not expose a form action`);
		assert.equal(control.name, null, `${label}: ${control.selector} must not submit a name`);
		assert.equal(control.value, null, `${label}: ${control.selector} must not submit a value`);
	}
}

async function assertMobilePreviewUx(cdp, label, { confirmation = false, stale = false } = {}) {
	const state = await evaluate(cdp, `(() => {
		const text = (selector) => document.querySelector(selector)?.innerText ?? '';
		const visible = (selector) => {
			const element = document.querySelector(selector);
			return Boolean(element && getComputedStyle(element).display !== 'none');
		};
		return {
			viewportWidth: document.documentElement.clientWidth,
			scrollWidth: document.documentElement.scrollWidth,
			pathText: text('#mobile-preview-path-card'),
			pathVisible: visible('#mobile-preview-path-card'),
			actionBarText: text('#preview-mobile-action-bar'),
			actionBarClass: document.querySelector('#preview-mobile-action-bar')?.className ?? '',
			confirmationPresent: Boolean(document.querySelector('#mobile-confirmation-status-card')),
			confirmationVisible: visible('#mobile-confirmation-status-card'),
			confirmationText: text('#mobile-confirmation-status-card')
		};
	})()`);
	assert.ok(state.scrollWidth <= state.viewportWidth + 8, `${label}: mobile viewport must not have obvious horizontal overflow (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.equal(state.pathVisible, true, `${label}: mobile preview path card must be visible at narrow width`);
	assert.match(state.pathText, /Mobile preview path/, `${label}: mobile path card title must render`);
	assert.match(state.pathText, /Tap Preview transaction; this is the only submitting action/, `${label}: mobile path card must identify the only submit action`);
	assert.match(state.pathText, /no CREATE\/PATCH\/DELETE\/batch action is available/, `${label}: mobile path card must repeat the no-write boundary`);
	assert.match(state.actionBarClass, /sticky bottom-0/, `${label}: mobile action bar must keep sticky bottom classes`);
	assert.match(state.actionBarText, /Preview transaction/, `${label}: mobile action bar must expose preview submit copy`);
	assert.match(state.actionBarText, /Create disabled/, `${label}: mobile action bar must keep disabled create copy`);
	if (!confirmation) {
		assert.equal(state.confirmationPresent, false, `${label}: mobile confirmation status must be absent before successful preview`);
		return;
	}
	assert.equal(state.confirmationVisible, true, `${label}: mobile confirmation status must be visible after successful preview`);
	assert.match(state.confirmationText, /Mobile confirmation status/, `${label}: mobile confirmation status title must render`);
	assert.match(state.confirmationText, /Future Create: disabled/i, `${label}: mobile confirmation status must keep Future Create disabled`);
	assert.match(state.confirmationText, /Copy helper: placeholders only/i, `${label}: mobile confirmation status must keep copy helper redacted`);
	assert.match(state.confirmationText, /No write path is enabled/, `${label}: mobile confirmation status must repeat no-write boundary`);
	if (stale) {
		assert.match(state.confirmationText, /Stale — run Preview transaction again/, `${label}: stale mobile confirmation must require re-preview`);
	} else {
		assert.match(state.confirmationText, /Current non-mutating preview response ready for local review/, `${label}: current mobile confirmation must identify the non-mutating preview`);
	}
}

function assertNoMutationRequestsObserved(api, browserRequests, label) {
	assert.deepEqual(forbiddenBrowserMutationRequests(browserRequests), [], `${label}: browser must not issue CREATE/PATCH/DELETE/batch/validate/preflight/backup/audit/write-beta boundary requests`);
	assert.deepEqual(api.forbiddenRequests, [], `${label}: synthetic API boundary must not observe blocked mutation requests`);
	assert.deepEqual(
		api.requests.filter((request) => isForbiddenTransactionMutation(request.method ?? 'GET', request.path, request.search ?? '')),
		[],
		`${label}: synthetic API stub must observe zero validate/preflight/backup/audit/write-beta boundary requests`
	);
}

async function assertReadinessShellsRemainPending(cdp, label) {
	const shellState = await evaluate(cdp, `(() => {
		const text = (selector) => document.querySelector(selector)?.innerText ?? '';
		return {
			targetText: text('#target-preflight-readiness'),
			executionText: text('#execution-readiness-shell'),
			readinessText: text('#redacted-create-readiness-state'),
			preflightStatuses: Array.from(document.querySelectorAll('[data-preflight-status]')).map((item) => item.getAttribute('data-preflight-status')),
			executionStatuses: Array.from(document.querySelectorAll('[data-execution-readiness-status]')).map((item) => item.getAttribute('data-execution-readiness-status')),
			evidenceText: text('#execution-evidence-packet-plan'),
			evidencePacketStatuses: Array.from(document.querySelectorAll('[data-execution-evidence-status]')).map((item) => item.getAttribute('data-execution-evidence-status')),
			disabledProbeText: text('#disabled-probe-readiness-matrix'),
			disabledProbeStatuses: Array.from(document.querySelectorAll('[data-disabled-probe-status]')).map((item) => item.getAttribute('data-disabled-probe-status'))
		};
	})()`);
	assert.match(shellState.targetText, /Target readiness not checked/, `${label}: target readiness must stay not checked`);
	assert.match(shellState.targetText, /target_preflight\.target_class: pending/, `${label}: target class must stay pending`);
	assert.deepEqual(shellState.preflightStatuses, Array(13).fill('pending'), `${label}: target preflight checks must stay pending`);
	assert.match(shellState.executionText, /Execution readiness not checked/, `${label}: execution readiness must stay not checked`);
	assert.match(shellState.executionText, /backup_state: pending/, `${label}: backup readiness must stay pending`);
	assert.match(shellState.executionText, /probe_state: pending/, `${label}: probe readiness must stay pending`);
	assert.deepEqual(shellState.executionStatuses, Array(9).fill('pending'), `${label}: execution readiness checks must stay pending`);
	assert.match(shellState.evidenceText, /Future evidence packet plan \(pending\)/, `${label}: execution evidence packet plan must remain visible`);
	assert.match(shellState.evidenceText, /evidence are pending and not collected/, `${label}: execution evidence packet plan must stay not collected`);
	assert.deepEqual(shellState.evidencePacketStatuses, Array(6).fill('pending'), `${label}: execution evidence packet steps must stay pending`);
	assert.match(shellState.disabledProbeText, /Disabled-write probe matrix \(pending\)/, `${label}: disabled-probe matrix must remain visible`);
	assert.match(shellState.disabledProbeText, /validate\/preflight\/CREATE\/PATCH\/DELETE\/batch probes are pending and not executed/, `${label}: disabled-probe matrix must stay not executed`);
	assert.deepEqual(shellState.disabledProbeStatuses, Array(6).fill('pending'), `${label}: disabled-probe matrix entries must stay pending`);
	assert.match(shellState.readinessText, /session_armed status\s+not_armed/, `${label}: redacted readiness must stay unarmed`);
	assert.match(shellState.readinessText, /allowed execution status\s+blocked; allowed false/, `${label}: redacted readiness must keep execution blocked`);
	assert.ok(!shellState.readinessText.includes('count 99'), `${label}: unsafe readiness counts must not render`);
	assert.ok(!/target_preflight\.status:\s*(?:ready|passed|ok)/i.test(shellState.targetText), `${label}: target readiness must not render ready/passed status`);
	assert.ok(!/execution_readiness\.status:\s*(?:ready|passed|ok)/i.test(shellState.executionText), `${label}: execution readiness must not render ready/passed status`);
	assert.ok(!/private probe true|helper called true|allowed true|session_armed status\s+armed|allowed execution status\s+ready/i.test(shellState.readinessText), `${label}: unsafe active readiness details must stay clamped out of the UI`);
}

async function assertExecutionResultShellRemainsPending(cdp, label) {
	const executionResultState = await evaluate(cdp, `(() => {
		const text = (selector) => document.querySelector(selector)?.innerText ?? '';
		return {
			executionResultText: text('#execution-result-shell'),
			executionResultStatuses: Array.from(document.querySelectorAll('[data-execution-result-status]')).map((item) => item.getAttribute('data-execution-result-status')),
			executionResultSteps: Array.from(document.querySelectorAll('[data-execution-result-step]')).map((item) => item.getAttribute('data-execution-result-step'))
		};
	})()`);
	assert.match(executionResultState.executionResultText, /Execution-result UX shell \(not run\)/, `${label}: execution-result shell must remain visible`);
	assert.match(executionResultState.executionResultText, /execution_result\.status\s+not_executed/, `${label}: execution-result status must stay not_executed`);
	assert.match(executionResultState.executionResultText, /create_result_state\s+blocked/, `${label}: create result must stay blocked`);
	assert.match(executionResultState.executionResultText, /success_state\s+pending/, `${label}: success state must stay pending`);
	assert.match(executionResultState.executionResultText, /failure_state\s+pending/, `${label}: failure state must stay pending`);
	assert.match(executionResultState.executionResultText, /rollback_state\s+not_run/, `${label}: rollback state must stay not_run`);
	assert.match(executionResultState.executionResultText, /no success or failure result is claimed/, `${label}: no success/failure claim copy must stay visible`);
	assert.match(executionResultState.executionResultText, /Result outcome legend \(disabled\)/, `${label}: result outcome legend must stay visible`);
	assert.match(executionResultState.executionResultText, /Do not infer success from preview or approval copy/, `${label}: result legend must prevent preview-as-success interpretation`);
	assert.match(executionResultState.executionResultText, /Rollback\/restore: owner-approved recovery path only/, `${label}: rollback legend must stay owner-approved and non-mutating`);
	assert.match(executionResultState.executionResultText, /Disabled result triage/, `${label}: execution-result triage panel must stay visible`);
	assert.match(executionResultState.executionResultText, /Current state: no CREATE execution attempted; preview data is not a success result/, `${label}: triage panel must keep preview separate from success`);
	assert.match(executionResultState.executionResultText, /Success requires redacted CREATE reference and private read-back before any success copy/, `${label}: triage panel must state success evidence requirements`);
	assert.match(executionResultState.executionResultText, /Failure state keeps success blocked until a safe error is translated/, `${label}: triage panel must state failure/no-success boundary`);
	assert.match(executionResultState.executionResultText, /Rollback state remains owner-approved recovery only and is not run from this page/, `${label}: triage panel must keep rollback disabled`);
	assert.match(executionResultState.executionResultText, /Post-result reset\/probe state stays pending until GNUCASH_WRITES_ENABLED=false is verified/, `${label}: triage panel must require reset/probe evidence before result completion`);
	assert.match(executionResultState.executionResultText, /performs no restore and emits no success claim/, `${label}: rollback/no-success boundary must stay visible`);
	assert.deepEqual(executionResultState.executionResultStatuses, Array(6).fill('pending'), `${label}: execution-result steps must stay pending`);
	assert.deepEqual(
		executionResultState.executionResultSteps,
		['success_create_ref_recorded', 'success_read_back_verified', 'failure_error_translated', 'failure_no_success_claim', 'rollback_decision_recorded', 'post_result_disabled_probes_verified'],
		`${label}: execution-result shell must keep exact success/failure/rollback/post-result step IDs`
	);
	assert.ok(!/execution_result\.status\s+(?:success|failed|rolled_back)|rollback_state\s+(?:run|complete)|success_state\s+(?:done|success)/i.test(executionResultState.executionResultText), `${label}: execution-result shell must not render completed result states`);
}

async function assertApprovalPacketAbsent(cdp, label) {
	const state = await evaluate(cdp, `(() => ({
		approvalPacket: Boolean(document.querySelector('#approval-packet')),
		futureCreate: Boolean(document.querySelector('#future-create-disabled')),
		previewReviewed: Boolean(document.querySelector('#preview-reviewed-confirmation')),
		copyTemplate: Boolean(document.querySelector('#copy-approval-template'))
	}))()`);
	assert.deepEqual(
		state,
		{ approvalPacket: false, futureCreate: false, previewReviewed: false, copyTemplate: false },
		`${label}: approval packet and future-create controls must be absent before a successful preview`
	);
}

async function assertApprovalPacketControls(cdp, label, { reviewedDisabled = false } = {}) {
	const state = await evaluate(cdp, `(() => {
		const approval = document.querySelector('#approval-packet');
		const copy = document.querySelector('#copy-approval-template');
		const reviewed = document.querySelector('#preview-reviewed-confirmation');
		const future = document.querySelector('#future-create-disabled');
		return {
			approvalText: approval?.innerText ?? '',
			approvalClosestFormId: approval?.closest('form')?.id ?? null,
			safetyChecklistText: document.querySelector('#approval-packet-safety-checklist')?.innerText ?? '',
			copyType: copy?.type ?? null,
			copyFormAttribute: copy?.getAttribute('form'),
			copyFormAction: copy?.getAttribute('formaction'),
			copyName: copy?.getAttribute('name'),
			copyValue: copy?.getAttribute('value'),
			reviewedType: reviewed?.type ?? null,
			reviewedFormAttribute: reviewed?.getAttribute('form'),
			reviewedName: reviewed?.getAttribute('name'),
			reviewedDisabled: Boolean(reviewed?.disabled),
			reviewedFormId: reviewed?.form?.id ?? null,
			futureDisabled: Boolean(future?.disabled),
			futureType: future?.type ?? null,
			futureFormAttribute: future?.getAttribute('form'),
			futureFormId: future?.form?.id ?? null,
			futureName: future?.getAttribute('name'),
			futureValue: future?.getAttribute('value'),
			futureFormAction: future?.getAttribute('formaction')
		};
	})()`);
	assert.match(state.approvalText, /no approval is recorded/, `${label}: approval packet must not record approval`);
	assert.match(state.approvalText, /Future Create remains disabled/, `${label}: approval packet must keep Future Create disabled`);
	assert.match(state.approvalText, /Future CREATE count\s+1/i, `${label}: approval packet must keep exact future CREATE count visible`);
	assert.equal(state.approvalClosestFormId, null, `${label}: approval packet must remain outside the preview submission form`);
	assert.match(state.safetyChecklistText, /Fresh same-context owner approval with exact CREATE count = 1/, `${label}: approval packet checklist must require fresh exact-count owner approval`);
	assert.match(state.safetyChecklistText, /disabled-write probes for validate\/preflight\/CREATE\/PATCH\/DELETE\/batch/, `${label}: approval packet checklist must require disabled mutation probes`);
	assert.match(state.safetyChecklistText, /DELETE, batch, and balance-affecting PATCH remain forbidden/, `${label}: approval packet checklist must preserve forbidden mutation families`);
	assert.equal(state.copyType, 'button', `${label}: copy approval template control must be a non-submit button`);
	assert.equal(state.copyFormAttribute, null, `${label}: copy approval template control must not attach to a form by attribute`);
	assert.equal(state.copyFormAction, null, `${label}: copy approval template control must not expose a form action`);
	assert.equal(state.copyName, null, `${label}: copy approval template control must not expose a submitted name`);
	assert.equal(state.copyValue, null, `${label}: copy approval template control must not expose a submitted value`);
	assert.equal(state.reviewedType, 'checkbox', `${label}: preview-reviewed control must be a checkbox`);
	assert.equal(state.reviewedFormAttribute, null, `${label}: preview-reviewed checkbox must not attach to a form by attribute`);
	assert.equal(state.reviewedName, null, `${label}: preview-reviewed checkbox must be local-only and unnamed`);
	assert.equal(state.reviewedFormId, null, `${label}: preview-reviewed checkbox must remain outside the preview form`);
	assert.equal(state.reviewedDisabled, reviewedDisabled, `${label}: preview-reviewed disabled state must match preview freshness`);
	assert.equal(state.futureDisabled, true, `${label}: Future Create must stay disabled`);
	assert.equal(state.futureType, 'button', `${label}: Future Create must stay non-submitting`);
	assert.equal(state.futureFormAttribute, null, `${label}: Future Create must not attach to a form by attribute`);
	assert.equal(state.futureFormId, null, `${label}: Future Create must remain outside the preview form`);
	assert.equal(state.futureName, null, `${label}: Future Create must not expose a submitted name`);
	assert.equal(state.futureValue, null, `${label}: Future Create must not expose a submitted value`);
	assert.equal(state.futureFormAction, null, `${label}: Future Create must not expose a form action`);
}

function isForbiddenBrowserBoundaryRequest(request) {
	const method = request.method.toUpperCase();
	const url = new URL(request.url);
	const actionTarget = `${url.pathname}${url.search}`;
	if (method === 'POST' && url.pathname === '/transactions/new' && url.search === '?/preview') return false;
	if (/(?:\/|%2F)(?:backups?|audit|write-alpha|owner-writebeta)(?:\/|$|[?&=])/i.test(actionTarget)) return true;
	const mentionsTransactions = url.pathname.includes('/transactions') || url.search.includes('/transactions') || /%2Ftransactions/i.test(url.search);
	if (!mentionsTransactions) return false;
	if (method === 'PATCH' || method === 'DELETE') return true;
	if (method === 'POST') return true;
	return /(?:\/|%2F|\?\/)(?:create|validate|preflight|batch|delete|patch)(?:\/|%2F|$|[?&=])/i.test(actionTarget);
}

function forbiddenBrowserMutationRequests(requests) {
	return requests.filter(isForbiddenBrowserBoundaryRequest);
}

function assertMutationRequestPredicates() {
	const allowedApiRequests = [
		['GET', '/health', ''],
		['GET', '/books/1/transactions/create-readiness-status', ''],
		['POST', '/books/1/transactions/create-preview', '']
	];
	for (const [method, path, search] of allowedApiRequests) {
		assert.equal(isForbiddenTransactionMutation(method, path, search), false, `synthetic API boundary must allow ${method} ${path}${search}`);
	}

	const forbiddenApiRequests = [
		['POST', '/books/1/transactions', ''],
		['POST', '/books/1/transactions/create', ''],
		['POST', '/books/1/transactions/validate', ''],
		['POST', '/books/1/transactions/preflight', ''],
		['POST', '/books/1/transactions/batch', ''],
		['PATCH', '/books/1/transactions/synthetic-id', ''],
		['DELETE', '/books/1/transactions/synthetic-id', ''],
		['POST', '/books/1/backups', ''],
		['POST', '/books/1/audit', ''],
		['POST', '/books/1/write-alpha/transactions', ''],
		['POST', '/books/1/owner-writebeta/transactions', ''],
		['POST', '/books/1/transactions/create-preview', '?next=%2Fbooks%2F1%2Ftransactions%2Fbatch'],
		['POST', '/books/1/transactions/create-preview', '?next=/books/1/transactions/validate'],
		['GET', '/books/1/transactions/create-readiness-status', '?next=%2Fbooks%2F1%2Ftransactions%2Fbatch'],
		['GET', '/books/1/transactions/create-readiness-status', '?next=%2Fbooks%2F1%2Fbackups']
	];
	for (const [method, path, search] of forbiddenApiRequests) {
		assert.equal(isForbiddenTransactionMutation(method, path, search), true, `synthetic API boundary must block ${method} ${path}${search}`);
	}

	const allowedBrowserRequests = [
		{ method: 'GET', url: 'http://127.0.0.1:4173/transactions/new' },
		{ method: 'POST', url: 'http://127.0.0.1:4173/transactions/new?/preview' }
	];
	for (const request of allowedBrowserRequests) {
		assert.equal(isForbiddenBrowserBoundaryRequest(request), false, `browser boundary must allow ${request.method} ${new URL(request.url).pathname}${new URL(request.url).search}`);
	}

	const forbiddenBrowserRequests = [
		{ method: 'POST', url: 'http://127.0.0.1:4173/transactions/new' },
		{ method: 'POST', url: 'http://127.0.0.1:4173/transactions/new?/create' },
		{ method: 'POST', url: 'http://127.0.0.1:4173/transactions/new?/preview&next=%2Fbooks%2F1%2Ftransactions%2Fbatch' },
		{ method: 'GET', url: 'http://127.0.0.1:4173/transactions/new?/validate' },
		{ method: 'GET', url: 'http://127.0.0.1:4173/transactions/new?next=%2Fbooks%2F1%2Ftransactions%2Fbatch' },
		{ method: 'PATCH', url: 'http://127.0.0.1:4173/transactions/synthetic-id' },
		{ method: 'DELETE', url: 'http://127.0.0.1:4173/transactions/synthetic-id' },
		{ method: 'POST', url: 'http://127.0.0.1:4173/books/1/backups' },
		{ method: 'GET', url: 'http://127.0.0.1:4173/audit/transactions' },
		{ method: 'GET', url: 'http://127.0.0.1:4173/write-alpha/transactions' },
		{ method: 'GET', url: 'http://127.0.0.1:4173/owner-writebeta/transactions' }
	];
	for (const request of forbiddenBrowserRequests) {
		assert.equal(isForbiddenBrowserBoundaryRequest(request), true, `browser boundary must block ${request.method} ${new URL(request.url).pathname}${new URL(request.url).search}`);
	}
}

async function runSmoke() {
	assertSourceSafety();
	assertMutationRequestPredicates();
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the browser smoke');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	const profileDir = mkdtempSync(join(tmpdir(), 'gnucash-web-smoke-'));
	let webProcess;
	let chromiumProcess;
	let cdp;
	const browserRequests = [];

	try {
		webProcess = spawnLogged(process.execPath, [viteBin, 'dev', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
			cwd: root,
			env: {
				...process.env,
				API_INTERNAL_URL: api.url,
				APP_ENV: 'test',
				GNUCASH_WRITES_ENABLED: 'false',
				JWT_SECRET: 'dummy-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-browser-smoke-password'
			}
		});
		const webBase = `http://127.0.0.1:${webPort}`;
		await waitForHttp(`${webBase}/login`, 45000);

		chromiumProcess = spawnLogged(chromiumBin, [
			'--headless=new',
			'--disable-gpu',
			'--disable-dev-shm-usage',
			'--disable-background-networking',
			'--disable-component-update',
			'--disable-default-apps',
			'--disable-extensions',
			'--disable-sync',
			'--metrics-recording-only',
			'--no-first-run',
			'--no-sandbox',
			`--remote-debugging-address=127.0.0.1`,
			`--remote-debugging-port=${debugPort}`,
			`--user-data-dir=${profileDir}`,
			'--window-size=390,900',
			'about:blank'
		], { cwd: root, env: process.env });
		cdp = await connectCdp(debugPort);
		cdp.on('Network.requestWillBeSent', (params) => {
			browserRequests.push({ method: params.request.method, url: params.request.url });
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', {
			width: 390,
			height: 900,
			deviceScaleFactor: 2,
			mobile: true
		});
		await cdp.send('Network.setCookie', {
			name: 'access_token',
			value: syntheticToken,
			url: webBase,
			path: '/',
			sameSite: 'Lax'
		});
		await cdp.send('Page.navigate', { url: `${webBase}/transactions/new` });
		await waitForExpression(cdp, `document.body && document.body.innerText.includes('Preview only / no write executed')`, 'no-write warning');
		await waitForExpression(cdp, `document.body && document.body.innerText.includes('Write session not armed') && document.body.innerText.includes('CREATE execution unavailable without fresh owner approval')`, 'write-session gate');
		await waitForExpression(cdp, `document.body && document.body.innerText.includes('allowed_create_count: 0') && document.body.innerText.includes('target_class: required')`, 'write-session default status');
		await waitForExpression(cdp, `document.querySelector('#redacted-create-readiness-state')?.innerText.includes('session_armed status') && document.querySelector('#redacted-create-readiness-state')?.innerText.includes('not_armed') && document.querySelector('#redacted-create-readiness-state')?.innerText.includes('allowed execution status') && document.querySelector('#redacted-create-readiness-state')?.innerText.includes('allowed false')`, 'unsafe readiness endpoint response clamped to blocked UI status');
		await waitForExpression(cdp, `!document.body.innerText.includes('Synthetic unsafe status should be clamped by the web route.') && !document.body.innerText.includes('count 99') && !document.body.innerText.includes('ready; allowed true')`, 'unsafe readiness endpoint details not rendered');
		await waitForExpression(cdp, `Boolean(document.querySelector('#target-preflight-readiness'))`, 'target preflight panel');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('Target readiness not checked')`, 'target preflight not checked status');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('target_preflight.status: not_checked') && document.querySelector('#target-preflight-readiness')?.innerText.includes('target_preflight.target_class: pending')`, 'target preflight default status');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('Target file exists/readable') && document.querySelector('#target-preflight-readiness')?.innerText.includes('No .LCK/.LNK lock') && document.querySelector('#target-preflight-readiness')?.innerText.includes('Manual Desktop verification required')`, 'target preflight checklist');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-preflight-status]')).length === 13 && Array.from(document.querySelectorAll('[data-preflight-status]')).every((item) => item.getAttribute('data-preflight-status') === 'pending')`, 'target preflight pending checks');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-preflight-check]')).map((item) => item.getAttribute('data-preflight-check')).join('|') === 'target_class_selected|target_file_exists_readable|target_outside_repo|desktop_closed|no_concurrent_writer_lock|no_lck_lnk|no_syncthing_conflict_before|independent_backup_exists|restore_proof_available|reviewed_non_stale_preview|exact_create_count_one|reset_disabled_probes_required|manual_desktop_verification_required'`, 'target preflight exact shell checklist');
		await waitForExpression(cdp, `document.querySelector('#execution-readiness-shell')?.innerText.includes('Execution readiness not checked') && document.querySelector('#execution-readiness-shell')?.innerText.includes('execution_readiness.status: not_checked')`, 'execution readiness default status');
		await waitForExpression(cdp, `document.querySelector('#execution-readiness-shell')?.innerText.includes('Independent backup plan required') && document.querySelector('#execution-readiness-shell')?.innerText.includes('Post-CREATE read-back required') && document.querySelector('#execution-readiness-shell')?.innerText.includes('Disabled PATCH/DELETE/batch probes required')`, 'execution readiness checklist');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-readiness-status]')).length === 9 && Array.from(document.querySelectorAll('[data-execution-readiness-status]')).every((item) => item.getAttribute('data-execution-readiness-status') === 'pending')`, 'execution readiness pending checks');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-readiness-check]')).map((item) => item.getAttribute('data-execution-readiness-check')).join('|') === 'backup_plan_required|backup_readable_copy_required|post_create_read_back_required|redacted_audit_required|writes_reset_required|disabled_create_probe_required|disabled_validate_preflight_probe_required|disabled_patch_delete_batch_probes_required|manual_desktop_verification_record_required'`, 'execution readiness exact shell checklist');
		await waitForExpression(cdp, `document.querySelector('#execution-evidence-packet-plan')?.innerText.includes('Future evidence packet plan (pending)') && document.querySelector('#execution-evidence-packet-plan')?.innerText.includes('evidence are pending and not collected')`, 'execution evidence packet plan default status');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-evidence-status]')).length === 6 && Array.from(document.querySelectorAll('[data-execution-evidence-status]')).every((item) => item.getAttribute('data-execution-evidence-status') === 'pending')`, 'execution evidence packet pending checks');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-evidence-step]')).map((item) => item.getAttribute('data-execution-evidence-step')).join('|') === 'backup_before_create_evidence|read_back_after_create_evidence|audit_after_create_evidence|reset_disabled_evidence|disabled_probes_after_reset_evidence|desktop_verification_evidence'`, 'execution evidence packet exact shell checklist');
		await waitForExpression(cdp, `document.querySelector('#disabled-probe-readiness-matrix')?.innerText.includes('Disabled-write probe matrix (pending)') && document.querySelector('#disabled-probe-readiness-matrix')?.innerText.includes('blocked_or_unavailable')`, 'disabled-probe matrix default status');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-disabled-probe-status]')).length === 6 && Array.from(document.querySelectorAll('[data-disabled-probe-status]')).every((item) => item.getAttribute('data-disabled-probe-status') === 'pending')`, 'disabled-probe matrix pending checks');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-disabled-probe]')).map((item) => item.getAttribute('data-disabled-probe')).join('|') === 'validate_probe_after_reset|preflight_probe_after_reset|create_probe_after_reset|patch_probe_after_reset|delete_probe_after_reset|batch_probe_after_reset'`, 'disabled-probe exact shell checklist');
		await waitForExpression(cdp, `document.querySelector('#execution-result-shell')?.innerText.includes('Execution-result UX shell (not run)') && document.querySelector('#execution-result-shell')?.innerText.includes('rollback_state') && document.querySelector('#execution-result-outcome-legend')?.innerText.includes('Result outcome legend (disabled)') && document.querySelector('#execution-result-outcome-legend')?.innerText.includes('Do not infer success from preview or approval copy')`, 'execution result shell default status');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-result-status]')).length === 6 && Array.from(document.querySelectorAll('[data-execution-result-status]')).every((item) => item.getAttribute('data-execution-result-status') === 'pending')`, 'execution result pending checks');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-execution-result-step]')).map((item) => item.getAttribute('data-execution-result-step')).join('|') === 'success_create_ref_recorded|success_read_back_verified|failure_error_translated|failure_no_success_claim|rollback_decision_recorded|post_result_disabled_probes_verified'`, 'execution result exact shell checklist');
		await assertPreviewOnlyRuntimeTopology(cdp, 'initial page');
		await assertMobilePreviewUx(cdp, 'initial page');
		await assertReadinessShellsRemainPending(cdp, 'initial page');
		await assertExecutionResultShellRemainsPending(cdp, 'initial page');
		await assertApprovalPacketAbsent(cdp, 'initial page');
		await assertDisabledButtonInert(cdp, 'form button[type="button"][disabled]', 'Create disabled', browserRequests, 'form Create disabled');
		assertNoMutationRequestsObserved(api, browserRequests, 'initial disabled Create probe');
		await waitForExpression(cdp, `Boolean(document.querySelector('#debit-account-select') && document.querySelector('#credit-account-select'))`, 'account selectors');
		assert.deepEqual(
			await evaluate(cdp, `Array.from(document.querySelectorAll('#debit-account-select option, #credit-account-select option')).map((option) => option.value).filter(Boolean).sort()`),
			['smoke-destination', 'smoke-destination', 'smoke-source', 'smoke-source'],
			'browser selectors must expose only selectable synthetic account IDs'
		);

		await setInput(cdp, '#debit-account-search', 'Source');
		await waitForExpression(cdp, `document.querySelector('#debit-account-count')?.innerText.includes('Showing 1 of 2')`, 'source account filter count');
		await setInput(cdp, '#debit-account-search', '');
		await setInput(cdp, '#credit-account-search', 'Destination');
		await waitForExpression(cdp, `document.querySelector('#credit-account-count')?.innerText.includes('Showing 1 of 2')`, 'destination account filter count');
		await setInput(cdp, '#credit-account-search', '');

		await setInput(cdp, '#preview-date', '2026-07-05');
		await setInput(cdp, '#preview-currency', 'SEK');
		await setInput(cdp, '#preview-description', syntheticDescription);
		await setInput(cdp, '#preview-amount', syntheticAmount);
		await setInput(cdp, '#preview-memo', syntheticMemo);
		await setSelect(cdp, '#debit-account-select', 'smoke-source');
		await setSelect(cdp, '#credit-account-select', 'smoke-source');

		const sameAccountBrowserPostsBefore = browserRequests.filter((request) => request.method === 'POST' && new URL(request.url).pathname === '/transactions/new').length;
		const sameAccountApiPreviewBefore = api.requests.filter((request) => request.method === 'POST' && request.path === '/books/1/transactions/create-preview').length;
		await click(cdp, 'button[formaction="?/preview"]');
		await waitForExpression(cdp, `document.body && document.body.innerText.includes('Source and destination accounts must be different')`, 'same-account client block');
		await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 500))`, { awaitPromise: true });
		assert.equal(
			browserRequests.filter((request) => request.method === 'POST' && new URL(request.url).pathname === '/transactions/new').length,
			sameAccountBrowserPostsBefore,
			'same-account client block must not submit the preview action'
		);
		assert.equal(
			api.requests.filter((request) => request.method === 'POST' && request.path === '/books/1/transactions/create-preview').length,
			sameAccountApiPreviewBefore,
			'same-account client block must not reach create-preview'
		);
		await assertPreviewOnlyRuntimeTopology(cdp, 'same-account client block');
		await assertMobilePreviewUx(cdp, 'same-account client block');
		await assertReadinessShellsRemainPending(cdp, 'same-account client block');
		await assertExecutionResultShellRemainsPending(cdp, 'same-account client block');
		await assertApprovalPacketAbsent(cdp, 'same-account client block');
		assertNoMutationRequestsObserved(api, browserRequests, 'same-account client block');
		await setSelect(cdp, '#credit-account-select', 'smoke-destination');

		const formSnapshot = await evaluate(cdp, `(() => Object.fromEntries(new FormData(document.querySelector('button[formaction="?/preview"]').closest('form')).entries()))()`);
		assert.equal(formSnapshot.debit_account_id, 'smoke-source', 'source selector must submit the selected account id');
		assert.equal(formSnapshot.credit_account_id, 'smoke-destination', 'destination selector must submit the selected account id');
		assert.ok(!('debit-account-search' in formSnapshot) && !('credit-account-search' in formSnapshot), 'search text must not be submitted');

		await evaluate(cdp, `(() => {
			window.__smokeClipboardWrites = [];
			const smokeClipboard = {
				writeText: async (text) => { window.__smokeClipboardWrites.push(String(text)); }
			};
			Object.defineProperty(Navigator.prototype, 'clipboard', {
				configurable: true,
				get: () => smokeClipboard
			});
			Object.defineProperty(navigator, 'clipboard', {
				configurable: true,
				get: () => smokeClipboard
			});
			return navigator.clipboard === smokeClipboard;
		})()`);

		await click(cdp, 'button[formaction="?/preview"]');
		await waitForExpression(cdp, `document.body && document.body.innerText.includes('Normalized preview')`, 'normalized preview');
		await waitForExpression(cdp, `Boolean(document.querySelector('#approval-packet'))`, 'approval packet');
		await assertPreviewOnlyRuntimeTopology(cdp, 'post-preview');
		await assertMobilePreviewUx(cdp, 'post-preview', { confirmation: true });
		await assertReadinessShellsRemainPending(cdp, 'post-preview');
		await assertExecutionResultShellRemainsPending(cdp, 'post-preview');
		await assertApprovalPacketControls(cdp, 'post-preview approval packet');
		assertNoMutationRequestsObserved(api, browserRequests, 'post-preview');
		await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 1000))`, { awaitPromise: true });

		const approvalText = await evaluate(cdp, `document.querySelector('#approval-packet')?.innerText ?? ''`);
		assert.match(approvalText, /Fresh same-context owner approval with exact CREATE count = 1/, 'approval packet must require fresh owner approval and exact count');
		assert.match(approvalText, /Write session must be armed and target class\/preflight must pass/, 'approval packet must require armed session and target preflight');
		assert.match(approvalText, /Future CREATE count\s+1/i, 'approval packet must show future CREATE count 1');
		const readinessText = await evaluate(cdp, `document.querySelector('#future-create-readiness-list')?.innerText ?? ''`);
		assert.match(readinessText, /session_armed = false/, 'future create readiness must report unarmed session');
		assert.match(readinessText, /CREATE execution allowed: false/, 'future create readiness must report create execution blocked');
		assert.match(readinessText, /Target preflight status: not_checked/, 'future create readiness must report target preflight not checked');
		assert.match(readinessText, /Execution readiness status: not_checked/, 'future create readiness must report execution readiness not checked');
		assert.match(readinessText, /Execution result status: not_executed/, 'future create readiness must report execution result not executed');
		assert.match(readinessText, /rollback state is not_run/, 'future create readiness must report rollback not run');
		assert.match(readinessText, /Preview-reviewed checkbox alone is not enough/, 'future create readiness must state reviewed checkbox alone is insufficient');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.disabled === true`), true, 'Future Create must remain disabled');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.type === 'button'`), true, 'Future Create must stay a non-submit button');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.closest('form') === null`), true, 'Future Create must remain outside the preview submission form');
		assert.equal(await evaluate(cdp, `(() => {
			const button = document.querySelector('#future-create-disabled');
			return Boolean(button && !button.hasAttribute('formaction') && !button.hasAttribute('name') && !button.hasAttribute('value'));
		})()`), true, 'Future Create must not define submitted attributes');
		await assertDisabledButtonInert(cdp, '#future-create-disabled', 'Future Create disabled', browserRequests, 'post-preview Future Create');

		const renderedTemplate = await evaluate(cdp, `document.querySelector('#approval-packet pre')?.innerText ?? ''`);
		for (const privateValue of ['Synthetic Source', 'Synthetic Destination', syntheticDescription, syntheticMemo, syntheticAmount]) {
			assert.ok(!renderedTemplate.includes(privateValue), `rendered approval template must not include preview value: ${privateValue}`);
		}
		assert.match(renderedTemplate, /Target book: <selected book in web UI>/, 'rendered approval template must be placeholder-only');
		const copyPostCountBefore = browserRequests.filter((request) => request.method === 'POST').length;
		const copyForbiddenCountBefore = forbiddenBrowserMutationRequests(browserRequests).length;
		await click(cdp, '#copy-approval-template');
		await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 250))`, { awaitPromise: true });
		assert.equal(
			browserRequests.filter((request) => request.method === 'POST').length,
			copyPostCountBefore,
			'copy approval template click must not submit or call a POST endpoint'
		);
		assert.equal(
			forbiddenBrowserMutationRequests(browserRequests).length,
			copyForbiddenCountBefore,
			'copy approval template click must not call a mutation boundary endpoint'
		);
		assertNoMutationRequestsObserved(api, browserRequests, 'copy approval template');
		const copiedTemplate = await evaluate(cdp, `window.__smokeClipboardWrites?.[0] ?? ''`);
		const copyStatusText = await evaluate(cdp, `document.querySelector('#approval-packet-copy-note')?.innerText ?? ''`);
		assert.match(copyStatusText, /The copy button uses placeholders only|Redacted placeholder template copied/, 'copy approval template status must stay redacted and placeholder-only');
		if (copiedTemplate) {
			for (const privateValue of ['Synthetic Source', 'Synthetic Destination', syntheticDescription, syntheticMemo, syntheticAmount]) {
				assert.ok(!copiedTemplate.includes(privateValue), `copied approval template must not include preview value: ${privateValue}`);
			}
			assert.match(copiedTemplate, /Target book: <selected book in web UI>/, 'copied approval template must be placeholder-only');
		}
		assert.equal(await evaluate(cdp, `(window.__smokeClipboardWrites?.length ?? 0) <= 1`), true, 'approval template clipboard shim must not write more than one placeholder template');

		await click(cdp, '#preview-reviewed-confirmation');
		await waitForExpression(cdp, `document.querySelector('#preview-reviewed-confirmation')?.checked === true`, 'preview-reviewed checkbox checked');
		await waitForExpression(cdp, `document.querySelector('#preview-reviewed-status')?.innerText.includes('Preview reviewed locally') && document.querySelector('#preview-reviewed-status')?.innerText.includes('preview-reviewed checkbox alone is not enough')`, 'preview-reviewed still blocked status');
		await assertPreviewOnlyRuntimeTopology(cdp, 'reviewed preview');
		await assertMobilePreviewUx(cdp, 'reviewed preview', { confirmation: true });
		await assertApprovalPacketControls(cdp, 'reviewed approval packet');
		await assertDisabledButtonInert(cdp, '#future-create-disabled', 'Future Create disabled', browserRequests, 'reviewed Future Create');
		await assertReadinessShellsRemainPending(cdp, 'reviewed preview');
		await assertExecutionResultShellRemainsPending(cdp, 'reviewed preview');
		assertNoMutationRequestsObserved(api, browserRequests, 'reviewed preview');
		await setInput(cdp, '#preview-description', 'Synthetic browser smoke changed draft');
		await waitForExpression(cdp, `document.querySelector('#preview-stale-warning')?.innerText.includes('stale and cannot support a future owner-approved CREATE')`, 'stale warning after draft change');
		await waitForExpression(cdp, `document.querySelector('#approval-packet-copy-note')?.innerText.includes('The copy button uses placeholders only')`, 'stale resets approval copy status');
		assert.equal(await evaluate(cdp, `(window.__smokeClipboardWrites?.length ?? 0) <= 1`), true, 'stale draft must not copy another approval template');
		assert.equal(await evaluate(cdp, `document.querySelector('#preview-reviewed-confirmation')?.checked === false`), true, 'stale draft must reset local reviewed checkbox');
		assert.equal(await evaluate(cdp, `document.querySelector('#preview-reviewed-confirmation')?.disabled === true`), true, 'stale preview must disable local reviewed checkbox');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.disabled === true`), true, 'Future Create must remain disabled after stale change');
		await assertPreviewOnlyRuntimeTopology(cdp, 'stale preview');
		await assertMobilePreviewUx(cdp, 'stale preview', { confirmation: true, stale: true });
		await assertApprovalPacketControls(cdp, 'stale approval packet', { reviewedDisabled: true });
		await assertDisabledButtonInert(cdp, '#future-create-disabled', 'Future Create disabled', browserRequests, 'stale Future Create');
		await assertReadinessShellsRemainPending(cdp, 'stale preview');
		await assertExecutionResultShellRemainsPending(cdp, 'stale preview');
		assertNoMutationRequestsObserved(api, browserRequests, 'stale preview');

		await click(cdp, '#clear-preview-link');
		await waitForExpression(cdp, `!document.querySelector('#approval-packet') && document.body.innerText.includes('Preview only / no write executed')`, 'clear preview start-over state');
		await assertPreviewOnlyRuntimeTopology(cdp, 'clear preview');
		await assertMobilePreviewUx(cdp, 'clear preview');
		await assertApprovalPacketAbsent(cdp, 'clear preview');
		await assertReadinessShellsRemainPending(cdp, 'clear preview');
		await assertExecutionResultShellRemainsPending(cdp, 'clear preview');
		assertNoMutationRequestsObserved(api, browserRequests, 'clear preview');

		assertNoMutationRequestsObserved(api, browserRequests, 'final browser smoke');
		const createReadinessStatusCalls = api.requests.filter((request) => request.method === 'GET' && request.path === '/books/1/transactions/create-readiness-status');
		assert.ok(createReadinessStatusCalls.length >= 1, 'browser smoke must load create-readiness-status as read-only status');
		const createPreviewCalls = api.requests.filter((request) => request.method === 'POST' && request.path === '/books/1/transactions/create-preview');
		assert.equal(createPreviewCalls.length, 1, 'browser smoke must call create-preview exactly once through the server action');
		assert.equal(api.previewPayloads.length, 1, 'synthetic API stub must capture exactly one create-preview payload');
		const previewPayload = api.previewPayloads[0];
		assert.deepEqual(
			Object.keys(previewPayload).sort(),
			['amount', 'credit_account_id', 'currency', 'date', 'debit_account_id', 'description', 'memo'].sort(),
			'create-preview payload must contain only preview API fields'
		);
		assert.equal(previewPayload.debit_account_id, 'smoke-source', 'create-preview payload must submit only the selected source account id');
		assert.equal(previewPayload.credit_account_id, 'smoke-destination', 'create-preview payload must submit only the selected destination account id');
		assert.equal(previewPayload.amount, syntheticAmount, 'create-preview payload must preserve the decimal amount string');
		assert.equal(previewPayload.currency, 'SEK', 'create-preview payload must submit the selected currency code');
		for (const forbiddenPayloadField of [
			'book_id',
			'debit-account-search',
			'credit-account-search',
			'previewReviewed',
			'approvalTemplateCopied',
			'writeSessionGate',
			'targetPreflight',
			'executionReadiness',
			'executionResult',
			'evidence_packet_plan',
			'disabled_probe_plan',
			'create_execution_allowed',
			'allowed_create_count'
		]) {
			assert.ok(!(forbiddenPayloadField in previewPayload), `create-preview payload must not submit local-only field: ${forbiddenPayloadField}`);
		}
		const transactionEntryAppSubmissions = browserRequests.filter((request) => {
			const url = new URL(request.url);
			return request.method === 'POST' && url.pathname === '/transactions/new';
		});
		assert.deepEqual(
			transactionEntryAppSubmissions.map((request) => new URL(request.url).search),
			['?/preview'],
			'browser must submit the transaction-entry form exactly once and only to the preview action'
		);
	} catch (error) {
		if (webProcess) console.error(`web-server-output-tail:\n${webProcess.outputTail()}`);
		if (chromiumProcess) console.error(`chromium-output-tail:\n${chromiumProcess.outputTail()}`);
		throw error;
	} finally {
		cdp?.close();
		await stopProcess(chromiumProcess);
		await stopProcess(webProcess);
		await api.close();
		rmSync(profileDir, { recursive: true, force: true });
	}
}

await runSmoke();
console.log('transaction-entry-preview-browser: ok (synthetic, writes-disabled, no mutation requests)');
