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
	assert.match(page, /id="armed-session-requirements"[\s\S]*Target class required[\s\S]*Exact CREATE count required[\s\S]*preview-reviewed checkbox alone is not enough/s, 'armed-session requirements panel must remain disabled placeholder guidance');
	assert.match(page, /id="target-preflight-readiness"[\s\S]*Target preflight required[\s\S]*Target readiness not checked[\s\S]*Default state: all target readiness checks are pending \/ not checked \/ not armed/s, 'target preflight shell must default to not checked/pending');
	assert.match(page, /id="target-preflight-checklist"/, 'target preflight checklist must be rendered');
	for (const targetPreflightLabel of ['Target file exists/readable', 'Target is outside repo', 'GnuCash Desktop closed', 'No .LCK/.LNK lock', 'Manual Desktop verification required']) {
		assert.ok(page.includes(targetPreflightLabel), `target preflight checklist missing label: ${targetPreflightLabel}`);
	}
	assert.doesNotMatch(page, /data-preflight-status="(?:checked|passed|ready|ok)"/, 'target preflight shell must not mark checks passed by default');
	assert.match(page, /id="approval-packet"[\s\S]*Future Create remains disabled/s, 'approval packet must stay visible and no-write');
	assert.match(page, /id="preview-stale-warning"[\s\S]*stale and cannot support a future owner-approved CREATE/s, 'stale-preview warning must remain present');
	assert.match(page, /id="future-create-disabled"[\s\S]*type="button"[\s\S]*disabled/s, 'Future Create must remain disabled and non-submitting');
	assert.match(page, /navigator\.clipboard\.writeText\(safeApprovalTemplate\)/, 'copy button must use the static placeholder-only approval template');
	assert.doesNotMatch(page, /clipboard\.writeText\([^)]*preview\./, 'copy button must not copy private preview values');
	assert.doesNotMatch(page, /localStorage|sessionStorage/, 'preview smoke requires no browser storage persistence');
	assert.match(server, /export const actions: Actions = \{\s*preview:\s*async/s, '/transactions/new must expose only the preview action');
	assert.deepEqual(
		[...new Set([...server.matchAll(/\/transactions(?:\/create-preview|\/validate)?/g)].map((match) => match[0]))],
		['/transactions/create-preview'],
		'create-preview must remain the only transaction submission target in /transactions/new server code'
	);
	assert.doesNotMatch(server, /\b(?:create|validate)\s*:\s*async/, '/transactions/new must not define active create or validate actions');
	assert.doesNotMatch(server, /\/transactions\/validate|`\/books\/\$\{bookId\}\/transactions`|hasWriteAcknowledgement/, '/transactions/new must not call validate/write API paths');
	assert.match(server, /function createWriteSessionGate\(\)[\s\S]*const sessionArmed = false[\s\S]*const allowedCreateCount = 0[\s\S]*create_execution_allowed: false/s, 'server write-session gate must default to unarmed and CREATE-disabled');
	assert.match(server, /function createTargetPreflight\(\)[\s\S]*required: true[\s\S]*status: 'not_checked'[\s\S]*target_class: targetClass[\s\S]*status: 'pending'/s, 'server target preflight must default to required/not_checked/pending');
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

function isForbiddenTransactionMutation(method, pathname) {
	const upper = method.toUpperCase();
	if (!pathname.includes('/transactions')) return false;
	if (upper === 'PATCH' || upper === 'DELETE') return true;
	if (upper !== 'POST') return false;
	return !pathname.endsWith('/transactions/create-preview');
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	const server = createServer(async (req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname });
		if (isForbiddenTransactionMutation(req.method ?? 'GET', url.pathname)) {
			forbiddenRequests.push({ method: req.method, path: url.pathname });
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
			if (req.method === 'POST' && url.pathname === '/books/1/transactions/create-preview') {
				const payload = await readBody(req);
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

function forbiddenBrowserMutationRequests(requests) {
	return requests.filter((request) => {
		const method = request.method.toUpperCase();
		if (!['POST', 'PATCH', 'DELETE'].includes(method)) return false;
		const url = new URL(request.url);
		if (!url.pathname.includes('/transactions')) return false;
		if (method === 'POST' && url.pathname === '/transactions/new' && url.search.includes('/preview')) return false;
		return true;
	});
}

async function runSmoke() {
	assertSourceSafety();
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
		await waitForExpression(cdp, `Boolean(document.querySelector('#target-preflight-readiness'))`, 'target preflight panel');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('Target readiness not checked')`, 'target preflight not checked status');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('target_preflight.status: not_checked') && document.querySelector('#target-preflight-readiness')?.innerText.includes('target_preflight.target_class: pending')`, 'target preflight default status');
		await waitForExpression(cdp, `document.querySelector('#target-preflight-readiness')?.innerText.includes('Target file exists/readable') && document.querySelector('#target-preflight-readiness')?.innerText.includes('No .LCK/.LNK lock') && document.querySelector('#target-preflight-readiness')?.innerText.includes('Manual Desktop verification required')`, 'target preflight checklist');
		await waitForExpression(cdp, `Array.from(document.querySelectorAll('[data-preflight-status]')).length >= 13 && Array.from(document.querySelectorAll('[data-preflight-status]')).every((item) => item.getAttribute('data-preflight-status') === 'pending')`, 'target preflight pending checks');
		await waitForExpression(cdp, `Boolean(document.querySelector('#debit-account-select') && document.querySelector('#credit-account-select'))`, 'account selectors');

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
		await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 1000))`, { awaitPromise: true });

		const approvalText = await evaluate(cdp, `document.querySelector('#approval-packet')?.innerText ?? ''`);
		assert.match(approvalText, /Fresh same-context owner approval with exact CREATE count = 1/, 'approval packet must require fresh owner approval and exact count');
		assert.match(approvalText, /Write session must be armed and target class\/preflight must pass/, 'approval packet must require armed session and target preflight');
		assert.match(approvalText, /Future CREATE count\s+1/i, 'approval packet must show future CREATE count 1');
		const readinessText = await evaluate(cdp, `document.querySelector('#future-create-readiness-list')?.innerText ?? ''`);
		assert.match(readinessText, /session_armed = false/, 'future create readiness must report unarmed session');
		assert.match(readinessText, /CREATE execution allowed: false/, 'future create readiness must report create execution blocked');
		assert.match(readinessText, /Target preflight status: not_checked/, 'future create readiness must report target preflight not checked');
		assert.match(readinessText, /Preview-reviewed checkbox alone is not enough/, 'future create readiness must state reviewed checkbox alone is insufficient');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.disabled === true`), true, 'Future Create must remain disabled');

		const renderedTemplate = await evaluate(cdp, `document.querySelector('#approval-packet pre')?.innerText ?? ''`);
		for (const privateValue of ['Synthetic Source', 'Synthetic Destination', syntheticDescription, syntheticMemo, syntheticAmount]) {
			assert.ok(!renderedTemplate.includes(privateValue), `rendered approval template must not include preview value: ${privateValue}`);
		}
		assert.match(renderedTemplate, /Target book: <selected book in web UI>/, 'rendered approval template must be placeholder-only');
		await click(cdp, '#copy-approval-template');
		await evaluate(cdp, `new Promise((resolve) => setTimeout(resolve, 250))`, { awaitPromise: true });
		const copiedTemplate = await evaluate(cdp, `window.__smokeClipboardWrites?.[0] ?? ''`);
		if (copiedTemplate) {
			for (const privateValue of ['Synthetic Source', 'Synthetic Destination', syntheticDescription, syntheticMemo, syntheticAmount]) {
				assert.ok(!copiedTemplate.includes(privateValue), `copied approval template must not include preview value: ${privateValue}`);
			}
			assert.match(copiedTemplate, /Target book: <selected book in web UI>/, 'copied approval template must be placeholder-only');
		}

		await click(cdp, '#preview-reviewed-confirmation');
		await waitForExpression(cdp, `document.querySelector('#preview-reviewed-confirmation')?.checked === true`, 'preview-reviewed checkbox checked');
		await setInput(cdp, '#preview-description', 'Synthetic browser smoke changed draft');
		await waitForExpression(cdp, `document.querySelector('#preview-stale-warning')?.innerText.includes('stale and cannot support a future owner-approved CREATE')`, 'stale warning after draft change');
		assert.equal(await evaluate(cdp, `document.querySelector('#preview-reviewed-confirmation')?.checked === false`), true, 'stale draft must reset local reviewed checkbox');
		assert.equal(await evaluate(cdp, `document.querySelector('#preview-reviewed-confirmation')?.disabled === true`), true, 'stale preview must disable local reviewed checkbox');
		assert.equal(await evaluate(cdp, `document.querySelector('#future-create-disabled')?.disabled === true`), true, 'Future Create must remain disabled after stale change');

		await click(cdp, '#clear-preview-link');
		await waitForExpression(cdp, `!document.querySelector('#approval-packet') && document.body.innerText.includes('Preview only / no write executed')`, 'clear preview start-over state');

		const unsafeBrowserRequests = forbiddenBrowserMutationRequests(browserRequests);
		assert.deepEqual(unsafeBrowserRequests, [], 'browser must not issue CREATE/PATCH/DELETE/batch transaction requests');
		assert.deepEqual(api.forbiddenRequests, [], 'synthetic API stub must not receive mutation requests');
		const createPreviewCalls = api.requests.filter((request) => request.method === 'POST' && request.path === '/books/1/transactions/create-preview');
		assert.equal(createPreviewCalls.length, 1, 'browser smoke must call create-preview exactly once through the server action');
		assert.ok(browserRequests.some((request) => request.method === 'POST' && new URL(request.url).pathname === '/transactions/new'), 'browser must submit only the /transactions/new preview action');
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
