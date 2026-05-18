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

Russian safety copy was written manually. Do not machine-translate new safety warnings without human review.

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
