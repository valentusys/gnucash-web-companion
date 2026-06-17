import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const page = readFileSync(join(here, '..', 'src', 'routes', 'transactions', 'new', '+page.svelte'), 'utf8');
const server = readFileSync(join(here, '..', 'src', 'routes', 'transactions', 'new', '+page.server.ts'), 'utf8');

const requiredPageFragments = [
	'Transaction entry preview',
	'Preview only / no write executed',
	'name="date"',
	'name="debit_account_id"',
	'name="credit_account_id"',
	'name="amount"',
	'name="currency"',
	'name="description"',
	'name="memo"',
	'Preview transaction',
	'Create disabled',
	'type="button" disabled',
	'md:grid-cols-2'
];

const requiredServerFragments = [
	'/transactions/create-preview',
	'formToPreviewPayload',
	'debit_account_id',
	'credit_account_id',
	'No write was executed',
	'previewOnly: true'
];

for (const fragment of requiredPageFragments) {
	if (!page.includes(fragment)) {
		throw new Error(`transaction-entry page missing required fragment: ${fragment}`);
	}
}
for (const forbidden of ['formaction="?/create"', 'Create transaction</button>', '`/books/${bookId}/transactions`,']) {
	if (page.includes(forbidden) || server.includes(forbidden)) {
		throw new Error(`transaction-entry preview slice contains forbidden create path/control: ${forbidden}`);
	}
}
for (const fragment of requiredServerFragments) {
	if (!server.includes(fragment)) {
		throw new Error(`transaction-entry server action missing required fragment: ${fragment}`);
	}
}

console.log('transaction-entry-preview-static: ok');
