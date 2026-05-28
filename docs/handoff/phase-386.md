# Phase 386 handoff

- goal: synchronize public status on main to the Phase 380 baseline after PR #40 merge.
- scope: README, README.ru, CHANGELOG, PROJECT_STATUS, docs/ROADMAP, and public status guard.
- non-goals: no new write evidence, no mutation, no release.
- acceptance criteria: public docs agree that Phase 380 is completed/merged and current public releases remain `v0.1.7-readonly` and `v0.2.8-writealpha` unless a later release is actually published.
- safety checks: no overclaim; copied-book evidence is described as narrow/experimental; no production/original/private/only-copy safety claim; `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` gate preserved.
- verification:
  - `python3 scripts/check_public_status.py`: passed after guard baseline update to Phase 380.
  - `git diff --check`: passed.
  - Public docs now state Phase 0-380 / completed through Phase 380 and retain current release `v0.2.8-writealpha`.
- expected artifacts: synchronized public docs, updated public status guard, this handoff.
- final verdict: CONTINUE.
