# Issue #49 web UI CREATE trial safe non-mutating backlog policy

This policy is for `scripts/autonomy/supervisor.py --on-empty generate-from-policy`
when a sustained run under issue #49 exhausts the starter queue before the wall-clock budget.
It generates only safe product/code/test/docs tasks for the web UI CREATE execution-trial preparation phase.

Policy invariants:

- Preserve `GNUCASH_WRITES_ENABLED=false` in defaults and rendered Compose.
- Preserve enabled-write `APP_ENV=test` gates.
- Keep GnuCash Desktop as the authoritative editor.
- Keep `/transactions/new` preview-first and no-write by default.
- Future Create controls must remain disabled and inert unless a future owner-approved session is implemented separately.
- Runtime prompts and reports stay under ignored `.hermes/autonomy/`.
- Generated workers must treat each task's allowed scope as a ceiling.
- Repeated generated tasks may be no-ops when no safe scoped improvement remains.
- Repeated tasks must not create cosmetic edits solely to avoid a no-op.
- A no-op worker should report exact gates run, clean/dirty status, and mutation
  counters (`CREATE 0 / PATCH 0 / DELETE 0 / batch 0`).
- Do not use tracked docs or issue comments to publish raw private evidence.

## Task: issue49-backup-readback-audit-reset-probes-shell
- target: issue #49 / future execution readiness shell
- goal: Add or improve non-mutating backup, read-back, audit, reset, and disabled-probe readiness shell behavior for the future web UI CREATE trial.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; target probing; opening GnuCash books; creating backups; running audit; enabling writes; dogfood; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue if the UI remains default-pending and disabled

## Task: issue49-readonly-status-readiness-object
- target: issue #49 / redacted readiness status
- goal: Add or improve redacted read-only readiness state for writes-enabled, session-armed, count, target, preflight, backup, and allowed-execution status.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/routers/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; write-service calls; private target probing; opening GnuCash books; backup, lock, or audit helper calls; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, preserve-write-defaults, fail-closed-status
- stop/continue recommendation: continue if default state is redacted, disabled, and fail-closed

## Task: issue49-preview-boundary-guard-hardening
- target: issue #49 / preview and readiness boundary guards
- goal: Strengthen tests or static guards that prove create-preview remains the only transaction-entry submission target and Future Create stays disabled.
- allowed scope: apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/tests/**, scripts/check_* safety guards, docs/handoff/**
- non-goals: CREATE; PATCH; DELETE; batch; target probing; write enablement; dogfood; release publication; broad safety claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, guard-hardening, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue if guards stay conservative and passing

## Task: issue49-synthetic-browser-smoke-expansion
- target: issue #49 / synthetic browser smoke
- goal: Expand deterministic browser smoke around readiness panels, approval packet state, disabled Future Create, and mutation-request blocking.
- allowed scope: apps/web/scripts/test-transaction-entry-preview-browser.mjs, apps/web/scripts/test-transaction-entry-preview.mjs, apps/web/src/routes/transactions/new/**, docs/handoff/**
- non-goals: CREATE; PATCH; DELETE; batch; private fixtures; target probing; write service calls; releases
- verification commands:
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, browser-smoke, synthetic-only, preserve-write-defaults
- stop/continue recommendation: continue if smoke remains synthetic-only and observes no mutation requests

## Task: issue49-small-readonly-product-polish
- target: read-only product UI / transaction-entry clarity
- goal: Make one small browser/mobile read-only UX improvement tied to transaction-entry, navigation, empty states, or error clarity.
- allowed scope: apps/web/src/routes/**, apps/web/src/lib/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; write enablement; target probing; large refactors; dogfood; release publication; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, read-only-ux, preserve-write-defaults
- stop/continue recommendation: continue if the change is small and read-only

## Task: issue49-autonomy-workflow-improvement
- target: autonomy workflow / issue #49 safe long runs
- goal: Improve queue, policy, or runbook clarity that makes future safe issue #49 long runs easier without replacing product work.
- allowed scope: docs/autonomy/**, scripts/autonomy/**, apps/api/tests/test_autonomy_supervisor.py, docs/handoff/**
- non-goals: CREATE; PATCH; DELETE; batch; live target probing; release publication; public write beta claims; changing tool safety defaults
- verification commands:
  - cd apps/api && pytest tests/test_autonomy_supervisor.py -q
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, autonomy-docs, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue if product/code/test slices have already made progress

## Task: issue49-final-redacted-gate-report
- target: issue #49 / final redacted gate report
- goal: Produce or update concise redacted status documentation tied to completed code or test slices and real command output.
- allowed scope: docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; target probing; private data; dogfood; release publication; issue closure without explicit owner approval
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, final-gates, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue only if the runtime budget still has safe work
