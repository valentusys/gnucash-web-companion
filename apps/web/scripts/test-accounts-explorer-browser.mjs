import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const viteBin = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(root, '.svelte-kit', 'output', 'server', 'index.js');
const smokeHome = process.env.ACCOUNTS_EXPLORER_SMOKE_HOME ?? (process.env.USER ? join('/home', process.env.USER) : homedir());
const smokeTempRoot = process.env.ACCOUNTS_EXPLORER_SMOKE_TMPDIR ?? join(smokeHome, '.cache', 'gwc-accounts-explorer');
const evidenceDir = process.env.ACCOUNTS_EXPLORER_SMOKE_EVIDENCE_DIR ?? join(root, '..', '..', '.hermes', 'autonomy', 'issue55-accounts-browser');
const screenshotsDir = join(evidenceDir, 'screenshots');
const syntheticToken = 'synthetic-accounts-explorer-browser-smoke-token';
const privateAccountSentinel = 'PRIVATE_ACCOUNT_SENTINEL_RAW_API_DETAIL_GUID_PATH_TOKEN';
const cdpCommandTimeoutMs = Number(process.env.ACCOUNTS_EXPLORER_CDP_TIMEOUT_MS ?? '90000');

const assetRootId = '00000000000000000000000000000011';
const liabilityRootId = '00000000000000000000000000000022';
const checkingAccountId = '11111111111111111111111111111111';
const duplicateCheckingAccountId = '22222222222222222222222222222222';
const placeholderAccountId = '33333333333333333333333333333333';
const hiddenAccountId = '44444444444444444444444444444444';
const repairedAccountId = '55555555555555555555555555555555';
const childAccountId = '66666666666666666666666666666666';
const securityAccountId = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
const transactionId = 'tx-account-activity-1';

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
	name: 'Synthetic Accounts Explorer Book',
	storage_type: 'sqlite',
	base_currency: 'SEK',
	is_default: true,
	is_archived: false,
	access_role: 'owner',
	access_role_label: 'Owner',
	access_role_description: 'Synthetic owner access for accounts browser smoke only.',
	read_only: true,
	status: 'available',
	status_severity: 'ok',
	access_status: 'owner',
	can_open_read_only_views: true,
	storage_diagnostics: {
		status: 'available',
		configured: true,
		checked: true,
		safe_summary: 'Synthetic accounts explorer fixture.',
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
		message: 'Synthetic local accounts explorer smoke fixture; no private book is used.'
	}
};

function commodity(namespace = 'CURRENCY', mnemonic = 'SEK') {
	return { namespace, mnemonic };
}

function amount(value, namespace = 'CURRENCY', mnemonic = 'SEK') {
	return { amount: value, commodity: commodity(namespace, mnemonic) };
}

function segment(id, name) {
	return { id, name };
}

function node({
	id,
	parentId = null,
	sourceParentId = parentId,
	rootId = id,
	path,
	depth,
	name,
	type,
	commodityRef = commodity(),
	hidden = false,
	placeholder = false,
	childCount = 0,
	directBalance = amount('0.00'),
	recursiveBalances = [directBalance],
	matchState = 'match',
	structureStatus = 'normal'
}) {
	return {
		id,
		source_parent_id: sourceParentId,
		parent_id: parentId,
		root_id: rootId,
		path,
		full_path: path.map((item) => item.name).join(':'),
		depth,
		name,
		type,
		commodity: commodityRef,
		hidden,
		placeholder,
		child_count: childCount,
		direct_balance: directBalance,
		recursive_balances: recursiveBalances,
		match_state: matchState,
		structure_status: structureStatus
	};
}

const assetsNode = node({
	id: assetRootId,
	rootId: assetRootId,
	path: [segment(assetRootId, 'Assets')],
	depth: 0,
	name: 'Assets',
	type: 'ASSET',
	childCount: 5,
	directBalance: amount('0.00'),
	recursiveBalances: [amount('1325.25'), amount('2.0000', 'FUND', 'SEK')],
	matchState: 'ancestor_context',
	structureStatus: 'root'
});

const liabilitiesNode = node({
	id: liabilityRootId,
	rootId: liabilityRootId,
	path: [segment(liabilityRootId, 'Liabilities')],
	depth: 0,
	name: 'Liabilities',
	type: 'LIABILITY',
	childCount: 1,
	directBalance: amount('0.00'),
	recursiveBalances: [amount('-75.00')],
	matchState: 'ancestor_context',
	structureStatus: 'root'
});

const checkingNode = node({
	id: checkingAccountId,
	parentId: assetRootId,
	rootId: assetRootId,
	path: [
		segment(assetRootId, 'Assets'),
		segment(checkingAccountId, 'VeryLongSyntheticParentSegmentThatMustWrapOnMobile Checking')
	],
	depth: 1,
	name: 'Checking',
	type: 'BANK',
	childCount: 1,
	directBalance: amount('1200.25'),
	recursiveBalances: [amount('1210.25')]
});

const duplicateCheckingNode = node({
	id: duplicateCheckingAccountId,
	parentId: liabilityRootId,
	rootId: liabilityRootId,
	path: [segment(liabilityRootId, 'Liabilities'), segment(duplicateCheckingAccountId, 'Checking')],
	depth: 1,
	name: 'Checking',
	type: 'CREDIT',
	directBalance: amount('-75.00'),
	recursiveBalances: [amount('-75.00')]
});

const placeholderNode = node({
	id: placeholderAccountId,
	parentId: assetRootId,
	rootId: assetRootId,
	path: [segment(assetRootId, 'Assets'), segment(placeholderAccountId, 'Placeholder Rollup')],
	depth: 1,
	name: 'Placeholder Rollup',
	type: 'ASSET',
	placeholder: true,
	directBalance: amount('0.00'),
	recursiveBalances: []
});

const hiddenNode = node({
	id: hiddenAccountId,
	parentId: assetRootId,
	rootId: assetRootId,
	path: [segment(assetRootId, 'Assets'), segment(hiddenAccountId, 'Hidden Savings')],
	depth: 1,
	name: 'Hidden Savings',
	type: 'BANK',
	hidden: true,
	directBalance: amount('125.00'),
	recursiveBalances: [amount('125.00')]
});

const securityNode = node({
	id: securityAccountId,
	parentId: assetRootId,
	rootId: assetRootId,
	path: [segment(assetRootId, 'Assets'), segment(securityAccountId, 'SEK Security')],
	depth: 1,
	name: 'SEK Security',
	type: 'STOCK',
	commodityRef: commodity('FUND', 'SEK'),
	directBalance: amount('2.0000', 'FUND', 'SEK'),
	recursiveBalances: [amount('2.0000', 'FUND', 'SEK')]
});

