import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
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
	const reporting_currency = {
		status: 'ready',
		source: 'detected',
		reason: 'dominant_detected',
		configured_currency: null,
		configured_currency_status: 'missing',
		selected_currency: 'SEK',
		candidates: [
			{ currency: 'SEK', distinct_transaction_count: 2, nonzero_split_count: 4, active_leaf_account_count: 2, eligible_leaf_account_count: 2 },
			{ currency: 'EUR', distinct_transaction_count: 1, nonzero_split_count: 2, active_leaf_account_count: 1, eligible_leaf_account_count: 1 }
		],
		excluded_currencies: ['EUR'],
		non_currency_commodities_excluded: true
	};
	if (mode === 'empty') {
		return {
			status: 'ready',
			currency: 'SEK',
			net_worth: '0.00',
			assets: '0.00',
			liabilities: '0.00',
			income_this_month: '0.00',
			expenses_this_month: '0.00',
			as_of_date: '2026-07-31',
			reporting_basis: 'base_currency_only',
			includes_currency_conversion: false,
			limitations: [],
			reporting_currency
		};
	}
	return {
		status: 'ready',
		currency: 'SEK',
		net_worth: '1450.00',
		assets: '2000.00',
		liabilities: '550.00',
		income_this_month: '125.00',
		expenses_this_month: '45.67',
		as_of_date: '2026-07-31',
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: ['base_currency_only: No FX conversion; synthetic fixture excludes non-base currencies.'],
		reporting_currency
	};
}

function expensesPayload(mode) {
	if (mode === 'empty') return [];
	return [
		{ account_id: 'expense-housing', account_name: 'Synthetic Housing', total: '15.00', currency: 'SEK' },
		{ account_id: 'expense-food', account_name: 'Synthetic Food', total: '10.00', currency: 'SEK' },
		{ account_id: 'expense-transport', account_name: 'Synthetic Transport', total: '8.00', currency: 'SEK' },
		{ account_id: 'expense-health', account_name: 'Synthetic Health', total: '6.00', currency: 'SEK' },
		{ account_id: 'expense-utilities', account_name: 'Synthetic Utilities', total: '4.00', currency: 'SEK' },
		{ account_id: 'expense-dining', account_name: 'Synthetic Dining', total: '2.00', currency: 'SEK' },
		{ account_id: 'expense-books', account_name: 'Synthetic Books', total: '0.67', currency: 'SEK' }
	];
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
			counter_account_name: 'Synthetic Bank',
			direction: {
				status: 'resolved',
				reason: 'balanced',
				currency: 'SEK',
				from_accounts: [{ account_id: 'income-salary', display_name: 'Synthetic Income', full_name: 'Income:Synthetic Salary', value: '-125.00', split_count: 1 }],
				to_accounts: [{ account_id: 'bank-main', display_name: 'Synthetic Bank', full_name: 'Assets:Synthetic Bank', value: '125.00', split_count: 1 }]
			},
			amount_is_unambiguous: true
		},
		{
			id: 'tx-dashboard-no-representative',
			date: '2026-07-10',
			description: 'Synthetic Missing Representative',
			amount: '999.91',
			currency: 'SEK',
			account_id: 'expense-food',
			account_name: 'Synthetic Food',
			counter_account_name: 'Synthetic Bank',
			direction: {
				status: 'resolved',
				reason: 'balanced',
				currency: 'SEK',
				from_accounts: [{ account_id: 'bank-main', display_name: 'Synthetic Bank', full_name: 'Assets:Synthetic Bank', value: '-9.91', split_count: 1 }],
				to_accounts: [{ account_id: 'expense-food', display_name: 'Synthetic Food', full_name: 'Expenses:Synthetic Food', value: '9.91', split_count: 1 }]
			},
			amount_is_unambiguous: false
		},
		{
			id: 'tx-dashboard-composite',
			date: '2026-07-09',
			description: 'Synthetic Composite Purchase',
			amount: '777.72',
			currency: 'SEK',
			account_id: 'expense-food',
			account_name: 'Synthetic Food',
			counter_account_name: 'Synthetic Bank',
			direction: {
				status: 'composite',
				reason: 'multiple_accounts',
				currency: 'SEK',
				from_accounts: [{ account_id: 'bank-main', display_name: 'Synthetic Bank', full_name: 'Assets:Synthetic Bank', value: '-12.00', split_count: 1 }],
				to_accounts: [
					{ account_id: 'expense-food', display_name: 'Synthetic Food', full_name: 'Expenses:Synthetic Food', value: '8.00', split_count: 1 },
					{ account_id: 'expense-supplies', display_name: 'Synthetic Supplies', full_name: 'Expenses:Synthetic Supplies', value: '4.00', split_count: 1 }
				]
			},
			amount_is_unambiguous: false
		},
		{
			id: 'tx-dashboard-ambiguous',
			date: '2026-07-08',
			description: 'Synthetic Ambiguous Entry',
			amount: '888.83',
			currency: 'SEK',
			account_id: 'bank-main',
			account_name: 'Synthetic Bank',
			counter_account_name: '',
			direction: {
				status: 'ambiguous',
				reason: 'unbalanced',
				currency: 'SEK',
				from_accounts: [],
				to_accounts: []
			},
			representative_amount: { amount: '888.83', currency: 'SEK' }
		}
	];
}

