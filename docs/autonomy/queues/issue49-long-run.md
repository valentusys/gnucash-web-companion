# Issue #49 web UI CREATE trial safe non-mutating long-run queue

This queue seeds a sustained repo-local autonomy run for issue #49 after the
write-session gate and target preflight/readiness shells. It is intentionally
product/code/test first. When these starter tasks are exhausted, use:

```bash
--on-empty generate-from-policy \
--backlog-policy docs/autonomy/backlog-policies/issue49-web-ui-create-trial-safe-nonmutating.md
```

The queue does not authorize financial-data mutation, target probing, releases,
or public write posture changes.

## Task: issue49-backup-readback-audit-reset-probes-shell
- target: issue #49 / web UI future execution readiness
- goal: Add a non-mutating backup/read-back/audit/reset/probes readiness UI and server shell for the future bounded web UI CREATE trial.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; target probing; opening GnuCash books; backup creation; audit execution; enabling writes; releases; public write beta claims; production/stable/security-audited claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue if the shell remains default-pending and Future Create remains disabled

## Task: issue49-armed-session-status-object
- target: issue #49 / read-only readiness status
- goal: Add a read-only status object or endpoint only if it is useful and remains fail-closed by default.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/routers/**, apps/api/tests/**, docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; write-service calls; target probing; opening GnuCash books; backup or lock helpers; enabling writes; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, preserve-write-defaults, fail-closed-status
- stop/continue recommendation: continue if default status exposes only redacted disabled readiness fields

## Task: issue49-browser-smoke-expansion
- target: issue #49 / deterministic synthetic browser smoke
- goal: Expand synthetic browser smoke coverage for the current readiness shells and disabled Future Create boundary.
- allowed scope: apps/web/scripts/test-transaction-entry-preview-browser.mjs, apps/web/scripts/test-transaction-entry-preview.mjs, apps/web/src/routes/transactions/new/**, docs/handoff/**
- non-goals: CREATE; PATCH; DELETE; batch; private fixtures; target probing; write service calls; release or publication work
- verification commands:
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, browser-smoke, synthetic-only, preserve-write-defaults
- stop/continue recommendation: continue if smoke remains synthetic-only and observes no mutation requests

## Task: issue49-static-backend-guard-hardening
- target: issue #49 / guard hardening
- goal: Strengthen static and backend guards that keep readiness shells from becoming active execution by accident.
- allowed scope: apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/tests/**, scripts/check_* safety guards, docs/handoff/**
- non-goals: CREATE; PATCH; DELETE; batch; write enablement; private target checks; release publication; broad readiness claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, guard-hardening, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue if guards fail closed on active write paths and pass locally

## Task: issue49-readonly-product-polish
- target: product UI / read-only companion usefulness
- goal: If issue #49 readiness shell work is saturated, make one small read-only product UX improvement tied to transaction-entry or navigation clarity.
- allowed scope: apps/web/src/routes/**, apps/web/src/lib/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; write enablement; target probing; large refactors; release publication; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, product-code, read-only-ux, preserve-write-defaults
- stop/continue recommendation: continue if the change is small, read-only, and product-relevant

## Task: issue49-final-gates-redacted-status
- target: issue #49 / final redacted status packet
- goal: Run full local gates and update only concise redacted status docs when tied to completed code or test slices.
- allowed scope: docs/handoff/**, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: CREATE; PATCH; DELETE; batch; target probing; private data; release publication; public write beta claims; issue closure without explicit owner approval
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
- safety flags: no-private-data, no-release, final-gates, preserve-write-defaults, no-dogfood
- stop/continue recommendation: continue only if minimum runtime still requires safe generated policy tasks
