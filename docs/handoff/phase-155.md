# Phase 155 — Multi-book read-only operator UX slice

Date: 2026-05-19
Status: DONE — safe configured-book diagnostics added without book management actions
Starting HEAD: `ae139e2`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 4/10 only)

## Goal

Advance GitHub #13 without adding dangerous book management: make configured-book visibility and access problems clearer for self-hosted operators.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-154.md`;
  - roadmap phase 4 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 155 only; no neighboring roadmap phases were started.
- Added backend-safe book metadata diagnostics for `GET /books` and `GET /books/{book_id}`:
  - `status`: `available`, `missing_file`, `not_configured`, or `remote_or_unchecked`;
  - `access_status="accessible"` for visible books;
  - `storage_diagnostics` with safe summaries and safe next actions;
  - `operator_guidance.private_path_redacted=true`.
- Removed raw `uri_or_path` from serialized book metadata responses so the API no longer exposes private filesystem paths through `/books` metadata.
- Kept listing app-metadata-focused: local SQLite existence is checked only as a path presence diagnostic; the metadata listing does not open GnuCash data.
- Updated `/books` UI to render storage diagnostics, private-path-redaction copy, and safe next actions while preserving only read-only view links.
- Added/updated tests for unauthorized, archived, missing-file, default marker, existing-file, private-path redaction, and no-management-action behavior.
- Updated `docs/book-switcher-readonly-model.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

Targeted backend metadata/access checks:

```bash
cd apps/api && pytest tests/test_multi_book_access.py tests/test_accounts.py -q
```

Result: passed.

Frontend/static route checks:

```bash
cd apps/web && npm run test:auth-routes
```

Result: passed.

Standard checks run for this phase:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'`
- `git diff --check`
- Sensitive tracked-file hygiene scan

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No upload, delete, default-changing UI, registry edit UI, direct file browser, collaborative/family-wallet flow, or GnuCash data write was added.
- Unauthorized and archived books remain hidden or blocked by backend access checks.
- `/books` metadata does not return raw `uri_or_path` and the UI does not render private paths.
- No real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, account name, description, memo, amount, or private data was committed.
- No tag, release, package, image, or production-readiness/security-audit claim was added.

## Files changed

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_accounts.py`
- `apps/api/tests/test_multi_book_access.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/book-switcher-readonly-model.md`
- `docs/handoff/phase-155.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
