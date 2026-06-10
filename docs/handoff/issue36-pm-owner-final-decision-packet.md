# Issue #36 PM/Owner final decision packet

Date/time UTC: 2026-06-10T23:20:00Z
Issue: #36 — Track remaining controlled-write v0.2 readiness gates
Decision: `CLOSE_36_AS_MAINTENANCE_BOUNDARY`

This is a short PM/Owner decision packet. It is not a dogfood run, not a GnuCash mutation, not release
preparation, and not publication approval.

## Decision

Close #36 as a completed readiness/guard/maintenance boundary issue.

The original tracker has accumulated enough accepted boundary evidence and guard coverage to stop using
#36 as an open-ended maintenance bucket. Keeping it open now invites repeated wording-only maintenance
runs rather than a single actionable blocker.

## Evidence considered

- W3 copied-book evidence is accepted narrowly for the staged outside-git copied/restorable target and
  exact counts: CREATE 2 / PATCH 1 metadata/memo-only / DELETE 1 disposable transaction.
- #22 is closed narrowly for one GnuCash 5.14 Desktop-generated synthetic SQLite read-only fixture.
- #28 is closed.
- Repeated r8-r13/r14 no-release/readiness docs preserve the conservative release posture.
- Current guards passed for public status, write-safety defaults, markdown readability, tracked hygiene,
  whitespace, and the focused write-safety guard test suite.
- No release, public write beta, real-book mutation, stable claim, production-ready claim, or
  security-audited claim is preserved by this decision.

## Why option A is selected

Option B is rejected because there is no single remaining actionable blocker that belongs inside #36.
The remaining work items are different future decision scopes, not one blocker:

1. future owner-writebeta release-candidate decision;
2. future real-book trial safety model;
3. future broader write compatibility evidence.

Option C is not executed as an issue-splitting operation in this packet because those future scopes need
fresh owner/PM authorization and exact goals before issue creation. They should be created later when the
owner wants that work started.

## Preserved boundaries after closure

Closing #36 does not change product safety posture:

- no release;
- no public write beta;
- no real/private/original/working/only-copy mutation;
- `v0.4.0-owner-writebeta` remains unpublished;
- no stable, production-ready, hosted-SaaS, public-internet-safe, security-audited, only-copy-safe, or
  broad GnuCash compatibility claim;
- `GNUCASH_WRITES_ENABLED=false` remains default;
- enabled write-alpha/writebeta routes remain `APP_ENV=test` gated.

## Future work must be new scope

Any later work must start from a new issue plus explicit owner/PM approval in the same execution context:

- future owner-writebeta release-candidate decision;
- future real-book trial safety model;
- future broader write compatibility evidence.

Those future issues may cite #36 as historical maintenance evidence only. They must not treat #36 closure
as release approval, public-write approval, real-book mutation approval, or compatibility proof.

## Safety result for this packet

- Mutation counts for this packet: CREATE 0 / PATCH 0 / DELETE 0.
- No dogfood was run.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account
  name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated,
  committed, or posted.
- No release, tag, package, image, public write beta, or stable/production/security-audited claim was
  created.
