# Issue #36 real working-book trial blocker runbook R4 handoff

Date: 2026-06-05
Task id: `real-working-book-trial-blocker-runbook-r4`

## Scope

Allowed scope was `docs/**` and `docs/handoff/**` only. No GnuCash book was
opened, copied, inspected, or mutated. No dogfood, write enablement, release,
tag, package, or image publication was performed.

## Result

Updated `docs/write-alpha/real-working-book-trial-runbook.md` with R4
non-mutating gate detail:

- future trial pre-authorization runbook that keeps the trial blocked until a
  separate same-context approval packet passes every gate;
- owner/PM approval freshness and mismatch rules;
- minimum rollback proof expectations using redacted pass/fail summaries only.

The runbook still explicitly says a real working-book trial is blocked and is not
authorized for issue #36.

## Verification

Commands run after all tracked docs changes were written:

```bash
python3 scripts/check_public_status.py
python3 scripts/check_markdown_readability.py
python3 scripts/check_tracked_hygiene.py
git diff --check
```

Observed output:

```text
public-status-guard: ok
markdown-readability-guard: ok (10 docs checked)
Tracked hygiene check passed (1867 tracked paths inspected).
```

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
