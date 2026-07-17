import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(root, '.svelte-kit', 'output', 'server', 'index.js');
const smokeHome = process.env.TRANSACTION_CREATE_PRODUCT_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.TRANSACTION_CREATE_PRODUCT_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-transaction-create-product');
const cdpCommandTimeoutMs = 120000;
const token = 'synthetic-product-create-token';
const accountA = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const accountB = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const previewToken = 'pt1.synthetic.payload.signature';
const idempotencyKey = '11111111-2222-4333-8444-555555555555';

function resolveChromiumBin() {
	if (process.env.CHROMIUM_BIN) return process.env.CHROMIUM_BIN;
	for (const candidate of [
		'/snap/chromium/current/usr/lib/chromium-browser/chrome',
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

const syntheticUser = {
	id: 1,
	username: 'synthetic_product_create',
	display_name: 'Synthetic Product Create',
	is_admin: true,
	is_enabled: true,
	auth_version: 1
};

const syntheticBook = {
	id: 1,
	name: 'Synthetic Product Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	is_enabled: true,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access.',
	read_only: false,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	capabilities: {
		read_only: false,
		can_register_metadata: true,
		can_open_accounts: true,
		can_open_transactions: true,
		can_open_reports: true,
		can_upload: false,
		can_edit: true,
		can_delete: false
	},
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic registered local SQLite book.',
		safe_next_actions: []
	},
	management_actions: ['rename', 'recheck'],
	operator_guidance: {
		metadata_source: 'synthetic',
		data_access: 'stubbed',
		read_only_default: false,
		private_path_redacted: true,
		storage_type_label: 'Synthetic',
		unsupported_management_actions: [],
		message: 'Synthetic local smoke fixture; no private book is used.'
	},
	health: {
		status: 'ready',
		safe_code: 'ready',
		source_status: 'ready',
		open_status: 'ready',
		accounts_status: 'ready',
		transactions_status: 'ready',
		reports_status: 'ready',
		checked_at: '2026-07-17T00:00:00Z',
		last_successful_at: '2026-07-17T00:00:00Z'
	}
};

const accounts = [
	{ id: accountA, name: 'Cash', full_name: 'Assets:Cash', type: 'ASSET', currency: 'SEK', balance: '100.00', placeholder: false, hidden: false, parent_id: null },
	{ id: accountB, name: 'Groceries', full_name: 'Expenses:Groceries', type: 'EXPENSE', currency: 'SEK', balance: '0.00', placeholder: false, hidden: false, parent_id: null }
];

function jsonResponse(res, status, body, extraHeaders = {}) {
	res.writeHead(status, {
		'content-type': 'application/json',
		...extraHeaders
	});
	res.end(JSON.stringify(body));
}

function readBody(req) {
	return new Promise((resolve, reject) => {
		let data = '';
		req.on('data', (chunk) => {
			data += chunk.toString('utf8');
		});
		req.on('end', () => {
			try {
				resolve(data ? JSON.parse(data) : null);
			} catch (error) {
				reject(error);
			}
		});
		req.on('error', reject);
	});
}

function createApiServer() {
	const requests = [];
	const server = createServer(async (req, res) => {
		try {
			const url = new URL(req.url ?? '/', 'http://127.0.0.1');
			const requestRecord = { method: req.method, pathname: url.pathname, headers: req.headers, body: null };
			requests.push(requestRecord);
			if (req.headers.authorization !== `Bearer ${token}`) {
				jsonResponse(res, 401, { error: { code: 'AUTH_REQUIRED', message_key: 'auth.required' } });
				return;
			}
			if (req.method === 'GET' && url.pathname === '/auth/me') {
				jsonResponse(res, 200, syntheticUser);
				return;
			}
			if (req.method === 'GET' && url.pathname === '/books') {
				jsonResponse(res, 200, [syntheticBook]);
				return;
			}
			if (req.method === 'GET' && url.pathname === '/books/1') {
				jsonResponse(res, 200, syntheticBook);
				return;
			}
			if (req.method === 'GET' && url.pathname === '/books/1/accounts') {
				jsonResponse(res, 200, accounts);
				return;
			}
			if (req.method === 'GET' && url.pathname === '/books/1/transaction-create-settings') {
				jsonResponse(res, 200, {
					enabled: true,
					effective_enabled: true,
					deployment_writes_enabled: true,
					user_can_create: true,
					create_generation: 7,
					recovery_required: false,
					reason_key: 'enabled'
				});
				return;
			}
			if (req.method === 'POST' && url.pathname === '/books/1/transactions/create-preview') {
				const body = await readBody(req);
				requestRecord.body = body;
				assert.deepEqual(Object.keys(body).sort(), ['currency', 'date', 'description', 'splits']);
				assert.equal(body.splits.length, 2);
				jsonResponse(res, 200, {
					preview_only: true,
					confirm_allowed: true,
					create_count: 1,
					preview_token: previewToken,
					expires_at: '2026-07-17T00:10:00Z',
					idempotency_key: idempotencyKey,
					create_generation: 7,
					currency: body.currency,
					date: body.date,
					description: body.description,
					splits: body.splits.map((split, index) => ({
						index,
						account: accounts.find((account) => account.id === split.account_id),
						amount: split.amount,
						memo: split.memo
					})),
					warnings: []
				});
				return;
			}
			if (req.method === 'POST' && url.pathname === '/books/1/transactions') {
				const body = await readBody(req);
				requestRecord.body = body;
				assert.equal(req.headers['idempotency-key'], idempotencyKey);
				assert.equal(body.preview_token, previewToken);
				assert.deepEqual(Object.keys(body).sort(), ['preview_token', 'transaction']);
				jsonResponse(res, 201, {
					status: 'created',
					transaction_id: 'synthetic-created-1',
					audit_ref: 'aud_synthetic_1',
					backup_ref: 'bkp_synthetic_1',
					readback: { verified: true, transaction_present: true, split_count: 2, balanced: true, currency_consistent: true },
					links: { transaction: '/transactions/synthetic-created-1', explorer: '/transactions' }
				});
				return;
			}
			if (req.method === 'GET' && url.pathname === '/books/1/transactions/synthetic-created-1') {
				jsonResponse(res, 200, {
					id: 'synthetic-created-1',
					date: '2026-07-17',
					description: 'Synthetic #59 product browser create',
					currency: 'SEK',
					splits: [
						{ account_id: accountA, account_name: 'Assets:Cash', memo: 'paid', amount: '-12.34', currency: 'SEK' },
						{ account_id: accountB, account_name: 'Expenses:Groceries', memo: 'food', amount: '12.34', currency: 'SEK' }
					],
					is_write_alpha_owned: true
				});
				return;
			}
			jsonResponse(res, 404, { error: { code: 'NOT_FOUND', message_key: 'not_found' } });
		} catch (error) {
			jsonResponse(res, 500, { error: { code: 'SYNTHETIC_STUB_FAILED', message_key: 'synthetic.failed', request_ref: String(error?.message ?? error) } });
		}
	});
	return { server, requests };
}

function getFreePort() {
	return new Promise((resolve, reject) => {
		const server = net.createServer();
		server.listen(0, '127.0.0.1', () => {
			const address = server.address();
			server.close(() => resolve(address.port));
		});
		server.on('error', reject);
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
				// retry
			}
			if (Date.now() - started > timeoutMs) return reject(new Error(`Timed out waiting for ${url}`));
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
			output = output.slice(-16000);
		});
	}
	child.outputTail = () => output;
	return child;
}