const repairedNode = node({
	id: repairedAccountId,
	sourceParentId: 'ffffffffffffffffffffffffffffffff',
	rootId: repairedAccountId,
	path: [segment(repairedAccountId, 'Repaired Orphan')],
	depth: 0,
	name: 'Repaired Orphan',
	type: 'EXPENSE',
	directBalance: amount('0.00'),
	recursiveBalances: [amount('0.00')],
	matchState: 'ancestor_context',
	structureStatus: 'orphan_promoted'
});

const childNode = node({
	id: childAccountId,
	parentId: checkingAccountId,
	rootId: assetRootId,
	path: [
		segment(assetRootId, 'Assets'),
		segment(checkingAccountId, 'VeryLongSyntheticParentSegmentThatMustWrapOnMobile Checking'),
		segment(childAccountId, 'Synthetic Child')
	],
	depth: 2,
	name: 'Synthetic Child',
	type: 'BANK',
	directBalance: amount('10.00'),
	recursiveBalances: [amount('10.00')]
});

const largeAccountCount = 220;
const largeAssetNodes = Array.from({ length: largeAccountCount }, (_, index) => {
	const sequence = String(index + 1).padStart(3, '0');
	const id = (0x1000 + index).toString(16).padStart(32, '0');
	return node({
		id,
		parentId: assetRootId,
		rootId: assetRootId,
		path: [segment(assetRootId, 'Assets'), segment(id, `Generated Account ${sequence}`)],
		depth: 1,
		name: `Generated Account ${sequence}`,
		type: 'BANK',
		directBalance: amount(`${index + 1}.00`),
		recursiveBalances: [amount(`${index + 1}.00`)]
	});
});
assetsNode.child_count += largeAssetNodes.length;

const allExplorerNodes = [assetsNode, liabilitiesNode, checkingNode, duplicateCheckingNode, placeholderNode, hiddenNode, securityNode, repairedNode, ...largeAssetNodes];

function scanFor(nodes) {
	return {
		candidate_accounts: nodes.length,
		returned_nodes: nodes.length,
		split_rows: nodes.length + 4,
		split_aggregate_rows: nodes.length + 2,
		query_count: 1,
		rollup_bucket_cells: nodes.reduce((total, item) => total + item.recursive_balances.length, 0),
		serialized_bytes: JSON.stringify(nodes).length,
		exhausted: true,
		limits: { accounts: 500, depth: 12, split_rows: 5000 }
	};
}

function explorerPayload(url) {
	const params = url.searchParams;
	const mode = params.get('mode') === 'flat' ? 'flat' : 'tree';
	const query = (params.get('query') ?? '').toLowerCase();
	const hiddenMode = params.get('hidden') ?? 'exclude';
	const placeholderMode = params.get('placeholder') ?? 'include';
	const typeFilters = params.getAll('type').map((value) => value.toUpperCase());
	let nodes = allExplorerNodes.filter((item) => {
		if (hiddenMode === 'exclude' && item.hidden) return false;
		if (hiddenMode === 'only' && !item.hidden) return false;
		if (placeholderMode === 'exclude' && item.placeholder) return false;
		if (placeholderMode === 'only' && !item.placeholder) return false;
		if (typeFilters.length && !typeFilters.includes(item.type)) return false;
		if (query && !`${item.name} ${item.full_path} ${item.type}`.toLowerCase().includes(query)) {
			return item.match_state === 'ancestor_context';
		}
		return true;
	});
	if (query === 'checking') {
		nodes = [assetsNode, liabilitiesNode, checkingNode, duplicateCheckingNode, placeholderNode, hiddenNode, repairedNode].filter((item) => {
			if (hiddenMode === 'exclude' && item.hidden) return false;
			if (placeholderMode === 'exclude' && item.placeholder) return false;
			return true;
		});
	}
	if (query === 'nomatch') nodes = [];
	return {
		book_id: 1,
		mode,
		normalized_filters: {
			query: query || null,
			types: typeFilters,
			hidden: hiddenMode,
			placeholder: placeholderMode
		},
		root_ids: mode === 'flat' ? [] : Array.from(new Set(nodes.map((item) => item.root_id))),
		nodes,
		returned_count: nodes.length,
		scan: scanFor(nodes),
		balance_basis: 'native_commodity_account_natural_sign',
		includes_currency_conversion: false,
		limitations: ['synthetic_fixture: No FX conversion; native commodity buckets are intentionally separate.']
	};
}

function overviewPayload(accountId) {
	const base = accountId === securityAccountId ? securityNode : accountId === duplicateCheckingAccountId ? duplicateCheckingNode : checkingNode;
	const children = accountId === checkingAccountId ? [childNode] : [];
	return {
		...base,
		match_state: undefined,
		breadcrumbs: base.path.slice(0, -1),
		subtree_account_count: children.length + 1,
		child_count: children.length,
		children,
		children_returned: children.length,
		children_truncated: false,
		scan: scanFor([base, ...children]),
		balance_basis: 'native_commodity_account_natural_sign',
		includes_currency_conversion: false,
		limitations: []
	};
}

function activityPayload(accountId, url) {
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const limit = Number(url.searchParams.get('limit') ?? '10');
	const isSecurity = accountId === securityAccountId;
	const isEmpty = dateFrom === '2026-08-01';
	const isPartialRecent = dateFrom === '2026-09-01';
	const isPartialChange = dateFrom === '2026-09-15';
	const isPartial = isPartialRecent || isPartialChange;
	const activityCommodity = isSecurity ? commodity('FUND', 'SEK') : commodity('CURRENCY', 'SEK');
	if (isEmpty) {
		return {
			book_id: 1,
			account_id: accountId,
			date_from: dateFrom,
			date_to: dateTo,
			scope: 'direct_account',
			commodity: activityCommodity,
			change: null,
			inflow: null,
			outflow: null,
			flow_status: 'not_applicable_for_generic_account',
			recent_transactions: [],
			limit,
			returned_count: 0,
			has_more: false,
			transaction_explorer_compatible: !isSecurity,
			partial_failure: false,
			section_statuses: [
				{ section: 'change', status: 'empty', detail: null },
				{ section: 'recent_transactions', status: 'empty', detail: null }
			],
			scan: { selected_accounts: 1, change_split_rows: 0, recent_transaction_objects: 0, recent_split_rows: 0, query_count: 1, serialized_bytes: 0, limits: { recent: limit } },
			limitations: []
		};
	}
	const recentTransactions = isSecurity
		? []
		: [
				{
					id: transactionId,
					date: '2026-07-11',
					description: 'Synthetic account grocery',
					matched_quantity: amount('-42.50'),
					counter_account_name: 'Synthetic Grocer',
					is_write_alpha_owned: false
				}
			];
	return {
		book_id: 1,
		account_id: accountId,
		date_from: dateFrom,
		date_to: dateTo,
		scope: 'direct_account',
		commodity: activityCommodity,
		change: isSecurity ? amount('2.0000', 'FUND', 'SEK') : amount('125.25'),
		inflow: null,
		outflow: null,
		flow_status: 'not_applicable_for_generic_account',
		recent_transactions: recentTransactions,
		limit,
		returned_count: recentTransactions.length,
		has_more: false,
		transaction_explorer_compatible: !isSecurity,
		partial_failure: isPartial,
		section_statuses: [
			{ section: 'change', status: isPartialChange ? 'error' : 'ok', detail: isPartialChange ? `${privateAccountSentinel}:change/raw/backend/diagnostic` : null },
			{ section: 'recent_transactions', status: isPartialRecent ? 'error' : 'ok', detail: isPartialRecent ? `${privateAccountSentinel}:recent/raw/backend/diagnostic` : null }
		],
		scan: { selected_accounts: 1, change_split_rows: 3, recent_transaction_objects: recentTransactions.length, recent_split_rows: recentTransactions.length * 2, query_count: 2, serialized_bytes: 512, limits: { recent: limit } },
		limitations: isPartial ? [`${privateAccountSentinel}/redacted/raw/backend/path`] : []
	};
}

