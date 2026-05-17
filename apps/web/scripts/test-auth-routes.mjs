import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import assert from 'node:assert/strict';

const root = new URL('..', import.meta.url).pathname;

function read(relativePath) {
	return readFileSync(join(root, relativePath), 'utf8');
}

function walk(dir, files = []) {
	for (const entry of readdirSync(dir)) {
		const full = join(dir, entry);
		if (statSync(full).isDirectory()) {
			walk(full, files);
		} else {
			files.push(full);
		}
	}
	return files;
}

const hooks = read('src/hooks.server.ts');
assert.match(hooks, /PROTECTED_PREFIXES[\s\S]*'\/dashboard'[\s\S]*'\/accounts'/, 'dashboard and accounts routes must be protected');
assert.match(hooks, /redirect\(303, `\/login\?next=/, 'protected routes must redirect to /login');
assert.match(hooks, /cookies\.get\('access_token'\)/, 'protected routes must use the httpOnly cookie');

const loginServer = read('src/routes/login/+page.server.ts');
assert.match(loginServer, /cookies\.set\(AUTH_COOKIE, data\.access_token/, 'login must store token in cookie');
assert.match(loginServer, /httpOnly:\s*true/, 'auth cookie must be httpOnly');
assert.doesNotMatch(loginServer, /localStorage|sessionStorage/, 'login must not use browser storage');

const logoutServer = read('src/routes/logout/+server.ts');
assert.match(logoutServer, /cookies\.delete\('access_token'/, 'logout must delete auth cookie');

const transactionsServer = read('src/routes/transactions/+page.server.ts');
assert.match(
	transactionsServer,
	/writesEnabled:\s*env\.GNUCASH_WRITES_ENABLED === 'true'/,
	'transactions page must expose writesEnabled only when GNUCASH_WRITES_ENABLED is true'
);

const newTransactionServer = read('src/routes/transactions/new/+page.server.ts');
assert.match(
	newTransactionServer,
	/env\.GNUCASH_WRITES_ENABLED !== 'true'[\s\S]*redirect\(303, '\/transactions'\)/,
	'new transaction page must redirect when frontend writes are disabled'
);
assert.match(
	newTransactionServer,
	/hasWriteAcknowledgement\(formData\)[\s\S]*experimental controlled-write transaction/,
	'final create action must require explicit write acknowledgement'
);
assert.ok(
	newTransactionServer.indexOf('hasWriteAcknowledgement(formData)') <
		newTransactionServer.indexOf('`/books/${bookId}/transactions/validate`', newTransactionServer.indexOf('create:')),
	'write acknowledgement must be checked before final create validation/write API calls'
);

const transactionListPage = read('src/routes/transactions/+page.svelte');
assert.match(
	transactionListPage,
	/data\.writesEnabled[\s\S]*Experimental post-MVP write mode[\s\S]*New transaction/,
	'transactions page must show warning text near the enabled write entry point'
);

const newTransactionPage = read('src/routes/transactions/new/+page.svelte');
assert.match(
	newTransactionPage,
	/WriteModeWarning/,
	'new transaction page must render prominent write-mode warning component'
);
assert.match(
	newTransactionPage,
	/name="write_acknowledgement"[\s\S]*experimental-write-mode-acknowledged[\s\S]*required/,
	'new transaction final create form must include a required acknowledgement checkbox'
);

const writeModeWarning = read('src/lib/components/WriteModeWarning.svelte');
for (const phrase of [
	'experimental post-MVP',
	'MVP v0.1 remains read-only by default',
	'GNUCASH_WRITES_ENABLED=false',
	'GnuCash Desktop remains the authoritative editor',
	'disposable/test copies',
	'Never use this experimental path with your only real financial book'
]) {
	assert.ok(writeModeWarning.includes(phrase), `write warning must include: ${phrase}`);
}

for (const file of walk(join(root, 'src'))) {
	const content = readFileSync(file, 'utf8');
	// Theme-related files are allowed to use localStorage for theme preference only (not auth tokens)
	if (file.endsWith('app.html') || file.endsWith('theme.ts')) {
		assert.doesNotMatch(content, /access_token/, `${file} must not reference auth tokens`);
		continue;
	}
	assert.doesNotMatch(content, /localStorage|sessionStorage/, `${file} must not use localStorage/sessionStorage`);
}

console.log('auth route checks passed');
