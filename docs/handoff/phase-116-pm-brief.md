# Phase 116 PM brief — GitHub #38 copied personal-book dogfood

Date: 2026-05-19
Status: planned
Related issue: GitHub #38

## Decision

Run the copied personal-book dogfood pass now that Val provided an explicit safe copied GnuCash SQL book archive. Keep the whole phase local-only, read-only, redacted, and non-release.

## Goal

Validate the existing read-only Docker/Caddy deployment against the copied personal GnuCash SQL book enough to close GitHub #38 if all required dogfood evidence passes.

## Non-goals

- Do not publish tags, releases, packages, screenshots, CSV exports, or raw data dumps.
- Do not enable write mode or expand controlled-write capability.
- Do not commit the copied book, source zip, runtime app DB, backups, `.env`, screenshots, CSV exports, private filesystem paths, account names, transaction descriptions, memos, amounts, tokens, credentials, or secrets.
- Do not claim production readiness, security audit, broad compatibility, hosted SaaS readiness, or safe write mode.

## Acceptance criteria

- The archive is unpacked only into a private temporary directory outside the repository.
- Minimal SQLite preflight passes without printing private GnuCash data.
- Local Docker/Caddy deployment runs with `GNUCASH_WRITES_ENABLED=false` against the copied book.
- `/api/health` passes.
- Login, dashboard, accounts, account detail, transactions, transaction detail, filters, and CSV export paths are checked.
- Write UI remains hidden.
- Write endpoints return HTTP 403 while writes are disabled.
- Results are recorded in a redacted dogfood artifact with only route/status/pass-fail evidence.
- GitHub #38 receives a redacted evidence comment and is closed only if all acceptance criteria pass.

## Safety checks

- Keep original cache zip untouched.
- Keep all runtime state outside git.
- Use local-only URLs.
- Do not print or commit private account names, descriptions, memos, amounts, full private paths, raw SQL dumps, screenshots, or CSV bodies.
- Confirm tracked files do not include sensitive artifact names or private runtime outputs before commit.

## Verification

Minimum required:

```bash
git diff --check
python sensitive tracked-file scan over git ls-files with synthetic fixture allowlist
SMOKE_API_BASE_URL=http://localhost:18080/api SMOKE_ADMIN_PASSWORD=... GNUCASH_WRITES_ENABLED=false scripts/smoke/read-only-api-smoke.py
SMOKE_WEB_BASE_URL=http://localhost:18080 SMOKE_ADMIN_PASSWORD=... GNUCASH_WRITES_ENABLED=false scripts/smoke/read-only-browser-dogfood.py
```

Full backend/frontend suites are optional if no product code changes are made.

## Files/docs to update

- `docs/dogfood/phase-116-personal-book-dogfood.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-116.md`

## GitHub/backlog

- If all evidence passes, comment on and close GitHub #38 as completed.
- If any required evidence is blocked or fails, leave GitHub #38 open with a redacted BLOCKED/FAIL comment.
