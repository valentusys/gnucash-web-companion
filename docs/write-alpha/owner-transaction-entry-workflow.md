# Owner transaction-entry workflow for CREATE + optional PATCH app-created metadata

Issue: [#48 Owner transaction-entry workflow for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Status: **PLANNING_SCOPE_ONLY_NO_MUTATION**. This document does not authorize mutation by itself.

## Purpose

#47 validated the first mixed CREATE + PATCH app-created metadata-only session and documented policy v1.
The next product task is convenience: the owner should not need to write long prompts or manually compose
fields for 10+ real operations. #48 defines a safe owner-only workflow for entering operations as a compact
list/table/CSV-like text, seeing a private preview, and approving the exact CREATE count before any future
mutation.

## Strict scope

#48 is limited to owner-only transaction-entry workflow planning and/or implementation.

Allowed future target classes, only after fresh same-context owner approval:

- test copy;
- owner-selected real-book target.

Allowed future operation classes, only after fresh same-context owner approval:

- CREATE after parser/validator success, target preflight, private preview, and exact CREATE count approval;
- optional PATCH only for app-created transactions;
- optional PATCH scope only description/memo metadata-only.

## Forbidden operations and claims

#48 forbids:

- CREATE without explicit same-context owner approval;
- PATCH of historical/manual transactions;
- PATCH amount/account/split/date/currency changes;
- PATCH of any balance-affecting field;
- DELETE;
- batch mutation unless a future issue explicitly authorizes batch semantics;
- unattended mutation;
- dogfood loops;
- public write beta;
- release/tag/package/image publication;
- production, stable, or security-audited claims;
- committing or posting raw private paths, account names, descriptions, memos, amounts, GUIDs, books,
  backups, screenshots, tokens, keys, certs, or `.env` content.

## Safe owner input format

The owner input format should be compact, explicit, and easy to paste from Telegram or a local text editor.
The recommended planning format is pipe-separated text with a header row:

```text
date | debit | credit | amount | currency | description | memo
YYYY-MM-DD | <source account alias/name> | <destination account alias/name> | <decimal amount> | <ISO code> | <text> | <optional text>
```

CSV-like input may be accepted later if the same field semantics and validation rules are preserved. The
parser must not infer missing financial fields from descriptions or prior rows.

## Parser and validator requirements

The parser/validator must produce either a rejected plan or a normalized private preview. It must validate:

1. **Date** — required; parse only an explicit date format selected by the implementation plan, preferably
   `YYYY-MM-DD`; reject missing, invalid, or ambiguous dates.
2. **Debit/source account** — required; resolve against the selected target's account list; reject missing,
   placeholder, inaccessible, or ambiguous matches unless the owner resolves them.
3. **Credit/destination account** — required; resolve with the same rules as debit/source account.
4. **Amount** — required decimal string; reject missing, zero if not explicitly supported, invalid decimal,
   float-derived, range-invalid, or locale-ambiguous values.
5. **Currency** — required; reject missing, unsupported, or account-incompatible currency values; do not fake
   conversion.
6. **Description** — required unless a future issue explicitly permits blank descriptions; reject values that
   cannot be safely previewed or audited.
7. **Memo** — optional metadata only; if present, preserve it as text and include it in private preview.

Account matching must be fail-closed. If two or more candidate accounts can match the owner-provided text, the
workflow must stop and ask the owner to resolve the exact account before any mutation.

## Preview-before-mutation workflow

The intended future flow is:

1. Owner selects target class and target handle in the same context.
2. Tool runs target preflight and records only redacted readiness in tracked/GitHub output.
3. Owner provides compact transaction input.
4. Parser validates every row and account resolution.
5. System returns a private preview in Telegram/local UI only.
6. Owner approves in the same context with the exact CREATE count.
7. Only then may a future approved task execute individual CREATE operations, one at a time.

The preview must include enough private detail for the owner to verify the plan, but those private details must
not be copied to GitHub issues, commits, tracked reports, or CI logs.

## Exact CREATE count approval

A future mutating task must require approval wording that includes the exact CREATE count derived from the
preview, for example: `approve CREATE count N for this target and this preview`. Approval for `N` rows must not
be reused if parsing changes, rows are added/removed, account resolution changes, or target preflight is rerun
against a different target.

## Optional PATCH boundary

Optional PATCH remains #47-compatible:

- only app-created transactions;
- exact app-created identity proof before every PATCH;
- only description/memo metadata-only;
- no historical/manual transaction mutation;
- no amount/account/split/date/currency/balance-affecting changes;
- read-back after PATCH must prove unchanged financial fields.

## Preserve #47 policy

Every future #48 mutating session must preserve #47 policy:

- backup before each CREATE/PATCH unless the same-context owner approval explicitly approves a safer policy;
- read-back after each CREATE/PATCH;
- redacted audit evidence with opaque refs only;
- default-disabled reset after session;
- disabled-write probes for validate/preflight, CREATE, PATCH, and DELETE route families when available;
- Syncthing conflict-copy checks before/after if the target is under Syncthing;
- redacted-only GitHub/tracked reports;
- private details only in Telegram/local UI.

## Private Telegram verification-list rule

Private verification lists must use correct human-readable columns and must not swap Date, GUID, Accounts,
Description, Memo, or Amounts.

For owner verification, prefer compact numbered plain text if a Markdown table may wrap or shift columns:

```text
1. Date: <date>; GUID: <guid>; Debit: <account>; Credit: <account>; Amount: <amount currency>;
   Description: <description>; Memo: <memo or empty>
```

GitHub/tracked reports must remain redacted-only and must not include those private details.

## Acceptance checklist

- [ ] Safe owner input format defined.
- [ ] Parser/validator or planning docs cover date, debit/source account, credit/destination account, amount,
      currency, description, and optional memo.
- [ ] Preview step exists before mutation.
- [ ] Preview is private Telegram/local UI only, not GitHub/tracked output.
- [ ] Ambiguous account matches are rejected unless owner resolves them.
- [ ] Missing/invalid amount, currency, or date is rejected.
- [ ] Exact CREATE count approval is required.
- [ ] Target preflight is required.
- [ ] #47 backup/read-back/audit/reset/probes and Syncthing conflict-copy rules are preserved.
- [ ] Redacted-only GitHub/tracked reports are preserved.
- [ ] Private verification-list column rule and numbered plain-text fallback are documented.

## Current non-mutating state

This document is a transition/planning artifact. No CREATE, PATCH, DELETE, dogfood loop, release, tag,
package, image publication, public write beta, or production/stable/security-audited claim is made here.
