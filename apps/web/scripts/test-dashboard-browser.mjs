import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(root, '.svelte-kit', 'output', 'server', 'index.js');
const smokeHome = process.env.DASHBOARD_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.DASHBOARD_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-dashboard');
const syntheticToken = 'synthetic-dashboard-smoke-token';
const privateDashboardSentinel = 'PRIVATE_DASHBOARD_SENTINEL_ACCOUNT_PATH_GUID';
const cdpCommandTimeoutMs = Number(process.env.DASHBOARD_CDP_TIMEOUT_MS ?? '90000');

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

const syntheticBook = {
	id: 1,
	name: 'Synthetic Dashboard Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for dashboard browser smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic dashboard fixture.',
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
		message: 'Synthetic local dashboard smoke fixture; no private book is used.'
	}
};

function jsonResponse(res, status, body) {
	const payload = Buffer.from(JSON.stringify(body));
	res.writeHead(status, {
		'content-type': 'application/json',
		'content-length': String(payload.length)
	});
	res.end(payload);
}

function summaryPayload(mode) {
	if (mode === 'empty') {
		return {
			currency: 'SEK',
			net_worth: '0.00',
			assets: '0.00',
			liabilities: '0.00',
			income_this_month: '0.00',
			expenses_this_month: '0.00',
			as_of_date: '2026-07-31',
			reporting_basis: 'base_currency_only',
			includes_currency_conversion: false,
			limitations: []
		};
	}
	return {
		currency: 'SEK',
		net_worth: '1450.00',
		assets: '2000.00',
		liabilities: '-550.00',
		income_this_month: '125.00',
		expenses_this_month: '45.67',
		as_of_date: '2026-07-31',
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: ['base_currency_only: No FX conversion; synthetic fixture excludes non-base currencies.']
	};
}

function expensesPayload(mode) {
	if (mode === 'empty') return [];
	return [{ account_id: 'expense-food', account_name: 'Synthetic Food', total: '45.67', currency: 'SEK' }];
}

function cashflowPayload(mode) {
	if (mode === 'empty') return [];
	return [{ month: '2026-07', inflow: '125.00', outflow: '45.67', net: '79.33' }];
}

function recentTransactionsPayload(mode) {
	if (mode === 'empty') return [];
	return [
		{
			id: 'tx-dashboard-1',
			date: '2026-07-11',
			description: 'Synthetic Salary',
			amount: '125.00',
			currency: 'SEK',
			account_id: 'income-salary',
			account_name: 'Synthetic Income',
			counter_account_name: 'Synthetic Bank'
		}
	];
}

function isForbiddenApiMutation(method, pathname, search = '') {
	const upper = method.toUpperCase();
	if (upper !== 'GET' && upper !== 'HEAD') return true;
	const target = `${pathname}${search}`;
	return /(?:\/|%2F)(?:transactions|backups?|audit|write-alpha|owner-writebeta)(?:\/|$|[?&=])/i.test(target)
		|| /(?:\/|%2F|[?&=])(?:validate|preflight|create|patch|delete|batch)(?:\/|%2F|$|[?&=])/i.test(target);
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	const state = { mode: 'empty' };
	const server = createServer((req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });

		if (isForbiddenApiMutation(req.method ?? 'GET', url.pathname, url.search)) {
			forbiddenRequests.push({ method: req.method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, { detail: 'Synthetic dashboard smoke blocked a mutation-capable endpoint.' });
		}
		if (req.method === 'GET' && url.pathname === '/health') {
			return jsonResponse(res, 200, { status: 'ok', first_run: null });
		}
		if (req.method === 'GET' && url.pathname === '/auth/me') {
			return jsonResponse(res, 200, { id: 1, username: 'synthetic_dashboard', display_name: 'Synthetic Dashboard', is_admin: false });
		}
		if (req.method === 'GET' && url.pathname === '/books') {
			return jsonResponse(res, 200, [syntheticBook]);
		}
		if (req.method !== 'GET' || !url.pathname.startsWith('/books/1/reports/')) {
			return jsonResponse(res, 404, { detail: 'Synthetic dashboard smoke endpoint not found.' });
		}

		if (url.pathname === '/books/1/reports/summary') return jsonResponse(res, 200, summaryPayload(state.mode));
		if (url.pathname === '/books/1/reports/recent-transactions') return jsonResponse(res, 200, recentTransactionsPayload(state.mode));
		if (url.pathname === '/books/1/reports/expenses-by-account') {
			if (state.mode === 'failed-sections') return jsonResponse(res, 500, { detail: privateDashboardSentinel });
			return jsonResponse(res, 200, expensesPayload(state.mode));
		}
		if (url.pathname === '/books/1/reports/cashflow') {
			if (state.mode === 'failed-sections') return jsonResponse(res, 500, { detail: privateDashboardSentinel });
			return jsonResponse(res, 200, cashflowPayload(state.mode));
		}
		return jsonResponse(res, 404, { detail: 'Synthetic dashboard smoke endpoint not found.' });
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
		setMode: (mode) => {
			state.mode = mode;
		},
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
				// retry until timeout
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
			output = output.slice(-12000);
		});
	}
	child.outputTail = () => output;
	return child;
}

