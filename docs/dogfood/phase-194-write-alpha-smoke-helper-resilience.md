# Phase 194 — Write-alpha smoke helper resilience dogfood

Date: 2026-05-20
Status: PASS on synthetic/disposable local runtime
Scope: smoke-helper resilience only; no write-route semantics, scope, defaults, or release state changed.

## Goal

Confirm that the create/PATCH/DELETE write-alpha smoke helpers can finish with bounded, path-redacted evidence when runtime artifacts are host-side root-owned or otherwise unreadable, without rerunning successful mutating routes.

## Safety setup

- Runtime used only a committed synthetic fixture copied into ignored `data/books/main.gnucash.sqlite`.
- Mutating helper runs used explicit local-only `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.
- Default read-only verification before and after used `GNUCASH_WRITES_ENABLED=false`.
- Cleanup used stopped-runtime acknowledgement and redacted runtime cleanup.
- No real/private/only-copy book, `.env`, app DB, backup, screenshot, CSV export, token, key, cert, raw path, account name, memo, amount, or private data was committed.

## Evidence summary

### Default read-only pre-smoke

Command:

```bash
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-api-smoke.py
```

Result: PASS. Health/login/books/accounts/transactions/detail/CSV/reports passed. Disabled validate/create/PATCH/DELETE probes returned 403.

### Write-alpha create helper

Setup: fresh ignored synthetic runtime copy, local Docker/Caddy with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.

Command:

```bash
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-create-smoke.py
```

Result: PASS.

Bounded evidence:

- exactly one balanced two-split create succeeded;
- validation rejected unbalanced and invalid-account probes;
- backup count increased before mutation response returned;
- `transaction.create` success audit count increased by exactly one;
- lock evidence was `stale_released`, not active;
- output remained redacted.

A first local attempt before the compose-env fallback fix executed the create route successfully but stopped at container evidence collection because `docker compose exec` interpolation lacked dummy compose env vars in the smoke process. The mutating route was not rerun on that same runtime. Container-side redacted inspection showed one backup, one successful create audit, and one stale lock. The helper was fixed, runtime was cleaned, a fresh synthetic copy was prepared, and the create helper then passed once.

### Write-alpha PATCH helper

Setup: fresh ignored synthetic runtime copy, local Docker/Caddy with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.

Command:

```bash
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-patch-smoke.py
```

Result: PASS.

Bounded evidence:

- missing-transaction PATCH returned 404 without a new backup;
- exactly one metadata/split-memo PATCH succeeded;
- API/runtime read-back matched synthetic markers only;
- split amount fingerprint was unchanged;
- backup count increased before mutation response returned;
- success audit count increased by exactly one and failed safe-error audit was recorded;
- lock evidence was `stale_released`, not active;
- output remained redacted.

### Write-alpha DELETE + restore helper

Setup: fresh ignored synthetic runtime copy, local Docker/Caddy with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.

Command:

```bash
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-delete-restore-smoke.py
```

Result: PASS.

Bounded evidence:

- exactly one existing synthetic transaction DELETE succeeded;
- API/runtime absence checks confirmed the transaction was deleted;
- backup count increased by exactly one before mutation response returned;
- success audit count increased by exactly one;
- backup contained the deleted transaction with matching bounded split fingerprint;
- restore proof was emitted because the host-readable backup was actually copied back into the disposable runtime copy and API read-back passed;
- lock evidence was `stale_released`, not active;
- output remained redacted.

### Final default read-only smoke

After stopped-runtime cleanup and fresh ignored synthetic copy, local Docker/Caddy was started with `GNUCASH_WRITES_ENABLED=false`.

Command:

```bash
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-api-smoke.py
```

Result: PASS. Disabled validate/create/PATCH/DELETE probes returned 403.

Final cleanup dry-run reported zero artifacts in ignored `books`, `app`, `backups`, and `locks` classes.

## Helper behavior verified

- Host-side backup/audit/lock evidence collection now falls back to API-container read-only inspection when local permissions block access.
- Container probe output is JSON-only and reduced to counts/statuses; raw paths, filenames, audit payloads, account names, memos, and amounts are not printed.
- The helpers do not rerun mutating routes after a route success just to recover evidence.
- DELETE restore proof is printed only when a restore copy actually happens; otherwise the helper reports a path-safe restore-skip status after container-side backup evidence.

## Boundaries

This is smoke tooling resilience evidence only. It is not production readiness, not a security audit, not a real/private-book write-safety claim, and not release publication evidence. Writes remain disabled by default and write-alpha remains `APP_ENV=test` plus explicit local-only enablement only.
