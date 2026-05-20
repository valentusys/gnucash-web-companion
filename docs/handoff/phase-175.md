# Phase 175 — write-alpha controlled create dogfood

Date: 2026-05-20
Status: COMPLETE — one disposable create dogfood run completed; no private/real book used
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 4 only)

## Goal

Run the first actual write-alpha create transaction dogfood only on a copied/disposable book/test fixture.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-174.md`;
  - roadmap file named by the phase contract;
  - Phase 173 copied-book runbook, Phase 174 preflight helper, write routes, write tests, smoke helpers, and Docker config.
- Copied the committed synthetic fixture to a temporary external path and ran Phase 174 preflight against that external disposable copy.
- Started local Docker/Caddy runtime with `APP_ENV=test` and explicit local-only `GNUCASH_WRITES_ENABLED=true` against an ignored runtime copy under `data/books/`.
- Performed exactly one balanced two-split create through the existing write-alpha API route.
- Confirmed validation behavior around the create:
  - valid balanced request passed validation;
  - unbalanced probe rejected;
  - invalid-account probe rejected;
  - placeholder-style probe rejected via intentionally invalid placeholder probe id, while backend placeholder-account rejection remains covered by targeted tests.
- Confirmed read-back of the created transaction through the API.
- Confirmed backup creation, audit row creation, and lock release with redacted evidence.
- Stopped the write-enabled runtime immediately after create evidence collection.
- Restored the disposable runtime copy and ran read-only API smoke with default write-disabled config.
- Removed ignored runtime book/app DB/backup/lock artifacts after the run.
- Added a reusable redacted write-alpha create smoke helper.

## Files changed

- `scripts/smoke/write-alpha-create-smoke.py`
- `docs/dogfood/phase-175-write-alpha-create-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-175.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `GNUCASH_WRITES_ENABLED=true` was used only as an explicit local runtime override with `APP_ENV=test`.
- Runtime target was an ignored disposable copy under `data/books/`.
- App DB, backups, and lock files stayed under ignored `data/` runtime paths and were removed after the run.
- No real/private/only-copy book was used.
- No PATCH or DELETE dogfood was run.
- No release/tag/package was published.
- No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Verification

Commands run:

```bash
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose up --build
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/write-alpha-create-smoke.py
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose exec -T api <redacted lock/audit/backup probe>
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose down --remove-orphans
APP_ENV=test ... docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-api-smoke.py
APP_ENV=test ... docker compose down --remove-orphans
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git status --short -- data/books data/backups data/app data/locks
```

Results:

- Preflight passed with redacted summary only.
- Exactly one create succeeded in the write-enabled disposable runtime.
- Backup count increased by one for the create route.
- Audit success row count increased by one.
- Lock-release probe passed by reacquiring the remaining file lock after the write; the current implementation leaves the lock file itself present until cleanup.
- API read-back of the created transaction passed.
- Read-only API smoke after restore passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Default Compose config still renders `GNUCASH_WRITES_ENABLED: "false"`.
- Ignored runtime artifacts were removed from `data/books`, `data/backups`, `data/app`, and `data/locks`.

## Next

Continue only with the next explicitly requested phase. Do not run GnuCash Desktop verification, backup/restore drill, PATCH dogfood, DELETE dogfood, release/tag publication, or broader UX/API hardening unless a later phase explicitly requests it.
