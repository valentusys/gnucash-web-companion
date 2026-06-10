# Issue #44 real-book trial preparation packet

Date: 2026-06-11
Issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)

## Status

Preparation only. No GnuCash book was opened, copied, backed up, restored, or mutated by this packet.
No route was armed and no CREATE, PATCH, DELETE, or batch operation was executed.

## Public posture reconciled

- `v0.5.0-public-readonly-beta` remains the current public read-only beta.
- `v0.4.0-owner-writebeta` remains unpublished.
- `v0.5.1-public-readonly-beta` remains unpublished.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Enabled write-alpha/writebeta flows remain `APP_ENV=test` gated.
- #36 is closed as `CLOSE_36_AS_MAINTENANCE_BOUNDARY`.
- Current active issue is #44 Owner real-book trial safety model.
- #44 is not mutation approval, not release approval, and not public write beta approval.

## Scope prepared for a later owner-approved trial

The first possible real-book trial is constrained to:

- one CREATE transaction only;
- no PATCH;
- no DELETE;
- no batch;
- no unattended real-book mutation;
- no release, tag, package, or image;
- no public write beta;
- no production, stable, or security-audited claim.

## Required owner/PM input before any mutation

A later same-context approval must provide all of the following in one explicit decision:

1. Exact target class: owner-selected real-book trial target, not original-only or only-copy unsafe use.
2. Exact operation count: CREATE 1, PATCH 0, DELETE 0, batch 0.
3. Confirmation that GnuCash Desktop is closed for the target and no concurrent writer is active.
4. Confirmation that an independent backup exists outside the app route backup path.
5. Confirmation that restore path/proof was verified before mutation.
6. Approval to take a route backup immediately before the one CREATE.
7. Approval to perform read-back and audit capture after the one CREATE.
8. Approval to reset to default-disabled writes immediately after CREATE.
9. Approval to run disabled-write probes after reset.
10. Commitment that all committed or issue-posted evidence is redacted only.

If any item is missing, the trial must stop before mutation.

## Evidence model

Allowed committed or issue-posted evidence:

- target class label, without raw path or book name;
- operation count summary: CREATE 0/1, PATCH 0, DELETE 0, batch 0;
- boolean backup/restore/read-back/audit/reset/probe markers;
- route backup reference as a redacted opaque ID only;
- audit reference as a redacted opaque ID only;
- disabled-write probe status codes and route family labels only.

Forbidden in committed or issue-posted evidence:

- raw private paths;
- account names;
- transaction descriptions;
- memos;
- amounts;
- book names or raw book files;
- backup paths or backup files;
- screenshots containing private data;
- tokens, keys, certs, or `.env` content.

## Prepared artifacts

- `docs/write-alpha/owner-real-book-trial-runbook.md`
- `docs/write-alpha/owner-real-book-trial-checklist.md`

## Stop conditions

Stop before mutation if any of these is true:

- same-context owner/PM approval is absent or ambiguous;
- target class or operation count is not exact;
- GnuCash Desktop may still be open;
- a lock or concurrent writer is present;
- independent backup is absent;
- restore proof is missing or unverified;
- route backup cannot be taken;
- evidence would require posting raw private data;
- `GNUCASH_WRITES_ENABLED=false` or `APP_ENV=test` gates would be weakened;
- the task begins to imply release, public write beta, stable, production, or security-audited status.

## Result of this packet

Prepared the safety model only. Mutation remains unapproved and unexecuted.
