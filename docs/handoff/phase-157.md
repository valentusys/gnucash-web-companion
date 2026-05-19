# Phase 157 — Scheduled transactions read-only clarity v2

Date: 2026-05-19
Status: DONE — scheduled/recurring metadata clarity improved without editor, prediction, write, or template-detail exposure
Starting HEAD: `14a9815`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 6/10 only)

## Goal

Make scheduled/recurring transaction awareness more useful without pretending to edit or predict GnuCash schedules.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-156.md`;
  - roadmap phase 6 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 157 only; no neighboring roadmap phases were started.
- Improved `/scheduled` display controls using URL-only, non-persistent metadata filters:
  - status filter: all/enabled/disabled;
  - template-reference filter: all/template present/no template reference;
  - sort display: start date/name/enabled first.
- Added counts and clear-filter links so filtered views explain how many safe scheduled metadata rows are visible.
- Split empty states into:
  - true empty/no adapter-visible scheduled metadata;
  - filtered empty state when URL display filters hide all safe metadata rows.
- Strengthened page copy around safe fields and limitations:
  - GnuCash Desktop remains the authoritative scheduled-transaction editor;
  - no schedule editor is rendered;
  - no next-run prediction is calculated;
  - no template split amounts, accounts, memos, transaction descriptions, or raw SQL are exposed;
  - no scheduled metadata/filter values are persisted in localStorage/sessionStorage.
- Added backend regression coverage for deterministic ordering and DTO redaction of unsafe template/source attributes.
- Updated frontend static route checks to pin scheduled filters, sorting, counts, clear-filter action, no browser storage, no editor controls, and no fake next-run copy.
- Updated `docs/scheduled-transactions.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

Targeted checks run before handoff:

```bash
cd apps/api && pytest tests/test_scheduled_transactions.py -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
```

Results: passed.

Standard checks run for this phase:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'`
- `SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite` after local Docker/Caddy startup with `GNUCASH_WRITES_ENABLED=false` and a temporary ignored `data/app/app.db` reset; the previous ignored app DB was restored after shutdown.
- `git diff --check`
- Sensitive tracked-file hygiene scan

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No scheduled transaction create/edit/delete/instantiate UI or API was added.
- No next-run prediction was added because the phase did not add tested GnuCash schedule semantics.
- No template split amounts, accounts, memos, transaction descriptions, raw SQL, browser persistence, localStorage/sessionStorage state, real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, or private financial data was committed.

## Files changed

- `apps/api/tests/test_scheduled_transactions.py`
- `apps/web/src/routes/scheduled/+page.server.ts`
- `apps/web/src/routes/scheduled/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/scheduled-transactions.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-157.md`
