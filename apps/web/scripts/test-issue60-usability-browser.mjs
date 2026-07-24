import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const here = dirname(fileURLToPath(import.meta.url));
const webRoot = join(here, '..');
const repoRoot = resolve(webRoot, '..', '..');
const apiRoot = join(repoRoot, 'apps', 'api');
const viteBin = join(webRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const previewServerIndex = join(webRoot, '.svelte-kit', 'output', 'server', 'index.js');
const issue60BaselineSha = '51ae5b3598678e6e09bfbd2024e5df5fe8a4a2c3';
const jwtSecret = 'issue60-usability-browser-' + 'x'.repeat(48);
const adminPassword = 'issue60-usability-admin-pass';
const cdpCommandTimeoutMs = 120000;

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

function sleep(ms) {
	return new Promise((resolvePromise) => setTimeout(resolvePromise, ms));
}

function jsString(value) {
	return JSON.stringify(value);
}

function sqliteUrl(path) {
	return `sqlite:///${path}`;
}

function hashFile(path) {
	const digest = createHash('sha256');
	digest.update(readFileSync(path));
	return digest.digest('hex');
}

function spawnLogged(command, args, options = {}) {
	const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
	let output = '';
	for (const stream of [child.stdout, child.stderr]) {
		stream.on('data', (chunk) => {
			output += chunk.toString('utf8');
			output = output.slice(-40000);
		});
	}
	child.outputTail = () => output;
	return child;
}

function runGit(args) {
	const result = spawnSync('git', ['-C', repoRoot, ...args], { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
	assert.equal(result.status, 0, `git ${args.join(' ')} failed\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`);
	return result.stdout;
}

function changedOrUntrackedIssue60Paths() {
	const commands = [
		['diff', '--name-only', '--diff-filter=ACMRT', `${issue60BaselineSha}..HEAD`],
		['diff', '--name-only', '--diff-filter=ACMRT'],
		['diff', '--cached', '--name-only', '--diff-filter=ACMRT'],
		['ls-files', '--others', '--exclude-standard']
	];
	const paths = new Set();
	for (const args of commands) {
		for (const path of runGit(args).split('\n').filter(Boolean)) paths.add(path);
	}
	return [...paths].sort();
}

function isRawRuntimeOrPrivateArtifact(path) {
	return /(^|\/)(data\/books|data\/backups|data\/app|secrets)(\/|$)|\.gnucash\.sqlite$|app\.db$/.test(path);
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

async function removeTempRoot(path) {
	for (let attempt = 1; attempt <= 5; attempt += 1) {
		try {
			rmSync(path, { recursive: true, force: true });
			return;
		} catch (error) {
			if (!['ENOTEMPTY', 'EBUSY', 'EPERM'].includes(error?.code) || attempt === 5) throw error;
			await sleep(attempt * 250);
		}
	}
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

function generateIssue60Manifest(root) {
	return runPythonJson(
		`import json, sys\nfrom pathlib import Path\nfrom tests.support.generate_issue60_usability_fixture import generate_issue60_usability_fixture\nfixture=generate_issue60_usability_fixture(Path(sys.argv[1]))\nprint(json.dumps(fixture.to_manifest(), ensure_ascii=False, sort_keys=True))`,
		[root]
	);
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

async function waitForHttp(url, timeoutMs = 45000) {
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

async function apiJson(apiBase, token, path, { method = 'GET', body = undefined } = {}) {
	const response = await fetch(`${apiBase}${path}`, {
		method,
		headers: {
			...(body === undefined ? {} : { 'content-type': 'application/json' }),
			...(token ? { authorization: `Bearer ${token}` } : {})
		},
		body: body === undefined ? undefined : JSON.stringify(body)
	});
	const text = await response.text();
	let parsed = null;
	try {
		parsed = text ? JSON.parse(text) : null;
	} catch {
		parsed = null;
	}
	return { status: response.status, body: parsed, text };
}

async function login(apiBase) {
	const response = await apiJson(apiBase, '', '/auth/login', {
		method: 'POST',
		body: { username: 'admin', password: adminPassword }
	});
	assert.equal(response.status, 200, `login failed: ${response.text}`);
	assert.ok(response.body?.access_token, 'login must return access_token');
	return response.body.access_token;
}

async function startApi({ appDbPath, allowedRoots, port, writesEnabled }) {
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
			GNUCASH_WRITES_ENABLED: writesEnabled ? 'true' : 'false'
		}
	});
	try {
		await waitForHttp(`http://127.0.0.1:${port}/health`);
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
		await waitForHttp(`http://127.0.0.1:${port}/login`);
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
		'--disable-background-networking',
		'--disable-component-update',
		'--disable-default-apps',
		'--disable-extensions',
		'--disable-sync',
		'--metrics-recording-only',
		'--no-first-run',
		'--remote-debugging-address=127.0.0.1',
		`--remote-debugging-port=${debugPort}`,
		`--user-data-dir=${profileDir}`,
		'--window-size=1280,900',
		'about:blank'
	]);
	const cdp = await connectCdp(debugPort);
	const state = { cdp, chromeProcess, consoleEvents: [], requests: [], responses: [], requestMethods: new Map() };
	cdp.on('Runtime.consoleAPICalled', (event) => {
		if (['error', 'warning'].includes(event.type)) state.consoleEvents.push(event);
	});
	cdp.on('Network.requestWillBeSent', (event) => {
		state.requestMethods.set(event.requestId, event.request.method);
		state.requests.push({ id: event.requestId, method: event.request.method, url: event.request.url });
	});
	cdp.on('Network.responseReceived', (event) => {
		state.responses.push({ id: event.requestId, method: state.requestMethods.get(event.requestId) ?? '', url: event.response.url, status: event.response.status });
	});
	await cdp.send('Page.enable');
	await cdp.send('Runtime.enable');
	await cdp.send('Network.enable');
	return state;
}

async function evaluate(cdp, expression, options = {}) {
	let result;
	try {
		result = await cdp.send('Runtime.evaluate', {
			expression,
			awaitPromise: options.awaitPromise ?? false,
			returnByValue: true,
			userGesture: true
		});
	} catch (error) {
		throw new Error(`${error.message} while evaluating ${expression.slice(0, 240).replace(/\s+/g, ' ')}`);
	}
	if (result.exceptionDetails) throw new Error(`Browser evaluation failed: ${JSON.stringify(result.exceptionDetails)}`);
	return result.result?.value;
}

async function waitForExpression(cdp, expression, label, timeoutMs = 30000) {
	const started = Date.now();
	while (Date.now() - started < timeoutMs) {
		if (await evaluate(cdp, expression)) return;
		await sleep(150);
	}
	const snapshot = await evaluate(cdp, `(() => ({ path: location.pathname, search: location.search, text: document.body.innerText.slice(0, 4000) }))()`);
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

async function setViewport(cdp, width, height = 900) {
	await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: width <= 480 ? 2 : 1, mobile: width <= 480 });
}

async function setSession(cdp, webBase, token, bookId, locale = 'en') {
	await cdp.send('Network.clearBrowserCookies');
	await cdp.send('Network.setCookie', { name: 'access_token', value: token, url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'selected_book_id', value: String(bookId), url: webBase, path: '/', sameSite: 'Lax' });
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: locale, url: webBase, path: '/', sameSite: 'Lax' });
}

