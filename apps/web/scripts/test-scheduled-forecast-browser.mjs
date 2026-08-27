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
const smokeHome = process.env.SCHEDULED_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.SCHEDULED_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-scheduled');
const syntheticToken = 'synthetic-scheduled-forecast-token';
const privateLimitationSentinel = 'PRIVATE_SCHEDULE_LIMITATION_MUST_NOT_RENDER_91A4';
const cdpCommandTimeoutMs = Number(process.env.SCHEDULED_CDP_TIMEOUT_MS ?? '90000');

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
	name: 'Synthetic Schedule Book With A Long Mobile Label',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_enabled: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for scheduled forecast smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	capabilities: {
		read_only: true,
		can_register_metadata: false,
		can_open_accounts: true,
		can_open_transactions: true,
		can_open_reports: true,
		can_upload: false,
		can_edit: false,
		can_delete: false
	},
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic scheduled forecast fixture.',
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
		message: 'Synthetic scheduled forecast smoke; no private book is used.'
	}
};

const recurrence = [{ period_type: 'month', multiplier: 1, period_start: '2026-01-01', weekend_adjust: 'none' }];

function scheduledItem({ id, name, enabled = true, nextDue, overdue = false, upcoming7 = [], upcoming30 = [], forecastStatus = 'ready', amount }) {
	return {
		id,
		name,
		enabled,
		start_date: '2026-01-01',
		end_date: null,
		last_occurred: '2026-07-01',
		num_occurrences: null,
		remaining_occurrences: null,
		auto_create: false,
		auto_notify: true,
		advance_create_days: 0,
		advance_notify_days: 3,
		instance_count: 7,
		has_template_account: amount?.status !== 'not_available',
		template_reference_status: amount?.status !== 'not_available' ? 'present_redacted' : 'not_present_redacted',
		recurrence,
		forecast: {
			status: forecastStatus,
			as_of_date: '2026-08-28',
			next_due_date: nextDue,
			is_overdue: overdue,
			upcoming_7_days: upcoming7,
			upcoming_30_days: upcoming30
		},
		amount: amount ?? {
			status: 'not_available',
			amount: null,
			currency: null,
			unresolved_formula_count: 0,
			reason: 'no_template_reference'
		},
		new_transactions_created: 0,
		limitations: [privateLimitationSentinel]
	};
}

const scheduledTransactions = [
	scheduledItem({
		id: 'schedule-overdue',
		name: 'Synthetic overdue obligation',
		nextDue: '2026-08-20',
		overdue: true,
		upcoming7: ['2026-08-29'],
		upcoming30: ['2026-08-29', '2026-09-20'],
		amount: { status: 'unresolved', amount: null, currency: null, unresolved_formula_count: 2, reason: 'template_variables_unresolved' }
	}),
	scheduledItem({
		id: 'schedule-upcoming',
		name: 'Synthetic due soon',
		nextDue: '2026-08-29',
		upcoming7: ['2026-08-29'],
		upcoming30: ['2026-08-29', '2026-09-29'],
		amount: { status: 'resolved', amount: '125.5000', currency: 'SEK', unresolved_formula_count: 0, reason: null }
	}),
	scheduledItem({
		id: 'schedule-next30',
		name: 'Synthetic within thirty days',
		nextDue: '2026-09-12',
		upcoming30: ['2026-09-12']
	}),
	scheduledItem({
		id: 'schedule-later',
		name: 'Synthetic later obligation',
		nextDue: '2026-10-10'
	}),
	scheduledItem({
		id: 'schedule-disabled',
		name: 'Synthetic disabled schedule',
		enabled: false,
		nextDue: null,
		forecastStatus: 'disabled'
	})
];

function allGreenHealth() {
	const checks = Object.fromEntries(
		['jwt_secret', 'admin_bootstrap', 'default_book', 'cors', 'write_mode'].map((key) => [key, {
			status: 'ok',
			message: `Synthetic ${key} check passed.`,
			safe_next_actions: []
		}])
	);
	return {
		status: 'ok',
		service: 'gnucash-web-companion-api',
		warnings: [],
		first_run: {
			summary: 'All synthetic first-run checks passed.',
			action_required: [],
			checks
		}
	};
}

