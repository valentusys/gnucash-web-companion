# Issue #36 long-run autonomy queue

This queue is a seed for sustained supervisor v2 runs. It intentionally contains a small finite set of safe starter tasks, then relies on:

```bash
--on-empty generate-from-policy \
--backlog-policy docs/autonomy/backlog-policies/issue36-owner-writebeta.md
```

to keep a 5-hour session busy only while safe issue #36 owner-writebeta readiness tasks remain.

It does not authorize GnuCash mutations, dogfood, real/private/original/working/only-copy books, releases, tags, packages, images, public write beta, or stable/production/security-audited claims.

## Task: issue36-current-state-reconcile
- target: issue #36 / current readiness state
- goal: Reconcile tracked issue #36 readiness docs with current safe guard state, keeping all owner-writebeta wording conservative.
- allowed scope: docs/**, PROJECT_STATUS.md, docs/handoff/**
- non-goals: product dogfood; GnuCash mutations; private/original/working/only-copy books; release publication; public write beta claims; production/stable/security-audited claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, docs-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if docs remain conservative and gates pass

## Task: autonomy-v2-generated-policy-preview
- target: autonomy supervisor v2 / issue #36 policy preview
- goal: Review generated policy prompts and improve only safe policy/runbook wording if the dry-run reveals ambiguity.
- allowed scope: docs/autonomy/**, scripts/autonomy/** tests/docs only
- non-goals: live agent execution; GnuCash mutations; dogfood; private/original/working/only-copy books; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest tests/test_autonomy_supervisor.py -q
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, autonomy-docs, preserve-write-defaults
- stop/continue recommendation: continue into generated policy tasks if git status is clean

## Task: issue36-final-safe-gate-report-seed
- target: issue #36 / safe final gate report seed
- goal: Prepare the final full-gate reporting shape without claiming release readiness or performing dogfood.
- allowed scope: docs/handoff/** only
- non-goals: code changes unless required by failing guard tests; GnuCash mutations; private/original/working/only-copy books; releases; public write beta claims; issue closure without owner approval
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run build
  - JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, final-gates, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only through safe generated policy tasks if minimum runtime/task settings require it
