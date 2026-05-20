# Phase 179 — write-alpha API hardening from dogfood findings

Date: 2026-05-20
Status: COMPLETE — backend path-safe error hardening from disposable write-alpha dogfood findings
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 8 only)

## Scope

This phase fixed one concrete backend safety gap linked to Phase 175–178 copied/disposable write-alpha dogfood: backend write-alpha error details could still expose raw path-like internals during lock contention or post-backup write failures, while Phase 178 had to defensively suppress such strings in frontend forms.

No new write endpoint, write operation, production/private-write support, direct SQL write, or default write enablement was added.

## Backend changes

- Write-alpha route lock-contention responses now return a generic per-book lock message without embedding the lock key or book path.
- Write-alpha `GnuCashWriteError` handling now uses a safe detail helper:
  - preserves validation/business errors that do not look like paths or URIs;
  - collapses path-like or URI-like internals to a generic operator-safe failure message;
  - keeps backup evidence in the explicit `backup_path` audit/response field rather than in error text.
- Create/PATCH/DELETE scope and route shapes remain unchanged.

## Regression coverage

Added route-level copied/disposable fixture tests for:

- path-like post-backup create failures: API response and audit `error` no longer include the source path, while `backup_path` remains recorded;
- active lock contention/stale-lock-style failures: API response and audit `error` no longer include the book/lock path and still report write-lock contention;
- existing disabled-write short-circuit, test-only gate, backup-before-write, audit, and lock-release coverage remains in `tests/test_transaction_writes.py`.

## Safety result

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-enabled paths still require `APP_ENV=test` and explicit copied/disposable test scope.
- No real/private/only-copy book was opened or mutated in this phase.
- No raw GnuCash book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data is committed.
- No release/tag/package was published.

## Verification performed

```bash
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_path_like_create_failure_uses_safe_api_and_audit_error tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_lock_contention_error_does_not_leak_lock_file_or_book_path tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_concurrent_enabled_create_allows_one_success_and_one_lock_contention tests/test_transaction_writes.py::TestWritesDisabledByDefault::test_disabled_write_routes_short_circuit_before_book_resolution -q
```

Result: passed (`4 passed`, piecash/SQLAlchemy warnings only).

Additional verification recorded in `docs/handoff/phase-179.md`: full `tests/test_transaction_writes.py` passed, full backend `pytest -q` passed (`404 passed, 33 warnings`), Docker Compose config validation passed with `GNUCASH_WRITES_ENABLED: "false"`, `git diff --check` passed, and sensitive tracked-file hygiene scan passed.
