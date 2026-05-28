# Phase 472 — PM public-readonly scope decision

- goal: PM picks minimal v0.5 scope.
- scope: Scope: installation guide, security posture, feedback packet, final issue cleanup, fresh-clone smoke gate.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: PM excludes public write and broad launch.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: PM sign-off.
- expected artifacts: docs/strategy/phase-472-public-readonly-beta-scope.md; docs/handoff/phase-472.md
- final verdict: CONTINUE.
