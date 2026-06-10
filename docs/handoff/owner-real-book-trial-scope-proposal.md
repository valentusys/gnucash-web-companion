# Owner real-book trial safety model scope proposal

Date/time UTC: 2026-06-11T00:00:00Z
Created issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)
References: #36 as historical maintenance evidence only

This is a reconcile and next-scope packet. It is not dogfood, not mutation approval, not release
preparation, and not publication approval.

## Reconcile result

- #36 is closed as `CLOSE_36_AS_MAINTENANCE_BOUNDARY`.
- #36 closure is historical maintenance evidence only.
- #36 closure is not real-book approval, not public write beta approval, not release approval, and not
  broad compatibility proof.
- The public docs should describe #36 as closed, not as an open/current maintenance queue.
- `NO_RELEASE`, no public write beta, no real/private/original/working/only-copy mutation approval,
  `GNUCASH_WRITES_ENABLED=false`, and enabled write-alpha/writebeta `APP_ENV=test` gates remain
  preserved.

## New issue proposal

Title: Owner real-book trial safety model

Goal: prepare the first strictly limited owner-approved real-book trial safety model without executing
that trial in this packet.

The first trial scope is intentionally minimal:

- one owner-approved CREATE transaction only;
- explicit same-context owner/PM approval before any mutation;
- backup and restore proof before and after the trial;
- Desktop closed / lock check before mutation;
- read-back after mutation;
- audit evidence after mutation;
- default-disabled reset proof after mutation.

## Forbidden for the first trial

- PATCH existing transactions;
- DELETE;
- batch operations;
- unattended real-book mutation;
- public write beta;
- release/tag/package/image publication;
- production, stable, hosted-SaaS, public-internet-safe, security-audited, only-copy-safe, or broad
  GnuCash compatibility claims.

## Required safety model before any mutation

Before any future worker may mutate a real book, the new issue must record or require:

1. explicit owner-selected target and explicit same-context owner/PM authorization;
2. independent backup and restore proof for the exact target class;
3. Desktop closed and lock/no-concurrent-writer check;
4. exact mutation scope: one CREATE only;
5. route backup/read-back/audit evidence requirements;
6. restore/rollback expectation and hard-stop conditions;
7. default-disabled reset and probe evidence after the trial;
8. redacted reporting only;
9. no raw private paths, account names, descriptions, memos, amounts, app DBs, books, backups,
   exports, screenshots, tokens, keys, certs, or `.env` content in committed or posted evidence.

## Safety result for this packet

- Mutation counts for this packet: CREATE 0 / PATCH 0 / DELETE 0.
- No dogfood was run.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account
  name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated,
  committed, or posted.
- No release, tag, package, image, public write beta, or stable/production/security-audited claim was
  created.
