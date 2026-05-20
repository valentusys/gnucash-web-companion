# Russian localization and i18n foundation

English remains the canonical language for product documentation and safety wording. Russian localization is a convenience layer and may lag behind English until reviewed.

## Current approach

The web UI uses a small in-repository message catalog instead of adding a heavy i18n dependency during pre-alpha:

- `apps/web/src/lib/i18n/messages.ts` defines supported locales and typed message keys.
- `apps/web/src/lib/i18n/index.ts` exposes locale helpers and server-side cookie lookup.
- `apps/web/src/routes/locale/+server.ts` stores the chosen locale in the `ui_locale` cookie.
- English (`en`) is the default locale.
- Russian (`ru`) is opt-in through the UI language switcher.

This keeps localization narrow while leaving room to replace the catalog with a dedicated SvelteKit i18n library later if the translation surface grows.

## Localized surface

Phase 52 intentionally localized only a small reviewed set:

- login title, helper text, username/password labels, submit button;
- authenticated navigation labels;
- read-only safety banner label/message;
- dashboard title;
- accounts section/title;
- transactions section/title.

Phase 93 extended the same limited approach, still without promising complete translation:

- `/books` navigation label now uses the message catalog in desktop and mobile navigation;
- `/books` metadata page headings, helper copy, read-only badges, access labels, empty state, and read-only safety note now use English/Russian catalog strings;
- `README.ru.md` was refreshed to describe the real but limited Russian UI surface.

Phase 113 adds a glossary and one high-value transaction UI slice:

- transaction filter headings/help, active filter summary labels, date preset helper copy, split reconciliation state labels, reset action, and CSV export helper/button copy use the English/Russian catalog;
- the same URL-only filter behavior remains in place: no search strings, account IDs, dates, amounts, or state filters are stored in `localStorage`/`sessionStorage`;
- Russian copy keeps the read-only/export safety meaning instead of implying editing, production readiness, or complete translation.

Phase 126 updates that narrow transaction search label to mention description, transaction notes, and split memo semantics. The Russian placeholder keeps the GnuCash terms `notes` and `split memo` explicit because the underlying fields are technical GnuCash concepts and the translation surface remains partial.

Phase 149 covers the new read-only UX copy added after `v0.1.4-readonly` without turning localization into a full-app rewrite:

- account-tree filtering labels, counts, empty states, and loading copy now use English/Russian catalog strings;
- dashboard/reporting limitation labels for conservative totals, reporting basis, and currency-conversion status now use the catalog;
- transaction detail and split-readability labels, helper copy, empty split state, reconciliation labels, and hidden-by-default write-alpha DELETE warnings now use the catalog;
- `/books`, transaction list/filter/export, and the app-shell read-only/current-book banner remain covered by the existing catalog entries;
- English remains canonical, Russian remains partial/opt-in, and the safety wording continues to state read-only/default-disabled/write-alpha boundaries conservatively.

Phase 159 reduces release-critical partial-localization friction without claiming full translation:

- dashboard report cards, dashboard drilldown helper copy, recent transactions, expenses-by-account, and cashflow labels now use English/Russian catalog entries;
- `/scheduled` title, safety copy, URL-only filters/sorting, safe metadata labels, and empty states now use the catalog;
- the unauthenticated landing page subtitle/sign-in action uses the catalog fallback while `/login`, `/accounts`, `/transactions`, `/books`, and the app-shell safety banner remain covered by earlier catalog entries;
- `t(locale, key, replacements)` now supports simple named interpolation for localized counts and recurrence summaries;
- Russian remains partial/opt-in, English remains canonical, and no backend/API localization rewrite or production/readiness claim was added.

Phase 169 closes the most visible RU/EN mismatch on recent release-critical read-only/operator paths without claiming complete localization:

- login form validation, invalid-credentials, service-unavailable, and first-run auth-configuration failures now use the English/Russian catalog based on the existing `ui_locale` cookie;
- the global error component/page now localize 403, 404, generic API/network, and 5xx first-run operator guidance, including safe `/health`, local `.env`, and book-volume next actions;
- existing CSV export states and book-context recovery notices remain catalog-backed from earlier phases;
- English remains canonical, Russian remains partial/opt-in, and backend/API localization is still not a full rewrite.

Phase 208 polishes the operator-facing safety slice for the current write-alpha cycle without changing backend behavior or claiming complete localization:

