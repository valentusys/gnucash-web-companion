# Phase 448 — Owner warning and confirmation UI prototype

- goal: Add UI warnings for future owner-writebeta.
- scope: Extended WriteModeWarning.svelte with owner-writebeta session gate warning prototype.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: UI warns that preflight, backup/restore readiness, preview and confirmation are required, and makes no safety claim.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: cd apps/web && npm run check.
- expected artifacts: apps/web/src/lib/components/WriteModeWarning.svelte; docs/handoff/phase-448.md
- final verdict: CONTINUE.
