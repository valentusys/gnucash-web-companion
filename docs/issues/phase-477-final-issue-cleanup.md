# Phase 477 — Final issue/milestone cleanup

- goal: Prepare repo issues for beta/no-release.
- scope: Reviewed open issues list and mapped #36/#22/#28/#29/#17/#13.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Open issues have clear local meaning.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: gh issue list.
- expected artifacts: docs/issues/phase-477-final-issue-cleanup.md; docs/handoff/phase-477.md
- final verdict: CONTINUE.
