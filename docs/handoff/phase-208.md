# Phase 208 — Frontend safety/locale polish for operator flows

Date: 2026-05-20
Status: COMPLETE — operator-facing safety copy is catalog-backed for the changed English/Russian read-only/write-alpha flows
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 7 only)

## Goal

Polish English/Russian safety copy for operator-facing read-only/write-alpha warnings without claiming full localization or changing backend behavior.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-207.md`, and the cycle-1 roadmap file.
- Kept English canonical and Russian partial/opt-in; no backend API localization rewrite was added.
- Added/updated typed catalog keys for release-critical read-only safety, write-alpha warnings, acknowledgement/final-confirmation text, books audit-evidence link copy, and write-alpha audit-summary labels/help/error states.
- Routed relevant visible safety/operator strings through `t(locale, ...)` in:
  - app-shell read-only status banner;
  - books page audit-evidence link;
  - write-mode warning component;
  - transaction create acknowledgement/final confirmation;
  - write-alpha audit-summary page.
- Extended static frontend checks to pin safe localization usage and wording boundaries for pre-alpha/not-production/not-security-audited/default-false/disposable-only copy.
- Preserved existing no-browser-storage boundaries for locale/auth/financial state; only the existing theme preference exception remains.
- Updated `CHANGELOG.md`, `docs/localization.md`, and `PROJECT_STATUS.md`.

## Files changed

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte`
- `apps/web/src/lib/components/WriteModeWarning.svelte`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/routes/books/write-alpha-audit/+page.svelte`
- `apps/web/src/routes/transactions/new/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `CHANGELOG.md`
- `docs/localization.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-208.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest -q
# passed: 481 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check
# passed: svelte-check 0 errors/0 warnings

cd apps/web && npm run test:auth-routes
# passed: auth route checks passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

git diff --check
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite
# passed: default read-only browser dogfood on copied committed synthetic fixture; write UI hidden; auth cookie not readable from document.cookie; mobile no-overflow checks passed; CSV route check passed; no screenshot/download/CSV artifacts written
```

Docker/Caddy smoke used only the committed synthetic fixture copied into ignored `data/books/main.gnucash.sqlite` and was torn down after verification. The ignored runtime fixture copy was removed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write UI remains gated and hidden in default read-only browser dogfood.
- No backend write behavior, backend API localization, write scope, release/tag, product marketing launch, production-readiness claim, or security-audit claim was added.
- Russian remains a conservative operator-safety slice only; this phase does not claim full-app localization.
- No localStorage/sessionStorage was added for locale, auth, book, audit, or financial state.
- No secrets, app DB, backup artifact, `.env`, screenshot, export, token, key, cert, private path, account name, memo, amount, real/private book, or private financial data was committed.

## Risks / follow-up

- Localization coverage is intentionally partial and operator-safety focused; future user-facing copy still needs separate review before being described as localized.
- Backend/API error payloads remain English/server-canonical unless a future scoped phase explicitly designs API localization.
- This phase did not add new write-alpha dogfood evidence or change any write backend behavior.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