function transactionExplorerPayload(url) {
	return {
		items: [
			{
				id: transactionId,
				date: url.searchParams.get('date_to') ?? '2026-07-30',
				description: 'Synthetic account drilldown transaction',
				representative_amount: { amount: '-42.50', currency: 'SEK' },
				representative_account: { id: checkingAccountId, name: 'Checking' },
				matched_amount: { amount: '-42.50', currency: 'SEK' },
				amount_basis: 'selected_accounts',
				matched_account_ids: [checkingAccountId],
				counter_account_name: 'Synthetic Grocer',
				is_write_alpha_owned: false
			}
		],
		sort: url.searchParams.get('sort') ?? 'date_desc',
		page_size: Number(url.searchParams.get('page_size') ?? '50'),
		returned_count: 1,
		has_more: false,
		has_previous: false,
		next_cursor: null,
		previous_cursor: null,
		scan: { candidate_rows: 1, split_rows: 2, query_count: 1, scan_limited: false, exhausted: true },
		limitations: []
	};
}

function transactionDetailPayload(id) {
	return {
		id,
		date: '2026-07-11',
		description: 'Synthetic account grocery',
		currency: 'SEK',
		is_write_alpha_owned: false,
		splits: [
			{ account_id: checkingAccountId, account_name: 'Checking', memo: 'Account smoke debit', reconcile_state: 'n', amount: '-42.50', currency: 'SEK' },
			{ account_id: '77777777777777777777777777777777', account_name: 'Synthetic Expenses', memo: 'Account smoke credit', reconcile_state: 'n', amount: '42.50', currency: 'SEK' }
		]
	};
}

function legacyAccounts() {
	return allExplorerNodes.map((item) => ({
		id: item.id,
		name: item.name,
		full_name: item.full_path,
		type: item.type,
		currency: item.commodity.mnemonic,
		balance: item.direct_balance.amount,
		placeholder: item.placeholder,
		hidden: item.hidden,
		parent_id: item.parent_id
	}));
}

function jsonResponse(res, status, body) {
	const payload = Buffer.from(JSON.stringify(body));
	res.writeHead(status, {
		'content-type': 'application/json',
		'content-length': String(payload.length)
	});
	res.end(payload);
}

function isForbiddenApiMutation(method, pathname, search = '') {
	const upper = method.toUpperCase();
	if (upper !== 'GET' && upper !== 'HEAD') return true;
	const target = `${pathname}${search}`;
	return /(?:\/|%2F|[?&=])(?:validate|preflight|create|patch|delete|batch|write-alpha|owner-writebeta|backups?|audit)(?:\/|%2F|$|[?&=])/i.test(target);
}