async function stopProcess(child) {
	if (!child || child.exitCode !== null) return;
	await new Promise((resolve) => {
		let done = false;
		const finish = () => {
			if (done) return;
			done = true;
			resolve();
		};
		child.once('exit', finish);
		child.kill('SIGTERM');
		setTimeout(() => child.exitCode === null && child.kill('SIGKILL'), 3000);
		setTimeout(finish, 8000);
	});
}

function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
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
			for (const handler of this.handlers.get(message.method) ?? []) handler(message.params ?? {});
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
			}, cdpCommandTimeoutMs).unref();
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
	if (result.exceptionDetails) throw new Error(`Browser evaluation failed: ${JSON.stringify(result.exceptionDetails)}`);
	return result.result?.value;
}

async function waitForExpression(cdp, expression, label, timeoutMs = 30000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		if (await evaluate(cdp, expression)) return;
		await sleep(150);
	}
	throw new Error(`Timed out waiting for browser condition: ${label}`);
}

function waitForCdpEvent(cdp, method, label, timeoutMs = 30000) {
	return new Promise((resolve, reject) => {
		let done = false;
		const timeout = setTimeout(() => {
			if (done) return;
			done = true;
			reject(new Error(`Timed out waiting for CDP event: ${label}`));
		}, timeoutMs);
		cdp.on(method, (params) => {
			if (done) return;
			done = true;
			clearTimeout(timeout);
			resolve(params);
		});
	});
}

function jsString(value) {
	return JSON.stringify(value);
}

async function navigate(cdp, webBase, path, label) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 30000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([load, waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path)}`, label)]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path)}`, label);
}

async function setSession(cdp, webBase) {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: token, url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'selected_book_id', value: '1', url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });
}

