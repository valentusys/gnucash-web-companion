import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const smokeHome = process.env.TRANSACTIONS_EXPLORER_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.TRANSACTIONS_EXPLORER_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-transactions-explorer');
const syntheticToken = 'synthetic-transactions-explorer-smoke-token';
const accountId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const secondAccountId = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const cdpCommandTimeoutMs = Number(process.env.TRANSACTIONS_EXPLORER_CDP_TIMEOUT_MS ?? '90000');

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
	name: 'Synthetic Explorer Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for explorer browser smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic explorer fixture.',
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
		message: 'Synthetic local transactions explorer smoke fixture; no private book is used.'
	}
};

const accounts = [
	{ id: accountId, name: 'Synthetic Checking', full_name: 'Assets:Synthetic Checking', type: 'ASSET', currency: 'SEK', balance: '123.45', placeholder: false, hidden: false, parent_id: null },
	{ id: secondAccountId, name: 'Synthetic Expenses', full_name: 'Expenses:Synthetic', type: 'EXPENSE', currency: 'SEK', balance: '0.00', placeholder: false, hidden: false, parent_id: null }
];

function jsonResponse(res, status, body) {
	const payload = Buffer.from(JSON.stringify(body));
	res.writeHead(status, {
		'content-type': 'application/json',
		'content-length': String(payload.length)
	});
	res.end(payload);
}

function explorerPayload(url) {
	const pageSize = Number(url.searchParams.get('page_size') ?? '50');
	const cursor = url.searchParams.get('cursor') ?? '';
	const query = url.searchParams.get('query') ?? '';
	const description = query ? `Synthetic ${query} explorer transaction` : 'Synthetic explorer transaction';
	const id = cursor ? 'tx-explorer-2' : 'tx-explorer-1';
	return {
		items: [
			{
				id,
				date: cursor ? '2026-07-12' : '2026-07-11',
				description,
				representative_amount: { amount: cursor ? '20.00' : '10.50', currency: 'SEK' },
				representative_account: { id: accountId, name: 'Synthetic Checking' },
				matched_amount: { amount: cursor ? '20.00' : '10.50', currency: 'SEK' },
				amount_basis: 'selected_accounts',
				matched_account_ids: [accountId],
				counter_account_name: 'Synthetic Counterparty'
			}
		],
		sort: url.searchParams.get('sort') ?? 'date_desc',
		page_size: Number.isFinite(pageSize) ? pageSize : 50,
		returned_count: 1,
		has_more: !cursor,
		has_previous: Boolean(cursor),
		next_cursor: cursor ? null : 'cursor-next',
		previous_cursor: cursor ? 'cursor-prev' : null,
		scan: { candidate_rows: 2, split_rows: 2, query_count: 1, scan_limited: false, exhausted: Boolean(cursor) },
		limitations: []
	};
}

function transactionDetailPayload(id) {
	return {
		id,
		date: id === 'tx-explorer-2' ? '2026-07-12' : '2026-07-11',
		description: id === 'tx-explorer-2' ? 'Synthetic second explorer transaction' : 'Synthetic explorer transaction',
		currency: 'SEK',
		splits: [
			{ account_id: accountId, account_name: 'Synthetic Checking', memo: 'Explorer smoke debit', reconcile_state: 'n', amount: '-10.50', currency: 'SEK' },
			{ account_id: secondAccountId, account_name: 'Synthetic Expenses', memo: 'Explorer smoke credit', reconcile_state: 'n', amount: '10.50', currency: 'SEK' }
		]
	};
}

