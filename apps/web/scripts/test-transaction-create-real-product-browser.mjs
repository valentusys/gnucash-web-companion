import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, rmSync, mkdirSync, copyFileSync, readFileSync, readdirSync, chmodSync, utimesSync, unlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const webRoot = join(here, '..');
const repoRoot = resolve(webRoot, '..', '..');
const apiRoot = join(repoRoot, 'apps', 'api');
const viteBin = join(webRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(webRoot, '.svelte-kit', 'output', 'server', 'index.js');
const cdpCommandTimeoutMs = 120000;
const jwtSecret = 'real-product-browser-create-gate-' + 'x'.repeat(48);
const adminPassword = 'real-product-browser-admin-pass';
const lockDir = '/data/locks';
const reversedNaturalSignAccountTypes = new Set(['LIABILITY', 'PAYABLE', 'CREDIT', 'INCOME', 'EQUITY']);

function resolveApiPython() {
	if (process.env.API_PYTHON) return process.env.API_PYTHON;
	const worktreeVenvPython = join(apiRoot, '.venv', 'bin', 'python');
	return existsSync(worktreeVenvPython) ? worktreeVenvPython : 'python';
}

const apiPython = resolveApiPython();

function apiPythonPath() {
	return apiPython.includes('/') ? `${dirname(apiPython)}:${process.env.PATH ?? ''}` : (process.env.PATH ?? '');
}

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

function jsString(value) {
	return JSON.stringify(value);
}

function sleep(ms) {
	return new Promise((resolvePromise) => setTimeout(resolvePromise, ms));
}

function getFreePort() {
	return new Promise((resolvePromise, reject) => {
		const server = net.createServer();
		server.listen(0, '127.0.0.1', () => {
			const address = server.address();
			server.close(() => resolvePromise(address.port));
		});
		server.on('error', reject);
	});
}

function hashFile(path) {
	const digest = createHash('sha256');
	digest.update(readFileSync(path));
	return digest.digest('hex');
}

function sqliteUrl(path) {
	return `sqlite:///${path}`;
}

function spawnLogged(command, args, options) {
	const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
	let output = '';
	for (const stream of [child.stdout, child.stderr]) {
		stream.on('data', (chunk) => {
			output += chunk.toString('utf8');
			output = output.slice(-30000);
		});
	}
	child.outputTail = () => output;
	return child;
}

async function stopProcess(child) {
	if (!child || child.exitCode !== null) return;
	await new Promise((resolvePromise) => {
		let done = false;
		const finish = () => {
			if (done) return;
			done = true;
			resolvePromise();
		};
		child.once('exit', finish);
		child.kill('SIGTERM');
		setTimeout(() => child.exitCode === null && child.kill('SIGKILL'), 3000);
		setTimeout(finish, 8000);
	});
}

function runPythonJson(code, args = [], { input = null, env = {} } = {}) {
	const result = spawnSync(apiPython, ['-c', code, ...args], {
		cwd: apiRoot,
		env: {
			...process.env,
			PATH: apiPythonPath(),
			PYTHONPATH: apiRoot,
			...env
		},
		input: input === null ? undefined : JSON.stringify(input),
		encoding: 'utf8',
		maxBuffer: 20 * 1024 * 1024
	});
	if (result.status !== 0) {
		throw new Error(`python failed (${result.status})\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`);
	}
	const stdout = result.stdout.trim();
	assert.ok(stdout, 'python helper must return JSON stdout');
	return JSON.parse(stdout);
}

function queryAppDb(appDbPath, sql, params = []) {
	return runPythonJson(
		`import json, sqlite3, sys\nreq=json.load(sys.stdin)\ncon=sqlite3.connect(req['db'])\ncon.row_factory=sqlite3.Row\ntry:\n rows=[dict(row) for row in con.execute(req['sql'], req.get('params', [])).fetchall()]\n print(json.dumps(rows, sort_keys=True))\nfinally:\n con.close()`,
		[],
		{ input: { db: appDbPath, sql, params } }
	);
}

function bookSnapshot(path, transactionId = '') {
	return runPythonJson(
		`import json, sys, piecash\npath=sys.argv[1]\ntxid=sys.argv[2]\nbook=piecash.open_book(path, readonly=True)\ntry:\n txs=list(getattr(book, 'transactions', []) or [])\n all_splits=[]\n for tx in txs:\n  all_splits.extend(list(getattr(tx, 'splits', []) or []))\n target=None\n if txid:\n  for tx in txs:\n   if str(getattr(tx, 'guid', '') or '') == txid:\n    target=tx\n    break\n def dec(value):\n  return format(value, 'f')\n def account_guid(account):\n  return str(getattr(account, 'guid', '') or '')\n detail=None\n if target is not None:\n  commodity=getattr(target, 'currency', None)\n  detail={\n   'id': str(getattr(target, 'guid', '') or ''),\n   'date': getattr(target, 'post_date').isoformat(),\n   'description': str(getattr(target, 'description', '') or ''),\n   'currency': str(getattr(commodity, 'mnemonic', '') or ''),\n   'splits': sorted([\n    {\n     'account_id': account_guid(getattr(split, 'account', None)),\n     'account_name': str(getattr(getattr(split, 'account', None), 'name', '') or ''),\n     'amount': dec(getattr(split, 'value')),\n     'memo': str(getattr(split, 'memo', '') or ''),\n    } for split in (getattr(target, 'splits', []) or [])\n   ], key=lambda item: (item['account_id'], item['amount'], item['memo']))\n  }\n print(json.dumps({'transactions': len(txs), 'splits': len(all_splits), 'transaction': detail}, sort_keys=True, ensure_ascii=False))\nfinally:\n book.close()`,
		[path, transactionId]
	);
}

function generateFixtureManifest(root) {
	return runPythonJson(
		`import json, sys\nfrom pathlib import Path\nfrom tests.support.generate_transaction_create_fixtures import generate_transaction_create_fixture_set\nfixture_set=generate_transaction_create_fixture_set(Path(sys.argv[1]))\nprint(json.dumps(fixture_set.to_manifest(), ensure_ascii=False, sort_keys=True))`,
		[root]
	);
}

function decimalParts(value) {
	const text = String(value).trim();
	const match = /^([+-]?)(\d+)(?:\.(\d+))?$/.exec(text);
	assert.ok(match, `invalid decimal string: ${value}`);
	return {
		sign: match[1] === '-' ? -1n : 1n,
		digits: `${match[2]}${match[3] ?? ''}`.replace(/^0+/, '') || '0',
		scale: (match[3] ?? '').length
	};
}

function scaleDecimal(parts, scale) {
	return parts.sign * BigInt(`${parts.digits}${'0'.repeat(scale - parts.scale)}`);
}

function formatScaled(value, scale) {
	const sign = value < 0n ? '-' : '';
	const absolute = value < 0n ? -value : value;
	if (scale === 0) return `${sign}${absolute}`;
	const raw = absolute.toString().padStart(scale + 1, '0');
	return `${sign}${raw.slice(0, -scale)}.${raw.slice(-scale)}`;
}

function decimalSubtract(left, right) {
	const a = decimalParts(left);
	const b = decimalParts(right);
	const scale = Math.max(a.scale, b.scale);
	return formatScaled(scaleDecimal(a, scale) - scaleDecimal(b, scale), scale);
}

function decimalNegate(value) {
	const parts = decimalParts(value);
	return formatScaled(-scaleDecimal(parts, parts.scale), parts.scale);
}

function decimalNormalize(value) {
	const parts = decimalParts(value);
	return formatScaled(scaleDecimal(parts, parts.scale), parts.scale);
}

function decimalEqual(left, right) {
	const a = decimalParts(left);
	const b = decimalParts(right);
	const scale = Math.max(a.scale, b.scale);
	return scaleDecimal(a, scale) === scaleDecimal(b, scale);
}

function decimalDisplayVariants(value) {
	const unsigned = decimalNormalize(value).replace('-', '');
	const trimmed = unsigned.includes('.') ? unsigned.replace(/0+$/, '').replace(/\.$/, '') : unsigned;
	return [...new Set([unsigned, trimmed])];
}

function expectedDisplayDeltaForSplit(testCase, split) {
	const account = Object.values(testCase.accounts).find((candidate) => candidate.id === split.account_id);
	assert.ok(account, `missing account metadata for ${split.account_id}`);
	return reversedNaturalSignAccountTypes.has(String(account.type).toUpperCase()) ? decimalNegate(split.amount) : decimalNormalize(split.amount);
}

function accountBalancesById(items) {
	return Object.fromEntries(items.map((item) => [item.id, item.balance]));
}

async function waitForHttp(url, timeoutMs = 30000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		try {
			const response = await fetch(url);
			if (response.status < 500) return;
		} catch {
			// retry
		}
		await sleep(250);
	}
	throw new Error(`Timed out waiting for ${url}`);
}

