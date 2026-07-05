# Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata

Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Transition issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)
Status: **WEB_UI_PREVIEW_ONLY_SUFFICIENTLY_VALIDATED**. This document does not authorize mutation by itself.

## Product framing

`gnucash-web-companion` is a browser/mobile companion application for existing GnuCash books. The product goal
for #48 is therefore **not** a Telegram/agent bookkeeping workflow. The agent may be used as a developer/tester
and may help with local/debug harnesses, but the main user-facing transaction-entry interface must be the web
application.

#47 validated the first mixed CREATE + PATCH app-created metadata-only session and documented policy v1. #48
re-scopes the next step from prompt-heavy operator evidence into an owner-only web UI workflow for creating
transactions from a browser/mobile form, previewing them, and confirming before CREATE.

## Strict scope

#48 is limited to owner-only web transaction-entry workflow planning and/or implementation.

Allowed future target classes, only after fresh same-context owner approval for a mutating run:

- test copy;
- owner-selected real-book target.

Allowed future operation classes, only after fresh same-context owner approval for a mutating run:

- CREATE through the app UI after backend validation, preview, and explicit UI confirmation;
- optional PATCH through the app UI only for app-created transactions;
- optional PATCH scope only description/memo metadata-only.

Writes remain disabled by default. Opening or documenting #48 is not mutation approval.

## Desired implementation direction

### Backend

- Add or refine a validate/preview endpoint for a single transaction create payload.
- Preserve existing write disabled-by-default gates and `APP_ENV=test` write gating.
- Keep the preview endpoint non-mutating.
- Preserve target preflight before any future mutation.
- Keep exact CREATE count at **1 per form submit** unless a future issue explicitly expands this.
- Validate date, debit/source account, credit/destination account, amount, currency, description, and optional
  memo before preview/confirmation.
- Reject ambiguous account matches unless the owner resolves them in the UI.
- Reject missing/invalid amount, currency, or date.

### Frontend

- Add a browser/mobile transaction-entry form in the app UI.
- Include these fields:
  - date;
  - debit/source account selector or autocomplete;
  - credit/destination account selector or autocomplete;
  - amount field using string/Decimal semantics;
  - currency field;
  - description field;
  - optional memo field.
- Show a preview/confirmation step before CREATE.
- Make the layout mobile-friendly and accessible.
- Keep private transaction details in the local app UI/runtime only, not in GitHub/tracked reports.

### Optional PATCH UI

If implemented under #48, PATCH must remain #47-compatible:

- only app-created transactions;
- exact app-created identity proof before PATCH;
- description/memo metadata-only;
- no historical/manual transaction mutation;
- no amount/account/split/date/currency/balance-affecting changes;
- read-back after PATCH must prove unchanged financial fields.

## Forbidden operations and claims

#48 forbids:

- CREATE without explicit UI confirmation and future same-context owner approval for a mutating run;
- PATCH of historical/manual transactions;
- PATCH amount/account/split/date/currency changes;
- PATCH of any balance-affecting field;
- DELETE;
- batch mutation;
- unattended mutation;
- dogfood against a private book without explicit future approval;
- public write beta;
- release/tag/package/image publication;
- production, stable, or security-audited claims;
- committing or posting raw private paths, account names, descriptions, memos, amounts, GUIDs, books,
  backups, screenshots, tokens, keys, certs, or `.env` content.

## Web preview-before-mutation workflow

The intended future product flow is:

1. Owner opens the transaction-entry form in the web app.
2. Owner selects or confirms the target book context in the app.
3. Owner enters one transaction.
4. Backend validates the payload and returns a non-mutating preview.
5. UI shows the preview locally in the browser/mobile app.
6. Owner explicitly confirms the preview.
7. Only then may the app execute one routed CREATE operation, subject to enabled write gates and session scope.
8. App reads back the result, records audit evidence, and shows local/private result details.

