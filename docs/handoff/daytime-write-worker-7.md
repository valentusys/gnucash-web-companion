# Daytime Write Worker 7 — #36-W1-A route/state fail-closed matrix

## Worker ID

daytime-write-worker-7

## Target issue

#36 — controlled-write v0.2 readiness gates

## Package

#36-W1-A — Route/state fail-closed matrix.

## Goal

Add focused regression coverage proving the shared routed mutation guard fails closed before CREATE/PATCH/DELETE can proceed unless an owner-writebeta session is exactly armed with a matching, unexpired confirmation and restore-readiness evidence.

## Scope completed

Added `apps/api/tests/test_owner_writebeta_route_guard_fail_closed.py` with 13 tests for `require_owner_writebeta_if_active()`:

- inactive/no-session and DISABLED sessions do not bypass the older write gates or mutate state;
- every active non-CONFIRMATION state fails closed with HTTP 403 and leaves state unchanged;
- missing preview hash / confirmation token headers fail closed;
- mismatched preview hash fails closed;
- mismatched confirmation token fails closed;
- expired confirmation fails closed without transitioning to MUTATING;
- missing restore-readiness evidence fails closed without transitioning to MUTATING;
- a matching, unexpired confirmation with restore-readiness evidence transitions exactly once to MUTATING;
- a second attempt after MUTATING is rejected.

No production code changed.

## Verification

From `apps/api`:

```text
python -m pytest -q tests/test_owner_writebeta_route_guard_fail_closed.py --tb=short
13 passed, 1 warning in 0.93s
```

Related owner-writebeta suite:

```text
python -m pytest -q \
  tests/test_owner_writebeta_route_guard_fail_closed.py \
  tests/test_owner_writebeta_routes.py \
  tests/test_owner_writebeta_state_machine.py \
  tests/test_owner_writebeta_synthetic_failure_drill.py --tb=short
55 passed, 1 warning in 15.27s
```

Repository check:

```text
git diff --check
# clean
```

## Safety notes

- No original/private/working/only-copy GnuCash book was touched.
- Tests use synthetic in-memory `OwnerWritebetaSession` objects only.
- No GnuCash book, SQLite book, backup, export, screenshot, `.env`, token, key, private path, account name, transaction description, memo, amount, or raw private evidence was added.
- `GNUCASH_WRITES_ENABLED=false` default remains unchanged.
- `APP_ENV=test` gate remains unchanged.
- No public write beta and no release.

## Issue #36 comment draft

> daytime-write-worker-7 (#36-W1-A): Added routed mutation-guard fail-closed matrix tests for `require_owner_writebeta_if_active()`. New coverage proves every active non-CONFIRMATION state rejects mutation, missing preview/confirmation headers reject, mismatched preview hash/token reject, expired confirmations reject without mutating, missing restore-readiness evidence rejects without mutating, and a matching unexpired confirmation transitions exactly once to MUTATING before subsequent attempts reject. Verification: route-guard test 13 passed; related owner-writebeta suite 55 passed; `git diff --check` clean. No production code change, no book mutation, no private evidence, writes remain default-disabled.

## Blockers

None for this package.