async function apiJson(apiBase, token, path, options = {}) {
	const response = await fetch(`${apiBase}${path}`, {
		method: options.method ?? 'GET',
		headers: {
			authorization: `Bearer ${token}`,
			...(options.body === undefined ? {} : { 'content-type': 'application/json' }),
			...(options.headers ?? {})
		},
		body: options.body === undefined ? undefined : JSON.stringify(options.body)
	});
	const text = await response.text();
	let body = null;
	try {
		body = text ? JSON.parse(text) : null;
	} catch {
		body = text;
	}
	return { status: response.status, ok: response.ok, body, text, headers: response.headers };
}

async function login(apiBase) {
	const response = await fetch(`${apiBase}/auth/login`, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ username: 'admin', password: adminPassword })
	});
	const body = await response.json().catch(() => null);
	assert.equal(response.status, 200, `login failed: ${JSON.stringify(body)}`);
	assert.ok(body?.access_token, 'login must return access_token');
	return body.access_token;
}

async function registerBook(apiBase, token, testCase, { name, makeDefault = true, enableCreate = true } = {}) {
	const request = {
		name: name ?? `Real browser ${testCase.label}`,
		storage_type: 'sqlite',
		uri_or_path: testCase.targetPath,
		base_currency: testCase.baseCurrency,
		make_default: makeDefault
	};
	const preflight = await apiJson(apiBase, token, '/books/preflight', { method: 'POST', body: request });
	assert.equal(preflight.status, 200, `book preflight failed for ${testCase.label}: ${preflight.text}`);
	assert.equal(preflight.body.status, 'ready', `book preflight not ready for ${testCase.label}`);
	const registered = await apiJson(apiBase, token, '/books', {
		method: 'POST',
		body: { ...request, preflight_token: preflight.body.preflight_token }
	});
	assert.equal(registered.status, 201, `book registration failed for ${testCase.label}: ${registered.text}`);
	const bookId = registered.body.id;
	assert.ok(Number.isInteger(bookId), 'registered book id must be an integer');
	if (enableCreate) {
		const enabled = await apiJson(apiBase, token, `/books/${bookId}/transaction-create-settings`, {
			method: 'PATCH',
			body: { enabled: true }
		});
		assert.equal(enabled.status, 200, `transaction-create enable failed for ${testCase.label}: ${enabled.text}`);
		assert.equal(enabled.body.enabled, true, `transaction-create setting must be enabled for ${testCase.label}`);
	}
	return { bookId, preflight: preflight.body, registered: registered.body };
}

async function startApi({ tempRoot, appDbPath, allowedRoots, writesEnabled, port }) {
	mkdirSync(dirname(appDbPath), { recursive: true });
	const apiProcess = spawnLogged(apiPython, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port)], {
		cwd: apiRoot,
		env: {
			...process.env,
			PATH: apiPythonPath(),
			PYTHONPATH: apiRoot,
			APP_ENV: 'test',
			APP_DATABASE_URL: sqliteUrl(appDbPath),
			GNUCASH_BOOK_ALLOWED_ROOTS: JSON.stringify(allowedRoots),
			JWT_SECRET: jwtSecret,
			APP_ADMIN_USERNAME: 'admin',
			APP_ADMIN_PASSWORD: adminPassword,
			GNUCASH_WRITES_ENABLED: writesEnabled ? 'true' : 'false',
			REAL_PRODUCT_BROWSER_TEMP_ROOT: tempRoot
		}
	});
	try {
		await waitForHttp(`http://127.0.0.1:${port}/health`, 45000);
	} catch (error) {
		throw new Error(`${error.message}\napi output:\n${apiProcess.outputTail()}`);
	}
	return apiProcess;
}

async function startWeb({ apiBase, port }) {
	const webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(port), '--strictPort'], {
		cwd: webRoot,
		env: {
			...process.env,
			API_INTERNAL_URL: apiBase,
			ORIGIN: `http://127.0.0.1:${port}`
		}
	});
	try {
		await waitForHttp(`http://127.0.0.1:${port}/login`, 45000);
	} catch (error) {
		throw new Error(`${error.message}\nweb output:\n${webProcess.outputTail()}`);
	}
	return webProcess;
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
		await new Promise((resolvePromise, reject) => {
			this.ws.addEventListener('open', resolvePromise, { once: true });
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
		return new Promise((resolvePromise, reject) => {
			this.pending.set(id, { resolve: resolvePromise, reject });
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
	assert.ok(target?.webSocketDebuggerUrl, 'Chromium CDP page target must expose websocket URL');
	const cdp = new CdpClient(target.webSocketDebuggerUrl);
	await cdp.connect();
	return cdp;
}

async function startBrowser({ profileDir, debugPort }) {
	const chromeProcess = spawnLogged(chromiumBin, [
		'--headless=new',
		'--disable-gpu',
		'--no-sandbox',
		'--disable-dev-shm-usage',
		`--remote-debugging-port=${debugPort}`,
		`--user-data-dir=${profileDir}`,
		'--window-size=320,900',
		'about:blank'
	]);
	const cdp = await connectCdp(debugPort);
	const state = {
		cdp,
		chromeProcess,
		consoleEvents: [],
		requests: [],
		responses: [],
		requestMethods: new Map()
	};
	cdp.on('Runtime.consoleAPICalled', (event) => {
		if (['error', 'warning'].includes(event.type)) state.consoleEvents.push(event);
	});
	cdp.on('Network.requestWillBeSent', (event) => {
		state.requestMethods.set(event.requestId, event.request.method);
		state.requests.push({ id: event.requestId, method: event.request.method, url: event.request.url });
	});
	cdp.on('Network.responseReceived', (event) => {
		state.responses.push({
			id: event.requestId,
			method: state.requestMethods.get(event.requestId) ?? '',
			url: event.response.url,
			status: event.response.status,
			headers: event.response.headers ?? {}
		});
	});
	await cdp.send('Page.enable');
	await cdp.send('Runtime.enable');
	await cdp.send('Network.enable');
	await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 900, deviceScaleFactor: 1, mobile: true });
	return state;
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
	const snapshot = await evaluate(cdp, `(() => ({ path: location.pathname, search: location.search, text: document.body.innerText.slice(0, 3000), html: document.documentElement.outerHTML.slice(0, 3000) }))()`);
	throw new Error(`Timed out waiting for browser condition: ${label}\n${JSON.stringify(snapshot, null, 2)}`);
}

function waitForCdpEvent(cdp, method, label, timeoutMs = 30000) {
	return new Promise((resolvePromise, reject) => {
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
			resolvePromise(params);
		});
	});
}

