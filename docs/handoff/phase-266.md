# Phase 266 — Public docs drift guard update for v0.2.8 owner dry-run posture

Date: 2026-05-22

## Goal

Prevent README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP from drifting after the owner dry-run preparation work.

## Scope

- Updated the public status guard current baseline from the previous post-release baseline to Phase 266.
- Updated README, README.ru, PROJECT_STATUS, CHANGELOG, and docs/ROADMAP to agree on the current completed phase.
- Added a concise public note that the owner copied-book path remains dry-run only.
- Added stale-current pattern coverage for the now-obsolete Phase 261–265 public baseline strings.

## Non-goals

- No product code changes.
- No release, tag, package, or publication.
- No mutation, CREATE, PATCH, or DELETE execution.
- No write-gate relaxation.
- No owner/private/original/only-copy book use.

## Acceptance criteria

- Public status guard passes.
- README and README.ru are not misleading about the current release state.
- PROJECT_STATUS current baseline is updated.
- The owner-facing next step remains copied-book dry-run only, not CREATE-one.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default write posture.
- The `APP_ENV=test` write-alpha gate remains documented and unchanged.
- No production/security/public-internet/broad-compatibility claim was added.
- No real/private/original/only-copy write-safety claim was added.
- No private financial data, raw paths, account names, memos, amounts, secrets, tokens, backups, app DBs, screenshots, or CSV exports were added.

## Verification

- `pytest -q apps/api/tests/test_public_status_guard.py`
  - Result: `27 passed`.
- `python scripts/check_public_status.py`
  - Result: `public-status-guard: ok`.
- `git diff --check`
  - Result: pass.

## Expected artifacts

- Updated `scripts/check_public_status.py`
- Updated `apps/api/tests/test_public_status_guard.py`
- Updated `README.md`
- Updated `README.ru.md`
- Updated `docs/ROADMAP.md`
- Updated `PROJECT_STATUS.md`
- Updated `CHANGELOG.md`
- `docs/handoff/phase-266.md`

## PM invocation

PM was not invoked. Phase 266 is public-status/documentation guard maintenance with no release/no-release decision, owner-risk authorization, write-mode relaxation, publication, security exception, private-data risk, or conflicting owner choice.

## Result

Phase 266 is complete. The next roadmap phase is Phase 267 — synthetic full owner-dry-run rehearsal from a fresh clone.
