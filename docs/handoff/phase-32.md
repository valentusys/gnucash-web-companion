# Phase 32 — PM Brief: Backend Write-Gating Regression Coverage

## Status

Complete. Implemented by engineer in guarded background mission phase 3.

## PM decision

Make the next engineer phase an audit-driven safety regression-test phase for backend write-gating, focused on GitHub issue #18.

## Why

The immediately preceding audit (`docs/audits/2026-05-17-audit.md`, background mission phase 1) found that backend write-gating is currently effective by real API behavior: validate/create/patch returned 403 with writes disabled and the write service was not instantiated. However, that proof exists only as an ad-hoc audit probe plus one committed validate-endpoint disabled-writes test. The highest-risk accepted blocker is to make this protection durable in committed tests before any further release-value work or write-related cleanup.

This is not a feature phase. It is a safety guardrail phase.

## Goal

Turn the phase 1 ad-hoc FastAPI write-gating audit into committed regression coverage proving that, when `GNUCASH_WRITES_ENABLED=false`:

- `POST /books/{book_id}/transactions/validate` returns 403 with read-only wording;
- `POST /books/{book_id}/transactions` returns 403 with read-only wording;
- `PATCH /books/{book_id}/transactions/{transaction_id}` returns 403 with read-only wording;
- `_write_service_for` / `GnuCashWriteService` is not constructed or called for any of those disabled-write requests.

## Non-goals

- Do not enable writes by default.
- Do not add new write endpoints or write-mode UI.
- Do not broaden controlled writes beyond existing validate/create/patch behavior.
- Do not publish a tag, release, or package.
- Do not claim production-safe or audited write support.
- Do not remove safety warnings or reposition controlled writes as MVP v0.1.
- Do not commit real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, keys, certs, or real screenshots.

## Acceptance criteria

1. `Settings.gnucash_writes_enabled: bool = False` remains the default in `apps/api/app/config.py`.
2. Each existing controlled-write route still calls the write-enabled guard before any book-specific write service is constructed:
   - validate transaction;
   - create transaction;
   - patch transaction.
3. Committed tests cover disabled-write behavior for all three routes.
4. The tests fail if `_write_service_for` is called while writes are disabled.
5. Existing enabled-write tests still pass; the new tests must not mask regressions by leaving dependency overrides or monkeypatches behind.
6. Documentation/status updates describe this as safety regression coverage, not as expanded write support.
7. GitHub issue #18 is referenced and closed only if the committed tests satisfy the issue.

## Suggested implementation notes for engineer

- Prefer extending `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` rather than creating a broad new testing subsystem.
- Factor a small helper payload if it reduces duplication, but keep tests explicit enough that validate/create/patch are individually visible.
- Monkeypatch `app.routers.transactions._write_service_for` to raise or record calls, then assert zero calls / unreachable path for disabled-write requests.
- Use the existing in-memory app DB/test client fixtures where possible.
- Keep the dependency override for `READ_ONLY_TEST_SETTINGS` isolated and restored so later enabled-write tests continue to run.
- If a real regression is discovered, fix only the gate ordering/default needed to satisfy the safety criteria; do not refactor the write service broadly.

## Safety checks

Engineer must explicitly verify and report:

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The read-only MVP boundary remains intact.
- No backend write service is constructed when writes are disabled.
- No new GnuCash write capability, delete/import/recurring/account-edit feature, banking integration, or CSV/OFX import was added.
- No frontend auth token storage moved to localStorage/sessionStorage.
- No real financial/secrets artifacts were added.

## Verification commands

Required after implementation:

```bash
cd apps/api && pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

GitHub/status preflight:

```bash
git --version
gh --version || true
gh auth status || true
gh issue view 18 || true
```

## Files/docs to update

Expected production/test files:

- `apps/api/tests/test_transaction_writes.py` — primary expected change.
- `apps/api/app/config.py` — only if the default is found wrong; it should remain `False`.
- `apps/api/app/routers/transactions.py` — only if route ordering/gating is found wrong.

Expected docs/status files:

- `PROJECT_STATUS.md` — after engineer completion, mark Phase 32 complete and record test results.
- `docs/handoff/phase-32.md` — update this PM brief with implementation summary, verification, commit, and GitHub issue outcome.
- `CHANGELOG.md` — add an Unreleased safety/testing entry if tests are added.
- `docs/v0.2-controlled-writes.md` — optional: clarify that disabled-write bypass regression coverage exists after Phase 32; do not rewrite the design as production-ready.

## GitHub/backlog

- Primary issue: #18 “Verify backend write feature flag cannot be bypassed”.
- If criteria are satisfied, close #18 with the commit SHA and test command summary.
- Do not close #19, #20, #21, or #22 as part of this phase unless the engineer actually addresses them in scope, which is not expected.

## Handoff requirements for engineer

At completion, update this file with:

- implementation summary;
- exact tests/checks run and results;
- safety confirmation;
- commit SHA;
- push status;
- GitHub issue #18 status.

## Blockers

None.

## Engineer implementation summary

- Extended `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` into committed regression coverage for all three controlled-write routes:
  - `POST /books/{book_id}/transactions/validate`;
  - `POST /books/{book_id}/transactions`;
  - `PATCH /books/{book_id}/transactions/{transaction_id}`.
- Added a default-settings assertion that `Settings().gnucash_writes_enabled is False`.
- Added a monkeypatched `_write_service_for` sentinel that raises if the write service is constructed while writes are disabled; each disabled-write route test asserts it remains uncalled.
- Updated `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/v0.2-controlled-writes.md` to describe this as safety regression coverage only, not expanded write support.

## Verification

- `cd apps/api && pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` — passed (`4 passed`, one existing piecash/SQLAlchemy deprecation warning).
- `cd apps/api && pytest -q` — passed (`269 passed`, 27 existing warnings).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed (`svelte-check found 0 errors and 0 warnings`; auth route checks passed; build completed).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

## Safety confirmation

- `Settings.gnucash_writes_enabled: bool = False` remains the default in `apps/api/app/config.py`.
- Existing `_ensure_writes_enabled()` guard remains in place and is called before book-specific write-service construction in validate/create/patch routes.
- No backend write service is constructed when writes are disabled, proven by committed API tests.
- No new GnuCash write capability, delete/import/recurring/account-edit feature, banking integration, CSV/OFX import, frontend auth token storage change, real financial artifact, or secret was added.

## Commit / push / GitHub

- Implementation commit: `5bdb201` (`test: cover disabled write gating`).
- Handoff/status commits: `9deec92`, `9969b21`.
- Push: pushed to `origin/main` after this status update.
- GitHub issue #18: closed after commits were pushed and checks passed.
