# Phase 499 — PM v0.5 release/no-release decision

Goal: Complete the phase objective from the Phase 481–530 roadmap.

Scope: Repository docs, release evidence, GitHub state, and safe verification only.

Non-goals: No private data, no original GnuCash book access, no stable/production release, and no public write-safety claim.

Acceptance criteria: The phase decision/evidence is recorded with safety boundaries intact.

Safety checks: GNUCASH_WRITES_ENABLED=false remains default; APP_ENV=test write gate is not weakened; no private books, app DBs, exports, secrets, raw paths, account names, descriptions, memos, or amounts are committed.

Verification: Git/GitHub state reviewed; public status guard and release/doc posture checked where relevant.

Expected artifacts: This handoff plus the referenced audit/release/strategy/dogfood document.

Findings:
PM decision: AUTHORIZE_V0_5_PRE_RELEASE.

Constraints:
- Publish only a GitHub pre-release.
- Tag: v0.5.0-public-readonly-beta.
- Messaging must say read-only beta, not production-ready, not stable, not security-audited, not public-internet safe, and not public write beta.
- Abort if final checks or tag/release absence fail.

Final verdict: RELEASE_READY