function scheduledPayload(mode) {
	if (mode === 'empty') return [];
	return [
		{ id: 'schedule-rent', name: 'Synthetic Rent', enabled: true, start_date: '2025-01-01' },
		{ id: 'schedule-insurance', name: 'Synthetic Insurance', enabled: true, start_date: '2025-02-01' },
		{ id: 'schedule-disabled', name: 'Synthetic Disabled Rule', enabled: false, start_date: '2025-03-01' }
	].map((item) => ({
		...item,
		forecast: {
			status: item.enabled ? 'ready' : 'disabled', reason: null, as_of_date: '2026-07-15',
			next_due_date: item.enabled ? '2026-08-01' : null, is_overdue: false,
			upcoming_7_days: [], upcoming_30_days: item.enabled ? ['2026-08-01'] : []
		},
		amount: { status: 'not_available', amount: null, currency: null, unresolved_formula_count: 0, reason: 'no_template_reference' },
		recurrence: [], new_transactions_created: 0, limitations: [],
		end_date: null, last_occurred: null, num_occurrences: null, remaining_occurrences: null,
		auto_create: false, auto_notify: false, advance_create_days: 0, advance_notify_days: 0,
		instance_count: 0, has_template_account: false, template_reference_status: 'not_present_redacted'
	}));
}

function periodReport({ dateFrom, dateTo, mode, comparison = false }) {
	const failed = mode === 'failed-sections' && !comparison;
	const empty = mode === 'empty';
	const expenses = comparison
		? [
			{ account_id: 'expense-housing', account_name: 'Synthetic Housing', total: '5.00', currency: 'SEK' },
			{ account_id: 'expense-food', account_name: 'Synthetic Food', total: '9.00', currency: 'SEK' },
			{ account_id: 'expense-transport', account_name: 'Synthetic Transport', total: '12.00', currency: 'SEK' }
		]
		: expensesPayload(mode);
	const cashflow = comparison
		? { date_from: dateFrom, date_to: dateTo, currency: 'SEK', inflow: '100.00', outflow: '30.00', net: '70.00' }
		: { date_from: dateFrom, date_to: dateTo, currency: 'SEK', inflow: '125.00', outflow: '45.67', net: '79.33' };
	return {
		book_id: 1,
		date_from: dateFrom,
		date_to: dateTo,
		currency: 'SEK',
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: [],
		partial_failure: failed,
		empty,
		section_statuses: [
			{ section: 'summary', status: empty ? 'empty' : 'ok', detail: null },
			{ section: 'cashflow', status: failed ? 'error' : empty ? 'empty' : 'ok', detail: failed ? privateDashboardSentinel : null },
			{ section: 'monthly_cashflow', status: failed ? 'error' : empty ? 'empty' : 'ok', detail: failed ? privateDashboardSentinel : null },
			{ section: 'expenses_by_account', status: failed ? 'error' : empty ? 'empty' : 'ok', detail: failed ? privateDashboardSentinel : null }
		],
		summary: empty ? null : {
			currency: 'SEK',
			net_worth: comparison ? '1350.00' : '1450.00',
			assets: comparison ? '1900.00' : '2000.00',
			liabilities: '550.00',
			as_of_date: dateTo,
			reporting_basis: 'base_currency_only',
			includes_currency_conversion: false,
			limitations: []
		},
		cashflow: failed || empty ? null : cashflow,
		monthly_cashflow: failed || empty ? [] : [{ month: dateTo.slice(0, 7), inflow: cashflow.inflow, outflow: cashflow.outflow, net: cashflow.net }],
		expenses_by_account: failed || empty ? [] : expenses
	};
}

