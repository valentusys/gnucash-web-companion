# Issue #50 disposable copied-book web UI CREATE drill autonomy queue

This queue seeds a sustained repo-local autonomy run for issue #50. It is
product/code/test first and authorizes routed write-alpha operations only against
synthetic or disposable copied-like SQLite fixtures created inside test tempdirs
or ignored runtime paths outside the repository.

Use with:

```bash
--on-empty generate-from-policy \
--backlog-policy docs/autonomy/backlog-policies/issue50-disposable-copied-book-create-drill.md
```

The queue does not authorize owner financial files, Syncthing working files,
private/original/only-copy targets, release work, public write posture changes,
or committed book/backup/export/screenshot artifacts.

## Task: issue50-disposable-target-preflight-harness
- target: issue #50 / disposable target preflight harness
- goal: Build or tighten a test harness that creates a synthetic or copied-like SQLite fixture in a temp workspace, proves the target is outside the repo and disposable, and fails closed before any routed CREATE when that proof is absent.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; committing SQLite books/backups/exports/screenshots; releases; public write beta claims; default write enablement
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into routed CREATE once the disposable target preflight fails closed and stays outside repo

## Task: issue50-routed-create-drill
- target: issue #50 / routed CREATE drill
- goal: Exercise one bounded routed CREATE through the backend application write boundary against a disposable copied-like fixture, including backup before write, read-back after write, audit row, Decimal string amount, currency, date, description, memo, and two balanced splits.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; direct SQL writes; committed books/backups/raw transaction dumps; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into reopen and reset probes after CREATE read-back and audit proof pass on disposable data

## Task: issue50-reopen-balance-verification
- target: issue #50 / reopen and balance verification
- goal: Add or improve verification that closes and reopens the disposable fixture after routed CREATE, then proves transaction presence, split count, split amounts, currency, memo, and expected balance deltas through read-only service paths.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; direct SQL mutation; committed fixture binaries; releases; broad compatibility claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, readback-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into disabled reset/probes when reopen and balance checks use disposable data only

## Task: issue50-reset-disabled-probes
- target: issue #50 / reset and disabled probes
- goal: Prove the drill resets writes disabled after the bounded session and that validate, preflight/readiness, CREATE, PATCH, DELETE, and batch route families are blocked or unavailable with defaults restored.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; weakening GNUCASH_WRITES_ENABLED=false defaults; removing safety guards; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, disabled-probes, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into failure drills after disabled probes prove write routes are blocked again

## Task: issue50-failure-drills
- target: issue #50 / failure drills
- goal: Cover invalid account rejection, stale preview or confirmation rejection, writes-disabled rejection, missing backup or recovery boundary rejection, lock/preflight failure if feasible, and safe rollback/recovery messaging without raw paths.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy book access; deleting safety guards; committed runtime artifacts; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, failure-drill, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into optional PATCH/DELETE if failure drills remain fail-closed

## Task: issue50-web-ui-test-mode-readiness
- target: issue #50 / web UI test-mode readiness
- goal: If the web route cannot yet drive the explicit test execution path, add a test-only or synthetic harness that can exercise the product CREATE workflow without activating default/user mode execution.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: default/user mode CREATE activation; owner/private/original/working/Syncthing/only-copy book access; screenshots; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into browser smoke when test-mode execution remains explicit and default UI stays disabled

## Task: issue50-browser-create-smoke
- target: issue #50 / synthetic browser CREATE smoke
- goal: Add or improve deterministic browser smoke for the explicit synthetic CREATE drill path, proving browser-to-app-to-API boundaries and no requests against non-disposable targets.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: screenshots; owner/private/original/working/Syncthing/only-copy book access; mutation requests against non-disposable targets; release work; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into optional PATCH/DELETE or docs if browser smoke proves the explicit test path safely

## Task: issue50-patch-metadata-only-drill
- target: issue #50 / optional metadata-only PATCH drill
- goal: If CREATE drill is already proven, add or improve PATCH coverage only for app-created disposable transactions and only for metadata text fields, while rejecting amount, account, split, date, and currency changes.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: PATCH on non-app-created transactions; balance-affecting PATCH; owner/private/original/working/Syncthing/only-copy book access; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, patch-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into DELETE only if PATCH remains metadata-only and app-owned

## Task: issue50-delete-app-owned-drill
- target: issue #50 / optional app-owned DELETE drill
- goal: If time remains, add or improve DELETE coverage only for app-owned synthetic/disposable transactions and prove non-owned DELETE is rejected.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: DELETE on historical/manual/non-owned transactions; owner/private/original/working/Syncthing/only-copy book access; direct SQL workarounds; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, disposable-fixture-only, delete-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into redacted docs and final gates if app-owned DELETE is bounded or explicitly deferred

## Task: issue50-redacted-docs-status
- target: issue #50 / redacted docs and status
- goal: Update PROJECT_STATUS, owner transaction-entry workflow docs, and the issue50 handoff with what actually passed, clearly separating untouched owner/private/working/Syncthing books from synthetic/disposable targets and default production-disabled posture.
- allowed scope: docs/handoff/issue50-disposable-copied-book-create-drill.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: raw transaction data; private paths; account names from non-synthetic sources; screenshots; books/backups/exports; releases; public write beta claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into final full gates if docs are redacted and status matches real checks

## Task: issue50-final-gates-and-issue-update
- target: issue #50 / final gates and issue update
- goal: Run the required final local checks, update the GitHub issue with a redacted result packet if gh is available, and leave the repository clean with committed safe scoped changes.
- allowed scope: docs/handoff/issue50-disposable-copied-book-create-drill.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md, apps/api/tests/**, apps/web/scripts/**
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
