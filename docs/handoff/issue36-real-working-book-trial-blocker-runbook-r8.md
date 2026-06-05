# Issue #36 real working-book trial blocker runbook R8 handoff

Date: 2026-06-05
Task id: `real-working-book-trial-blocker-runbook-r8`

## Scope

Allowed scope was `docs/**` and `docs/handoff/**` only. No GnuCash book was
opened, copied, inspected, or mutated. No dogfood, write enablement, release,
tag, package, or image publication was performed.

## Result

Updated `docs/write-alpha/real-working-book-trial-runbook.md` with R8
non-mutating blocker detail:

- a pre-mutation stop/go register for packet identity, mutation budget, target
  class, backup, writer exclusion, runtime gate, evidence shape, and no-release
  posture;
- owner approval wording constraints that keep approval narrow, same-context, and
  free of private evidence;
- minimum rollback evidence rows that keep missing or inconsistent evidence in
  `rollback review` or blocked status, not success.

The runbook still explicitly says a real working-book trial is blocked and is not
authorized for issue #36.

## Verification

Commands required for this task were run after the runbook and this handoff were
written:

```bash
python3 scripts/check_public_status.py
python3 scripts/check_markdown_readability.py
python3 scripts/check_tracked_hygiene.py
git diff --check
```

See final worker status for observed output.

## Safety notes

- Documentation-only tracked changes under `docs/**` and `docs/handoff/**`.
- Mutation counts for this task: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default write posture.
- Enabled write paths remain `APP_ENV=test` gated.
- No real/private/original/working/only-copy book was opened, copied, inspected,
  or mutated.
- No GnuCash book, SQLite book, app DB, backup, CSV export, screenshot, `.env`,
  token, key, cert, private path, account name, transaction description, memo,
  amount, or raw private evidence was committed or posted.
- No public write beta, release, stable, production-ready, security-audited,
  broad compatibility, or only-copy safety claim is made.
