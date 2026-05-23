# Default-disabled reset checklist for write-alpha work

Status: Phase 306 maintenance-hardening checklist. This is a non-mutating operator checklist for ending any synthetic/disposable or copied/restorable write-alpha investigation safely.

## Purpose

Every write-alpha investigation must end by proving the app is back in read-only mode. This checklist consolidates the minimum reset evidence so future handoffs do not rely on memory or raw private runtime details.

This checklist does not authorize any mutation. It applies only after a separately authorized synthetic/disposable or copied/restorable-test-book write-alpha run.

## Required reset state

- `GNUCASH_WRITES_ENABLED=false` is the active runtime posture.
- Enabled write-alpha routes are no longer reachable as write-enabled routes.
- The app can still serve read-only health, login, book discovery, accounts, transactions, reports, scheduled transaction metadata, and write-alpha audit summary.
- Disabled validate/create/PATCH/DELETE probes return 403.
- No screenshots, CSV exports, raw payloads, app DBs, books, backups, locks, private paths, account names, memos, descriptions, amounts, tokens, keys, or certs are staged for commit.

## Minimum commands

Use documented dummy/local values when rendering Compose config:

```bash
JWT_SECRET=dummy-validation-secret \
APP_ADMIN_PASSWORD=dummy \
GNUCASH_WRITES_ENABLED=false \
docker compose config --quiet
```

Then run the read-only API smoke against the local read-only deployment:

```bash
SMOKE_ADMIN_PASSWORD='<local dummy or smoke admin password>' \
SMOKE_API_BASE_URL=http://localhost:8080/api \
scripts/smoke/read-only-api-smoke.py
```

Expected API smoke coverage:

- health;
- login;
- `/auth/me`;
- `/books` and `/books/{id}`;
- accounts;
- transactions and transaction detail when fixture data has transactions;
- CSV export headers;
- reports summary;
- scheduled transactions;
- write-alpha audit summary;
- disabled validate/create/PATCH/DELETE all return 403.

If browser/UI was involved, also run:

```bash
SMOKE_ADMIN_PASSWORD='<local dummy or smoke admin password>' \
SMOKE_WEB_BASE_URL=http://localhost:8080 \
scripts/smoke/read-only-browser-dogfood.py \
  --base-url http://localhost:8080 \
  --fixture-path data/books/main.gnucash.sqlite \
  --viewport-width 320 \
  --viewport-height 720
```

Expected browser smoke coverage:

- login page and authenticated dashboard;
- write UI hidden while writes are disabled;
- `document.cookie` does not expose the auth token;
- accounts, books, scheduled, account detail, transactions, transaction detail;
- CSV export fetch with expected header;
- no screenshots/downloads/CSV artifacts written.

## Commit hygiene before handoff

Run:

```bash
git status --short
git diff --check
python3 scripts/check_public_status.py
```

Allowed tracked changes are only source/docs/test changes intentionally made for the current phase.

Forbidden to stage or commit:

- `.env` files;
- runtime `data/books/*` books;
- runtime `data/app/*` app DBs;
- `data/backups/*` backups;
- lock files;
- screenshots;
- CSV exports;
- raw evidence with private paths, account names, memos, descriptions, amounts, tokens, keys, certs, or raw request/response payloads.

## Handoff wording

A safe handoff after write-alpha investigation should state only bounded facts, for example:

- reset/default-disabled verification passed;
- disabled validate/create/PATCH/DELETE probes returned 403;
- read-only API/browser smoke passed on a synthetic/disposable or copied/restorable test book;
- no private/runtime artifacts were committed.

Do not state or imply:

- production readiness;
- security audit completion;
- public-internet safety;
- broad GnuCash version compatibility;
- safety for original/private/only-copy books;
- DELETE readiness from CREATE/PATCH evidence.