The preview must include enough private detail for the owner to verify the plan, but those private details must
not be copied to GitHub issues, commits, tracked reports, or CI logs.

## Input field validation rules

The web form and backend preview must validate:

1. **Date** — required; prefer explicit `YYYY-MM-DD`; reject missing, invalid, or ambiguous dates.
2. **Debit/source account** — required; select by stable app account identity where possible; reject missing,
   placeholder, inaccessible, or ambiguous account matches.
3. **Credit/destination account** — required; same rules as debit/source account.
4. **Amount** — required decimal string; reject missing, zero if not explicitly supported, invalid decimal,
   float-derived, range-invalid, or locale-ambiguous values.
5. **Currency** — required; reject missing, unsupported, or account-incompatible currency values; do not fake
   conversion.
6. **Description** — required unless a future issue explicitly permits blank descriptions; preview exactly what
   will be written.
7. **Memo** — optional metadata only; if present, preserve it as text and include it in local/private preview.

Account selection should prefer explicit selectors/autocomplete over free-text matching. If free-text matching is
used anywhere, it must fail closed on ambiguous matches and require owner resolution before preview can become
confirmable.

## Optional local/debug/import-helper input

Pipe-separated or CSV-like compact text may remain useful as a **developer/local/debug/import-helper**, but it is
not the primary user-facing product workflow for #48.

If such a helper is kept or added, it must remain local/test scoped and produce the same single-transaction web
payload semantics before preview. It must not become an unattended batch importer under #48.

Example helper-only format:

```text
date | debit | credit | amount | currency | description | memo
YYYY-MM-DD | <source account alias/name> | <destination account alias/name> | <decimal amount> | <ISO code> | <text> | <optional text>
```

CSV-like helper input may be accepted only if the same validation, preview, redaction, and no-batch boundaries
are preserved.

## Preserve #47 policy

Every future #48 mutating session must preserve #47 policy:

- backup before each CREATE/PATCH unless the same-context owner approval explicitly approves a safer policy;
- read-back after each CREATE/PATCH;
- redacted audit evidence with opaque refs only;
- default-disabled reset after session;
- disabled-write probes for validate/preflight, CREATE, PATCH, and DELETE route families when available;
- Syncthing conflict-copy checks before/after if the target is under Syncthing;
- redacted-only GitHub/tracked reports;
- private details only in local app UI/runtime, Telegram, or other private owner context.

## Private verification-list rule

Private verification lists must use correct human-readable columns and must not swap Date, GUID, Accounts,
Description, Memo, or Amounts.

For owner verification outside the app UI, prefer compact numbered plain text if a Markdown table may wrap or
shift columns:

```text
1. Date: <date>; GUID: <guid>; Debit: <account>; Credit: <account>; Amount: <amount currency>;
   Description: <description>; Memo: <memo or empty>
```

GitHub/tracked reports must remain redacted-only and must not include those private details.

## Acceptance checklist

- [ ] Product scope states web UI, not Telegram/agent-driven bookkeeping.
- [ ] Browser/mobile transaction-entry form is planned or implemented.
- [ ] Backend validate/preview endpoint is planned or implemented and is non-mutating.
- [ ] Form covers date, debit/source account, credit/destination account, amount, currency, description, and
      optional memo.
- [ ] Preview/confirmation step exists before CREATE.
- [ ] CREATE count remains 1 per form submit unless a future issue expands scope.
- [ ] Preview is private local app UI/runtime only, not GitHub/tracked output.
- [ ] Ambiguous account matches are rejected unless owner resolves them.
- [ ] Missing/invalid amount, currency, or date is rejected.
- [ ] Target preflight and existing write gates are preserved.
- [ ] Optional PATCH remains app-created description/memo metadata-only.
- [ ] DELETE, batch mutation, and balance-affecting PATCH edits remain forbidden.
- [ ] #47 backup/read-back/audit/reset/probes and Syncthing conflict-copy rules are preserved.
- [ ] Redacted-only GitHub/tracked reports are preserved.
- [ ] Compact text/CSV remains optional local/debug/import-helper only, not the main user-facing workflow.

