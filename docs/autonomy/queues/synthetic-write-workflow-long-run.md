# Synthetic write workflow autonomy queue

This queue seeds a sustained repo-local autonomy run for the synthetic GnuCash
write workflow phase. It is product/code/test first and authorizes write
operations only against disposable synthetic SQLite fixtures created by the test
suite or local ignored runtime paths.

Use with:

```bash
--on-empty generate-from-policy \
--backlog-policy docs/autonomy/backlog-policies/synthetic-write-workflow.md
```

The queue does not authorize owner financial files, Syncthing files, releases,
public write posture changes, or committing fixture binaries.

## Task: synthetic-fixture-framework
- target: synthetic write workflow / fixture framework
- goal: Build or extend an automatic synthetic SQLite fixture generator with a predictable account tree and balances for repeatable backend tests.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; committing SQLite/books/backups/screenshots/exports; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into write architecture after fixture generation and tests are green

## Task: write-architecture-boundary
- target: synthetic write workflow / backend architecture
- goal: Implement or tighten the preview, validation, armed execution boundary, write operation, and read-back verification path while keeping defaults disabled.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/write-alpha/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; direct SQL writes; broad write support claims; releases; changing default GNUCASH_WRITES_ENABLED=false
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into CREATE tests if the boundary is default-disabled and test-gated

## Task: synthetic-create-tests
- target: synthetic write workflow / CREATE transaction
- goal: Add end-to-end tests for creating a balanced transaction in a disposable synthetic book, then reopening the book and checking balances.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; committing generated books; screenshots; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, synthetic-fixture-only, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into PATCH tests after CREATE read-back and balance checks pass

## Task: synthetic-patch-tests
- target: synthetic write workflow / PATCH transaction
- goal: Add regression tests that permit synthetic description and memo edits while rejecting amount, account, split, currency, and date changes.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; changing immutable financial fields; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, synthetic-fixture-only, patch-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into delete design or safe synthetic delete tests

## Task: synthetic-delete-boundary
- target: synthetic write workflow / DELETE transaction
- goal: If the architecture already supports deletion safely, test deletion of synthetic transactions only; otherwise create a design proposal without unsafe workarounds.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/write-alpha/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; deleting non-synthetic records; direct SQL workarounds; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, synthetic-fixture-only, delete-boundary, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into browser workflow after safe delete boundary is proven or documented as deferred

## Task: browser-write-workflow-ux
- target: synthetic write workflow / browser product flow
- goal: Develop the real preview, confirmation, execution-result, success, failure, rollback, and error-handling UX while production/default execution remains disabled.
- allowed scope: apps/web/src/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; enabling production writes; committing screenshots; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue into history or import/export improvements if the write workflow is already covered

## Task: final-synthetic-write-gates
- target: synthetic write workflow / final gate report
- goal: Run required final checks and update only concise redacted status docs tied to completed code and test slices.
- allowed scope: docs/handoff/**, docs/write-alpha/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; raw transactions; fixture binaries; screenshots; releases; public write beta claims; production/stable/security-audited claims
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
- safety flags: no-private-data, no-release, final-gates, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only if the runtime budget still has safe generated policy work