async function navigate(cdp, webBase, path, label) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 30000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([load, waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path.split('?')[0])}`, label)]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path.split('?')[0])}`, label);
}

async function setSession(cdp, webBase, token, bookId) {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: token, url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'selected_book_id', value: String(bookId), url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });
}

async function visibleText(cdp) {
	return evaluate(cdp, 'document.body.innerText');
}

async function ensureSplitRows(cdp, count) {
	while ((await evaluate(cdp, `document.querySelectorAll('select[name="split_account_id"]').length`)) < count) {
		await evaluate(cdp, `document.querySelector('#split-editor button[type="button"]')?.click()`);
		await sleep(100);
	}
	await waitForExpression(cdp, `document.querySelectorAll('select[name="split_account_id"]').length === ${count}`, `${count} split rows visible`);
}

async function fillTransactionForm(cdp, request) {
	await ensureSplitRows(cdp, request.splits.length);
	await evaluate(cdp, `(() => {
		const request = ${jsString(request)};
		const set = (selector, value) => {
			const el = document.querySelector(selector);
			if (!el) throw new Error('missing ' + selector);
			el.value = value;
			el.dispatchEvent(new Event('input', { bubbles: true }));
			el.dispatchEvent(new Event('change', { bubbles: true }));
		};
		set('input[name="date"]', request.date);
		set('input[name="currency"]', request.currency);
		set('input[name="description"]', request.description);
		const accounts = Array.from(document.querySelectorAll('select[name="split_account_id"]'));
		const amounts = Array.from(document.querySelectorAll('input[name="split_amount"]'));
		const memos = Array.from(document.querySelectorAll('input[name="split_memo"]'));
		request.splits.forEach((split, index) => {
			accounts[index].value = split.account_id;
			accounts[index].dispatchEvent(new Event('change', { bubbles: true }));
			amounts[index].value = split.amount;
			amounts[index].dispatchEvent(new Event('input', { bubbles: true }));
			amounts[index].dispatchEvent(new Event('change', { bubbles: true }));
			memos[index].value = split.memo;
			memos[index].dispatchEvent(new Event('input', { bubbles: true }));
			memos[index].dispatchEvent(new Event('change', { bubbles: true }));
		});
	})()`);
	await waitForExpression(cdp, `document.querySelector('#running-balance')?.innerText.includes('Exact zero-sum')`, 'live exact zero-sum balance');
}

async function submitPreview(cdp) {
	await evaluate(cdp, `(() => {
		const form = document.querySelector('#transaction-create-form');
		const button = form?.querySelector('button[formaction="?/preview"]');
		if (!form || !button) throw new Error('missing preview form/button');
		form.requestSubmit(button);
	})()`);
}

async function submitConfirmForm(cdp) {
	await evaluate(cdp, `(() => {
		const form = document.querySelector('#confirm-create-form');
		const button = form?.querySelector('button[formaction="?/confirm"]');
		if (!form || !button) throw new Error('missing confirm form/button');
		form.requestSubmit(button);
	})()`);
}

async function readConfirmHidden(cdp) {
	return evaluate(cdp, `(() => {
		const form = document.querySelector('#confirm-create-form');
		if (!form) throw new Error('missing confirm form');
		const get = (fieldName) => form.querySelector('[name="' + fieldName + '"]')?.value ?? '';
		return {
			book_id: get('book_id'),
			preview_token: get('preview_token'),
			idempotency_key: get('idempotency_key'),
			transaction_json: get('transaction_json')
		};
	})()`);
}

async function mutateConfirmTransactionJson(cdp, mutatorSource) {
	await evaluate(cdp, `(() => {
		const input = document.querySelector('#confirm-create-form input[name="transaction_json"]');
		if (!input) throw new Error('missing transaction_json input');
		const transaction = JSON.parse(input.value);
		(${mutatorSource})(transaction);
		input.value = JSON.stringify(transaction);
	})()`);
}

async function browserReplayConfirm(cdp, hidden) {
	return evaluate(
		cdp,
		`(async () => {
			const body = new URLSearchParams(${jsString(hidden)});
			const response = await fetch('/transactions/new?/confirm', {
				method: 'POST',
				headers: { 'content-type': 'application/x-www-form-urlencoded' },
				body,
				redirect: 'manual'
			});
			return { status: response.status, location: response.headers.get('location') ?? '', text: (await response.text()).slice(0, 1000) };
		})()`,
		{ awaitPromise: true }
	);
}

function routeResponsesSince(state, startIndex, pathFragment) {
	return state.responses.slice(startIndex).filter((item) => item.url.includes(pathFragment));
}

function routeRequestsSince(state, startIndex, pathFragment) {
	return state.requests.slice(startIndex).filter((item) => item.url.includes(pathFragment));
}

function makeScenarioCase(manifest, caseName, label, scenarioRoot, counters) {
	const source = manifest.cases[caseName];
	assert.ok(source, `missing generated case ${caseName}`);
	const targetDir = join(scenarioRoot, 'targets');
	mkdirSync(targetDir, { recursive: true });
	const targetPath = join(targetDir, `${label}-${caseName}.gnucash.sqlite`);
	copyFileSync(source.source_path, targetPath);
	counters.target_copied += 1;
	return {
		label,
		name: caseName,
		kind: source.kind,
		sourcePath: source.source_path,
		targetPath,
		sourceHash: hashFile(source.source_path),
		targetHashBefore: hashFile(targetPath),
		baseCurrency: source.base_currency,
		accounts: source.accounts,
		request: source.request,
		expected: source.expected,
		sourceSnapshotBefore: bookSnapshot(source.source_path),
		targetSnapshotBefore: bookSnapshot(targetPath)
	};
}

