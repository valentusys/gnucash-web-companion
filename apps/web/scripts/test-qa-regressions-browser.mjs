// Synthetic-only read-only acceptance against REAL FastAPI + built SvelteKit.
// No legacy CREATE runner is imported. Every child stays in the caller's cgroup.
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { createServer } from 'node:http';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = resolve(webRoot, '../..');
const apiRoot = join(repoRoot, 'apps/api');
const apiPython = process.env.API_PYTHON ?? 'python';
const chromeBin = process.env.CHROMIUM_BIN ?? '/usr/bin/google-chrome';
const evidenceParent = process.env.QA_EVIDENCE_DIR ?? tmpdir();
mkdirSync(evidenceParent, { recursive: true });
const root = mkdtempSync(join(evidenceParent, 'gwc-qa-readonly-'));
const children = [];
const browserRequests = [];
const apiRequests = [];
const browserErrors = [];
const ports = [];
let proxy;
let cdp;
let fixture;
let failure;
const hash = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
const delay = (ms) => new Promise((done) => setTimeout(done, ms));
const started = Date.now();
const scenario = process.env.QA_SCENARIO ?? 'scheduled_partial';
const evidence = { head: '', scenario, status: 'INCOMPLETE' };

function pythonJson(code, args = []) {
    const result = spawnSync(apiPython, ['-c', code, ...args], {
        cwd: apiRoot, env: { ...process.env, PYTHONPATH: apiRoot, GNUCASH_WRITES_ENABLED: 'false' },
        encoding: 'utf8', timeout: 30000,
    });
    assert.equal(result.status, 0, `synthetic Python helper failed: ${result.stderr}`);
    return JSON.parse(result.stdout);
}

function start(command, args, env, cwd, label) {
    const child = spawn(command, args, { cwd, env, stdio: ['ignore', 'pipe', 'pipe'], detached: false });
    children.push(child); // Register before any readiness check, including failed startup.
    let output = '';
    for (const stream of [child.stdout, child.stderr]) stream.on('data', (chunk) => { output = (output + chunk).slice(-30000); });
    child.on('error', (error) => { output += error.message; });
    child.qaOutput = () => output;
    child.qaLabel = label;
    return child;
}

async function stop(child) {
    if (child.exitCode !== null || child.signalCode !== null) return;
    child.kill('SIGTERM');
    for (let index = 0; index < 30 && child.exitCode === null && child.signalCode === null; index++) await delay(100);
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    for (let index = 0; index < 30 && child.exitCode === null && child.signalCode === null; index++) await delay(100);
    assert.ok(child.exitCode !== null || child.signalCode !== null, `${child.qaLabel} must stop`);
}

