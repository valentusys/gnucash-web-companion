# Phase 207 — Write-alpha audit-summary redaction hardening

Date: 2026-05-20
Status: COMPLETE — audit-summary endpoint/UI now exposes only bounded counts/status/time windows and stricter redacted rows
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 6 only)

## Goal

Strengthen the read-only write-alpha audit-summary endpoint/UI so prior disposable write runs are inspectable without leaking payloads, backup paths, amounts, memos, account names, or private paths.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-206.md`, and the cycle-1 roadmap file.
- Hardened the existing read-only `GET /books/{book_id}/write-alpha-audit-summary` endpoint:
  - payload `result` is normalized to `started`, `success`, `failed`, or `unknown`;
  - payload `timestamp` is used only when safely parseable and non-path-like, otherwise the app metadata `created_at` timestamp is used;
  - transaction ID prefixes are emitted only for opaque safe ID-like values, never path-like text;
  - error text is replaced with a generic safe message when it contains path/URI markers, amount-like decimals, or account/memo/description/private-book wording;
  - response metadata now includes bounded `time_window` and `status_summary` rows for operator review.
- Preserved access constraints: admin/owner and editor access still allowed; viewer, outsider, and unauthenticated access remain blocked.
- Updated `/books/write-alpha-audit` to render requested/returned time windows and bounded status rows while still showing only action/result/timestamp/opaque transaction prefix/backup-present/safe-error fields.
- Updated frontend static checks to pin URL-only filters, safe count/status/time-window UX, bounded mobile layout, and no raw payload/browser-storage/mutating controls.
- Updated `CHANGELOG.md` and `PROJECT_STATUS.md` with factual Phase 207 state.

## Files changed

- `apps/api/app/routers/transactions.py`
- `apps/api/app/schemas/gnucash_writes.py`
- `apps/api/tests/test_write_alpha_audit_summary.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/books/write-alpha-audit/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-207.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_write_alpha_audit_summary.py -q
# passed: 6 passed; existing piecash/FastAPI warnings only

cd apps/api && pytest -q
# passed: 481 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed: svelte-check 0 errors/0 warnings; auth route checks passed; build passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://127.0.0.1:8080/api --username admin
# passed: validate/create/PATCH/DELETE disabled-write probes returned 403
```

Runtime cleanup after the smoke stopped Docker Compose, removed the ignored synthetic runtime book, and removed the ignored app DB via the stopped-runtime cleanup helper.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was confirmed in rendered Docker Compose config for API and web.
- The audit-summary route remains read-only and app-metadata-only; it does not open, parse, copy, mutate, back up, restore, or lock a GnuCash book.
- No new mutating write route, write-scope expansion, automatic lock deletion, release/tag publication, or production write-safety claim was added.
- Raw audit payloads, backup paths, private paths, amounts, memos, account names, descriptions, request summaries, patch field values, and delete summaries are not rendered by the endpoint/UI.
- No localStorage/sessionStorage was added for audit state.
- Docker smoke used only the committed synthetic fixture copied into ignored `data/books/main.gnucash.sqlite`; ignored runtime artifacts were removed after teardown.
- No real/private book, app DB, backup, `.env`, screenshot, export, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.

## Risks / follow-up

- Audit summary remains an operator convenience view over local app metadata for synthetic/disposable write-alpha evidence only; it is not a production audit-log product.
- Error redaction is intentionally conservative and may hide harmless custom error wording if it looks like a path, amount, account, memo, description, or private data.
- This phase did not run write-enabled dogfood and does not add any new write-safety evidence for real/private books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