async function navigate(cdp, webBase, path, label) {
	const load = waitForCdpEvent(cdp, 'Page.loadEventFired', label, 30000).catch(() => null);
	await cdp.send('Page.navigate', { url: `${webBase}${path}` });
	await Promise.race([load, waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path.split('?')[0])}`, label)]);
	await waitForExpression(cdp, `document.readyState !== 'loading' && location.pathname === ${jsString(path.split('?')[0])}`, label);
}

async function pageState(cdp) {
	return evaluate(cdp, `(() => ({
		text: document.body.innerText,
		html: document.documentElement.outerHTML,
		overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
		activeElementTag: document.activeElement?.tagName ?? '',
		activeElementText: document.activeElement?.textContent ?? ''
	}))()`);
}

function assertNoPrivateOrTechnicalLeak(state, label, { allowVisibleTemplateName = false } = {}) {
	assert.ok(state.overflowX <= 1, `${label}: no horizontal document overflow, got ${state.overflowX}`);
	assert.doesNotMatch(state.text, /\bXXX\b/, `${label}: no visible XXX pseudo-currency`);
	assert.doesNotMatch(state.text, /Root Account/, `${label}: structural Root Account must not be visible`);
	assert.doesNotMatch(state.text, /Template transaction must stay hidden/, `${label}: canonical template transaction must stay hidden`);
	assert.doesNotMatch(state.text, /[0-9a-f]{32}/i, `${label}: ordinary UI must not expose 32-hex GUIDs`);
	if (!allowVisibleTemplateName) assert.doesNotMatch(state.text, /Template Root\s+Template Root/, `${label}: canonical template root subtree must not be listed`);
}

async function assertDashboard(cdp, webBase, locale, width) {
	await setViewport(cdp, width, width <= 480 ? 920 : 900);
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: locale, url: webBase, path: '/', sameSite: 'Lax' });
	await navigate(cdp, webBase, `/dashboard?issue60_locale=${locale}&issue60_width=${width}`, `dashboard ${locale} ${width}`);
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(locale === 'ru' ? 'Обзор' : 'Dashboard')})`, `dashboard localized title ${locale}`);
	const state = await pageState(cdp);
	assertNoPrivateOrTechnicalLeak(state, `dashboard ${locale} ${width}`, { allowVisibleTemplateName: true });
	assert.match(state.text, /RUB/, `dashboard ${locale}: RUB reporting currency must be visible`);
	assert.doesNotMatch(
		state.text,
		locale === 'ru'
			? /(?:Капитал|Активы|Обязательства|Доходы|Расходы)[\s\S]{0,120}\bUSD\b/i
			: /(?:Net worth|Assets|Liabilities|Income|Expenses)[\s\S]{0,120}\bUSD\b/i,
		`dashboard ${locale}: USD must not be mixed into primary totals`
	);
	if (locale === 'ru') {
		for (const phrase of [
			'Другие валюты не включены: USD. Конвертация не выполняется.',
			'Ценные бумаги и невалютные товары не включены в денежные итоги.',
			'Откуда',
			'Куда',
			'Без описания',
			'Направление не удалось определить однозначно.',
			'Составная транзакция'
		]) assert.ok(state.text.includes(phrase), `dashboard RU must include ${phrase}`);
	} else {
		for (const phrase of [
			'Other currencies excluded: USD. No FX conversion is performed.',
			'Securities and non-currency commodities are excluded from money totals.',
			'From',
			'To',
			'No description',
			'Direction could not be determined unambiguously.',
			'Composite transaction'
		]) assert.ok(state.text.includes(phrase), `dashboard EN must include ${phrase}`);
	}
	for (const description of [
		'Зарплата июль',
		'Покупка стройматериалов',
		'Перевод Сбербанк ВТБ',
		'Кредитная карта продукты',
		'Покупка продукты и транспорт',
		'Две строки продуктов',
		'Нулевая техническая строка',
		'Один счет с обеих сторон',
		'Видимый счет с Template в имени'
	]) assert.ok(state.text.includes(description), `dashboard must show latest transaction ${description}`);
	for (const accountLabel of ['Сбербанк — Банки', 'ВТБ', 'Продукты', 'Транспорт', 'Кредитная карта']) {
		assert.ok(state.text.includes(accountLabel), `dashboard must show compact direction/account label ${accountLabel}`);
	}
	return { overflowX: state.overflowX, textLength: state.text.length };
}

