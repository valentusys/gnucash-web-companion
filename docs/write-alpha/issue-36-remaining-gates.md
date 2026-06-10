# Issue #36 remaining controlled-write gates

Status: keep #36 open. This is a non-mutating PM gate packet, not execution approval and
not a release decision.

Current reconciliation: tracked docs, GitHub #36, and the guarded repository posture agree that
owner-writebeta remains maintenance-only. The W3 copied/restorable evidence is accepted narrowly,
but it does not authorize a public write beta, release publication, real/private/working/only-copy
mutation, broad compatibility claim, stable claim, production-ready claim, or security-audited claim.

## PM decision after W3

PM decision: `COPIED_BOOK_GATE_ACCEPTED_KEEP_36_OPEN_FOR_RELEASE_OR_REAL_BOOK_DECISION`.

The copied-book dogfood gate is accepted narrowly for the committed W3 evidence. #36 stays
open for release/no-release review, supported-version compatibility limits, and any later
real-book/owner-only decision.

## Current accepted evidence

Accepted evidence is narrow and review-only unless noted otherwise:

- Default-disabled repository/config posture: `GNUCASH_WRITES_ENABLED=false` remains the committed
  default and `APP_ENV=test` remains required for enabled write-alpha/writebeta route execution.
- Disabled-route and reset/default-disabled probes: accepted as non-mutating/default posture evidence.
- Backup/restore, recovery/hard-stop, and concurrency/lock-contention guards: accepted as
  synthetic/non-mutating readiness checks and future evidence requirements.
- Maintainer review/recovery procedure and checklist: accepted as documentation gates only.
- Copied-book dogfood gate accepted for W3 only: W3 CREATE 2 / PATCH 1 / DELETE 1 on one staged
  outside-git copied/restorable target.
- W3 PATCH acceptance is metadata/memo-only on a write-alpha-created transaction.
- W3 DELETE acceptance is limited to a write-alpha-created disposable transaction.
- W3 backup, route-backup, audit, read-back, restore, compatibility-open, and default-disabled
  CREATE/PATCH/DELETE probe evidence is accepted as redacted copied/restorable evidence.
- Copied/restorable CREATE/PATCH/DELETE evidence remains accepted narrowly for the exact
  copied/restorable evidence already recorded; it is not a real-book claim and not broad GnuCash
  compatibility.
- Compatibility wording guard: supported-version write compatibility remains pending and claims must stay
  tied to synthetic/disposable or copied/restorable evidence only.
- Issue #22 is now closed narrowly for one isolated GnuCash 5.14 Desktop-generated synthetic SQLite
  read-only fixture only. That closure removes the docs-vs-GitHub drift but does not prove write
  compatibility, broad Desktop-version support, real-book safety, or non-SQLite backend support.
- Current guard state: write-safety, public-status, markdown-readability, and tracked-hygiene guards
  remain the required non-mutating checks before any future #36 closure or release decision.
  Tracked-hygiene coverage includes committed private/runtime artifact classes, raw private-evidence
  markers, private-looking path/account/description/memo/amount labels, and high-risk affirmative
  write/public readiness claims. Passing those guards is repository hygiene only, not release
  authorization.

## Gates still blocking #36 closure

#36 must stay open unless a maintainer/PM review explicitly accepts every blocker below and states the
original issue scope is satisfied.

1. Supported-version write compatibility evidence
   - Updated after #22: one GnuCash 5.14 Desktop-generated synthetic SQLite fixture has passed
     read-only validation, so the #22 docs-vs-GitHub drift is resolved.
   - Still pending for #36 closure/release: Desktop/version-specific write compatibility has not been
     accepted across supported GnuCash versions.
   - Required before closure: redacted evidence tied to synthetic/disposable or copied/restorable
     fixtures only, with no broad backend/Desktop/version support claim.

2. Future copied/restorable mutation evidence packet
   - Pending: future mutation evidence is not authorized by this audit.
   - Required before closure if pursued: same-context owner + PM authorization, Desktop closed for the
     target copy, outside-git copied/restorable fixture provenance, independent backup, preflight,
     route family/count scope, backup, read-back, audit, lock/contention, restore/rollback,
     reset/default-disabled probe, and redaction review.

3. Real/private/original/only-copy boundary
   - Pending: no real working-book mutation is authorized or accepted.
   - Required before any expansion: an explicit later PM/owner decision and a safety model that still
     forbids original/private/working/only-copy first-use mutation.

4. Release/public posture
   - Pending: no public write beta, v0.2-ready, stable, production-ready, or security-audited claim is
     authorized.
   - Required before closure: PM release/no-release decision remains `NO_RELEASE` unless separately
     authorized after all gates pass.

5. Closure decision itself
   - Pending: no maintainer/PM acceptance says the original #36 scope is satisfied.
   - Required before closure: re-read #36, linked handoffs, latest CI, this blocker list, and current
     guard results; then record either a keep-open decision or an explicit closure decision.

6. Guarded documentation state
   - Pending: any future owner-writebeta wording must continue to pass the repository guard scripts and
     keep all owner-writebeta claims bounded to maintenance, copied/restorable evidence, and explicit
     same-context authorization.
   - Required before closure or release: public docs and handoffs must still say `NO_RELEASE`, no public
     write beta, no real/private/original/working/only-copy safety claim, default
     `GNUCASH_WRITES_ENABLED=false`, and enabled write-alpha/writebeta `APP_ENV=test` gating.

## Owner-only writebeta release prerequisites

A later v0.4 owner-writebeta release candidate can be prepared only after a PM release gate records
one of the allowed release decisions. That gate must preserve all of these constraints:

- owner-only scope, not public write beta;
- default `GNUCASH_WRITES_ENABLED=false` and enabled write-alpha/writebeta `APP_ENV=test` gate;
- no stable, production-ready, or security-audited claim;
- no hosted-SaaS or public-internet safety claim;
- no real/private/original/working/only-copy safety claim or first-use mutation claim;
- W3 evidence described only as staged copied/restorable evidence;
- exact blockers for supported-version compatibility and real working-book owner decision.

## Real working-book trial prerequisites

No real working-book trial is approved by this packet. A later trial would require owner input and a
separate safety model before any mutation, including at minimum:

- explicit owner-selected target and PM authorization in the same execution context;
- independent backup and restore path verified before mutation;
- Desktop closed / no concurrent writer proof;
- exact route family and count authorization;
- read-back, audit, backup, restore, default-disabled reset, and compatibility evidence;
- redacted reporting only;
- a hard prohibition on original/private/working/only-copy first-use mutation unless that exact later
  owner decision overrides this boundary with a safer staged plan.

## Required verification before any future #36 closure attempt

Run these from a clean working tree:

```bash
cd apps/api && pytest -q tests/test_write_safety_defaults_guard.py tests/test_write_alpha_readiness.py
cd ../.. && python3 scripts/check_write_safety_defaults.py
python3 scripts/check_public_status.py
python3 scripts/check_markdown_readability.py
python3 scripts/check_tracked_hygiene.py
git diff --check
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

## Safety result for this audit

- Mutation counts for this PM gate and packet refresh: CREATE 0 / PATCH 0 / DELETE 0.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account
  name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated,
  committed, or posted.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Enabled write-alpha/writebeta remains `APP_ENV=test` gated.
- Recommendation: keep #36 open.
