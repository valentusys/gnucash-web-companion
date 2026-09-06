import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import {
	existsSync,
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	statSync,
	writeFileSync
} from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(root, '.svelte-kit', 'output', 'server', 'index.js');
const smokeHome = process.env.BOOKS_ONBOARDING_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.BOOKS_ONBOARDING_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-books-onboarding');
const adminToken = 'synthetic-books-admin-token';
const userToken = 'synthetic-books-user-token';
const privateRawPath = '/redacted-test-source/source-book.gnucash.sqlite';
const backendSentinel = 'BACKEND_ARBITRARY_BOOK_PATH_SENTINEL';
const maliciousNotice = '<script>backend-arbitrary-notice</script>';
const cdpCommandTimeoutMs = Number(process.env.BOOKS_ONBOARDING_CDP_TIMEOUT_MS ?? '120000');

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
			if (body.length > 1_000_000) {
				reject(new Error('Synthetic books API request body too large'));
				req.destroy();
			}
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
	const match = String(header).match(/^Bearer\s+(.+)$/i);
	return match?.[1] ?? '';
}

function isAdminToken(token) {
	return token === adminToken;
}

function fixedProblem(code) {
	return {
		safe_code: code,
		safe_message: `${backendSentinel}: ${privateRawPath}`,
		detail: `${backendSentinel}: ${privateRawPath}`
	};
}

function sectionStatus(status, safeCode) {
	return {
		status,
		safe_code: safeCode,
		message: null,
		retryable: status !== 'ready' && status !== 'available' && status !== 'ok'
	};
}

function capabilities(openable, canRegister = false) {
	return {
		read_only: true,
		can_register_metadata: canRegister,
		can_open_accounts: openable,
		can_open_transactions: openable,
		can_open_reports: openable,
		can_upload: false,
		can_edit: false,
		can_delete: false,
		can_edit_gnucash: false,
		can_delete_source: false
	};
}

function preflightResponse(token, options = {}) {
	const duplicate = options.duplicate === true;
	const rejected = options.rejected === true;
	return {
		status: rejected ? 'rejected' : 'ready',
		format: 'gnucash_sqlite',
		preflight_token: token,
		registration_status: duplicate
			? sectionStatus('unavailable', 'already_registered')
			: sectionStatus('available', 'registration_available'),
		source_status: rejected ? sectionStatus('rejected', options.safeCode ?? 'open_failed') : sectionStatus('ready', 'source_ready'),
		open_status: rejected ? sectionStatus('rejected', options.safeCode ?? 'open_failed') : sectionStatus('ready', 'open_ready'),
		accounts: rejected ? sectionStatus('unavailable', 'accounts_ready') : sectionStatus('ready', 'accounts_ready'),
		transactions: rejected ? sectionStatus('unavailable', 'transactions_ready') : sectionStatus('ready', 'transactions_ready'),
		reports: rejected ? sectionStatus('unavailable', 'reports_ready') : sectionStatus('ready', 'reports_ready'),
		capabilities: capabilities(!rejected, !duplicate && !rejected),
		checked_at: '2026-07-15T08:00:00Z',
		safe_code: duplicate ? 'already_registered' : rejected ? (options.safeCode ?? 'open_failed') : 'ready',
		message: null,
		read_counters: {
			source_opens_readonly: 1,
			source_write_opens: 0,
			mutation_capable_requests: 0
		}
	};
}

function bookFixture(overrides = {}) {
	const enabled = overrides.is_enabled !== false;
	const failed = overrides.failed === true;
	const openable = enabled && !failed;
	const id = overrides.id;
	return {
		id,
		name: overrides.name ?? `Synthetic Book ${id}`,
		storage_type: 'sqlite',
		base_currency: overrides.base_currency ?? 'SEK',
		is_default: overrides.is_default === true,
		is_enabled: enabled,
		is_archived: false,
		created_at: '2026-07-15T08:00:00Z',
		updated_at: '2026-07-15T08:00:00Z',
		access_role: 'owner',
		access_role_label: 'Owner',
		access_role_description: 'Synthetic owner access for books onboarding browser smoke only.',
		read_only: true,
		status: failed ? 'failed' : enabled ? 'available' : 'disabled',
		status_severity: failed ? 'action_required' : 'ok',
		access_status: 'owner',
		can_open_read_only_views: openable,
		health: {
			status: failed ? 'failed' : enabled ? 'ready' : 'disabled',
			safe_code: failed ? 'open_failed' : enabled ? 'ready' : 'book_not_enabled',
			checked_at: '2026-07-15T08:00:00Z',
			last_successful_at: failed ? null : '2026-07-15T08:00:00Z',
			source_status: failed ? 'failed' : enabled ? 'ready' : 'disabled',
			open_status: failed ? 'failed' : enabled ? 'ready' : 'disabled',
			accounts_status: failed ? 'unavailable' : enabled ? 'ready' : 'disabled',
			transactions_status: failed ? 'unavailable' : enabled ? 'ready' : 'disabled',
			reports_status: failed ? 'unavailable' : enabled ? 'ready' : 'disabled'
		},
		capabilities: capabilities(openable, false),
		storage_diagnostics: {
			status: failed ? 'missing_file' : enabled ? 'available' : 'not_configured',
			configured: true,
			checked: true,
			safe_summary: failed
				? 'Synthetic failed book safe summary; no private path is included.'
				: 'Synthetic registered book safe summary; private path redacted.',
			safe_next_actions: []
		},
		management_actions: overrides.management_actions ?? (enabled
			? ['rename', 'disable', 'recheck', 'remove_from_registry', 'set_default']
			: ['rename', 'enable', 'recheck', 'remove_from_registry']),
		operator_guidance: {
			metadata_source: 'synthetic',
			data_access: 'stubbed',
			read_only_default: true,
			private_path_redacted: true,
			storage_type_label: 'Synthetic SQLite',
			unsupported_management_actions: [],
			message: 'Synthetic local books onboarding smoke fixture; no private book is used.'
		}
	};
}

