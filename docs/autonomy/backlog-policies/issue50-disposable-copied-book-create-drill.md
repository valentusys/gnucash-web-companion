# Issue #50 disposable copied-book CREATE drill backlog policy

This policy is for `scripts/autonomy/supervisor.py --on-empty generate-from-policy`
when the issue #50 starter queue exhausts before the configured wall-clock or
task minimums.

Policy invariants:

- Preserve `GNUCASH_WRITES_ENABLED=false` in defaults and rendered Compose.
- Preserve enabled-write `APP_ENV=test` gates.
- Use only synthetic/disposable SQLite fixtures created by tests or ignored
  runtime paths outside the repository.
- Any routed CREATE/PATCH/DELETE in this policy is limited to disposable fixture
  targets with redacted evidence only.
- Do not commit fixture binaries, app DBs, backups, screenshots, exports, raw
  transaction dumps, secrets, tokens, or local data files.
- Do not use owner financial files, Syncthing files, or sole-copy targets.
- Do not publish releases, tags, packages, or images.
- Do not claim public write beta, production, stable, security-audited, or broad
  compatibility status.
- Runtime prompts and reports stay under ignored `.hermes/autonomy/` unless a
  tracked handoff is explicitly requested.
- Generated workers must treat each task's allowed scope as a ceiling.
- Repeated tasks may end as honest no-op checkpoints when no safe scoped
  improvement remains.

## Task: issue50-disposable-harness-followup
- target: issue #50 / disposable harness follow-up
- goal: Improve temp fixture creation, outside-repo proof, disposable-target guardrails, or copied-like setup helpers for the routed CREATE drill.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; fixture binaries; screenshots; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if disposable target proofs fail closed and no runtime artifact is tracked

## Task: issue50-create-route-followup
- target: issue #50 / routed CREATE follow-up
- goal: Expand routed CREATE test coverage for backup-before-write, lock acquisition, audit start/success rows, read-back, Decimal string preservation, date, currency, description, memo, two splits, and redacted response evidence.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; direct SQL writes; fixture binaries; raw evidence; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if routed CREATE remains bounded to disposable fixture data

## Task: issue50-reopen-balance-followup
- target: issue #50 / reopen balance follow-up
- goal: Improve reopen and read-only verification after the disposable CREATE drill, including transaction presence, split balance, account balance deltas, and currency consistency.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; committed runtime data; releases; broad compatibility claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, readback-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if read-back and balance checks use disposable data only

## Task: issue50-disabled-probes-followup
- target: issue #50 / disabled probes follow-up
- goal: Strengthen reset-disabled checks and post-reset blocked/unavailable probes for validate, preflight/readiness, CREATE, PATCH, DELETE, and batch route families.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; write default changes; safety guard deletion; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, disabled-probes, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if defaults are restored and all relevant route families are blocked or unavailable

## Task: issue50-failure-boundary-followup
- target: issue #50 / failure boundary follow-up
- goal: Add or improve invalid-account, stale-preview, writes-disabled, missing-backup/recovery, lock/preflight-failure, and safe rollback-message coverage for disposable fixture drills.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; weakening guards; committed runtime artifacts; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, failure-drill, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if failures are explicit, redacted, and fail closed

## Task: issue50-web-harness-followup
- target: issue #50 / web harness follow-up
- goal: Improve explicit test-mode web harness coverage for the transaction-entry CREATE workflow while default/user mode remains disabled and inert.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: default/user mode execution; owner/private/original/working/Syncthing/only-copy targets; screenshots; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if browser/UI execution remains explicit test-mode only

## Task: issue50-patch-delete-followup
- target: issue #50 / optional PATCH DELETE follow-up
- goal: If CREATE coverage is saturated, improve metadata-only PATCH coverage for app-created disposable transactions or bounded app-owned DELETE coverage with non-owned rejection.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: non-owned PATCH/DELETE; balance-affecting PATCH; owner/private/original/working/Syncthing/only-copy targets; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, patch-test, delete-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if optional operations remain app-owned, bounded, and disposable-only

## Task: issue50-docs-status-followup
- target: issue #50 / docs status follow-up
- goal: Update redacted issue50 handoff, write-alpha workflow docs, or project status with real checks and safety counters from completed disposable fixture drills.
- allowed scope: docs/handoff/issue50-disposable-copied-book-create-drill.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: raw transaction data; private paths; committed books/backups/exports/screenshots; releases; public write posture claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if docs are redacted and tied to commands that actually ran

## Task: issue50-final-gates-followup
- target: issue #50 / final gate follow-up
- goal: Run required final checks, record real command outcomes in redacted docs, and leave the repository clean with committed safe scoped changes.
- allowed scope: docs/handoff/issue50-disposable-copied-book-create-drill.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md, apps/api/tests/**, apps/web/scripts/**
- non-goals: raw evidence; fixture binaries; screenshots; releases; public write posture claims; owner/private/original/working/Syncthing/only-copy targets
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
- safety flags: generated-safe, no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only if the requested runtime still has safe scoped work
