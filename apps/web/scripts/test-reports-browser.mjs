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
const previewServerIndex = join(root, '.svelte-kit', 'output', 'server', 'index.js');
const smokeHome = process.env.REPORTS_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.REPORTS_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-rpt');
const syntheticToken = 'synthetic-reports-smoke-token';
const privateReportSentinel = 'PRIVATE_REPORT_SENTINEL_4F1B2C_ACCOUNT_PATH_GUID';
const cdpCommandTimeoutMs = Number(process.env.REPORTS_CDP_TIMEOUT_MS ?? '90000');

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
	name: 'Synthetic Reports Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for reports browser smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic reports fixture.',
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
		message: 'Synthetic local reports smoke fixture; no private book is used.'
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

function summaryPayload(dateTo, side = 'primary', mode = 'full') {
	const currency = mode === 'not_comparable' && side === 'primary' ? 'XXX' : 'SEK';
	if (mode === 'empty') {
		return {
			currency,
			net_worth: '0.00',
			assets: '0.00',
			liabilities: '0.00',
			as_of_date: dateTo,
			reporting_basis: 'base_currency_only',
			includes_currency_conversion: false,
			limitations: []
		};
	}
	return {
		currency,
		net_worth: side === 'primary' ? '1450.00' : '1250.00',
		assets: side === 'primary' ? '2000.00' : '1800.00',
		liabilities: side === 'primary' ? '-550.00' : '-550.00',
		as_of_date: dateTo,
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: ['base_currency_only: No FX conversion; synthetic fixture excludes non-base currencies.']
	};
}

function cashflowPayload(dateFrom, dateTo, side = 'primary', mode = 'full') {
	const currency = mode === 'not_comparable' && side === 'primary' ? 'XXX' : 'SEK';
	if (mode === 'empty') {
		return { date_from: dateFrom, date_to: dateTo, currency, inflow: '0.00', outflow: '0.00', net: '0.00' };
	}
	return side === 'primary'
		? { date_from: dateFrom, date_to: dateTo, currency, inflow: '125.00', outflow: '45.67', net: '79.33' }
		: { date_from: dateFrom, date_to: dateTo, currency, inflow: '100.00', outflow: '60.00', net: '40.00' };
}

function monthlyPayload(side = 'primary', mode = 'full') {
	if (mode === 'empty' || mode === 'partial') return [];
	return side === 'primary'
		? [{ month: '2026-07', inflow: '125.00', outflow: '45.67', net: '79.33' }]
		: [{ month: '2026-06', inflow: '100.00', outflow: '60.00', net: '40.00' }];
}

function expensesPayload(side = 'primary', mode = 'full') {
	if (mode === 'empty' || mode === 'not_comparable') return [];
	return side === 'primary'
		? [
				{ account_id: 'expense-food', account_name: 'Synthetic Food', total: '45.67', currency: 'SEK' },
				{ account_id: 'expense-rent', account_name: 'Synthetic Rent', total: '0.00', currency: 'SEK' },
				{ account_id: 'expense-refund', account_name: 'Synthetic Refund', total: '-10.00', currency: 'SEK' }
			]
		: [
				{ account_id: 'expense-food', account_name: 'Synthetic Food', total: '45.67', currency: 'SEK' },
				{ account_id: 'expense-rent', account_name: 'Synthetic Rent', total: '100.00', currency: 'SEK' },
				{ account_id: 'expense-refund', account_name: 'Synthetic Refund', total: '5.00', currency: 'SEK' }
			];
}

function sectionStatuses(mode = 'full') {
	if (mode === 'empty') {
		return [
			{ section: 'summary', status: 'empty', detail: null },
			{ section: 'cashflow', status: 'empty', detail: null },
			{ section: 'monthly_cashflow', status: 'empty', detail: null },
			{ section: 'expenses_by_account', status: 'empty', detail: null }
		];
	}
	return [
		{ section: 'summary', status: 'ok', detail: null },
		{ section: 'cashflow', status: mode === 'partial' ? 'error' : 'ok', detail: mode === 'partial' ? privateReportSentinel : null },
		{ section: 'monthly_cashflow', status: mode === 'partial' ? 'error' : 'ok', detail: mode === 'partial' ? privateReportSentinel : null },
		{ section: 'expenses_by_account', status: 'ok', detail: null }
	];
}

