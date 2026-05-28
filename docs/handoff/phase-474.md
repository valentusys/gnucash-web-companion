# Phase 474 — Public read-only smoke/fresh-clone test

- goal: Verify public read-only beta install path.
- scope: Local full fresh-clone Docker/browser smoke was not run in this constrained run; config and tests ran instead.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Fresh-clone smoke remains blocker for release candidate.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: pytest targeted; npm check; docker compose config.
- expected artifacts: docs/dogfood/phase-474-public-readonly-fresh-clone-smoke.md; docs/handoff/phase-474.md
- final verdict: CONTINUE.

Blocker: v0.5 release requires an actual fresh-clone read-only smoke on synthetic/disposable data.
