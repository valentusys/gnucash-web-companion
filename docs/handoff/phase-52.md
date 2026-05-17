# Phase 52 — Russian Localization Planning and i18n Foundation

## Status

Complete. Phase 52 implemented the i18n foundation, kept English as the default, added a small manually reviewed Russian UI string set, updated status/release-facing docs, passed required checks, updated GitHub #17, and pushed the phase commit. No blockers remain.

## PM report

### Decision

Execute exactly Phase 52 from the roadmap: start Russian localization carefully by adding a narrow SvelteKit i18n foundation and a small reviewed Russian string set, without translating the whole app or making Russian the default.

### Why

The project is mature enough to begin opt-in localization, but v0.1 must not be blocked by translation completeness. A typed in-repo catalog keeps the foundation small and auditable while preserving English docs and safety wording as canonical.

### Phase brief

- Goal: add an English-default i18n structure, opt-in Russian UI strings for the requested small surface, and documentation that translations may lag English.
- Non-goals: no full-project translation, no Russian default, no v0.1 translation blocker, no machine-translated safety warnings without review, no controlled-write expansion, no release/tag publication.
- Acceptance criteria:
  - i18n foundation exists in the SvelteKit app.
  - English UI remains the default and existing English UI is not broken.
  - Russian strings exist for login, safety banner, dashboard title, accounts title, and transactions title.
  - `README.ru.md` stub/initial translation exists.
  - Documentation states English docs are canonical and translations may lag.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
  - GitHub #17 is updated if `gh` is available.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe/default documented state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No write routes, write UI scope, auth token storage, release artifacts, real data, `.env`, app DB, backups, secrets, keys, or tokens are added.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Locale work could expand into full translation churn. Mitigation: Phase 52 limited translation to the requested strings only.
- Safety text could be mistranslated. Mitigation: Russian safety banner and README wording were written manually; docs forbid unreviewed machine-translated safety text.
- Locale persistence could introduce browser-storage policy drift. Mitigation: locale uses a server-set `ui_locale` cookie and auth-route checks assert no localStorage/sessionStorage use outside existing theme code.

### Files/docs to update

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/i18n/index.ts`
- `apps/web/src/routes/locale/+server.ts`
- `apps/web/src/lib/components/LocaleSwitcher.svelte`
- Login/navigation/safety banner/dashboard/accounts/transactions Svelte components
- `apps/web/scripts/test-auth-routes.mjs`
- `README.ru.md`
- `docs/localization.md`
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-52.md`

### GitHub/backlog

- Related issue: GitHub #17.
- Phase 52 should update #17 with the foundation summary and leave it open for broader translation/docs work unless the issue scope says otherwise.
- Next planned phase after completion: Phase 53 — Community announcement draft.

## Engineer report

Implemented Phase 52 only:

- Added typed English/Russian message catalog and helper functions in `apps/web/src/lib/i18n/`.
- Added `/locale` server route that stores opt-in locale choice in an httpOnly `ui_locale` cookie.
- Added `LocaleSwitcher.svelte` and wired it into login, desktop nav, and mobile nav.
- Localized the requested small set while preserving English default:
  - login title/subtitle/labels/button;
  - authenticated navigation labels;
  - read-only safety banner label/message;
  - dashboard title;
  - accounts title;
  - transactions title.
- Added static route checks for i18n defaults, Russian string presence, cookie-based locale switching, and no browser storage for locale/auth.
- Added `README.ru.md` initial Russian stub and `docs/localization.md` documenting the English-canonical policy, manually reviewed safety text requirement, and non-goals.
- Updated `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` through Phase 52.

No backend product behavior was changed. No write route, write UI scope, auth-token storage path, release/tag, real financial data, fixture binary, secret, or backup was added.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed (`280 passed`, 27 existing warnings).
- `cd apps/web && npm run check` — passed (`0 errors`, `0 warnings`).
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- Russian is opt-in; English remains default and canonical for docs/safety wording.
- No write scope was expanded.
- No book upload, import, admin book-management UI, account editing, sync, banking integration, or collaborative editing was added.
- No auth token localStorage/sessionStorage path was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Commit message: `feat: add phase 52 i18n foundation`.
- Push: pushed to `origin/main`.

## GitHub issue status

- GitHub #17 was updated with the Phase 52 localization foundation summary and remains open for broader future translation/localization work.

## Blockers

None.