function periodReportPayload(dateFrom, dateTo, side = 'primary', mode = 'full') {
	return {
		book_id: 1,
		date_from: dateFrom,
		date_to: dateTo,
		currency: mode === 'not_comparable' && side === 'primary' ? 'XXX' : 'SEK',
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: ['base_currency_only: No FX conversion; synthetic fixture excludes non-base currencies.'],
		partial_failure: mode === 'partial',
		empty: mode === 'empty',
		section_statuses: sectionStatuses(mode),
		summary: summaryPayload(dateTo, side, mode),
		cashflow: cashflowPayload(dateFrom, dateTo, side, mode),
		monthly_cashflow: monthlyPayload(side, mode),
		expenses_by_account: expensesPayload(side, mode)
	};
}

function moneyDelta(primary, comparison, delta, absoluteDelta, currency = 'SEK') {
	return { primary, comparison, delta, absolute_delta: absoluteDelta, currency };
}

function comparisonReportPayload(params, mode = 'full') {
	const comparable = mode !== 'not_comparable';
	const partial = mode === 'partial';
	const empty = mode === 'empty';
	const deltaStatus = mode === 'not_comparable' ? 'not_comparable' : empty ? 'empty' : 'ok';
	return {
		book_id: 1,
		comparison_mode: params.comparison_mode,
		primary: periodReportPayload(params.date_from, params.date_to, 'primary', mode),
		comparison: periodReportPayload(params.comparison_date_from, params.comparison_date_to, 'comparison', mode),
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations:
			mode === 'not_comparable'
				? ['currency_mismatch: XXX vs SEK; no FX conversion configured.']
				: ['base_currency_only: No FX conversion; synthetic comparison fixture excludes non-base currencies.'],
		partial_failure: partial,
		empty,
		comparable,
		delta_section_statuses: [
			{ section: 'summary', status: deltaStatus, detail: null },
			{ section: 'cashflow', status: partial ? 'error' : deltaStatus, detail: partial ? privateReportSentinel : null },
			{ section: 'expenses_by_account', status: deltaStatus, detail: null }
		],
		summary_delta:
			comparable && !empty
				? {
						currency: 'SEK',
						assets: moneyDelta('2000.00', '1800.00', '200.00', '200.00'),
						liabilities: moneyDelta('-550.00', '-550.00', '0.00', '0.00'),
						net_worth: moneyDelta('1450.00', '1250.00', '200.00', '200.00')
					}
				: null,
		cashflow_delta:
			comparable && !empty && !partial
				? {
						currency: 'SEK',
						inflow: moneyDelta('125.00', '100.00', '25.00', '25.00'),
						outflow: moneyDelta('45.67', '60.00', '-14.33', '14.33'),
						net: moneyDelta('79.33', '40.00', '39.33', '39.33')
					}
				: null,
		expense_changes:
			comparable && !empty
				? [
						{
							account_id: 'expense-rent',
							account_name: 'Synthetic Rent',
							primary_total: '0.00',
							comparison_total: '100.00',
							delta: '-100.00',
							absolute_delta: '100.00',
							currency: 'SEK'
						},
						{
							account_id: 'expense-refund',
							account_name: 'Synthetic Refund',
							primary_total: '-10.00',
							comparison_total: '5.00',
							delta: '-15.00',
							absolute_delta: '15.00',
							currency: 'SEK'
						},
						{
							account_id: 'expense-food',
							account_name: 'Synthetic Food',
							primary_total: '45.67',
							comparison_total: '45.67',
							delta: '0.00',
							absolute_delta: '0.00',
							currency: 'SEK'
						},
						{
							account_id: 'expense-dining',
							account_name: 'Synthetic Dining',
							primary_total: '80.00',
							comparison_total: '75.00',
							delta: null,
							absolute_delta: null,
							currency: 'SEK',
							status: 'not_comparable',
							detail: privateReportSentinel
						}
					]
				: []
	};
}