function jsonResponse(res, status, body) {
	const payload = Buffer.from(JSON.stringify(body));
	res.writeHead(status, {
		'content-type': 'application/json',
		'content-length': String(payload.length)
	});
	res.end(payload);
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	let scheduledFailure = false;
	const server = createServer((req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		const method = req.method ?? 'GET';
		requests.push({ method, path: url.pathname, search: url.search });
		if (!['GET', 'HEAD'].includes(method) || /(?:create|validate|patch|delete|batch|backup|write-alpha)/i.test(`${url.pathname}${url.search}`)) {
			forbiddenRequests.push({ method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, { detail: 'Synthetic scheduled smoke blocked a mutation-capable request.' });
		}
		if (method === 'GET' && url.pathname === '/health') return jsonResponse(res, 200, allGreenHealth());
		if (method === 'GET' && url.pathname === '/auth/me') {
			return jsonResponse(res, 200, { id: 1, username: 'synthetic_scheduled', display_name: 'Synthetic Scheduled', is_admin: false });
		}
		if (method === 'GET' && url.pathname === '/books') return jsonResponse(res, 200, [syntheticBook]);
		if (method === 'GET' && url.pathname === '/books/1/scheduled-transactions') {
			if (scheduledFailure) return jsonResponse(res, 503, { detail: 'Synthetic scheduled read failure.' });
			return jsonResponse(res, 200, scheduledTransactions);
		}
		return jsonResponse(res, 404, { detail: 'Synthetic scheduled smoke endpoint not found.' });
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
		setScheduledFailure(value) {
			scheduledFailure = value;
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

function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForHttp(url, timeoutMs = 30000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		try {
			const response = await fetch(url);
			if (response.status < 500) return;
		} catch {
			// retry until timeout
		}
		await sleep(200);
	}
	throw new Error(`Timed out waiting for ${url}`);
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

async function removeProfileDir(profileDir) {
	for (let attempt = 1; attempt <= 5; attempt += 1) {
		try {
			rmSync(profileDir, { recursive: true, force: true });
			return;
		} catch (error) {
			if (!['ENOTEMPTY', 'EBUSY', 'EPERM'].includes(error?.code) || attempt === 5) throw error;
			await sleep(attempt * 200);
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
	assert.ok(target?.webSocketDebuggerUrl, 'Chromium CDP page target must expose websocket URL');
	const cdp = new CdpClient(target.webSocketDebuggerUrl);
	await cdp.connect();
	return cdp;
}

async function evaluate(cdp, expression) {
	const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true });
	if (result.exceptionDetails) throw new Error(`Browser evaluation failed: ${JSON.stringify(result.exceptionDetails)}`);
	return result.result?.value;
}

async function waitForExpression(cdp, expression, label, timeoutMs = 30000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		if (await evaluate(cdp, expression)) return;
		await sleep(150);
	}
	const snapshot = await evaluate(cdp, `({ path: location.pathname, title: document.title, text: document.body.innerText.slice(0, 3000) })`);
	throw new Error(`Timed out waiting for ${label}\n${JSON.stringify(snapshot, null, 2)}`);
}

function waitForCdpEvent(cdp, method, timeoutMs = 30000) {
	return new Promise((resolve) => {
		let done = false;
		const finish = (value) => {
			if (done) return;
			done = true;
			resolve(value);
		};
		const timer = setTimeout(() => finish(null), timeoutMs);
		cdp.on(method, (params) => {
			clearTimeout(timer);
			finish(params);
		});
	});
}

async function navigate(cdp, baseUrl, path, selector) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired');
	await cdp.send('Page.navigate', { url: `${baseUrl}${path}` });
	await load;
	await waitForExpression(cdp, `location.pathname === ${JSON.stringify(path.split('?')[0])} && document.querySelector(${JSON.stringify(selector)})`, `${path} ${selector}`);
}

async function setViewport(cdp, width, height) {
	await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: width <= 480 ? 2 : 1, mobile: width <= 480 });
}

async function setAuthenticatedSession(cdp, baseUrl) {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: syntheticToken, url: baseUrl, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'selected_book_id', value: '1', url: baseUrl, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: baseUrl, path: '/', sameSite: 'Lax' });
}