function isForbiddenApiMutation(method) {
	return !['GET', 'HEAD'].includes(method.toUpperCase());
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	const server = createServer((req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });

		if (isForbiddenApiMutation(req.method ?? 'GET')) {
			forbiddenRequests.push({ method: req.method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, { detail: 'Synthetic explorer smoke blocked a mutation-capable endpoint.' });
		}
		if (url.pathname === '/health') return jsonResponse(res, 200, { status: 'ok', first_run: null });
		if (url.pathname === '/books') return jsonResponse(res, 200, [syntheticBook]);
		if (url.pathname === '/books/1/accounts') return jsonResponse(res, 200, accounts);
		if (url.pathname === '/books/1/transactions/explorer') return jsonResponse(res, 200, explorerPayload(url));
		const detailMatch = url.pathname.match(/^\/books\/1\/transactions\/(.+)$/);
		if (detailMatch) return jsonResponse(res, 200, transactionDetailPayload(decodeURIComponent(detailMatch[1])));
		return jsonResponse(res, 404, { detail: 'Synthetic explorer smoke endpoint not found.' });
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

function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

async function removeProfileDir(profileDir) {
	for (let attempt = 1; attempt <= 5; attempt += 1) {
		try {
			rmSync(profileDir, { recursive: true, force: true });
			return;
		} catch (error) {
			if (!['ENOTEMPTY', 'EBUSY', 'EPERM'].includes(error?.code) || attempt === 5) throw error;
			await sleep(attempt * 250);
		}
	}
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

async function navigate(cdp, webBase, path, label, readyPath = '/transactions') {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 20000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([
		load,
		waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(readyPath)}`, label, 20000)
	]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(readyPath)}`, label, 20000);
}

function explorerRequests(api) {
	return api.requests.filter((request) => request.path === '/books/1/transactions/explorer');
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

async function assertBoundedDateRangeRequiredState(cdp, api, browserRequests, expectedExplorerRequests, label, locale = 'en') {
	const state = await evaluate(cdp, `(() => {
		const form = document.querySelector('form[action="/transactions"][method="GET"]');
		const resetHref = Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href === '/transactions?sort=date_desc&page_size=50') ?? '';
		return {
			bodyText: document.body?.innerText ?? '',
			dateFromValue: document.querySelector('#tx-date-from')?.value ?? null,
			dateToValue: document.querySelector('#tx-date-to')?.value ?? null,
			pageSizeValue: document.querySelector('#tx-page-size')?.value ?? null,
			resetHref,
			formControls: form?.querySelectorAll('input, select, button, a').length ?? 0
		};
	})()`);
	if (locale === 'ru') {
		assert.match(state.bodyText, /Выберите ограниченный диапазон дат/, `${label}: RU bounded-date message must be rendered`);
		assert.match(state.bodyText, /Задайте date_from и date_to/, `${label}: RU bounded-date help must be rendered`);
	} else {
		assert.match(state.bodyText, /Choose a bounded date range/, `${label}: EN bounded-date message must be rendered`);
		assert.match(state.bodyText, /Set both date_from and date_to/, `${label}: EN bounded-date help must be rendered`);
	}
	assert.equal(state.dateFromValue, '', `${label}: no hidden date_from may be invented`);
	assert.equal(state.dateToValue, '', `${label}: no hidden date_to may be invented`);
	assert.equal(state.pageSizeValue, '50', `${label}: canonical reset/default must preserve page_size=50`);
	assert.equal(state.resetHref, '/transactions?sort=date_desc&page_size=50', `${label}: reset link must stay canonical no-date state`);
	assert.ok(state.formControls >= 8, `${label}: bounded-date state must preserve explorer controls`);
	assert.equal(explorerRequests(api).length, expectedExplorerRequests, `${label}: no-date route must issue zero new explorer requests`);
	assertNoMutationRequestsObserved(api, browserRequests, label);
	return state;
}

async function assertNoMobileOverflowAndAccessibleExplorer(cdp, label) {
	const state = await evaluate(cdp, `(() => {
		const root = document.documentElement;
		const body = document.body;
		const viewportWidth = window.innerWidth;
		const scrollWidth = Math.max(root?.scrollWidth ?? 0, body?.scrollWidth ?? 0);
		const form = document.querySelector('form[action="/transactions"][method="GET"]');
		const submit = form?.querySelector('button[type="submit"]');
		submit?.focus();
		const targetRects = Array.from(form?.querySelectorAll('a, button, select, input') ?? [])
			.map((el) => el.getBoundingClientRect())
			.filter((rect) => rect.width > 0 && rect.height > 0);
		return {
			viewportWidth,
			scrollWidth,
			fieldsets: form?.querySelectorAll('fieldset').length ?? 0,
			labels: form?.querySelectorAll('label[for]').length ?? 0,
			describedControls: ['#tx-state', '#tx-account-ids', '#tx-direction'].every((selector) => Boolean(document.querySelector(selector)?.getAttribute('aria-describedby'))),
			submitFocused: document.activeElement === submit,
			shortTargets: targetRects.filter((rect) => rect.height < 40).length,
			bodyText: body?.innerText ?? ''
		};
	})()`);
	assert.equal(state.viewportWidth, 320, `${label}: browser evidence must run at a 320px viewport`);
	assert.ok(state.scrollWidth <= state.viewportWidth + 8, `${label}: 320px viewport must not have obvious horizontal overflow (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.ok(state.fieldsets >= 3, `${label}: explorer form must use fieldset/legend groups`);
	assert.ok(state.labels >= 8, `${label}: explorer form controls must have explicit labels`);
	assert.ok(state.describedControls, `${label}: explorer help text must be associated with controlled fields`);
	assert.ok(state.submitFocused, `${label}: explorer submit control must be keyboard-focusable`);
	assert.equal(state.shortTargets, 0, `${label}: explorer form controls must expose at least 40px rendered touch height`);
	assert.match(state.bodyText, /Transaction Explorer|Обзор транзакций|Transactions|Транзакции|Просмотр транзакций/i, `${label}: transactions page title must be visible at 320px`);
	return state;
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the transactions explorer browser smoke');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	mkdirSync(smokeTempRoot, { recursive: true });
	const profileDir = mkdtempSync(join(smokeTempRoot, 'transactions-explorer-browser-'));
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
				JWT_SECRET: 'dummy-transactions-explorer-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-transactions-explorer-browser-smoke-password'
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
			'--window-size=320,820',
			'about:blank'
		], {
			cwd: root,
			env: { ...process.env, TMPDIR: smokeTempRoot, TMP: smokeTempRoot, TEMP: smokeTempRoot }
		});

		cdp = await connectCdp(debugPort);
		cdp.on('Network.requestWillBeSent', (params) => {
			browserRequests.push({ method: params.request.method, url: params.request.url });
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 820, deviceScaleFactor: 2, mobile: true });
		await cdp.send('Network.setCookie', { name: 'access_token', value: syntheticToken, url: webBase, path: '/', sameSite: 'Lax' });
		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });

		await navigate(cdp, webBase, '/transactions', 'default bounded date required');
		await waitForExpression(cdp, `document.body.innerText.includes('Choose a bounded date range')`, 'default bounded date body', 20000);
		await assertBoundedDateRangeRequiredState(cdp, api, browserRequests, 0, 'default /transactions bounded-date state', 'en');
		const noDateMobileState = await assertNoMobileOverflowAndAccessibleExplorer(cdp, 'default /transactions bounded-date state');

		await navigate(cdp, webBase, '/transactions?sort=date_desc&page_size=50', 'canonical reset bounded date required');
		await waitForExpression(cdp, `document.body.innerText.includes('Choose a bounded date range')`, 'canonical reset bounded date body', 20000);
		await assertBoundedDateRangeRequiredState(cdp, api, browserRequests, 0, 'canonical reset bounded-date state', 'en');

		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'ru', url: webBase, path: '/', sameSite: 'Lax' });
		await navigate(cdp, webBase, '/transactions?sort=date_desc&page_size=50', 'canonical reset bounded date required ru');
		await waitForExpression(cdp, `document.body.innerText.includes('Выберите ограниченный диапазон дат')`, 'canonical reset bounded date body ru', 20000);
		await assertBoundedDateRangeRequiredState(cdp, api, browserRequests, 0, 'canonical reset bounded-date RU state', 'ru');
		await assertNoMobileOverflowAndAccessibleExplorer(cdp, 'canonical reset bounded-date RU state');
		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });

		const initialPath = `/transactions?date_from=2026-07-01&date_to=2026-07-31&account_ids=${accountId}&sort=date_desc&page_size=2`;
		await navigate(cdp, webBase, initialPath, 'initial explorer');
		await waitForExpression(cdp, `document.body.innerText.includes('Synthetic explorer transaction') && document.querySelector('#tx-page-size')?.value === '2'`, 'initial explorer body', 20000);
		const mobileState = await assertNoMobileOverflowAndAccessibleExplorer(cdp, 'transactions explorer browser smoke');
		let lastExplorer = explorerRequests(api).at(-1);
		assert.ok(lastExplorer, 'initial SSR load must call /transactions/explorer');
		let lastParams = new URLSearchParams(lastExplorer.search);
		assert.equal(lastParams.get('account_ids'), accountId, 'initial explorer API request must preserve canonical account_ids');
		assert.equal(lastParams.get('date_from'), '2026-07-01', 'initial explorer API request must preserve date_from');
		assert.equal(lastParams.get('page_size'), '2', 'initial explorer API request must preserve page_size');
		assert.equal(lastParams.get('offset'), null, 'explorer API request must not use legacy offset pagination');

		const firstState = await evaluate(cdp, `(() => {
			const detail = Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href?.startsWith('/transactions/tx-explorer-1?return_to='));
			return {
				location: location.pathname + location.search,
				detail,
				next: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href?.includes('cursor=cursor-next')),
				bodyText: document.body.innerText
			};
		})()`);
		assert.ok(firstState.detail, 'transaction rows must link to details with return_to');
		assert.match(firstState.detail, /return_to=%2Ftransactions%3F/, 'detail href must encode the canonical explorer return URL');
		assert.ok(firstState.next, 'cursor pagination must expose a next link from next_cursor');
		assert.match(firstState.bodyText, /Returned 1 row\(s\) on this cursor page; requested page_size=2\./, 'explorer status must reflect returned_count and page_size');

		await navigate(cdp, webBase, firstState.next, 'cursor next');
		await waitForExpression(cdp, `location.search.includes('cursor=cursor-next') && document.body.innerText.includes('20.00')`, 'cursor next body', 20000);
		lastExplorer = explorerRequests(api).at(-1);
		lastParams = new URLSearchParams(lastExplorer.search);
		assert.equal(lastParams.get('cursor'), 'cursor-next', 'cursor next URL must map to explorer API cursor');
		assert.equal(lastParams.get('page_size'), '2', 'cursor next must preserve page_size');

		await evaluate(cdp, `(() => {
			const input = document.querySelector('#tx-query');
			input.value = 'coffee';
			input.dispatchEvent(new Event('input', { bubbles: true }));
			document.querySelector('form[action="/transactions"]').requestSubmit();
		})()`);
		await waitForExpression(cdp, `location.pathname === '/transactions' && location.search.includes('query=coffee') && !location.search.includes('cursor=')`, 'submitted explorer query', 20000);
		lastExplorer = explorerRequests(api).at(-1);
		lastParams = new URLSearchParams(lastExplorer.search);
		assert.equal(lastParams.get('query'), 'coffee', 'GET form submission must synchronize query URL state to explorer API');
		assert.equal(lastParams.get('cursor'), null, 'filter form submission must reset cursor pagination');

		const detailHref = await evaluate(cdp, `Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href?.startsWith('/transactions/tx-explorer-1?return_to='))`);
		assert.ok(detailHref, 'filtered explorer result must still link to detail with return_to');
		await navigate(cdp, webBase, detailHref, 'transaction detail', '/transactions/tx-explorer-1');
		await waitForExpression(cdp, `document.body.innerText.includes('Read-only view of the selected GnuCash transaction') && document.querySelector('a[href^="/transactions?"]')`, 'transaction detail body', 20000);
		const backHref = await evaluate(cdp, `document.querySelector('a[href^="/transactions?"]')?.getAttribute('href')`);
		assert.ok(backHref.includes('query=coffee'), 'transaction detail back link must preserve filtered explorer query');
		assert.ok(backHref.includes(`account_ids=${accountId}`), 'transaction detail back link must preserve selected account');
		await navigate(cdp, webBase, backHref, 'return from detail');
		await waitForExpression(cdp, `location.pathname === '/transactions' && location.search.includes('query=coffee') && document.body.innerText.includes('Synthetic coffee explorer transaction')`, 'returned explorer context', 20000);

		const resetHref = await evaluate(cdp, `Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href === '/transactions?sort=date_desc&page_size=50')`);
		assert.equal(resetHref, '/transactions?sort=date_desc&page_size=50', 'returned explorer context must expose the canonical Reset explorer link');
		const beforeResetExplorerRequestCount = explorerRequests(api).length;
		await navigate(cdp, webBase, resetHref, 'follow reset to bounded date required');
		await waitForExpression(cdp, `location.search === '?sort=date_desc&page_size=50' && document.body.innerText.includes('Choose a bounded date range')`, 'reset bounded date body', 20000);
		await assertBoundedDateRangeRequiredState(cdp, api, browserRequests, beforeResetExplorerRequestCount, 'followed Reset bounded-date state', 'en');

		const beforePairedRangeExplorerRequestCount = explorerRequests(api).length;
		await evaluate(cdp, `(() => {
			document.querySelector('#tx-date-from').value = '2026-07-01';
			document.querySelector('#tx-date-to').value = '2026-07-31';
			document.querySelector('form[action="/transactions"]').requestSubmit();
		})()`);
		await waitForExpression(cdp, `location.search.includes('date_from=2026-07-01') && location.search.includes('date_to=2026-07-31') && document.body.innerText.includes('Synthetic explorer transaction')`, 'paired date range explorer body', 20000);
		lastExplorer = explorerRequests(api).at(-1);
		lastParams = new URLSearchParams(lastExplorer.search);
		assert.equal(explorerRequests(api).length, beforePairedRangeExplorerRequestCount + 1, 'selecting a paired date range from reset state must issue exactly one explorer request');
		assert.equal(lastParams.get('date_from'), '2026-07-01', 'paired date range request must include date_from');
		assert.equal(lastParams.get('date_to'), '2026-07-31', 'paired date range request must include date_to');
		assert.equal(lastParams.get('page_size'), '50', 'paired date range request must preserve canonical page_size');

		assertNoMutationRequestsObserved(api, browserRequests, 'transactions explorer browser smoke');
		console.log(`transactions explorer browser smoke passed: explorer_requests=${explorerRequests(api).length} no_date_explorer_requests=0 api_forbidden=${api.forbiddenRequests.length} browser_forbidden=${forbiddenBrowserMutationRequests(browserRequests).length} mobile_width=${noDateMobileState.viewportWidth}/${mobileState.viewportWidth} scroll_width=${noDateMobileState.scrollWidth}/${mobileState.scrollWidth}`);
	} catch (error) {
		const webTail = webProcess?.outputTail?.() ?? '';
		const chromiumTail = chromiumProcess?.outputTail?.() ?? '';
		throw new Error(`${error.message}\n--- vite preview tail ---\n${webTail}\n--- chromium tail ---\n${chromiumTail}`);
	} finally {
		cdp?.close();
		await stopProcess(chromiumProcess);
		await stopProcess(webProcess);
		await api.close();
		await removeProfileDir(profileDir);
	}
}

await runSmoke();
