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
const smokeHome = process.env.ADMIN_USERS_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.ADMIN_USERS_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-admin-users');
const cdpCommandTimeoutMs = Number(process.env.ADMIN_USERS_CDP_TIMEOUT_MS ?? '120000');

const adminToken = 'JWT_SENTINEL_ADMIN_USERS_BROWSER_ADMIN';
const userToken = 'JWT_SENTINEL_ADMIN_USERS_BROWSER_USER';
const expiredToken = 'JWT_SENTINEL_ADMIN_USERS_BROWSER_EXPIRED';
const exactCreatePassword = ' exact create password 57 ! keep spaces ';
const exactResetPassword = ' exact reset password 57 ! keep spaces ';
const privatePathSentinel = '/home/private/Syncthing/only-copy/admin-users-private.gnucash.sqlite';
const backendSentinel = 'RAW_SQL_ADMIN_USERS_SENTINEL_password_hash_jwt_cookie_path_57';
const passwordHashSentinel = 'PASSWORD_HASH_SENTINEL_ADMIN_USERS_57';
const cookieSentinel = 'COOKIE_SENTINEL_ADMIN_USERS_57';
const leakSentinels = [
	adminToken,
	userToken,
	expiredToken,
	exactCreatePassword,
	exactResetPassword,
	privatePathSentinel,
	backendSentinel,
	passwordHashSentinel,
	cookieSentinel
];

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

function syntheticBook() {
	return {
		id: 1,
		name: 'Synthetic Admin Users Book',
		storage_type: 'sqlite',
		base_currency: 'SEK',
		is_default: true,
		is_archived: false,
		access_role: 'owner',
		access_role_label: 'Owner',
		access_role_description: 'Synthetic owner access for admin-users browser smoke only.',
		read_only: true,
		status: 'available',
		status_severity: 'ok',
		access_status: 'owner',
		can_open_read_only_views: true,
		storage_diagnostics: {
			status: 'available',
			configured: true,
			checked: true,
			safe_summary: 'Synthetic admin users browser fixture.',
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
			message: 'Synthetic local admin-users smoke fixture; no private book is used.'
		}
	};
}

const bookOptions = [
	{ id: 1, name: 'Synthetic Admin Users Book', is_default: true },
	{ id: 2, name: 'Synthetic Reports Access Book', is_default: false }
];

function now(offset = 0) {
	return `2026-07-15T13:${String(20 + offset).padStart(2, '0')}:00Z`;
}

function userRecord({ id, username, displayName, isAdmin = false, enabled = true, assignments = [] }) {
	return {
		id,
		username,
		display_name: displayName,
		is_admin: isAdmin,
		is_enabled: enabled,
		created_at: now(id),
		updated_at: now(id + 1),
		assignments
	};
}

function userSummary(user) {
	return {
		id: user.id,
		username: user.username,
		display_name: user.display_name,
		is_admin: user.is_admin,
		is_enabled: user.is_enabled,
		assignment_count: user.assignments.length,
		created_at: user.created_at,
		updated_at: user.updated_at
	};
}

function userDetail(user) {
	return { ...userSummary(user), assignments: user.assignments.map((assignment) => ({ ...assignment })) };
}

function adminProblem(code) {
	return {
		safe_code: code,
		detail: {
			safe_code: code,
			raw_backend_detail: backendSentinel,
			password_hash: passwordHashSentinel,
			cookie: cookieSentinel,
			uri_or_path: privatePathSentinel
		}
	};
}

