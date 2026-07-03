# Issue #48 transaction-entry preview accessibility/mobile smoke checklist

Date: 2026-07-04
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PREVIEW_ONLY_ACCESSIBILITY_MOBILE_SMOKE_NO_MUTATION**

## Scope

This is a non-mutating #48 hardening slice for the product web UI at `/transactions/new`. It does not authorize
or execute CREATE, PATCH, DELETE, or batch mutation. The page remains preview-only and still submits only to the
non-mutating `POST /books/{book_id}/transactions/create-preview` endpoint.

Future CREATE still requires fresh same-context owner approval, an exact CREATE count, enabled write gates, and
#47-compatible backup/read-back/audit/reset/probe requirements. DELETE, batch mutation, historical/manual
mutation, and amount/account/split/date/currency PATCH edits remain forbidden.

## Implementation hardening summary

- Added explicit `label for` / `id` pairs for book, date, source/debit search, source/debit selector,
  destination/credit search, destination/credit selector, amount, currency, description, and memo.
- Linked field hints and field-level errors with `aria-describedby` where the route renders them.
- Linked the form and disabled Create button to the preview-only/no-write warning and disabled-Create explanation.
- Kept the safe error summary at the top with no raw private paths, secrets, or runtime internals and with
  `No CREATE/PATCH/DELETE/batch executed` copy.
- Kept source/destination account search as a filter only; submitted account references remain controlled account IDs.
- Added amount input polish with decimal input mode and a decimal-string pattern marker while keeping backend
  validation authoritative.
- Kept date explicit and currency conservative with a three-letter-code marker and no conversion claim.
- Added narrow-screen layout polish with `min-w-0`, stacked sections, max-width controls, and breakable long
  selected account/preview text.

## Redacted manual/browser smoke checklist

Run this only against safe local/test context unless a future task explicitly authorizes a different target. Do not
copy private account names, descriptions, memos, amounts, GUIDs, book paths, screenshots, backups, tokens, keys,
certs, or `.env` content into GitHub/tracked docs.

- [ ] Start the app with `GNUCASH_WRITES_ENABLED=false`.
- [ ] Open `/transactions/new`.
- [ ] Confirm the page loads and the active book selector is visible.
- [ ] Confirm the preview-only/no-write warning is visible.
- [ ] Confirm the disabled Create explanation is visible.
- [ ] Confirm source/debit account search filters visible options.
- [ ] Confirm destination/credit account search filters visible options.
- [ ] Confirm search text is not submitted as the account reference; final values come from account selectors.
- [ ] Confirm source and destination cannot be submitted as the same account.
- [ ] Submit an invalid date and confirm a safe field-level date error plus the safe top summary.
- [ ] Submit an invalid/zero amount and confirm a safe field-level amount error plus the safe top summary.
- [ ] Submit a missing/invalid description and confirm a safe field-level description error plus the safe top summary.
- [ ] Confirm every error state includes `No CREATE/PATCH/DELETE/batch executed`.
- [ ] Fill a valid preview form and confirm the normalized preview renders.
- [ ] Confirm the preview shows `preview_only`, `create_count`, source/destination accounts, amount/currency,
  date, description, memo, and `Create remains disabled in this slice`.
- [ ] Confirm the Create button remains disabled/inert after preview.
- [ ] Confirm no CREATE/PATCH/DELETE/batch operation is executed.
- [ ] Check a narrow/mobile viewport: sections stack cleanly, account selectors remain readable, preview text wraps,
  and the disabled Create explanation remains visible without horizontal overflow.
- [ ] Confirm no private details are added to GitHub issues, commits, tracked docs, CI logs, or screenshots.

## Verification guards

`npm run test:transaction-entry-preview` covers the static preview-only boundary plus accessibility/mobile markers:
explicit labels, `aria-describedby` linkages, no-write warning, disabled Create explanation, field-level errors,
account search controls, same-account prevention, decimal amount marker, mobile/narrow layout markers, and absence
of active create/write actions.

`npm run test:auth-routes` remains aligned with the preview-only route policy.

## Safety summary

This slice performs no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package, image
publication, public write beta, or production/stable/security-audited claim.

Exact next allowed step: another non-mutating #48 hardening slice, such as browser/manual smoke execution against a
redacted safe local/test context or additional accessibility guard coverage. Any future CREATE still requires fresh
same-context owner approval with exact CREATE count and #47-compatible safety requirements.
