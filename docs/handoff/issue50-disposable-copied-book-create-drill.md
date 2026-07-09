# Issue #50 disposable copied-book web UI CREATE drill

Status: **REDACTED_DOCS_STATUS_RECORDED**
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

## Checks and safety counters re-run for this docs-status follow-up

These checks ran from the repository root on 2026-07-09 and used only synthetic or disposable test fixtures:

- `PYTHONPATH=apps/api apps/api/.venv/bin/python -m pytest apps/api/tests/test_owner_writebeta_synthetic_route_family_drill.py -q`
  - Result: `18 passed, 3 warnings in 13.78s`.
  - Covered one routed CREATE real-service-path drill, one route-family CREATE/PATCH/DELETE reset session,
    five immutable PATCH field rejection cases, and fail-closed drills for stale preview, expired preview,
    writes-disabled confirmation, missing backup/restore readiness, invalid account, and lock failure.
- `node apps/web/scripts/test-transaction-entry-preview.mjs`
  - Result: `transaction-entry-preview-static: ok`.
- `node apps/web/scripts/test-transaction-entry-preview-browser.mjs`
  - Result: `transaction-entry-preview-browser: ok (synthetic browser preview writes-disabled; explicit test-mode CREATE harness)`.
  - Browser/API counters asserted by the harness: exactly one normal `create-preview` request, zero browser-observed
    CREATE/PATCH/DELETE/batch/validate/preflight/backup/audit/write-beta boundary requests, four rejected
    partial/user-mode product-route CREATE probes, exactly one accepted explicit test-mode synthetic CREATE request
    against the API stub, and zero accepted non-disposable target requests.

Safety counters for this docs-status packet:

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

Continue into the issue #50 final full gates only after these redacted docs/status changes pass the scoped guards.
The next packet should run the full final gate list before posting any issue update or claiming broader completion.
