# Phase 81 — Default-book Seed Log Redaction

## Status

Complete. Phase 81 was a PM→Engineer post-release hardening phase with one concrete tested behavior change. No auditor role was used. No audit-only phase or `docs/audits/phase-81-audit.md` was created.

No new tag/release was published. No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Pick GitHub #27 for Phase 81: a narrow, low-risk, post-release hardening task that changes real application behavior and is directly testable.

### Why

Phase 80 published `v0.1.0-readonly`; Phase 81 should therefore avoid another release/tag and avoid audit-only work. #27 was open, concrete, security/logging-related, and safely fixable without touching read/write product scope: default-book seed logs exposed full configured paths/URIs even though Phase 54 diagnostics intentionally avoid sensitive path/connection details.

### Phase brief

- Goal: redact default-book seed logs so startup/default-book seed logging does not expose full filesystem paths or connection URI details.
- Non-goals: no auditor role, no audit-only docs, no write-mode changes, no `GNUCASH_WRITES_ENABLED` enablement, no v0.2 planning, no new release/tag, no product-scope expansion.
- Acceptance criteria:
  - `seed_default_book()` still stores the configured path/URI in `Book.uri_or_path` for runtime use.
  - The seed log line includes only a non-sensitive filename/book label.
  - Regression tests prove full local paths, URI strings, hostnames, usernames, credential-like values, and query parameters are not logged.
  - `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff record Phase 81 evidence.
  - GitHub #27 is updated/closed only after evidence exists.
- Safety checks:
  - Keep MVP read-only by default.
  - Do not commit real financial data, real GnuCash books, `.env`, app DB, backups, secrets, keys, screenshots/exports with real data.
  - Preserve positioning: GnuCash Desktop remains authoritative; project is not SaaS, not a GnuCash replacement, not collaborative accounting.
- Verification:
  - RED test first: `pytest tests/test_seed.py::TestSeedDefaultBook::test_seed_log_redacts_full_default_book_path -q` failed before implementation because the full path was logged.
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - verify `v0.1.0-readonly` release state with git/gh.

### GitHub/backlog

- Close #27 with implementation/check evidence.
- Leave #22, #26, #28–#36 open for later narrow phases; do not close issues without evidence.

## Engineer report

### Concrete result

Implemented a tested log-redaction fix for default-book seeding:

- Added `_safe_book_log_label(path)` in `apps/api/app/services/seed.py`.
- Default-book seed logging now emits only a sanitized filename/book label, not the configured full path/URI.
- The configured path/URI is still stored unchanged in `Book.uri_or_path` so runtime book access behavior is preserved.
- URI-derived book names now come from the URI path basename rather than the raw URI/query string, preventing log-visible query parameters.
- Added regression tests in `apps/api/tests/test_seed.py`:
  - full filesystem path redaction while retaining filename visibility;
  - connection URI detail redaction for full URI, username, credential-like value, host, and query parameter.

### TDD evidence

RED:

```text
pytest tests/test_seed.py::TestSeedDefaultBook::test_seed_log_redacts_full_default_book_path -q
FAILED: caplog contained /srv/private/customer-ledgers/main.gnucash.sqlite
```

GREEN targeted check:

```text
pytest tests/test_seed.py -q
11 passed
```

### Required checks

```text
cd apps/api && pytest -q
284 passed, 27 warnings

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

git diff --check
passed
```

Release-state verification:

```text
git tag --list 'v0.1.0-readonly'
v0.1.0-readonly

gh release view v0.1.0-readonly --json tagName,isPrerelease,url,targetCommitish,publishedAt
{"isPrerelease":true,"publishedAt":"2026-05-18T06:04:26Z","tagName":"v0.1.0-readonly","targetCommitish":"main","url":"https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly"}
```

### Files changed

- `apps/api/app/services/seed.py`
- `apps/api/tests/test_seed.py`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-81.md`

### GitHub/release

- GitHub #27 closed after implementation and passing checks.
- No new release/tag was created.
- Existing `v0.1.0-readonly` GitHub pre-release remains published at https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly

### Commit/push

Phase changes were committed and pushed to `origin/main` after the required checks. The pushed HEAD was verified after push, and the working tree was clean.
