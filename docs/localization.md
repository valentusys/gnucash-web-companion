# Russian localization and i18n foundation

English remains the canonical language for product documentation and safety wording. Russian localization is a convenience layer and may lag behind English until reviewed.

## Current approach

The web UI uses a small in-repository message catalog instead of adding a heavy i18n dependency during pre-alpha:

- `apps/web/src/lib/i18n/messages.ts` defines supported locales and typed message keys.
- `apps/web/src/lib/i18n/index.ts` exposes locale helpers and server-side cookie lookup.
- `apps/web/src/routes/locale/+server.ts` stores the chosen locale in the `ui_locale` cookie.
- English (`en`) is the default locale.
- Russian (`ru`) is opt-in through the UI language switcher.

This keeps the Phase 52 scope narrow while leaving room to replace the catalog with a dedicated SvelteKit i18n library later if the translation surface grows.

## Localized surface in Phase 52

Phase 52 intentionally localizes only a small reviewed set:

- login title, helper text, username/password labels, submit button;
- authenticated navigation labels;
- read-only safety banner label/message;
- dashboard title;
- accounts section/title;
- transactions section/title.

Russian safety copy was written manually. Do not machine-translate new safety warnings without human review.

## Non-goals

- Russian is not the default locale.
- v0.1 is not blocked on complete translation.
- Backend/API error messages are not localized yet.
- Full documentation translation is not promised.
- Controlled-write scope is not expanded by localization work.

## Adding strings

1. Add a typed key to `MessageKey` in `apps/web/src/lib/i18n/messages.ts`.
2. Add English and Russian values for the key.
3. Use `t(locale, 'key')` from `$lib/i18n` in Svelte components.
4. Keep English wording canonical and manually review any safety/security/accounting text before adding Russian.
5. Run frontend checks before committing.
