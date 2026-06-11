# Issue #44 real-book trial preflight report

Date: 2026-06-11
Issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)
Status: **BLOCKED before CREATE**

## Scope

This is a preflight-only report. It does not authorize or execute a real-book mutation.

Explicitly not performed:

- CREATE: 0
- PATCH: 0
- DELETE: 0
- batch: 0
- dogfood: not run
- release/tag/package/image publication: not run
- public write beta: not run

No raw private target path, account name, transaction description, memo, amount, book, backup,
screenshot, token, key, cert, or `.env` content is committed in this report.

## Repository and issue checks

- Repository working tree before report: clean.
- Branch: `main`.
- Local `main` matched `origin/main` before this report was created.
- #44 state: open.
- Public docs preserve that #44 is not mutation approval.
- `GNUCASH_WRITES_ENABLED=false` default is preserved by repository guards.
- Enabled write flows remain `APP_ENV=test` gated by repository guards.

## Non-mutating runtime checks

- GnuCash Desktop exact process check: no `gnucash` process observed.
- GnuCash CLI exact process check: no `gnucash-cli` process observed.
- Mutation performed by this preflight: false.
- Runtime writes enabled during preflight: false.
- Future enabled-write runtime was not armed during this preflight.

## Capability checks for a later approved CREATE

Static source/runbook checks show the later CREATE path has documented or implemented support for:

- route backup immediately before CREATE;
- restore verification helper availability;
- read-back after CREATE;
- redacted audit evidence capture;
- default-disabled reset;
- disabled-write probes after reset;
- CREATE/PATCH/DELETE route-family presence for later post-reset blocked-write probes;
- audit summary route presence.

## Blockers

The first real-book CREATE trial is **not ready** from this preflight alone.

Exact blockers:

1. Target-specific private handle was not recorded in this tracked report, and the local preflight helper
   requires a target path to verify target readability, outside-git class, target-specific lock hints,
   and target fingerprint markers.
2. Independent backup existence was not target-verified in this tracked report.
3. Restore path/proof was not target-verified in this tracked report.
4. Target-specific lock/no-concurrent-writer state cannot be proven without the private target handle.
5. Future mutation runtime must be armed only in the mutation context with `APP_ENV=test`; it was not
   armed during this preflight-only run.

## READY/BLOCKED verdict

**BLOCKED** until a later same-context owner/PM approval provides the private target handle and allows
redacted target-specific verification before CREATE.

## Exact owner approval needed before CREATE

A later CREATE trial requires explicit same-context owner/PM approval with:

1. Exact redacted target class.
2. Exact operation count: CREATE 1, PATCH 0, DELETE 0, batch 0.
3. Confirmation that GnuCash Desktop is closed for the target.
4. Confirmation that no concurrent writer or lock is active for the target.
5. Confirmation that an independent backup exists.
6. Confirmation that restore path/proof was verified before mutation.
7. Approval to take route backup immediately before CREATE.
8. Approval to perform read-back and redacted audit capture after CREATE.
9. Approval to reset writes to disabled immediately after CREATE.
10. Approval to run disabled-write probes after reset.
11. Confirmation that committed or issue-posted evidence remains redacted only.

If any item is absent, stop before mutation.