async function assertAccounts(cdp, webBase, manifest, width) {
	await setViewport(cdp, width, width <= 480 ? 1000 : 900);
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'ru', url: webBase, path: '/', sameSite: 'Lax' });
	await navigate(cdp, webBase, '/accounts', `accounts ${width}`);
	const state = await pageState(cdp);
	assertNoPrivateOrTechnicalLeak(state, `accounts ${width}`, { allowVisibleTemplateName: true });
	for (const phrase of ['Сбербанк — Банки', 'Сбербанк — Бизнес', 'Template Root', 'Группа', 'Непроводимая группа']) {
		assert.ok(state.text.includes(phrase), `accounts page must include ${phrase}`);
	}
	assert.ok(state.html.includes(`/accounts/${encodeURIComponent(manifest.accounts.visible_template_named.id)}`), 'legitimate Template-named user account must be clickable');
	return { overflowX: state.overflowX };
}

async function assertCreateSelector(cdp, webBase, manifest) {
	await setViewport(cdp, 320, 1000);
	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });
	await navigate(cdp, webBase, '/transactions/new', 'new transaction create selector');
	await waitForExpression(cdp, `document.querySelector('#transaction-create-form')`, 'create form visible');
	const options = await evaluate(cdp, `Array.from(document.querySelectorAll('select[name="split_account_id"] option')).map((option) => ({ value: option.value, text: option.textContent.trim(), title: option.getAttribute('title') ?? '' }))`);
	const values = new Set(options.map((option) => option.value));
	for (const excludedKey of ['root', 'template_root', 'template_checking', 'template_food', 'assets', 'banks', 'business', 'liabilities', 'income', 'expenses', 'equity']) {
		if (manifest.accounts[excludedKey]) assert.equal(values.has(manifest.accounts[excludedKey].id), false, `CREATE selector excludes ${excludedKey}`);
	}
	for (const includedKey of ['sber', 'business_sber', 'products', 'fees', 'visible_template_named']) {
		assert.equal(values.has(manifest.accounts[includedKey].id), true, `CREATE selector includes postable ${includedKey}`);
	}
	assert.ok(options.some((option) => option.text.includes('Сбербанк — Банки')), 'CREATE selector uses duplicate-safe compact Sberbank label');
	assert.ok(options.some((option) => option.text.includes('Template Root')), 'CREATE selector keeps legitimate Template-named postable account');
	const state = await pageState(cdp);
	assertNoPrivateOrTechnicalLeak(state, 'create selector', { allowVisibleTemplateName: true });
	return { visibleOptions: options.filter((option) => option.value).length };
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
		return { book_id: get('book_id'), preview_token: get('preview_token'), idempotency_key: get('idempotency_key'), transaction_json: get('transaction_json') };
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

