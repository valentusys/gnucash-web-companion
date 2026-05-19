# Phase 166 — CSV export reliability and user feedback hardening

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 5/10 only)

## Goal

Make synchronous read-only CSV export safer and clearer under empty, filtered, capped, and timeout/error conditions.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-165.md`;
  - roadmap phase 5 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 166 only; no neighboring roadmap phases were started.
- Reviewed the backend CSV endpoint and SvelteKit export proxy behavior:
  - backend keeps `CSV_EXPORT_LIMIT = 10_000`;
  - CSV export remains synchronous and read-only;
  - proxy continues to forward `content-disposition`, content type, and `X-CSV-Export-*` advisory headers.
- Added backend regression coverage for CSV reliability:
  - empty filtered exports return only the CSV header row;
  - empty exports report `X-CSV-Export-Total: 0`, `X-CSV-Export-Truncated: false`, and the synchronous timeout policy;
  - account-scoped filtered exports keep row/header parity through the same endpoint and metadata headers.
- Added one UX improvement where the current UI was ambiguous:
  - transaction-list CSV export now shows localized row-count guidance derived from existing read-only list/count metadata;
  - account-detail CSV export shows the same guidance for the fixed account scope;
  - users see distinct copy for header-only empty exports, under-cap exports, and above-cap/truncated exports;
  - copy explicitly preserves string money values and no currency conversion.
- Updated frontend static route checks to pin the new CSV export UX contract.
- Updated `docs/transactions-filters.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No production writes were enabled.
- No import, background export queue, or CSV cap change was added.
- No raw CSV artifact, real/private GnuCash book, app DB, backup, `.env`, screenshot/export, token, key, cert, private path, account name, transaction description, memo, amount, or private financial data was committed.
- CSV amount values remain strings; no fake currency conversion was added.
- No browser persistence of transaction filters was added.
- No release/tag/package was published.

## Verification

```bash
cd apps/api && pytest tests/test_transaction_export.py -q
cd apps/web && npm run test:auth-routes
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted CSV backend tests passed.
- Frontend auth/static route checks passed.
- Backend full suite passed.
- Frontend `npm run check` passed.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/transactions-filters.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-166.md`
