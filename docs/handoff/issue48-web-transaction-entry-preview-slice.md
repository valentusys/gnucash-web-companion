# Issue #48 web transaction-entry preview slice

Date: 2026-06-17
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PREVIEW_ONLY_IMPLEMENTED_NO_MUTATION**

## What changed

Implemented the first non-mutating #48 implementation slice for the product web UI path:

- backend single-transaction CREATE preview endpoint;
- browser/mobile transaction-entry preview form;
- preview panel showing normalized private preview in local app UI/runtime;
- CREATE/Submit mutation action disabled in the UI;
- static frontend guard script for preview-only form expectations.

## Backend slice

Added a non-mutating endpoint:

```text
POST /books/{book_id}/transactions/create-preview
```

Request fields:

- date;
- debit/source account ID;
- credit/destination account ID;
- amount as decimal string;
- currency;
- description;
- optional memo.

The endpoint:

- works with `GNUCASH_WRITES_ENABLED=false`;
- requires owner access;
- opens the selected book read-only to resolve account display paths;
- validates required date/account/amount/currency/description fields;
- rejects invalid date;
- rejects zero/invalid/missing amount;
- rejects unsupported account currency for the requested currency;
- rejects same-account debit/credit;
- returns `preview_only=true` and `create_count=1`;
- never constructs the write service, lock, backup, audit, or mutation path.

## Frontend slice

Updated `/transactions/new` from an enabled-write CREATE form into a preview-only web form.

The UI includes:

- date field;
- debit/source account selector;
- credit/destination account selector;
- amount field;
- currency field;
- description field;
- optional memo field;
- preview button;
- preview-only/no-write warning;
- normalized preview panel;
- disabled Create button.

The transactions list now exposes a preview entry point even when writes are disabled, clearly labeled as
preview-only.

## Tests and guards

Added backend coverage for:

- valid preview returns normalized preview and `create_count=1`;
- missing date rejected;
- invalid date rejected;
- missing debit account rejected;
- missing credit account rejected;
- same debit/credit account rejected;
- missing amount rejected;
- invalid amount rejected;
- zero amount rejected;
- amount string precision preserved without float conversion;
- missing currency rejected;
- unsupported currency rejected;
- missing description rejected;
- preview endpoint does not call mutation/write path;
- preview works with writes disabled by default.

Added frontend static preview guard:

```text
npm run test:transaction-entry-preview
```

It checks that the form exposes required fields, shows preview-only state, includes a disabled Create control,
uses the preview endpoint, and does not include a create action/path.

## 2026-07-04 reconciliation

The implementation and static guards were reconciled against the preview-only #48 policy after review found
stale write-enabled expectations in frontend guard coverage. The route remains reachable with
`GNUCASH_WRITES_ENABLED=false`, loads books/accounts through read-only active-book context, and exposes only a
`preview` form action backed by `POST /books/{book_id}/transactions/create-preview`.

The static frontend guard now also checks:

- `package.json` exposes `npm run test:transaction-entry-preview`;
- `/transactions/new` route files exist;
- the transactions list exposes `/transactions/new` outside the `writesEnabled` block;
- the entry point and form are clearly labeled preview-only/no-write;
- old `create`/`validate` actions, `/transactions/validate`, and bare `/transactions` mutation calls are absent.

The broader auth/static route guard was synchronized so it no longer requires the obsolete write-enabled
redirect/acknowledgement flow for `/transactions/new`.

## Safety summary

This slice performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package,
image publication, public write beta, or production/stable/security-audited claim.

Tracked/GitHub reporting remains redacted-only. Private transaction details are local app UI/runtime data only.
Telegram/agent compact input remains a development/test helper only, not the product workflow.

## Exact next allowed step

The exact next allowed step is another non-mutating #48 hardening slice: improve account selector UX,
preview error rendering, and/or backend preview validation while keeping writes disabled by default and no
CREATE/PATCH/DELETE execution. Any future CREATE requires fresh same-context owner approval with exact CREATE
count and #47-compatible safety requirements.
