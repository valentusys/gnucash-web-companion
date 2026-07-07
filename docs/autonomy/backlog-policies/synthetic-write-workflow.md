# Synthetic write workflow backlog policy

This policy is for `scripts/autonomy/supervisor.py --on-empty generate-from-policy`
when the synthetic write workflow queue exhausts starter tasks before the
configured wall-clock or task minimums.

Policy invariants:

- Preserve `GNUCASH_WRITES_ENABLED=false` in defaults and rendered Compose.
- Preserve enabled-write `APP_ENV=test` gates.
- Use only disposable synthetic SQLite fixtures created by tests or ignored
  runtime paths.
- Do not commit fixture binaries, app DBs, backups, screenshots, exports, raw
  transaction dumps, secrets, tokens, or local data files.
- Do not use owner financial files, Syncthing files, or a sole working copy.
- Do not publish releases, tags, packages, or images.
- Do not claim public write beta, production, stable, security-audited, or broad
  compatibility status.
- Runtime prompts and reports stay under ignored `.hermes/autonomy/` unless a
  tracked handoff is explicitly requested.
- Generated workers must treat each task's allowed scope as a ceiling.
- Repeated tasks may end as honest no-op checkpoints when no safe scoped
  improvement remains.

## Task: synthetic-fixture-generator-followup
- target: synthetic write workflow / fixture generator
- goal: Improve deterministic fixture generation, account lookup helpers, or balance assertions for synthetic tests.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; fixture binaries; screenshots; releases; broad compatibility claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if fixture behavior is deterministic and no data artifact is tracked

## Task: synthetic-validation-followup
- target: synthetic write workflow / validation
- goal: Improve validation tests for balanced splits, Decimal string handling, placeholder rejection, account existence, and currency consistency.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; direct SQL writes; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if invalid synthetic requests fail before execution

## Task: synthetic-armed-boundary-followup
- target: synthetic write workflow / armed boundary
- goal: Improve tests or implementation around the preview to armed-execution boundary without changing default-disabled behavior.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; enabling production writes; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if execution remains disabled by default and test-gated when enabled

## Task: synthetic-create-followup
- target: synthetic write workflow / CREATE coverage
- goal: Expand CREATE transaction tests for source, destination, amount, currency, date, description, memo, splits, reopening, and balance verification.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; fixture binaries; screenshots; releases; broad safety claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if read-back and balance checks are exercised on disposable data

## Task: synthetic-patch-followup
- target: synthetic write workflow / PATCH coverage
- goal: Expand PATCH tests for permitted text metadata edits and forbidden financial-field changes.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; amount/account/split/currency/date edits; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, patch-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if forbidden field changes fail with regression coverage

## Task: synthetic-delete-followup
- target: synthetic write workflow / DELETE boundary
- goal: Add safe synthetic delete coverage only if supported, or improve the tracked design proposal for a later safe implementation.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/write-alpha/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; non-synthetic delete paths; direct SQL workarounds; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, delete-boundary, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if delete is either safely tested on disposable data or explicitly deferred

## Task: synthetic-reopen-recovery-followup
- target: synthetic write workflow / recovery checks
- goal: Improve reopen, rollback, recovery, corrupted-fixture, lock, or concurrency tests for disposable synthetic data.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; committing generated data; releases; broad compatibility claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, recovery-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if recovery behavior is tested without tracked runtime artifacts

## Task: synthetic-browser-workflow-followup
- target: synthetic write workflow / browser UX
- goal: Improve preview, confirmation, execution result, success, failure, rollback, or disabled-default UX for the synthetic write flow.
- allowed scope: apps/web/src/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; enabling production writes; screenshots; releases; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:auth-routes
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if browser checks prove default execution remains disabled

## Task: transaction-history-followup
- target: synthetic write workflow / transaction history UI
- goal: If write workflow coverage is saturated, improve transaction history clarity around newly created synthetic transactions without using owner data.
- allowed scope: apps/web/src/**, apps/web/scripts/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; fixture binaries; screenshots; releases; broad write support claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:auth-routes
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, synthetic-fixture-only, preserve-write-defaults
- stop/continue recommendation: continue if the change is product-relevant and synthetic-data-only

## Task: import-export-followup
- target: synthetic write workflow / import-export polish
- goal: If higher-priority write work is saturated, improve synthetic import/export tests or UI around redacted disposable data only.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; raw exports; CSV bodies in tracked docs; releases; broad compatibility claims
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, product-code, preserve-write-defaults
- stop/continue recommendation: continue if no raw export or runtime artifact is tracked

## Task: synthetic-performance-followup
- target: synthetic write workflow / performance checks
- goal: Add or improve bounded synthetic performance checks for write-preview, validation, or read-back paths without production claims.
- allowed scope: apps/api/app/**, apps/api/tests/**, scripts/**, docs/performance/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; production performance claims; release publication; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_public_status.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, performance-test, preserve-write-defaults
- stop/continue recommendation: continue if any measurements are labeled local synthetic only

## Task: compatibility-followup
- target: synthetic write workflow / compatibility checks
- goal: Improve compatibility notes or tests for disposable SQLite fixtures without claiming broad GnuCash version or backend support.
- allowed scope: apps/api/app/**, apps/api/tests/**, docs/gnucash-compatibility.md, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; PostgreSQL/MySQL/MariaDB support claims; releases; public write posture claims
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, synthetic-fixture-only, compatibility-docs, preserve-write-defaults
- stop/continue recommendation: continue if wording remains narrow to disposable SQLite fixtures

## Task: mobile-ux-followup
- target: synthetic write workflow / mobile UX
- goal: Improve mobile-first usability for the preview and confirmation path while keeping execution disabled outside synthetic test mode.
- allowed scope: apps/web/src/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; enabling production writes; screenshots; releases; public write beta claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, mobile-ux, preserve-write-defaults
- stop/continue recommendation: continue if mobile changes preserve disabled-default execution

## Task: final-gate-followup
- target: synthetic write workflow / final gates
- goal: Run required final checks and update concise redacted handoff/status docs with real command outcomes.
- allowed scope: docs/handoff/**, docs/write-alpha/**, PROJECT_STATUS.md
- non-goals: owner financial files; Syncthing files; raw transactions; fixture binaries; screenshots; releases; public write beta claims
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
- safety flags: generated-safe, no-private-data, no-release, final-gates, synthetic-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue only if the runtime budget still requires more safe scoped work
