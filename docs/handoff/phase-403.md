# Phase 403 — Backup manifest / restore trace improvement

- goal: improve traceability between mutation, backup, audit row, restore check.
- scope: document opaque-ref trace requirements and verify existing evidence schema covers refs.
- non-goals: no write behavior expansion.
- acceptance criteria: mutation evidence correlates backup/audit/restore by opaque refs.
- safety checks: no raw paths/private values.
- verification: existing Phase 391-398 evidence has route backup count, ownership refs, audit counts, restore proof; docs updated through runbook/evidence matrix.
- expected artifacts: handoff.
- final verdict: CONTINUE.
