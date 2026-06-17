# Issue #47 to #48 transaction-entry workflow transition

Date: 2026-06-17
Previous tracker: [#47 Owner real-book CREATE + PATCH app-created metadata-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/47)
New tracker: [#48 Owner transaction-entry workflow for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PRODUCT_WORKFLOW_SCOPE_OPENED_NO_MUTATION**

## #47 state

#47 remains open as the active mixed CREATE + PATCH app-created metadata-only operating-mode tracker.
Its first mixed session is owner-verified and policy v1 is documented.

Validated #47 evidence state:

- CREATE: 10 / 10 owner-confirmed in the first mixed session;
- PATCH: 5 / 5 owner-confirmed in the first mixed session;
- DELETE: 0;
- batch: 0;
- PATCH scope: description/memo metadata-only;
- PATCH targets: app-created transactions only;
- amount/account/split/date/currency unchanged checks passed;
- backup/read-back/audit/reset/probes were required and documented;
- Syncthing conflict-copy checks apply when the target is under Syncthing;
- GitHub/tracked evidence remains redacted-only;
- private details remain Telegram/local UI only.

#47 does not authorize mutation by itself. Fresh same-context owner/PM approval with exact counts is still
required before any future CREATE or PATCH session.

## Why #48 exists

The current owner workflow is too prompt-heavy for real use: the owner should not need to write long prompts or
manually compose fields for 10+ operations. #48 transitions from evidence/policy to a product task: a safe
owner-only transaction-entry workflow that accepts compact list/table/CSV-like input, validates it, previews it
privately, and requires exact CREATE count approval before any future mutation.

## #48 strict scope

#48 is strictly limited to:

- owner-only use;
- test copy or owner-selected real-book target only;
- compact text/table/CSV-like transaction input;
- parser/validator or planning docs for date, debit/source account, credit/destination account, amount,
  currency, description, and optional memo;
- preview before mutation;
- exact CREATE count approval;
- optional PATCH only for app-created transactions and only description/memo metadata-only;
- target preflight before future mutation;
- private preview and verification details only in Telegram/local UI;
- redacted-only GitHub/tracked reports.

## Forbidden in #48

#48 forbids:

- CREATE without explicit same-context owner approval;
- PATCH historical/manual transactions;
- PATCH amount/account/split/date/currency changes;
- PATCH balance-affecting fields;
- DELETE;
- batch mutation without an explicit future issue;
- unattended mutation;
- dogfood loops;
- public write beta;
- release/tag/package/image publication;
- production, stable, or security-audited claims;
- raw private paths, account names, descriptions, memos, amounts, GUIDs, books, backups, screenshots,
  tokens, keys, certs, or `.env` content in commits, GitHub issues, tracked reports, or CI logs.

## Acceptance criteria carried into #48

1. Define a safe owner input format.
2. Add parser/validator or planning docs for date, debit/source account, credit/destination account, amount,
   currency, description, and optional memo.
3. Add preview step before mutation.
4. Preview must show private details only in Telegram/local UI, not GitHub.
5. Reject ambiguous account matches unless owner resolves them.
6. Reject missing/invalid amount, currency, or date.
7. Require exact CREATE count approval.
8. Require target preflight.
9. Preserve #47 backup/read-back/audit/reset/probes, Syncthing conflict-copy checks if applicable, and
   redacted-only GitHub/tracked reports.
10. Add the private Telegram verification-list rule: correct human-readable columns, no swapped
    Date/GUID/Accounts/Description/Amounts, and compact numbered plain text if table formatting is risky.

## Transition safety summary

This transition task performed no CREATE, PATCH, DELETE, batch mutation, dogfood loop, release, tag, package,
image publication, public write beta, or production/stable/security-audited claim. It opened #48 and recorded
planning docs only.

## Exact next allowed step

The exact next allowed step is non-mutating #48 implementation planning or parser/validator/preview work that
keeps writes disabled by default. A future mutating run remains blocked until same-context owner approval states
the target, exact CREATE count from a private preview, optional PATCH count if any, and #47-compatible safety
requirements.
