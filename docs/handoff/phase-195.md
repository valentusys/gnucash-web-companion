# Phase 195 — Write-alpha audit summary operator UX hardening

Date: 2026-05-20
Status: COMPLETE — scoped endpoint/UI hardening implemented, tested, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 4 only)

## Goal

Improve the read-only audit-summary operator view so disposable write-alpha evidence is easier to review without exposing payloads, backups, paths, memos, account names, or amounts.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-194.md`;
  - roadmap file named by the phase contract;
  - existing audit-summary API/UI/tests.
- Hardened existing read-only endpoint `GET /books/{book_id}/write-alpha-audit-summary`:
  - added safe filters for `action`, `result`, `since`, and `until`;
  - added filtered total/returned counts;
  - added grouped counts by safe action/result labels;
  - kept output app-metadata-only and redacted;
  - kept viewer/unauthorized users blocked and owner/editor users allowed;
  - invalid path-like timestamp filters return safe 422 copy without echoing the input.
- Hardened `/books/write-alpha-audit` operator UX:
  - URL-only GET filters for action/result/time window;
  - count/status cards for filtered rows, actions, results, and time window;
  - filtered empty-state copy that stays disposable/test-only;
  - bounded mobile layout classes (`min-w-0`, `overflow-x-hidden`, truncation) with no forced horizontal scrolling.
- Updated backend/frontend static tests for authorization, redaction, filters, empty states, count/status metadata, no browser storage, and mobile no-overflow guards.
- Updated `PROJECT_STATUS.md`.

## Files changed

- `PROJECT_STATUS.md`
- `apps/api/app/routers/transactions.py`
- `apps/api/app/schemas/gnucash_writes.py`
- `apps/api/tests/test_write_alpha_audit_summary.py`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/books/write-alpha-audit/+page.server.ts`
- `apps/web/src/routes/books/write-alpha-audit/+page.svelte`
- `docs/handoff/phase-195.md`

No write route semantics, write scope, Docker/runtime default, raw audit export, audit editor, release/tag state, GitHub issue state, or product mutation behavior was changed.

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_write_alpha_audit_summary.py -q
# 5 passed, 2 warnings

cd apps/api && pytest tests/test_write_alpha_audit_summary.py tests/test_transaction_writes.py -q
# 64 passed, 34 warnings

cd apps/api && pytest -q
# 469 passed, 34 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered default remains false for API and web

git diff --check
# passed

# sensitive tracked-file hygiene scan from phase execution playbook
# passed
```

## Redaction / safety evidence

Backend tests include synthetic app-metadata rows containing private-looking backup paths, private file paths, raw request/update/delete summaries, memos, account names, and amounts. Assertions prove those strings are absent from the JSON response. The UI static checks pin rendering to the safe summary fields, count/status metadata, and URL-only filters.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The audit summary remains read-only and app-metadata-only; it does not open GnuCash books.
- No raw request payloads, backup paths, private file paths, account names, memos, amounts, or export/editor controls are exposed.
- No localStorage/sessionStorage was added for audit state.
- No real/private/only-copy book was used.
- No `.env`, app DB, book, backup, screenshot, CSV export, token, key, cert, raw path, account name, memo, amount, or private financial artifact was committed.
- No release, tag, package, Docker image, production-readiness claim, security-audit claim, or real/private-book write-safety claim was added.

## Risks / follow-up

- The view is still an operator helper for synthetic/disposable write-alpha evidence only, not a production audit-log product.
- Filters are intentionally narrow and URL-only; no saved views or export are provided to avoid persisting or extracting audit context.
- Write-alpha remains experimental, disabled by default, `APP_ENV=test` gated when enabled, and unsafe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
