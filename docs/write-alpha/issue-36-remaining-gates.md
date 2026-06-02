# Issue #36 remaining controlled-write gates

Status: keep #36 open. This is a non-mutating audit packet, not execution approval and not a
release decision.

## Current accepted evidence

Accepted evidence is narrow and review-only unless noted otherwise:

- Default-disabled repository/config posture: `GNUCASH_WRITES_ENABLED=false` remains the committed
  default and `APP_ENV=test` remains required for enabled write-alpha/writebeta route execution.
- Disabled-route and reset/default-disabled probes: accepted as non-mutating/default posture evidence.
- Backup/restore, recovery/hard-stop, and concurrency/lock-contention guards: accepted as
  synthetic/non-mutating readiness checks and future evidence requirements.
- Maintainer review/recovery procedure and checklist: accepted as documentation gates only.
- Copied/restorable CREATE/PATCH/DELETE evidence: accepted narrowly for the exact copied/restorable
  evidence already recorded; it is not a real-book claim and not broad GnuCash compatibility.
- Compatibility wording guard: supported-version write compatibility remains pending and claims must stay
  tied to synthetic/disposable or copied/restorable evidence only.

## Gates still blocking #36 closure

#36 must stay open unless a maintainer/PM review explicitly accepts every blocker below and states the
original issue scope is satisfied.

1. Supported-version write compatibility evidence
   - Pending: Desktop/version-specific write compatibility has not been accepted across supported
     GnuCash versions.
   - Required before closure: redacted evidence tied to synthetic/disposable or copied/restorable
     fixtures only, with no broad backend/Desktop/version support claim.

2. Future copied/restorable mutation evidence packet
   - Pending: future mutation evidence is not authorized by this audit.
   - Required before closure if pursued: same-context owner + PM authorization, Desktop closed for the
     target copy, outside-git copied/restorable fixture provenance, independent backup, preflight,
     route family/count scope, backup, read-back, audit, lock/ contention, restore/rollback,
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

- Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account
  name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated,
  committed, or posted.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Enabled write-alpha/writebeta remains `APP_ENV=test` gated.
- Recommendation: keep #36 open.
