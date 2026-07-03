# Issue #48 web transaction-entry preview UX hardening

Date: 2026-07-04
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PREVIEW_ONLY_UX_HARDENED_NO_MUTATION**

## Scope

This is a non-mutating #48 hardening slice for the existing browser/mobile transaction-entry preview form.
It does not authorize or execute CREATE, PATCH, DELETE, or batch mutation.

## What changed

Hardened the preview-only `/transactions/new` user experience:

- added lightweight search/filter inputs for debit/source and credit/destination account selectors;
- kept final account submission as selected account IDs from `<select>` controls, not free-text account names;
- displayed full account paths and currency in account selector options;
- kept placeholder/hidden accounts excluded in server load and UI selector logic;
- added same-account client prevention before preview submit;
- improved preview error rendering with a safe top summary and field-level errors where possible;
- kept fallback error copy safe for unexpected API failures;
- expanded the preview panel to show `preview_only`, `create_count`, source/destination accounts,
  amount/currency, date, description, memo, and that Create remains disabled in this slice.

## Backend/mutation boundary

The backend preview endpoint remains:

```text
POST /books/{book_id}/transactions/create-preview
```

The endpoint remains non-mutating and works while `GNUCASH_WRITES_ENABLED=false`. This slice did not add any
write service, write lock, backup, audit, ownership, CREATE, PATCH, DELETE, or batch path to `/transactions/new`.

The frontend server action only calls `create-preview`; it does not call `/transactions/validate` or a bare
`/transactions` mutation endpoint.

## Tests and guards

The frontend static guard `npm run test:transaction-entry-preview` now checks:

- `/transactions/new` route files exist;
- preview-only/no-write copy exists;
- source/destination selectors exist;
- account search/filter inputs exist;
- free-text search is not the submitted account reference;
- placeholder/hidden account prevention is represented in server/UI logic;
- same-account prevention is represented;
- Create remains disabled/inert;
- no active create action/path exists;
- `/transactions/create-preview` is the only transaction submission target;
- safe error summary and no-write error copy exist;
- field-level error rendering exists;
- the transactions list still exposes the preview entry point outside `writesEnabled`.

The broader `npm run test:auth-routes` guard remains aligned with preview-only behavior.

## Safety summary

This slice performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package,
image publication, public write beta, or production/stable/security-audited claim.

Tracked and GitHub reporting remain redacted-only. Private account names, transaction descriptions, memos,
amounts, GUIDs, book paths, backups, screenshots, tokens, keys, certs, and `.env` content were not posted.

## Exact next allowed step

The exact next allowed step is another non-mutating #48 hardening slice, such as preview-panel polish,
accessibility copy, or test coverage improvements. Any future CREATE still requires fresh same-context owner
approval with exact CREATE count and #47-compatible backup/read-back/audit/reset/probe requirements.
