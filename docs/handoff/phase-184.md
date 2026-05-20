# Phase 184 — write-alpha PATCH disposable dogfood

Date: 2026-05-20
Status: COMPLETE — synthetic/disposable PATCH dogfood evidence captured without write-scope expansion
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 3 only)

## Goal

Obtain real synthetic/disposable dogfood evidence for the existing PATCH transaction metadata/split-memo route, comparable to prior create evidence, without adding functionality.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-183.md`;
  - roadmap file named by the phase contract;
  - relevant transaction write route/service/tests and smoke helpers.
- Added `scripts/smoke/write-alpha-patch-smoke.py`, a redacted local smoke helper for the existing PATCH route.
- Copied the committed synthetic fixture to a temporary external disposable source, preflighted source/runtime/backup path classes, then copied it into ignored runtime data.
- Ran exactly one successful PATCH under explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.
- Verified API read-back, runtime SQLite marker read-back, unchanged split amount fingerprint, backup count, audit rows, safe missing-transaction error behavior, and lock release evidence.
- Restarted runtime in default write-disabled mode and ran read-only API smoke proving validate/create/PATCH/DELETE return 403.
- Removed ignored runtime book/app DB/backups/locks after verification.
- Added evidence artifact `docs/dogfood/phase-184-write-alpha-patch-dogfood.md`.

## Files changed

- `scripts/smoke/write-alpha-patch-smoke.py`
- `docs/dogfood/phase-184-write-alpha-patch-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-184.md`

## Verification summary

Commands/results recorded for this phase:

```bash
python3 -m py_compile scripts/smoke/write-alpha-patch-smoke.py
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/phase184 <temp synthetic source>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose exec -T api python - --api-base-url http://localhost:8000 --password dummy --app-db /data/app/app.db --backup-root /data/backups --lock-root /data/locks --runtime-book /data/books/main.gnucash.sqlite < scripts/smoke/write-alpha-patch-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaPatchRouteDisposableFixture -q
cd apps/api && pytest tests/test_write_alpha_smoke_lock_evidence.py -q
cd apps/web && npm run test:auth-routes
git diff --check
# sensitive tracked-file hygiene scan over git ls-files
```

Results:

- PATCH smoke passed with redacted output.
- Preflight passed for external disposable source, ignored runtime book target, and ignored backup class.
- PATCH smoke confirmed one successful metadata/split-memo PATCH, one safe failed missing-transaction PATCH audit, one backup, API/runtime read-back, unchanged split amount fingerprint, and non-active stale-released lock evidence from inside the API container.
- Read-only API smoke after default reset passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- Targeted backend PATCH route tests passed.
- Smoke lock evidence tests passed.
- Frontend auth-route/static checks passed.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No new write endpoint or write feature was added.
- PATCH scope stayed limited to transaction description/date/split memos; no amount/account mutation was attempted.
- The write-enabled run was explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.
- Only the committed synthetic fixture copied into ignored runtime data was mutated.
- Runtime book/app DB/backups/locks were removed after verification.
- No real/private/only-copy book, `.env`, token, key, cert, screenshot, export, app DB, runtime book, backup, lock artifact, raw path, account name, original description, original memo, amount, or private financial data was committed.
- No release, tag, package, or publication action was performed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start DELETE dogfood, audit UI work, or release-readiness work from this phase.
