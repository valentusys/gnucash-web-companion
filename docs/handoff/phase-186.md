# Phase 186 — write-alpha audit trail review UI for disposable runs

Date: 2026-05-20
Status: COMPLETE — redacted audit summary endpoint/UI added without expanding write scope
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 5 only)

## Goal

Make write-alpha run audit evidence operator-visible in a safe form without exposing private paths/raw amounts and without turning it into a production audit feature.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-185.md`;
  - roadmap file named by the phase contract;
  - relevant write audit model/routes/tests and frontend protected-route/API files.
- Added a narrow read-only backend endpoint: `GET /books/{book_id}/write-alpha-audit-summary`.
- Endpoint summarizes only app metadata audit rows for `transaction.create`, `transaction.patch`, and `transaction.delete`.
- DTO exposes only safe fields: action, result, timestamp, bounded transaction ID prefix, backup-present boolean, and path-safe error text.
- Endpoint requires authentication and editor/owner access; viewer and unauthorized users are blocked.
- Added `/books/write-alpha-audit` UI for active-book operator review, with explicit disposable-run/non-production-audit copy and redaction boundaries.
- Linked the audit evidence view from `/books` when an active accessible book exists.
- Added backend tests for auth/access/redaction and frontend static route checks for safe fields/no storage/no mutation UI.
- Added synthetic app-DB-only dogfood evidence: `docs/dogfood/phase-186-write-alpha-audit-summary-dogfood.md`.

## Files changed

- `apps/api/app/routers/transactions.py`
- `apps/api/app/schemas/gnucash_writes.py`
- `apps/api/tests/test_write_alpha_audit_summary.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/routes/books/write-alpha-audit/+page.server.ts`
- `apps/web/src/routes/books/write-alpha-audit/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/dogfood/phase-186-write-alpha-audit-summary-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-186.md`

## Verification summary

Commands/results recorded for this phase:

```bash
cd apps/api && pytest tests/test_write_alpha_audit_summary.py -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/api && python <synthetic app-DB audit summary dogfood probe>
```

Results:

- Backend audit-summary tests passed (`3 passed`), including unauthenticated 401, viewer/unauthorized 403, action filtering, bounded transaction ID prefixes, backup-path redaction, private-path safe error mapping, and raw payload leakage checks.
- Frontend auth-route/static checks passed, including the new audit evidence route copy, safe fields, no `localStorage`/`sessionStorage`, no forms, and no raw audit payload rendering.
- Svelte check passed with `0 errors and 0 warnings`.
- Synthetic app-DB-only dogfood passed: admin 200, viewer 403, three create/PATCH/DELETE rows summarized, no paths/raw payload markers returned.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The new endpoint is read-only app metadata only; it does not construct write services or read GnuCash books.
- No GnuCash mutation, new write endpoint, write-mode enablement, release, tag, package, or publication action was performed.
- DTO/UI do not expose backup paths, private file paths, raw request payloads, account names, memos, or amounts.
- No real/private/only-copy book, runtime app DB, runtime book, backup, lock artifact, `.env`, token, key, cert, screenshot, export, raw path, amount, or private financial data was committed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start multi-book regression, reporting edge cases, fresh-clone smoke, release-candidate dogfood, or release-readiness work from this phase.
