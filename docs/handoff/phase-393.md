# Phase 393 handoff

- goal: preflight copied-book target safely.
- scope: outside-git working copy, read-only piecash open, backup/evidence directories, default-disabled baseline.
- non-goals: no mutation.
- acceptance criteria: preflight passes or blocker recorded.
- safety checks: committed docs are redacted; original untouched; working copy outside git.
- verification: copied SQL book staged outside git; piecash read-only open passed; preflight counts read; defaults remain disabled.
- expected artifacts: `docs/dogfood/phase-393-session-preflight-redacted.md`, this handoff.
- final verdict: CONTINUE.
