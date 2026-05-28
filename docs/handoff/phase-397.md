# Phase 397 handoff

- goal: prove restore and compatibility after the realistic session.
- scope: pre-batch backup restore, piecash read-only open, default-disabled reset.
- non-goals: no new mutation.
- acceptance criteria: restore and compatibility pass.
- safety checks: restore targets outside git; no private evidence committed.
- verification: restored backup checksum matched; restored counts matched pre-session counts; piecash read-only open passed; disabled create/PATCH returned 403.
- expected artifacts: `docs/dogfood/phase-397-session-restore-compat.md`, this handoff.
- final verdict: CONTINUE.
