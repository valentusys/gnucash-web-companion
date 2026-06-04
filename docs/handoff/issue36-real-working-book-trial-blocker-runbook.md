# Issue #36 real working-book trial blocker runbook handoff

Date: 2026-06-05

## Scope

Task: `real-working-book-trial-blocker-runbook` from
`docs/autonomy/backlog-policies/issue36-owner-writebeta.md`.

Allowed scope was docs-only. No GnuCash book was opened, copied, inspected, or
mutated. No dogfood, write enablement, release publication, tag, package, or
image publication was performed.

## Result

Added `docs/write-alpha/real-working-book-trial-runbook.md` as a conservative
future-trial blocker checklist. It explicitly says the real working-book trial is
not authorized and remains blocked for issue #36.

Updated `docs/write-alpha/owner-writebeta-operating-guide.md` to point to the
new runbook while preserving:

- `GNUCASH_WRITES_ENABLED=false` as the default posture;
- `APP_ENV=test` gating for enabled write paths;
- real/private/original/only-copy books blocked as write targets;
- no public write beta, production-ready, stable, security-audited, broad
  compatibility, or only-copy safety claim.

## Current safety posture

Continue only with non-mutating documentation, guard checks, tests, or planning
unless a future owner and PM approval appears in the same execution context as a
specific trial package.

Any future real working-book trial still needs explicit owner approval, PM
approval, a non-original/non-only-copy target, independent backup and
restore-to-copy expectations, redacted evidence rules, disabled reset, and a
post-reset disabled probe.