async function startSyntheticApi() {
	const requests = [];
	const forbiddenRequests = [];
	const server = createServer((req, res) => {
		const url = new URL(req.url ?? '/', 'http://127.0.0.1');
		requests.push({ method: req.method, path: url.pathname, search: url.search, pathWithSearch: `${url.pathname}${url.search}` });

		if (isForbiddenApiMutation(req.method ?? 'GET', url.pathname, url.search)) {
			forbiddenRequests.push({ method: req.method, path: url.pathname, search: url.search });
			return jsonResponse(res, 409, { detail: 'Synthetic accounts smoke blocked a mutation-capable endpoint.' });
		}
		if (req.method === 'GET' && url.pathname === '/health') return jsonResponse(res, 200, { status: 'ok', first_run: null });
		if (req.method === 'GET' && url.pathname === '/auth/me') {
			return jsonResponse(res, 200, { id: 1, username: 'synthetic_accounts', display_name: 'Synthetic Accounts', is_admin: false });
		}
		if (req.method === 'GET' && url.pathname === '/books') return jsonResponse(res, 200, [syntheticBook]);
		if (req.method === 'GET' && url.pathname === '/books/1/accounts') return jsonResponse(res, 200, legacyAccounts());
		if (req.method === 'GET' && url.pathname === '/books/1/accounts/explorer') return jsonResponse(res, 200, explorerPayload(url));

		const overviewMatch = url.pathname.match(/^\/books\/1\/accounts\/([0-9a-f]{32})\/overview$/);
		if (req.method === 'GET' && overviewMatch) return jsonResponse(res, 200, overviewPayload(overviewMatch[1]));
		const activityMatch = url.pathname.match(/^\/books\/1\/accounts\/([0-9a-f]{32})\/activity$/);
		if (req.method === 'GET' && activityMatch) return jsonResponse(res, 200, activityPayload(activityMatch[1], url));
		if (req.method === 'GET' && url.pathname === '/books/1/transactions/explorer') return jsonResponse(res, 200, transactionExplorerPayload(url));
		const transactionMatch = url.pathname.match(/^\/books\/1\/transactions\/(.+)$/);
		if (req.method === 'GET' && transactionMatch) return jsonResponse(res, 200, transactionDetailPayload(decodeURIComponent(transactionMatch[1])));
		return jsonResponse(res, 404, { detail: 'Synthetic accounts smoke endpoint not found.' });
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
		try {
			if (await evaluate(cdp, expression)) return;
		} catch {
			// Navigation can briefly invalidate the JS context; keep polling until timeout.
		}
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

async function navigateAndWait(cdp, webBase, path, readyExpression, label) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 20000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([load, waitForExpression(cdp, readyExpression, label, 20000)]);
	await waitForExpression(cdp, readyExpression, label, 20000);
	await assertPageSanitized(cdp, label);
}

async function captureScreenshot(cdp, name) {
	mkdirSync(screenshotsDir, { recursive: true });
	const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
	const path = join(screenshotsDir, `${name}.png`);
	writeFileSync(path, Buffer.from(result.data, 'base64'));
	return path;
}

function accountExplorerRequests(api) {
	return api.requests.filter((request) => request.path === '/books/1/accounts/explorer');
}

function accountOverviewRequests(api) {
	return api.requests.filter((request) => /^\/books\/1\/accounts\/[0-9a-f]{32}\/overview$/.test(request.path));
}

function accountActivityRequests(api) {
	return api.requests.filter((request) => /^\/books\/1\/accounts\/[0-9a-f]{32}\/activity$/.test(request.path));
}

function transactionExplorerRequests(api) {
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
	assert.deepEqual(api.forbiddenRequests, [], `${label}: synthetic API must observe zero mutation-capable/write endpoint requests`);
	assert.deepEqual(forbiddenBrowserMutationRequests(browserRequests), [], `${label}: browser must issue zero mutation-capable requests`);
}

function assertRequestParams(request, expectedParams, label) {
	const url = new URL(`${request.path}${request.search}`, 'http://127.0.0.1');
	for (const [key, value] of Object.entries(expectedParams)) {
		assert.equal(url.searchParams.get(key), value, `${label}: ${key}`);
	}
}

function assertRequestParamsAbsent(request, keys, label) {
	const url = new URL(`${request.path}${request.search}`, 'http://127.0.0.1');
	for (const key of keys) {
		assert.equal(url.searchParams.get(key), null, `${label}: ${key} must be absent`);
	}
}

async function assertPageSanitized(cdp, label) {
	const html = await evaluate(cdp, `document.documentElement?.outerHTML ?? ''`);
	const htmlContainsPrivateSentinel = html.includes(privateAccountSentinel);
	assert.equal(htmlContainsPrivateSentinel, false, `${label}: private sentinel/raw API detail must not be serialized into browser HTML`);
	assert.doesNotMatch(html, /SECRET|TOKEN|PRIVATE_ACCOUNT_SENTINEL|RAW_API_DETAIL/i, `${label}: private sentinel/token markers must not be visible`);
	return htmlContainsPrivateSentinel;
}

async function assertStorageEmpty(cdp, label) {
	const state = await evaluate(cdp, `(() => ({
		localKeys: Object.keys(localStorage),
		sessionKeys: Object.keys(sessionStorage)
	}))()`);
	assert.deepEqual(state.localKeys, [], `${label}: account flow must not persist state in localStorage`);
	const accountSessionKeys = state.sessionKeys.filter((key) => /account|explorer|filter|cursor|offset|date_from|date_to/i.test(key));
	assert.deepEqual(accountSessionKeys, [], `${label}: account flow must not persist account/filter/cursor state in sessionStorage`);
}

async function assertAccessibleResponsiveAccounts(cdp, label, expectedLocalePattern, expectedWidth) {
	const state = await evaluate(cdp, `(() => {
		const root = document.documentElement;
		const body = document.body;
		const viewportWidth = window.innerWidth;
		const scrollWidth = Math.max(root?.scrollWidth ?? 0, body?.scrollWidth ?? 0);
		const form = document.querySelector('form[action="/accounts"][method="GET"]');
		const submit = form?.querySelector('button[type="submit"]');
		submit?.focus();
		const targetRects = Array.from(form?.querySelectorAll('a, button, select, input[type="search"], label:has(input[type="checkbox"])') ?? [])
			.map((el) => el.getBoundingClientRect())
			.filter((rect) => rect.width > 0 && rect.height > 0);
		return {
			viewportWidth,
			scrollWidth,
			labels: form?.querySelectorAll('label').length ?? 0,
			fieldsets: form?.querySelectorAll('fieldset').length ?? 0,
			ariaLive: Boolean(document.querySelector('[aria-live="polite"], [aria-live="assertive"]')),
			submitFocused: document.activeElement === submit,
			shortTargets: targetRects.filter((rect) => rect.height < 40).length,
			semanticNestedLists: Boolean(document.querySelector('section[aria-label] ul li button[aria-expanded]')),
			documentHeight: root?.scrollHeight ?? 0,
			accountRows: document.querySelectorAll('[data-account-row]').length,
			bodyText: body?.innerText ?? ''
		};
	})()`);
	assert.equal(state.viewportWidth, expectedWidth, `${label}: browser evidence must run at the expected mobile viewport`);
	assert.ok(state.scrollWidth <= state.viewportWidth + 8, `${label}: mobile viewport must not have meaningful horizontal overflow (${state.scrollWidth} > ${state.viewportWidth})`);
	assert.ok(state.labels >= 15, `${label}: account explorer controls must have visible labels`);
	assert.ok(state.fieldsets >= 1, `${label}: account type filters must use fieldset/legend semantics`);
	assert.ok(state.ariaLive, `${label}: account status/validation must expose aria-live`);
	assert.ok(state.submitFocused, `${label}: submit control must be keyboard-focusable`);
	assert.equal(state.shortTargets, 0, `${label}: visible controls must be at least 40px high`);
	assert.ok(state.semanticNestedLists, `${label}: tree mode must render semantic nested lists with native branch buttons`);
	assert.ok(state.accountRows <= 8, `${label}: collapsed mobile tree must mount only bounded root rows, got ${state.accountRows}`);
	assert.ok(state.documentHeight <= 2000, `${label}: collapsed mobile document height must stay bounded, got ${state.documentHeight}`);
	assert.match(state.bodyText, expectedLocalePattern, `${label}: expected localized account title/status must be visible`);
	return state;
}

function assertNoConsoleErrors(runtimeExceptions, consoleErrors) {
	assert.deepEqual(runtimeExceptions, [], 'browser runtime must have zero uncaught exceptions');
	assert.deepEqual(consoleErrors, [], 'browser console must have zero console.error/assert calls');
}

async function runSmoke() {
	assert.ok(existsSync(viteBin), 'Vite must be installed before running the accounts explorer browser smoke');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before accounts explorer browser smoke; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);

	mkdirSync(evidenceDir, { recursive: true });
	const api = await startSyntheticApi();
	const webPort = await getFreePort();
	const debugPort = await getFreePort();
	mkdirSync(smokeTempRoot, { recursive: true });
	const profileDir = mkdtempSync(join(smokeTempRoot, 'accounts-explorer-browser-'));
	let webProcess;
	let chromiumProcess;
	let cdp;
	const browserRequests = [];
	const runtimeExceptions = [];
	const consoleErrors = [];
	const screenshots = [];
	let htmlContainsPrivateSentinel = false;

	try {
		webProcess = spawnLogged(process.execPath, [viteBin, 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
			cwd: root,
			env: {
				...process.env,
				API_INTERNAL_URL: api.url,
				APP_ENV: 'test',
				GNUCASH_WRITES_ENABLED: 'false',
				JWT_SECRET: 'dummy-accounts-explorer-browser-smoke-secret',
				APP_ADMIN_PASSWORD: 'dummy-accounts-explorer-browser-smoke-password'
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
			'--window-size=1440,900',
			'about:blank'
		], {
			cwd: root,
			env: { ...process.env, TMPDIR: smokeTempRoot, TMP: smokeTempRoot, TEMP: smokeTempRoot }
		});

		cdp = await connectCdp(debugPort);
		cdp.on('Network.requestWillBeSent', (params) => {
			browserRequests.push({ method: params.request.method, url: params.request.url });
		});
		cdp.on('Runtime.exceptionThrown', (params) => {
			runtimeExceptions.push(params.exceptionDetails?.text ?? JSON.stringify(params.exceptionDetails ?? {}));
		});
		cdp.on('Runtime.consoleAPICalled', (params) => {
			if (['error', 'assert'].includes(params.type)) consoleErrors.push(`${params.type}: ${params.args?.map((arg) => arg.value ?? arg.description ?? '').join(' ')}`);
		});
		await cdp.send('Page.enable');
		await cdp.send('Runtime.enable');
		await cdp.send('Network.enable');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
		await cdp.send('Network.setCookie', { name: 'access_token', value: syntheticToken, url: webBase, path: '/', sameSite: 'Lax' });
		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });

		await navigateAndWait(cdp, webBase, '/accounts', `location.pathname === '/accounts' && location.search === '' && document.body.innerText.includes('Account explorer loaded')`, 'default accounts explorer');
		assert.equal(accountExplorerRequests(api).length, 1, '/accounts default must issue exactly one bounded account explorer request');
		assertRequestParamsAbsent(accountExplorerRequests(api).at(-1), ['cursor', 'offset', 'limit'], 'default account explorer request');
		const defaultState = await evaluate(cdp, `(() => ({
			bodyText: document.body.innerText,
			resetHref: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href === '/accounts') ?? '',
			paths: Array.from(document.querySelectorAll('p')).map((p) => p.textContent.trim()).filter((text) => text.includes('Checking')),
			initialDomRows: document.querySelectorAll('[data-account-row]').length,
			initialDocumentHeight: document.documentElement.scrollHeight,
			groupToggleCount: document.querySelectorAll('[data-account-toggle]').length,
			resultsLabel: document.querySelector('section[aria-label="Server-filtered account explorer results"]')?.getAttribute('aria-label') ?? ''
		}))()`);
		assert.ok(allExplorerNodes.length >= 212, 'synthetic account fixture must contain at least 212 discoverable accounts');
		assert.equal(defaultState.resetHref, '/accounts', 'default account explorer reset href must be exactly /accounts');
		assert.ok(defaultState.initialDomRows <= 8, `collapsed initial tree must mount only bounded root rows, got ${defaultState.initialDomRows}`);
		assert.ok(defaultState.initialDocumentHeight <= 4200, `collapsed initial document height must stay bounded, got ${defaultState.initialDocumentHeight}`);
		assert.ok(defaultState.groupToggleCount >= 2, 'tree mode must expose top-level branch toggles');
		assert.equal(defaultState.resultsLabel, 'Server-filtered account explorer results', 'results section must be semantically labelled');
		assert.doesNotMatch(defaultState.bodyText, /Recursive native-commodity buckets/i, 'technical native buckets must be hidden before disclosure');
		assert.match(defaultState.bodyText, /Balance details/i, 'collapsed balance disclosure must be available from each visible account row');
		assert.doesNotMatch(defaultState.bodyText, /FX total|converted total|cross-currency total/i, 'account explorer must not display a fake FX/cross-commodity total');
		screenshots.push(await captureScreenshot(cdp, 'accounts-desktop-en-initial'));
		await evaluate(cdp, `document.querySelector('[data-account-balance-details="${assetRootId}"] summary')?.click()`);
		await waitForExpression(cdp, `document.body.innerText.includes('RECURSIVE NATIVE-COMMODITY BUCKETS')`, 'technical balance disclosure');
		const disclosedBalanceText = await evaluate(cdp, `document.body.innerText`);
		assert.match(disclosedBalanceText, /Direct native balance[\s\S]*Recursive native-commodity buckets/i, 'balance disclosure must reveal exact direct and native-bucket labels');
		assert.match(disclosedBalanceText, /No FX conversion|No FX/i, 'balance disclosure must state the no-FX boundary');

		await evaluate(cdp, `document.querySelector('[data-account-toggle="${assetRootId}"]')?.focus()`);
		await cdp.send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: ' ', code: 'Space', windowsVirtualKeyCode: 32 });
		await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: ' ', code: 'Space', windowsVirtualKeyCode: 32 });
		await waitForExpression(cdp, `document.querySelector('[data-account-toggle="${assetRootId}"]')?.getAttribute('aria-expanded') === 'true'`, 'keyboard-expand Assets');
		const expandedState = await evaluate(cdp, `(() => ({
			rows: document.querySelectorAll('[data-account-row]').length,
			height: document.documentElement.scrollHeight,
			firstGeneratedVisible: document.body.innerText.includes('Generated Account 001'),
			nextButton: Boolean(document.querySelector('[data-account-page-next="${assetRootId}"]'))
		}))()`);
		assert.ok(expandedState.rows <= 32, `expanded branch must mount one bounded child window, got ${expandedState.rows}`);
		assert.ok(expandedState.height <= 9000, `expanded branch document height must remain bounded, got ${expandedState.height}`);
		assert.equal(expandedState.firstGeneratedVisible, true, 'first child window must expose generated accounts');
		assert.equal(expandedState.nextButton, true, 'large child group must expose a next-page button');
		await evaluate(cdp, `document.querySelector('[data-account-page-next="${assetRootId}"]')?.click()`);
		await waitForExpression(cdp, `document.body.innerText.includes('Generated Account 025')`, 'second Assets child page');
		const secondPageState = await evaluate(cdp, `(() => ({ rows: document.querySelectorAll('[data-account-row]').length, first: document.body.innerText.includes('Generated Account 001'), later: document.body.innerText.includes('Generated Account 025') }))()`);
		assert.ok(secondPageState.rows <= 32, `second child page must keep DOM bounded, got ${secondPageState.rows}`);
		assert.equal(secondPageState.first, false, 'moving to the next child page must unmount the first window');
		assert.equal(secondPageState.later, true, 'moving to the next child page must mount later accounts');
		await assertStorageEmpty(cdp, 'default /accounts');
		screenshots.push(await captureScreenshot(cdp, 'accounts-desktop-en-paged'));

		await navigateAndWait(cdp, webBase, '/accounts?query=Generated%20Account%20220', `location.pathname === '/accounts' && document.body.innerText.includes('Generated Account 220')`, 'far generated account search discovery');
		const farSearchState = await evaluate(cdp, `(() => ({ rows: document.querySelectorAll('[data-account-row]').length, height: document.documentElement.scrollHeight, bodyText: document.body.innerText }))()`);
		assert.ok(farSearchState.rows <= 8, `server search must reveal the far account without mounting the full tree, got ${farSearchState.rows}`);
		assert.ok(farSearchState.height <= 5000, `far-account search document height must stay bounded, got ${farSearchState.height}`);
		assert.match(farSearchState.bodyText, /Generated Account 220/, 'all generated accounts must remain discoverable through sticky server search');

		const beforeCanonicalExplorer = accountExplorerRequests(api).length;
		await navigateAndWait(
			cdp,
			webBase,
			'/accounts?placeholder=include&hidden=exclude&type=asset&query=checking&mode=tree',
			`location.pathname === '/accounts' && location.search === '?query=checking&type=ASSET' && document.body.innerText.includes('Account explorer loaded')`,
			'canonical account explorer URL'
		);
		assert.equal(accountExplorerRequests(api).length, beforeCanonicalExplorer + 1, 'canonical explorer URL must issue exactly one new explorer request');
		assertRequestParams(accountExplorerRequests(api).at(-1), { query: 'checking', type: 'ASSET' }, 'canonical account explorer request');
		assertRequestParamsAbsent(accountExplorerRequests(api).at(-1), ['mode', 'hidden', 'placeholder', 'cursor', 'offset'], 'canonical account explorer request');

		const beforeFlatExplorer = accountExplorerRequests(api).length;
		await navigateAndWait(
			cdp,
			webBase,
			'/accounts?mode=flat&query=checking&hidden=include&placeholder=include',
			`location.pathname === '/accounts' && location.search === '?mode=flat&query=checking&hidden=include' && document.body.innerText.includes('Account explorer loaded')`,
			'flat account explorer warnings'
		);
		assert.equal(accountExplorerRequests(api).length, beforeFlatExplorer + 1, 'flat warning URL must issue exactly one new explorer request');
		assertRequestParams(accountExplorerRequests(api).at(-1), { mode: 'flat', query: 'checking', hidden: 'include' }, 'flat warning explorer request');
		const warningState = await evaluate(cdp, `document.body.innerText`);
		assert.match(warningState, /Assets:[\s\S]*Checking[\s\S]*Liabilities:Checking/, 'duplicate account names must remain distinguishable by full path');
		assert.match(warningState, /Ancestor context|ancestors included only/i, 'ancestor_context warning/badge must be visible');
		assert.match(warningState, /Hidden accounts are visible|Hidden Savings/i, 'hidden account warning/state must be visible when included');
		assert.match(warningState, /Placeholder accounts|Placeholder Rollup/i, 'placeholder warning/state must be visible when present');
		assert.match(warningState, /Repaired hierarchy|orphan|cycle repairs/i, 'repaired hierarchy warning/state must be visible');

		const beforeInvalidExplorerCount = accountExplorerRequests(api).length;
		await navigateAndWait(
			cdp,
			webBase,
			'/accounts?cursor=stale&offset=50&query=checking',
			`location.pathname === '/accounts' && document.body.innerText.includes('Invalid account explorer filters')`,
			'invalid account explorer URL'
		);
		const invalidExplorerState = await evaluate(cdp, `(() => ({
			bodyText: document.body.innerText,
			formControls: document.querySelector('form[action="/accounts"]')?.querySelectorAll('input, select, button, a').length ?? 0,
			resetHref: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href')).find((href) => href === '/accounts') ?? ''
		}))()`);
		assert.equal(accountExplorerRequests(api).length, beforeInvalidExplorerCount, 'invalid account explorer URL must issue zero explorer endpoint requests');
		assert.ok(invalidExplorerState.formControls >= 18, 'invalid account explorer state must keep visible controls rendered');
		assert.equal(invalidExplorerState.resetHref, '/accounts', 'invalid account explorer reset href must be exactly /accounts');
		assert.match(invalidExplorerState.bodyText, /Unsupported account explorer URL parameter|Invalid account explorer filters/, 'invalid account explorer UI must be safe and actionable');
		await assertStorageEmpty(cdp, 'invalid account explorer URL');

		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 320, height: 700, deviceScaleFactor: 2, mobile: true });
		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'ru', url: webBase, path: '/', sameSite: 'Lax' });
		await navigateAndWait(cdp, webBase, '/accounts?hidden=include', `location.pathname === '/accounts' && document.body.innerText.includes('Account explorer загружен')`, 'mobile RU accounts explorer');
		const mobileState = await assertAccessibleResponsiveAccounts(cdp, 'mobile RU accounts explorer', /Дерево счетов|Account explorer загружен/, 320);
		await assertStorageEmpty(cdp, 'mobile RU accounts explorer');
		screenshots.push(await captureScreenshot(cdp, 'accounts-mobile-ru-320x700'));
		await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 780, deviceScaleFactor: 2, mobile: true });
		await navigateAndWait(cdp, webBase, '/accounts', `location.pathname === '/accounts' && document.body.innerText.includes('Account explorer loaded')`, 'mobile EN 390 accounts explorer');
		const mobile390State = await assertAccessibleResponsiveAccounts(cdp, 'mobile EN 390 accounts explorer', /Account tree|Account explorer loaded/, 390);
		assert.ok((await evaluate(cdp, `document.querySelectorAll('[data-account-row]').length`)) <= 8, '390px initial account DOM must remain collapsed and bounded');
		await assertStorageEmpty(cdp, 'mobile EN 390 accounts explorer');
		await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

		const overviewBefore = accountOverviewRequests(api).length;
		const activityBefore = accountActivityRequests(api).length;
		await navigateAndWait(
			cdp,
			webBase,
			`/accounts/${checkingAccountId}`,
			`location.pathname === '/accounts/${checkingAccountId}' && document.body.innerText.includes('Overview only')`,
			'account detail overview only'
		);
		assert.equal(accountOverviewRequests(api).length, overviewBefore + 1, 'account detail without dates must issue one overview request');
		assert.equal(accountActivityRequests(api).length, activityBefore, 'account detail without dates must issue zero activity requests');
		const overviewState = await evaluate(cdp, `document.body.innerText`);
		assert.match(overviewState, /Assets[\s\S]*Checking[\s\S]*Synthetic Child/, 'account detail must show breadcrumbs, path, and child summaries');
		assert.match(overviewState, /Direct native balance/i, 'account detail overview must show direct native balance label');
		assert.match(overviewState, /Recursive native-commodity buckets/i, 'account detail overview must show recursive native bucket label');
		assert.match(overviewState, /1200\.25/, 'account detail overview must show native direct balance amount');
		assert.match(overviewState, /SSR request counters: overview=1, activity=0\./, 'overview-only detail must render request counters');

		for (const [path, label] of [
			[`/accounts/${checkingAccountId}?date_from=2026-07-01`, 'one-sided account activity dates'],
			[`/accounts/${checkingAccountId}?date_from=2026-07-31&date_to=2026-07-01`, 'reversed account activity dates'],
			[`/accounts/${checkingAccountId}?date_from=2025-01-01&date_to=2026-01-02`, 'too-wide account activity dates'],
			[`/accounts/${checkingAccountId}?date_from=2026-02-31&date_to=2026-03-01`, 'invalid account activity date']
		]) {
			const beforeInvalidActivity = accountActivityRequests(api).length;
			await navigateAndWait(cdp, webBase, path, `document.body.innerText.includes('Invalid account detail URL')`, label);
			assert.equal(accountActivityRequests(api).length, beforeInvalidActivity, `${label}: invalid detail URL must issue zero activity endpoint requests`);
			const bodyText = await evaluate(cdp, `document.body.innerText`);
			assert.match(bodyText, /Account id, date_from\/date_to, limit, or return_to validation failed/, `${label}: validation UI must be safe and localized`);
		}

		const validDetailPath = `/accounts/${checkingAccountId}?date_from=2026-07-01&date_to=2026-07-30&limit=5&return_to=%2Faccounts%3Fquery%3Dchecking`;
		const overviewCountBeforeValid = accountOverviewRequests(api).length;
		const activityCountBeforeValid = accountActivityRequests(api).length;
		await navigateAndWait(cdp, webBase, validDetailPath, `location.pathname === '/accounts/${checkingAccountId}' && document.body.innerText.includes('Account activity loaded')`, 'valid account activity');
		assert.equal(accountOverviewRequests(api).length, overviewCountBeforeValid + 1, 'valid account activity must issue one overview request');
		assert.equal(accountActivityRequests(api).length, activityCountBeforeValid + 1, 'valid account activity must issue one activity request');
		assertRequestParams(accountActivityRequests(api).at(-1), { date_from: '2026-07-01', date_to: '2026-07-30', limit: '5' }, 'valid account activity request');
		const validActivityState = await evaluate(cdp, `(() => {
			const links = Array.from(document.querySelectorAll('a')).map((a) => ({ text: a.textContent.replace(/\s+/g, ' ').trim(), href: a.getAttribute('href') ?? '' }));
			return { bodyText: document.body.innerText, links };
		})()`);
		assert.match(validActivityState.bodyText, /Exact direct change/i, 'valid activity must show exact native commodity change label');
		assert.match(validActivityState.bodyText, /125\.25[\s\S]*SEK|SEK[\s\S]*125\.25/, 'valid activity must show exact native commodity change amount');
		assert.match(validActivityState.bodyText, /Generic inflow\/outflow classification is not applicable/, 'valid activity must not fake generic inflow/outflow for account scope');
		assert.match(validActivityState.bodyText, /Synthetic account grocery[\s\S]*-42\.50/, 'valid activity must show recent direct transaction rows and matched quantity');
		const txExplorerHref = validActivityState.links.find((link) => link.href.startsWith('/transactions?') && link.href.includes(`account_ids=${checkingAccountId}`))?.href ?? '';
		assert.ok(txExplorerHref, `compatible account activity must expose exact transaction explorer link; links=${JSON.stringify(validActivityState.links)}`);
		const txExplorerUrl = new URL(txExplorerHref, webBase);
		assert.equal(txExplorerUrl.pathname, '/transactions', 'transaction explorer drilldown path');
		assert.equal(txExplorerUrl.searchParams.get('date_from'), '2026-07-01', 'transaction explorer drilldown date_from');
		assert.equal(txExplorerUrl.searchParams.get('date_to'), '2026-07-30', 'transaction explorer drilldown date_to');
		assert.equal(txExplorerUrl.searchParams.get('account_ids'), checkingAccountId, 'transaction explorer drilldown account_ids');
		assert.equal(txExplorerUrl.searchParams.get('sort'), 'date_desc', 'transaction explorer drilldown sort');
		assert.equal(txExplorerUrl.searchParams.get('page_size'), '50', 'transaction explorer drilldown page_size');
		assert.equal(txExplorerUrl.searchParams.get('cursor'), null, 'transaction explorer drilldown must not include cursor');
		const reportHref = validActivityState.links.find((link) => link.href.startsWith('/reports?'))?.href ?? '';
		const reportUrl = new URL(reportHref, webBase);
		assert.equal(reportUrl.pathname, '/reports', 'base report drilldown path');
		assert.equal(reportUrl.searchParams.get('preset'), 'custom', 'base report preset');
		assert.equal(reportUrl.searchParams.get('date_from'), '2026-07-01', 'base report date_from');
		assert.equal(reportUrl.searchParams.get('date_to'), '2026-07-30', 'base report date_to');
		assert.equal(reportUrl.searchParams.get('comparison_mode'), 'previous_equivalent', 'base report comparison mode');
		assert.equal(reportUrl.searchParams.get('comparison_date_from'), '2026-06-01', 'base report comparison date_from');
		assert.equal(reportUrl.searchParams.get('comparison_date_to'), '2026-06-30', 'base report comparison date_to');

		const transactionDetailHref = validActivityState.links.find((link) => link.href.startsWith(`/transactions/${transactionId}?return_to=`))?.href ?? '';
		assert.ok(transactionDetailHref, 'recent activity rows must link to transaction detail with return_to');
		await navigateAndWait(cdp, webBase, transactionDetailHref, `location.pathname === '/transactions/${transactionId}' && document.body.innerText.includes('Synthetic account grocery')`, 'transaction detail account return_to');
		const transactionBackHref = await evaluate(cdp, `document.querySelector('main > a')?.getAttribute('href') ?? ''`);
		assert.ok(transactionBackHref.startsWith(`/accounts/${checkingAccountId}?date_from=2026-07-01&date_to=2026-07-30&limit=5&return_to=%2Faccounts%3Fquery%3Dchecking`), 'transaction detail back link must round-trip to canonical account detail return_to');

		const beforeTxExplorer = transactionExplorerRequests(api).length;
		await navigateAndWait(cdp, webBase, txExplorerUrl.pathname + txExplorerUrl.search, `location.pathname === '/transactions' && document.body.innerText.includes('Synthetic account drilldown transaction')`, 'account activity transaction explorer drilldown');
		assert.equal(transactionExplorerRequests(api).length, beforeTxExplorer + 1, 'clicking exact account drilldown must issue one transaction explorer request');
		assertRequestParams(transactionExplorerRequests(api).at(-1), { date_from: '2026-07-01', date_to: '2026-07-30', account_ids: checkingAccountId, sort: 'date_desc', page_size: '50' }, 'account drilldown transaction explorer request');
		assertRequestParamsAbsent(transactionExplorerRequests(api).at(-1), ['cursor', 'offset'], 'account drilldown transaction explorer request');

		await navigateAndWait(cdp, webBase, `/accounts/${checkingAccountId}?date_from=2026-08-01&date_to=2026-08-31`, `document.body.innerText.includes('No direct activity in this date range')`, 'empty account activity');
		const emptyActivityText = await evaluate(cdp, `document.body.innerText`);
		assert.match(emptyActivityText, /No recent direct transactions were returned/, 'empty account activity must render a deterministic empty recent state');
		assert.doesNotMatch(emptyActivityText, /Partial account activity|Account detail failed/, 'empty activity must not be confused with partial or failed states');

		await navigateAndWait(cdp, webBase, `/accounts/${checkingAccountId}?date_from=2026-09-01&date_to=2026-09-30`, `document.body.innerText.includes('Partial account activity')`, 'partial account activity recent section redaction');
		const partialActivityText = await evaluate(cdp, `document.body.innerText`);
		assert.match(partialActivityText, /Partial account activity[\s\S]*125\.25/, 'partial account activity must keep unaffected exact-change evidence visible');
		assert.doesNotMatch(partialActivityText, new RegExp(privateAccountSentinel), 'partial account activity must redact raw backend detail/private sentinel');
		htmlContainsPrivateSentinel = htmlContainsPrivateSentinel || (await assertPageSanitized(cdp, 'partial account activity recent section redaction'));

		await navigateAndWait(cdp, webBase, `/accounts/${checkingAccountId}?date_from=2026-09-15&date_to=2026-09-30`, `document.body.innerText.includes('Partial account activity')`, 'partial account activity change section redaction');
		const partialChangeActivityText = await evaluate(cdp, `document.body.innerText`);
		assert.match(partialChangeActivityText, /Partial account activity[\s\S]*125\.25/, 'partial change account activity must keep exact-change product evidence visible');
		assert.doesNotMatch(partialChangeActivityText, new RegExp(privateAccountSentinel), 'partial change account activity must redact raw backend detail/private sentinel');
		htmlContainsPrivateSentinel = htmlContainsPrivateSentinel || (await assertPageSanitized(cdp, 'partial account activity change section redaction'));

		await navigateAndWait(cdp, webBase, `/accounts/${securityAccountId}?date_from=2026-07-01&date_to=2026-07-30`, `location.pathname === '/accounts/${securityAccountId}' && document.body.innerText.includes('Account activity loaded')`, 'security account activity no FX drilldown');
		const securityState = await evaluate(cdp, `(() => ({
			bodyText: document.body.innerText,
			drilldownLinks: Array.from(document.querySelectorAll('a')).map((a) => a.getAttribute('href') ?? '').filter((href) => href.startsWith('/transactions?'))
		}))()`);
		assert.match(securityState.bodyText, /FUND:SEK|SEK Security/, 'same-mnemonic non-currency security account must show native commodity identity');
		assert.match(securityState.bodyText, /unavailable_no_fx_scope/, 'non-base/non-currency account must render explicit no-FX unavailable drilldown state');
		assert.deepEqual(securityState.drilldownLinks.filter((href) => href.includes(`account_ids=${securityAccountId}`)), [], 'non-currency same-mnemonic security account must not expose exact transaction explorer link');

		for (const [returnTo, label] of [
			['javascript:alert(1)', 'scheme return_to'],
			['//evil.example/accounts', 'protocol-relative return_to'],
			['/accounts#fragment', 'fragment return_to'],
			['/books', 'unknown route return_to']
		]) {
			await navigateAndWait(
				cdp,
				webBase,
				`/transactions/${transactionId}?return_to=${encodeURIComponent(returnTo)}`,
				`location.pathname === '/transactions/${transactionId}' && document.body.innerText.includes('Synthetic account grocery')`,
				label
			);
			const safeBackHref = await evaluate(cdp, `document.querySelector('main > a')?.getAttribute('href') ?? ''`);
			assert.equal(safeBackHref, '/transactions', `${label}: malicious/unknown transaction detail return_to must fall back safely`);
		}

		assertNoMutationRequestsObserved(api, browserRequests, 'accounts explorer browser smoke');
		assertNoConsoleErrors(runtimeExceptions, consoleErrors);
		console.log(`accounts explorer browser smoke passed: account_explorer_requests=${accountExplorerRequests(api).length} overview_requests=${accountOverviewRequests(api).length} activity_requests=${accountActivityRequests(api).length} transaction_explorer_requests=${transactionExplorerRequests(api).length} initial_dom_rows=${defaultState.initialDomRows} initial_document_height=${defaultState.initialDocumentHeight} discoverable_accounts=${allExplorerNodes.length} html_contains_private_sentinel=${htmlContainsPrivateSentinel} api_forbidden=${api.forbiddenRequests.length} browser_forbidden=${forbiddenBrowserMutationRequests(browserRequests).length} runtime_exceptions=${runtimeExceptions.length} console_errors=${consoleErrors.length} mobile_width=${mobileState.viewportWidth} mobile_scroll_width=${mobileState.scrollWidth} mobile_390_width=${mobile390State.viewportWidth} screenshots=${screenshots.join(',')}`);
	} catch (error) {
		let failureEvidence = '';
		try {
			if (cdp) {
				const currentUrl = await evaluate(cdp, `location.href`).catch(() => 'unknown');
				const bodyText = await evaluate(cdp, `document.body.innerText`).catch(() => '');
				const htmlContainsPrivateSentinel = await evaluate(cdp, `document.documentElement.outerHTML.includes(${JSON.stringify(privateAccountSentinel)})`).catch(() => false);
				const screenshot = await captureScreenshot(cdp, 'failure-current-page');
				screenshots.push(screenshot);
				failureEvidence = join(evidenceDir, 'last-failure.json');
				writeFileSync(
					failureEvidence,
					JSON.stringify(
						{
							error: error.message,
							current_url: currentUrl,
							body_excerpt: bodyText.slice(0, 2000),
							html_contains_private_sentinel: htmlContainsPrivateSentinel,
							request_counts: {
								account_explorer: accountExplorerRequests(api).length,
								overview: accountOverviewRequests(api).length,
								activity: accountActivityRequests(api).length,
								transaction_explorer: transactionExplorerRequests(api).length,
								api_forbidden: api.forbiddenRequests.length,
								browser_forbidden: forbiddenBrowserMutationRequests(browserRequests).length,
								runtime_exceptions: runtimeExceptions.length,
								console_errors: consoleErrors.length
							},
							screenshots
						},
						null,
						2
					)
				);
			}
		} catch (evidenceError) {
			failureEvidence = `failed to write failure evidence: ${evidenceError.message}`;
		}
		const webTail = webProcess?.outputTail?.() ?? '';
		const chromiumTail = chromiumProcess?.outputTail?.() ?? '';
		throw new Error(`${error.message}\n--- evidence ---\n${failureEvidence}\n--- vite preview tail ---\n${webTail}\n--- chromium tail ---\n${chromiumTail}`);
	} finally {
		cdp?.close();
		await stopProcess(chromiumProcess);
		await stopProcess(webProcess);
		await api.close();
		await removeProfileDir(profileDir);
	}
}

await runSmoke();
