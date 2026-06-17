# Issue #48 re-scope to web transaction-entry UI

Date: 2026-06-17
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **WEB_UI_PRODUCT_SCOPE_NO_MUTATION**

## Correction

#48 was initially phrased too much like an owner sends compact text/CSV-like input to an agent. That is not the
product direction for `gnucash-web-companion`.

The project goal is a web companion application for GnuCash: browser/mobile UI over an existing GnuCash book.
The agent is a developer/tester, not the primary user-facing transaction-entry interface.

## Re-scoped #48 product target

#48 is now scoped to an owner-only web transaction-entry UI:

- browser/mobile transaction-entry form;
- CREATE through the app UI after preview/confirmation;
- optional PATCH through the app UI only for app-created transaction description/memo metadata;
- writes disabled by default;
- exact CREATE count remains 1 per form submit unless a future issue expands scope;
- target preflight and existing write gates preserved;
- private data stays in local app UI/runtime/private owner context;
- GitHub/tracked reports stay redacted-only.

## Desired implementation direction

### Backend

- Add or refine a non-mutating validate/preview endpoint for transaction create payloads.
- Preserve existing write disabled-by-default gates.
- Preserve target preflight before future mutation.
- Validate date, debit/source account, credit/destination account, amount, currency, description, and optional
  memo.
- Reject ambiguous account matches unless owner resolves them.
- Reject missing/invalid amount, currency, or date.
- Keep exact CREATE count at 1 per form submit unless a future issue expands scope.

### Frontend

- Add browser/mobile transaction-entry form.
- Fields: date, debit/source account selector/autocomplete, credit/destination account selector/autocomplete,
  amount string, currency, description, optional memo.
- Add preview/confirmation before CREATE.
- Keep layout mobile-friendly and accessible.

### Safety

- CREATE only after explicit UI confirmation.
- PATCH only app-created description/memo metadata if implemented.
- No DELETE.
- No batch.
- No amount/account/split/date/currency edit via PATCH at this stage.
- No historical/manual transaction mutation.
- No unattended mutation.
- No public write beta.
- No release/tag/package/image publication.
- No production, stable, or security-audited claims.

## Telegram/agent/local helper boundary

Telegram/agent compact input may remain useful only as development/test harness or local/debug/import-helper.
It must not be the main product workflow and must not become unattended batch mutation under #48.

Pipe/CSV-like helper input, if kept, must produce the same validated single-transaction payload semantics before
preview and must preserve redacted-only tracked reporting.

## Transition safety summary

This re-scope task performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag,
package, image publication, public write beta, or production/stable/security-audited claim.

## Exact next allowed implementation step

The exact next allowed step is non-mutating #48 implementation planning or code for the web UI path: backend
single-transaction validate/preview endpoint plus browser/mobile form and preview/confirmation flow, with writes
disabled by default and no CREATE/PATCH/DELETE execution.
