# Phase 77 — Real Read-only Dogfood on Copied/Disposable GnuCash Book

## Status

Complete. Phase 77 was not audit-only: it ran the local Docker deployment against a copied/disposable GnuCash SQL book, recorded API/browser dogfood evidence, verified runtime writes-disabled behavior, created a release-blocking GitHub issue for the web UI failure, produced dogfood and audit artifacts, updated status docs, and pushed the phase commit.

The phase did not add features, did not enable writes, did not write to the GnuCash book, did not touch a real/original personal book, did not commit runtime data or secrets, and did not publish a release.

## PM report

### Scenario

Run the Docker deployment locally against a copied/disposable GnuCash SQL SQLite book with `GNUCASH_WRITES_ENABLED=false`, then dogfood the read-only MVP flows:

- login;
- dashboard/reports summary;
- accounts;
- account detail;
- account transactions;
- transactions;
- transaction detail;
- search/filter;
- CSV export;
- disabled validate/create/patch write endpoints.

Because no safe real personal copied book was discoverable locally, the PM accepted the committed synthetic/disposable SQL fixture as the safe source class for this phase, with the result clearly marked as partial against the requested real-copied-book target.

### Pass/fail criteria

Pass:

- Docker starts with a copied/disposable SQL book outside git runtime paths.
- `/api/health` is `ok` and reports the default book present/readable.
- `GNUCASH_WRITES_ENABLED=false` is verified in runtime config and health output.
- Login and read-only API/UI flows work.
- Write endpoints return read-only/write-disabled 403 responses.
- No real book, app DB, backup, `.env`, secret, screenshot with real financial data, token, or raw export is committed.

Fail/blocker:

- Runtime writes are enabled or write probes bypass the gate.
- Docker cannot run.
- Login/core read-only behavior fails.
- Browser/UI dogfood cannot proceed.
- Only real/original book access is available.

### Release blockers

1. #37 — Docker web UI redirects `/login` to itself and prevents browser dogfood.
2. #25 remains open because Phase 77 produced successful API dogfood but failed browser/UI dogfood.
3. A safe real copied personal GnuCash SQL book was not available/discoverable; the phase used a synthetic/disposable fixture.
4. `v0.1.0-readonly` must not be published until the web blocker is fixed and copied/disposable-data browser dogfood is rerun successfully.

## Engineer report

### What ran

Setup outside git:

- Runtime workdir: `/tmp/gnucash-web-companion-phase77`.
- Runtime book copy: `/tmp/gnucash-web-companion-phase77/data/books/main.gnucash.sqlite`.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Runtime copy SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.

Docker/config:

- `docker --version` — Docker 29.5.0.
- `docker compose version` — v5.1.3.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- Docker Compose started with `docker-compose.yml` plus temp override and temp env file.

Runtime proof:

- API service: running and healthy.
- Proxy service: running.
- Web service: running but unhealthy.
- `/api/health`: `status=ok`, app DB reachable, default book present/readable, `writes_enabled=false`.
- Compose config showed `GNUCASH_WRITES_ENABLED: "false"` for API and web.

### What worked

API dogfood passed:

- login;
- `/auth/me`;
- `/books` and `/books/1`;
- `/books/1/accounts`;
- `/books/1/accounts/{account_id}`;
- `/books/1/transactions`;
- `/books/1/transactions/{transaction_id}`;
- `/books/1/reports/summary`;
- `/books/1/transactions?query=salary`;
- `/books/1/transactions/export?query=salary`;
- disabled validate/create/patch write probes.

Smoke script result:

```text
PASS: read-only API smoke checks completed
```

Manual API result highlights:

```text
accounts: count= 10
transactions: total= 5 returned= 5
search_filter: query=salary returned= 1 total= 1
csv_export: status= 200 content_type= text/csv; charset=utf-8 rows= 2
write_disabled: POST /books/1/transactions/validate status= 403
write_disabled: POST /books/1/transactions status= 403
write_disabled: PATCH /books/1/transactions/nonexistent status= 403
```

### What failed

Browser/UI dogfood failed before login:

```text
GET /login -> HTTP/1.1 303 See Other
Location: /login
```

`curl -L --max-redirs 5 http://127.0.0.1:18080/login` hit a redirect loop. Browser navigation to both `http://127.0.0.1:18080/login` and `http://localhost:18080/login` timed out. This prevented UI checks for dashboard, accounts, account detail, transactions, transaction detail, search/filter, and CSV export.

### Issues created

- #37 — Docker web UI redirects `/login` to itself and prevents browser dogfood.

#25 remains open; Phase 77 is progress but not closure.

### Artifacts

- `docs/dogfood/phase-77-readonly-dogfood.md`
- `docs/audits/phase-77-audit.md`
- `docs/handoff/phase-77.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## Auditor report

### Evidence review

The dogfood artifact contains actual runtime evidence rather than only planning/audit text. It records the environment, commit, copied/disposable book source class, writes-disabled proof, API checks, browser attempt, failures, safe log snippets, issue created, and release verdict.

The safety boundary held:

- writes disabled in Compose config;
- writes disabled in health output;
- write endpoints returned 403;
- no real/original book was touched;
- no runtime data or secrets were committed.

### Release verdict

Not ready for `v0.1.0-readonly`.

Reason: API dogfood succeeded, but the user-facing web UI cannot load `/login` in Docker and browser dogfood is blocked. A read-only web companion release needs browser-level evidence. Fix #37 and rerun dogfood before publishing v0.1.

## Checks

Run during Phase 77:

- `git status --short --branch` — clean at phase start.
- `git log -1 --oneline` — starting HEAD `12092a7 docs: add phase 76 v0.2 planning audit`.
- `~/.local/bin/gh auth status` — authenticated as `valentusys`.
- `search_files /home/val *.gnucash*` — no safe real personal GnuCash SQL book found; only committed fixtures found.
- `docker --version` — Docker 29.5.0.
- `docker compose version` — v5.1.3.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- Docker local deployment with temp env/override — started.
- `/api/health` — `ok`, default book present/readable, `writes_enabled=false`.
- `scripts/smoke/read-only-api-smoke.py` against `http://127.0.0.1:18080/api` — passed.
- Manual API dogfood for accounts/account detail/transactions/transaction detail/search/filter/CSV export/write-disabled probes — passed except browser/UI route.
- `browser_navigate` to `/login` — timed out due to redirect loop.
- `curl -L --max-redirs 5 /login` — failed with repeated `303 Location: /login`.

Final repository verification after docs/status updates:

- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed, 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed, 0 errors and 0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- Phase 77 Docker dogfood stack was stopped with `docker compose ... down` after evidence collection.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the runtime and documented state.
- Controlled writes remain experimental/post-MVP and disabled by default.
- No write scope was expanded.
- No feature was added.
- No release/tag was published.
- No production-readiness/security-audited claim was made.
- No real GnuCash book, app DB, backup, `.env`, secret, token, certificate, key, screenshot with real financial data, or raw CSV export was committed.

## Commit / push

- Phase commit message: `docs: add phase 77 dogfood evidence`.
- Phase commit: current pushed `origin/main` HEAD for Phase 77.
- Pushed to `origin/main`: yes.

## Next required work

1. Fix #37 with a narrow tested bugfix.
2. Rerun Docker browser/API dogfood with writes disabled.
3. Keep #25 open until browser dogfood passes and PM accepts the copied/disposable book source class.
4. Do not start another audit-only phase unless explicitly requested.
