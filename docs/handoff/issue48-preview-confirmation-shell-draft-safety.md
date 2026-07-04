# Issue #48 preview confirmation shell and draft-safety slice

Date: 2026-07-04
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PREVIEW_ONLY_CONFIRMATION_SHELL_NO_MUTATION**

## Scope

This is a non-mutating product UI slice for `/transactions/new`. It keeps the page preview-only and does not
authorize or execute CREATE, PATCH, DELETE, or batch mutation.

The route still submits only to the non-mutating `POST /books/{book_id}/transactions/create-preview` endpoint.
The Create/Future Create controls remain disabled and non-submitting.

## Product improvements

- Added a post-preview confirmation shell that shows how the future owner-approved CREATE review step will look
  without enabling any write action.
- Added a local-only “I reviewed this local preview” checkbox. It has no submitted field name and cannot enable a
  CREATE action.
- Added a disabled Future Create control in the confirmation shell so the future workflow shape is visible while
  preserving the no-write boundary.
- Added stale-preview detection: if form fields change after a successful preview, the UI warns that the previous
  preview is stale and requires running Preview again before any future approval step.
- Added a Clear preview / start over link that reloads `/transactions/new` instead of persisting private draft data.
- Added account-selector count helpers showing how many selectable accounts match each source/destination filter.
- Expanded selected-account summaries with account type and currency so long account paths are easier to verify on
  browser/mobile layouts.

## Guard coverage

`npm run test:transaction-entry-preview` now checks:

- confirmation-shell copy and markup are present;
- local draft-change tracking exists;
- stale previews reset the local reviewed state;
- the confirmation checkbox is local UI only;
- Future Create remains a disabled `type="button"` control;
- Clear preview / start over exists without browser storage persistence;
- no `localStorage` or `sessionStorage` is used for private transaction drafts;
- account filter counts and selected-account type summaries are present;
- the preview action remains the only transaction submission target for `/transactions/new`.

## Redacted browser smoke

A local browser smoke was run against a safe synthetic/test context with `APP_ENV=test` and
`GNUCASH_WRITES_ENABLED=false`.

Result: **PASS**.

Redacted assertions:

- page loaded with the preview-only/no-write warning and disabled Create control;
- account filter counts rendered for source and destination selectors;
- selected account summaries rendered account type/currency context;
- one preview form POST rendered the normalized preview and confirmation shell;
- the Future Create control remained disabled and non-submitting;
- the local preview-reviewed checkbox changed only local UI state;
- changing a form field after preview rendered the stale-preview warning and disabled the reviewed checkbox;
- Clear preview / start over remained a link to `/transactions/new`;
- narrow/mobile viewport had no obvious horizontal overflow and kept confirmation/stale/count UI visible;
- browser-observed mutation-capable transaction requests outside the preview form action: `0`.

## Safety summary

This slice performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package, image
publication, public write beta, or production/stable/security-audited claim.

Future CREATE still requires fresh same-context owner approval with exact CREATE count, enabled write gates, and
#47-compatible backup/read-back/audit/reset/probe requirements. DELETE, batch, historical/manual mutation, and
amount/account/split/date/currency edits remain forbidden.