async function freePort() {
    const server = net.createServer();
    await new Promise((done, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', done); });
    const port = server.address().port;
    await new Promise((done) => server.close(done));
    ports.push(port);
    return port;
}

async function waitHttp(url) {
    for (let index = 0; index < 150; index++) {
        try { if ((await fetch(url, { signal: AbortSignal.timeout(1000) })).ok) return; } catch { /* bounded readiness retry */ }
        const exited = children.find((child) => child.exitCode !== null || child.signalCode !== null);
        if (exited) throw new Error(`${exited.qaLabel} exited: ${exited.qaOutput()}`);
        await delay(200);
    }
    throw new Error(`Readiness timeout: ${url}`);
}

class Cdp {
    pending = new Map();
    nextId = 1;
    loadCount = 0;
    async connect(url) {
        this.ws = new WebSocket(url);
        await new Promise((done, reject) => { this.ws.addEventListener('open', done, { once: true }); this.ws.addEventListener('error', reject, { once: true }); });
        this.ws.addEventListener('message', ({ data }) => {
            const message = JSON.parse(data);
            if (message.id) {
                const pending = this.pending.get(message.id);
                if (!pending) return;
                this.pending.delete(message.id);
                clearTimeout(pending.timer);
                message.error ? pending.reject(new Error(message.error.message)) : pending.done(message.result);
            } else if (message.method === 'Page.loadEventFired') {
                this.loadCount++;
            } else if (message.method === 'Network.requestWillBeSent') {
                const request = message.params.request;
                browserRequests.push({ method: request.method, path: new URL(request.url).pathname });
            } else if (message.method === 'Runtime.exceptionThrown') {
                browserErrors.push(message.params.exceptionDetails.text);
            } else if (message.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(message.params.type)) {
                browserErrors.push(message.params.args.map((arg) => arg.value ?? arg.description).join(' '));
            }
        });
    }
    send(method, params = {}) {
        const id = this.nextId++;
        return new Promise((done, reject) => {
            const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 90000);
            this.pending.set(id, { done, reject, timer });
            this.ws.send(JSON.stringify({ id, method, params }));
        });
    }
    async evaluate(expression) {
        const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, userGesture: true });
        assert.ok(!result.exceptionDetails, JSON.stringify(result.exceptionDetails));
        return result.result?.value;
    }
    async wait(expression) {
        for (let index = 0; index < 150; index++) {
            if (await this.evaluate(expression)) return;
            await delay(100);
        }
        throw new Error(`DOM condition failed: ${expression}`);
    }
    async navigate(url) {
        const before = this.loadCount;
        await this.send('Page.navigate', { url });
        for (let index = 0; index < 300 && this.loadCount === before; index++) await delay(100);
        assert.ok(this.loadCount > before, 'A new document must load before DOM assertions');
    }
    close() {
        this.ws?.close();
        for (const pending of this.pending.values()) { clearTimeout(pending.timer); pending.reject(new Error('CDP closed')); }
        this.pending.clear();
    }
}

