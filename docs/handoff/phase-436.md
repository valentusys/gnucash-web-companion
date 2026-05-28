# Phase 436 — Open issue and milestone triage

- goal: Align open issues with milestones.
- scope: Reviewed open issues #36, #22, #28, #29, #17, #13 from gh issue list.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Issues mapped locally; no noisy issue changes required for this run.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: gh issue list --state open.
- expected artifacts: docs/issues/phase-436-milestone-triage.md; docs/handoff/phase-436.md
- final verdict: CONTINUE.

Mapping: #36 owner-writebeta safety; #22 public-readonly compatibility; #28 public docs readability; #29 future localization glossary; #17 future Russian docs/UI localization; #13 future multi-book UI.
