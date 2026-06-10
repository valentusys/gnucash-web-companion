# Issue #36 controlled-write boundary closure

Status: `CLOSE_36_AS_MAINTENANCE_BOUNDARY`.

This document supersedes the earlier keep-open remaining-gates packet. It records the PM/Owner decision
that #36 is closed as a completed readiness/guard/maintenance boundary issue, while preserving all
conservative safety and release boundaries.

## Decision

PM decision: `CLOSE_36_AS_MAINTENANCE_BOUNDARY`.

Close #36 because the remaining possible work is no longer one actionable #36 blocker. It is separate
future scope that requires new issues and explicit owner/PM approval.

## Accepted maintenance boundary evidence

Accepted evidence is narrow and review-only unless explicitly stated:

- Default-disabled repository/config posture: `GNUCASH_WRITES_ENABLED=false` remains the committed
  default and `APP_ENV=test` remains required for enabled write-alpha/writebeta route execution.
- Disabled-route and reset/default-disabled probes are accepted as non-mutating/default posture evidence.
- Backup/restore, recovery/hard-stop, concurrency/lock-contention, state-machine evidence, restore
  evidence, and default-disabled probes remain accepted as guard coverage and future evidence
  requirements, not release proof.
- Copied-book dogfood gate accepted for W3 only: W3 CREATE 2 / PATCH 1 / DELETE 1 on one staged
  outside-git copied/restorable target.
- W3 PATCH acceptance is metadata/memo-only on a write-alpha-created transaction.
- W3 DELETE acceptance is limited to a write-alpha-created disposable transaction.
- W3 backup, route-backup, audit, read-back, restore, compatibility-open, and default-disabled
  CREATE/PATCH/DELETE probe evidence is accepted as redacted copied/restorable evidence.
- Copied/restorable CREATE/PATCH/DELETE evidence remains accepted narrowly for the exact
  copied/restorable evidence already recorded; it is not a real-book claim and not broad GnuCash
  compatibility.
- Issue #22 is closed narrowly for one isolated GnuCash 5.14 Desktop-generated synthetic SQLite read-only
  fixture only. That closure does not prove write compatibility, broad Desktop-version support,
  real-book safety, or non-SQLite backend support.
- Issue #28 is closed.
- Current guard state remains the required non-mutating safety net for later work: write-safety,
  public-status, markdown-readability, and tracked-hygiene guards preserve repository hygiene only, not
  release authorization.

## Preserved boundaries after #36 closure

#36 closure explicitly preserves:

- `NO_RELEASE`;
- no public write beta;
- no stable, production-ready, or security-audited claim;
- no real/private/original/working/only-copy safety claim;
- no real/private/original/only-copy safety claim;
- no real/private/original/working/only-copy mutation;
- no only-copy safety claim;
- no broad GnuCash compatibility claim;
- `v0.4.0-owner-writebeta` unpublished;
- `GNUCASH_WRITES_ENABLED=false` as default;
- enabled write-alpha/writebeta `APP_ENV=test` gate.

## Future work split

The following topics must be new issues or explicit owner/PM tasks. They are not blockers that keep #36
open:

1. Future owner-writebeta release-candidate decision.
   - Requires explicit owner/PM release-candidate scope before any release artifacts, tag, package,
     image, announcement, or publication work.
2. Future real-book trial safety model.
   - Requires explicit owner-selected target, independent backup/restore plan, same-context PM approval,
     and a safety model before any mutation. It still must forbid original/private/working/only-copy
     first-use mutation unless a later owner decision names a safer staged override.
3. Future broader write compatibility evidence.
   - Supported-version write compatibility evidence remains unaccepted beyond narrow synthetic/
     disposable or copied/restorable evidence only. Any broader claim requires a separate issue,
     redacted evidence, and explicit review.
4. Future copied/restorable mutation evidence packet.
   - Requires same-context owner + PM authorization before execution, route family and operation counts,
     backup/read-back/audit/lock/restore/reset expectations, and redaction requirements.

## Closure rule now applied

The old closure decision requirement is satisfied by
`docs/handoff/issue36-pm-owner-final-decision-packet.md` with decision
`CLOSE_36_AS_MAINTENANCE_BOUNDARY`. Future workers must not reopen #36 for general maintenance or repeat
no-release wording. If new work is needed, create or request a new issue with exact scope.

## Safety result for this packet

- Mutation counts for this PM gate and packet refresh: CREATE 0 / PATCH 0 / DELETE 0.
- No dogfood was run.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account
  name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated,
  committed, or posted.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Enabled write-alpha/writebeta remains `APP_ENV=test` gated.
- Recommendation: close #36 as maintenance boundary, not as release approval.