function accountExplorerPayload(bookId) {
	return {
		book_id: bookId,
		mode: 'tree',
		normalized_filters: { query: null, types: [], hidden: 'active', placeholder: 'all' },
		root_ids: ['assets-root'],
		nodes: [
			{
				id: `book-${bookId}-checking`,
				source_parent_id: null,
				parent_id: null,
				root_id: 'assets-root',
				path: [{ id: `book-${bookId}-checking`, name: 'Synthetic Checking' }],
				full_path: 'Assets:Synthetic Checking',
				depth: 0,
				name: 'Synthetic Checking',
				type: 'ASSET',
				commodity: { namespace: 'CURRENCY', mnemonic: 'SEK' },
				hidden: false,
				placeholder: false,
				child_count: 0,
				direct_balance: { amount: '10.00', commodity: { namespace: 'CURRENCY', mnemonic: 'SEK' } },
				recursive_balances: [{ amount: '10.00', commodity: { namespace: 'CURRENCY', mnemonic: 'SEK' } }],
				match_state: 'match'
			}
		],
		returned_count: 1,
		scan: {
			candidate_accounts: 1,
			returned_nodes: 1,
			split_rows: 0,
			split_aggregate_rows: 0,
			query_count: 1,
			rollup_bucket_cells: 1,
			serialized_bytes: 512,
			exhausted: true,
			limits: {}
		},
		balance_basis: 'native_commodity_account_natural_sign',
		includes_currency_conversion: false,
		limitations: []
	};
}

function accountOptions(bookId) {
	const items = [{
		id: `book-${bookId}-checking`,
		parent_id: null,
		name: 'Synthetic Checking',
		display_name: 'Synthetic Checking',
		full_name: 'Assets:Synthetic Checking',
		type: 'ASSET',
		commodity: { namespace: 'CURRENCY', mnemonic: 'SEK' },
		currency: 'SEK',
		placeholder: false,
		hidden: false,
		selectable: true
	}];
	return {
		book_id: bookId,
		purpose: 'transactions_filter',
		normalized_filters: { query: null, currency: 'SEK', cursor: null },
		items,
		limit: 200,
		returned_count: items.length,
		next_cursor: null,
		partial_failure: false,
		error_code: null,
		scan: {
			candidate_accounts: items.length,
			matched_accounts: items.length,
			returned_items: items.length,
			query_count: 1,
			serialized_bytes: 1024,
			exhausted: true,
			limits: { max_items: 200 }
		},
		balance_basis: 'not_loaded',
		includes_currency_conversion: false,
		limitations: []
	};
}

function isForbiddenGnuCashMutation(method, pathname, search = '') {
	const upper = method.toUpperCase();
	if (!['POST', 'PATCH', 'PUT', 'DELETE'].includes(upper)) return false;
	const target = `${pathname}${search}`;
	return /(?:\/|%2F)(?:transactions|accounts|reports|backups?|audit|write-alpha|owner-writebeta)(?:\/|$|[?&=])/i.test(target)
		|| /(?:\/|%2F|[?&=])(?:create-preview|validate|batch|splits|commodities)(?:\/|%2F|$|[?&=])/i.test(target);
}

