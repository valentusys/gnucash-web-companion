# Issue #51 disposable UI execution rehearsal backlog policy

This policy is for `scripts/autonomy/supervisor.py --on-empty generate-from-policy`
when the issue #51 starter queue exhausts before the configured wall-clock or
task minimums.

Policy invariants:

- Preserve `GNUCASH_WRITES_ENABLED=false` in defaults and rendered Compose.
- Preserve enabled-write `APP_ENV=test` gates.
- Use only synthetic/disposable SQLite fixtures created by tests or ignored
  runtime paths outside the repository.
- Any CREATE/PATCH/DELETE in this policy is limited to disposable fixture
  targets with redacted evidence only.
- Normal/default `/transactions/new` remains preview-only; explicit execution is
  test-mode only.
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

## Task: issue51-ui-harness-followup
- target: issue #51 / UI rehearsal harness follow-up
- goal: Improve the browser/manual-like transaction-entry harness so it proves preview, reviewed approval evidence, and explicit test-mode execution against synthetic or disposable copied-like fixtures only.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/web/package.json, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: owner/private/original/working/Syncthing/only-copy targets; screenshots; default CREATE activation; release work; public write posture claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if the explicit execution path remains test-mode and disposable-only

## Task: issue51-result-ui-followup
- target: issue #51 / result UI follow-up
- goal: Improve redacted success/result and failure result panels for the explicit disposable CREATE rehearsal, including create_count, read-back, backup/audit, reset/default-disabled probes, and no raw book evidence.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: raw paths; screenshots; default CREATE activation; release work; public write posture claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if result UI remains redacted and default mode stays preview-only

## Task: issue51-browser-smoke-followup
- target: issue #51 / browser smoke follow-up
- goal: Expand deterministic browser smoke or add a dedicated disposable CREATE browser command to prove the UI-to-route rehearsal, no normal-mode execution, and no non-disposable target requests.
- allowed scope: apps/web/scripts/test-transaction-entry-preview*.mjs, apps/web/scripts/**, apps/web/package.json, apps/web/src/routes/transactions/new/**, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: screenshots; default CREATE activation; owner/private/original/working/Syncthing/only-copy targets; release work; public write posture claims
- verification commands:
  - cd apps/web && npm run check
  - cd apps/web && npm run build
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, browser-smoke, create-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if browser smoke remains synthetic/disposable-only

## Task: issue51-failure-ui-followup
- target: issue #51 / failure UI follow-up
- goal: Add or improve stale-preview, target-preflight, writes-disabled, backup, lock, read-back, reset/probe failure coverage with redacted UI-visible or API-result-shaped evidence.
- allowed scope: apps/web/src/routes/transactions/new/**, apps/web/scripts/test-transaction-entry-preview*.mjs, apps/api/app/**, apps/api/tests/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: raw paths; weakening guards; committed runtime artifacts; owner/private/original/working/Syncthing/only-copy targets; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, failure-drill, browser-smoke, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if failure evidence is redacted and fail-closed

## Task: issue51-guard-hardening-followup
- target: issue #51 / execution gate hardening follow-up
- goal: Improve backend/frontend guard coverage so explicit execution requires test-mode synthetic/disposable proof, rejects header/query smuggling, and leaves default route families blocked or unavailable.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, scripts/check_*.py, docs/handoff/**, PROJECT_STATUS.md
- non-goals: safety guard removal; default write enablement; owner/private/original/working/Syncthing/only-copy targets; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run check
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, disabled-probes, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if gates remain fail-closed and defaults are restored

## Task: issue51-patch-delete-ui-followup
- target: issue #51 / optional PATCH DELETE UI follow-up
- goal: If CREATE rehearsal coverage is saturated, improve metadata-only PATCH coverage for app-created disposable transactions or bounded app-owned DELETE coverage with non-owned rejection.
- allowed scope: apps/api/app/**, apps/api/tests/**, apps/web/src/routes/transactions/new/**, apps/web/scripts/**, docs/handoff/**, PROJECT_STATUS.md
- non-goals: non-owned PATCH/DELETE; balance-affecting PATCH; owner/private/original/working/Syncthing/only-copy targets; releases
- verification commands:
  - cd apps/api && pytest -q
  - cd apps/web && npm run test:transaction-entry-preview
  - cd apps/web && npm run test:transaction-entry-preview-browser
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, product-code, disposable-fixture-only, patch-test, delete-test, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if optional operations remain app-owned, bounded, and disposable-only

## Task: issue51-docs-status-followup
- target: issue #51 / docs status follow-up
- goal: Update redacted issue51 handoff, write-alpha workflow docs, or project status with real checks and safety counters from completed disposable UI rehearsal work.
- allowed scope: docs/handoff/issue51-disposable-ui-execution-rehearsal.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md
- non-goals: raw transaction data; private paths; committed books/backups/exports/screenshots; releases; public write posture claims
- verification commands:
  - python3 scripts/check_public_status.py
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, final-gates, disposable-fixture-only, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if docs are redacted and tied to commands that actually ran

## Task: issue51-final-gates-followup
- target: issue #51 / final gate follow-up
- goal: Run required final checks, run a new disposable-browser command if it exists, record real command outcomes in redacted docs or issue comments, and leave the repository clean with committed safe scoped changes.
- allowed scope: docs/handoff/issue51-disposable-ui-execution-rehearsal.md, docs/write-alpha/owner-transaction-entry-workflow.md, PROJECT_STATUS.md, apps/api/tests/**, apps/web/scripts/**, apps/web/package.json
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
