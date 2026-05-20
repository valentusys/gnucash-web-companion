# Phase 178 — write-alpha UX guardrails from dogfood findings

Date: 2026-05-20
Status: COMPLETE — narrow UX/safety guardrails updated from disposable dogfood findings
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 7 only)

## Goal

Fix only real UX/safety friction discovered during copied-book write-alpha dogfood.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-177.md`;
  - roadmap file named by the phase contract;
  - Phase 175–177 dogfood evidence and frontend write-mode routes/static checks.
- Used the concrete Phase 175–177 dogfood finding that write-alpha operators need clearer visible completion criteria: explicit `APP_ENV=test`, ignored disposable runtime copy, never source/only copy, and backup/audit/lock-release evidence.
- Updated only warning/acknowledgement/error guardrails and static checks.
- Ran default-false browser dogfood to confirm write controls remain hidden.

## Files changed

- `apps/web/src/lib/components/WriteModeWarning.svelte`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/transactions/new/+page.svelte`
- `apps/web/src/routes/transactions/new/+page.server.ts`
- `apps/web/src/routes/transactions/[id]/+page.server.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/dogfood/phase-178-write-alpha-ux-guardrails.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-178.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The hidden-by-default write UI gate still depends on `env.GNUCASH_WRITES_ENABLED === 'true'`.
- No write route, account/import/recurring write feature, backend mutation semantics, Docker default, or `APP_ENV=test` gate was changed.
- Safe frontend error mapping now suppresses raw path-like backend detail strings in write-alpha create/delete forms.
- No localStorage/sessionStorage was added; existing theme-only storage allowance remains unchanged.
- No real/private/only-copy book was opened or mutated.
- No release/tag/package was published.
- No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Verification

Commands run:

```bash
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
APP_ENV=test JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-browser-dogfood.py
APP_ENV=test JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down --remove-orphans
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
git diff --check
python3 <tracked sensitive-file hygiene scan>
```

Results:

- Frontend route/static checks passed.
- Svelte check passed.
- Frontend production build passed.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` by default.
- Default-false browser dogfood passed, including hidden write UI and no `New transaction` link in the read-only runtime. One initial run against `http://127.0.0.1:8080` failed the same-origin login guard because runtime `ORIGIN` was `http://localhost:8080`; rerun against matching `http://localhost:8080` passed.
- `git diff --check` passed.
- Tracked sensitive-file hygiene scan passed.

## Next

Continue only with the next explicitly requested phase. Do not run Phase 8 API hardening, combined regression dogfood, release-readiness gate, release/tag publication, PATCH dogfood, DELETE dogfood, or private-book disaster recovery unless a later phase explicitly requests it.