## Preview-only implementation slice

The first #48 implementation slice adds a **preview-only** web transaction-entry path. It does not authorize or
execute CREATE, PATCH, DELETE, or batch mutation.

Implemented direction:

- backend `POST /books/{book_id}/transactions/create-preview` validates one transaction create payload and returns
  a normalized private preview with `preview_only=true` and `create_count=1`;
- the endpoint works with `GNUCASH_WRITES_ENABLED=false`;
- the endpoint opens the selected book read-only to resolve account display paths and never constructs the write
  service, lock, backup, audit, or mutation path;
- `/transactions/new` is a browser/mobile preview form with date, debit/source account, credit/destination account,
  amount, currency, description, and optional memo fields;
- the UI shows preview-only/no-write messaging and a normalized local preview panel;
- Create/Submit mutation remains disabled/absent for this slice.

Future CREATE remains blocked until fresh same-context owner approval states exact CREATE count and #47-compatible
backup/read-back/audit/reset/probe requirements. DELETE, batch mutation, historical/manual mutation, and
amount/account/split/date/currency PATCH edits remain forbidden.

## Preview-only UX/error hardening slice

The next non-mutating #48 hardening slice improves browser/mobile usability while preserving the same no-write
boundary:

- debit/source and credit/destination selectors include lightweight search/filter inputs;
- the final submitted account values remain explicit account IDs from `<select>` controls, not ambiguous free text;
- full account paths are shown in the selectors;
- placeholder/hidden accounts are filtered out and documented in the UI;
- the UI prevents selecting the same source and destination account before preview submit;
- preview errors render a safe summary plus field-level hints where possible;
- error rendering always states that no CREATE/PATCH/DELETE/batch was executed;
- the preview panel explicitly shows `preview_only`, `create_count`, source/destination accounts, amount/currency,
  date, description, memo, and that Create remains disabled in this slice.

This hardening does not add a CREATE action, PATCH action, DELETE action, batch operation, release approval,
public write beta, or production/stable/security-audited claim. Future CREATE still requires fresh same-context
owner approval and an exact CREATE count.

## Preview-only accessibility/mobile smoke hardening slice

The accessibility/mobile smoke hardening slice keeps `/transactions/new` preview-only while improving product UI
quality:

- every key form field has an explicit label/id pairing: book, date, debit/source search and selector,
  credit/destination search and selector, amount, currency, description, and memo;
- field hints, field-level errors, the preview-only/no-write warning, and disabled Create explanation are linked
  with `aria-describedby` where rendered;
- the error summary remains safe, top-of-form, and repeats `No CREATE/PATCH/DELETE/batch executed`;
- amount/date/currency inputs are clearer while backend preview validation remains authoritative;
- narrow/mobile layout keeps sections stacked, constrains controls, and wraps long account/preview text;
- a redacted manual/browser smoke checklist is tracked at
  `docs/handoff/issue48-transaction-entry-preview-accessibility-mobile-smoke.md`.

This slice still does not approve or execute CREATE, PATCH, DELETE, batch mutation, private-book dogfood,
release/tag/package/image publication, public write beta, or production/stable/security-audited claims. Future
CREATE still requires fresh same-context owner approval and an exact CREATE count. DELETE, batch, and
amount/account/split/date/currency edits remain forbidden.

## Preview-only confirmation shell and draft-safety slice

The confirmation-shell/draft-safety slice keeps `/transactions/new` preview-only while making the future product
workflow clearer:

- a post-preview confirmation shell shows the future owner-approved CREATE review shape without enabling writes;
- the local-only preview-reviewed checkbox has no submitted field name and cannot enable CREATE;
- Future Create remains a disabled `type="button"` control;
- changing any form field after a successful preview marks the preview stale and tells the owner to run Preview
  again before any future approval step;
