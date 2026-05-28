# Phase 475 — Security/privacy posture

- goal: Prepare public-readonly posture.
- scope: Added security posture doc; SECURITY.md update if needed.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: No public internet/security-audited claim.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: Docs review; secret/private scan.
- expected artifacts: docs/security/public-readonly-beta-security-posture.md; docs/handoff/phase-475.md
- final verdict: CONTINUE.