const watchdog = setTimeout(() => { failure = new Error('Acceptance exceeded 180-second bound'); for (const child of children) child.kill('SIGTERM'); }, 180000);
try {
    assert.ok(existsSync(join(webRoot, 'build/index.js')), 'Run npm run build once before browser cases');
    const git = spawnSync('git', ['-C', repoRoot, 'rev-parse', 'HEAD'], { encoding: 'utf8' });
    assert.equal(git.status, 0);
    evidence.head = git.stdout.trim();
    evidence.dirty_files = spawnSync('git', ['-C', repoRoot, 'status', '--porcelain'], { encoding: 'utf8' }).stdout.trim().split('\n').filter(Boolean);
    fixture = pythonJson('import json,sys\nfrom tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture\nprint(json.dumps(generate_qa_regression_fixture(sys.argv[1], scenario=sys.argv[2])))', [join(root, 'generated'), scenario]);
    evidence.seed = fixture.seed;
    evidence.hash_before = fixture.sha256;
    const apiPort = await freePort();
    const webPort = await freePort();
    const debugPort = await freePort();
    const apiBase = `http://127.0.0.1:${apiPort}`;
    const webBase = `http://127.0.0.1:${webPort}`;
    const password = randomBytes(24).toString('hex');
    const apiEnv = {
        ...process.env, PYTHONPATH: apiRoot, APP_ENV: 'test',
        APP_DATABASE_URL: `sqlite:///${join(root, 'app.db')}`,
        GNUCASH_DEFAULT_BOOK_PATH: fixture.book_path,
        GNUCASH_BOOK_ALLOWED_ROOTS: JSON.stringify([join(root, 'generated')]),
        GNUCASH_WRITES_ENABLED: 'false', JWT_SECRET: randomBytes(48).toString('hex'),
        APP_ADMIN_USERNAME: 'admin', APP_ADMIN_PASSWORD: password, APP_ADMIN_PASSWORD_HASH: '',
    };
    start(apiPython, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(apiPort)], apiEnv, apiRoot, 'api');
    await waitHttp(`${apiBase}/health`);
    // Transparent proxy observes real web→API responses. No response stubs/DTO rewriting.
    proxy = createServer(async (request, response) => {
        const record = { method: request.method, path: new URL(request.url, apiBase).pathname, status: null };
        apiRequests.push(record);
        try {
            const chunks = [];
            for await (const chunk of request) chunks.push(chunk);
            const headers = { ...request.headers }; delete headers.host; delete headers.connection;
            const upstream = await fetch(`${apiBase}${request.url}`, {
                method: request.method, headers, redirect: 'manual',
                body: ['GET', 'HEAD'].includes(request.method) ? undefined : Buffer.concat(chunks),
                signal: AbortSignal.timeout(15000),
            });
            record.status = upstream.status;
            response.writeHead(upstream.status, { 'content-type': upstream.headers.get('content-type') ?? 'application/json' });
            response.end(Buffer.from(await upstream.arrayBuffer()));
        } catch { record.status = 502; response.writeHead(502); response.end(); }
    });
    await new Promise((done, reject) => { proxy.once('error', reject); proxy.listen(0, '127.0.0.1', done); });
    const proxyPort = proxy.address().port; ports.push(proxyPort);
    start(process.execPath, [join(webRoot, 'node_modules/vite/bin/vite.js'), 'preview', '--host', '127.0.0.1', '--port', String(webPort), '--strictPort'], {
        ...process.env, HOST: '127.0.0.1', PORT: String(webPort), ORIGIN: webBase,
        API_INTERNAL_URL: `http://127.0.0.1:${proxyPort}`,
    }, webRoot, 'web');
    await waitHttp(`${webBase}/login`);
    start(chromeBin, ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
        '--disable-background-networking', '--disable-component-update', '--no-first-run',
        '--remote-debugging-address=127.0.0.1', `--remote-debugging-port=${debugPort}`,
        `--user-data-dir=${join(root, 'chrome-profile')}`, '--window-size=1440,1000', 'about:blank'], {
            ...process.env,
            // Chromium's XDG portal integration otherwise calls StartTransientUnit
            // and moves itself out of the controller cgroup. No desktop bus in tests.
            DBUS_SESSION_BUS_ADDRESS: `unix:path=${join(root, 'no-session-bus')}`,
            DBUS_SYSTEM_BUS_ADDRESS: `unix:path=${join(root, 'no-system-bus')}`,
        }, webRoot, 'chrome');
    await waitHttp(`http://127.0.0.1:${debugPort}/json/list`);
    const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
    cdp = new Cdp(); await cdp.connect(targets.find((target) => target.type === 'page').webSocketDebuggerUrl);
    for (const domain of ['Page', 'Runtime', 'Network']) await cdp.send(`${domain}.enable`);
    if (existsSync('/proc/self/cgroup')) {
        const group = readFileSync('/proc/self/cgroup', 'utf8');
        for (const child of children) assert.equal(readFileSync(`/proc/${child.pid}/cgroup`, 'utf8'), group, 'test runtime must remain in caller cgroup');
        evidence.cgroup_verified = true;
    }
    await cdp.navigate(`${webBase}/login`);
    await cdp.wait('document.querySelector("input[name=username]")');
    await cdp.evaluate(`document.querySelector('input[name=username]').value='admin'; document.querySelector('input[name=password]').value=${JSON.stringify(password)}; document.querySelector('button[type=submit]').click()`);
    await cdp.wait('location.pathname === "/dashboard" && document.querySelector("main")');
    const expectedInvalid = fixture.invalid_schedule_ids.length;
    const expectedRows = fixture.valid_schedule_ids.length + expectedInvalid;
    evidence.cases = [];
    for (const [locale, width] of [['en', 1440], ['ru', 390]]) {
        await cdp.send('Network.setCookie', { name: 'ui_locale', value: locale, url: webBase, path: '/', sameSite: 'Lax' });
        await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: width < 500 });
        await cdp.navigate(`${webBase}/scheduled`);
        // Assertion, not a timeout: baseline must show the real 422 page rather than 16 rows.
        const rows = await cdp.evaluate('document.querySelectorAll("[data-schedule-row]").length');
        assert.equal(rows, expectedRows, 'QA-01 real backend must render valid schedules plus diagnostic rows');
        assert.equal(await cdp.evaluate('document.querySelectorAll("[data-schedule-group=unavailable] [data-schedule-row]").length'), expectedInvalid);
        const warning = await cdp.evaluate('document.querySelector("[data-forecast-incomplete]")?.innerText ?? ""');
        assert.equal(Boolean(warning), expectedInvalid > 0);
        if (expectedInvalid) assert.match(warning, locale === 'ru' ? /Прогноз неполный/ : /Forecast incomplete/);
        const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png' });
        writeFileSync(join(root, `synthetic-scheduled-${locale}.png`), Buffer.from(screenshot.data, 'base64'), { mode: 0o600 });
        await cdp.navigate(`${webBase}/dashboard`);
        assert.equal(await cdp.evaluate('Boolean(document.querySelector("[data-obligations-incomplete]"))'), expectedInvalid > 0, 'Dashboard must disclose incomplete forecast even when reporting needs setup');
        evidence.cases.push({ locale, width, scheduled_rows: rows, unavailable_rows: expectedInvalid });
    }
    assert.ok(apiRequests.some((r) => r.path.endsWith('/scheduled-transactions') && r.status === 200));
    assert.deepEqual(browserErrors, []);
    evidence.status = 'PASS';
} catch (error) {
    failure = error;
    evidence.status = 'FAIL';
    evidence.error = error.message;
} finally {
    clearTimeout(watchdog);
    cdp?.close();
    const cleanupErrors = [];
    for (const child of [...children].reverse()) {
        try { await stop(child); } catch (error) { cleanupErrors.push(error.message); }
    }
    if (proxy) { proxy.closeAllConnections(); await new Promise((done) => proxy.close(done)); }
    for (const port of ports) {
        const open = await new Promise((done) => {
            const socket = net.connect({ port, host: '127.0.0.1' });
            socket.once('connect', () => { socket.destroy(); done(true); });
            socket.once('error', () => done(false));
        });
        if (open) cleanupErrors.push(`port ${port} still open`);
    }
    evidence.runtime_stopped = cleanupErrors.length === 0;
    evidence.api_requests = apiRequests;
    evidence.browser_requests = browserRequests;
    evidence.book_mutation_requests = [...browserRequests, ...apiRequests].filter((r) => !['GET', 'HEAD', 'OPTIONS'].includes(r.method) && !['/login', '/auth/login', '/logout'].includes(r.path));
    if (fixture) {
        evidence.hash_after = hash(fixture.book_path);
        if (evidence.hash_after !== evidence.hash_before) cleanupErrors.push('Generated book changed');
        evidence.quick_check = pythonJson('import json,sqlite3,sys\nwith sqlite3.connect("file:"+sys.argv[1]+"?mode=ro",uri=True) as db:\n print(json.dumps(db.execute("pragma quick_check").fetchone()[0]))', [fixture.book_path]);
        if (evidence.quick_check !== 'ok') cleanupErrors.push('SQLite quick_check failed');
    }
    if (evidence.book_mutation_requests.length) cleanupErrors.push('Unexpected mutation request');
    if (cleanupErrors.length) { evidence.status = 'FAIL'; failure ??= new Error(cleanupErrors.join('; ')); }
    evidence.cleanup_errors = cleanupErrors;
    evidence.elapsed_ms = Date.now() - started;
    if (failure) for (const child of children) writeFileSync(join(root, `${child.qaLabel}.log`), child.qaOutput(), { mode: 0o600 });
    writeFileSync(join(root, 'evidence.json'), JSON.stringify(evidence, null, 2), { mode: 0o600 });
    console.log(JSON.stringify({ status: evidence.status, evidence: join(root, 'evidence.json'), runtime_stopped: evidence.runtime_stopped, book_mutation_requests: evidence.book_mutation_requests.length }));
}
if (failure) throw failure;