async function scheduledPageState(cdp) {
	return evaluate(cdp, `(() => {
		const firstCard = document.querySelector('[data-first-meaningful-card="true"]');
		const banner = document.querySelector('[data-read-only-banner]');
		const mobileLabels = [...document.querySelectorAll('[data-mobile-primary] > span:last-child, [data-mobile-more] > span:last-child')].map((node) => ({
			text: node.textContent?.trim() ?? '',
			overflow: node.scrollWidth - node.clientWidth,
			textOverflow: getComputedStyle(node).textOverflow
		}));
		const rect = firstCard?.getBoundingClientRect();
		const mobileNavTop = document.querySelector('[data-mobile-nav]')?.getBoundingClientRect().top ?? null;
		return {
			title: document.title,
			text: document.body.innerText,
			overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
			groups: [...document.querySelectorAll('[data-schedule-group]')].map((node) => node.getAttribute('data-schedule-group')),
			rowCount: document.querySelectorAll('[data-schedule-row]').length,
			closedRowDetails: document.querySelectorAll('[data-schedule-row] details:not([open])').length,
			focusableSummaries: [...document.querySelectorAll('[data-schedule-row] summary')].every((node) => node.tabIndex === 0 && Boolean(node.textContent?.trim())),
			firstCardTop: rect?.top ?? null,
			firstCardBottom: rect?.bottom ?? null,
			viewportHeight: innerHeight,
			mobileNavTop,
			bannerHeight: banner?.getBoundingClientRect().height ?? null,
			bannerOpen: banner?.querySelector('details')?.open ?? null,
			mobileLabels,
			primaryCount: document.querySelectorAll('[data-mobile-primary]').length,
			moreCount: document.querySelectorAll('[data-mobile-more]').length,
			favicon: new URL(document.querySelector('link[rel="icon"]')?.getAttribute('href') ?? '', location.href).pathname,
			modernMobileMeta: document.querySelector('meta[name="mobile-web-app-capable"]')?.getAttribute('content') ?? ''
		};
	})()`);
}

let api;
let webProcess;
let chromeProcess;
let cdp;
let profileDir;

