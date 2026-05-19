# Phase 123 — Write-alpha safety foundation without default enablement

Date: 2026-05-19
Status: complete
Previous phase: `docs/handoff/phase-122.md`

## Goal

Start post-MVP/write-alpha safety foundation work only, while keeping `GNUCASH_WRITES_ENABLED=false` as the default and not enabling or broadening controlled writes.

## Scope completed

- Started from clean `main` in sync with `origin/main` at `8a011cc4fcf7c030a45a3b42935351b6308e450a`.
- Reviewed `AGENTS.md`, `PROJECT_STATUS.md`, and recent handoffs before changes.
- Inspected existing controlled-write implementation and tests around:
  - disabled-by-default route gating;
  - backup service and backup-before-write ordering;
  - file-based write locks and lock contention;
  - audit logs for routed create/patch attempts;
  - create validation for split count, zero-sum, decimals, accounts, currencies, dates, and placeholder accounts.
- Added backend regression coverage in `apps/api/tests/test_transaction_writes.py` for Phase 123 gaps:
  - repository defaults keep writes disabled in `Settings`, `.env.example`, and Docker Compose fallback;
  - disabled validate/create/patch routes return 403 before resolving books or constructing a write service;
  - service validation explicitly reports split-count, invalid decimal, missing-account, invalid-date, non-zero-sum, and placeholder-account errors;
  - create-route write-lock failure is audited as a failed routed write attempt and records no backup path.
- Updated `docs/v0.2-controlled-writes.md` with Phase 123 readiness gates and remaining gaps before any real-user write enablement.
- Updated `PROJECT_STATUS.md` and `CHANGELOG.md` through Phase 123.

## Non-goals preserved

- No default write enablement.
- No new edit/delete/import/recurring/account-write capability.
- No frontend write UI change.
- No release publication, tag creation, GitHub release, package, or uploaded artifact.
- No production-book write safety claim.
- No real/private book, app DB, backup, `.env`, screenshot, CSV export, secret, token, key, cert, private path, account name, transaction description, memo, amount, or personal financial data committed.

## Verification run

Targeted RED/GREEN evidence:

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWritesDisabledByDefault tests/test_transaction_writes.py::TestWriteServiceValidationRules tests/test_transaction_writes.py::TestCreateTransaction::test_create_write_lock_failure_writes_failed_audit_log -q
```

RED result before adjustment: failed as expected because `TransactionSplitWriteDTO` schema rejected `amount="not-decimal"` at DTO construction before the service-level invalid-decimal regression could exercise `validate_transaction_create()`.

GREEN result after using Pydantic `model_construct()` only for the malformed service-level decimal probe: `9 passed, 1 warning`.

Final required checks for this phase:

```bash
cd apps/api && pytest -q
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
cd apps/api && python - <<'PY'
from app.config import Settings
print(f"Settings.gnucash_writes_enabled={Settings().gnucash_writes_enabled}")
PY
```

Results:

- Backend pytest: passed — `358 passed, 27 warnings in 133.54s`.
- Docker Compose config validation: passed with no output.
- `git diff --check`: passed with no output.
- Config default proof: `Settings.gnucash_writes_enabled=False`.

Frontend checks were not run because Phase 123 touched no frontend code, routes, styles, or web dependencies.

## Safety notes

- `GNUCASH_WRITES_ENABLED=false` remains the default in code, `.env.example`, and Docker Compose.
- Controlled writes remain experimental post-MVP/write-alpha work.
- The route-level disabled-write regression now proves write routes short-circuit before book resolution and write-service construction.
- Backup-before-write and write-lock coverage were inspected and left unchanged; Phase 123 added missing adjacent safety evidence rather than expanding write behavior.
- Remaining BLOCKED gaps before any real-user write enablement: maintainer review, broader supported-version write compatibility evidence, documented recovery/review procedure, and explicit later authorization.

## Files changed

- `apps/api/tests/test_transaction_writes.py`
- `docs/v0.2-controlled-writes.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-123.md`
