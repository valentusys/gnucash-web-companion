# Phase 484 — PM product track selection

Goal: PM chooses the product track for this run.

Scope: Repository docs, release evidence, GitHub state, and safe verification only.

Non-goals: No private data, no original GnuCash book access, no stable/production release, and no public write-safety claim.

Acceptance criteria: The phase decision/evidence is recorded with safety boundaries intact.

Safety checks: GNUCASH_WRITES_ENABLED=false remains default; APP_ENV=test write gate is not weakened; no private books, app DBs, exports, secrets, raw paths, account names, descriptions, memos, or amounts are committed.

Verification: Git/GitHub state reviewed; public status guard and release/doc posture checked where relevant.

Expected artifacts: This handoff plus the referenced audit/release/strategy/dogfood document.

Findings:
PM decision: TRACK_C_DUAL_TRACK_WITH_RELEASE_DECISION_AT_PHASE_530.

Rationale:
- v0.5 public read-only beta has the shortest safe path: docs exist, write mode stays disabled, and full checks can support a conservative pre-release.
- v0.4 owner-writebeta remains higher risk and needs implemented gate evidence plus copied-book dogfood before any release.
- Real working-book mutation remains blocked without exact same-context owner authorization.

Stop criteria:
- Stop immediately on private artifact, default write enablement, APP_ENV=test weakening, failed restore/read-back/compatibility/default-reset after any mutation, or unsafe release messaging.

Final verdict: CONTINUE
