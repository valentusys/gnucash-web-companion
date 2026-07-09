# Issue #51 app-owned DELETE UI rehearsal

Status: **BOUNDED_SYNTHETIC_REHEARSAL_ADDED**
Issue: [#51 optional app-owned DELETE UI rehearsal](https://github.com/valentusys/gnucash-web-companion/issues/51)
Related docs: [PROJECT_STATUS.md](../../PROJECT_STATUS.md),
[owner transaction-entry workflow](../write-alpha/owner-transaction-entry-workflow.md)

This handoff is redacted. It records synthetic/disposable fixture-only code and test coverage. It does not include
raw transaction data, private paths, account names, descriptions, memos, amounts, screenshots, books, backups,
exports, app DBs, `.env`, tokens, keys, certs, or raw private evidence.

## Scope boundary

Issue #51 coverage is limited to app-owned/write-alpha-created transactions on synthetic or disposable copied-like
SQLite fixtures created in test tempdirs outside the repository. It does not authorize DELETE for historical,
manual, non-owned, owner/private/original/working/Syncthing, or only-copy books.

Default write posture remains unchanged:

- `GNUCASH_WRITES_ENABLED=false` remains the default;
- enabled write routes remain `APP_ENV=test` gated;
- the normal `/transactions/new` UI remains preview-only and does not activate DELETE;
- no release, tag, package, image, public write beta, stable, production-ready, or security-audited claim is made.

## What changed

1. Added `apps/web/scripts/issue51_product_delete_drill.py`.
   - Creates exactly one app-owned disposable transaction as setup through the product CREATE route.
   - Proves a non-owned DELETE attempt is rejected without mutation or backup creation.
   - Proves an app-owned but non-disposable DELETE attempt is rejected without mutation or backup creation.
   - Executes exactly one product-route DELETE for the app-owned disposable setup transaction.
   - Reopens the disposable fixture and verifies the transaction is absent, retained transactions are unchanged,
     balances are reverted, a pre-delete backup exists, and a success audit row is recorded.
   - Resets to default-disabled writes and verifies DELETE is blocked after reset.
   - Emits only a redacted result panel with opaque refs; raw paths, IDs, account values, amounts, memos,
     descriptions, screenshots, and secrets are not emitted.

2. Extended the deterministic browser rehearsal harness.
   - The explicit test-mode browser script now runs the backend product-route DELETE drill after the existing
     disposable CREATE and metadata-only PATCH rehearsals.
   - The default/user-mode synthetic API still rejects DELETE requests, including query-smuggled explicit-test
     attempts, as inert boundary probes.
   - The browser boundary asserts the explicit DELETE harness is not default UI activation and does not broaden
     the `/transactions/new` product UI.

3. Added inactive UI contract copy on `/transactions/new`.
   - The page now documents a redacted app-owned DELETE result-panel contract as inactive display-only guidance.
   - The contract states that only app-created disposable targets are in scope and that non-app-created and
     non-disposable DELETE attempts must be rejected before mutation.
   - The contract forbids raw product-route result fields and private evidence in any DELETE result panel.

## Safety counters for this packet

- owner/private/original/working/Syncthing/only-copy books opened, copied, or mutated: 0;
- product dogfood runs or private target probes: 0;
- committed books, backups, exports, screenshots, app DBs, `.env`, tokens, keys, certs, or raw evidence files: 0;
- default write-posture flips: 0;
- public write beta, release, stable, production-ready, or security-audited claims: 0.

## Final local verification

These task-required gates ran from the repository root in isolated shells after staging the safe tracked changes:

- `cd apps/api && pytest -q`
  - Result: `1096 passed, 56 warnings in 347.54s (0:05:47)`.
- `cd apps/web && npm run test:transaction-entry-preview`
  - Result: `transaction-entry-preview-static: ok`.
- `cd apps/web && npm run test:transaction-entry-preview-browser`
  - Result: `transaction-entry-preview-browser: ok (normal browser preview-only/failure/query guards; explicit test-mode product-route disposable CREATE, metadata-only PATCH, and app-owned DELETE drills)`.
- `python3 scripts/check_write_safety_defaults.py`
  - Result: `write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; APP_ENV=development default present; APP_ENV=test gate text present; explicit write enablement present; reset/default-disabled probe wording present`.
- `python3 scripts/check_tracked_hygiene.py`
  - Result: `Tracked hygiene check passed (1967 tracked paths inspected).`
- `git diff --check`
  - Result: exit 0 with no whitespace errors.

Supplemental staged-diff whitespace check also passed with `git diff --cached --check`.

## Follow-up

Issue #51 remains bounded to synthetic/disposable fixture-only DELETE rehearsal evidence. Any owner/private target,
product dogfood, historical/manual/non-owned DELETE, release work, or public write posture change remains outside
this packet and requires fresh explicit scope/approval.
