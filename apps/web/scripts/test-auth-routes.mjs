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
assert.match(hooks, /PROTECTED_PREFIXES\s*=\s*\['\/dashboard'\]/, 'dashboard route must be protected');
assert.match(hooks, /redirect\(303, `\/login\?next=/, 'protected routes must redirect to /login');
assert.match(hooks, /cookies\.get\('access_token'\)/, 'protected routes must use the httpOnly cookie');

const loginServer = read('src/routes/login/+page.server.ts');
assert.match(loginServer, /cookies\.set\(AUTH_COOKIE, data\.access_token/, 'login must store token in cookie');
assert.match(loginServer, /httpOnly:\s*true/, 'auth cookie must be httpOnly');
assert.doesNotMatch(loginServer, /localStorage|sessionStorage/, 'login must not use browser storage');

const logoutServer = read('src/routes/logout/+server.ts');
assert.match(logoutServer, /cookies\.delete\('access_token'/, 'logout must delete auth cookie');

for (const file of walk(join(root, 'src'))) {
	const content = readFileSync(file, 'utf8');
	assert.doesNotMatch(content, /localStorage|sessionStorage/, `${file} must not use localStorage/sessionStorage`);
}

console.log('auth route checks passed');
