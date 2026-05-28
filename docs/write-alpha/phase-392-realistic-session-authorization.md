# Phase 392 — Realistic session authorization

- goal: PM defines one bounded copied-book write session.
- scope: exact operation limits, target rules, abort conditions, restore requirements.
- non-goals: no mutation in this phase.
- acceptance criteria: PM writes exact operation limits, target rules, abort conditions, restore requirements.
- safety checks: no historical/manual transaction mutation; no amount/account/split mutation; no DELETE in this session.
- verification: PM sign-off recorded here.
- expected artifacts: this authorization and `docs/handoff/phase-392.md`.
- final verdict: CONTINUE.

PM authorization: `AUTHORIZE_REALISTIC_SESSION_2C_1P_0D`.

Limits:
- CREATE: exactly 2 two-split disposable write-alpha test transactions.
- PATCH: exactly 1 metadata/memo-only PATCH on the first transaction created in this session.
- DELETE: exactly 0. No DELETE is authorized in this session.

Abort conditions: stop on any backup, read-back, audit, ownership, restore, compatibility, default-reset, outside-git, or redaction failure. Mutate only the copied/restorable working copy outside git. Commit only redacted summaries.