async function fillProductForm(cdp, amountA = '-12.34', amountB = '12.34') {
	await evaluate(cdp, `(() => {
		const set = (selector, value) => {
			const el = document.querySelector(selector);
			if (!el) throw new Error('missing ' + selector);
			el.value = value;
			el.dispatchEvent(new Event('input', { bubbles: true }));
			el.dispatchEvent(new Event('change', { bubbles: true }));
		};
		set('input[name="date"]', '2026-07-17');
		set('input[name="currency"]', 'SEK');
		set('input[name="description"]', 'Synthetic #59 product browser create');
		const accounts = document.querySelectorAll('select[name="split_account_id"]');
		const amounts = document.querySelectorAll('input[name="split_amount"]');
		const memos = document.querySelectorAll('input[name="split_memo"]');
		accounts[0].value = ${jsString(accountA)};
		accounts[0].dispatchEvent(new Event('change', { bubbles: true }));
		accounts[1].value = ${jsString(accountB)};
		accounts[1].dispatchEvent(new Event('change', { bubbles: true }));
		amounts[0].value = ${jsString(amountA)};
		amounts[0].dispatchEvent(new Event('input', { bubbles: true }));
		amounts[1].value = ${jsString(amountB)};
		amounts[1].dispatchEvent(new Event('input', { bubbles: true }));
		memos[0].value = 'paid';
		memos[0].dispatchEvent(new Event('input', { bubbles: true }));
		memos[1].value = 'food';
		memos[1].dispatchEvent(new Event('input', { bubbles: true }));
	})()`);
}

