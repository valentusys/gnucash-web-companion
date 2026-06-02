# Overnight 2026-06-02 worker 02 handoff

## Target

- Worker task ID: `overnight-2026-06-02-worker-02`
- Issue/package: #36 — Default-disabled reset probe tests
- Scope: non-mutating owner-writebeta/write-alpha reset/default-disabled route guards only

## Summary of changes

- Added a route-level owner-writebeta reset/default-disabled regression test.
- The test simulates an already-admitted routed mutation by moving the in-memory owner-writebeta session to `mutating`; it does not open, copy, or mutate any GnuCash book.
- The test verifies `verify-reset` with reset evidence reaches `reset_required`, `reset-disabled` returns the session to `disabled`, and default-disabled validate/CREATE/PATCH/DELETE probes all remain 403/read-only after reset.
- Tightened `OwnerWritebetaSession.transition(... DISABLED)` so completed reset drops stale active-arm material (`preview_hash`, `confirmation_token_ref`, `expires_at`) while preserving opaque post-mutation evidence refs.

## RED/GREEN TDD cycle

RED:

```text
cd apps/api && pytest tests/test_owner_writebeta_routes.py::test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed -q
```

Result before code change:

```text
FAILED ... assert 'owb-prev-29a8181cd3292944' is None
1 failed, 1 warning
```

GREEN:

```text
cd apps/api && pytest tests/test_owner_writebeta_routes.py::test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed -q
```

Result after minimal state-machine change:

```text
1 passed, 1 warning
```

## Files changed

- `apps/api/app/owner_writebeta_state_machine.py`
- `apps/api/tests/test_owner_writebeta_routes.py`
- `PROJECT_STATUS.md`
- `docs/handoff/overnight-2026-06-02-worker-02.md`

## Tests and verification

Completed locally:

```text
cd apps/api && pytest tests/test_owner_writebeta_routes.py::test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed -q
# 1 passed, 1 warning

cd apps/api && pytest tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_state_machine.py tests/test_transaction_writes.py::TestWritesDisabledByDefault -q
# 22 passed, 1 warning
```

Additional verification completed locally:

```text
cd apps/api && pytest tests/test_owner_writebeta_routes.py tests/test_owner_writebeta_state_machine.py tests/test_transaction_writes.py::TestWritesDisabledByDefault -q
# 22 passed, 1 warning

cd apps/api && pytest -q
# 645 passed, 38 warnings

git diff --check
# passed

python3 scripts/check_public_status.py
# public-status-guard: ok

python3 scripts/check_tracked_hygiene.py
# Tracked hygiene check passed (1727 tracked paths inspected).

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed
```

## CI

- CI link: pending until commit is pushed.

## Safety summary

- Mutation counts in this package: CREATE 0 / PATCH 0 / DELETE 0.
- No real/private/original/only-copy/working GnuCash book was opened, copied, or mutated.
- No app DB, GnuCash book, backup, CSV/export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence was committed.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` write gate remains unchanged.
- No write-alpha/writebeta scope expansion, release/tag/package/image, public write beta, production/stable/security-audited claim, or real-book write-safety claim was added.

## Issue update

- #36 should remain open.
- Planned issue comment summary: default-disabled reset route test added; stale active-arm refs now cleared on disabled reset; disabled write-route probes remain 403/read-only after reset; exact remaining gates remain broader controlled-write readiness and any future copied/restorable evidence under explicit owner/PM authorization.

## Commit

- Commit SHA: `414c22c` (`fix: clear owner-writebeta reset arm state`).

## Remaining blockers

- #36 broader controlled-write readiness remains open.
- Real working/private/original/only-copy mutation remains blocked.
- Any future copied/restorable mutation evidence requires exact same-context owner + PM authorization and full backup/restore/read-back/audit/compatibility/redaction gates.
- No public write beta or owner-writebeta release is justified by this package.

## Recommendation for supervisor next package

- Keep #36 open and choose another non-mutating readiness gate, preferably rollback/error-path expectations or maintainer review/recovery procedure docs/tests.
- Do not move to real mutation/dogfood from this package.
