# Issue #46 to CREATE + PATCH app-created operating-mode transition

Date: 2026-06-16
Source issue: [#46 Owner real-book PATCH app-created transaction trial](https://github.com/valentusys/gnucash-web-companion/issues/46)
Next issue: [#47 Owner real-book CREATE + PATCH app-created metadata-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/47)
Verdict: **TRANSITION_DOCUMENTED_NO_MUTATION**

## Evidence basis

#45 CREATE-only test-copy sessions succeeded and were owner-verified.

#46 PATCH app-created metadata-only trials are sufficiently validated for PATCH app-created metadata-only on
the test copy:

- first PATCH trial: PATCH 5 / 5;
- expanded PATCH trial: PATCH 20 / 20;
- owner manually verified expanded metadata-only suffixes: 20 / 20;
- CREATE: 0 during PATCH trials;
- DELETE: 0;
- batch: 0;
- metadata-only and amount/account/split/date/currency unchanged checks passed;
- read-back, redacted audit, default-disabled reset, disabled-write probes, and conflict checks passed.

This transition task executed no CREATE, PATCH, DELETE, batch operation, dogfood loop, release, or publication.

## #46 state

#46 remains open if needed as the PATCH app-created metadata-only boundary/evidence tracker. #46 is not
DELETE approval, batch approval, release approval, public write beta approval, or production/stable/security-
audited evidence.

## New CREATE + PATCH operating boundary

#47 was created as the separate next issue for future bounded mixed CREATE plus PATCH app-created
metadata-only operating sessions.

#47 is strictly scoped:

- owner-only;
- test copy / owner-selected real-book target only;
- CREATE allowed only as bounded individual operations;
- PATCH allowed only for app-created transactions;
- PATCH scope only description/memo metadata-only;
- no amount changes;
- no account changes;
- no split changes;
- no date/currency/balance-affecting changes;
- no historical/manual transaction mutation;
- no DELETE;
- no batch;
- no unattended mutation;
- no public write beta;
- no release/tag/package/image publication;
- no production/stable/security-audited claims.

## Required before any future #47 session

A future #47 session requires explicit same-context owner/PM approval before mutation and must define:

1. exact target class;
2. exact CREATE count;
3. exact PATCH count;
4. exact app-created identity boundary before PATCH;
5. backup policy;
6. read-back after each CREATE/PATCH;
7. redacted audit evidence;
8. default-disabled reset after the session;
9. disabled-write probes after reset;
10. Syncthing conflict-copy check before/after if target is under Syncthing;
11. manual Desktop verification for early mixed sessions;
12. redacted-only GitHub/tracked reporting.

## Private verification-list rule

Future private Telegram verification lists must use correct human-readable columns and must not swap Date,
GUID, Description, or Amounts. GitHub/tracked reports remain redacted-only and must not include raw private
paths, account names, descriptions, memos, amounts, GUIDs, books, backups, screenshots, tokens, keys, certs,
or `.env` content.

## Exact next allowed step

The exact next allowed step is a future owner/PM-approved #47 bounded CREATE + PATCH app-created
metadata-only operating session. No CREATE or PATCH is authorized until that fresh same-context approval
exists.
