# Controlled-write readiness dashboard for #36

Status: keep #36 open. This dashboard is a non-mutating index of evidence and gaps.
It is not release approval and not authorization to mutate any book.

## Snapshot

- Release decision: NO_RELEASE.
- Public posture: no public write beta; no stable, production-ready, or security-audited
  claim; no broad compatibility claim; no real/private/original/working/only-copy safety claim,
  including no only-copy safety claim.
- Defaults: `GNUCASH_WRITES_ENABLED=false` remains default and enabled write-alpha/writebeta routes remain `APP_ENV=test` gated.
- Mutation counts for this dashboard package: CREATE 0 / PATCH 0 / DELETE 0.
- Book boundary: no original, private, real working, or only-copy GnuCash book is a safe write target.

## Evidence index

| Evidence area | Current evidence | Closure status |
|---|---|---|
| State-machine evidence | `docs/write-alpha/owner-writebeta-state-machine.md`, route/state tests, reset/default-disabled behavior, and audit-summary tests cover fail-closed state transitions. | Helpful, but not enough for #36 closure by itself. |
| Copied-book evidence | Historical copied/restorable CREATE/PATCH/DELETE packets are accepted only for their exact copied/restorable scopes. | Not a real-book claim and not broad GnuCash compatibility. |
| Restore evidence | Restore and recovery runbooks/tests distinguish restore-to-copy and recovery drills from destructive restore or real-book safety. | Needs continued guard coverage before closure. |
| Default-disabled probes | Disabled-probe/reset evidence and committed config guards preserve `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test`. | Must remain green on every closure attempt. |
| Compatibility gaps | Supported-version write compatibility remains pending and evidence must stay tied to synthetic/disposable or copied/restorable fixtures only. | Blocks #36 closure. |

## Future copied/restorable mutation packet requirement

Any future copied/restorable dogfood package requires same-context owner + PM authorization before execution. The authorization must name:

1. the copied/restorable target class outside git;
2. the route family and operation counts;
3. backup/read-back/audit/lock/restore/reset expectations;
4. redaction requirements;
5. confirmation that no original/private/real-working/only-copy book is used.

Absent that authorization, only non-mutating guards, docs, and tests are allowed.

## Closure decision rule

Keep #36 open until a maintainer/PM review accepts every remaining gate in
`docs/write-alpha/issue-36-remaining-gates.md`, current CI/guards are green, and the
release decision is explicitly recorded. Default is NO_RELEASE.

## Safety result

No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert, private
path, account name, transaction description, memo, amount, or raw private evidence was
opened, copied, mutated, committed, or posted.
