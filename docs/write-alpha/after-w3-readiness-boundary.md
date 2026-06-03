# After-W3 controlled-write readiness boundary

Status: non-mutating #36 readiness packet. This document is not release approval, not
copied-book mutation approval, and not real/private/original/working/only-copy safety evidence.

## Decision posture

- #36 remains open after the accepted W3 copied-book dogfood gate.
- Release decision remains `NO_RELEASE`; no `v0.4.0-owner-writebeta` release candidate is prepared,
  tagged, published, or claimed by this packet.
- Public posture remains no public write beta, no stable release, no production-ready claim, and no
  security-audited claim.
- The W3 copied-book evidence is accepted only for the staged outside-git copied/restorable target and
  exact operation counts already recorded: CREATE 2, PATCH 1 metadata/memo-only on a
  write-alpha-created transaction, and DELETE 1 on a write-alpha-created disposable transaction.

## Default-disabled and recovery boundary

- `GNUCASH_WRITES_ENABLED=false` remains the committed default before and after any future readiness
  package.
- Enabled write-alpha/writebeta routes remain `APP_ENV=test` gated.
- Any future mutation packet must finish with reset/default-disabled probes for every touched write
  route family.
- Any failed backup, read-back, audit, lock/contention, restore, or disabled-probe step is a hard stop:
  preserve evidence, keep writes disabled, do not retry against the same copy, and escalate to PM/owner.
- Recovery evidence is acceptable only as restore-to-copy or synthetic/disposable evidence unless a
  later same-context PM/owner decision explicitly changes scope.

## Compatibility boundary

- Supported-version write compatibility remains pending and blocks #36 closure.
- Compatibility claims must stay tied to synthetic/disposable or copied/restorable evidence only.
- The W3 copied-book evidence is not a broad GnuCash compatibility claim and not a real-book claim.
- #22 stays open until an isolated Desktop-generated synthetic SQLite fixture exists and passes
  fail-closed preflight plus default-read-only validation.
- PostgreSQL/MySQL/MariaDB GnuCash backends remain unclaimed for this release/readiness posture.

## Future owner-only decision inputs

A later owner-only writebeta decision needs a fresh PM gate that re-reads this boundary,
`docs/write-alpha/issue-36-remaining-gates.md`, the current compatibility matrix, latest CI, and any
new redacted evidence. It must still preserve:

1. no public write beta;
2. default `GNUCASH_WRITES_ENABLED=false`;
3. enabled write-alpha/writebeta `APP_ENV=test` gating;
4. no original/private/working/only-copy first-use mutation;
5. no stable, production-ready, or security-audited claim;
6. explicit same-context owner + PM authorization for any copied/restorable mutation packet.

## Safety result

- Mutation counts for this packet: CREATE 0 / PATCH 0 / DELETE 0.
- No GnuCash book, SQLite book, app DB, backup, export, screenshot, `.env`, token, key, cert, private
  path, account name, transaction description, memo, amount, or raw private evidence was opened,
  copied, mutated, committed, or posted.
