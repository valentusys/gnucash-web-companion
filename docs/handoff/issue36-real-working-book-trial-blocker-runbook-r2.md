# Issue #36 real working-book trial blocker runbook R2 handoff

Date: 2026-06-05

## Scope

Task: `real-working-book-trial-blocker-runbook-r2` from
`docs/autonomy/backlog-policies/issue36-owner-writebeta.md`.

Allowed scope was docs-only. No GnuCash book was opened, copied, inspected, or
mutated. No dogfood, write enablement, release publication, tag, package, or
image publication was performed.

## Result

Updated `docs/write-alpha/real-working-book-trial-runbook.md` with R2 sections
that make the future trial gate stricter and more explicit:

- approval packet requirements before any owner or PM decision;
- owner and PM gate wording rules for same-context, exact-packet approval;
- rollback decision tree for pre-mutation stops, post-mutation rollback review,
  restore-to-copy proof, reset, and disabled-probe failure.

The runbook still explicitly says a real working-book trial is blocked and is not
authorized for issue #36.

## Current safety posture

Continue only with non-mutating documentation, guard checks, tests, or planning
unless a future owner and PM approval appears in the same execution context as a
specific bounded trial package.

The default posture remains `GNUCASH_WRITES_ENABLED=false`; enabled write paths
remain `APP_ENV=test` gated; real/private/original/working/only-copy books remain
blocked; no public write beta, release, production-ready, stable,
security-audited, broad compatibility, or only-copy safety claim is made.

## Verification

Run after this handoff is created:

- `python3 scripts/check_public_status.py`
- `python3 scripts/check_markdown_readability.py`
- `python3 scripts/check_tracked_hygiene.py`
- `git diff --check`
