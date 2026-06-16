# Issue #45 to PATCH app-created transition

Date: 2026-06-16
Source issue: [#45 Owner real-book CREATE-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/45)
Next issue: [#46 Owner real-book PATCH app-created transaction trial](https://github.com/valentusys/gnucash-web-companion/issues/46)
Verdict: **TRANSITION_DOCUMENTED_NO_MUTATION**

## Evidence basis

#45 CREATE-only test-copy sessions are sufficiently validated for CREATE-only on the test copy:

- latest generated session: CREATE 20 / 20;
- PATCH: 0;
- DELETE: 0;
- batch: 0;
- owner manually verified 20 / 20 in GnuCash Desktop;
- read-back, redacted audit, default-disabled reset, disabled-write probes, and conflict checks passed.

This transition task executed no CREATE, PATCH, DELETE, batch operation, dogfood loop, release, or publication.

## #45 state

#45 remains open if needed for CREATE-only operating-mode tracking. #45 is not PATCH approval, DELETE approval,
batch approval, release approval, public write beta approval, or production/stable/security-audited evidence.

## New PATCH boundary

#46 was created as the separate next issue for a first owner-only PATCH app-created transaction trial.

#46 is strictly scoped:

- owner-only;
- test copy / owner-selected real-book target only;
- PATCH only app-created transactions;
- first PATCH scope: metadata/description/memo-only;
- no amount changes;
- no account changes;
- no split changes;
- no historical/manual transaction mutation;
- no DELETE;
- no batch;
- no unattended mutation;
- no public write beta;
- no release/tag/package/image publication;
- no production/stable/security-audited claims.

## Required before any future PATCH

A future PATCH trial requires explicit same-context owner/PM approval before mutation and must define:

1. exact redacted target class;
2. exact app-created transaction identity boundary;
3. exact PATCH count;
4. metadata/description/memo-only PATCH scope;
5. backup before each PATCH or an explicitly approved backup policy;
6. read-back after each PATCH;
7. redacted audit evidence;
8. default-disabled reset after the session;
9. disabled-write probes after reset;
10. manual GnuCash Desktop verification for early PATCH trials;
11. redacted-only GitHub/tracked reporting.

## Redaction and safety

Committed and GitHub-posted evidence must not include raw private paths, account names, descriptions,
memos, amounts, GUIDs, books, backups, screenshots, tokens, keys, certs, or `.env` content.

## Exact next allowed step

The exact next allowed step is a future owner/PM-approved #46 PATCH app-created transaction trial, limited to
metadata/description/memo-only PATCH of exactly identified app-created transactions on a test copy or
owner-selected target. No PATCH is authorized until that fresh same-context approval exists.
