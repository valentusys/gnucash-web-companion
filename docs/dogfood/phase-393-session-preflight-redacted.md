# Phase 393 — Session preflight and snapshot (redacted)

- goal: prepare copied-book target safely before realistic session.
- scope: outside-git target, temporary app DB context, independent backup, redaction, backup directory, compatibility tools, default-disabled baseline.
- non-goals: no mutation.
- acceptance criteria: preflight passes or stops with blocker.
- safety checks: no private paths in committed docs; checksums/snapshots captured locally only; original source not mutated.
- verification: copied SQL book was retrieved from the owner-provided Windows directory as a copy, extracted, then copied again into an outside-git working directory; piecash read-only open passed; counts were read; working-copy checksum prefix was recorded locally only; `.env.example`/Docker defaults remain disabled.
- expected artifacts: this redacted preflight and `docs/handoff/phase-393.md`.
- final verdict: CONTINUE.

Redacted result: preflight passed. The working target is outside git and restorable/discardable. Private source/target paths, account names, descriptions, memos, amounts, and raw checksums are intentionally not committed.