function backupEvidenceFor(targetPath) {
	const backupRoot = join(dirname(dirname(targetPath)), 'backups', basename(targetPath, '.sqlite'));
	const entries = existsSync(backupRoot) ? readdirSync(backupRoot).sort() : [];
	return {
		backupRoot,
		backupFiles: entries.filter((name) => !name.endsWith('.verified.json')),
		markerFiles: entries.filter((name) => name.endsWith('.verified.json'))
	};
}

async function runCreateFlow({ cdp, webBase, apiBase, token, bookId, appDbPath, manifest }) {
	const request = {
		date: '2026-07-21',
		description: 'Issue60 UI CREATE контроль',
		currency: 'RUB',
		splits: [
			{ account_id: manifest.accounts.sber.id, amount: '-321.45', memo: 'issue60 from bank' },
			{ account_id: manifest.accounts.fees.id, amount: '321.45', memo: 'issue60 to fees' }
		]
	};
	const sourceHashBefore = hashFile(manifest.source_path);
	const targetHashBefore = hashFile(manifest.target_path);
	const sourceSnapshotBefore = bookSnapshot(manifest.source_path);
	const targetSnapshotBefore = bookSnapshot(manifest.target_path);
	assert.equal(sourceHashBefore, manifest.source_hash, 'generated source hash before CREATE');
	assert.equal(targetHashBefore, manifest.target_hash_before, 'target starts as disposable copy of source');

	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'en', url: webBase, path: '/', sameSite: 'Lax' });
	await navigate(cdp, webBase, '/transactions/new', 'CREATE flow page');
	await fillTransactionForm(cdp, request);
	await submitPreview(cdp);
	await waitForExpression(cdp, `document.querySelector('#normalized-preview') && document.querySelector('#confirm-create-form')`, 'preview and confirm form visible');
	const hidden = await readConfirmHidden(cdp);
	assert.ok(hidden.preview_token.startsWith('pt1.'), 'real preview token shape');
	assert.ok(hidden.idempotency_key.length >= 16, 'idempotency key shape');

	await submitConfirmForm(cdp);
	await waitForExpression(cdp, `location.pathname === '/transactions' && location.search.includes('create_status=created')`, 'created redirect');
	const succeededAfterCreate = queryAppDb(appDbPath, 'SELECT planned_transaction_guid FROM transaction_create_idempotency WHERE book_id = ? AND state = ? ORDER BY id', [bookId, 'succeeded']);
	assert.equal(succeededAfterCreate.length, 1, 'one succeeded idempotency after first confirm');
	const transactionId = succeededAfterCreate[0].planned_transaction_guid;
	assert.match(transactionId, /^[0-9a-f]{32}$/, 'planned transaction GUID shape');

	const duplicate = await browserReplayConfirm(cdp, hidden);
	assert.ok([200, 303].includes(duplicate.status), `duplicate confirm status ${duplicate.status}`);
	if (duplicate.status === 303) assert.ok(duplicate.location.includes('already_created'), 'duplicate confirm redirects as already_created');

	const detail = await apiJson(apiBase, token, `/books/${bookId}/transactions/${transactionId}`);
	assert.equal(detail.status, 200, `created transaction detail readback: ${detail.text}`);
	assert.equal(detail.body.description, request.description, 'created detail description');
	assert.equal(detail.body.is_write_alpha_owned, true, 'created detail ownership flag');
	assert.deepEqual(
		[...detail.body.splits].map((split) => [split.account_id, split.amount, split.memo]).sort(),
		request.splits.map((split) => [split.account_id, split.amount, split.memo]).sort(),
		'created split readback exact accounts/amounts/memos'
	);
	const directSnapshotAfter = bookSnapshot(manifest.target_path, transactionId);
	assert.equal(directSnapshotAfter.transactions, targetSnapshotBefore.transactions + 1, 'exactly one target transaction after duplicate');
	assert.equal(directSnapshotAfter.splits, targetSnapshotBefore.splits + request.splits.length, 'exact target split increment after duplicate');
	assert.ok(directSnapshotAfter.transaction, 'direct reopened target transaction exists');
	assert.equal(bookSnapshot(manifest.source_path).transactions, sourceSnapshotBefore.transactions, 'source transaction count unchanged');
	assert.equal(bookSnapshot(manifest.source_path).splits, sourceSnapshotBefore.splits, 'source split count unchanged');
	const sourceHashAfter = hashFile(manifest.source_path);
	const targetHashAfter = hashFile(manifest.target_path);
	assert.equal(sourceHashAfter, sourceHashBefore, 'source hash unchanged after CREATE');
	assert.notEqual(targetHashAfter, targetHashBefore, 'target hash changed after CREATE');

	const backup = backupEvidenceFor(manifest.target_path);
	assert.equal(backup.backupFiles.length, 1, 'exactly one backup file');
	assert.equal(backup.markerFiles.length, 1, 'exactly one verified backup marker');
	assert.equal(hashFile(join(backup.backupRoot, backup.backupFiles[0])), targetHashBefore, 'backup hash equals pre-create target');
	const idempotencyRows = queryAppDb(appDbPath, 'SELECT state, safe_error_code, planned_transaction_guid FROM transaction_create_idempotency WHERE book_id = ? ORDER BY id', [bookId]);
	const ownershipRows = queryAppDb(appDbPath, 'SELECT transaction_id FROM write_alpha_transaction_ownership WHERE book_id = ? ORDER BY id', [bookId]);
	const auditRows = queryAppDb(appDbPath, 'SELECT action, payload_json FROM audit_logs WHERE book_id = ? ORDER BY id', [bookId]);
	assert.equal(idempotencyRows.filter((row) => row.state === 'succeeded').length, 1, 'one succeeded idempotency row');
	assert.equal(ownershipRows.length, 1, 'one ownership row');
	assert.equal(ownershipRows[0].transaction_id, transactionId, 'ownership row transaction id');
	assert.ok(auditRows.filter((row) => row.action === 'transaction.create.confirm').length >= 3, 'audit contains confirm started/success/duplicate stages');

	await cdp.send('Network.setCookie', { name: 'ui_locale', value: 'ru', url: webBase, path: '/', sameSite: 'Lax' });
	await navigate(cdp, webBase, `/transactions?date_from=${request.date}&date_to=${request.date}&query=${encodeURIComponent(request.description)}&sort=date_desc&page_size=50`, 'created transaction explorer read path');
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(request.description)}) && document.body.innerText.includes('Откуда') && document.body.innerText.includes('Куда')`, 'created transaction visible with RU direction');
	await navigate(cdp, webBase, '/dashboard', 'dashboard after create');
	await waitForExpression(cdp, `document.body.innerText.includes(${jsString(request.description)}) && document.body.innerText.includes('Комиссии')`, 'created transaction appears in dashboard latest');

	return {
		transaction_id: transactionId,
		source_hash_before: sourceHashBefore,
		source_hash_after: sourceHashAfter,
		target_hash_before: targetHashBefore,
		target_hash_after: targetHashAfter,
		target_counts: { before: targetSnapshotBefore, after: { transactions: directSnapshotAfter.transactions, splits: directSnapshotAfter.splits } },
		backup_files: backup.backupFiles.length,
		verified_backup_markers: backup.markerFiles.length,
		idempotency_rows: idempotencyRows.length,
		ownership_rows: ownershipRows.length,
		audit_rows: auditRows.length,
		duplicate_status: duplicate.status
	};
}

function assertTrackedHygiene() {
	const hygiene = spawnSync(apiPython, [join(repoRoot, 'scripts', 'check_tracked_hygiene.py')], {
		cwd: repoRoot,
		env: { ...process.env, PATH: apiPythonPath() },
		encoding: 'utf8',
		maxBuffer: 20 * 1024 * 1024
	});
	assert.equal(hygiene.status, 0, `tracked hygiene guard failed\nstdout:\n${hygiene.stdout}\nstderr:\n${hygiene.stderr}`);
	const forbidden = changedOrUntrackedIssue60Paths().filter(isRawRuntimeOrPrivateArtifact);
	assert.deepEqual(forbidden, [], 'no newly introduced raw fixture/app DB/backup/private artifacts are tracked or pending');
	return { tracked_forbidden_artifacts: forbidden.length };
}

async function runSmoke() {
	assert.ok(apiPython === 'python' || existsSync(apiPython), `backend Python missing at ${apiPython}`);
	assert.ok(existsSync(viteBin), 'Vite must be installed before running issue60 browser gate');
	assert.ok(existsSync(previewServerIndex), 'Build output must exist before issue60 browser gate; run npm run build first');
	assert.ok(existsSync(chromiumBin), `Chromium binary not found at ${chromiumBin}`);
	const packageJson = JSON.parse(readFileSync(join(webRoot, 'package.json'), 'utf8'));
	assert.equal(packageJson.scripts?.['test:issue60-usability-browser'], 'npm run build && node scripts/test-issue60-usability-browser.mjs', 'package.json must expose the issue60 generated-real-book browser gate');

	const tempRoot = mkdtempSync(join(tmpdir(), 'gwc-issue60-usability-'));
	let apiProcess;
	let webProcess;
	let browser;
	try {
		const fixtureRoot = join(tempRoot, 'fixture');
		const manifest = generateIssue60Manifest(fixtureRoot);
		assert.equal(manifest.seed, 60060, 'issue60 fixture seed must be stable');
		assert.equal(hashFile(manifest.source_path), manifest.source_hash, 'source hash matches manifest');
		assert.equal(hashFile(manifest.target_path), manifest.target_hash_before, 'target hash matches manifest');
		assert.equal(manifest.source_hash, manifest.target_hash_before, 'target starts as source copy');
		assert.equal(manifest.expected.owner_private_access_count, 0, 'fixture owner/private counter starts zero');

		const appDbPath = join(tempRoot, 'app', 'app.db');
		const apiPort = await getFreePort();
		const webPort = await getFreePort();
		const apiBase = `http://127.0.0.1:${apiPort}`;
		const webBase = `http://127.0.0.1:${webPort}`;
		const allBrowserRequests = [];
		const allConsoleEvents = [];
		const launchBrowser = async (locale) => {
			if (browser) {
				allBrowserRequests.push(...browser.requests);
				allConsoleEvents.push(...browser.consoleEvents);
				browser.cdp.close();
				await stopProcess(browser.chromeProcess);
			}
			const profileDir = mkdtempSync(join(tempRoot, 'chrome-'));
			browser = await startBrowser({ profileDir, debugPort: await getFreePort() });
			await setSession(browser.cdp, webBase, token, bookId, locale);
		};
		apiProcess = await startApi({ appDbPath, allowedRoots: [fixtureRoot], port: apiPort, writesEnabled: true });
		const token = await login(apiBase);
		const bookRequest = { name: 'Issue60 generated usability book', storage_type: 'sqlite', uri_or_path: manifest.target_path, base_currency: 'RUB', make_default: true };
		const preflight = await apiJson(apiBase, token, '/books/preflight', { method: 'POST', body: bookRequest });
		assert.equal(preflight.status, 200, `preflight failed: ${preflight.text}`);
		assert.equal(preflight.body.status, 'ready', 'preflight ready');
		const registered = await apiJson(apiBase, token, '/books', { method: 'POST', body: { ...bookRequest, preflight_token: preflight.body.preflight_token } });
		assert.equal(registered.status, 201, `registration failed: ${registered.text}`);
		const bookId = registered.body.id;
		assert.ok(Number.isInteger(bookId), 'registered book id');
		const defaultCreateSettings = await apiJson(apiBase, token, `/books/${bookId}/transaction-create-settings`);
		assert.equal(defaultCreateSettings.status, 200, 'default create settings readable');
		assert.equal(defaultCreateSettings.body.enabled, false, 'per-book CREATE is default OFF before isolated enablement');
		const enabled = await apiJson(apiBase, token, `/books/${bookId}/transaction-create-settings`, { method: 'PATCH', body: { enabled: true } });
		assert.equal(enabled.status, 200, `enable create failed: ${enabled.text}`);
		assert.equal(enabled.body.enabled, true, 'isolated book CREATE enabled');

		const summary = await apiJson(apiBase, token, `/books/${bookId}/reports/summary`);
		assert.equal(summary.status, 200, `summary failed: ${summary.text}`);
		assert.equal(summary.body.status, 'ready', 'summary ready');
		assert.equal(summary.body.currency, 'RUB', 'summary selected RUB');
		assert.equal(summary.body.includes_currency_conversion, false, 'summary no FX conversion');
		assert.equal(summary.body.reporting_currency.selected_currency, 'RUB', 'reporting currency selected RUB');
		assert.deepEqual(summary.body.reporting_currency.excluded_currencies, ['USD'], 'USD excluded, not mixed');
		assert.equal(summary.body.reporting_currency.non_currency_commodities_excluded, true, 'BTC/non-currency excluded');
		assert.doesNotMatch(JSON.stringify(summary.body), /XXX/, 'summary API does not synthesize XXX');

		const recent = await apiJson(apiBase, token, `/books/${bookId}/reports/recent-transactions?limit=50`);
		assert.equal(recent.status, 200, `recent failed: ${recent.text}`);
		const recentIds = new Set(recent.body.map((tx) => tx.id));
		assert.equal(recentIds.has(manifest.transactions.template_hidden), false, 'canonical template transaction excluded from ordinary recent API');
		for (const key of ['salary', 'building', 'transfer', 'three_split', 'card', 'repeated', 'zero', 'empty_description', 'usd', 'security', 'same_account_both_sides', 'visible_template_named']) {
			assert.equal(recentIds.has(manifest.transactions[key]), true, `ordinary recent includes ${key}`);
		}

		webProcess = await startWeb({ apiBase, port: webPort });
		await launchBrowser('ru');

		console.log('issue60-browser: dashboard ru desktop');
		const dashboardDesktop = await assertDashboard(browser.cdp, webBase, 'ru', 1280);
		console.log('issue60-browser: dashboard ru mobile');
		const dashboardMobile = await assertDashboard(browser.cdp, webBase, 'ru', 320);
		await launchBrowser('en');
		console.log('issue60-browser: dashboard en desktop');
		const dashboardEnglish = await assertDashboard(browser.cdp, webBase, 'en', 1280);
		await launchBrowser('ru');
		console.log('issue60-browser: accounts mobile');
		const accountsMobile = await assertAccounts(browser.cdp, webBase, manifest, 320);
		console.log('issue60-browser: create selector');
		const createSelector = await assertCreateSelector(browser.cdp, webBase, manifest);
		console.log('issue60-browser: controlled CREATE flow');
		const create = await runCreateFlow({ cdp: browser.cdp, webBase, apiBase, token, bookId, appDbPath, manifest });
		const hygiene = assertTrackedHygiene();

		const collectedRequests = [...allBrowserRequests, ...browser.requests];
		const collectedConsoleEvents = [...allConsoleEvents, ...browser.consoleEvents];
		const forbiddenBrowserMutations = collectedRequests.filter((request) => {
			const url = new URL(request.url, 'http://127.0.0.1');
			return ['PATCH', 'DELETE', 'PUT'].includes(request.method) || /batch|import|ofx|csv|upload|source_deletion/i.test(url.pathname + url.search);
		});
		assert.deepEqual(forbiddenBrowserMutations, [], 'browser must not send forbidden PATCH/DELETE/PUT/batch/import/upload/source-deletion requests');
		assert.deepEqual(collectedConsoleEvents, [], 'browser console must not contain warnings/errors');
		assert.equal(hashFile(manifest.source_path), manifest.source_hash, 'final generated source hash unchanged');

		const counters = {
			fixture_seed: manifest.seed,
			source_create_count: 1,
			disposable_copy_count: 1,
			target_create_count: 1,
			target_duplicate_confirm_count: 1,
			target_patch_count: 0,
			target_delete_count: 0,
			owner_private_access_count: 0,
			committed_raw_artifacts: hygiene.tracked_forbidden_artifacts,
			browser_forbidden_mutations: forbiddenBrowserMutations.length,
			console_events: collectedConsoleEvents.length
		};
		assert.deepEqual(counters, {
			fixture_seed: 60060,
			source_create_count: 1,
			disposable_copy_count: 1,
			target_create_count: 1,
			target_duplicate_confirm_count: 1,
			target_patch_count: 0,
			target_delete_count: 0,
			owner_private_access_count: 0,
			committed_raw_artifacts: 0,
			browser_forbidden_mutations: 0,
			console_events: 0
		}, 'issue60 safety counters');
		const result = {
			book_id: bookId,
			dashboard_desktop: dashboardDesktop,
			dashboard_mobile: dashboardMobile,
			dashboard_english: dashboardEnglish,
			accounts_mobile: accountsMobile,
			create_selector: createSelector,
			create,
			counters,
			source_hash_before: manifest.source_hash,
			source_hash_after: hashFile(manifest.source_path),
			temp_root_cleaned_by_trap: true
		};
		console.log(`ok - issue60 generated usability browser gate passed book=${bookId} create=${create.transaction_id} source_hash=${result.source_hash_after}`);
		console.log(`ISSUE60_USABILITY_BROWSER_SUMMARY ${JSON.stringify(result, sortKeysReplacer, 0)}`);
		return result;
	} finally {
		browser?.cdp?.close();
		await stopProcess(browser?.chromeProcess);
		await stopProcess(webProcess);
		await stopProcess(apiProcess);
		await removeTempRoot(tempRoot);
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
