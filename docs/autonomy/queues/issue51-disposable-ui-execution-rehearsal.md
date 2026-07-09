# Issue #51 disposable copied-book UI execution rehearsal autonomy queue

This queue seeds a sustained repo-local autonomy run for issue #51. It is
product/code/test first and authorizes CREATE/PATCH/DELETE only against
synthetic or disposable copied-like SQLite fixtures created inside test tempdirs
or ignored runtime paths outside the repository.

Use with:

```bash
--on-empty generate-from-policy \
--backlog-policy docs/autonomy/backlog-policies/issue51-disposable-ui-execution-rehearsal.md
```

The queue does not authorize owner financial files, Syncthing working files,
private/original/only-copy targets, release work, public write posture changes,
or committed book/backup/export/screenshot artifacts.

## Task: issue51-ui-execution-rehearsal-harness
- target: issue #51 / browser UI execution rehearsal harness
- goal: Add or tighten a browser/manual-like harness that drives the `/transactions/new` transaction-entry form through preview and reviewed approval evidence, then reaches only an explicit test-mode execution path for a synthetic or disposable copied-like target.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/web/package.json, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; normal/default UI CREATE activation; screenshots; committed runtime artifacts; releases; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into result UI and product-path CREATE proof when browser execution remains explicit test-mode only

## Task: issue51-result-panel
- target: issue #51 / redacted CREATE result panel
- goal: Add or tighten a redacted success/result state for the explicit synthetic test-mode CREATE rehearsal that shows create_count, read-back verification, backup/audit states, reset/default-disabled probe summary, and no private/raw book data.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: raw book paths; private account names; screenshots; normal/default UI CREATE activation; releases; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into routed disposable CREATE evidence when the result state is redacted and default mode remains preview-only

## Task: issue51-product-path-create-drill
- target: issue #51 / UI-to-route disposable CREATE drill
- goal: Connect the explicit test-mode UI harness to the same backend route/write boundary used by the product path for exactly one bounded CREATE against a disposable copied-like fixture, then prove backup, lock, audit, write, read-back, reopen, split balance, currency, date, description, memo, ownership, reset, and disabled probes.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; direct SQL writes; committed books/backups/raw evidence; normal/default UI CREATE activation; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, create-test, readback-test, disabled-probes, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into normal-mode and failure UI guards when the bounded CREATE count is one and all evidence is redacted

## Task: issue51-normal-mode-preview-only-guard
- target: issue #51 / normal UI preview-only guard
- goal: Prove the normal/default `/transactions/new` path still submits only preview requests, keeps Future Create inert, and cannot reach the explicit test-mode execution path through ordinary browser use.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: enabling default CREATE; owner/private/original/working/Syncthing/only-copy targets; screenshots; releases; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into failure UI once the default browser path is proved preview-only

## Task: issue51-failure-ui-drills
- target: issue #51 / failure UI drills
- goal: Cover stale preview rejection, target preflight rejection, writes-disabled rejection, backup failure, lock failure, read-back failure, reset/probe failure, and safe recovery copy in browser-visible or API-result-shaped redacted UI evidence.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; raw paths; weakening safety guards; committed runtime artifacts; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, failure-drill, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into browser smoke hardening when failure states are redacted and fail closed

## Task: issue51-browser-create-disposable-smoke
- target: issue #51 / disposable CREATE browser smoke command
- goal: Add or expand deterministic browser smoke, and add `npm run test:transaction-entry-create-disposable-browser` if useful, to prove the UI rehearsal reaches only the explicit synthetic/disposable CREATE path and never browser-drives non-disposable targets or raw evidence.
- allowed scope: apps/web/scripts/test-transaction-entry-preview*.mjs, apps/web/scripts/**, apps/web/package.json, apps/web/src/routes/transactions/new/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: screenshots; owner/private/original/working/Syncthing/only-copy targets; default CREATE activation; mutation requests against non-disposable targets; release work; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into guard hardening if the browser smoke stays synthetic/disposable-only

## Task: issue51-backend-frontend-smuggling-guards
- target: issue #51 / execution gate and smuggling guards
- goal: Harden backend and frontend guards so the explicit create harness requires synthetic/disposable proof, rejects query/header smuggling into non-disposable targets, and leaves no write endpoint reachable without explicit test-mode gates.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, scripts/check_*.py, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; deleting safety guards; weakening defaults; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into optional PATCH/DELETE if execution gates are fail-closed

## Task: issue51-patch-metadata-ui-rehearsal
- target: issue #51 / optional metadata-only PATCH UI rehearsal
- goal: If CREATE rehearsal is already proven, add or improve UI/API-shaped PATCH rehearsal only for app-created disposable transactions and only for description/memo metadata, while rejecting amount, account, split, date, and currency changes.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: PATCH on non-app-created transactions; balance-affecting PATCH; owner/private/original/working/Syncthing/only-copy book access; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, patch-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into DELETE only if PATCH remains metadata-only and app-owned

## Task: issue51-delete-app-owned-ui-rehearsal
- target: issue #51 / optional app-owned DELETE UI rehearsal
- goal: If time remains, add or improve UI/API-shaped DELETE rehearsal only for app-owned synthetic/disposable transactions and prove non-owned or non-disposable DELETE attempts are rejected.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: DELETE on historical/manual/non-owned transactions; owner/private/original/working/Syncthing/only-copy book access; direct SQL workarounds; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, delete-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into redacted docs and final gates if app-owned DELETE is bounded or explicitly deferred

## Task: issue51-redacted-docs-status
- target: issue #51 / redacted docs and status
- goal: Update PROJECT_STATUS, owner transaction-entry workflow docs, and the issue51 handoff with what actually passed, clearly separating untouched owner/private/working/Syncthing books from synthetic/disposable targets and default production-disabled posture.
- allowed scope: docs/handoff/issue51-disposable-ui-execution-rehearsal.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: raw transaction data; private paths; account names from non-synthetic sources; screenshots; books/backups/exports; releases; public write beta claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into final full gates if docs are redacted and status matches real checks

## Task: issue51-final-gates-and-issue-update
- target: issue #51 / final gates and issue update
- goal: Run the required final local checks, run the new disposable-browser command if it exists, update GitHub issue #51 with a redacted result packet if gh is available, and leave the repository clean with committed safe scoped changes.
- allowed scope: docs/handoff/issue51-disposable-ui-execution-rehearsal.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md, apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, apps/web/package.json
- non-goals: raw evidence; committed books/backups/exports/screenshots; release/tag/package/image publication; public write beta claims; owner/private/original/working/Syncthing/only-copy book access
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
- safety flags: no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only if the runtime budget still has safe generated policy work