function comparisonPayload(mode, url) {
	const dateFrom = url.searchParams.get('date_from');
	const dateTo = url.searchParams.get('date_to');
	const comparisonDateFrom = url.searchParams.get('comparison_date_from');
	const comparisonDateTo = url.searchParams.get('comparison_date_to');
	assert.equal(dateFrom, '2026-07-01', 'dashboard comparison must start at the summary as-of month');
	assert.equal(dateTo, '2026-07-31', 'dashboard comparison must end at the summary as-of date');
	assert.equal(comparisonDateFrom, '2026-05-31', 'dashboard previous-equivalent range must use exact inclusive date arithmetic');
	assert.equal(comparisonDateTo, '2026-06-30', 'dashboard previous-equivalent range must end immediately before the primary period');
	assert.equal(url.searchParams.get('comparison_mode'), 'previous_equivalent', 'dashboard comparison mode');
	const failed = mode === 'failed-sections';
	const empty = mode === 'empty';
	return {
		book_id: 1,
		comparison_mode: 'previous_equivalent',
		reporting_basis: 'base_currency_only',
		includes_currency_conversion: false,
		limitations: [],
		primary: periodReport({ dateFrom, dateTo, mode }),
		comparison: periodReport({ dateFrom: comparisonDateFrom, dateTo: comparisonDateTo, mode, comparison: true }),
		comparable: !failed && !empty,
		partial_failure: failed,
		empty,
		delta_section_statuses: [
			{ section: 'summary', status: empty ? 'empty' : 'ok', detail: null },
			{ section: 'cashflow', status: failed ? 'error' : empty ? 'empty' : 'ok', detail: failed ? privateDashboardSentinel : null },
			{ section: 'expenses_by_account', status: failed ? 'error' : empty ? 'empty' : 'ok', detail: failed ? privateDashboardSentinel : null }
		],
		summary_delta: empty ? null : {
			currency: 'SEK',
			assets: { primary: '2000.00', comparison: '1900.00', delta: '100.00', absolute_delta: '100.00', currency: 'SEK' },
			liabilities: { primary: '550.00', comparison: '550.00', delta: '0.00', absolute_delta: '0.00', currency: 'SEK' },
			net_worth: { primary: '1450.00', comparison: '1350.00', delta: '100.00', absolute_delta: '100.00', currency: 'SEK' }
		},
		cashflow_delta: empty ? null : {
			currency: 'SEK',
			inflow: { primary: '125.00', comparison: '100.00', delta: '25.00', absolute_delta: '25.00', currency: 'SEK' },
			outflow: { primary: '45.67', comparison: '30.00', delta: '15.67', absolute_delta: '15.67', currency: 'SEK' },
			net: { primary: '79.33', comparison: '70.00', delta: '9.33', absolute_delta: '9.33', currency: 'SEK' }
		},
		expense_changes: empty ? [] : [
			{ account_id: 'expense-housing', account_name: 'Synthetic Housing', primary_total: '15.00', comparison_total: '5.00', delta: '10.00', absolute_delta: '10.00', currency: 'SEK', status: 'ok', detail: null },
			{ account_id: 'expense-transport', account_name: 'Synthetic Transport', primary_total: '8.00', comparison_total: '12.00', delta: '-4.00', absolute_delta: '4.00', currency: 'SEK', status: 'ok', detail: null },
			{ account_id: 'expense-food', account_name: 'Synthetic Food', primary_total: '10.00', comparison_total: '9.00', delta: '1.00', absolute_delta: '1.00', currency: 'SEK', status: 'ok', detail: null }
		]
	};
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
		if (req.method === 'GET' && url.pathname === '/books/1/reports/reporting-date') return jsonResponse(res, 200, { as_of_date: '2026-09-06', basis: 'api_local_calendar' });

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
		if (req.method === 'GET' && url.pathname === '/books/1/scheduled-transactions') {
			return jsonResponse(res, 200, scheduledPayload(state.mode));
		}
		if (req.method !== 'GET' || !url.pathname.startsWith('/books/1/reports/')) {
			return jsonResponse(res, 404, { detail: 'Synthetic dashboard smoke endpoint not found.' });
		}

		if (url.pathname === '/books/1/reports/summary') return jsonResponse(res, 200, summaryPayload(state.mode));
		if (url.pathname === '/books/1/reports/recent-transactions') return jsonResponse(res, 200, recentTransactionsPayload(state.mode));
		if (url.pathname === '/books/1/reports/comparison') return jsonResponse(res, 200, comparisonPayload(state.mode, url));
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

async function assertDecisionDashboard(cdp, { requireFirstViewport }) {
	const state = await evaluate(cdp, `(() => ({
		bodyText: document.body?.innerText ?? '',
		viewportHeight: window.innerHeight,
		overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
		decisions: Array.from(document.querySelectorAll('[data-dashboard-decision]')).map((node) => ({
			id: node.getAttribute('data-dashboard-decision'),
			top: node.getBoundingClientRect().top,
			bottom: node.getBoundingClientRect().bottom
		})),
		safetyDetails: Array.from(document.querySelectorAll('details[data-dashboard-safety-details]')).map((node) => ({ open: node.open })),
		expenseRows: Array.from(document.querySelectorAll('[data-dashboard-expense-row]')).map((node) => node.textContent.replace(/\\s+/g, ' ').trim()),
		recentKinds: Array.from(document.querySelectorAll('[data-dashboard-recent-kind]')).map((node) => node.getAttribute('data-dashboard-recent-kind')),
		dateWhiteSpaces: Array.from(document.querySelectorAll('[data-dashboard-date]')).map((node) => getComputedStyle(node).whiteSpace),
		links: Array.from(document.querySelectorAll('a[href]')).map((node) => node.getAttribute('href'))
	}))()`);

	assert.equal(state.overflowX, false, 'decision dashboard must not overflow horizontally');
	assert.deepEqual(state.decisions.map((item) => item.id), ['position', 'month-result', 'largest-changes', 'upcoming-obligations'], 'dashboard must order the four decision cards first');
	if (requireFirstViewport) {
		assert.ok(state.decisions.every((item) => item.top >= 0 && item.bottom <= state.viewportHeight), 'desktop first viewport must contain all four decision cards');
	}
	assert.deepEqual(state.safetyDetails, [{ open: false }], 'dashboard must have exactly one collapsed calculation/safety details panel');
	assert.match(state.bodyText, /Position[\s\S]*1450\.00[\s\S]*As of[\s\S]*2026-07-31/, 'position card must show exact signed net worth and summary as-of date');
	assert.match(state.bodyText, /Month result[\s\S]*79\.33[\s\S]*125\.00[\s\S]*45\.67/, 'month result must use exact API cashflow strings');
	assert.match(state.bodyText, /Largest changes[\s\S]*Synthetic Housing[\s\S]*10\.00[\s\S]*Synthetic Transport[\s\S]*-4\.00/, 'largest changes must preserve signed Decimal deltas');
	assert.match(state.bodyText, /Upcoming obligations[\s\S]*2 enabled schedules[\s\S]*Exact next due dates are not available yet/, 'upcoming obligations must be honest when next-occurrence data is unavailable');
	assert.equal(state.expenseRows.length, 5, 'dashboard must show exactly the top five expenses');
	assert.match(state.expenseRows.join('\n'), /Synthetic Housing[\s\S]*Synthetic Utilities/, 'top-five expenses must remain visible');
	assert.doesNotMatch(state.bodyText, /Synthetic Dining|Synthetic Books/, 'expenses beyond the top five must stay out of the compact dashboard');
	assert.ok(state.links.some((href) => href?.startsWith('/reports?preset=custom&date_from=2026-07-01&date_to=2026-07-31')), 'view-all expenses link must preserve the exact as-of month report range');
	assert.ok(state.links.includes('/scheduled'), 'upcoming obligations must link to the read-only scheduled view');
	assert.match(state.bodyText, /From Synthetic Income to Synthetic Bank/, 'ordinary two-split transaction must use a friendly one-line summary');
	assert.deepEqual(state.recentKinds, ['ordinary', 'ordinary', 'composite', 'ambiguous'], 'composite and ambiguous copy must be reserved for true non-ordinary cases');
	assert.match(state.bodyText, /125\.00\s+SEK/, 'ordinary transaction may show its explicit representative amount');
	assert.doesNotMatch(state.bodyText, /999\.91|777\.72|888\.83/, 'dashboard must not invent or leak representative amounts from fallback/composite/ambiguous values');
	assert.ok(state.dateWhiteSpaces.length >= 5 && state.dateWhiteSpaces.every((value) => value === 'nowrap'), 'as-of and recent transaction dates must not wrap');
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
	const summaryGrid = readFileSync(join(root, 'src', 'lib', 'components', 'SummaryGrid.svelte'), 'utf8');
	const recent = readFileSync(join(root, 'src', 'lib', 'components', 'RecentTransactions.svelte'), 'utf8');
	const expenses = readFileSync(join(root, 'src', 'lib', 'components', 'ExpensesByAccount.svelte'), 'utf8');
	assert.match(server, /sectionErrors[\s\S]*summary[\s\S]*expenses[\s\S]*cashflow[\s\S]*recentTransactions/s, 'dashboard server must return explicit per-section error state');
	assert.match(page, /data-dashboard-section-error[\s\S]*role="alert"[\s\S]*dashboard\.sectionError\.redacted/s, 'dashboard page must render accessible fixed-copy section errors');
	assert.doesNotMatch(server, /e\.message|error\.message/, 'dashboard server must not return raw backend exception messages');
	assert.match(server, /getReportingDate\(fetchFn, bookPrefix, token, summary\?\.as_of_date\)[\s\S]*monthStart[\s\S]*previousEquivalentRange[\s\S]*reports\/comparison/s, 'dashboard report range must prefer summary as-of and use exact previous-equivalent dates');
	assert.doesNotMatch(server, /new Date\(\)\.toISOString\(\)/, 'QA-04 dashboard fallback cannot derive today from a JS UTC instant');
	assert.match(summaryGrid, /data-dashboard-decision="position"[\s\S]*data-dashboard-decision="month-result"[\s\S]*data-dashboard-decision="largest-changes"[\s\S]*data-dashboard-decision="upcoming-obligations"/s, 'dashboard summary must prioritize the four decision cards');
	assert.match(summaryGrid, /<details[\s\S]*data-dashboard-safety-details[\s\S]*dashboard\.reportingBasis[\s\S]*dashboard\.currencyConversion/s, 'technical calculation and safety copy must live in one disclosure');
	assert.match(expenses, /expenses\.slice\(0, 5\)[\s\S]*data-dashboard-expense-row/s, 'expenses component must render only five rows');
	assert.match(expenses, /viewAllHref[\s\S]*dashboard\.viewAllExpenses/s, 'expenses component must expose a view-all link');
	assert.match(recent, /RecentTransaction[\s\S]*ordinaryTwoSplit[\s\S]*tx\.amount_is_unambiguous[\s\S]*tx\.amount\.replace[\s\S]*currency: tx\.currency[\s\S]*data-dashboard-recent-kind/s, 'QA-02 recent amounts must use the real report contract and backend simple-amount classification');
	assert.doesNotMatch(recent, /tx\.representative_amount|tx\.matched_amount/, 'QA-02 explorer-only amount fields cannot leak into recent rendering');
	assert.doesNotMatch(`${server}\n${page}\n${summaryGrid}\n${recent}\n${expenses}`, /parseFloat\(|Number\([^)]*(?:amount|total|net|inflow|outflow|expense|income|delta)/, 'dashboard must not use float/Number conversion on money strings');
	assert.doesNotMatch(`${summaryGrid}\n${expenses}`, /from ['"][^'"]*(?:chart|d3|echarts|plotly|recharts)/i, 'dashboard trends must not add a heavy chart dependency');
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
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
		await cdp.send('Network.setCookie', { name: 'access_token', value: syntheticToken, url: webBase, path: '/', sameSite: 'Lax' });

		api.setMode('populated');
		await navigateDashboard(cdp, webBase, 'decision dashboard desktop');
		await assertDecisionDashboard(cdp, { requireFirstViewport: true });
		if (process.env.DASHBOARD_SMOKE_SCREENSHOT) {
			const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
			writeFileSync(process.env.DASHBOARD_SMOKE_SCREENSHOT, Buffer.from(screenshot.data, 'base64'));
		}
		assertNoMutationRequestsObserved(api, browserRequests, 'decision dashboard desktop');

		for (const width of [390, 320]) {
			await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 760, deviceScaleFactor: 2, mobile: true });
			await navigateDashboard(cdp, webBase, `decision dashboard mobile ${width}`);
			await assertDecisionDashboard(cdp, { requireFirstViewport: false });
			if (width === 320 && process.env.DASHBOARD_SMOKE_MOBILE_SCREENSHOT) {
				const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
				writeFileSync(process.env.DASHBOARD_SMOKE_MOBILE_SCREENSHOT, Buffer.from(screenshot.data, 'base64'));
			}
			assertNoMutationRequestsObserved(api, browserRequests, `decision dashboard mobile ${width}`);
		}

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
