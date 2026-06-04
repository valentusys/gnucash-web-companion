# Daytime write-mode autonomy queue

This sample queue is for local supervisor dry-runs and, after maintainer review,
live bounded worker launches. It does not authorize touching private/original
GnuCash books, publishing releases, or broad write-beta claims.

## Task: issue36-docs-reconcile
- target: issue #36 / controlled write-mode docs
- goal: Reconcile controlled write-mode operator docs with current GitHub issue state and keep owner-writebeta wording conservative.
- allowed scope: docs/write-alpha*, docs/handoff tracked summaries, PROJECT_STATUS.md if needed
- non-goals: product code; frontend code; backend route changes; dogfood; GnuCash mutations; releases; tags; packages; images; public write beta claims; production/stable/security-audited claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if docs-only changes pass quick-docs gates and git status is clean

## Task: autonomy-runbook-polish
- target: autonomy/operator runbook
- goal: Improve the local autonomous supervisor runbook examples and recovery guidance based on dry-run output.
- allowed scope: docs/autonomy/** only
- non-goals: product code; GnuCash book operations; GitHub issue mutation; releases; tags; packages; images
- verification commands:
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, docs-only
- stop/continue recommendation: continue if markdown and hygiene gates pass

## Task: final-safe-gate-review
- target: repository safety gates
- goal: Run and summarize the final safe gate set without broadening write posture or making release claims.
- allowed scope: final report/handoff documentation only
- non-goals: code changes; dogfood; real/private book inspection; release publication; issue closure unless explicitly authorized by prompt
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run build
  - JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, final-gates
- stop/continue recommendation: stop after final gate summary
