# Phase 442 — PM owner-writebeta controls

- goal: PM chooses mandatory controls.
- scope: Controls: armed session, target fingerprint, independent backup proof, restore dry-run proof, Desktop closed confirmation, banner, preview, health check, reset.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: PM requires all listed controls for any v0.4 writebeta claim.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: PM sign-off.
- expected artifacts: docs/strategy/phase-442-owner-writebeta-controls.md; docs/handoff/phase-442.md
- final verdict: CONTINUE.
