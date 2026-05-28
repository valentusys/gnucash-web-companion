# Phase 397 — Session restore and compatibility proof

- goal: prove copied book and relevant backups remain usable after the session.
- scope: restore from backup, verify mutated and restored books via available tooling.
- non-goals: no new mutation.
- acceptance criteria: restore and compatibility pass or blocker documented.
- safety checks: restore targets outside git; no private evidence committed.
- verification: pre-batch backup existed; restored target matched backup checksum; restored counts returned to pre-session transaction count; mutated book opened read-only with piecash; disabled create and patch probes returned 403 after reset.
- expected artifacts: this redacted dogfood summary and `docs/handoff/phase-397.md`.
- final verdict: CONTINUE.
