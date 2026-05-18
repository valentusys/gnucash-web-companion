# Phase 116 — GitHub #38 copied personal-book dogfood

Date: 2026-05-19
Status: complete
Related issue: GitHub #38
PM brief: `docs/handoff/phase-116-pm-brief.md`
Dogfood artifact: `docs/dogfood/phase-116-personal-book-dogfood.md`

## Summary

Phase 116 completed the GitHub #38 copied personal-book dogfood pass using Val's provided safe copied GnuCash SQL book archive. The run stayed local-only and read-only, with `GNUCASH_WRITES_ENABLED=false` throughout.

The source archive was not modified. The copied book was unpacked only into a private temporary directory outside the repository and mounted read-only into a local Docker/Caddy deployment. Runtime app DB, backups, locks, compose override, browser profile, and any transient state stayed outside git.

## Result

PASS — all GitHub #38 acceptance criteria were met:

- `/api/health` passed against the copied personal book.
- Login, dashboard, accounts, account detail, transactions, transaction detail, filter, and CSV export paths were checked.
- Write UI remained hidden on checked UI routes.
- Disabled write endpoints returned HTTP 403.
- Redacted evidence was recorded without private data.

## Implementation / operations

- Created PM brief: `docs/handoff/phase-116-pm-brief.md`.
- Created redacted dogfood artifact: `docs/dogfood/phase-116-personal-book-dogfood.md`.
- Used Docker/Caddy with an override file outside the repository to mount the private copied book read-only and keep app DB/backups/locks outside git.
- No product code changes were required.
- No tag, release, package, public release artifact, screenshot, CSV export file, `.env`, app DB, backup, copied book, or source zip was committed.

## Verification

Passed:

```bash
# Copied-book minimal preflight, no private data printed
# filename present, SQLite read-only open, integrity_check=ok, required table set present

SMOKE_API_BASE_URL=http://localhost:18080/api \
  SMOKE_ADMIN_PASSWORD=... \
  GNUCASH_WRITES_ENABLED=false \
  scripts/smoke/read-only-api-smoke.py
# PASS: read-only API smoke checks completed

SMOKE_WEB_BASE_URL=http://localhost:18080 \
  SMOKE_ADMIN_PASSWORD=... \
  GNUCASH_WRITES_ENABLED=false \
  scripts/smoke/read-only-browser-dogfood.py
# PASS: read-only browser dogfood completed

git diff --check
# passed

python sensitive tracked-file scan over git ls-files with synthetic fixture allowlist
# PASS: no unexpected tracked sensitive artifact names
```

Full backend/frontend suites were not rerun because Phase 116 made no product-code changes. The Docker image build executed the frontend production build successfully as part of `docker compose up --build`.

## Safety

- `GNUCASH_WRITES_ENABLED=false` was enforced.
- Source cache archive was not modified.
- Copied book was used only from private temporary storage outside git.
- No raw SQL dumps were performed.
- No private account names, transaction descriptions, memos, amounts, full private filesystem paths, app DB contents, credentials, tokens, cookies, screenshots, or CSV bodies were committed or recorded in docs.
- No release/tag/package was published.
- Controlled writes remain post-MVP/experimental and disabled by default.

## GitHub

GitHub #38 was eligible to close after this phase because all acceptance evidence passed. A redacted issue comment was prepared with links to the committed artifact and handoff.

## Commit/push

- Commit: pending at handoff creation time; final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
