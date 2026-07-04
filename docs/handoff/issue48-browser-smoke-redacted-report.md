# Issue #48 browser smoke redacted report

Date: 2026-07-04
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **PASS**

## Scope

This report covers a redacted browser smoke execution for `/transactions/new` against a safe local/test context.
It does not authorize or execute CREATE, PATCH, DELETE, or batch mutation.

Runtime posture:

- `APP_ENV=test` local posture.
- `GNUCASH_WRITES_ENABLED=false`.
- Local admin bootstrap and local copied test GnuCash SQLite fixture only.
- App metadata database was local/ephemeral for this smoke.
- No private/original/working/only-copy book target was used.
- No screenshots were committed or attached.

## Browser smoke result

Browser smoke verdict: **PASS**

Required smoke checklist: **20 passed / 0 failed**.

Automation assertion detail: **22 passed / 0 failed** because the no-mutation error copy and disabled Create state were checked in multiple UI states.

## Endpoint/write boundary observed

Allowed preview endpoint used:

- `POST /books/{book_id}/transactions/create-preview`

Observed transaction-preview POSTs during the successful browser smoke:

- invalid date preview: safe `422` validation response;
- zero amount preview: safe `422` validation response;
- missing description preview: safe `422` validation response;
- valid preview: safe `200` preview response.

Observed mutation boundary:

- no CREATE route invoked;
- no PATCH route invoked;
- no DELETE route invoked;
- no batch route invoked;
- no active mutation-capable control became enabled;
- browser-observed mutation-capable requests outside preview/login: `0`.

## Redacted browser observations

- `/transactions/new` loaded after local login and remained available with writes disabled.
- Active book selector was visible.
- Preview-only/no-write warning was visible.
- Disabled Create explanation was visible.
- Source/debit account search filtered visible options.
- Destination/credit account search filtered visible options.
- Search text was not submitted as the final account reference; submitted account values came from selectors.
- Same-account source/destination selection was blocked before preview submit.
- Invalid date produced a field-level date error plus the safe top summary.
- Zero amount produced a field-level amount error plus the safe top summary.
- Missing description produced a field-level description error plus the safe top summary.
- Every tested error state included `No CREATE/PATCH/DELETE/batch executed`.
- Valid safe local preview rendered normalized preview metadata and fields, including `preview_only`, `create_count`,
  source/destination accounts, amount/currency, date, description, memo, and `Create remains disabled in this slice`.
- Create remained disabled/inert after valid preview.
- Narrow/mobile viewport check passed: sections stacked, account selectors remained readable, preview text wrapped,
  disabled Create explanation remained visible, and no obvious horizontal overflow was observed.

## UI bugs found

None.

No non-mutating UI fix was required during this smoke.

## Redaction confirmation

This report intentionally omits raw private paths, account names, book names beyond generic test context,
descriptions, memos, amounts, GUIDs, screenshots, tokens, keys, certs, and `.env` content.

## Safety summary

This smoke performed no CREATE, PATCH, DELETE, batch mutation, private-book dogfood, release, tag, package,
image publication, public write beta, or production/stable/security-audited claim.

Exact next allowed step: another non-mutating #48 hardening slice if desired, such as adding this browser-smoke
assertion harness to tracked tooling with redacted output. Any future CREATE still requires fresh same-context owner
approval with exact CREATE count and #47-compatible safety requirements.
