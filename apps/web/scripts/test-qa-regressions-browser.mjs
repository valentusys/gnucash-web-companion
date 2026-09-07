// Synthetic-only read-only acceptance against REAL FastAPI + built SvelteKit.
// No legacy CREATE runner is imported. Every child stays in the caller's cgroup.
import assert from 'node:assert/strict';
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { createServer } from 'node:http';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';
import { compareDecimalStrings } from '../src/lib/money.js';
import { isReadOnlyQaRequest } from './qa-request-policy.mjs';

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
const additionalFixtures = [];
let alternateBookId;
let currencyResolution;
let recentPayload;
let explorerPayload;
let overviewPayload;
let previewPayload;
let disconnectPreview = false;
let summaryAsOf;
let scheduledAsOf = [];
let scopeIds;
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
                const url = new URL(request.url);
                browserRequests.push({ method: request.method, path: url.pathname, search: url.search });
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
    if (process.env.QA_FORM_CURRENCY === '1' && scenario === 'money') {
        additionalFixtures.push(pythonJson('import json,sys\nfrom tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture\nprint(json.dumps(generate_qa_regression_fixture(sys.argv[1], scenario="currency_eur")))', [join(root, 'generated', 'alternate')]));
    }
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
    const clockInstant = process.env.QA_REPORTING_INSTANT;
    const clockZone = process.env.QA_REPORTING_ZONE ?? 'UTC';
    const expectedClockDate = clockInstant ? pythonJson('import json,sys\nfrom datetime import datetime\nfrom zoneinfo import ZoneInfo\nprint(json.dumps(datetime.fromisoformat(sys.argv[1]).astimezone(ZoneInfo(sys.argv[2])).date().isoformat()))', [clockInstant, clockZone]) : null;
    // Test-only clock injection before app import; no production freeze-clock setting and no host clock/TZ changes.
    const apiArgs = clockInstant
        ? ['-c', 'import sys,uvicorn\nfrom datetime import datetime\nfrom zoneinfo import ZoneInfo\nfrom app.services import reporting_clock\nfrozen=datetime.fromisoformat(sys.argv[1]).astimezone(ZoneInfo(sys.argv[2])).date()\nreporting_clock.reporting_today=lambda:frozen\nuvicorn.run("app.main:app",host="127.0.0.1",port=int(sys.argv[3]))', clockInstant, clockZone, String(apiPort)]
        : ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(apiPort)];
    if (clockInstant) evidence.clock = { instant: clockInstant, zone: clockZone, as_of_date: expectedClockDate };
    start(apiPython, apiArgs, apiEnv, apiRoot, 'api');
    await waitHttp(`${apiBase}/health`);
    if (additionalFixtures.length) {
        alternateBookId = pythonJson('import json,sqlite3,sys\nwith sqlite3.connect(sys.argv[1]) as db:\n row=db.execute("SELECT base_currency FROM books WHERE uri_or_path=?",(sys.argv[2],)).fetchone()\n assert row == (None,), row\n cursor=db.execute("INSERT INTO books(name,storage_type,uri_or_path,base_currency,is_default,is_archived,is_enabled,transaction_create_enabled,transaction_create_generation,transaction_create_recovery_required,created_at,updated_at) VALUES (?, ?, ?, NULL,0,0,1,0,1,0,?,?)",("SYNTHETIC Alternate EUR","sqlite",sys.argv[3],"2026-09-01 00:00:00","2026-09-01 00:00:00"))\n book_id=cursor.lastrowid\n db.execute("INSERT INTO user_book_access(user_id,book_id,role) SELECT id,?,? FROM users WHERE username=?",(book_id,"owner","admin"))\n assert db.execute("SELECT base_currency,transaction_create_enabled FROM books WHERE id=?",(book_id,)).fetchone()==(None,0)\n print(json.dumps(book_id))', [join(root,'app.db'),fixture.book_path,additionalFixtures[0].book_path]);
        evidence.synthetic_app_metadata_registered_books = 1;
    }
    if (['money', 'recent_sparse', 'pagination'].includes(scenario) && !process.env.QA_FORM_CURRENCY) {
        // Isolated synthetic APP metadata setup only; never writes the generated GnuCash book.
        scopeIds = pythonJson('import json,sqlite3,sys\nfrom tests.support.generate_qa_regression_fixture import guid\nwith sqlite3.connect(sys.argv[1]) as db:\n cursor=db.execute("UPDATE books SET base_currency=? WHERE uri_or_path=?", ("RUB",sys.argv[2]))\n assert cursor.rowcount == 1\nprint(json.dumps({name:guid("account:"+name) for name in ["cash","expense","savings"]}))', [join(root, 'app.db'), fixture.book_path]);
        evidence.synthetic_app_metadata_setup_updates = 1;
    }
    // Transparent proxy observes real web→API responses. No response stubs/DTO rewriting.
    proxy = createServer(async (request, response) => {
        const requestUrl = new URL(request.url, apiBase);
        const record = { method: request.method, path: requestUrl.pathname, search: requestUrl.search, query: Object.fromEntries(requestUrl.searchParams), status: null };
        apiRequests.push(record);
        if (disconnectPreview && record.path.endsWith('/transactions/create-preview')) {
            // Explicit network-failure test only: break transport, never replace a DTO.
            record.status = 'network_disconnected';
            response.destroy();
            return;
        }
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
            const body = Buffer.from(await upstream.arrayBuffer());
            if (record.path.endsWith('/reports/recent-transactions') && upstream.status === 200) recentPayload = JSON.parse(body.toString('utf8'));
            if (record.path.endsWith('/transactions/explorer') && upstream.status === 200) explorerPayload = JSON.parse(body.toString('utf8'));
            if (record.path.endsWith('/transactions/create-preview') && upstream.status === 200) previewPayload = JSON.parse(body.toString('utf8'));
            if (/\/accounts\/[0-9a-f]{32}\/overview$/.test(record.path) && upstream.status === 200) overviewPayload = JSON.parse(body.toString('utf8'));
            if (record.path.endsWith('/reports/summary') && upstream.status === 200) {
                const summary = JSON.parse(body.toString('utf8'));
                summaryAsOf = summary.as_of_date;
                currencyResolution = summary.reporting_currency;
            }
            if (record.path.endsWith('/scheduled-transactions') && upstream.status === 200) scheduledAsOf = JSON.parse(body.toString('utf8')).map(item => item.forecast.as_of_date);
            response.end(body);
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
        if (process.env.QA_FORM_CURRENCY === '1') {
            await cdp.navigate(`${webBase}/books/1/select?next=/transactions/new`);
            const expected = scenario==='money'?'RUB':scenario==='currency_eur'?'EUR':'';
            assert.equal(await cdp.evaluate('document.querySelector("#transaction-currency").value'), expected, 'QA-08 fresh currency must match resolver without configured metadata');
            assert.equal(currencyResolution.configured_currency,null);
            assert.equal(currencyResolution.selected_currency,expected||null);
            assert.equal(currencyResolution.status,expected?'ready':'setup_required');
            if (!expected) assert.match(await cdp.evaluate('document.querySelector("#transaction-currency-help").innerText'),locale==='ru'?/Укажите валюту счетов/:/Choose the currency of the accounts/);
            if (alternateBookId) {
                // Exercise the actual BookSwitcher, recording whether its redirect reloads.
                const marker = await cdp.evaluate('window.qaDocumentMarker = "same-document"');
                await cdp.evaluate(`document.querySelector('#transaction-description').value='SYNTHETIC PRIVATE DRAFT'; document.querySelector('#transaction-description').dispatchEvent(new Event('input',{bubbles:true})); document.querySelector('input[name=split_amount]').value='123.4500';document.querySelector('input[name=split_amount]').dispatchEvent(new Event('input',{bubbles:true}));`);
                for (const [bookId, currency] of [[alternateBookId,'EUR'],[1,'RUB']]) {
                    if (width < 768) {
                        await cdp.evaluate(`document.querySelector('[data-mobile-more][aria-expanded=false]')?.click()`);
                        await cdp.wait(`Boolean(document.querySelector('[data-mobile-menu] select[data-testid=book-switcher-select]'))`);
                    }
                    await cdp.evaluate(`(()=>{const s=Array.from(document.querySelectorAll('[data-testid=book-switcher-select]')).find(e=>e.getClientRects().length);s.value=${JSON.stringify(String(bookId))};s.dispatchEvent(new Event('change',{bubbles:true}));})()`);
                    await cdp.wait(`document.querySelector('input[name=book_id]')?.value===${JSON.stringify(String(bookId))} && document.querySelector('#transaction-currency')?.value===${JSON.stringify(currency)}`);
                    evidence.book_switch_navigation = await cdp.evaluate('window.qaDocumentMarker')===marker?'client_side':'document_reload';
                    assert.equal(await cdp.evaluate('document.querySelector("#transaction-description").value'),'');
                    assert.equal(await cdp.evaluate('document.querySelector("input[name=split_amount]").value'),'');
                    assert.equal(currencyResolution.selected_currency,currency);
                }
                evidence.form_book_switch = true;
            }
            evidence.cases.push({locale,width,form_currency:true});
            continue;
        }
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
        if (clockInstant) {
            assert.equal(summaryAsOf, expectedClockDate, 'QA-04 summary uses the API installation calendar');
            assert.ok(scheduledAsOf.length > 0 && scheduledAsOf.every(date => date === expectedClockDate), 'QA-04 Scheduled and Dashboard obligations share that date');
            await cdp.navigate(`${webBase}/reports`);
            assert.equal(await cdp.evaluate(`document.querySelector('input[name=date_to]')?.value`), expectedClockDate, 'QA-04 report default cannot use the SSR UTC date');
            await cdp.navigate(`${webBase}/transactions?date_from=${expectedClockDate.slice(0, 7)}-01&date_to=${expectedClockDate}`);
            const preset = await cdp.evaluate(`document.querySelector('section[aria-labelledby=transactions-date-presets-title] a')?.href`);
            assert.equal(new URL(preset).searchParams.get('date_to'), expectedClockDate, 'QA-04 quick preset uses the same reporting date');
            await cdp.navigate(`${webBase}/scheduled?as_of_date=2026-09-01`);
            assert.ok(scheduledAsOf.every(date => date === '2026-09-01'), 'Explicit scheduled as_of_date wins');
        }
        if (scenario === 'pagination') {
            const firstHref='/transactions?date_from=2026-09-01&date_to=2026-09-30&page_size=20&sort=date_desc';
            await cdp.navigate(webBase+firstHref);await cdp.wait('document.querySelector("tbody tr a")');
            assert.equal(explorerPayload.returned_count,20);assert.equal(explorerPayload.items.length,20);assert.equal(explorerPayload.has_more,true);
            const firstIds=explorerPayload.items.map(x=>x.id);
            const exportHref=await cdp.evaluate(`document.querySelector('main a[href*="/transactions/export"]')?.getAttribute('href')`);
            assert.ok(exportHref,'First page exposes the real CSV route for these compatible filters');
            const next=await cdp.evaluate(`Array.from(document.querySelectorAll('nav a')).find(a=>a.innerText===${JSON.stringify(locale==='ru'?'Вперёд':'Next')})?.getAttribute('href')`);
            assert.ok(next,'Real next-page href exists');
            await cdp.navigate(webBase+next);await cdp.wait('document.querySelector("tbody tr a")');
            assert.equal(explorerPayload.items.length,12);assert.equal(explorerPayload.returned_count,12);assert.equal(explorerPayload.has_more,false);
            const allIds=[...firstIds,...explorerPayload.items.map(x=>x.id)];
            assert.equal(new Set(allIds).size,32);assert.deepEqual([...allIds].sort(),Object.values(fixture.transactions).map(x=>x.id).sort());
            const body=await cdp.evaluate('document.querySelector("main").innerText');
            assert.ok(body.includes(locale==='ru'?'Это последняя страница':'This is the last page'),'Nonempty continuation has a final-page message');
            assert.ok(!body.includes(locale==='ru'?'не вернул строки':'returned no rows'),'Nonempty page never claims no rows');
            const previous=await cdp.evaluate(`Array.from(document.querySelectorAll('nav a')).find(a=>a.innerText===${JSON.stringify(locale==='ru'?'Назад':'Previous')})?.getAttribute('href')`);
            assert.ok(previous);await cdp.navigate(webBase+previous);await cdp.wait('document.querySelector("tbody tr a")');
            assert.deepEqual(explorerPayload.items.map(x=>x.id),firstIds,'Previous cursor returns the identical first page');
            const exported=await cdp.evaluate(`fetch(${JSON.stringify(exportHref)}).then(async r=>({status:r.status,text:await r.text()}))`);
            assert.equal(exported.status,200);
            const exportedIds=JSON.parse(execFileSync(apiPython,['-c','import csv,io,json,sys; print(json.dumps([r["id"] for r in csv.DictReader(io.StringIO(sys.stdin.read().lstrip("\\ufeff")))]))'],{input:exported.text,encoding:'utf8'}));
            assert.deepEqual(exportedIds.sort(),[...allIds].sort(),'CSV export exactly matches both cursor pages');
            await cdp.navigate(webBase+firstHref+'&cursor=invalid-synthetic-cursor');
            assert.ok(await cdp.evaluate('!!document.querySelector("main [role=alert]")'),'Invalid cursor is not shown as successful final page');
        }
        if (scenario === 'money') {
            if (process.env.QA_FORM_STATES === '1') {
                await cdp.navigate(`${webBase}/transactions/new`);
                assert.equal(await cdp.evaluate('document.querySelectorAll("main [role=alert]").length'), 0, 'QA-07 fresh GET cannot claim a request failed');
                assert.doesNotMatch(await cdp.evaluate('document.querySelector("main").innerText'), locale === 'ru' ? /Транзакция создана|уже создал/ : /Transaction created|already created/i, 'QA-07 no fabricated success');
                const fill = `((values) => { for (const [selector, value] of values) {const el=document.querySelector(selector); el.value=value; el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}));} })`;
                await cdp.evaluate(`${fill}(${JSON.stringify([
                    ['#transaction-date','2026-09-01'],['#transaction-currency','RUB'],['#transaction-description','SYNTHETIC QA preview only'],
                    ['select[name=split_account_id]',scopeIds.cash],['fieldset:nth-of-type(2) select[name=split_account_id]',scopeIds.expense],
                    ['input[name=split_amount]','-1.2300'],['fieldset:nth-of-type(2) input[name=split_amount]','1.2300'],
                ])})`);
                const previewsBefore = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length;
                await cdp.evaluate(`document.querySelector('button[formaction="?/preview"]').click()`);
                await cdp.wait('Boolean(document.querySelector("#normalized-preview"))');
                assert.ok(previewPayload, 'actual non-mutating API preview must be observed');
                assert.equal(apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length, previewsBefore+1);
                assert.equal(previewPayload.confirm_allowed, false);
                assert.equal(previewPayload.preview_only, true);
                assert.deepEqual(previewPayload.splits.map(s=>s.amount), ['-1.2300','1.2300'], 'preview preserves exact decimal strings');
                assert.deepEqual(previewPayload.splits.map(s=>s.account.id), [scopeIds.cash,scopeIds.expense]);
                assert.ok(previewPayload.warnings.some(w=>w.code==='CREATE_DEPLOYMENT_DISABLED'));
                assert.equal(await cdp.evaluate('document.querySelectorAll("main [role=alert]").length'), 0, 'QA-07 successful preview is not a request failure');
                assert.equal(await cdp.evaluate(`document.querySelectorAll('#confirm-create-form,button[formaction="?/confirm"]').length`), 0, 'read-only preview cannot expose a confirm action');
                const previewText = await cdp.evaluate('document.querySelector("#normalized-preview").innerText');
                assert.doesNotMatch(previewText, /failed safely|Backend details were redacted|безопасной ошибкой|детали скрыты/i, 'known restriction is not a generic error');
                assert.match(previewText, locale==='ru' ? /CREATE выключен настройками deployment/ : /CREATE is disabled by deployment settings/);
                await cdp.evaluate(`${fill}([["#transaction-description","SYNTHETIC QA changed draft"]])`);
                await cdp.wait(`Array.from(document.querySelectorAll('main [role=status]')).some(e=>e.innerText.includes(${JSON.stringify(locale==='ru'?'Draft изменился':'Draft changed')}))`);
                assert.equal(await cdp.evaluate('Boolean(document.querySelector("#transaction-create-error-summary"))'), false, 'stale draft is a status, not a request failure');
                await cdp.evaluate(`${fill}([['fieldset:nth-of-type(2) input[name=split_amount]','2.2300']])`);
                await cdp.evaluate(`document.querySelector('button[formaction="?/preview"]').click()`);
                await cdp.wait('Boolean(document.querySelector("#transaction-create-error-summary"))');
                assert.equal(await cdp.evaluate('Boolean(document.querySelector("#normalized-preview"))'), false, 'failed validation does not show a successful preview');
                assert.ok(apiRequests.some(r=>r.path.endsWith('/transactions/create-preview') && r.status===422));
                assert.equal(await cdp.evaluate('document.querySelector("input[name=split_amount]").value'), '-1.2300');
                assert.equal(await cdp.evaluate('document.querySelector("#transaction-currency").value'), 'RUB');
                await cdp.evaluate(`${fill}([["#transaction-currency","USD"]])`);
                const invalidBefore = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length;
                const invalidLoadBefore = cdp.loadCount;
                await cdp.evaluate(`document.querySelector('button[formaction="?/preview"]').click()`);
                for (let i=0;i<150 && cdp.loadCount===invalidLoadBefore;i++) await delay(100);
                assert.ok(cdp.loadCount>invalidLoadBefore,'validation response must finish before checking retained input');
                await cdp.wait(`document.querySelector('input[name=currency]')?.value==='USD' && document.querySelector('input[name=split_amount]')?.value==='-1.2300'`);
                assert.equal(apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length,invalidBefore+1);
                evidence.explicit_currency_preserved = true;
                disconnectPreview = true;
                await cdp.evaluate(`document.querySelector('button[formaction="?/preview"]').click()`);
                await cdp.wait(`document.querySelector('#transaction-create-error-summary')?.innerText.includes(${JSON.stringify('Write failed')})`);
                disconnectPreview = false;
                evidence.form_states = ['fresh','preview_blocked','stale','validation_error','network_unavailable'];
                evidence.preview_network_fault_injected = true;
                await cdp.navigate(`${webBase}/dashboard`);
            }
            assert.ok(Array.isArray(recentPayload), 'real recent report response must be observed');
            assert.equal(recentPayload.length, Object.keys(fixture.transactions).length);
            const domRows = await cdp.evaluate(`Array.from(document.querySelectorAll('[data-dashboard-recent-kind]')).map(row => ({text: row.innerText, amount: row.querySelector(':scope > span.shrink-0')?.innerText.replace(/\\s+/g,' ').trim() ?? ''}))`);
            for (const [name, spec] of Object.entries(fixture.transactions)) {
                const payload = recentPayload.find(row => row.id === spec.id);
                assert.equal(typeof payload?.amount, 'string', 'QA-02 real DTO must retain amount');
                assert.equal(typeof payload?.currency, 'string', 'QA-02 real DTO must retain currency');
                assert.equal(payload.representative_amount, undefined, 'recent reports must not pretend to be explorer DTOs');
                const row = domRows.find(row => row.text.includes(`SYNTHETIC QA ${name}`));
                assert.ok(row, `real recent row ${name} must render`);
                if (spec.magnitude !== null) {
                    const magnitude = payload.amount.replace(/^[+-]/, '');
                    assert.equal(compareDecimalStrings(magnitude, spec.magnitude), 0, 'real amount must equal the deterministic fixture amount');
                    assert.equal(payload.currency, spec.currency);
                    assert.equal(row.amount, `${magnitude} ${payload.currency}`, `QA-02 ${name}: show exact neutral magnitude from the real DTO, including zero`);
                } else {
                    assert.equal(row.amount, locale === 'ru' ? 'Сумма не показана' : 'Amount not shown', 'complex/multicurrency must not masquerade as a simple amount');
                }
            }
            evidence.recent_money_rows = domRows.length;
            const recentHref = await cdp.evaluate(`document.querySelector('li[data-dashboard-recent-kind]')?.closest('section')?.querySelector('a')?.href`);
            const recentUrl = new URL(recentHref);
            assert.equal(recentUrl.searchParams.get('date_from'), '2026-09-01', 'QA-09 recent link must use the dates actually shown');
            assert.equal(recentUrl.searchParams.get('date_to'), '2026-09-01');
            const readsBefore = apiRequests.filter(row => row.path.endsWith('/transactions/explorer')).length;
            await cdp.evaluate(`document.querySelector('li[data-dashboard-recent-kind]').closest('section').querySelector('a').click()`);
            await cdp.wait(`location.pathname === '/transactions' && Array.from(document.querySelectorAll('[role=button]')).some(row => row.getClientRects().length && row.innerText.includes('SYNTHETIC QA income'))`);
            assert.ok(apiRequests.filter(row => row.path.endsWith('/transactions/explorer')).length > readsBefore, 'Recent link click must reach the real backend explorer');
            assert.ok(await cdp.evaluate(`document.body.innerText.includes('SYNTHETIC QA income')`), 'The transaction shown on Dashboard remains reachable');
            evidence.recent_drilldown_click = true;
            await cdp.navigate(`${webBase}/transactions?date_from=2026-09-01&date_to=2026-09-02&page_size=20`);
            const explorerRows = await cdp.evaluate(`Array.from(document.querySelectorAll('[role=button]')).filter(row => row.getClientRects().length && row.innerText.includes('SYNTHETIC QA ')).map(row => ({text:row.innerText, amount:(row.querySelector('td:last-child') ?? row.querySelector('.shrink-0.text-right'))?.innerText.replace(/\\s+/g,' ').trim() ?? ''}))`);
            assert.equal(explorerRows.length, Object.keys(fixture.transactions).length, 'QA-03 real explorer rows must render');
            for (const [name, spec] of Object.entries(fixture.transactions)) {
                const row = explorerRows.find(row => row.text.includes(`SYNTHETIC QA ${name}`));
                assert.ok(row);
                if (spec.magnitude !== null) {
                    const payload = recentPayload.find(row => row.id === spec.id);
                    assert.ok(row.amount.startsWith(`${payload.amount.replace(/^[+-]/, '')} ${spec.currency}`), `QA-03 ${name}: explorer must show neutral magnitude, not arbitrary signed first split: ${row.amount}`);
                } else {
                    assert.match(row.amount, locale === 'ru' ? /сумма не показана/ : /No representative total is shown/, 'QA-03 complex amount stays explicit');
                }
            }
            evidence.explorer_money_rows = explorerRows.length;
            for (const [account, description, expected, group] of [
                ['cash', 'expense', '-123.45 RUB', false],
                ['expense', 'expense', '123.45 RUB', false],
                ['cash', 'transfer', '0.00 RUB', true],
            ]) {
                const scope = `account_ids=${scopeIds[account]}${group ? `&account_ids=${scopeIds.savings}` : ''}`;
                await cdp.navigate(`${webBase}/transactions?date_from=2026-09-01&date_to=2026-09-02&page_size=20&${scope}`);
                const amount = await cdp.evaluate(`(() => {const row=Array.from(document.querySelectorAll('[role=button]')).find(row=>row.getClientRects().length && row.innerText.includes(${JSON.stringify(`SYNTHETIC QA ${description}`)})); return (row?.querySelector('td:last-child') ?? row?.querySelector('.shrink-0.text-right'))?.innerText.replace(/\\s+/g,' ').trim() ?? '';})()`);
                assert.ok(amount.startsWith(expected), `QA-03 scoped signed quantity must match: ${amount}`);
                assert.match(amount, group ? (locale === 'ru' ? /выбранных счетов/ : /selected accounts/) : (locale === 'ru' ? /Изменение счёта/ : /Account change/), 'signed quantity must identify its account basis');
            }
            evidence.scoped_money_cases = 3;
        }
        if (['recent_sparse', 'empty'].includes(scenario)) {
            await cdp.navigate(`${webBase}/dashboard`);
            const shown = [...recentPayload];
            const links = await cdp.evaluate(`Array.from(document.querySelectorAll('[data-recent-period]')).map(a => ({href:a.href, text:a.innerText}))`);
            assert.equal(links.length, scenario === 'recent_sparse' ? 3 : 1, 'QA-09 every sparse period or explicit empty default must be visible');
            const primaryHref = await cdp.evaluate(`document.querySelector('[data-recent-drilldown]')?.href`);
            assert.equal(primaryHref, links[0].href, 'Header uses the latest bounded period');
            const reached = new Set();
            for (const [index, link] of links.entries()) {
                const url = new URL(link.href);
                const from = url.searchParams.get('date_from');
                const to = url.searchParams.get('date_to');
                assert.ok(from && to && from <= to && (Date.parse(to) - Date.parse(from)) / 86400000 < 366);
                assert.ok(link.text.includes(from) && link.text.includes(to), 'The allowed period is visibly labelled');
                assert.match(link.text, index === 0 ? (locale === 'ru' ? /Последний период/ : /Latest period/) : (locale === 'ru' ? /Более ранние/ : /Older transactions/));
                if (scenario === 'empty') {
                    assert.equal(from, summaryAsOf.slice(0, 7) + '-01');
                    assert.equal(to, summaryAsOf);
                }
                const readsBefore = apiRequests.length;
                explorerPayload = undefined;
                await cdp.evaluate(`document.querySelectorAll('[data-recent-period]')[${index}].click()`);
                await cdp.wait(`location.pathname === '/transactions' && document.querySelector('input[name=date_from]')?.value === ${JSON.stringify(from)}`);
                const expected = shown.filter(tx => tx.date >= from && tx.date <= to);
                if (expected.length) await cdp.wait(`Array.from(document.querySelectorAll('[role=button]')).some(row => row.getClientRects().length && row.innerText.includes(${JSON.stringify(expected[0].description)}))`);
                assert.ok(explorerPayload, 'Click reaches real explorer, not only a filter screen');
                assert.deepEqual(explorerPayload.items.map(tx => tx.id).sort(), expected.map(tx => tx.id).sort());
                for (const tx of expected) {
                    assert.ok(await cdp.evaluate(`Array.from(document.querySelectorAll('[role=button]')).some(row => row.getClientRects().length && row.innerText.includes(${JSON.stringify(tx.description)}))`));
                    reached.add(tx.id);
                }
                const request = apiRequests.slice(readsBefore).find(row => row.path.endsWith('/transactions/explorer') && row.status === 200);
                const recentRequest = apiRequests.findLast(row => row.path.endsWith('/reports/recent-transactions'));
                assert.equal(request?.path.replace('/transactions/explorer', ''), recentRequest.path.replace('/reports/recent-transactions', ''), 'Active book preserved');
                assert.equal(request.query.date_from, from);
                assert.equal(request.query.date_to, to);
                assert.equal(request.query.sort, 'date_desc');
                assert.equal(request.query.page_size, '50');
                assert.equal(request.query.cursor, undefined);
                // app.html currently hardcodes lang=en (tracked for QA-12); verify actual UI locale here.
                assert.equal(await cdp.evaluate('document.querySelector("main h1")?.innerText'), locale === 'ru' ? 'Просмотр транзакций' : 'Browse transactions', 'UI locale preserved on click');
                if (!expected.length) {
                    assert.equal(explorerPayload.returned_count, 0);
                    assert.ok(await cdp.evaluate(`Boolean(document.querySelector('main [role=status]'))`), 'Genuine empty result explained');
                }
                await cdp.navigate(`${webBase}/dashboard`);
            }
            assert.equal(reached.size, shown.length, 'All previously shown transactions remain reachable');
            evidence.recent_period_clicks = links.length;
            evidence.recent_reachable_rows = reached.size;
        }
        if (scenario === 'account_groups') {
            const ids = fixture.accounts;
            await cdp.navigate(`${webBase}/accounts/${ids.group}`);
            assert.equal(overviewPayload.placeholder, true);
            assert.equal(overviewPayload.structure_status, 'root', 'QA-06 real canonical-root child is not an orphan');
            assert.doesNotMatch(await cdp.evaluate('document.querySelector("main").innerText'), /orphan|cycle repairs/i, 'QA-06 no false repair warning in actual account card');
            assert.equal(overviewPayload.children_truncated, true);
            const totals = (await cdp.evaluate(`document.querySelector('[data-account-recursive-totals]')?.innerText ?? ''`)).replace(/\s+/g, ' ');
            assert.ok(totals, 'QA-05 placeholder must show recursive totals');
            for (const bucket of overviewPayload.recursive_balances) {
                assert.ok(totals.includes(`${bucket.amount} ${bucket.commodity.mnemonic}`), `Group shows each native currency, not a sum of the truncated children: ${JSON.stringify({totals, bucket})}`);
            }
            assert.ok(await cdp.evaluate(`document.body.innerText.includes(${JSON.stringify(locale === 'ru' ? 'Непроводимая группа' : 'Non-postable group')})`), 'Placeholder remains non-postable');
            assert.equal(await cdp.evaluate(`document.querySelectorAll('form[action^="/accounts/"]').length`), 0, 'No direct-activity form on a group');
            assert.ok(await cdp.evaluate(`Boolean(document.querySelector('[data-account-children-truncated]'))`), 'Truncation stays explicit');
            const allHref = await cdp.evaluate(`document.querySelector('[data-account-all-children]')?.href`);
            assert.ok(allHref, 'Truncated overview exposes a route to all envelopes');
            assert.equal(new URL(allHref).searchParams.get('hidden'), 'include', 'Hidden tail envelopes must remain reachable');
            await cdp.evaluate(`document.querySelector('[data-account-all-children]').click()`);
            await cdp.wait(`document.querySelector('[data-account-toggle="${ids.group}"]')`);
            await cdp.evaluate(`document.querySelector('[data-account-toggle="${ids.group}"]').click()`);
            await cdp.wait(`document.querySelector('#account-children-${ids.group} [data-account-row]')`);
            const visited = new Set();
            for (let page = 0; page < 20; page++) {
                const current = await cdp.evaluate(`Array.from(document.querySelectorAll('#account-children-${ids.group} [data-account-row]')).map(row=>row.dataset.accountRow)`);
                current.forEach(id => visited.add(id));
                const more = await cdp.evaluate(`!document.querySelector('[data-account-page-next="${ids.group}"]').disabled`);
                if (!more) break;
                await cdp.evaluate(`document.querySelector('[data-account-page-next="${ids.group}"]').click()`);
                await cdp.wait(`document.querySelector('#account-children-${ids.group} [data-account-row]')?.dataset.accountRow !== ${JSON.stringify(current[0])}`);
            }
            assert.equal(visited.size, 205, 'All immediate envelopes are discoverable, not just the overview prefix');
            assert.ok(visited.has(ids.last) && visited.has(ids.nested));
            await cdp.evaluate(`document.querySelector('[data-account-row="${ids.last}"] a').click()`);
            await cdp.wait(`location.pathname === '/accounts/${ids.last}' && document.querySelector('main h1')?.innerText.includes('Envelope 203')`);
            assert.ok((await cdp.evaluate(`document.body.innerText`)).replace(/\s+/g, ' ').includes('7 RUB'), 'Tail balance is available');
            await cdp.navigate(`${webBase}/accounts/${ids.nested}`);
            const nestedTotals = (await cdp.evaluate(`document.querySelector('[data-account-recursive-totals]')?.innerText ?? ''`)).replace(/\s+/g, ' ');
            for (const bucket of overviewPayload.recursive_balances) assert.ok(nestedTotals.includes(`${bucket.amount} ${bucket.commodity.mnemonic}`));
            assert.equal(overviewPayload.children_returned, 3);
            assert.equal(await cdp.evaluate(`document.querySelectorAll('[data-account-child]').length`), 3);
            assert.equal(await cdp.evaluate(`document.querySelectorAll('[data-account-all-children]').length`), 0, 'No false truncation navigation for complete children');
            for (const [id, amount] of [[ids.zero, '0 RUB'], [ids.negative, '-25 RUB']]) {
                await cdp.navigate(`${webBase}/accounts/${id}`);
                assert.ok((await cdp.evaluate(`document.body.innerText`)).replace(/\s+/g, ' ').includes(amount), 'Zero and negative leaf balances remain visible');
            }
            assert.equal(apiRequests.filter(row => /\/accounts\/[0-9a-f]{32}\/activity$/.test(row.path)).length, 0, 'Overview browsing never requests direct activity');
            evidence.account_group_children_reached = visited.size;
            evidence.account_group_currency_buckets = 3;
        }
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
    evidence.book_mutation_requests = [...browserRequests.filter(r=>!isReadOnlyQaRequest(r,'browser')), ...apiRequests.filter(r=>!isReadOnlyQaRequest(r,'api'))];
    evidence.preview_requests = apiRequests.filter(r=>r.method==='POST' && r.path.endsWith('/transactions/create-preview')).length;
    if (fixture) {
        evidence.hash_after = hash(fixture.book_path);
        if (evidence.hash_after !== evidence.hash_before) cleanupErrors.push('Generated book changed');
        evidence.quick_check = pythonJson('import json,sqlite3,sys\nwith sqlite3.connect("file:"+sys.argv[1]+"?mode=ro",uri=True) as db:\n print(json.dumps(db.execute("pragma quick_check").fetchone()[0]))', [fixture.book_path]);
        if (evidence.quick_check !== 'ok') cleanupErrors.push('SQLite quick_check failed');
    }
    evidence.additional_fixture_checks = additionalFixtures.map(item=>{
        const unchanged = hash(item.book_path)===item.sha256;
        const quick_check = pythonJson('import json,sqlite3,sys\nwith sqlite3.connect("file:"+sys.argv[1]+"?mode=ro",uri=True) as db:\n print(json.dumps(db.execute("pragma quick_check").fetchone()[0]))',[item.book_path]);
        if (!unchanged || quick_check!=='ok') cleanupErrors.push('Additional generated book changed or failed quick_check');
        return {scenario:item.scenario,unchanged,quick_check};
    });
    if (evidence.book_mutation_requests.length) cleanupErrors.push('Unexpected mutation request');
    if (cleanupErrors.length) { evidence.status = 'FAIL'; failure ??= new Error(cleanupErrors.join('; ')); }
    evidence.cleanup_errors = cleanupErrors;
    evidence.elapsed_ms = Date.now() - started;
    if (failure) for (const child of children) writeFileSync(join(root, `${child.qaLabel}.log`), child.qaOutput(), { mode: 0o600 });
    writeFileSync(join(root, 'evidence.json'), JSON.stringify(evidence, null, 2), { mode: 0o600 });
    console.log(JSON.stringify({ status: evidence.status, evidence: join(root, 'evidence.json'), runtime_stopped: evidence.runtime_stopped, book_mutation_requests: evidence.book_mutation_requests.length }));
}
if (failure) throw failure;