async function verifyApiReadback(apiBase, token, testCase, bookId, transactionId) {
	const detail = await apiJson(apiBase, token, `/books/${bookId}/transactions/${transactionId}`);
	assert.equal(detail.status, 200, `detail readback failed for ${testCase.label}: ${detail.text}`);
	assert.equal(detail.body.id, transactionId, 'detail transaction id must match planned GUID');
	assert.equal(detail.body.date, testCase.request.date, 'detail date must match request');
	assert.equal(detail.body.description, testCase.request.description, 'detail description must match request');
	assert.equal(detail.body.currency, testCase.request.currency, 'detail currency must match request');
	assert.equal(detail.body.is_write_alpha_owned, true, 'detail must show write-alpha ownership');
	const actual = [...detail.body.splits].map((split) => [split.account_id, split.amount, split.memo ?? '']).sort();
	const expected = testCase.request.splits.map((split) => [split.account_id, split.amount, split.memo]).sort();
	assert.equal(actual.length, expected.length, `detail split count must match request for ${testCase.label}`);
	for (let index = 0; index < expected.length; index += 1) {
		assert.equal(actual[index][0], expected[index][0], `detail split account ${index} for ${testCase.label}`);
		assert.ok(decimalEqual(actual[index][1], expected[index][1]), `detail split amount ${index} for ${testCase.label}: expected ${expected[index][1]}, got ${actual[index][1]}`);
		assert.equal(actual[index][2], expected[index][2], `detail split memo ${index} for ${testCase.label}`);
	}
	return detail.body;
}

function verifyDirectBookReadback(testCase, transactionId) {
	const snapshot = bookSnapshot(testCase.targetPath, transactionId);
	assert.equal(snapshot.transactions, testCase.targetSnapshotBefore.transactions + 1, `${testCase.label} target transaction count +1`);
	assert.equal(snapshot.splits, testCase.targetSnapshotBefore.splits + testCase.request.splits.length, `${testCase.label} target split count delta`);
	assert.ok(snapshot.transaction, `${testCase.label} direct reopened transaction must exist`);
	assert.equal(snapshot.transaction.id, transactionId, `${testCase.label} direct transaction id`);
	assert.equal(snapshot.transaction.date, testCase.request.date, `${testCase.label} direct date`);
	assert.equal(snapshot.transaction.description, testCase.request.description, `${testCase.label} direct description`);
	assert.equal(snapshot.transaction.currency, testCase.request.currency, `${testCase.label} direct currency`);
	const actual = snapshot.transaction.splits.map((split) => [split.account_id, split.amount, split.memo]).sort();
	const expected = testCase.request.splits.map((split) => [split.account_id, split.amount, split.memo]).sort();
	assert.equal(actual.length, expected.length, `${testCase.label} direct split count`);
	for (let index = 0; index < expected.length; index += 1) {
		assert.equal(actual[index][0], expected[index][0], `${testCase.label} direct split account ${index}`);
		assert.ok(decimalEqual(actual[index][1], expected[index][1]), `${testCase.label} direct split amount ${index}: expected ${expected[index][1]}, got ${actual[index][1]}`);
		assert.equal(actual[index][2], expected[index][2], `${testCase.label} direct split memo ${index}`);
	}
	return snapshot;
}

function backupEvidenceFor(testCase) {
	const backupRoot = join(dirname(dirname(testCase.targetPath)), 'backups', basename(testCase.targetPath, '.sqlite'));
	const entries = existsSync(backupRoot) ? readdirSync(backupRoot).sort() : [];
	const backupFiles = entries.filter((name) => !name.endsWith('.verified.json'));
	const markerFiles = entries.filter((name) => name.endsWith('.verified.json'));
	return { backupRoot, backupFiles, markerFiles };
}

function verifySuccessfulBackup(testCase) {
	const evidence = backupEvidenceFor(testCase);
	assert.equal(evidence.backupFiles.length, 1, `${testCase.label} must create exactly one backup file`);
	assert.equal(evidence.markerFiles.length, 1, `${testCase.label} must create exactly one verified marker`);
	const backupPath = join(evidence.backupRoot, evidence.backupFiles[0]);
	const markerPath = join(evidence.backupRoot, evidence.markerFiles[0]);
	assert.equal(hashFile(backupPath), testCase.targetHashBefore, `${testCase.label} backup hash must equal target before hash`);
	const marker = JSON.parse(readFileSync(markerPath, 'utf8'));
	assert.equal(marker.status, 'verified', `${testCase.label} backup marker status`);
	assert.equal(marker.sha256, testCase.targetHashBefore, `${testCase.label} backup marker hash`);
	return { files: evidence.backupFiles.length, markers: evidence.markerFiles.length, marker_status: marker.status };
}

function idempotencyRows(appDbPath, bookId) {
	return queryAppDb(
		appDbPath,
		'SELECT id, book_id, planned_transaction_guid, state, safe_error_code, safe_result_json FROM transaction_create_idempotency WHERE book_id = ? ORDER BY id',
		[bookId]
	);
}

function auditRows(appDbPath, bookId) {
	return queryAppDb(appDbPath, 'SELECT id, action, payload_json FROM audit_logs WHERE book_id = ? ORDER BY id', [bookId]);
}

function ownershipRows(appDbPath, bookId) {
	return queryAppDb(appDbPath, 'SELECT id, transaction_id FROM write_alpha_transaction_ownership WHERE book_id = ? ORDER BY id', [bookId]);
}

function verifyMetadataSuccess(appDbPath, bookId, transactionId) {
	const idempotency = idempotencyRows(appDbPath, bookId);
	const succeeded = idempotency.filter((row) => row.state === 'succeeded');
	assert.equal(succeeded.length, 1, `book ${bookId} must have one succeeded idempotency row`);
	assert.equal(succeeded[0].planned_transaction_guid, transactionId, 'planned GUID must equal transaction id');
	const ownership = ownershipRows(appDbPath, bookId);
	assert.equal(ownership.length, 1, `book ${bookId} must have one ownership row`);
	assert.equal(ownership[0].transaction_id, transactionId, 'ownership transaction id must match');
	const audits = auditRows(appDbPath, bookId);
	const confirmAudits = audits.filter((row) => row.action === 'transaction.create.confirm');
	assert.ok(confirmAudits.length >= 3, `book ${bookId} must audit started/success/duplicate confirm`);
	return { idempotency, ownership, audits, confirmAudits };
}

