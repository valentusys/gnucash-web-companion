# Phase 183 — write-alpha lock recovery evidence

Date: 2026-05-20
Status: COMPLETE — redacted lock evidence path tightened without expanding write scope

## Goal

Tighten the practical recovery path after Phase 177/180 findings: a remaining `.lock` file after released `flock`, and host-side root-owned lock readability, must have safe operator guidance and test coverage without changing write-alpha scope.

## Evidence collected

This phase did not run a new GnuCash write. It exercised the lock-evidence helper on synthetic temporary lock files only, outside tracked runtime data, to prove classification semantics used by disposable write-alpha dogfood.

Redacted command class:

```text
python3 - <<'PY'
# import scripts/smoke/write-alpha-create-smoke.py
# create temporary lock root under /tmp
# inspect absent, stale released, and actively held flock states
PY
```

Redacted output summary:

```text
absent not_present False
stale stale_released False lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage
active active True write lock remains actively held after create
```

No book path, lock path, account name, transaction description, memo, amount, app DB row, backup filename, token, `.env`, screenshot, CSV export, or private data was printed or committed.

## Behavior now covered

- Active lock hold remains a write-contention condition and existing route coverage verifies it returns HTTP 409 with a path-safe message.
- Stale released lock files are classified as `stale_released`, not active contention, in both backend helper coverage and smoke-helper evidence coverage.
- Unreadable lock files are classified separately as `unreadable` with guidance to inspect from the API container or fix runtime ownership before removing only a book-specific stale lock with the app stopped.
- Operator guidance explicitly avoids raw paths and does not recommend real/private or only-copy books.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write endpoint scope changed: create/PATCH/DELETE behavior and gates are unchanged.
- No automatic lock deletion was added.
- No production lock-management UI was added.
- No real/private/only-copy book was used.
- No runtime book, backup, app DB, lock file, `.env`, token, key, cert, screenshot, export, or private data artifact was committed.
