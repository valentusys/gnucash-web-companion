# Phase 200 — Bounded write-alpha disposable CRUD/restore dogfood

Date: 2026-05-20
Status: COMPLETE — write-alpha create/PATCH/DELETE disposable route-family dogfood passed; default false reset and teardown verified
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 9 only)

## Goal

After cycle-3 helper/UX fixes, collect final bounded write-alpha evidence on synthetic/disposable data only, including create/PATCH/DELETE, audit, backup, lock, restore where actually completed, and return to default `GNUCASH_WRITES_ENABLED=false`.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-199.md`, cycle-3 roadmap file, write-alpha smoke helpers, read-only API smoke helper, and preflight helper.
- Used only the committed synthetic fixture copied into ignored runtime `data/books/main.gnucash.sqlite`.
- Preflighted an external disposable source copy with path-redacted output.
- Ran explicit local-only write-alpha Docker/Caddy smokes under `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.
- Reset ignored runtime data and copied a fresh synthetic fixture before each route-family smoke.
- Executed each write route family exactly once per prepared runtime copy:
  - create: success plus failed validation cases;
  - PATCH: safe missing-transaction case plus success;
  - DELETE: success plus completed restore proof.
- Inspected audit/backup/lock via resilient redacted smoke helpers; all post-run lock evidence was `stale_released`, not active.
- Reset to default false, rendered `GNUCASH_WRITES_ENABLED=false`, and ran final read-only API smoke with validate/create/PATCH/DELETE disabled-write 403 probes.
- Stopped runtime, removed ignored runtime artifacts and local dummy `.env`, and verified runtime directories had zero non-placeholder files.

## Files changed

- `docs/dogfood/phase-200-write-alpha-cycle-3-dogfood.md`
- `docs/handoff/phase-200.md`
- `PROJECT_STATUS.md`

## Verification summary

Commands/results:

```text
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-copy>
# passed; status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; dry_run=true

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# write-alpha smokes: true rendered for API and web only during explicit APP_ENV=test disposable runs
# final reset: false rendered for API and web

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-create-smoke.py
# PASS; create succeeded exactly once; validation failures safe; backup/audit evidence present; lock stale_released, not active

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-patch-smoke.py
# PASS; missing transaction safe; PATCH succeeded exactly once; backup/audit evidence present; lock stale_released, not active

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py
# PASS; DELETE succeeded exactly once; backup/audit evidence present; restore proof completed; lock stale_released, not active

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
# PASS; validate/create/PATCH/DELETE returned disabled-write 403 after default-false reset

python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
# removed ignored runtime artifacts with redacted output

teardown scan
# data/books, data/app, data/backups, data/locks: non_placeholder_files=0
```

Final repository checks:

```text
cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py -q
# passed

cd apps/api && pytest -q
# passed

cd apps/web && npm run check
# passed

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# false rendered for API and web

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and was verified in rendered Compose after the write-alpha runs.
- Write-alpha was enabled only in local disposable `APP_ENV=test` runtime for the three route-family smokes.
- No real/private/only-copy book was used.
- No write route, write default, production behavior, release, tag, package, image, or broad safety claim was added.
- No app DB, runtime book, backup, lock, `.env`, screenshot, export, token, key, cert, raw path, account name, description, memo, amount, or private financial data was committed.

## Risks / follow-up

- This is bounded synthetic/disposable pre-alpha evidence only; it does not prove real/private-book write safety, production readiness, or security posture.
- Stale released lock files can remain after writes; Phase 200 confirms they were not actively held and cleanup remains stopped-runtime-only.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