try {
	assert.ok(existsSync(viteBin), `vite must be installed at ${viteBin}`);
	assert.ok(existsSync(chromiumBin), `Chromium must be installed at ${chromiumBin}`);
	mkdirSync(smokeTempRoot, { recursive: true });
	profileDir = mkdtempSync(join(smokeTempRoot, 'profile-'));
	api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	const webBase = `http://127.0.0.1:${webPort}`;

	webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
		cwd: root,
		env: { ...process.env, API_INTERNAL_URL: api.url, ORIGIN: webBase }
	});
	await waitForHttp(`${webBase}/login`);

	chromeProcess = spawnLogged(chromiumBin, [
		'--headless=new',
		'--disable-gpu',
		'--no-sandbox',
		'--disable-dev-shm-usage',
		'--disable-background-networking',
		'--disable-component-update',
		'--disable-default-apps',
		'--disable-extensions',
		'--disable-sync',
		'--metrics-recording-only',
		'--no-first-run',
		'--remote-allow-origins=*',
		'--remote-debugging-address=127.0.0.1',
		`--remote-debugging-port=${debugPort}`,
		`--user-data-dir=${profileDir}`,
		'--window-size=1280,900',
		'about:blank'
	], { cwd: root, env: process.env });
	cdp = await connectCdp(debugPort);
	const browserRequests = [];
	const consoleErrors = [];
	cdp.on('Network.requestWillBeSent', (event) => browserRequests.push({ method: event.request.method, url: event.request.url }));
	cdp.on('Runtime.consoleAPICalled', (event) => {
		if (event.type === 'error') consoleErrors.push(event);
	});
	await cdp.send('Page.enable');
	await cdp.send('Runtime.enable');
	await cdp.send('Network.enable');
	await setAuthenticatedSession(cdp, webBase);

	const viewportEvidence = [];
	for (const [width, height] of [[1280, 900], [390, 844], [320, 760]]) {
		await setViewport(cdp, width, height);
		await navigate(cdp, webBase, '/scheduled', '[data-schedule-row]');
		const state = await scheduledPageState(cdp);
		assert.equal(state.overflowX, 0, `${width}px scheduled page must not overflow horizontally`);
		assert.deepEqual(state.groups, ['overdue', 'upcoming', 'next_30_days', 'later_or_inactive'], `${width}px forecast groups must be ordered deterministically`);
		assert.equal(state.rowCount, 5, `${width}px scheduled page must render all synthetic rows`);
		assert.equal(state.closedRowDetails, 5, `${width}px technical row details must be collapsed by default`);
		assert.equal(state.focusableSummaries, true, `${width}px technical summaries must remain keyboard-focusable and labelled`);
		assert.ok(state.firstCardTop !== null && state.firstCardTop < state.viewportHeight, `${width}px first meaningful schedule card must begin above the fold`);
		assert.ok(state.firstCardBottom !== null && state.firstCardBottom <= state.viewportHeight, `${width}px one complete meaningful schedule card must fit above the fold, bottom ${state.firstCardBottom}/${state.viewportHeight}`);
		assert.ok(state.bannerHeight !== null && state.bannerHeight <= 48, `${width}px healthy read-only banner must remain one compact line, got ${state.bannerHeight}`);
		assert.equal(state.bannerOpen, false, `${width}px safety details must be collapsed by default`);
		assert.match(state.text, /125\.5000\s+SEK/, `${width}px safely resolved exact Decimal string must be visible`);
		assert.ok(state.text.includes('Amount unavailable'), `${width}px unresolved rows must show a status instead of a fabricated amount`);
		assert.doesNotMatch(state.text, /0\.00/, `${width}px unresolved amount must not be fabricated as zero`);
		assert.ok(!state.text.includes(privateLimitationSentinel), `${width}px raw backend limitations must not render`);
		assert.equal(state.favicon, '/icon.svg', `${width}px favicon must be present`);
		assert.equal(state.modernMobileMeta, 'yes', `${width}px modern mobile capability meta must be present`);
		if (width <= 480) {
			assert.ok(state.mobileNavTop !== null && state.firstCardBottom <= state.mobileNavTop, `${width}px complete first card must remain above fixed mobile navigation, bottom ${state.firstCardBottom}/${state.mobileNavTop}`);
			assert.equal(state.primaryCount, 4, `${width}px mobile nav must have four primary links`);
			assert.equal(state.moreCount, 1, `${width}px mobile nav must have one More control`);
			for (const label of state.mobileLabels) {
				assert.ok(label.text, `${width}px mobile nav label must not be empty`);
				assert.ok(label.overflow <= 1, `${width}px mobile nav label ${label.text} must not be clipped`);
				assert.notEqual(label.textOverflow, 'ellipsis', `${width}px mobile nav label ${label.text} must not use ellipsis`);
			}
		}
		viewportEvidence.push({ width, overflowX: state.overflowX, firstCardTop: state.firstCardTop, firstCardBottom: state.firstCardBottom, mobileNavTop: state.mobileNavTop, bannerHeight: state.bannerHeight });
	}

	const moreButtonFocused = await evaluate(cdp, `(() => {
		const button = document.querySelector('[data-mobile-more]');
		button?.focus();
		button?.click();
		return document.activeElement === button;
	})()`);
	await waitForExpression(cdp, `document.querySelector('[data-mobile-more]')?.getAttribute('aria-expanded') === 'true' && document.querySelector('[data-mobile-menu]')`, 'mobile More menu expanded');
	const moreMenuState = await evaluate(cdp, `(() => {
		const button = document.querySelector('[data-mobile-more]');
		const menu = document.querySelector('[data-mobile-menu]');
		return { expanded: button?.getAttribute('aria-expanded'), text: menu?.textContent ?? '' };
	})()`);
	assert.equal(moreButtonFocused, true, 'mobile More button must accept keyboard focus');
	assert.equal(moreMenuState.expanded, 'true', 'mobile More button must expose expanded state');
	assert.match(moreMenuState.text, /Reports/);
	assert.match(moreMenuState.text, /Books/);

	await cdp.send('Network.clearBrowserCookies');
	await setViewport(cdp, 390, 844);
	await navigate(cdp, webBase, '/login', '[data-first-run-checks]');
	const loginDiagnostics = await evaluate(cdp, `(() => ({
		open: document.querySelector('[data-first-run-checks]')?.open,
		overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		title: document.title
	}))()`);
	assert.equal(loginDiagnostics.open, false, 'all-green login first-run diagnostics must be collapsed');
	assert.equal(loginDiagnostics.overflowX, 0, 'login diagnostics must not overflow at 390px');
	assert.match(loginDiagnostics.title, /^Sign in —/);

	await navigate(cdp, webBase, '/diagnostics', '[data-first-run-checks]');
	const publicDiagnostics = await evaluate(cdp, `(() => ({
		open: document.querySelector('[data-first-run-checks]')?.open,
		overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		title: document.title
	}))()`);
	assert.equal(publicDiagnostics.open, false, 'all-green public diagnostics must be collapsed');
	assert.equal(publicDiagnostics.overflowX, 0, 'public diagnostics must not overflow at 390px');
	assert.equal(publicDiagnostics.title, 'First-run diagnostics — GnuCash Web Companion');

	await setAuthenticatedSession(cdp, webBase);
	api.setScheduledFailure(true);
	await navigate(cdp, webBase, '/scheduled', '[role="alert"]');
	const errorState = await evaluate(cdp, `(() => ({
		title: document.title,
		text: document.body.innerText,
		links: [...document.querySelectorAll('[role="alert"] a')].map((link) => ({ href: link.getAttribute('href'), text: link.textContent?.trim() ?? '', aria: link.getAttribute('aria-label') }))
	}))()`);
	assert.equal(errorState.title, 'Service temporarily unavailable — GnuCash Web Companion', '503 document title must match visible service error');
	assert.ok(errorState.links.some((link) => link.href === '/diagnostics' && link.text.includes('diagnostics')), '503 must offer redacted diagnostics');
	assert.ok(errorState.links.some((link) => link.href === '/books' && link.text.includes('Review books')), '503 must offer books recovery');
	assert.ok(errorState.links.some((link) => link.href === '/scheduled' && link.text.includes('Retry')), '503 must offer retry with a labelled link');
	assert.ok(errorState.links.every((link) => Boolean(link.aria)), 'error actions must preserve explicit keyboard/screen-reader labels');
	api.setScheduledFailure(false);

	assert.equal(api.forbiddenRequests.length, 0, `browser smoke must not call mutation-capable API paths: ${JSON.stringify(api.forbiddenRequests)}`);
	assert.ok(api.requests.some((request) => request.method === 'GET' && request.path === '/books/1/scheduled-transactions'), 'browser must load the scheduled forecast via GET');
	assert.ok(api.requests.every((request) => ['GET', 'HEAD'].includes(request.method)), 'synthetic API traffic must remain read-only');
	assert.ok(browserRequests.every((request) => !/\/scheduled-transactions(?:\/|\?|$)/.test(request.url) || request.method === 'GET'), 'browser-observed scheduled endpoint traffic must be GET-only');
	assert.equal(consoleErrors.length, 0, `browser console must remain free of errors: ${JSON.stringify(consoleErrors)}`);

	console.log('scheduled forecast browser smoke passed', JSON.stringify({
		viewports: viewportEvidence,
		apiRequests: api.requests.length,
		forbiddenRequests: api.forbiddenRequests.length,
		resolvedAmount: '125.5000 SEK',
		firstRunCollapsed: true,
		errorActionsVerified: true
	}));
} catch (error) {
	const details = [
		error?.stack ?? String(error),
		webProcess ? `web output:\n${webProcess.outputTail()}` : '',
		chromeProcess ? `chromium output:\n${chromeProcess.outputTail()}` : ''
	].filter(Boolean).join('\n\n');
	throw new Error(details);
} finally {
	cdp?.close();
	await stopProcess(chromeProcess);
	await stopProcess(webProcess);
	if (api) await api.close();
	if (profileDir) await removeProfileDir(profileDir);
}
