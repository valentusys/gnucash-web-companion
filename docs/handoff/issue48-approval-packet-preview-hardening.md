# Issue #48 approval-packet preview hardening

Date: 2026-07-05
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PREVIEW_ONLY_APPROVAL_PACKET_NO_MUTATION**

## Scope

This is a non-mutating product UI and backend-test hardening slice for `/transactions/new` and the backend
`create-preview` path. It keeps the web companion workflow preview-only and does not authorize or execute CREATE,
PATCH, DELETE, or batch mutation.

## Product improvements

- Added an approval-packet panel after a valid preview so the owner can review the future same-context CREATE
  approval shape before any write-capable implementation exists.
- The approval packet summarizes the future target book, `create_count = 1`, source/debit account,
  destination/credit account, amount/currency, date, description, memo, and a safety checklist.
- Added a copy button for a redacted approval template that uses placeholders only. It does not copy account names,
  descriptions, memos, amounts, GUIDs, book paths, screenshots, or secrets.
- Preserved disabled/non-submitting Create and Future Create controls. No active CREATE action or mutation endpoint was
  added.
- Improved no-selectable-accounts and field-level validation copy so real users get safer guidance without exposing
  runtime internals or implying writes.

## Backend/test hardening

Backend preview coverage now additionally checks:

- missing book rejects safely before preview open or mutation metadata;
- view-only users cannot use the owner-only preview path;
- all-placeholder/no-selectable-account books fail with an explicit safe message;
- unknown account IDs and credit-account currency mismatch are rejected;
- high-precision decimal strings and trailing zeros are preserved as strings;
- preview read errors return path-safe responses without exposing runtime internals;
- preview success does not create audit rows or app-created ownership metadata;
- preview does not call write gates, write service, audit helpers, ownership mutation helpers, backup/audit field
  helpers, or lock-detail helpers.

## Guard coverage

`npm run test:transaction-entry-preview` now checks:

- approval-packet UI and no-write copy;
- placeholder-only approval template content;
- clipboard copy is limited to the safe template and does not write private preview values;
- no-selectable-account guidance exists;
- user-friendly field-error mapping remains present;
- `/transactions/new` still has only the preview action and `create-preview` remains the only transaction submission
  target.

## Safety summary

This slice performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package, image
publication, public write beta, or production/stable/security-audited claim.

Future CREATE still requires fresh same-context owner approval with exact CREATE count, enabled write gates, and
#47-compatible backup/read-back/audit/reset/probe requirements. DELETE, batch, historical/manual mutation, and
amount/account/split/date/currency edits remain forbidden.
