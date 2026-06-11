# Issue #45 second CREATE-only operating session report

Date: 2026-06-11
Issue: [#45 Owner real-book CREATE-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/45)
Final verdict: **CREATE_ONLY_SESSION_SUCCEEDED**

## Redacted target and scope

- Target class: `owner-primary-real-gnucash-sqlite-book`
- Mode: owner-only real-book CREATE-only operating session
- CREATE attempted: 5
- CREATE executed: 5
- PATCH: 0
- DELETE: 0
- batch: 0

## Preflight

Target-specific preflight was re-run before mutation and passed with redacted checks only:

- target exists: yes
- target non-empty: yes
- SQLite header check: passed
- exclusive write-lock check: passed
- sidecar lock check: passed
- concurrent writer/process check: passed

## Route backup policy and result

Policy: route backup immediately before each individual CREATE.

- CREATE 1 route backup: yes, opaque ref `bkp-ce4d60ed9daa`
- CREATE 2 route backup: yes, opaque ref `bkp-e17acb2472fd`
- CREATE 3 route backup: yes, opaque ref `bkp-12abcf7e5e5e`
- CREATE 4 route backup: yes, opaque ref `bkp-99f22e45f320`
- CREATE 5 route backup: yes, opaque ref `bkp-746990bcfa53`

## Read-back and audit evidence

- CREATE 1 read-back: passed, structural marker `tx1_splits2_balanced_single_currency`
- CREATE 1 audit evidence: captured, opaque ref `aud-290033f0e2d9`
- CREATE 2 read-back: passed, structural marker `tx1_splits2_balanced_single_currency`
- CREATE 2 audit evidence: captured, opaque ref `aud-1cf69490a476`
- CREATE 3 read-back: passed, structural marker `tx1_splits2_balanced_single_currency`
- CREATE 3 audit evidence: captured, opaque ref `aud-552bcd0d68b9`
- CREATE 4 read-back: passed, structural marker `tx1_splits2_balanced_single_currency`
- CREATE 4 audit evidence: captured, opaque ref `aud-bdf2f23ec488`
- CREATE 5 read-back: passed, structural marker `tx1_splits2_balanced_single_currency`
- CREATE 5 audit evidence: captured, opaque ref `aud-16bc061a5747`

## Reset and disabled-write probes

- Default-disabled reset: passed
- Disabled-write probes after reset: passed for validate/preflight, CREATE, PATCH, and DELETE route families
- Validate, CREATE, PATCH, and DELETE mutation gates returned HTTP 403 with `GNUCASH_WRITES_ENABLED=false`
- Owner-writebeta preflight/status family remained blocked by `writes_disabled_default`

## Safety summary

- Five individual CREATE operations were attempted and succeeded within the approved session limit.
- No PATCH was performed.
- No DELETE was performed.
- No batch operation was performed.
- No unattended mutation or dogfood loop was run.
- No release, tag, package, image publication, or public write beta was performed.
- No production, stable, or security-audited claim is made.
- No raw private paths, account names, descriptions, memos, amounts, books, backups, screenshots, tokens, keys, certs, or `.env` content are included in this tracked report.

## Manual Desktop verification

Owner manual GnuCash Desktop verification is still required for the created transactions.