- app-shell read-only status copy now states pre-alpha, default `GNUCASH_WRITES_ENABLED=false`, not production-ready, not security-audited, hidden-by-default write-alpha, and disposable-copy-only boundaries in English/Russian;
- `/books` keeps the write-alpha audit evidence link catalog-backed while preserving app-metadata-only, no-management, and private-path-redacted wording;
- the write-mode warning/new-transaction acknowledgement and final browser confirmation are catalog-backed and keep `APP_ENV=test`, disposable/test-copy, backup/audit/lock-release, never source/only-copy, and never-only-real-book constraints;
- `/books/write-alpha-audit` now uses catalog-backed EN/RU operator labels and warning copy, while the endpoint/API payloads remain English/backend-defined and redacted;
- static route checks pin unsafe-claim guards for pre-alpha, not production-ready, not security-audited, default-disabled, and disposable-only wording, and continue to reject `localStorage`/`sessionStorage` in sensitive UI paths.

Phase 219 adds a small glossary-backed catalog/test layer for release-critical accounting and operator-safety wording:

- `apps/web/src/lib/i18n/safety-glossary.ts` catalogs canonical English, preferred Russian wording, notes, and the message keys that carry each safety term;
- frontend static route checks now pin read-only default, `GNUCASH_WRITES_ENABLED=false`, write-alpha disposable/test-copy boundary, not production-ready, not security-audited, no currency conversion, and GnuCash Desktop authoritative-editor terms in EN/RU;
- static checks reject softened production/security/safe-write claims and continue to reject new `localStorage`/`sessionStorage` use in the localization slice;
- `/books` title/copy now says book metadata instead of broad “management”, preserving the no upload/delete/default-changing/registry-edit boundary;
- English remains canonical, Russian remains partial/opt-in, and no backend API localization rewrite or product behavior change was added.

Russian safety copy was written manually. Do not machine-translate new safety warnings without human review.

## Accounting and safety glossary

English is canonical. Use these Russian terms consistently in the UI/docs when a narrow Russian slice is added:

| Canonical English | Preferred Russian | Notes |
| --- | --- | --- |
| read-only / read-only by default | read-only / только чтение / только на чтение по умолчанию | Keep `read-only` where it reinforces the product boundary; do not translate it into a weaker “view mode” claim. |
| `GNUCASH_WRITES_ENABLED=false` | `GNUCASH_WRITES_ENABLED=false` | Keep the exact config flag visible when explaining the default-disabled write boundary. |
| GnuCash Desktop remains the authoritative editor | GnuCash Desktop остаётся главным редактором | Use for all write-boundary warnings. Do not imply the web UI is an editor in v0.1.x. |
| not production-ready | не готово для production / не production-ready | Keep explicit for release/deployment warnings. |
| not security-audited | не проходило security audit / не security-audited | Do not soften into “basic security included”. |
| controlled writes are experimental and disabled by default | controlled writes экспериментальны и отключены по умолчанию | Controlled writes are post-MVP; do not call them normal editing. |
| write-alpha disposable/test-copy boundary | write-alpha только для disposable/test copies | Use for enabled-write warnings; never imply real/private or only-copy book readiness. |
| not safe for real/private or only-copy books | не безопасно/не готово для real/private или only-copy книг | Use when documenting write-alpha limitations; avoid “safe write” wording. |
| no currency conversion / no FX conversion | без конвертации валют / без FX-конвертации | Dashboard, drilldown, transaction, and CSV/export copy must not imply FX conversion. |
| transaction | транзакция | Use for GnuCash transactions. |
| split | split | Keep the GnuCash term when referring to split-level data such as memo or reconciliation state. |
| split memo | split memo | Avoid implying it is the same as transaction description. |
| split reconciliation state | состояние сверки split | Used by the transaction state filter. |
| unreconciled | не сверено | Maps to GnuCash split `n`. |
| cleared | очищено | Maps to GnuCash split `c`; do not translate as “удалено”. |
| reconciled | сверено | Maps to GnuCash split `y`. |
| voided | аннулировано | Maps to GnuCash split `v`; do not imply deletion. |
| CSV export | CSV export / экспорт CSV | Export is read-only and filtered; do not call it import/sync. |
| filtered view | отфильтрованный вид | Applies equally to list and CSV export. |
| partial translation | частичный перевод | State that Russian is incomplete and English remains canonical. |

## Non-goals

- Russian is not the default locale.
- English remains canonical for documentation, release notes, safety docs, and security docs.
- No claim of complete Russian translation is made.
- v0.1/v0.1.x maintenance is not blocked on complete translation.
- Backend/API payloads are not localized as a full rewrite; only selected web-facing release-critical proxy/error/login messages are localized.
- Full documentation translation is not promised.
- Controlled-write scope is not expanded by localization work.

## Adding strings

1. Add a typed key to `MessageKey` in `apps/web/src/lib/i18n/messages.ts`.
2. Add English and Russian values for the key.
3. Use `t(locale, 'key')` from `$lib/i18n` in Svelte components.
4. Keep English wording canonical and manually review any safety/security/accounting text before adding Russian.
5. For UI pages that already have route/static checks, update `apps/web/scripts/test-auth-routes.mjs` or a more specific test so locale switching and safety wording are covered.
6. Run frontend checks before committing.
