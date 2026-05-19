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

Russian safety copy was written manually. Do not machine-translate new safety warnings without human review.

## Accounting and safety glossary

English is canonical. Use these Russian terms consistently in the UI/docs when a narrow Russian slice is added:

| Canonical English | Preferred Russian | Notes |
| --- | --- | --- |
| read-only / read-only by default | read-only / только чтение / только на чтение по умолчанию | Keep `read-only` where it reinforces the product boundary; do not translate it into a weaker “view mode” claim. |
| GnuCash Desktop remains the authoritative editor | GnuCash Desktop остаётся главным редактором | Use for all write-boundary warnings. Do not imply the web UI is an editor in v0.1.x. |
| not production-ready | не готово для production / не production-ready | Keep explicit for release/deployment warnings. |
| not security-audited | не проходило security audit / не security-audited | Do not soften into “basic security included”. |
| controlled writes are experimental and disabled by default | controlled writes экспериментальны и отключены по умолчанию | Controlled writes are post-MVP; do not call them normal editing. |
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
- Backend/API error messages are not localized yet.
- Full documentation translation is not promised.
- Controlled-write scope is not expanded by localization work.

## Adding strings

1. Add a typed key to `MessageKey` in `apps/web/src/lib/i18n/messages.ts`.
2. Add English and Russian values for the key.
3. Use `t(locale, 'key')` from `$lib/i18n` in Svelte components.
4. Keep English wording canonical and manually review any safety/security/accounting text before adding Russian.
5. For UI pages that already have route/static checks, update `apps/web/scripts/test-auth-routes.mjs` or a more specific test so locale switching and safety wording are covered.
6. Run frontend checks before committing.