async function clickByText(cdp, text) {
	await evaluate(cdp, `(() => {
		const button = Array.from(document.querySelectorAll('button')).find((item) => (item.textContent || '').includes(${jsString(text)}));
		if (!button) throw new Error('missing button ' + ${jsString(text)});
		const form = button.form;
		if (button.type === 'submit' && form) form.requestSubmit(button);
		else button.click();
	})()`);
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before browser smoke; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	const profileDir = mkdtempSync(join(tmpdir(), 'gwc-create-product-chrome-'));
	const api = createApiServer();
	const apiPort = await getFreePort();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	let webProcess;
	let chromeProcess;
	let cdp;
	const consoleErrors = [];
	const browserRequests = [];

	try {
		await new Promise((resolve) => api.server.listen(apiPort, '127.0.0.1', resolve));
		webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
			cwd: root,
			env: {
				...process.env,
				API_INTERNAL_URL: `http://127.0.0.1:${apiPort}`,
				ORIGIN: `http://127.0.0.1:${webPort}`
			}
		});
		await waitForHttp(`http://127.0.0.1:${webPort}/login`, 30000).catch((error) => {
			throw new Error(`${error.message}\nweb output:\n${webProcess.outputTail()}`);
		});

		chromeProcess = spawnLogged(chromiumBin, [
			'--headless=new',
			'--disable-gpu',
			'--no-sandbox',
			'--disable-dev-shm-usage',
			`--remote-debugging-port=${debugPort}`,
			`--user-data-dir=${profileDir}`,
			'--window-size=320,900',
			'about:blank'
		]);
		cdp = await connectCdp(debugPort);
		cdp.on('Runtime.consoleAPICalled', (event) => {
			if (['error', 'warning'].includes(event.type)) consoleErrors.push(event);
		});
		cdp.on('Network.requestWillBeSent', (event) => {
			browserRequests.push({ method: event.request.method, url: event.request.url });
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 900, deviceScaleFactor: 1, mobile: true });
		const webBase = `http://127.0.0.1:${webPort}`;
		await setSession(cdp, webBase);
		await navigate(cdp, webBase, '/transactions/new', 'transaction create page');
		await waitForExpression(cdp, `document.querySelector('#transaction-create-form') && document.body.innerText.includes('2..50 split rows')`, 'SSR form visible');
		await fillProductForm(cdp);
		await waitForExpression(cdp, `document.querySelector('#running-balance')?.innerText.includes('Exact zero-sum')`, 'live exact zero-sum balance');
		await clickByText(cdp, 'Preview transaction');
		try {
			await waitForExpression(cdp, `document.querySelector('#normalized-preview') && document.querySelector('#confirm-create-form')`, 'preview and confirm form visible');
		} catch (error) {
			const snapshot = await evaluate(cdp, `(() => {
				const form = document.querySelector('#transaction-create-form');
				return {
					path: location.pathname,
					search: location.search,
					bodyText: document.body.innerText,
					formValid: form?.checkValidity(),
					invalid: Array.from(form?.querySelectorAll(':invalid') || []).map((el) => ({ name: el.getAttribute('name'), id: el.id, value: el.value, tag: el.tagName })),
					formData: form ? Array.from(new FormData(form).entries()) : [],
					html: document.documentElement.outerHTML.slice(0, 4000)
				};
			})()`);
			console.error(JSON.stringify({ snapshot, apiRequests: api.requests }, null, 2));
			throw error;
		}

		await fillProductForm(cdp, '-12.35', '12.34');
		await waitForExpression(cdp, `document.body.innerText.includes('Draft changed after preview') && !document.querySelector('#confirm-create-form')`, 'stale preview disables confirm');
		await fillProductForm(cdp);
		await clickByText(cdp, 'Preview transaction');
		await waitForExpression(cdp, `document.querySelector('#confirm-create-form')`, 'fresh confirm form visible');
		await clickByText(cdp, 'Confirm create');
		await waitForExpression(cdp, `location.pathname === '/transactions/synthetic-created-1'`, 'confirm redirected to detail');

		const browserState = await evaluate(cdp, `(() => ({
			path: location.pathname,
			scrollWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
			viewportWidth: window.innerWidth,
			storageItems: [
				...Object.entries(localStorage).map(([key, value]) => ['localStorage', key, value]),
				...Object.entries(sessionStorage).map(([key, value]) => ['sessionStorage', key, value])
			],
			bodyText: document.body.innerText,
			formActions: Array.from(document.forms).map((form) => form.getAttribute('action') || '')
		}))()`);
		assert.equal(browserState.path, '/transactions/synthetic-created-1');
		assert.ok(browserState.scrollWidth <= browserState.viewportWidth + 8, `320px no horizontal overflow (${browserState.scrollWidth} > ${browserState.viewportWidth})`);
		const privateStorage = browserState.storageItems.filter((item) =>
			JSON.stringify(item).includes(previewToken) ||
			JSON.stringify(item).includes(idempotencyKey) ||
			JSON.stringify(item).includes('Synthetic #59 product browser create')
		);
		assert.deepEqual(privateStorage, [], 'no localStorage/sessionStorage use for drafts/tokens');
		assert.ok(!browserState.bodyText.includes('PRIVATE_LEDGER_SENTINEL'), 'browser must not leak backend private details');
		assert.deepEqual(consoleErrors, [], 'browser console must not contain warnings/errors');

		const previewCalls = api.requests.filter((request) => request.method === 'POST' && request.pathname === '/books/1/transactions/create-preview');
		const confirmCalls = api.requests.filter((request) => request.method === 'POST' && request.pathname === '/books/1/transactions');
		assert.equal(previewCalls.length, 2, 'browser should issue two preview API calls: original and stale refresh');
		assert.equal(confirmCalls.length, 1, 'browser should issue exactly one confirm API call');
		assert.equal(confirmCalls[0].headers['idempotency-key'], idempotencyKey, 'confirm must forward Idempotency-Key from preview');
		assert.equal(confirmCalls[0].body.preview_token, previewToken, 'confirm must forward preview token');
		assert.deepEqual(Object.keys(confirmCalls[0].body.transaction).sort(), ['currency', 'date', 'description', 'splits'], 'confirm transaction DTO shape must match #59');
		assert.ok(browserRequests.some((request) => request.method === 'POST' && request.url.includes('/transactions/new?/preview')), 'browser evidence must include preview form POST');
		assert.ok(browserRequests.some((request) => request.method === 'POST' && request.url.includes('/transactions/new?/confirm')), 'browser evidence must include confirm form POST');

		const disallowedApiMutations = api.requests.filter((request) =>
			['PATCH', 'DELETE', 'PUT'].includes(request.method) || /batch|import|ofx|csv/i.test(request.pathname)
		);
		assert.deepEqual(disallowedApiMutations, [], 'browser harness must not send PATCH/DELETE/PUT/batch/import requests');
		return {
			api_requests: api.requests.length,
			browser_requests: browserRequests.length,
			preview_calls: previewCalls.length,
			confirm_calls: confirmCalls.length,
			settings_gets: api.requests.filter((request) => request.method === 'GET' && request.pathname === '/books/1/transaction-create-settings').length,
			disallowed_mutations: disallowedApiMutations.length,
			console_errors: consoleErrors.length,
			private_storage_items: privateStorage.length,
			viewport_width: browserState.viewportWidth,
			scroll_width: browserState.scrollWidth
		};
	} finally {
		cdp?.close();
		await stopProcess(chromeProcess);
		await stopProcess(webProcess);
		await new Promise((resolve) => api.server.close(resolve));
		rmSync(profileDir, { recursive: true, force: true });
	}
}

runSmoke()
	.then((summary) => console.log(`ok - #59 transaction create product browser smoke passed: ${Object.entries(summary).map(([key, value]) => `${key}=${value}`).join(' ')}`))
	.catch((error) => {
		console.error(error);
		process.exitCode = 1;
	});
