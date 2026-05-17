# Phase 38 — Personal Dogfood Readiness

## Status

Complete. Documentation/checklist artifacts created; checks passed; commit/push completed.

## PM report

### Decision

Execute exactly Phase 38 from the roadmap as a read-only personal dogfood readiness phase.

### Why

After the Phase 37 audit/status sync, the next safest step is not a new feature or release. The project needs a conservative guide for testing the existing read-only UI/API against a copied personal GnuCash SQL book while preserving the core boundary: MVP read-only by default and controlled writes experimental/post-MVP only.

### Phase brief

- Goal: prepare a human-safe personal dogfood path for local read-only testing on a copied GnuCash SQL book.
- Non-goals: no product features, no automated smoke implementation, no release/tag, no write-scope expansion, no write-mode enablement, no real data committed.
- Acceptance criteria:
  - `docs/dogfood/personal-readonly-dogfood.md` exists and explains copied-book setup, `data/books/`, `GNUCASH_WRITES_ENABLED=false`, Docker startup, screens to check, CSV export, write UI hidden confirmation, shutdown, and cleanup.
  - `scripts/smoke/read-only-smoke-check.md` exists as the Phase 38 manual smoke checklist.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized for Phase 38.
  - Relevant checks pass.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe default.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No write code, auth storage, release artifact, real GnuCash book, `.env`, app DB, backup, secret, token, key, screenshot, or real export is committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

### Risks

- Dogfood instructions could accidentally encourage use of the authoritative real book; mitigated by repeated copy-only warnings.
- CSV export during dogfood can contain sensitive financial data; mitigated by explicit do-not-commit/delete guidance.
- Manual smoke checklist could be mistaken for Phase 39 automation; mitigated by naming it as manual and deferring automated smoke to Phase 39.

### Files/docs to update

- `docs/dogfood/personal-readonly-dogfood.md`
- `scripts/smoke/read-only-smoke-check.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-38.md`

### GitHub/backlog

- No Phase 38-specific GitHub issue was found in the current open issue list.
- Existing #18, #20, and #22 remain open for their separate scopes.

## Engineer report

Implemented Phase 38 documentation/checklist work only:

- Created `docs/dogfood/personal-readonly-dogfood.md`:
  - copy-only GnuCash SQL book setup under `data/books/`;
  - `.env` guidance with `GNUCASH_WRITES_ENABLED=false`;
  - Docker startup path;
  - required screen checks for login, dashboard, accounts, account detail, transactions, transaction detail, and CSV export;
  - explicit confirmation that write UI remains hidden in read-only mode;
  - shutdown/cleanup steps for app DB, copied book, backups, downloads;
  - safe dogfood reporting rules that avoid real financial data.
- Created `scripts/smoke/read-only-smoke-check.md` as a manual smoke checklist for this dogfood phase.
- Updated `PROJECT_STATUS.md` to completed through Phase 38 and set Phase 39 as the next planned phase.
- Updated `CHANGELOG.md` with a Phase 38 Unreleased entry.

No product code changed. No write behavior changed. No release/tag was created.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed (`269 passed, 27 warnings`).
- `cd apps/web && npm run check` — passed, 0 errors/warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No auth localStorage/sessionStorage path was introduced.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, certs, real screenshots, or real CSV exports were added.

## Commit / push

- Commit message: `docs: add phase 38 dogfood readiness`.
- Final commit SHA: see `git log -1 --oneline` for this phase commit.
- Push: pushed to `origin/main`.

## GitHub issue status

- No Phase 38-specific GitHub issue was found in the current open issue list.
- GitHub #18, #20, and #22 intentionally remain open for separate scopes.