async function stopProcess(child) {
	if (!child || child.exitCode !== null) return;
	await new Promise((resolve) => {
		let resolved = false;
		let forceKillTimer;
		let giveUpTimer;
		const finish = () => {
			if (resolved) return;
			resolved = true;
			clearTimeout(forceKillTimer);
			clearTimeout(giveUpTimer);
			resolve();
		};
		child.once('exit', finish);
		child.kill('SIGTERM');
		forceKillTimer = setTimeout(() => {
			if (child.exitCode === null) child.kill('SIGKILL');
		}, 3000);
		giveUpTimer = setTimeout(finish, 8000);
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

async function waitForExpression(cdp, expression, label, timeoutMs = 15000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		if (await evaluate(cdp, expression)) return;
		await new Promise((resolve) => setTimeout(resolve, 150));
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

async function navigateDashboard(cdp, webBase, label) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 20000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}/dashboard?smoke=${encodeURIComponent(label)}` });
	await Promise.race([
		load,
		waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === '/dashboard' && document.body?.innerText.includes('Dashboard')`, label, 20000)
	]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === '/dashboard' && document.body?.innerText.includes('Dashboard')`, label, 20000);
}

function forbiddenBrowserMutationRequests(browserRequests) {
	return browserRequests.filter((request) => {
		const url = new URL(request.url);
		if (!['POST', 'PATCH', 'DELETE', 'PUT'].includes(request.method)) return false;
		return !url.pathname.startsWith('/login');
	});
}

function assertNoMutationRequestsObserved(api, browserRequests, label) {
	assert.deepEqual(api.forbiddenRequests, [], `${label}: synthetic API must observe zero mutation-capable requests`);
	assert.deepEqual(forbiddenBrowserMutationRequests(browserRequests), [], `${label}: browser must issue zero mutation-capable requests`);
}

async function assertEmptyDashboard(cdp) {
	const state = await evaluate(cdp, `(() => ({
		bodyText: document.body?.innerText ?? '',
		sectionErrorCount: document.querySelectorAll('[data-dashboard-section-error][role="alert"]').length
	}))()`);
	assert.match(state.bodyText, /No transactions found\./, 'empty dashboard must keep recent-transactions empty state');
	assert.match(state.bodyText, /No expenses found for the selected period\./, 'empty dashboard must keep expenses empty state');
	assert.match(state.bodyText, /No cashflow data for the selected period\./, 'empty dashboard must keep cashflow empty state');
	assert.equal(state.sectionErrorCount, 0, 'empty dashboard must not render section-error alerts');
	assert.doesNotMatch(state.bodyText, /Dashboard section unavailable|could not be loaded|Backend details were redacted/, 'empty dashboard must not be confused with failed sections');
}

async function assertFailedSectionsDashboard(cdp) {
	const state = await evaluate(cdp, `(() => ({
		bodyText: document.body?.innerText ?? '',
		sectionErrorLabels: Array.from(document.querySelectorAll('[data-dashboard-section-error][role="alert"]')).map((node) => node.textContent.replace(/\\s+/g, ' ').trim())
	}))()`);
	assert.ok(state.sectionErrorLabels.length >= 2, 'failed dashboard sections must render accessible per-section alerts');
	assert.match(state.bodyText, /Dashboard section unavailable/, 'failed sections must show fixed section-error title');
	assert.match(state.bodyText, /This dashboard section could not be loaded\. Other sections are still shown when available\. Backend details were redacted\./, 'failed sections must show fixed redacted copy');
	assert.match(state.bodyText, /Synthetic Salary/, 'unaffected recent transactions section must remain visible');
	assert.match(state.bodyText, /1450\.00/, 'unaffected summary section must remain visible');
	assert.doesNotMatch(state.bodyText, /No expenses found for the selected period\./, 'failed expenses must not be presented as genuine empty data');
	assert.doesNotMatch(state.bodyText, /No cashflow data for the selected period\./, 'failed cashflow must not be presented as genuine empty data');
	assert.doesNotMatch(state.bodyText, new RegExp(privateDashboardSentinel.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), 'failed sections must redact backend details and private paths');
	assert.doesNotMatch(state.bodyText, /\/books\/1\/reports|PRIVATE_DASHBOARD_SENTINEL|ACCOUNT_PATH_GUID/, 'failed sections must not expose backend paths or private sentinels');
}

function assertStaticSafety() {
	const server = readFileSync(join(root, 'src', 'routes', 'dashboard', '+page.server.ts'), 'utf8');
	const page = readFileSync(join(root, 'src', 'routes', 'dashboard', '+page.svelte'), 'utf8');
	assert.match(server, /sectionErrors[\s\S]*summary[\s\S]*expenses[\s\S]*cashflow[\s\S]*recentTransactions/s, 'dashboard server must return explicit per-section error state');
	assert.match(page, /data-dashboard-section-error[\s\S]*role="alert"[\s\S]*dashboard\.sectionError\.redacted/s, 'dashboard page must render accessible fixed-copy section errors');
	assert.doesNotMatch(server, /e\.message|error\.message/, 'dashboard server must not return raw backend exception messages');
	assert.doesNotMatch(`${server}\n${page}`, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income)/, 'dashboard must not use float/Number conversion on money strings');
	assert.doesNotMatch(page, /localStorage|sessionStorage|formaction="\?\/create"|method="POST"/s, 'dashboard must not add browser storage or write submissions');
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the dashboard browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before dashboard browser smoke; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	mkdirSync(smokeTempRoot, { recursive: true });
	const profileDir = mkdtempSync(join(smokeTempRoot, 'dashboard-browser-'));
	let webProcess;
	let chromiumProcess;
	let cdp;
	const browserRequests = [];

	try {
		webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
			cwd: root,
			env: {
				...process.env,
				API_INTERNAL_URL: api.url,
				APP_ENV: 'test',
				GNUCASH_WRITES_ENABLED: 'false',
				JWT_SECRET: 'dummy-dashboard-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-dashboard-browser-smoke-password'
			}
		});
		const webBase = `http://127.0.0.1:${webPort}`;
		await waitForHttp(`${webBase}/login`, 45000);

		chromiumProcess = spawnLogged(chromiumBin, [
			'--headless',
			'--disable-gpu',
			'--disable-dev-shm-usage',
			'--disable-background-networking',
			'--disable-component-update',
			'--disable-default-apps',
			'--disable-extensions',
			'--disable-sync',
			'--metrics-recording-only',
			'--no-first-run',
			'--no-proxy-server',
			'--proxy-server=direct://',
			'--proxy-bypass-list=*',
			'--no-sandbox',
			'--remote-debugging-address=127.0.0.1',
			`--remote-debugging-port=${debugPort}`,
			`--user-data-dir=${profileDir}`,
			'--window-size=320,760',
			'about:blank'
		], {
			cwd: root,
			env: {
				...process.env,
				TMPDIR: smokeTempRoot,
				TMP: smokeTempRoot,
				TEMP: smokeTempRoot
			}
		});

		cdp = await connectCdp(debugPort);
		cdp.on('Network.requestWillBeSent', (params) => {
			browserRequests.push({ method: params.request.method, url: params.request.url });
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 760, deviceScaleFactor: 2, mobile: true });
		await cdp.send('Network.setCookie', { name: 'access_token', value: syntheticToken, url: webBase, path: '/', sameSite: 'Lax' });

		api.setMode('empty');
		await navigateDashboard(cdp, webBase, 'empty dashboard');
		await assertEmptyDashboard(cdp);
		assertNoMutationRequestsObserved(api, browserRequests, 'empty dashboard');

		api.setMode('failed-sections');
		await navigateDashboard(cdp, webBase, 'failed dashboard sections');
		await assertFailedSectionsDashboard(cdp);
		assertNoMutationRequestsObserved(api, browserRequests, 'failed dashboard sections');

		assertStaticSafety();
		console.log(`dashboard browser smoke passed: api_requests=${api.requests.length} api_forbidden=${api.forbiddenRequests.length} browser_forbidden=${forbiddenBrowserMutationRequests(browserRequests).length}`);
	} catch (error) {
		const webTail = webProcess?.outputTail?.() ?? '';
		const chromiumTail = chromiumProcess?.outputTail?.() ?? '';
		throw new Error(`${error.message}\n--- vite preview tail ---\n${webTail}\n--- chromium tail ---\n${chromiumTail}`);
	} finally {
		cdp?.close();
		await stopProcess(chromiumProcess);
		await stopProcess(webProcess);
		await api.close();
		rmSync(profileDir, { recursive: true, force: true });
	}
}

await runSmoke();