- Clear preview / start over reloads `/transactions/new` instead of storing private transaction details;
- account filter counts and selected-account type/currency summaries make account selection easier to verify on
  browser/mobile layouts;
- static guards prove the confirmation shell, stale-preview warning, no browser storage persistence, and disabled
  future-create control remain in place.

This slice still does not add a CREATE action, PATCH action, DELETE action, batch operation, private-book dogfood,
release/tag/package/image publication, public write beta, or production/stable/security-audited claim. Future
CREATE still requires fresh same-context owner approval and an exact CREATE count.

## Preview-only approval-packet and validation hardening slice

The approval-packet hardening slice keeps `/transactions/new` preview-only while making the future owner-approval
handoff explicit:

- a post-preview approval packet summarizes the future target book, `create_count = 1`, source/debit account,
  destination/credit account, amount/currency, date, description, memo, and safety checklist;
- the copy action uses a redacted placeholder-only approval template and does not copy private preview values;
- field-level validation copy is more user-oriented for missing book/account, no selectable accounts, same-account,
  amount, currency, date, description, and stale-preview cases;
- backend preview tests guard missing book, owner-only access, no selectable accounts, unknown accounts,
  credit-currency mismatch, read-error redaction, disabled-write behavior, Decimal/string preservation, and absence
  of write/backup/lock/audit/ownership paths;
- static guards prove the approval packet remains no-write and `create-preview` remains the only transaction-entry
  submission target.

This slice still does not add a CREATE action, PATCH action, DELETE action, batch operation, private-book dogfood,
release/tag/package/image publication, public write beta, or production/stable/security-audited claim. Future CREATE
still requires fresh same-context owner approval and an exact CREATE count.

## Deterministic synthetic browser smoke harness slice

The deterministic smoke harness keeps `/transactions/new` preview-only while making the previous manual/redacted
browser smoke reproducible:

- `npm run test:transaction-entry-preview-browser` starts a synthetic local API stub and the SvelteKit dev server with
  `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=false`;
- the harness drives headless Chromium through the Chrome DevTools Protocol instead of adding a new Playwright stack;
- it uses synthetic fixture data only and no private, original, working, or only-copy GnuCash book;
- it verifies the no-write warning, account filtering, account-ID submission, valid preview, approval packet,
  exact future CREATE count of 1, disabled Future Create control, placeholder-only approval template, local reviewed
  checkbox, stale-preview warning after draft changes, and Clear preview / start over;
- it observes browser requests and synthetic API calls and fails on CREATE, PATCH, DELETE, or batch transaction routes;
- detailed evidence is tracked in `docs/handoff/issue48-deterministic-browser-smoke-harness.md`.

This slice still does not add a CREATE action, PATCH action, DELETE action, batch operation, private-book dogfood,
release/tag/package/image publication, public write beta, or production/stable/security-audited claim. Future CREATE
still requires fresh same-context owner approval and an exact CREATE count.

## Transition to #49 owner-approved web UI CREATE trial

#48 is sufficiently validated for preview-only owner web transaction-entry UI. It may remain open as a
non-mutating preview/UI evidence tracker, but further #48 polishing should pause unless bugs are found.

The next product value is [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49):
a bounded, owner-approved CREATE through the web UI on a test copy or owner-selected target.

Creating #49 does not authorize mutation. Any future CREATE requires fresh same-context owner/PM approval with:

- exact target class;
- exact CREATE count;
- first trial default `CREATE 1 / PATCH 0 / DELETE 0 / batch 0` unless explicitly expanded later;
- write gates enabled only for the bounded session;
- `GNUCASH_WRITES_ENABLED=false` reset after the session.

Before any #49 CREATE, target preflight must prove the exact target exists/readable, is outside the repo,
GnuCash Desktop is closed, no concurrent writer/lock is present, no `.LCK`/`.LNK` is present, no Syncthing
conflict copy exists before/after if applicable, an independent backup exists, and restore proof is available.

