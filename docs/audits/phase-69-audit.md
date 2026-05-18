# Phase 69 Audit — Localization / i18n

Date: 2026-05-18

## Executive summary

Phase 69 audited the current Russian localization and i18n foundation. The current implementation is intentionally narrow and mostly consistent with the product safety boundary: English documentation remains canonical, Russian is opt-in, and localized safety copy does not promote writes, SaaS, production readiness, or collaborative accounting.

The audit found no release blocker caused by localization. It did find one meaningful non-blocking gap: there is no localization glossary for accounting and safety terms, so future Russian translation work could drift in terminology. GitHub issue #29 was created for that follow-up.

This audit does not approve `v0.1.0-readonly` publication. Existing release blockers #24 and #25 remain open.

## Verdict

Localization/i18n posture acceptable for the current pre-alpha read-only scope, with non-blocking glossary follow-up required before localization grows.

## Blockers

No new Phase 69 localization blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.
3. #27 — full configured GnuCash book paths/URIs should be redacted or summarized in default-book seed logs before shared/local deployment posture is treated as hardened.

## Important non-blockers

1. No dedicated localization glossary exists for accounting/safety terms. This is non-blocking for v0.1 because Russian localization is explicitly opt-in and incomplete, and English remains canonical. Tracked as #29.
2. `README.ru.md` is intentionally a short starter/reference page rather than a full translation. This is acceptable because it explicitly says it may lag behind English.
3. Backend/API error messages remain English-only. This matches the documented Phase 52 non-goals and should not block v0.1 unless PM changes release criteria.

## Localization/i18n checks

### English remains canonical

Passed.

Evidence:

- `README.ru.md` says English documentation in `README.md` remains canonical and the Russian file may lag.
- `docs/localization.md` says English remains the canonical language for product documentation and safety wording.
- `docs/localization.md` says Russian localization is a convenience layer and may lag behind English until reviewed.

### Russian README consistency

Passed.

`README.ru.md` does not contradict the English README on the audited safety/product points:

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` is the safe default.
- Controlled writes are experimental post-MVP and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- Users should test with a copy or synthetic fixture first.
- Early builds should not be exposed directly to the internet.
- English safety/security texts are the source of truth.

### Russian safety warnings manually reviewed

Acceptable for current scope.

Evidence:

- `docs/localization.md` states that Russian safety copy was written manually.
- `apps/web/src/lib/i18n/messages.ts` contains a small Russian safety banner string that preserves the read-only/default-write boundary:
  - `MVP по умолчанию работает только на чтение.`
  - `GnuCash Desktop остаётся главным редактором`
  - web writes require a separate post-MVP feature flag.

No machine-translation workflow or bulk translated safety text was introduced.

### UI i18n route safety

Passed by static inspection and frontend checks.

Evidence:

- Default locale is `en` in `apps/web/src/lib/i18n/messages.ts`.
- Supported locales are limited to `en` and `ru`.
- `localeFromCookie()` falls back to English for missing/invalid locale cookies.
- `/locale` accepts only supported locale values and redirects to a safe same-origin path returned by `safeReturnTo()`.
- The locale cookie is httpOnly, sameSite=lax, path=/, and stores only a locale value, not an auth token.
- The locale switcher changes only UI language and does not affect book selection, auth, write flags, or API routes.

### Locale defaults

Passed.

English remains the default. Russian remains opt-in through the UI language switcher and `ui_locale` cookie.

### Financial/accounting terms consistency

Partially passed with a non-blocking gap.

Current localized surface is small and uses understandable terms:

- Accounts → `Счета`
- Account tree → `Дерево счетов`
- Transactions → `Транзакции`
- Browse transactions → `Просмотр транзакций`
- Dashboard → `Обзор`

However, no durable glossary exists for future terms such as book, split, balance, commodity/currency, placeholder account, read-only, authoritative editor, and controlled writes. Created #29 to track a glossary before the translation surface grows.

### Translation does not block v0.1 unless PM says so

Passed.

Evidence:

- `docs/localization.md` explicitly says Russian is not the default locale and v0.1 is not blocked on complete translation.
- `README.ru.md` says Russian localization is only an initial starter page and English docs remain canonical.
- The v0.1 release plan lists localization issue #17 as post-MVP/non-blocking unless maintainers decide Russian docs are required before announcement.

## Product consistency

Passed for Phase 69 scope.

No audited localization doc or UI string reframes the project as SaaS, a GnuCash replacement, collaborative accounting, a family-wallet baseline, production-ready, security-audited, or safe for writes.

## Safety boundary

Passed for Phase 69 scope.

`GNUCASH_WRITES_ENABLED=false` remains the documented/default state. Phase 69 did not change backend settings, write routes, write UI, fixtures, deployment defaults, or any GnuCash access behavior.

## Release/readme/docs consistency

Mostly passed.

- README and PROJECT_STATUS were current through Phase 68 before this phase.
- README already linked the localization docs and correctly described the Phase 52 localization scope.
- `CHANGELOG.md` contained a Phase 52 localization entry and recent audit entries.
- Release docs do not require complete Russian localization for v0.1.

Required Phase 69 status synchronization is to update README, PROJECT_STATUS, CHANGELOG, and handoff after this audit.

## GitHub project hygiene

Passed with one created issue.

Created:

- #29 — Add localization glossary for accounting terms.

Existing related issue:

- #17 — Plan Russian documentation and UI localization.

No noisy issues were created for the intentionally short Russian README or English-only backend errors because both match the documented current scope.

## Security notes

No new security blocker found.

The locale switcher does not store auth tokens in localStorage/sessionStorage. Auth remains cookie-based. The `ui_locale` cookie is not sensitive and is limited to supported values. The audit did not find localization text that weakens public-internet or write-mode warnings.

## Test/CI notes

Relevant checks for this phase should include:

- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `git diff --check`
- optionally backend and Docker config validation for full phase confidence.

Because this phase records a release-adjacent audit trail, full backend/frontend/Docker checks may be run even though no product code is changed.

## Recommended next actions

1. Keep #29 open as a non-blocking localization-quality follow-up.
2. Do not make Russian the default locale before a broader manual review.
3. Do not require full Russian docs for v0.1 unless PM explicitly changes the release criteria.
4. Continue to treat English docs as canonical for safety, deployment, security, and release wording.
5. Keep #24/#25 as v0.1 release blockers until release notes and copied/disposable-data runtime evidence are complete.

## Suggested / created GitHub issues

Created:

- #29 — Add localization glossary for accounting terms (`documentation`, `audit`, `post-MVP`, `good-first-issue`).

Suggested but not created:

- No separate issue for full Russian README translation; current docs explicitly say the Russian page is a starter reference and may lag English.
- No separate issue for backend/API localization; current localization docs explicitly list backend/API error localization as a non-goal.

## What not to do next

- Do not publish `v0.1.0-readonly` based on this localization audit.
- Do not start Phase 70 automatically.
- Do not expand controlled writes or make write mode easier to enable.
- Do not make Russian the default locale without manual safety/security terminology review.
- Do not claim complete localization, production readiness, audited security, broad compatibility, SaaS readiness, GnuCash replacement status, collaborative accounting, or safe write-mode support.