function reportMode(dateFrom, dateTo) {
	if (dateFrom === '2026-08-01' || dateTo === '2026-08-31') return 'empty';
	if (dateFrom === '2026-07-10') return 'partial';
	if (dateFrom === '2026-09-01' || dateTo === '2026-09-30') return 'error';
	if (dateFrom === '2026-10-01') return 'not_comparable';
	return 'full';
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
	const server = createServer((req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });

		if (isForbiddenApiMutation(req.method ?? 'GET', url.pathname, url.search)) {
			forbiddenRequests.push({ method: req.method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, { detail: 'Synthetic reports smoke blocked a mutation-capable endpoint.' });
		}
		if (req.method === 'GET' && url.pathname === '/health') {
			return jsonResponse(res, 200, { status: 'ok', first_run: null });
		}
		if (req.method === 'GET' && url.pathname === '/books') {
			return jsonResponse(res, 200, [syntheticBook]);
		}

		if (url.pathname !== '/books/1/reports/comparison' || req.method !== 'GET') {
			return jsonResponse(res, 404, { detail: 'Synthetic reports comparison smoke endpoint not found.' });
		}

		const params = {
			date_from: url.searchParams.get('date_from') ?? '',
			date_to: url.searchParams.get('date_to') ?? '',
			comparison_mode: url.searchParams.get('comparison_mode') ?? '',
			comparison_date_from: url.searchParams.get('comparison_date_from') ?? '',
			comparison_date_to: url.searchParams.get('comparison_date_to') ?? ''
		};
		const mode = reportMode(params.date_from, params.date_to);

		if (mode === 'error') {
			return jsonResponse(res, 500, { detail: privateReportSentinel });
		}
		return jsonResponse(res, 200, comparisonReportPayload(params, mode));
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

async function navigateReports(cdp, webBase, path, label, readyText = 'Period reports explorer') {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 20000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([
		load,
		waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === '/reports' && document.body?.innerText.includes(${jsString(readyText)})`, label, 20000)
	]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === '/reports' && document.body?.innerText.includes(${jsString(readyText)})`, label, 20000);
}

function reportRequests(api) {
	return api.requests.filter((request) => request.path === '/books/1/reports/comparison');
}

function lastReportRequest(api) {
	const requests = reportRequests(api);
	assert.ok(requests.length > 0, 'at least one reports comparison request must be observed');
	return requests.at(-1);
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

async function assertNoMobileOverflowAndActiveReportsNav(cdp, label) {
	await cdp.send('Emulation.setDeviceMetricsOverride', {
		width: 320,
		height: 760,
		deviceScaleFactor: 2,
		mobile: true
	});
	const state = await evaluate(cdp, `(() => ({
		viewportWidth: document.documentElement.clientWidth,
		scrollWidth: document.documentElement.scrollWidth,
		activeReportsLinks: Array.from(document.querySelectorAll('a[href="/reports"][aria-current="page"][data-active-route="true"]')).length,
		fieldsets: document.querySelectorAll('fieldset legend').length,
		bodyText: document.body?.innerText ?? ''
	}))()`);
	assert.ok(state.scrollWidth <= state.viewportWidth + 8, `${label}: 320px viewport must not have obvious horizontal overflow (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.ok(state.activeReportsLinks >= 1, `${label}: Reports navigation must expose active aria-current route state`);
	assert.ok(state.fieldsets >= 2, `${label}: primary and comparison controls must use fieldset/legend semantics`);
	assert.match(state.bodyText, /Period reports explorer|Просмотр отчётов за период/, `${label}: reports page title must be visible at 320px`);
}

function assertHrefParams(href, expectedPath, expectedParams, label) {
	const url = new URL(href, 'http://127.0.0.1');
	assert.equal(url.pathname, expectedPath, `${label}: path`);
	for (const [key, value] of Object.entries(expectedParams)) {
		assert.equal(url.searchParams.get(key), value, `${label}: ${key}`);
	}
}

function assertRequestParams(request, expectedParams, label) {
	const url = new URL(`${request.path}${request.search}`, 'http://127.0.0.1');
	for (const [key, value] of Object.entries(expectedParams)) {
		assert.equal(url.searchParams.get(key), value, `${label}: ${key}`);
	}
}

async function assertFullComparisonPage(cdp) {
	const state = await evaluate(cdp, `(() => {
		const linkRows = Array.from(document.querySelectorAll('a')).map((link) => ({ text: link.textContent.replace(/\\s+/g, ' ').trim(), href: link.href }));
		const bodyText = document.body?.innerText ?? '';
		return {
			pathname: location.pathname,
			search: location.search,
			dateFrom: document.querySelector('input[name="date_from"]')?.value ?? '',
			dateTo: document.querySelector('input[name="date_to"]')?.value ?? '',
			comparisonDateFrom: document.querySelector('input[name="comparison_date_from"]')?.value ?? '',
			comparisonDateTo: document.querySelector('input[name="comparison_date_to"]')?.value ?? '',
			bodyText,
			html: document.documentElement.outerHTML,
			periodHref: linkRows.find((link) => link.text.includes('View /transactions for this period'))?.href ?? '',
			primaryExpenseHref: linkRows.find((link) => link.text.includes('Primary period: 0.00'))?.href ?? '',
			comparisonExpenseHref: linkRows.find((link) => link.text.includes('Comparison period: 100.00'))?.href ?? '',
			primaryNotComparableHref: linkRows.find((link) => link.text.includes('Primary period: 80.00'))?.href ?? '',
			comparisonNotComparableHref: linkRows.find((link) => link.text.includes('Comparison period: 75.00'))?.href ?? '',
			rowOrder: Array.from(document.querySelectorAll('section[aria-labelledby="reports-expense-changes-title"] li')).map((row) => row.textContent.replace(/\\s+/g, ' ').trim()),
			presetHrefs: linkRows.filter((link) => /This month|Last month|Year to date/.test(link.text)).map((link) => link.href),
			comparisonModeHrefs: linkRows.filter((link) => /Previous equivalent|Same period last year/.test(link.text)).map((link) => link.href)
		};
	})()`);
	assert.equal(state.pathname, '/reports', 'custom comparison page path must persist');
	assert.match(state.search, /comparison_mode=custom/, 'comparison mode must remain in URL');
	assert.equal(state.dateFrom, '2026-07-01', 'custom date_from input must persist selected value');
	assert.equal(state.dateTo, '2026-07-31', 'custom date_to input must persist selected value');
	assert.equal(state.comparisonDateFrom, '2026-06-01', 'comparison date_from input must persist selected value');
	assert.equal(state.comparisonDateTo, '2026-06-30', 'comparison date_to input must persist selected value');
	assert.match(state.bodyText, /No FX conversion/, 'base-currency/no-FX limitation must render');
	assert.match(state.bodyText, /Backend limitation:/, 'raw limitations must be visibly technical backend limitation text');
	assert.match(state.bodyText, /Exact 0\.00 values are genuine data/, 'zero-vs-missing safety copy must render');
	assert.match(state.bodyText, /Primary and comparison totals/, 'source period cards must render');
	assert.match(state.bodyText, /Balance change/, 'summary delta section must render');
	assert.match(state.bodyText, /Cashflow change/, 'cashflow delta section must render');
	assert.match(state.bodyText, /Spending changes by account/, 'expense change section must render');
	assert.match(state.bodyText, /Unchanged/, 'zero delta must be labeled unchanged');
	assert.match(state.bodyText, /Synthetic Rent[\s\S]*0\.00[\s\S]*100\.00/, 'one-sided successful zero expense row must stay visible');
	assert.match(state.bodyText, /Synthetic Refund[\s\S]*-10\.00[\s\S]*5\.00/, 'negative expense totals must stay visible and signed');
	assert.match(state.bodyText, /Synthetic Dining[\s\S]*80\.00[\s\S]*75\.00/, 'row-local not_comparable expense row must preserve side totals');
	assert.match(state.bodyText, /This account row is not comparable/, 'row-local not_comparable expense row must render fixed redacted copy');
	assert.doesNotMatch(state.html, new RegExp(privateReportSentinel), 'row-local backend detail must not be serialized into the browser HTML');
	assert.ok(state.rowOrder[0]?.includes('Synthetic Rent'), 'backend-ranked expense rows must be preserved: largest absolute delta first');
	assert.ok(state.rowOrder[1]?.includes('Synthetic Refund'), 'backend-ranked expense rows must preserve second row');
	assert.ok(state.rowOrder[2]?.includes('Synthetic Food'), 'backend-ranked expense rows must preserve unchanged zero row');
	assert.ok(state.rowOrder[3]?.includes('Synthetic Dining'), 'backend-ranked expense rows must preserve row-local not_comparable row after comparable rows');
	for (const href of state.presetHrefs) {
		const url = new URL(href);
		assert.equal(url.pathname, '/reports', 'preset link path');
		for (const key of ['preset', 'date_from', 'date_to', 'comparison_mode', 'comparison_date_from', 'comparison_date_to']) {
			assert.ok(url.searchParams.get(key), `preset link keeps ${key} query`);
		}
	}
	for (const href of state.comparisonModeHrefs) {
		const url = new URL(href);
		assert.equal(url.pathname, '/reports', 'comparison mode link path');
		for (const key of ['preset', 'date_from', 'date_to', 'comparison_mode', 'comparison_date_from', 'comparison_date_to']) {
			assert.ok(url.searchParams.get(key), `comparison link keeps ${key} query`);
		}
	}
	for (const href of [state.periodHref]) {
		assertHrefParams(href, '/transactions', { limit: '50', offset: '0', date_from: '2026-07-01', date_to: '2026-07-31' }, 'primary period transaction drilldown');
	}
	assertHrefParams(state.primaryExpenseHref, '/transactions', { limit: '50', offset: '0', account_id: 'expense-rent', date_from: '2026-07-01', date_to: '2026-07-31' }, 'primary expense drilldown');
	assertHrefParams(state.comparisonExpenseHref, '/transactions', { limit: '50', offset: '0', account_id: 'expense-rent', date_from: '2026-06-01', date_to: '2026-06-30' }, 'comparison expense drilldown');
	assertHrefParams(state.primaryNotComparableHref, '/transactions', { limit: '50', offset: '0', account_id: 'expense-dining', date_from: '2026-07-01', date_to: '2026-07-31' }, 'row-local not_comparable primary expense drilldown');
	assertHrefParams(state.comparisonNotComparableHref, '/transactions', { limit: '50', offset: '0', account_id: 'expense-dining', date_from: '2026-06-01', date_to: '2026-06-30' }, 'row-local not_comparable comparison expense drilldown');
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the reports browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before reports browser smoke; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	mkdirSync(smokeTempRoot, { recursive: true });
	const profileDir = mkdtempSync(join(smokeTempRoot, 'reports-browser-'));
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
				JWT_SECRET: 'dummy-reports-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-reports-browser-smoke-password'
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

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-07-01&date_to=2026-07-31&comparison_mode=custom&comparison_date_from=2026-06-01&comparison_date_to=2026-06-30',
			'full reports comparison page'
		);
		await assertNoMobileOverflowAndActiveReportsNav(cdp, 'full reports comparison page');
		await assertFullComparisonPage(cdp);
		assert.equal(reportRequests(api).length, 1, 'full reports page must call exactly one combined read-only comparison endpoint');
		assertRequestParams(lastReportRequest(api), {
			date_from: '2026-07-01',
			date_to: '2026-07-31',
			comparison_mode: 'custom',
			comparison_date_from: '2026-06-01',
			comparison_date_to: '2026-06-30'
		}, 'custom comparison request');
		assertNoMutationRequestsObserved(api, browserRequests, 'full reports comparison page');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-07-02&date_to=2026-12-30&comparison_mode=previous_equivalent&comparison_date_from=2026-01-01&comparison_date_to=2026-07-01',
			'previous equivalent reports comparison page'
		);
		assertRequestParams(lastReportRequest(api), {
			date_from: '2026-07-02',
			date_to: '2026-12-30',
			comparison_mode: 'previous_equivalent',
			comparison_date_from: '2026-01-01',
			comparison_date_to: '2026-07-01'
		}, 'previous-equivalent inclusive request');
		assertNoMutationRequestsObserved(api, browserRequests, 'previous equivalent reports comparison page');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2024-02-01&date_to=2024-02-29&comparison_mode=same_period_last_year&comparison_date_from=2023-02-01&comparison_date_to=2023-02-28',
			'prior year leap-clamp comparison page'
		);
		assertRequestParams(lastReportRequest(api), {
			date_from: '2024-02-01',
			date_to: '2024-02-29',
			comparison_mode: 'same_period_last_year',
			comparison_date_from: '2023-02-01',
			comparison_date_to: '2023-02-28'
		}, 'prior-year leap-clamp request');
		assertNoMutationRequestsObserved(api, browserRequests, 'prior year leap-clamp comparison page');

		const reportCountBeforeInvalid = reportRequests(api).length;
		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-07-01&date_to=2026-07-31&comparison_mode=custom&comparison_date_from=2026-07-31&comparison_date_to=2026-07-01',
			'invalid custom comparison range',
			'Invalid range'
		);
		const invalidText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		assert.match(invalidText, /No reports API request was made for this invalid range/, 'invalid comparison range must explicitly skip reports API calls');
		assert.equal(reportRequests(api).length, reportCountBeforeInvalid, 'invalid comparison range must not add report endpoint requests');
		assertNoMutationRequestsObserved(api, browserRequests, 'invalid custom comparison range');

		const reportCountBeforeInconsistent = reportRequests(api).length;
		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-07-02&date_to=2026-12-30&comparison_mode=previous_equivalent&comparison_date_from=2026-01-02&comparison_date_to=2026-07-01',
			'inconsistent derived comparison range',
			'Invalid range'
		);
		const inconsistentText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		assert.match(inconsistentText, /comparison_date_from=2026-01-01 and comparison_date_to=2026-07-01/, 'inconsistent derived comparison dates must show canonical required dates');
		assert.equal(reportRequests(api).length, reportCountBeforeInconsistent, 'inconsistent derived comparison range must not add report endpoint requests');
		assertNoMutationRequestsObserved(api, browserRequests, 'inconsistent derived comparison range');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-08-01&date_to=2026-08-31&comparison_mode=custom&comparison_date_from=2026-07-01&comparison_date_to=2026-07-31',
			'empty reports comparison page',
			'No report data'
		);
		const emptyText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		assert.match(emptyText, /No report data/, 'empty comparison response must render the empty state');
		assert.doesNotMatch(emptyText, /Report request failed|Partial report/, 'empty state must not be confused with API or partial errors');
		assertNoMutationRequestsObserved(api, browserRequests, 'empty reports comparison page');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-07-10&date_to=2026-07-20&comparison_mode=custom&comparison_date_from=2026-06-10&comparison_date_to=2026-06-20',
			'partial reports comparison page',
			'Partial report'
		);
		const partialText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		const partialHtml = await evaluate(cdp, `document.documentElement.outerHTML`);
		assert.match(partialText, /Partial report/, 'partial source section failure must render a partial report alert');
		assert.match(partialText, /Comparison delta is unavailable/, 'partial delta section failure must render fixed redacted copy');
		assert.doesNotMatch(partialText, new RegExp(privateReportSentinel), 'partial section failure must redact backend details');
		assert.doesNotMatch(partialHtml, new RegExp(privateReportSentinel), 'partial section backend detail must not be serialized into browser HTML');
		assert.match(partialText, /Synthetic Rent/, 'unaffected expense-change section must remain visible after a partial error');
		assertNoMutationRequestsObserved(api, browserRequests, 'partial reports comparison page');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-10-01&date_to=2026-10-31&comparison_mode=custom&comparison_date_from=2026-09-01&comparison_date_to=2026-09-30',
			'not comparable reports comparison page',
			'Comparison is not comparable'
		);
		const notComparableText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		assert.match(notComparableText, /Comparison is not comparable/, 'unknown/mismatched currency must render not_comparable copy');
		assert.match(notComparableText, /Backend limitation: currency_mismatch: XXX vs SEK; no FX conversion configured\./, 'technical backend limitation text must remain visibly technical');
		assert.doesNotMatch(notComparableText, /No report data/, 'not_comparable must not masquerade as empty');
		assertNoMutationRequestsObserved(api, browserRequests, 'not comparable reports comparison page');

		await navigateReports(
			cdp,
			webBase,
			'/reports?preset=custom&date_from=2026-09-01&date_to=2026-09-30&comparison_mode=custom&comparison_date_from=2026-08-01&comparison_date_to=2026-08-31',
			'all-error reports comparison page',
			'Report request failed'
		);
		const errorText = await evaluate(cdp, `document.body?.innerText ?? ''`);
		assert.match(errorText, /Report request failed/, 'whole-request failure must render load error state');
		assert.match(errorText, /Reports API request failed safely|Reports API is unavailable/, 'whole-request failure must use fixed safe copy');
		assert.doesNotMatch(errorText, new RegExp(privateReportSentinel), 'whole-request failure must redact unknown backend detail');
		assert.doesNotMatch(errorText, /No report data/, 'whole-request failure must not be presented as an empty report');
		assertNoMutationRequestsObserved(api, browserRequests, 'all-error reports comparison page');

		console.log(`reports browser smoke passed: api_report_requests=${reportRequests(api).length} api_forbidden=${api.forbiddenRequests.length} browser_forbidden=${forbiddenBrowserMutationRequests(browserRequests).length}`);
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