async function verifyOrdinaryRoutes(cdp, webBase, testCase, bookId) {
	const date = testCase.request.date;
	const encodedDescription = encodeURIComponent(testCase.request.description);
	await navigate(cdp, webBase, `/transactions?date_from=${date}&date_to=${date}&query=${encodedDescription}&sort=date_desc&page_size=50`, `${testCase.label} transactions explorer`);
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(testCase.request.description)})`, `${testCase.label} transactions explorer description`);
	await waitForExpression(cdp, `document.body.innerText.includes('write-alpha-created') && document.body.innerText.includes('Returned 1 row')`, `${testCase.label} transactions explorer created row`);

	const firstSplit = testCase.request.splits[0];
	const expectedDelta = expectedDisplayDeltaForSplit(testCase, firstSplit);
	const deltaVariants = decimalDisplayVariants(expectedDelta);
	await navigate(cdp, webBase, `/accounts/${encodeURIComponent(firstSplit.account_id)}?date_from=${date}&date_to=${date}&limit=5`, `${testCase.label} account activity`);
	await waitForExpression(cdp, `document.body.innerText.toLowerCase().includes('exact direct change')`, `${testCase.label} account activity exact change label`);
	await waitForExpression(cdp, `${jsString(deltaVariants)}.some((text) => document.body.innerText.includes(text))`, `${testCase.label} account activity delta`);
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(testCase.request.description)})`, `${testCase.label} account activity transaction description`);

	const reportAmount = testCase.name === 'income'
		? '2500.00'
		: testCase.name === 'three_split'
			? '30.00'
			: testCase.name === 'unicode'
				? '45.67'
				: '12.34';
	await navigate(cdp, webBase, `/reports?preset=custom&date_from=${date}&date_to=${date}&comparison_mode=custom&comparison_date_from=2026-01-01&comparison_date_to=2026-01-01`, `${testCase.label} reports period`);
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(reportAmount)})`, `${testCase.label} reports period total ${reportAmount}`);
	return { explorer_description: true, activity_delta: expectedDelta, report_amount: reportAmount };
}

async function runSuccessfulCase({ stack, testCase, counters }) {
	const { cdp } = stack.browser;
	await setSession(cdp, stack.webBase, stack.token, testCase.bookId);
	const beforeAccounts = accountBalancesById((await apiJson(stack.apiBase, stack.token, `/books/${testCase.bookId}/accounts`)).body);
	const beforeTargetHash = hashFile(testCase.targetPath);
	const beforeSourceHash = hashFile(testCase.sourcePath);
	assert.equal(beforeSourceHash, testCase.sourceHash, `${testCase.label} source hash before`);

	await navigate(cdp, stack.webBase, '/transactions/new', `${testCase.label} create page`);
	await waitForExpression(cdp, `document.querySelector('#transaction-create-form') && document.body.innerText.includes('2..50 split rows')`, `${testCase.label} SSR create form`);
	await fillTransactionForm(cdp, testCase.request);
	const previewResponseStart = stack.browser.responses.length;
	await submitPreview(cdp);
	await waitForExpression(cdp, `document.querySelector('#normalized-preview') && document.querySelector('#confirm-create-form')`, `${testCase.label} preview and confirm form`);
	const previewRoutes = routeResponsesSince(stack.browser, previewResponseStart, '/transactions/new?/preview');
	const hidden = await readConfirmHidden(cdp);
	assert.ok(hidden.preview_token.startsWith('pt1.'), `${testCase.label} real preview token shape`);
	assert.ok(hidden.idempotency_key.length >= 16, `${testCase.label} idempotency key shape`);

	const confirmResponseStart = stack.browser.responses.length;
	const confirmRequestStart = stack.browser.requests.length;
	await submitConfirmForm(cdp);
	await waitForExpression(cdp, `location.pathname === '/transactions' && location.search.includes('create_status=created')`, `${testCase.label} create redirect`);
	const confirmRoutes = routeResponsesSince(stack.browser, confirmResponseStart, '/transactions/new?/confirm');
	const confirmRequests = routeRequestsSince(stack.browser, confirmRequestStart, '/transactions/new?/confirm');
	assert.ok(confirmRequests.some((item) => item.method === 'POST'), `${testCase.label} browser must POST confirm form before create redirect`);

	const idempotencyAfterCreate = idempotencyRows(stack.appDbPath, testCase.bookId).filter((row) => row.state === 'succeeded');
	assert.equal(idempotencyAfterCreate.length, 1, `${testCase.label} one succeeded idempotency after create`);
	const transactionId = idempotencyAfterCreate[0].planned_transaction_guid;
	assert.match(transactionId, /^[0-9a-f]{32}$/, `${testCase.label} planned GUID shape`);

	const duplicate = await browserReplayConfirm(cdp, hidden);
	assert.ok([200, 303].includes(duplicate.status), `${testCase.label} duplicate browser replay status ${duplicate.status}`);
	if (duplicate.status === 303) assert.ok(duplicate.location.includes('already_created'), `${testCase.label} duplicate redirects as already_created`);
	counters.target_duplicate += 1;

	const apiDetail = await verifyApiReadback(stack.apiBase, stack.token, testCase, testCase.bookId, transactionId);
	const directSnapshot = verifyDirectBookReadback(testCase, transactionId);
	const afterAccounts = accountBalancesById((await apiJson(stack.apiBase, stack.token, `/books/${testCase.bookId}/accounts`)).body);
	for (const split of testCase.request.splits) {
		const actualDelta = decimalSubtract(afterAccounts[split.account_id], beforeAccounts[split.account_id]);
		const expectedDelta = expectedDisplayDeltaForSplit(testCase, split);
		assert.ok(decimalEqual(actualDelta, expectedDelta), `${testCase.label} display delta for ${split.account_id}: expected ${expectedDelta}, got ${actualDelta}`);
	}
	const backup = verifySuccessfulBackup(testCase);
	const metadata = verifyMetadataSuccess(stack.appDbPath, testCase.bookId, transactionId);
	const routes = await verifyOrdinaryRoutes(cdp, stack.webBase, testCase, testCase.bookId);

	const afterTargetHash = hashFile(testCase.targetPath);
	assert.notEqual(afterTargetHash, beforeTargetHash, `${testCase.label} target hash must change`);
	assert.equal(hashFile(testCase.sourcePath), beforeSourceHash, `${testCase.label} source hash must stay unchanged`);
	assert.equal(bookSnapshot(testCase.sourcePath).transactions, testCase.sourceSnapshotBefore.transactions, `${testCase.label} source transaction count unchanged`);
	assert.equal(bookSnapshot(testCase.sourcePath).splits, testCase.sourceSnapshotBefore.splits, `${testCase.label} source split count unchanged`);
	assert.equal(directSnapshot.transactions, testCase.targetSnapshotBefore.transactions + 1, `${testCase.label} exact one transaction after duplicate`);
	assert.equal(directSnapshot.splits, testCase.targetSnapshotBefore.splits + testCase.request.splits.length, `${testCase.label} exact split delta after duplicate`);
	counters.target_create += 1;

	const stubbedConfirmGuard = {
		browser_confirm_route_seen: confirmRequests.some((item) => item.url.includes('/transactions/new?/confirm')),
		target_hash_changed: beforeTargetHash !== afterTargetHash,
		planned_guid_read_back: apiDetail.id === transactionId && directSnapshot.transaction.id === transactionId,
		idempotency_succeeded: metadata.idempotency.filter((row) => row.state === 'succeeded').length,
		ownership_rows: metadata.ownership.length,
		backup_files: backup.files,
		verified_backup_markers: backup.markers
	};
	assert.deepEqual(stubbedConfirmGuard, {
		browser_confirm_route_seen: true,
		target_hash_changed: true,
		planned_guid_read_back: true,
		idempotency_succeeded: 1,
		ownership_rows: 1,
		backup_files: 1,
		verified_backup_markers: 1
	}, `${testCase.label} stubbed confirm guard`);

	return {
		case: testCase.name,
		book_id: testCase.bookId,
		transaction_id: transactionId,
		preview_route_statuses: previewRoutes.map((item) => item.status),
		confirm_route_statuses: confirmRoutes.map((item) => item.status),
		confirm_request_count: confirmRequests.length,
		duplicate_status: duplicate.status,
		source_hash_before: beforeSourceHash,
		source_hash_after: hashFile(testCase.sourcePath),
		target_hash_before: beforeTargetHash,
		target_hash_after: afterTargetHash,
		target_counts: { before: testCase.targetSnapshotBefore, after: { transactions: directSnapshot.transactions, splits: directSnapshot.splits } },
		backup,
		metadata: { idempotency_rows: metadata.idempotency.length, audit_rows: metadata.audits.length, ownership_rows: metadata.ownership.length },
		routes,
		stubbed_confirm_guard: stubbedConfirmGuard
	};
}

async function previewCase({ stack, testCase }) {
	const { cdp } = stack.browser;
	await setSession(cdp, stack.webBase, stack.token, testCase.bookId);
	await navigate(cdp, stack.webBase, '/transactions/new', `${testCase.label} create page`);
	await waitForExpression(cdp, `document.querySelector('#transaction-create-form')`, `${testCase.label} form visible`);
	await fillTransactionForm(cdp, testCase.request);
	const responseStart = stack.browser.responses.length;
	const requestStart = stack.browser.requests.length;
	await submitPreview(cdp);
	return { responseStart, requestStart };
}

function assertZeroMutation(testCase, beforeHash, beforeSnapshot, label) {
	assert.equal(hashFile(testCase.targetPath), beforeHash, `${label} target hash unchanged`);
	const after = bookSnapshot(testCase.targetPath);
	assert.equal(after.transactions, beforeSnapshot.transactions, `${label} transaction count unchanged`);
	assert.equal(after.splits, beforeSnapshot.splits, `${label} split count unchanged`);
	assert.equal(hashFile(testCase.sourcePath), testCase.sourceHash, `${label} source hash unchanged`);
}

async function runChangedPayloadRejection({ stack, testCase, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `document.querySelector('#confirm-create-form')`, `${testCase.label} confirm visible`);
	await mutateConfirmTransactionJson(stack.browser.cdp, `(transaction) => { transaction.description = transaction.description + ' changed'; }`);
	await submitConfirmForm(stack.browser.cdp);
	await waitForExpression(stack.browser.cdp, `document.querySelector('#transaction-create-error-summary') && document.body.innerText.includes('Draft no longer matches the preview')`, `${testCase.label} changed payload rejected UI`);
	const confirmRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/confirm');
	const confirmRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/confirm');
	assert.ok(confirmRequests.some((item) => item.method === 'POST'), `${testCase.label} changed payload confirm POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	counters.target_rejected += 1;
	return { case: testCase.label, code: 'PREVIEW_PAYLOAD_MISMATCH', route_statuses: confirmRoutes.map((item) => item.status), route_request_count: confirmRequests.length, target_hash: beforeHash };
}

