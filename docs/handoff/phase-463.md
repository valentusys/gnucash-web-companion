# Phase 463 — Real-book preflight/dry-run

- goal: Run only if Phase 462 authorizes real working-book trial.
- scope: Skipped because Phase 462 kept real working-book writes blocked.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: No real working-book preflight/mutation/restore over working book performed.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: No private evidence; defaults disabled.
- expected artifacts: docs/dogfood/phase-463-real-book-preflight-redacted.md; docs/handoff/phase-463.md
- final verdict: CONTINUE.
