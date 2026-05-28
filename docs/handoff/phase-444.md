# Phase 444 — Backup and restore UX design

- goal: Design operator backup/restore workflow.
- scope: User-visible backup location classes, restore verification, failure states, Desktop validation instructions.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Workflow includes blocker states.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: Docs review.
- expected artifacts: docs/write-alpha/backup-restore-ux-design.md; docs/handoff/phase-444.md
- final verdict: CONTINUE.