async function runStaleRejection({ stack, testCase, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `document.querySelector('#confirm-create-form')`, `${testCase.label} confirm visible`);
	const now = new Date();
	utimesSync(testCase.targetPath, now, now);
	await submitConfirmForm(stack.browser.cdp);
	await waitForExpression(stack.browser.cdp, `document.querySelector('#transaction-create-error-summary') && document.body.innerText.includes('Book or policy changed after preview')`, `${testCase.label} stale rejected UI`);
	const confirmRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/confirm');
	const confirmRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/confirm');
	assert.ok(confirmRequests.some((item) => item.method === 'POST'), `${testCase.label} stale confirm POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	counters.target_rejected += 1;
	return { case: testCase.label, code: 'PREVIEW_STALE', route_statuses: confirmRoutes.map((item) => item.status), route_request_count: confirmRequests.length, target_hash: beforeHash };
}

async function runDisabledPreview({ stack, testCase, expectedText, code, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `!document.querySelector('#confirm-create-form') && (((document.body && document.body.innerText) || '').includes(${jsString(expectedText)}) || ((document.body && document.body.innerText) || '').includes('Transaction create request failed safely'))`, `${testCase.label} disabled preview UI`);
	const previewRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/preview');
	const previewRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/preview');
	assert.ok(previewRequests.some((item) => item.method === 'POST'), `${testCase.label} disabled preview POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	counters.target_rejected += 1;
	return { case: testCase.label, code, route_statuses: previewRoutes.map((item) => item.status), route_request_count: previewRequests.length, target_hash: beforeHash };
}

async function runCrossCommodityRejection({ stack, testCase, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `document.querySelector('#transaction-create-error-summary') && document.body.innerText.includes('No FX conversion is performed')`, `${testCase.label} commodity mismatch UI`);
	const previewRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/preview');
	const previewRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/preview');
	assert.ok(previewRequests.some((item) => item.method === 'POST'), `${testCase.label} commodity mismatch preview POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	counters.target_rejected += 1;
	return { case: testCase.label, code: 'COMMODITY_MISMATCH', route_statuses: previewRoutes.map((item) => item.status), route_request_count: previewRequests.length, target_hash: beforeHash };
}

function lockFileForBook(bookId) {
	return join(lockDir, `book_${bookId}.lock`);
}

async function acquireExternalBookLock(bookId) {
	mkdirSync(lockDir, { recursive: true });
	const lockPath = lockFileForBook(bookId);
	const child = spawnLogged(apiPython, ['-c', `import fcntl, os, sys, time\npath=sys.argv[1]\nos.makedirs(os.path.dirname(path), exist_ok=True)\nfd=os.open(path, os.O_CREAT|os.O_RDWR)\nfcntl.flock(fd, fcntl.LOCK_EX)\nprint('LOCKED', flush=True)\ntime.sleep(120)`, lockPath], {
		cwd: apiRoot,
		env: { ...process.env, PATH: apiPythonPath() }
	});
	const started = Date.now();
	while (!child.outputTail().includes('LOCKED')) {
		if (Date.now() - started > 10000) throw new Error(`Timed out acquiring external lock for book ${bookId}: ${child.outputTail()}`);
		await sleep(100);
	}
	return { child, lockPath };
}

async function runLockBusy({ stack, testCase, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `document.querySelector('#confirm-create-form')`, `${testCase.label} confirm visible`);
	const lock = await acquireExternalBookLock(testCase.bookId);
	try {
		await submitConfirmForm(stack.browser.cdp);
		await waitForExpression(stack.browser.cdp, `document.querySelector('#transaction-create-error-summary') && document.body.innerText.includes('Book write lock is busy')`, `${testCase.label} lock busy UI`);
	} finally {
		await stopProcess(lock.child);
	}
	const confirmRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/confirm');
	const confirmRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/confirm');
	assert.ok(confirmRequests.some((item) => item.method === 'POST'), `${testCase.label} lock busy confirm POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	const rejected = idempotencyRows(stack.appDbPath, testCase.bookId).filter((row) => row.safe_error_code === 'BOOK_WRITE_BUSY');
	assert.equal(rejected.length, 1, `${testCase.label} BOOK_WRITE_BUSY idempotency rejection`);
	counters.target_rejected += 1;
	return { case: testCase.label, code: 'BOOK_WRITE_BUSY', retryable: true, route_statuses: confirmRoutes.map((item) => item.status), route_request_count: confirmRequests.length, idempotency_rejected: rejected.length, target_hash: beforeHash };
}

async function runBackupFailed({ stack, testCase, counters }) {
	const beforeHash = hashFile(testCase.targetPath);
	const beforeSnapshot = bookSnapshot(testCase.targetPath);
	const { responseStart, requestStart } = await previewCase({ stack, testCase });
	await waitForExpression(stack.browser.cdp, `document.querySelector('#confirm-create-form')`, `${testCase.label} confirm visible`);
	const firstHidden = await readConfirmHidden(stack.browser.cdp);
	const backupRoot = join(dirname(dirname(testCase.targetPath)), 'backups', basename(testCase.targetPath, '.sqlite'));
	mkdirSync(backupRoot, { recursive: true });
	chmodSync(backupRoot, 0o555);
	try {
		await submitConfirmForm(stack.browser.cdp);
		await waitForExpression(stack.browser.cdp, `document.querySelector('#transaction-create-error-summary') && document.body.innerText.includes('Backup failed before write')`, `${testCase.label} backup failed UI`);
	} finally {
		chmodSync(backupRoot, 0o755);
	}
	const confirmRoutes = routeResponsesSince(stack.browser, responseStart, '/transactions/new?/confirm');
	const confirmRequests = routeRequestsSince(stack.browser, requestStart, '/transactions/new?/confirm');
	assert.ok(confirmRequests.some((item) => item.method === 'POST'), `${testCase.label} backup failed confirm POST observed`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, testCase.label);
	const rejected = idempotencyRows(stack.appDbPath, testCase.bookId).filter((row) => row.safe_error_code === 'BACKUP_FAILED');
	assert.equal(rejected.length, 1, `${testCase.label} BACKUP_FAILED idempotency rejection`);

	await navigate(stack.browser.cdp, stack.webBase, '/transactions/new', `${testCase.label} backup retry page`);
	await fillTransactionForm(stack.browser.cdp, testCase.request);
	await submitPreview(stack.browser.cdp);
	await waitForExpression(stack.browser.cdp, `document.querySelector('#confirm-create-form')`, `${testCase.label} fresh preview after backup failure`);
	const freshHidden = await readConfirmHidden(stack.browser.cdp);
	assert.notEqual(freshHidden.idempotency_key, firstHidden.idempotency_key, `${testCase.label} fresh preview gets new idempotency key`);
	assert.notEqual(freshHidden.preview_token, firstHidden.preview_token, `${testCase.label} fresh preview gets new token`);
	assertZeroMutation(testCase, beforeHash, beforeSnapshot, `${testCase.label} after fresh preview`);
	counters.target_rejected += 1;
	return { case: testCase.label, code: 'BACKUP_FAILED', retryable: false, route_statuses: confirmRoutes.map((item) => item.status), route_request_count: confirmRequests.length, idempotency_rejected: rejected.length, fresh_key_changed: true, target_hash: beforeHash };
}

async function createBrowserStack({ tempRoot, appDbPath, allowedRoots, writesEnabled }) {
	const apiPort = await getFreePort();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	const apiBase = `http://127.0.0.1:${apiPort}`;
	const webBase = `http://127.0.0.1:${webPort}`;
	const apiProcess = await startApi({ tempRoot, appDbPath, allowedRoots, writesEnabled, port: apiPort });
	const token = await login(apiBase);
	const webProcess = await startWeb({ apiBase, port: webPort });
	const profileDir = mkdtempSync(join(tempRoot, 'chrome-'));
	const browser = await startBrowser({ profileDir, debugPort });
	return { apiBase, webBase, appDbPath, token, apiProcess, webProcess, browser, profileDir };
}

async function stopStack(stack) {
	if (!stack) return;
	stack.browser?.cdp?.close();
	await stopProcess(stack.browser?.chromeProcess);
	await stopProcess(stack.webProcess);
	await stopProcess(stack.apiProcess);
	if (stack.profileDir) rmSync(stack.profileDir, { recursive: true, force: true });
}

function cleanupLockFiles(bookIds) {
	for (const bookId of bookIds) {
		try {
			unlinkSync(lockFileForBook(bookId));
		} catch {
			// already absent
		}
	}
}

async function runGlobalDisabledCase({ tempRoot, manifest, counters, registeredBookIds }) {
	const root = join(tempRoot, 'global-disabled');
	mkdirSync(root, { recursive: true });
	const testCase = makeScenarioCase(manifest, 'income', 'global-disabled', root, counters);
	const appDbPath = join(root, 'app', 'app.db');
	const apiPort = await getFreePort();
	const apiBase = `http://127.0.0.1:${apiPort}`;
	let apiProcess = await startApi({ tempRoot: root, appDbPath, allowedRoots: [root], writesEnabled: true, port: apiPort });
	try {
		const token = await login(apiBase);
		const registration = await registerBook(apiBase, token, testCase, { name: 'Global disabled real browser', enableCreate: true });
		testCase.bookId = registration.bookId;
		registeredBookIds.push(registration.bookId);
	} finally {
		await stopProcess(apiProcess);
	}

	const stack = await createBrowserStack({ tempRoot: root, appDbPath, allowedRoots: [root], writesEnabled: false });
	try {
		stack.token = await login(stack.apiBase);
		return await runDisabledPreview({ stack, testCase, expectedText: 'CREATE is disabled by deployment settings.', code: 'CREATE_DEPLOYMENT_DISABLED', counters });
	} finally {
		await stopStack(stack);
	}
}

function assertNoForbiddenBrowserMutations(browserStates) {
	const allRequests = browserStates.flatMap((state) => state.requests ?? []);
	const forbidden = allRequests.filter((request) => {
		const url = new URL(request.url, 'http://127.0.0.1');
		return ['PATCH', 'DELETE', 'PUT'].includes(request.method) || /batch|import|ofx|csv|upload|source_deletion/i.test(url.pathname + url.search);
	});
	assert.deepEqual(forbidden, [], 'browser must not send forbidden PATCH/DELETE/PUT/batch/import/upload/source-deletion requests');
	return { browser_requests: allRequests.length, forbidden_mutations: forbidden.length };
}

async function runSmoke() {
	assert.ok(apiPython === 'python' || existsSync(apiPython), `backend Python missing at ${apiPython}`);
	assert.ok(existsSync(viteBin), 'Vite must be installed before running real browser gate');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before browser gate; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);
	const packageJson = JSON.parse(readFileSync(join(webRoot, 'package.json'), 'utf8'));
	assert.equal(packageJson.scripts?.['test:transaction-create-real-browser'], 'npm run build && node scripts/test-transaction-create-real-product-browser.mjs', 'package.json must expose the real product browser gate');

	const tempRoot = mkdtempSync(join(tmpdir(), 'gwc-real-create-browser-'));
	const counters = {
		fixture_seed: 59017,
		generated_sources_created: 5,
		generated_sources_copied: 0,
		generated_sources_modified: 0,
		generated_sources_deleted: 0,
		target_copied: 0,
		target_create: 0,
		target_duplicate: 0,
		target_rejected: 0,
		target_patch: 0,
		target_delete: 0,
		target_restored: 0,
		owner_private_list_access_probe_hash_copy_create_patch_delete_batch_source_deletion: 0
	};
	const registeredBookIds = [];
	const browserStates = [];
	let mainStack;
	try {
		const fixtureRoot = join(tempRoot, 'generated');
		const manifest = generateFixtureManifest(fixtureRoot);
		assert.equal(manifest.seed, 59017, 'generated fixture seed must be stable');
		for (const caseName of ['expense', 'income', 'three_split', 'unicode', 'incompatible_commodity']) {
			assert.equal(hashFile(manifest.cases[caseName].source_path), manifest.cases[caseName].source_hash, `${caseName} source hash manifest`);
		}

		const mainRoot = join(tempRoot, 'main');
		mkdirSync(mainRoot, { recursive: true });
		const successCases = [
			makeScenarioCase(manifest, 'expense', 'success-expense', mainRoot, counters),
			makeScenarioCase(manifest, 'income', 'success-income', mainRoot, counters),
			makeScenarioCase(manifest, 'three_split', 'success-three-split', mainRoot, counters),
			makeScenarioCase(manifest, 'unicode', 'success-unicode', mainRoot, counters)
		];
		const changedCase = makeScenarioCase(manifest, 'expense', 'reject-changed-payload', mainRoot, counters);
		const staleCase = makeScenarioCase(manifest, 'expense', 'reject-stale-source', mainRoot, counters);
		const perBookDisabledCase = makeScenarioCase(manifest, 'income', 'reject-per-book-disabled', mainRoot, counters);
		const lockBusyCase = makeScenarioCase(manifest, 'three_split', 'reject-lock-busy', mainRoot, counters);
		const backupFailedCase = makeScenarioCase(manifest, 'three_split', 'reject-backup-failed', mainRoot, counters);
		const incompatibleCase = makeScenarioCase(manifest, 'expense', 'reject-cross-commodity', mainRoot, counters);
		incompatibleCase.request = { ...incompatibleCase.request, currency: 'USD' };

		mainStack = await createBrowserStack({ tempRoot: mainRoot, appDbPath: join(mainRoot, 'app', 'app.db'), allowedRoots: [mainRoot], writesEnabled: true });
		browserStates.push(mainStack.browser);
		for (const testCase of [...successCases, changedCase, staleCase, lockBusyCase, backupFailedCase, incompatibleCase]) {
			const registration = await registerBook(mainStack.apiBase, mainStack.token, testCase, { name: `Real browser ${testCase.label}`, enableCreate: true });
			testCase.bookId = registration.bookId;
			registeredBookIds.push(registration.bookId);
		}
		{
			const registration = await registerBook(mainStack.apiBase, mainStack.token, perBookDisabledCase, { name: 'Real browser per-book disabled', enableCreate: false });
			perBookDisabledCase.bookId = registration.bookId;
			registeredBookIds.push(registration.bookId);
		}

		const successes = [];
		for (const testCase of successCases) {
			successes.push(await runSuccessfulCase({ stack: mainStack, testCase, counters }));
		}
		const changed = await runChangedPayloadRejection({ stack: mainStack, testCase: changedCase, counters });
		const stale = await runStaleRejection({ stack: mainStack, testCase: staleCase, counters });
		const perBookDisabled = await runDisabledPreview({ stack: mainStack, testCase: perBookDisabledCase, expectedText: 'CREATE is disabled for this book.', code: 'CREATE_BOOK_DISABLED', counters });
		const lockBusy = await runLockBusy({ stack: mainStack, testCase: lockBusyCase, counters });
		const backupFailed = await runBackupFailed({ stack: mainStack, testCase: backupFailedCase, counters });
		const crossCommodity = await runCrossCommodityRejection({ stack: mainStack, testCase: incompatibleCase, counters });
		const globalDisabled = await runGlobalDisabledCase({ tempRoot, manifest, counters, registeredBookIds });

		const browserSafety = assertNoForbiddenBrowserMutations(browserStates);
		const consoleEvents = browserStates.flatMap((state) => state.consoleEvents);
		assert.deepEqual(consoleEvents, [], 'browser console must not contain warnings/errors');
		const sourceTemplateTotals = Object.fromEntries(
			Object.entries(manifest.cases).map(([caseName, testCase]) => [caseName, { hash: hashFile(testCase.source_path), snapshot: bookSnapshot(testCase.source_path) }])
		);
		for (const [caseName, item] of Object.entries(sourceTemplateTotals)) {
			assert.equal(item.hash, manifest.cases[caseName].source_hash, `${caseName} final generated source hash unchanged`);
		}

		const summary = {
			fixture_seed: manifest.seed,
			successes,
			rejections: [changed, stale, globalDisabled, perBookDisabled, lockBusy, backupFailed, crossCommodity],
			counters,
			browser_safety: browserSafety,
			console_events: consoleEvents.length,
			source_template_totals: {
				all_hashes_unchanged: Object.entries(sourceTemplateTotals).every(([caseName, item]) => item.hash === manifest.cases[caseName].source_hash),
				transactions: Object.fromEntries(Object.entries(sourceTemplateTotals).map(([caseName, item]) => [caseName, item.snapshot.transactions])),
				splits: Object.fromEntries(Object.entries(sourceTemplateTotals).map(([caseName, item]) => [caseName, item.snapshot.splits]))
			},
			registered_books: registeredBookIds.length,
			temp_root_cleaned_by_trap: true
		};
		assert.equal(summary.successes.length, 4, 'four success cases required');
		assert.equal(summary.rejections.length, 7, 'seven rejection/disabled/busy/backup outcomes required');
		assert.equal(counters.target_create, 4, 'target CREATE counter');
		assert.equal(counters.target_duplicate, 4, 'duplicate counter');
		assert.equal(counters.target_rejected, 7, 'rejected/disabled outcome counter');
		assert.equal(counters.target_patch, 0, 'target PATCH counter');
		assert.equal(counters.target_delete, 0, 'target DELETE counter');
		assert.equal(counters.owner_private_list_access_probe_hash_copy_create_patch_delete_batch_source_deletion, 0, 'owner/private source vector counter');
		console.log(`ok - real ordinary-product browser CREATE gate passed success=${summary.successes.length} duplicate=${counters.target_duplicate} rejected=${counters.target_rejected} browser_requests=${browserSafety.browser_requests}`);
		console.log(`REAL_CREATE_BROWSER_SUMMARY ${JSON.stringify(summary, sortKeysReplacer, 0)}`);
		return summary;
	} finally {
		await stopStack(mainStack);
		cleanupLockFiles(registeredBookIds);
		rmSync(tempRoot, { recursive: true, force: true });
	}
}

function sortKeysReplacer(_key, value) {
	if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
	return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)));
}

runSmoke().catch((error) => {
	console.error(error);
	process.exitCode = 1;
});