function unknownProblem() {
	return {
		detail: {
			code: 'canonical_path',
			raw_backend_detail: backendSentinel,
			password_hash: passwordHashSentinel,
			cookie: cookieSentinel,
			uri_or_path: privatePathSentinel
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

function readBody(req) {
	return new Promise((resolve, reject) => {
		let body = '';
		req.setEncoding('utf8');
		req.on('data', (chunk) => {
			body += chunk;
		});
		req.on('end', () => resolve(body));
		req.on('error', reject);
	});
}

function parseJson(body) {
	if (!body) return {};
	try {
		return JSON.parse(body);
	} catch {
		return {};
	}
}

function bearerToken(req) {
	const header = req.headers.authorization ?? '';
	const match = /^Bearer\s+(.+)$/i.exec(Array.isArray(header) ? header[0] : header);
	return match?.[1] ?? '';
}

function tokenKind(token) {
	if (token === adminToken) return 'admin';
	if (token === userToken) return 'user';
	if (token === expiredToken) return 'expired';
	return 'unknown';
}

function isForbiddenProductWrite(method, pathname, search = '') {
	const upper = method.toUpperCase();
	if (!['POST', 'PATCH', 'PUT', 'DELETE'].includes(upper)) return false;
	const target = `${pathname}${search}`;
	return /(?:\/|%2F|[?&=])(?:transactions?|splits?|scheduled|backups?|gnucash|write-alpha|owner-writebeta|import|upload|ofx|csv|batch|create-preview|validate|source)(?:\/|%2F|$|[?&=])/i.test(target)
		|| /^\/books(?:\/|$)/.test(pathname);
}

function isAdminApiPath(pathname) {
	return pathname === '/admin/users' || pathname.startsWith('/admin/users/') || pathname.startsWith('/admin/book-access/');
}

async function startSyntheticApi() {
	const users = new Map([
		[1, userRecord({
			id: 1,
			username: 'synthetic_admin',
			displayName: 'Synthetic Admin',
			isAdmin: true,
			enabled: true,
			assignments: [{ book_id: 1, book_name: 'Synthetic Admin Users Book', is_default: true, role: 'owner' }]
		})],
		[2, userRecord({
			id: 2,
			username: 'synthetic_viewer',
			displayName: 'Synthetic Viewer',
			isAdmin: false,
			enabled: false,
			assignments: []
		})]
	]);
	let nextUserId = 3;
	const requests = [];
	const forbiddenProductWriteRequests = [];
	const normalUserForbiddenAttempts = [];
	const createBodies = [];
	const resetBodies = [];
	const mutationBodies = [];

	function requireAdmin(req, res) {
		const kind = tokenKind(bearerToken(req));
		if (kind === 'expired') {
			jsonResponse(res, 401, adminProblem('session_changed'));
			return false;
		}
		if (kind === 'admin') return true;
		normalUserForbiddenAttempts.push({ method: req.method, path: new URL(req.url ?? '/', 'http://127.0.0.1').pathname });
		jsonResponse(res, 403, adminProblem('admin_required'));
		return false;
	}

	function sortedUsers() {
		return [...users.values()].sort((left, right) => left.id - right.id);
	}

	function listPayload(url) {
		const limit = Math.max(1, Math.min(100, Number(url.searchParams.get('limit') ?? '50') || 50));
		const offset = Math.max(0, Number(url.searchParams.get('offset') ?? '0') || 0);
		const state = url.searchParams.get('state') ?? 'all';
		let items = sortedUsers();
		if (state === 'enabled') items = items.filter((user) => user.is_enabled);
		if (state === 'disabled') items = items.filter((user) => !user.is_enabled);
		const pageItems = offset >= 100 ? [] : items.slice(offset, offset + limit);
		return {
			items: pageItems.map(userSummary),
			total_count: items.length,
			limit,
			offset,
			has_next: offset + limit < items.length
		};
	}

	async function handler(req, res) {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		const method = req.method ?? 'GET';
		const kind = tokenKind(bearerToken(req));
		requests.push({ method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}`, tokenKind: kind });

		if (isForbiddenProductWrite(method, url.pathname, url.search)) {
			forbiddenProductWriteRequests.push({ method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, adminProblem('unknown_admin_problem'));
		}

		if (method === 'GET' && url.pathname === '/health') {
			return jsonResponse(res, 200, { status: 'ok', first_run: null });
		}
		if (kind === 'expired' && (url.pathname === '/auth/me' || isAdminApiPath(url.pathname))) {
			return jsonResponse(res, 401, adminProblem('session_changed'));
		}
		if (method === 'GET' && url.pathname === '/auth/me') {
			return jsonResponse(res, 200, {
				id: kind === 'admin' ? 1 : 2,
				username: kind === 'admin' ? 'synthetic_admin' : 'synthetic_viewer',
				display_name: kind === 'admin' ? 'Synthetic Admin' : 'Synthetic Viewer',
				is_admin: kind === 'admin'
			});
		}
		if (method === 'GET' && url.pathname === '/books') {
			return jsonResponse(res, 200, [syntheticBook()]);
		}

		if (method === 'GET' && url.pathname === '/admin/users') {
			if (!requireAdmin(req, res)) return;
			return jsonResponse(res, 200, listPayload(url));
		}
		if (method === 'GET' && url.pathname === '/admin/book-access/books') {
			if (!requireAdmin(req, res)) return;
			return jsonResponse(res, 200, bookOptions);
		}
		if (method === 'POST' && url.pathname === '/admin/users') {
			if (!requireAdmin(req, res)) return;
			const body = parseJson(await readBody(req));
			createBodies.push(body);
			mutationBodies.push({ kind: 'create', body });
			const username = String(body.username ?? '');
			if (username.includes('taken')) return jsonResponse(res, 409, adminProblem('username_taken'));
			if (username.includes('invalid')) return jsonResponse(res, 422, adminProblem('password_policy'));
			if (username.includes('unknown')) return jsonResponse(res, 500, unknownProblem());
			const user = userRecord({
				id: nextUserId++,
				username,
				displayName: String(body.display_name ?? ''),
				isAdmin: body.is_admin === true,
				enabled: true,
				assignments: []
			});
			users.set(user.id, user);
			return jsonResponse(res, 200, userDetail(user));
		}

		const userMatch = url.pathname.match(/^\/admin\/users\/(\d+)(?:\/(enable|disable|password-reset|book-access\/(\d+)))?$/);
		if (userMatch) {
			if (!requireAdmin(req, res)) return;
			const userId = Number(userMatch[1]);
			const suffix = userMatch[2] ?? '';
			const bookId = Number(userMatch[3] ?? '0');
			if (method === 'GET' && userId === 404) return jsonResponse(res, 404, adminProblem('user_not_found'));
			if (method === 'GET' && userId === 500) return jsonResponse(res, 500, unknownProblem());
			const user = users.get(userId);
			if (!user) return jsonResponse(res, 404, adminProblem('user_not_found'));

			if (method === 'GET' && suffix === '') return jsonResponse(res, 200, userDetail(user));
			if (method === 'PATCH' && suffix === '') {
				const body = parseJson(await readBody(req));
				mutationBodies.push({ kind: 'display_name', body });
				const displayName = String(body.display_name ?? '');
				if (displayName.includes('bad-display')) return jsonResponse(res, 422, adminProblem('display_name_invalid'));
				if (displayName.includes('unknown-display')) return jsonResponse(res, 500, unknownProblem());
				user.display_name = displayName;
				user.updated_at = now(user.id + 5);
				return jsonResponse(res, 200, userDetail(user));
			}
			if (method === 'POST' && suffix === 'enable') {
				user.is_enabled = true;
				user.updated_at = now(user.id + 6);
				mutationBodies.push({ kind: 'enable', userId });
				return jsonResponse(res, 200, userDetail(user));
			}
			if (method === 'POST' && suffix === 'disable') {
				if (userId === 1) return jsonResponse(res, 409, adminProblem('last_enabled_admin'));
				user.is_enabled = false;
				user.updated_at = now(user.id + 7);
				mutationBodies.push({ kind: 'disable', userId });
				return jsonResponse(res, 200, userDetail(user));
			}
			if (method === 'POST' && suffix === 'password-reset') {
				const body = parseJson(await readBody(req));
				resetBodies.push(body);
				mutationBodies.push({ kind: 'password_reset', body });
				if (String(body.new_password ?? '').includes('session-change')) return jsonResponse(res, 401, adminProblem('session_changed'));
				return jsonResponse(res, 200, { status: 'password_reset', subject_user_id: userId, session_invalidated: true });
			}
			if (method === 'PUT' && suffix.startsWith('book-access/')) {
				const body = parseJson(await readBody(req));
				mutationBodies.push({ kind: 'grant', userId, bookId, body });
				const option = bookOptions.find((book) => book.id === bookId);
				if (!option) return jsonResponse(res, 400, adminProblem('book_not_assignable'));
				const role = ['owner', 'editor', 'viewer'].includes(String(body.role)) ? String(body.role) : 'viewer';
				const assignment = { book_id: option.id, book_name: option.name, is_default: option.is_default, role };
				user.assignments = user.assignments.filter((entry) => entry.book_id !== bookId).concat(assignment);
				user.updated_at = now(user.id + 8);
				return jsonResponse(res, 200, assignment);
			}
			if (method === 'DELETE' && suffix.startsWith('book-access/')) {
				mutationBodies.push({ kind: 'revoke', userId, bookId });
				user.assignments = user.assignments.filter((entry) => entry.book_id !== bookId);
				user.updated_at = now(user.id + 9);
				return jsonResponse(res, 200, null);
			}
		}

		return jsonResponse(res, 404, unknownProblem());
	}

	const server = createServer((req, res) => {
		void handler(req, res).catch((error) => {
			res.statusCode = 500;
			res.end(JSON.stringify({ error: String(error?.message ?? error) }));
		});
	});

	await new Promise((resolve, reject) => {
		server.once('error', reject);
		server.listen(0, '127.0.0.1', resolve);
	});
	const address = server.address();
	return {
		url: `http://127.0.0.1:${address.port}`,
		requests,
		forbiddenProductWriteRequests,
		normalUserForbiddenAttempts,
		createBodies,
		resetBodies,
		mutationBodies,
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

async function navigate(cdp, webBase, path, label, readyPath = path.split('?')[0]) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 30000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([
		load,
		waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(readyPath)}`, label, 30000)
	]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(readyPath)}`, label, 30000);
}

async function setSession(cdp, webBase, token, locale = 'en') {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: token, url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: locale, url: webBase, path: '/', sameSite: 'Lax' });
}

async function pageSnapshot(cdp) {
	return evaluate(cdp, `(() => ({
		pathname: location.pathname,
		search: location.search,
		bodyText: document.body?.innerText ?? '',
		html: document.documentElement?.outerHTML ?? '',
		forms: Array.from(document.forms).map((form) => ({ action: form.getAttribute('action') ?? '', method: form.getAttribute('method') ?? 'GET' })),
		links: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href') ?? ''),
		alerts: document.querySelectorAll('[role="alert"]').length,
		statuses: document.querySelectorAll('[role="status"], [aria-live]').length,
		adminNavLinks: document.querySelectorAll('header nav a[href="/admin/users"], nav[aria-label="Mobile navigation"] a[href="/admin/users"]').length,
		activeAdminNavLinks: document.querySelectorAll('a[href="/admin/users"][aria-current="page"][data-active-route="true"]').length,
		passwordValues: Array.from(document.querySelectorAll('input[type="password"]')).map((input) => input.value)
	}))()`);
}

function capturedMetadataText(snapshots, browserRequests, consoleMessages, apiRequests = []) {
	return [
		...snapshots.map((snapshot) => `${snapshot.bodyText}\n${snapshot.html}\n${snapshot.passwordValues.join('\n')}`),
		browserRequests.map((request) => `${request.method} ${request.url}`).join('\n'),
		consoleMessages.join('\n'),
		apiRequests.map((request) => `${request.method} ${request.pathWithSearch}`).join('\n')
	].join('\n---\n');
}

function sentinelLeakCounts(text) {
	return Object.fromEntries(leakSentinels.map((sentinel) => [sentinel, text.split(sentinel).length - 1]));
}

function assertNoSentinelLeaks(snapshots, browserRequests, consoleMessages, apiRequests, label) {
	const counts = sentinelLeakCounts(capturedMetadataText(snapshots, browserRequests, consoleMessages, apiRequests));
	assert.deepEqual(Object.values(counts).filter((count) => count !== 0), [], `${label}: secret/path/token sentinel leak counts must all be 0`);
}

function forbiddenBrowserProductWriteRequests(browserRequests) {
	return browserRequests.filter((request) => {
		const url = new URL(request.url);
		return isForbiddenProductWrite(request.method, url.pathname, url.search);
	});
}

async function pressTab(cdp) {
	await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
	await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
}

async function assertMobileAccessibility(cdp, label) {
	await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 320, deviceScaleFactor: 2, mobile: true });
	const state = await evaluate(cdp, `(() => {
		const root = document.documentElement;
		const body = document.body;
		const viewportWidth = window.innerWidth;
		const scrollWidth = Math.max(root?.scrollWidth ?? 0, body?.scrollWidth ?? 0);
		const controls = Array.from(document.querySelectorAll('a, button, select, textarea, input:not([type="hidden"])'));
		const rects = controls.map((el) => ({ tag: el.tagName, type: el.getAttribute('type') ?? '', text: el.textContent?.trim() || el.getAttribute('name') || '', rect: el.getBoundingClientRect() })).filter((item) => item.rect.width > 0 && item.rect.height > 0);
		const enabledControls = controls.filter((el) => !el.disabled && (el.matches('a[href], button, select, textarea, input') || el.tabIndex >= 0));
		const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), select, textarea'));
		const unlabeled = inputs.filter((el) => {
			const id = el.getAttribute('id');
			return !el.closest('label') && !(id && document.querySelector('label[for="' + CSS.escape(id) + '"]')) && !el.getAttribute('aria-label');
		}).map((el) => el.getAttribute('name') ?? el.tagName);
		return {
			viewportWidth,
			scrollWidth,
			shortTargets: rects.filter((item) => item.tag !== 'A' && item.type !== 'checkbox' && item.rect.height < 32).map((item) => item.text || item.tag),
			clippedTargets: rects.filter((item) => item.rect.left < -1 || item.rect.right > viewportWidth + 1).map((item) => item.text || item.tag),
			unlabeled,
			focusableCount: enabledControls.length,
			alertCount: document.querySelectorAll('[role="alert"]').length,
			statusCount: document.querySelectorAll('[role="status"], [aria-live]').length
		};
	})()`);
	assert.equal(state.viewportWidth, 320, `${label}: browser evidence must run at a 320px viewport`);
	assert.ok(state.scrollWidth <= state.viewportWidth, `${label}: document.scrollWidth must be <= innerWidth (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.deepEqual(state.clippedTargets, [], `${label}: controls must not be clipped at 320px`);
	assert.deepEqual(state.shortTargets, [], `${label}: visible non-link controls must not be clipped below 32px`);
	assert.deepEqual(state.unlabeled, [], `${label}: controls must have labels/accessible names`);
	assert.ok(state.focusableCount > 0, `${label}: page must expose keyboard-focusable controls`);
	await evaluate(cdp, `document.body.focus()`);
	const focusTrail = [];
	for (let i = 0; i < Math.min(4, state.focusableCount); i += 1) {
		await pressTab(cdp);
		focusTrail.push(await evaluate(cdp, `document.activeElement ? (document.activeElement.tagName + ':' + (document.activeElement.textContent || document.activeElement.getAttribute('name') || document.activeElement.getAttribute('aria-label') || '')) : ''`));
	}
	assert.ok(focusTrail.some((entry) => /^(A|BUTTON|INPUT|SELECT|TEXTAREA):/.test(entry)), `${label}: keyboard Tab traversal must reach an interactive control`);
	return state;
}

async function submitForm(cdp, action, values = {}, checked = {}, label = action) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 30000).catch(() => null);
	await evaluate(cdp, `(() => {
		const action = ${jsString(action)};
		const form = Array.from(document.forms).find((candidate) => candidate.getAttribute('action') === action);
		if (!form) throw new Error('Form not found: ' + action);
		const values = ${jsString(values)};
		const checked = ${jsString(checked)};
		for (const [name, value] of Object.entries(values)) {
			const field = form.elements.namedItem(name);
			if (!field) throw new Error('Field not found: ' + name);
			field.value = value;
			field.dispatchEvent(new Event('input', { bubbles: true }));
			field.dispatchEvent(new Event('change', { bubbles: true }));
		}
		for (const [name, value] of Object.entries(checked)) {
			const field = form.elements.namedItem(name);
			if (!field) throw new Error('Checkbox not found: ' + name);
			field.checked = value;
			field.dispatchEvent(new Event('change', { bubbles: true }));
		}
		form.requestSubmit();
		return true;
	})()`);
	await load;
	await waitForExpression(cdp, `document.readyState !== 'loading'`, label, 30000);
}

function requestsSince(api, start) {
	return api.requests.slice(start);
}

function assertNoAdminPayloadRequests(requests, label) {
	assert.deepEqual(requests.filter((request) => isAdminApiPath(request.path)), [], `${label}: normal user route must not call admin users/book-access backend APIs`);
}

async function assertNormalUserRoute(cdp, api, webBase, path, expectedPath = path.split('?')[0]) {
	const before = api.requests.length;
	await setSession(cdp, webBase, userToken, 'en');
	await navigate(cdp, webBase, path, `normal user ${path}`, expectedPath);
	const snapshot = await pageSnapshot(cdp);
	assert.match(snapshot.bodyText, /Administrator account required|intentionally withholds admin user and access payloads/, `${path}: normal user must see fixed admin-required copy`);
	assert.doesNotMatch(snapshot.bodyText, /synthetic_admin|synthetic_viewer|Synthetic Viewer|Book access matrix|RAW_SQL|password_hash/i, `${path}: normal user must not see admin payload data`);
	assert.equal(snapshot.adminNavLinks, 0, `${path}: normal user must not receive admin-users nav from server fixture`);
	assertNoAdminPayloadRequests(requestsSince(api, before), `normal user ${path}`);
	await assertMobileAccessibility(cdp, `normal user ${path}`);
	return snapshot;
}

async function assertNormalUserApiForbidden(apiUrl) {
	const attempts = [
		['GET', '/admin/users', undefined],
		['GET', '/admin/users/1', undefined],
		['GET', '/admin/book-access/books?limit=50&offset=0', undefined],
		['POST', '/admin/users', { username: 'normal_attempt', display_name: 'Normal Attempt', password: 'not-used', is_admin: false }],
		['PATCH', '/admin/users/1', { display_name: 'Normal Attempt' }],
		['POST', '/admin/users/1/disable', undefined],
		['POST', '/admin/users/1/password-reset', { new_password: 'not-used' }],
		['PUT', '/admin/users/1/book-access/1', { role: 'owner' }],
		['DELETE', '/admin/users/1/book-access/1', undefined]
	];
	for (const [method, path, body] of attempts) {
		const response = await fetch(`${apiUrl}${path}`, {
			method,
			headers: {
				authorization: `Bearer ${userToken}`,
				...(body ? { 'content-type': 'application/json' } : {})
			},
			body: body ? JSON.stringify(body) : undefined
		});
		assert.equal(response.status, 403, `normal-user direct API attempt must be 403: ${method} ${path}`);
	}
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the admin-users browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before admin-users browser smoke; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	mkdirSync(smokeTempRoot, { recursive: true });
	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	const profileDir = mkdtempSync(join(smokeTempRoot, 'admin-users-browser-'));
	let webProcess;
	let chromiumProcess;
	let cdp;
	const browserRequests = [];
	const consoleMessages = [];
	const snapshots = [];

	try {
		webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
			cwd: root,
			env: {
				...process.env,
				API_INTERNAL_URL: api.url,
				APP_ENV: 'test',
				GNUCASH_WRITES_ENABLED: 'false',
				JWT_SECRET: 'dummy-admin-users-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-admin-users-browser-smoke-password'
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
			'--window-size=320,320',
			'about:blank'
		], {
			cwd: root,
			env: { ...process.env, TMPDIR: smokeTempRoot, TMP: smokeTempRoot, TEMP: smokeTempRoot }
		});

		cdp = await connectCdp(debugPort);
		cdp.on('Network.requestWillBeSent', (params) => {
			browserRequests.push({ method: params.request.method, url: params.request.url });
		});
		cdp.on('Runtime.consoleAPICalled', (params) => {
			consoleMessages.push(params.args?.map((arg) => String(arg.value ?? arg.description ?? '')).join(' ') ?? '');
		});
		cdp.on('Log.entryAdded', (params) => {
			consoleMessages.push(params.entry?.text ?? '');
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Log.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 320, deviceScaleFactor: 2, mobile: true });

		await setSession(cdp, webBase, adminToken, 'en');
		await navigate(cdp, webBase, '/admin/users?limit=1&offset=0&state=all', 'admin users list');
		let snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /User and book access administration/, 'EN admin users list title must render');
		assert.match(snapshot.bodyText, /Synthetic Admin[\s\S]*synthetic_admin[\s\S]*Enabled/s, 'list must render bounded admin user summary and status');
		assert.ok(snapshot.links.some((href) => href.includes('/admin/users?limit=1&offset=1&state=all')), 'list must expose bounded next-page link');
		assert.ok(snapshot.adminNavLinks >= 1 && snapshot.activeAdminNavLinks >= 1, 'admin server isAdmin fixture must expose active admin-users nav');
		await assertMobileAccessibility(cdp, 'admin users list');

		await navigate(cdp, webBase, '/admin/users?limit=50&offset=100&state=all', 'admin users empty list');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /No local users returned/, 'empty list state must render');
		await assertMobileAccessibility(cdp, 'admin users empty list');

		await navigate(cdp, webBase, '/admin/users?limit=50&offset=0&state=disabled', 'admin users disabled filter');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Synthetic Viewer[\s\S]*Disabled[\s\S]*Enable user/s, 'disabled filter/status and list enable action must render');
		await submitForm(cdp, '?/enableUser', {}, {}, 'enable disabled user from list');
		await waitForExpression(cdp, `document.body.innerText.includes('User enabled.')`, 'list enable success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /User enabled\./, 'list enable success state must render');

		await navigate(cdp, webBase, '/admin/users/new', 'admin users create form');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Create local user[\s\S]*New users start with zero book access by default/s, 'create route/form and zero-access default must render');
		assert.deepEqual(snapshot.passwordValues, [''], 'create password field starts empty');
		await assertMobileAccessibility(cdp, 'admin users create form');

		await submitForm(cdp, '?/create', {
			username: 'browser_created',
			display_name: 'Browser Created',
			initial_password: exactCreatePassword
		}, { is_admin: false }, 'create user success');
		await waitForExpression(cdp, `location.pathname === '/admin/users/3' && document.body.innerText.includes('User created with zero book access by default.')`, 'create redirect success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.equal(api.createBodies.at(-1)?.password, exactCreatePassword, 'create action must submit exact password text');
		assert.match(snapshot.bodyText, /Browser Created[\s\S]*No book assignments for this user/s, 'created detail must show zero-access default');
		assert.deepEqual(snapshot.passwordValues, [''], 'created detail reset password field must be empty');
		assert.doesNotMatch(snapshot.html, new RegExp(exactCreatePassword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), 'create password must not serialize into redirected DOM');

		await navigate(cdp, webBase, '/admin/users/new', 'create duplicate error');
		await submitForm(cdp, '?/create', {
			username: 'taken_user',
			display_name: 'Taken User',
			initial_password: exactCreatePassword
		}, { is_admin: true }, 'duplicate create submit');
		await waitForExpression(cdp, `document.body.innerText.includes('A user with that normalized username already exists.')`, 'duplicate safe copy', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.equal(api.createBodies.at(-1)?.password, exactCreatePassword, 'failed create must still submit exact password text');
		assert.deepEqual(snapshot.passwordValues, [''], 'failed create must not repopulate password');
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy|JWT_SENTINEL/i, '409 create error must redact arbitrary backend body');

		await navigate(cdp, webBase, '/admin/users/new', 'create validation error');
		await submitForm(cdp, '?/create', {
			username: 'invalid_user',
			display_name: 'Invalid User',
			initial_password: exactCreatePassword
		}, {}, 'invalid create submit');
		await waitForExpression(cdp, `document.body.innerText.includes('Password does not meet the local policy.')`, '422 safe copy', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.deepEqual(snapshot.passwordValues, [''], '422 create must not repopulate password');

		await navigate(cdp, webBase, '/admin/users/3', 'admin user detail');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Book access matrix/, `detail route must render access matrix; body=${snapshot.bodyText.slice(0, 1200)}`);
		assert.match(snapshot.bodyText, /Viewer: read-only views only/, `detail route must render viewer read-only copy; body=${snapshot.bodyText.slice(0, 1200)}`);
		assert.match(snapshot.bodyText, /GNUCASH_WRITES_ENABLED=false/, `detail route must state no GnuCash writes; body=${snapshot.bodyText.slice(0, 1200)}`);
		assert.equal(await evaluate(cdp, `document.querySelector('select[name="role"]')?.value ?? ''`), 'viewer', 'new book grants must default to viewer');
		await assertMobileAccessibility(cdp, 'admin user detail');

		await submitForm(cdp, '?/updateDisplayName', { display_name: 'Browser Renamed' }, {}, 'update display name success');
		await waitForExpression(cdp, `document.body.innerText.includes('Display name updated.') && document.body.innerText.includes('Browser Renamed')`, 'display name update success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Display name updated\./, 'display name success state must render');

		await submitForm(cdp, '?/updateDisplayName', { display_name: 'bad-display' }, {}, 'update display name 422');
		await waitForExpression(cdp, `document.body.innerText.includes('Display name is missing or outside the allowed length/character policy.')`, 'display name 422 safe copy', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy/i, '422 update error must redact arbitrary backend body');

		await submitForm(cdp, '?/updateDisplayName', { display_name: 'unknown-display' }, {}, 'update display name unknown');
		await waitForExpression(cdp, `document.body.innerText.includes('The admin action failed safely. Unknown backend details were redacted.')`, 'unknown backend safe copy', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy|canonical_path/i, 'unknown update error must not render raw backend body');

		await submitForm(cdp, '?/disableUser', {}, { confirm_disable: true }, 'disable user success');
		await waitForExpression(cdp, `document.body.innerText.includes('User disabled.') && document.body.innerText.includes('Enable user')`, 'disable success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /User disabled\.[\s\S]*Enable user/s, 'disable confirmation and success state must render');

		await submitForm(cdp, '?/enableUser', {}, {}, 'enable user success');
		await waitForExpression(cdp, `document.body.innerText.includes('User enabled.') && document.body.innerText.includes('Disable user')`, 'enable success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /User enabled\.[\s\S]*Disable user/s, 'enable success state must render');

		await submitForm(cdp, '?/resetPassword', { new_password: exactResetPassword }, { confirm_reset: true }, 'reset password success');
		await waitForExpression(cdp, `document.body.innerText.includes('Password reset; existing sessions are invalidated on the next request.')`, 'reset success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.equal(api.resetBodies.at(-1)?.new_password, exactResetPassword, 'reset action must submit exact password text');
		assert.deepEqual(snapshot.passwordValues, [''], 'reset password field must not retain submitted password');

		await submitForm(cdp, '?/resetPassword', { new_password: 'session-change-password' }, { confirm_reset: true }, 'reset password 401');
		await waitForExpression(cdp, `document.body.innerText.includes('Session changed. Sign in again to continue.')`, 'reset 401 safe copy', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy|JWT_SENTINEL/i, '401 reset error must render fixed session_changed copy only');
		assert.deepEqual(snapshot.passwordValues, [''], '401 reset must not retain submitted password');

		await submitForm(cdp, '?/grantAccess', { book_id: '2', role: 'editor' }, {}, 'grant editor access');
		await waitForExpression(cdp, `document.body.innerText.includes('Book access granted or updated.') && document.body.innerText.includes('Synthetic Reports Access Book')`, 'grant success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Book access granted or updated\.[\s\S]*Editor[\s\S]*no GnuCash writes are enabled/s, 'grant success must show editor app-metadata-only copy');
		assert.deepEqual(api.mutationBodies.filter((entry) => entry.kind === 'grant').at(-1)?.body, { role: 'editor' }, 'grant action must submit bounded role only');

		await submitForm(cdp, '?/revokeAccess', {}, { confirm_revoke: true }, 'revoke access');
		await waitForExpression(cdp, `document.body.innerText.includes('Book access revoked.') && document.body.innerText.includes('No book assignments for this user.')`, 'revoke success', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Book access revoked\.[\s\S]*No book assignments for this user\./s, 'revoke confirmation and success state must render');

		await navigate(cdp, webBase, '/admin/users/404', 'detail 404 safe');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /The requested user was not found\./, '404 detail must render fixed not-found copy');
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy/i, '404 detail must redact raw backend body');

		await navigate(cdp, webBase, '/admin/users/500', 'detail unknown safe');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Admin API is unavailable\. No raw backend details were shown\./, 'unknown detail load failure must render fixed safe copy');
		assert.doesNotMatch(snapshot.bodyText, /RAW_SQL|PASSWORD_HASH|Syncthing|only-copy|canonical_path/i, 'unknown detail failure must redact raw backend body');

		await setSession(cdp, webBase, adminToken, 'ru');
		await navigate(cdp, webBase, '/admin/users/new', 'RU admin users create');
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.match(snapshot.bodyText, /Создать локального user[\s\S]*Новые users начинают с нулевым доступом/s, 'RU create route must render localized key copy');
		await assertMobileAccessibility(cdp, 'RU admin users create');

		await assertNormalUserRoute(cdp, api, webBase, '/admin/users');
		await assertNormalUserRoute(cdp, api, webBase, '/admin/users/new');
		await assertNormalUserRoute(cdp, api, webBase, '/admin/users/3');
		await assertNormalUserApiForbidden(api.url);

		const beforeExpired = api.requests.length;
		await setSession(cdp, webBase, expiredToken, 'en');
		const expiredLoad = waitForCdpEvent(cdp, 'Page.loadEventFired', 'expired session safe state', 30000).catch(() => null);
		await cdp.send('Page.navigate', { url: `${webBase}/admin/users` });
		await expiredLoad;
		await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === '/login'`, 'expired session redirects to login', 30000);
		snapshot = await pageSnapshot(cdp);
		snapshots.push(snapshot);
		assert.equal(snapshot.pathname, '/login', `expired 401 session must redirect to the fixed login page; body=${snapshot.bodyText.slice(0, 800)}`);
		assert.match(snapshot.bodyText, /Sign in[\s\S]*Use the configured admin account to continue\./, `expired 401 login page must render fixed sign-in copy; body=${snapshot.bodyText.slice(0, 800)}`);
		assert.doesNotMatch(snapshot.bodyText, /Something went wrong|Admin API is unavailable|RAW_SQL|PASSWORD_HASH|Syncthing|only-copy|JWT_SENTINEL|canonical_path/i, 'expired 401 login state must reject generic errors, raw backend details, and sentinels');
		assertNoAdminPayloadRequests(requestsSince(api, beforeExpired), 'expired 401 session');

		assert.deepEqual(api.forbiddenProductWriteRequests, [], 'synthetic API must observe zero product/GnuCash write-capable requests');
		assert.deepEqual(forbiddenBrowserProductWriteRequests(browserRequests), [], 'browser must observe zero product/GnuCash write-capable requests');
		assertNoSentinelLeaks(snapshots, browserRequests, consoleMessages, api.requests, 'admin users browser smoke');

		console.log(`admin users browser smoke passed: scenarios=list-empty-pagination-status-create-detail-update-enable-disable-reset-grant-revoke errors=401/403/404/409/422/unknown expired_session_path=${snapshot.pathname} expired_session_copy=sign_in expired_admin_payload_calls=0 normal_user_admin_api_calls=0 product_write_calls=${api.forbiddenProductWriteRequests.length} browser_product_write_calls=${forbiddenBrowserProductWriteRequests(browserRequests).length} secret_sentinel_leaks=0 viewport_width=320 gnucash_writes_enabled=false`);
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