async function startSyntheticApi(sourcePaths) {
	const requests = [];
	const forbiddenGnuCashMutationRequests = [];
	const lifecycleRequests = [];
	const normalUserForbiddenAttempts = [];
	const sourceOpenModes = [];
	const preflights = new Map();
	const sourceByBook = new Map();
	const state = {
		books: [],
		nextId: 1,
		registerRequestBodies: [],
		preflightRequestBodies: []
	};

	function addBook({ sourcePath, name, baseCurrency = 'SEK', isDefault = false, isEnabled = true, failed = false }) {
		if (isDefault) {
			for (const book of state.books) book.is_default = false;
		}
		const id = state.nextId++;
		const book = bookFixture({ id, name, base_currency: baseCurrency, is_default: isDefault, is_enabled: isEnabled, failed });
		if (!state.books.length && !failed) book.is_default = true;
		state.books.push(book);
		sourceByBook.set(id, sourcePath);
		return book;
	}

	function findBook(id) {
		return state.books.find((book) => book.id === id) ?? null;
	}

	function requireAdmin(req, res) {
		if (isAdminToken(bearerToken(req))) return true;
		normalUserForbiddenAttempts.push({ method: req.method, path: new URL(req.url ?? '/', 'http://127.0.0.1').pathname });
		jsonResponse(res, 403, fixedProblem('admin_required'));
		return false;
	}

	function classifyPreflightPath(pathValue) {
		const path = String(pathValue ?? '');
		if (!path || path.includes('..')) return 'invalid_path';
		if (path.includes('outside-root')) return 'outside_allowed_roots';
		if (path.includes('symlink')) return 'symlink_forbidden';
		if (path.includes('missing')) return 'missing_file';
		if (path.includes('unavailable')) return 'permission_denied';
		if (path.includes('unsupported')) return 'unsupported_source';
		if (path.includes('not-regular')) return 'not_regular_file';
		if (path.includes('schema')) return 'invalid_gnucash_schema';
		if (path.includes('error')) return 'open_failed';
		if (!sourcePaths.includes(path)) return 'outside_allowed_roots';
		return null;
	}

	function isDuplicatePreflight(body) {
		const path = String(body.uri_or_path ?? '');
		const matchingBook = [...sourceByBook.entries()].find(([, source]) => source === path);
		if (!matchingBook) return false;
		const book = findBook(matchingBook[0]);
		return !(book && book.is_enabled === false && book.name === body.name);
	}

	function rememberPreflight(body, duplicate = false) {
		const token = `synthetic-preflight-${preflights.size + 1}`;
		preflights.set(token, {
			name: body.name,
			uri_or_path: body.uri_or_path,
			base_currency: body.base_currency,
			make_default: body.make_default === true,
			duplicate
		});
		return token;
	}

	async function handler(req, res) {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		const method = req.method ?? 'GET';
		requests.push({ method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });

		if (isForbiddenGnuCashMutation(method, url.pathname, url.search)) {
			forbiddenGnuCashMutationRequests.push({ method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, fixedProblem('book_registry_failed'));
		}

		if (method === 'GET' && url.pathname === '/health') {
			return jsonResponse(res, 200, { status: 'ok', first_run: null });
		}
		if (method === 'GET' && url.pathname === '/auth/me') {
			const admin = isAdminToken(bearerToken(req));
			return jsonResponse(res, 200, {
				id: admin ? 1 : 2,
				username: admin ? 'admin' : 'viewer',
				display_name: admin ? 'Synthetic Admin' : 'Synthetic Viewer',
				is_admin: admin
			});
		}
		if (method === 'GET' && url.pathname === '/books') {
			return jsonResponse(res, 200, state.books);
		}

		if (method === 'POST' && url.pathname === '/books/preflight') {
			if (!requireAdmin(req, res)) return;
			const body = parseJson(await readBody(req));
			state.preflightRequestBodies.push(body);
			sourceOpenModes.push({ operation: 'preflight', mode: 'readonly', path: body.uri_or_path });
			const problem = classifyPreflightPath(body.uri_or_path);
			if (problem) {
				return jsonResponse(res, 400, fixedProblem(problem));
			}
			const duplicate = isDuplicatePreflight(body);
			const token = rememberPreflight(body, duplicate);
			return jsonResponse(res, 200, preflightResponse(token, { duplicate }));
		}

		if (method === 'POST' && url.pathname === '/books') {
			if (!requireAdmin(req, res)) return;
			const body = parseJson(await readBody(req));
			state.registerRequestBodies.push(body);
			const remembered = preflights.get(String(body.preflight_token ?? ''));
			if (!remembered || remembered.duplicate) {
				return jsonResponse(res, 400, fixedProblem(remembered?.duplicate ? 'duplicate_canonical_path' : 'invalid_preflight_token'));
			}
			for (const key of ['name', 'uri_or_path', 'base_currency']) {
				if (String(body[key] ?? '') !== String(remembered[key] ?? '')) {
					return jsonResponse(res, 400, fixedProblem('preflight_request_mismatch'));
				}
			}
			if ((body.make_default === true) !== remembered.make_default) {
				return jsonResponse(res, 400, fixedProblem('preflight_request_mismatch'));
			}
			lifecycleRequests.push({ kind: 'register_metadata', path: url.pathname });
			const book = addBook({
				sourcePath: body.uri_or_path,
				name: body.name,
				baseCurrency: body.base_currency,
				isDefault: body.make_default === true
			});
			return jsonResponse(res, 200, book);
		}

		const bookMatch = url.pathname.match(/^\/books\/(\d+)(?:\/(.+))?$/);
		if (bookMatch) {
			const bookId = Number(bookMatch[1]);
			const suffix = bookMatch[2] ?? '';
			const book = findBook(bookId);
			if (!book) return jsonResponse(res, 404, fixedProblem('unknown_book_problem'));

			if (method === 'GET' && suffix === '') return jsonResponse(res, 200, book);
			if (method === 'GET' && suffix === 'accounts/options') return jsonResponse(res, 200, accountOptions(bookId));
			if (method === 'GET' && suffix === 'accounts') return jsonResponse(res, 410, fixedProblem('unknown_book_problem'));
			if (method === 'GET' && suffix === 'accounts/explorer') return jsonResponse(res, 200, accountExplorerPayload(bookId));
			if (method === 'GET' && suffix === 'reports/reporting-date') return jsonResponse(res, 200, { as_of_date: '2026-07-15' });
			if (method === 'GET' && suffix === 'reports/comparison') return jsonResponse(res, 500, fixedProblem('unknown_book_problem'));

			if (method === 'PATCH' && suffix === '') {
				if (!requireAdmin(req, res)) return;
				const body = parseJson(await readBody(req));
				book.name = String(body.name ?? book.name);
				book.base_currency = String(body.base_currency ?? book.base_currency).toUpperCase();
				book.updated_at = '2026-07-15T08:05:00Z';
				lifecycleRequests.push({ kind: 'patch_metadata', path: url.pathname });
				return jsonResponse(res, 200, book);
			}
			if (method === 'POST' && suffix === 'default') {
				if (!requireAdmin(req, res)) return;
				for (const item of state.books) item.is_default = item.id === bookId;
				lifecycleRequests.push({ kind: 'set_default_metadata', path: url.pathname });
				return jsonResponse(res, 200, book);
			}
			if (method === 'POST' && suffix === 'health/recheck') {
				if (!requireAdmin(req, res)) return;
				sourceOpenModes.push({ operation: 'recheck', mode: 'readonly', path: sourceByBook.get(bookId) });
				book.health = { ...book.health, checked_at: '2026-07-15T08:10:00Z', last_successful_at: '2026-07-15T08:10:00Z' };
				lifecycleRequests.push({ kind: 'recheck_readonly', path: url.pathname });
				return jsonResponse(res, 200, book);
			}
			if (method === 'POST' && suffix === 'disable') {
				if (!requireAdmin(req, res)) return;
				book.is_enabled = false;
				book.can_open_read_only_views = false;
				book.status = 'disabled';
				book.health = { ...book.health, status: 'disabled', safe_code: 'book_not_enabled' };
				book.capabilities = capabilities(false, false);
				book.management_actions = ['rename', 'enable', 'recheck', 'remove_from_registry'];
				lifecycleRequests.push({ kind: 'disable_metadata', path: url.pathname });
				return jsonResponse(res, 200, book);
			}
			if (method === 'POST' && suffix === 'enable') {
				if (!requireAdmin(req, res)) return;
				const body = parseJson(await readBody(req));
				const remembered = preflights.get(String(body.preflight_token ?? ''));
				if (!remembered || remembered.uri_or_path !== sourceByBook.get(bookId)) {
					return jsonResponse(res, 400, fixedProblem('invalid_preflight_token'));
				}
				book.is_enabled = true;
				book.can_open_read_only_views = true;
				book.status = 'available';
				book.health = {
					...book.health,
					status: 'ready',
					safe_code: 'ready',
					source_status: 'ready',
					open_status: 'ready',
					accounts_status: 'ready',
					transactions_status: 'ready',
					reports_status: 'ready'
				};
				book.capabilities = capabilities(true, false);
				book.management_actions = ['rename', 'disable', 'recheck', 'remove_from_registry', 'set_default'];
				if (body.make_default === true) {
					for (const item of state.books) item.is_default = item.id === bookId;
				}
				lifecycleRequests.push({ kind: 'enable_metadata', path: url.pathname });
				return jsonResponse(res, 200, book);
			}
			if (method === 'DELETE' && suffix === '') {
				if (!requireAdmin(req, res)) return;
				const index = state.books.findIndex((item) => item.id === bookId);
				if (index >= 0) state.books.splice(index, 1);
				sourceByBook.delete(bookId);
				lifecycleRequests.push({ kind: 'delete_metadata_only', path: url.pathname });
				return jsonResponse(res, 200, { removed: true });
			}
		}

		return jsonResponse(res, 404, fixedProblem('unknown_book_problem'));
	}

	const server = createServer((req, res) => {
		handler(req, res).catch((error) => {
			jsonResponse(res, 500, { detail: `${backendSentinel}: ${error.message}` });
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
		forbiddenGnuCashMutationRequests,
		lifecycleRequests,
		normalUserForbiddenAttempts,
		sourceOpenModes,
		state,
		addBook,
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
			output = output.slice(-16000);
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

async function waitForExpression(cdp, expression, label, timeoutMs = 20000) {
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

async function setSession(cdp, webBase, token, locale = 'en', selectedBookId = null) {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: token, url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: locale, url: webBase, path: '/', sameSite: 'Lax' });
	if (selectedBookId !== null) {
		await cdp.send('Network.setCookie', { name: 'selected_book_id', value: String(selectedBookId), url: webBase, path: '/', sameSite: 'Lax' });
	}
}

async function selectedBookCookie(cdp, webBase) {
	const cookies = await cdp.send('Network.getCookies', { urls: [webBase] });
	return cookies.cookies.find((cookie) => cookie.name === 'selected_book_id')?.value ?? null;
}

function forbiddenBrowserMutationRequests(browserRequests) {
	return browserRequests.filter((request) => {
		const url = new URL(request.url);
		if (!['POST', 'PATCH', 'PUT', 'DELETE'].includes(request.method)) return false;
		if (url.pathname.startsWith('/login')) return false;
		return isForbiddenGnuCashMutation(request.method, url.pathname, url.search);
	});
}

function browserUploadOrFilesystemRequests(browserRequests) {
	return browserRequests.filter((request) => /^(file|blob):/i.test(request.url) || /upload|filesystem/i.test(request.url));
}

function assertNoPrivateLeak(text, label, sourcePaths = []) {
	for (const value of [privateRawPath, backendSentinel, maliciousNotice, ...sourcePaths]) {
		assert.ok(!text.includes(value), `${label}: private/backend value leaked: ${value}`);
	}
}

async function pageSnapshot(cdp) {
	return evaluate(cdp, `(() => ({
		pathname: location.pathname,
		search: location.search,
		bodyText: document.body?.innerText ?? '',
		html: document.documentElement?.outerHTML ?? '',
		forms: Array.from(document.forms).map((form) => form.getAttribute('action') ?? ''),
		links: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href') ?? ''),
		alerts: document.querySelectorAll('[role="alert"]').length,
		statuses: document.querySelectorAll('[role="status"], [aria-live]').length
	}))()`);
}

async function assertMobileAccessibility(cdp, label) {
	const state = await evaluate(cdp, `(() => {
		const root = document.documentElement;
		const body = document.body;
		const viewportWidth = window.innerWidth;
		const scrollWidth = Math.max(root?.scrollWidth ?? 0, body?.scrollWidth ?? 0);
		const controls = Array.from(document.querySelectorAll('a, button, select, textarea, input:not([type="hidden"]):not([type="checkbox"])'));
		const rects = controls.map((el) => ({ tag: el.tagName, text: el.textContent?.trim() ?? el.getAttribute('name') ?? '', rect: el.getBoundingClientRect() })).filter((item) => item.rect.width > 0 && item.rect.height > 0);
		const enabledControls = controls.filter((el) => !el.disabled && (el.matches('a[href], button, select, textarea, input') || el.tabIndex >= 0));
		const firstFocusable = enabledControls[0];
		firstFocusable?.focus();
		const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), select, textarea'));
		const unlabeled = inputs.filter((el) => {
			const id = el.getAttribute('id');
			return !el.closest('label') && !(id && document.querySelector('label[for="' + CSS.escape(id) + '"]')) && !el.getAttribute('aria-label');
		}).map((el) => el.getAttribute('name') ?? el.tagName);
		return {
			viewportWidth,
			scrollWidth,
			shortTargets: rects.filter((item) => item.tag !== 'A' && item.rect.height < 32).map((item) => item.text || item.tag),
			clippedTargets: rects.filter((item) => item.rect.left < -1 || item.rect.right > viewportWidth + 1).map((item) => item.text || item.tag),
			unlabeled,
			focusedTag: firstFocusable?.tagName ?? '',
			focusableCount: enabledControls.length,
			formCount: document.forms.length
		};
	})()`);
	assert.equal(state.viewportWidth, 320, `${label}: browser evidence must run at a 320px viewport`);
	assert.ok(state.scrollWidth <= state.viewportWidth + 8, `${label}: 320px viewport must not overflow horizontally (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.deepEqual(state.clippedTargets, [], `${label}: controls must not be clipped at 320px`);
	assert.deepEqual(state.shortTargets, [], `${label}: visible non-checkbox controls must not be clipped below 32px`);
	assert.deepEqual(state.unlabeled, [], `${label}: forms must have labels/accessible names`);
	assert.ok(state.focusableCount > 0 && ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(state.focusedTag), `${label}: page must expose keyboard-focusable controls`);
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

async function postAppForm(cdp, path, fields = {}) {
	return evaluate(cdp, `(() => {
		const fields = ${jsString(fields)};
		const form = new FormData();
		for (const [key, value] of Object.entries(fields)) form.append(key, value);
		return fetch(${jsString(path)}, { method: 'POST', body: form }).then(async (response) => ({
			status: response.status,
			text: (await response.text()).slice(0, 2000)
		}));
	})()`, { awaitPromise: true });
}

function fileEvidence(path) {
	const stat = statSync(path);
	return {
		size: stat.size,
		mtimeMs: stat.mtimeMs,
		sha256: createHash('sha256').update(readFileSync(path)).digest('hex')
	};
}

function assertNoSqliteSidecars(path, label) {
	for (const suffix of ['-journal', '-wal', '-shm']) {
		assert.ok(!existsSync(`${path}${suffix}`), `${label}: SQLite sidecar must not exist: ${path}${suffix}`);
	}
}

async function assertNormalUserApiForbidden(apiUrl) {
	const attempts = [
		['POST', '/books/preflight', { name: 'Nope', uri_or_path: '/data/books/nope.sqlite', storage_type: 'sqlite', base_currency: 'SEK', make_default: false }],
		['POST', '/books', { name: 'Nope', uri_or_path: '/data/books/nope.sqlite', storage_type: 'sqlite', base_currency: 'SEK', make_default: false, preflight_token: 'x' }],
		['PATCH', '/books/1', { name: 'Nope', base_currency: 'SEK' }],
		['POST', '/books/1/default', undefined],
		['POST', '/books/1/disable', undefined],
		['POST', '/books/1/enable', { preflight_token: 'x', make_default: false }],
		['DELETE', '/books/1', undefined],
		['POST', '/books/1/health/recheck', undefined]
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
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the books onboarding browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before browser smoke; run npm run build before npm run test:books-onboarding-browser');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	mkdirSync(smokeTempRoot, { recursive: true });
	const sourceDir = mkdtempSync(join(smokeTempRoot, 'source-books-'));
	const sourcePath = join(sourceDir, 'safe-onboarding-book.gnucash.sqlite');
	const secondSourcePath = join(sourceDir, 'second-safe-onboarding-book.gnucash.sqlite');
	writeFileSync(sourcePath, 'synthetic sqlite book bytes for metadata-only onboarding smoke\n');
	writeFileSync(secondSourcePath, 'second synthetic sqlite book bytes for metadata-only onboarding smoke\n');
	const beforeSource = fileEvidence(sourcePath);
	const beforeSecondSource = fileEvidence(secondSourcePath);

	const api = await startSyntheticApi([sourcePath, secondSourcePath]);
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	const profileDir = mkdtempSync(join(smokeTempRoot, 'books-onboarding-browser-'));
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
				JWT_SECRET: 'dummy-books-onboarding-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-books-onboarding-browser-smoke-password'
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
			'--window-size=320,840',
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
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 840, deviceScaleFactor: 2, mobile: true });

		await setSession(cdp, webBase, adminToken, 'en');
		await navigate(cdp, webBase, '/books', 'admin no-books first run');
		let snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /No books are registered yet/, 'admin empty books page must show first-run title');
		assert.ok(snapshot.links.includes('/books/new'), 'admin empty books page must expose Add book CTA');
		assert.doesNotMatch(snapshot.bodyText, /Dashboard section unavailable|dead dashboard/i, 'admin no-books state must not dead-end into dashboard copy');
		await assertMobileAccessibility(cdp, 'admin /books no-books');

		await setSession(cdp, webBase, userToken, 'en');
		await navigate(cdp, webBase, '/books', 'normal user no-books first run');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /No book is assigned to this account/, 'normal user empty books page must show assigned-book message');
		assert.match(snapshot.bodyText, /administrator must register or assign a book/i, 'normal user empty state must ask an administrator');
		assert.ok(!snapshot.links.includes('/books/new'), 'normal user no-books page must not expose Add book CTA');
		assertNoPrivateLeak(snapshot.html, 'normal user no-books serialized page data', [sourcePath, secondSourcePath]);
		await assertMobileAccessibility(cdp, 'normal user /books no-books');

		await setSession(cdp, webBase, adminToken, 'en');
		await navigate(cdp, webBase, `/books?book_context=${encodeURIComponent(maliciousNotice)}&manage_success=${encodeURIComponent(maliciousNotice)}`, 'safe URL notices');
		snapshot = await pageSnapshot(cdp);
		assertNoPrivateLeak(snapshot.html, 'books URL-backed notices');
		assert.ok(!snapshot.bodyText.includes('backend-arbitrary-notice'), 'URL-backed notices must not reflect arbitrary input');

		await navigate(cdp, webBase, '/books/new', 'admin add book');
		await assertMobileAccessibility(cdp, 'admin /books/new initial');
		const invalidConfirmResponse = await postAppForm(cdp, '/books/new?/confirm', {
			name: 'Invalid Direct Confirm',
			mounted_path: sourcePath,
			base_currency: 'SEK',
			preflight_token: 'invalid-token'
		});
		assert.ok([200, 400].includes(invalidConfirmResponse.status), 'invalid direct confirm without ready token must return a handled action response');
		assert.equal(api.state.registerRequestBodies.length, 1, 'invalid direct confirm may reach metadata route once');
		assert.equal(api.lifecycleRequests.filter((request) => request.kind === 'register_metadata').length, 0, 'invalid direct confirm must not register metadata');

		await navigate(cdp, webBase, '/books/new', 'ready preflight page');
		await submitForm(cdp, '?/preflight', {
			name: 'Synthetic Onboarding Book',
			mounted_path: sourcePath,
			base_currency: 'sek'
		}, { make_default: true }, 'ready preflight');
		await waitForExpression(cdp, `document.body.innerText.includes('Preflight is ready') && document.body.innerText.includes('Confirm metadata registration')`, 'ready preflight preview', 30000);
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Registration has not happened yet/, 'ready preflight preview must state registration has not happened');
		assert.match(snapshot.bodyText, /Source ready|Accounts ready|Transactions ready|Reports ready/, 'ready preflight preview must show typed checklist statuses');
		assertNoPrivateLeak(snapshot.bodyText, 'ready preflight safe preview');
		assert.equal(api.lifecycleRequests.filter((request) => request.kind === 'register_metadata').length, 0, 'preflight must not register metadata');
		const readyPreflightBody = api.state.preflightRequestBodies.at(-1);
		assert.equal(readyPreflightBody.uri_or_path, sourcePath, 'preflight must submit the explicit server-side path exactly');
		assert.equal(readyPreflightBody.base_currency, 'SEK', 'preflight must normalize base currency before API submission');
		await assertMobileAccessibility(cdp, 'ready preflight /books/new');

		await submitForm(cdp, '?/confirm', {}, {}, 'confirm registration');
		await waitForExpression(cdp, `document.body.innerText.includes('Book metadata registered') && document.body.innerText.includes('View accounts')`, 'registration success', 30000);
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /source GnuCash file was not deleted, modified, copied, or converted/i, 'registration success must state source untouched');
		assert.equal(api.lifecycleRequests.filter((request) => request.kind === 'register_metadata').length, 1, 'confirm must register metadata exactly once');
		assert.equal(api.state.books.length, 1, 'successful confirm must create one metadata book');
		const registeredBookId = api.state.books[0].id;
		assert.equal(api.state.registerRequestBodies.at(-1).preflight_token.startsWith('synthetic-preflight-'), true, 'confirm must send an opaque preflight token');

		await navigate(cdp, webBase, '/books/new', 'duplicate preflight page');
		await submitForm(cdp, '?/preflight', {
			name: 'Duplicate Attempt',
			mounted_path: sourcePath,
			base_currency: 'SEK'
		}, {}, 'duplicate preflight');
		await waitForExpression(cdp, `document.body.innerText.toLowerCase().includes('already registered')`, 'duplicate preflight rendered', 30000);
		snapshot = await pageSnapshot(cdp);
		assert.ok(!snapshot.bodyText.includes('Confirm metadata registration'), 'duplicate preflight must block confirm UI');
		assert.equal(api.lifecycleRequests.filter((request) => request.kind === 'register_metadata').length, 1, 'duplicate preflight must not register metadata');

		const errorCases = [
			['/data/books/missing-source.gnucash.sqlite', 'The configured server-side source was not found'],
			['/data/books/unavailable-source.gnucash.sqlite', 'does not have permission'],
			['/data/books/unsupported-source.xml', 'Only a supported server-side SQLite source'],
			['/outside-root/private-book.gnucash.sqlite', 'outside the allowed'],
			['/data/books/symlink-source.gnucash.sqlite', 'symlink component'],
			['../path-traversal.gnucash.sqlite', 'mounted server path is invalid'],
			['/data/books/error-state.gnucash.sqlite', 'could not open the source']
		];
		for (const [pathValue, expectedCopy] of errorCases) {
			await navigate(cdp, webBase, '/books/new', `preflight error ${pathValue}`);
			await submitForm(cdp, '?/preflight', {
				name: 'Rejected Synthetic Book',
				mounted_path: pathValue,
				base_currency: 'SEK'
			}, {}, `preflight error submit ${pathValue}`);
			snapshot = await pageSnapshot(cdp);
			assert.match(snapshot.bodyText, new RegExp(expectedCopy, 'i'), `preflight error must show fixed copy for ${pathValue}`);
			assert.equal(snapshot.alerts >= 1, true, `preflight error must render accessible alert for ${pathValue}`);
			assertNoPrivateLeak(snapshot.bodyText, `preflight error ${pathValue}`);
		}

		await setSession(cdp, webBase, adminToken, 'ru');
		await navigate(cdp, webBase, '/books/new', 'RU preflight error');
		await submitForm(cdp, '?/preflight', {
			name: 'RU rejected book',
			mounted_path: '/outside-root/ru-private.gnucash.sqlite',
			base_currency: 'SEK'
		}, {}, 'RU outside root submit');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Источник находится вне разрешённых/i, 'RU preflight error must use localized fixed copy');
		assertNoPrivateLeak(snapshot.bodyText, 'RU preflight error');
		await assertMobileAccessibility(cdp, 'RU /books/new error');

		await setSession(cdp, webBase, adminToken, 'en');
		await navigate(cdp, webBase, '/books', 'registered books list');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Synthetic Onboarding Book/, 'registered book must appear on books list');
		assert.ok(snapshot.links.includes(`/books/${registeredBookId}/settings`), 'registered book must link to settings/health');
		for (const next of ['/accounts', '/transactions', '/reports']) {
			assert.ok(snapshot.links.includes(`/books/${registeredBookId}/select?next=${next}`), `registered book must expose exact safe link ${next}`);
		}
		await assertMobileAccessibility(cdp, 'registered /books list');

		await navigate(cdp, webBase, `/books/${registeredBookId}/select?next=/accounts`, 'select accounts', '/accounts');
		await waitForExpression(cdp, `location.pathname === '/accounts' && document.body.innerText.includes('Accounts')`, 'accounts reached', 30000);
		assert.equal(api.requests.some((request) => request.path === `/books/${registeredBookId}/accounts/explorer`), true, 'Accounts link must select exact book before loading accounts explorer');
		assert.equal(await selectedBookCookie(cdp, webBase), String(registeredBookId), 'Accounts link must persist selected book cookie');

		await navigate(cdp, webBase, `/books/${registeredBookId}/select?next=/transactions`, 'select transactions', '/transactions');
		await waitForExpression(cdp, `location.pathname === '/transactions' && /Transactions|Transaction Explorer/.test(document.body.innerText)`, 'transactions reached', 30000);
		assert.equal(api.requests.some((request) => request.path === `/books/${registeredBookId}/accounts/options`), true, 'Transactions link must select exact book before loading bounded transaction account options');
		assert.equal(api.requests.some((request) => request.path === `/books/${registeredBookId}/accounts`), false, 'Transactions link must not load legacy balance-bearing account options');

		await navigate(cdp, webBase, `/books/${registeredBookId}/select?next=/reports`, 'select reports', '/reports');
		await waitForExpression(cdp, `location.pathname === '/reports' && /Compare financial periods|FINANCIAL REPORTS/.test(document.body.innerText)`, 'reports reached', 30000);
		assert.equal(api.requests.some((request) => request.path === `/books/${registeredBookId}/reports/comparison`), true, 'Reports link must select exact book before loading reports');
		assert.ok(api.requests.some((request) => request.path === `/books/${registeredBookId}/reports/reporting-date`), 'Reports must resolve the selected book reporting clock before its default period');
		const comparisonRequest = api.requests.find((request) => request.path === `/books/${registeredBookId}/reports/comparison`);
		assert.equal(new URLSearchParams(comparisonRequest.search).get('date_from'), '2026-07-01', 'Reports default starts in the authoritative reporting month');
		assert.equal(new URLSearchParams(comparisonRequest.search).get('date_to'), '2026-07-15', 'Reports default ends at the authoritative reporting date');

		await navigate(cdp, webBase, `/books/${registeredBookId}/settings`, 'admin settings');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Book settings and health|Admin lifecycle controls/, 'settings page must render health/lifecycle UI');
		for (const action of ['?/renameBook', '?/recheckHealth', '?/disableBook', '?/removeBook']) {
			assert.ok(snapshot.forms.includes(action), `admin settings must expose ${action}`);
		}
		await assertMobileAccessibility(cdp, 'admin settings initial');

		await submitForm(cdp, '?/renameBook', { name: 'Renamed Synthetic Book', base_currency: 'usd' }, {}, 'rename metadata');
		await waitForExpression(cdp, `document.body.innerText.includes('Updated display metadata only') && document.body.innerText.includes('Renamed Synthetic Book')`, 'rename success', 30000);
		assert.equal(api.state.books[0].name, 'Renamed Synthetic Book', 'rename action must update app display metadata');
		assert.equal(api.state.books[0].base_currency, 'USD', 'rename action must normalize currency metadata');

		await submitForm(cdp, '?/recheckHealth', {}, {}, 'recheck health');
		await waitForExpression(cdp, `document.body.innerText.includes('Refreshed cached health')`, 'recheck success', 30000);
		assert.equal(api.sourceOpenModes.some((entry) => entry.operation === 'recheck' && entry.mode === 'readonly'), true, 'recheck source open must be readonly');

		await submitForm(cdp, '?/disableBook', {}, { confirm_metadata_only: true }, 'disable metadata');
		await waitForExpression(cdp, `document.body.innerText.includes('Disabled this app registration') && document.body.innerText.includes('Enable with fresh preflight')`, 'disable success', 30000);
		assert.equal(api.state.books[0].is_enabled, false, 'disable action must only disable app metadata');
		assert.equal(await selectedBookCookie(cdp, webBase), null, 'disable selected active book must clear selected-book cookie');

		await submitForm(cdp, '?/enablePreflight', { mounted_path: sourcePath }, { make_default: true }, 'enable preflight');
		await waitForExpression(cdp, `document.body.innerText.includes('Path-redacted enable preflight preview') && document.body.innerText.includes('Confirm enable')`, 'enable preflight rendered', 30000);
		snapshot = await pageSnapshot(cdp);
		assertNoPrivateLeak(snapshot.bodyText, 'enable preflight preview');
		await submitForm(cdp, '?/enableBook', {}, {}, 'enable metadata');
		await waitForExpression(cdp, `document.body.innerText.includes('Enabled this app registration') && document.body.innerText.includes('Renamed Synthetic Book')`, 'enable success', 30000);
		assert.equal(api.state.books[0].is_enabled, true, 'enable action must restore app metadata availability only');

		const secondBook = api.addBook({ sourcePath: secondSourcePath, name: 'Second Synthetic Book', baseCurrency: 'EUR', isDefault: false });
		const failedBook = api.addBook({ sourcePath: join(sourceDir, 'failed-book.gnucash.sqlite'), name: 'Failed Synthetic Book', baseCurrency: 'USD', failed: true });
		await navigate(cdp, webBase, '/books', 'multibook list with failed book');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Renamed Synthetic Book/, 'healthy book must remain visible in multibook list');
		assert.match(snapshot.bodyText, /Second Synthetic Book/, 'second book must appear in multibook list');
		assert.match(snapshot.bodyText, /Failed Synthetic Book/, 'failed book must not break registered list');
		assert.ok(snapshot.links.includes(`/books/${secondBook.id}/select?next=/accounts`), 'healthy second book must expose safe account link');
		assert.ok(!snapshot.links.includes(`/books/${failedBook.id}/select?next=/accounts`), 'failed book must not expose open links');

		await navigate(cdp, webBase, `/books/${secondBook.id}/select?next=/accounts`, 'select second book accounts', '/accounts');
		await waitForExpression(cdp, `location.pathname === '/accounts' && document.body.innerText.includes('Accounts')`, 'second accounts reached', 30000);
		assert.equal(await selectedBookCookie(cdp, webBase), String(secondBook.id), 'multibook switch must persist the exact selected book');
		assert.equal(api.requests.some((request) => request.path === `/books/${secondBook.id}/accounts/explorer`), true, 'multibook switch must load accounts for selected second book');

		await setSession(cdp, webBase, adminToken, 'en', 9999);
		await navigate(cdp, webBase, '/books', 'stale selected-cookie recovery');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /Book context reviewed/, 'stale selected-book cookie must show safe recovery notice');
		assert.equal(await selectedBookCookie(cdp, webBase), String(registeredBookId), 'stale selected-book cookie must recover to accessible default book');

		await setSession(cdp, webBase, adminToken, 'en', failedBook.id);
		await navigate(cdp, webBase, '/books', 'unavailable selected-cookie recovery');
		snapshot = await pageSnapshot(cdp);
		assert.match(snapshot.bodyText, /currently unavailable for read-only data views/, 'unavailable selected-book cookie must show safe recovery notice');
		assert.equal(await selectedBookCookie(cdp, webBase), String(registeredBookId), 'unavailable selected-book cookie must recover to accessible default book');
		assertNoPrivateLeak(snapshot.bodyText, 'selected-cookie recovery notices');

		await setSession(cdp, webBase, userToken, 'en', registeredBookId);
		await navigate(cdp, webBase, '/books', 'normal user registered books');
		snapshot = await pageSnapshot(cdp);
		assert.ok(!snapshot.links.includes('/books/new'), 'normal user books page must not expose registration link');
		assert.ok(!snapshot.forms.includes('?/setDefaultBook'), 'normal user books page must not expose default action');
		assert.ok(!snapshot.forms.includes('?/removeBook'), 'normal user books page must not expose unregister action');
		assertNoPrivateLeak(snapshot.html, 'normal user registered books serialized page data', [sourcePath, secondSourcePath]);

		await navigate(cdp, webBase, `/books/${registeredBookId}/settings`, 'normal user settings');
		snapshot = await pageSnapshot(cdp);
		for (const action of ['?/renameBook', '?/recheckHealth', '?/disableBook', '?/enablePreflight', '?/enableBook', '?/removeBook', '?/setDefaultBook']) {
			assert.ok(!snapshot.forms.includes(action), `normal user settings must not expose ${action}`);
		}
		assertNoPrivateLeak(snapshot.html, 'normal user settings serialized page data', [sourcePath, secondSourcePath]);
		await assertNormalUserApiForbidden(api.url);

		await setSession(cdp, webBase, adminToken, 'en', secondBook.id);
		await navigate(cdp, webBase, `/books/${secondBook.id}/settings`, 'unregister second settings');
		const deleteRequestsBeforeMissingConfirm = api.lifecycleRequests.filter((request) => request.kind === 'delete_metadata_only').length;
		const missingConfirmResponse = await postAppForm(cdp, `/books/${secondBook.id}/settings?/removeBook`, {});
		assert.ok([200, 400].includes(missingConfirmResponse.status) && /preflight|metadata-only action|confirm/i.test(missingConfirmResponse.text), 'unregister without metadata-only confirmation must return a handled app-action rejection');
		assert.equal(api.lifecycleRequests.filter((request) => request.kind === 'delete_metadata_only').length, deleteRequestsBeforeMissingConfirm, 'unregister without confirmation must not call API DELETE');
		await submitForm(cdp, '?/removeBook', {}, { confirm_metadata_only: true }, 'unregister metadata only');
		await waitForExpression(cdp, `location.pathname === '/books' && document.body.innerText.includes('Removed the book from the app registry only')`, 'unregister success redirect', 30000);
		assert.equal(api.state.books.some((book) => book.id === secondBook.id), false, 'unregister must remove only app metadata');
		assert.deepEqual(fileEvidence(secondSourcePath), beforeSecondSource, 'unregister must not modify source file hash/size/mtime');
		assertNoSqliteSidecars(secondSourcePath, 'unregister source sidecars');

		assert.deepEqual(fileEvidence(sourcePath), beforeSource, 'onboarding lifecycle must not modify first source file hash/size/mtime');
		assertNoSqliteSidecars(sourcePath, 'first source sidecars');
		assert.deepEqual(api.forbiddenGnuCashMutationRequests, [], 'synthetic API must observe zero product GnuCash mutation-capable requests');
		assert.deepEqual(forbiddenBrowserMutationRequests(browserRequests), [], 'browser must observe zero product GnuCash mutation-capable requests');
		assert.deepEqual(browserUploadOrFilesystemRequests(browserRequests), [], 'browser must not request upload/client filesystem APIs');
		assert.ok(api.sourceOpenModes.length >= 4, 'preflight/recheck/enable lifecycle must record source-open evidence');
		assert.deepEqual(api.sourceOpenModes.filter((entry) => entry.mode !== 'readonly'), [], 'all source opens must be readonly');
		assert.equal(api.normalUserForbiddenAttempts.length >= 8, true, 'normal user direct lifecycle API probes must be forbidden');

		console.log(`books onboarding browser smoke passed: books=${api.state.books.length} lifecycle_requests=${api.lifecycleRequests.length} readonly_source_opens=${api.sourceOpenModes.length} api_forbidden_gnucash=${api.forbiddenGnuCashMutationRequests.length} browser_forbidden_gnucash=${forbiddenBrowserMutationRequests(browserRequests).length} source_copy_modify_delete=0 upload_client_filesystem=${browserUploadOrFilesystemRequests(browserRequests).length} viewport_width=320 source_hash_unchanged=${beforeSource.sha256 === fileEvidence(sourcePath).sha256}`);
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
		rmSync(sourceDir, { recursive: true, force: true });
	}
}

await runSmoke();
