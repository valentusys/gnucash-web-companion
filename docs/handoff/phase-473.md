# Phase 473 — Public installation/upgrade docs pass

- goal: Make read-only install docs usable for external tester.
- scope: Added public read-only beta install guide; README points to roadmap/status.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: External tester has concise read-only-only path.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: Docker compose config check; markdown review.
- expected artifacts: docs/deployment/public-readonly-beta-install.md; docs/handoff/phase-473.md
- final verdict: CONTINUE.
