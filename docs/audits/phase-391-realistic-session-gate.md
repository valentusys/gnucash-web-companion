# Phase 391 — Realistic copied-book session gate

- goal: decide whether a more realistic copied-book write session is safe after Phase 380.
- scope: accepted Phase 354/363 evidence, release/no-release outcome, ownership metadata, backup/restore/compatibility tooling, and owner copy availability.
- non-goals: no mutation, no release.
- acceptance criteria: analyst recommends PM session authorization or stop.
- safety checks: copied/restorable outside-git only; original untouched; PM must set exact operation counts.
- verification: Phase 390 no-release executed; current guards pass; PR #40 merged; a copied SQL book was retrieved from the owner-provided Windows directory as a copy and staged outside git for later preflight; no private path or raw evidence is committed.
- expected artifacts: this audit and `docs/handoff/phase-391.md`.
- final verdict: CONTINUE.

Analyst recommendation: authorize one bounded copied-book session. Keep within previously proven small-batch bounds: exactly 2 CREATE operations, exactly 1 metadata/memo-only PATCH on a write-alpha-created transaction, and 0 DELETE operations.
