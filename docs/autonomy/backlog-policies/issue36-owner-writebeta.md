# Issue #36 owner-writebeta backlog policy

This policy is for `scripts/autonomy/supervisor.py --on-empty generate-from-policy` when the finite queue is exhausted before the requested minimum runtime or task count.

The policy only authorizes safe local tasks related to issue #36 owner-writebeta readiness. It does not authorize write-mode dogfood, GnuCash mutations, real/private/original/working/only-copy book access, release publication, public write beta claims, or production/stable/security-audited claims.

Policy invariants:

- Preserve `GNUCASH_WRITES_ENABLED=false` in defaults and rendered Compose.
- Preserve `APP_ENV=test` gates for enabled writes.
- No GnuCash mutations by default.
- No real/private/original/working/only-copy books.
- No release, tag, package, or image publication.
- No public write beta.
- No stable, production-ready, security-audited, broad compatibility, or only-copy safety claim.
- Runtime prompts/reports stay under ignored `.hermes/autonomy/` unless a tracked handoff is explicitly requested.

## Task: owner-writebeta-remaining-gates-audit
- target: issue #36 / owner-writebeta remaining gates audit
- goal: Audit the tracked docs, guards, and issue-facing readiness notes for remaining owner-writebeta gates, then document only conservative non-mutating findings or safe code/test improvements.
- allowed scope: docs/**, scripts/check_* safety guards, apps/api tests for safety-only guard behavior
- non-goals: GnuCash mutations; dogfood; private/original/working/only-copy books; releases; tags; packages; images; public write beta claims; production/stable/security-audited claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if changes are docs/guard/test-only, gates pass, and git status is clean

## Task: release-no-release-decision-docs
- target: issue #36 / release and no-release decision documentation
- goal: Improve documentation that explains why owner-writebeta readiness remains unreleased until owner approval, without changing release state or making public write-beta claims.
- allowed scope: docs/**, PROJECT_STATUS.md, docs/handoff/**
- non-goals: release publication; tag creation; package/image publication; public write beta claims; production/stable/security-audited claims; GnuCash mutations; dogfood
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, docs-only, preserve-write-defaults
- stop/continue recommendation: continue if docs remain conservative and no release artifacts are created

## Task: real-working-book-trial-blocker-runbook
- target: issue #36 / real-working-book trial blocker and runbook
- goal: Document prerequisites, blockers, rollback expectations, and owner approval gates for a future real-working-book trial without authorizing or running that trial.
- allowed scope: docs/**, docs/handoff/**
- non-goals: opening, copying, inspecting, or mutating real/private/original/working/only-copy books; dogfood; write enablement; release publication
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, docs-only, no-dogfood, app-env-test-gated-writes
- stop/continue recommendation: continue if the runbook explicitly says the trial is not authorized

## Task: backup-restore-readiness-docs-tests
- target: issue #36 / backup and restore readiness
- goal: Improve non-mutating backup/restore readiness docs or tests that validate wording and default-disabled safety without touching private data.
- allowed scope: docs/**, scripts/check_* guards, apps/api tests for non-mutating backup/restore documentation or guard behavior
- non-goals: creating backups from private books; restore into real books; dogfood; release publication; public write beta claims
- verification commands:
  - cd apps/api && pytest tests/test_autonomy_supervisor.py -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if changes are non-mutating docs/tests only

## Task: default-disabled-write-safety-guard-improvements
- target: issue #36 / default-disabled and write-safety guards
- goal: Strengthen guard tests or scripts that prove writes remain disabled by default and enabled writes remain `APP_ENV=test` gated.
- allowed scope: scripts/check_write_safety_defaults.py, apps/api tests, docs explaining the guard
- non-goals: enabling writes by default; dogfood; GnuCash mutations; private/original/working/only-copy books; release publication
- verification commands:
  - python3 scripts/check_write_safety_defaults.py
  - cd apps/api && pytest -q
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if guards still prove default-disabled write posture

## Task: audit-privacy-wording-guards
- target: issue #36 / audit and privacy wording guards
- goal: Improve checks or documentation that prevent private evidence, private paths, broad compatibility claims, or unsafe write-beta wording from entering tracked files.
- allowed scope: scripts/check_public_status.py, scripts/check_tracked_hygiene.py, docs/**, apps/api tests for guard behavior
- non-goals: private data inspection; screenshots; GnuCash exports; dogfood; releases; public write beta claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_tracked_hygiene.py
  - python3 scripts/check_markdown_readability.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, privacy-guard, conservative-wording
- stop/continue recommendation: continue if guards remain conservative and no private evidence is added

## Task: final-full-gate-report
- target: issue #36 / final full gate report
- goal: Produce or update a concise final gate report that records real command output and explicitly says no mutation, dogfood, release publication, or public write beta was performed.
- allowed scope: docs/handoff/** only
- non-goals: code changes; GnuCash mutations; private/original/working/only-copy books; releases; tags; packages; images; issue closure without owner authorization
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
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, final-gates, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: stop or continue only if minimum runtime/task settings still require another safe policy task

## Task: discovered-safe-quality-fixes-related-to-issue36
- target: issue #36 / discovered safe test-doc-code quality fixes
- goal: Address discovered safe docs, tests, or guard quality issues directly related to issue #36 while preserving all write and privacy safety boundaries.
- allowed scope: docs/**, scripts/check_* guards, apps/api tests, scripts/autonomy/** if the issue relates to autonomous readiness
- non-goals: unrelated refactors; GnuCash mutations; dogfood; private/original/working/only-copy books; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest tests/test_autonomy_supervisor.py -q
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, no-dogfood, issue36-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only for safe, bounded, issue #36 related fixes with clean git and passing gates
