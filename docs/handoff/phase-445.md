# Phase 445 — Real working-book eligibility design

- goal: Design future real working-book eligibility.
- scope: Independent backup age, target fingerprint, app metadata identity, Desktop closed confirmation, allowed/forbidden ops, confirmation wording, rollback plan.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Strict testable checklist documented.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: Docs review.
- expected artifacts: docs/write-alpha/real-working-book-eligibility.md; docs/handoff/phase-445.md
- final verdict: CONTINUE.
