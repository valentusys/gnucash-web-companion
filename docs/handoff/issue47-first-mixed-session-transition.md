# Issue #47 first mixed session post-success transition

Date: 2026-06-16
Issue: [#47 Owner real-book CREATE + PATCH app-created metadata-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/47)
Verdict: **POLICY_V1_DOCUMENTED_NO_MUTATION**

## Evidence basis

#47 first mixed CREATE + PATCH app-created metadata-only session succeeded and was owner-verified:

- CREATE: 10 / 10;
- PATCH: 5 / 5;
- DELETE: 0;
- batch: 0;
- PATCH scope: metadata/description-only;
- amount/account/split/date/currency unchanged: passed 5 / 5;
- owner manually verified in GnuCash Desktop:
  - CREATE: 10 / 10 confirmed;
  - PATCH: 5 / 5 confirmed.

This transition task executed no CREATE, PATCH, DELETE, batch operation, dogfood loop, release, or publication.

## Tracker state

- #45 remains the CREATE-only tracker.
- #46 remains the PATCH app-created metadata-only boundary/evidence tracker.
- #47 is the active mixed CREATE + PATCH app-created metadata-only operating-mode tracker.

No tracker is DELETE approval, batch approval, release approval, public write beta approval, or production/stable/security-audited evidence.

## Operating policy v1

CREATE + PATCH app-created metadata-only operating policy v1 allows only future bounded owner-approved sessions with:

- CREATE: explicit bounded count;
- PATCH: explicit bounded count;
- PATCH targets: app-created transactions only;
- PATCH scope: description/memo metadata-only only;
- DELETE: 0;
- batch: 0;
- no unattended mutation;
- no public write beta;
- no release/tag/package/image publication;
- no production/stable/security-audited claims;
- backup/read-back/audit/reset/probes;
- Syncthing conflict-copy checks before/after if applicable;
- redacted-only GitHub/tracked reporting;
- private details only in Telegram.

Fresh same-context owner/PM approval is required before every future session. #47 does not authorize mutation by itself.

## Private Telegram verification-list rule

Future private Telegram verification lists must use correct human-readable columns:

- Date must contain a date.
- GUID must contain a transaction GUID.
- Accounts must contain selected debit/credit accounts.
- Description before/after must contain descriptions.
- Amounts must contain amounts.
- Columns must not be swapped.
- If a formatted table cannot be produced safely, return compact numbered plain text instead.

GitHub/tracked reports must remain redacted-only and must not include raw private paths, account names, descriptions, memos, amounts, GUIDs, books, backups, screenshots, tokens, keys, certs, or `.env` content.

## Safety summary

- No CREATE was performed in this transition.
- No PATCH was performed in this transition.
- No DELETE was performed.
- No batch operation was performed.
- No dogfood loop was run.
- No private/original/working/only-copy book was touched.
- No release, tag, package, image publication, or public write beta was performed.
- No production, stable, or security-audited claim is made.

## Exact next allowed step

The exact next allowed step is a future #47 bounded owner-approved mixed CREATE + PATCH app-created metadata-only session with fresh same-context owner/PM approval, exact CREATE/PATCH counts, exact target class, app-created PATCH identity proof, backup/read-back/audit/reset/probes, and redacted-only tracked reporting.
