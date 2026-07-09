# Issue #50 disposable copied-book web UI CREATE drill

Status: **FINAL_LOCAL_GATES_RECORDED**
Issue: [#50 Disposable copied-book web UI CREATE drill](https://github.com/valentusys/gnucash-web-companion/issues/50)
Related docs: [PROJECT_STATUS.md](../../PROJECT_STATUS.md),
[owner transaction-entry workflow](../write-alpha/owner-transaction-entry-workflow.md)

This handoff is redacted. It records tracked code/test coverage and local guard posture only. It does not include
raw transaction data, private paths, non-synthetic account names, screenshots, books, backups, exports, `.env`,
tokens, keys, certs, or app DBs.

## Scope boundary

Allowed evidence class for #50 is synthetic or disposable copied-like SQLite fixtures created in test tempdirs or
ignored runtime paths outside the repository. Owner/private/original/working/Syncthing/only-copy GnuCash books stay
untouched by this packet.

Default production posture remains disabled:

- `GNUCASH_WRITES_ENABLED=false` remains the default;
- enabled write routes remain `APP_ENV=test` gated;
- no release, tag, package, image, public write beta, stable, production-ready, or security-audited claim is made;
- no default/user-mode web CREATE is enabled.

## What passed in current tracked coverage

1. Disposable target preflight and route-family gating.
   - Routed CREATE/PATCH/DELETE fail closed before write service construction when the target lacks copied,
     disposable, or synthetic proof.
   - Targets that appear inside the repository are rejected before write service construction.
   - Rejection details are redacted and do not echo raw private-looking paths.

2. Routed CREATE drill on disposable SQLite fixtures.
   - CREATE runs through the backend route against temporary disposable fixture data only.
   - The route records backup-before-write, audit row, read-back metadata, write-alpha ownership, and released lock
     evidence.
   - Reopen/read-only checks verify the created transaction is present with exact date, description, Decimal-string
     amounts, currency, memo fields, split count, and balanced split totals.
   - Balance deltas are verified through read-only service paths for both two-split and multi-split synthetic cases.

3. Reset and disabled probes.
   - After bounded synthetic route-family sessions, owner-writebeta state resets to disabled and clears preview/
     confirmation/restore refs.
   - With `GNUCASH_WRITES_ENABLED=false`, validate, readiness/preflight, CREATE, PATCH, DELETE, and batch route
     families are blocked or unavailable before additional write calls.

4. Failure drills.
   - Stale preview/confirmation headers reject before audit or write service.
   - Writes-disabled runtime rejects even with a fresh owner-writebeta confirmation.
   - Missing backup or restore-readiness evidence blocks CREATE before write service construction.
   - Invalid-account and write-lock failures hard-stop the session with redacted recovery messaging and failed audit
     rows where the route has entered the write boundary.
   - Read-back failure, backup failure, and post-backup write failure are covered on disposable fixtures without
     claiming success from uncertain results.

5. Web UI and browser synthetic harness boundaries.
   - The normal `/transactions/new` browser path remains preview-only and submits only `create-preview`.
   - Future Create stays disabled/inert in default/user mode.
   - The deterministic browser harness rejects browser-observed CREATE/PATCH/DELETE/batch/validate/preflight,
     backup, audit, and write-beta boundary requests.
   - The explicit synthetic CREATE harness is test-only, header/query gated, product-route shaped, and uses the
     synthetic API stub; it does not activate default UI CREATE.
   - Synthetic API boundary checks reject non-disposable target requests and query-smuggled mutation routes.

6. Optional PATCH and DELETE bounds.
   - PATCH coverage stays metadata-only for write-alpha-created/app-owned disposable transactions.
   - PATCH rejects amount, account, split, date, currency, nested financial payloads, non-owned transactions, and
     non-disposable targets without mutation.
   - DELETE coverage is limited to write-alpha-created/app-owned disposable transactions.
   - DELETE rejects non-owned, inert-marker, active unarmed preview, missing, and non-disposable targets before the
     write service where applicable.

## Final local gates re-run for this follow-up

These checks ran from the repository root on 2026-07-09. Backend/API tests and browser harnesses used only
synthetic or disposable test fixtures; no product dogfood or private target probe was run.

- `python3 scripts/check_public_status.py`
  - Result: `public-status-guard: ok`.
- `python3 scripts/check_write_safety_defaults.py`
  - Result: `write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; APP_ENV=development default present;
    APP_ENV=test gate text present; explicit write enablement present; reset/default-disabled probe wording present`.
- `python3 scripts/check_markdown_readability.py`
  - Result: `markdown-readability-guard: ok (27 docs checked)`.
- `python3 scripts/check_tracked_hygiene.py`
  - Result: `Tracked hygiene check passed (1961 tracked paths inspected).`
- `git diff --check`
  - Result: exit 0 with no whitespace errors.
- `cd apps/api && pytest -q`
  - Result: `1090 passed, 56 warnings in 346.76s (0:05:46)`.
- `cd apps/web && npm run check`
  - Result: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run build`
  - Result: exit 0; Vite production build completed and adapter-node reported `done`.
- `cd apps/web && npm run test:transaction-entry-preview`
  - Result: `transaction-entry-preview-static: ok`.
- `cd apps/web && npm run test:auth-routes`
  - Result: `auth route checks passed`.
- `cd apps/web && npm run test:transaction-entry-preview-browser`
  - Result: `transaction-entry-preview-browser: ok (synthetic browser preview writes-disabled; explicit test-mode
    CREATE harness)`.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - Result: exit 0 with no rendered-config errors.

Safety counters for this final-gates packet:

- owner/private/original/working/Syncthing/only-copy books opened, copied, or mutated: 0;
- product dogfood runs or private target probes: 0;
- committed books, backups, exports, screenshots, app DBs, `.env`, tokens, keys, certs, or unredacted evidence files: 0;
- release, tag, package, image, public write beta, stable, production-ready, or security-audited claims: 0;
- default write-posture flips: 0; `GNUCASH_WRITES_ENABLED=false` and enabled-write `APP_ENV=test` gates are preserved.

## What did not happen

- No owner/private/original/working/Syncthing/only-copy book was opened, copied, or mutated.
- No raw book, backup, export, screenshot, app DB, `.env`, token, key, cert, or private evidence was committed.
- No production/default write posture changed; rendered Compose defaults remain expected to keep writes disabled.
- No public write beta, broad compatibility, release, stable, production-ready, or security-audited claim is made.
- No GitHub issue update or release publication is part of this docs-status packet.

## Follow-up

Issue #50 final local gates are recorded for this disposable-fixture-only packet. Any GitHub issue update,
product dogfood, private target probe, release work, or future mutating step remains outside this packet and
requires fresh explicit scope/approval.