The #49 Create button may become active only when writes are enabled, the bounded session is owner-approved, the
preview is valid and non-stale, the preview-reviewed checkbox is checked, exact CREATE count is 1, and target
preflight passed. No active create path should be reachable in default read-only mode; default state remains
disabled/inert.

A future #49 trial must use UI preview before CREATE, CREATE only from reviewed current preview, backup before
CREATE, read-back after CREATE, redacted audit evidence, disabled-write probes after reset for validate/preflight,
CREATE, PATCH, and DELETE, and manual Desktop verification for the first UI CREATE trial.

GitHub/tracked reporting stays redacted-only. Private paths, account names, descriptions, memos, amounts, GUIDs,
book names, backups, screenshots, tokens, keys, certs, and `.env` content remain private-only.

## #49 CREATE execution gate / armed-session shell slice

The first #49 implementation slice is gate/shell only. It prepares the UI/server representation for a future
owner-approved web UI CREATE trial without wiring or executing CREATE.

Implemented non-mutating pieces:

- `/transactions/new` server load returns a redacted write-session gate object with `writes_enabled`,
  `session_armed`, `create_execution_allowed`, `create_execution_reason`, `allowed_create_count`, and
  `target_class`;
- defaults are safe/off: `session_armed=false`, `create_execution_allowed=false`, `allowed_create_count=0`, and
  `target_class=null`;
- with default `GNUCASH_WRITES_ENABLED=false`, the UI states `Preview mode`, `Write session not armed`, and
  `CREATE execution unavailable without fresh owner approval`;
- the page shows a disabled armed-session requirements panel for target class, exact CREATE count, reviewed
  non-stale preview, backup/read-back/audit/reset/probes, and manual Desktop verification;
- the Future Create control remains a disabled `type="button"`;
- the preview-reviewed checkbox remains local-only and is explicitly insufficient by itself;
- static and synthetic browser smoke guards prove create-preview remains the only transaction-entry submission
  target and no active CREATE path is reachable in default mode.

This slice executed no CREATE, PATCH, DELETE, or batch mutation, did not touch a private/original/working/only-copy
book, did not publish a release, and does not authorize a future CREATE. Future CREATE still requires fresh
same-context owner/PM approval; the first trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.

## #49 target preflight/readiness UI shell slice

The next #49 implementation slice adds target readiness shell only. It prepares the UI/server representation for a
future target preflight without executing any private preflight, probing files, opening books, creating backups,
checking locks, calling write helpers, or executing CREATE.

Implemented non-mutating pieces:

- `/transactions/new` server load returns a redacted `targetPreflight` object with `required=true`,
  `status=not_checked`, `target_class=null`, and all checks `pending`;
- the page shows a `Target preflight required` / `Target readiness not checked` panel;
- the pending checklist covers target class selection, target file exists/readable, outside-repo proof, GnuCash
  Desktop closed, no concurrent writer/lock, no `.LCK`/`.LNK`, Syncthing conflict-copy check if applicable,
  independent backup, restore proof, reviewed non-stale preview, exact `CREATE count = 1`, reset/disabled probes,
  and manual Desktop verification;
- no checked/passed/ready target readiness state exists in default mode;
- Future Create remains disabled/inert, and preview-reviewed checkbox alone remains insufficient;
- static and synthetic browser smoke guards prove `create-preview` remains the only transaction-entry submission
  target, no file/book/backup/lock/write helper is referenced by the target shell, and no active CREATE path is
  reachable in default mode.

This slice executed no CREATE, PATCH, DELETE, batch mutation, private target preflight, private/original/working/
only-copy book use, release publication, or public write beta. Future CREATE still requires fresh same-context
owner/PM approval; the first trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.

## Current non-mutating state

This document is a re-scope/planning artifact. No CREATE, PATCH, DELETE, dogfood loop, release, tag, package,
image publication, public write beta, or production/stable/security-audited claim is made here.
