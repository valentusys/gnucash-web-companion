# Overnight worker 03 — #22 Desktop tooling probe hardening

Worker task ID: `overnight-2026-06-02-worker-03`

Target issue/package: #22 Add compatibility fixtures from real GnuCash versions — Desktop tooling probe hardening with mocked outputs.

## Summary of changes

- Hardened `apps/api/scripts/probe_gnucash_desktop_tooling.py` so successful `--version` output is accepted only when it is:
  - bounded by `MAX_VERSION_OUTPUT_CHARS`;
  - free of path-like, account-like, memo-like, description-like, or amount-like content;
  - unambiguous enough to include a `GnuCash X.Y` style version token.
- Hardened `scripts/write_alpha_compatibility_check.py` so a mocked successful `gnucash-cli --report ...` result still fails closed if `gnucash-cli --version` output is unsafe, overlong, private-looking, or ambiguous.
- Added mocked-output pytest coverage for private-looking successful version output, ambiguous/overlong version output, and checker fail-closed behavior.
- Updated `docs/gnucash-compatibility.md` and `PROJECT_STATUS.md` with the conservative status: no Desktop-generated fixture was produced; #22 remains open.

No GUI GnuCash was launched. No real/private/original/working/only-copy GnuCash book was opened, copied, searched, inspected, or mutated.

## Files changed

- `apps/api/scripts/probe_gnucash_desktop_tooling.py`
- `scripts/write_alpha_compatibility_check.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_write_alpha_compatibility_check.py`
- `docs/gnucash-compatibility.md`
- `PROJECT_STATUS.md`
- `docs/handoff/overnight-2026-06-02-worker-03.md`

## RED/GREEN TDD evidence

RED before implementation:

```bash
cd apps/api && pytest \
  tests/test_gnucash_compatibility_metadata.py::test_desktop_tooling_probe_fails_closed_on_private_success_output \
  tests/test_gnucash_compatibility_metadata.py::test_desktop_tooling_probe_fails_closed_on_ambiguous_or_overlong_version \
  tests/test_write_alpha_compatibility_check.py::test_desktop_checker_fails_closed_on_private_or_ambiguous_version_output \
  -q
```

Result before implementation: `3 failed`.

GREEN after implementation: same command passed: `3 passed`.

Focused compatibility subset after implementation:

```bash
cd apps/api && pytest \
  tests/test_gnucash_compatibility_metadata.py \
  tests/test_write_alpha_compatibility_check.py \
  tests/test_safe_compatibility_report.py \
  tests/test_validate_compatibility_report.py \
  -q
```

Result: `24 passed`.

## Verification run

Required/local checks run from `/home/val/projects/gnucash-web-companion`:

```bash
cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_write_alpha_compatibility_check.py tests/test_safe_compatibility_report.py tests/test_validate_compatibility_report.py -q
cd ../..
git diff --check
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
JWT_SECRET=dummy-...cret APP_ADMIN_PASSWORD=*** docker compose config --quiet
```

Results:

- pytest compatibility subset: `24 passed` (existing piecash/SQLAlchemy warnings only).
- `git diff --check`: passed.
- `python3 scripts/check_public_status.py`: `public-status-guard: ok`.
- `python3 scripts/check_tracked_hygiene.py`: `Tracked hygiene check passed (1728 tracked paths inspected).`
- `docker compose config --quiet`: passed.
- Static added-line scan for hardcoded secrets, shell injection, eval/exec, pickle, and SQL formatting patterns: no findings.
- Independent review: passed. Reviewer reported no security concerns and no logic errors; only non-blocking suggestions around dead-code clarity and shared regex drift risk.

## CI

Implementation commit pushed to `main`: `ce620cd7df35ef7b59232cd1d30922dac85222b8`.

CI run: https://github.com/valentusys/gnucash-web-companion/actions/runs/26797616466

Status: `completed`, conclusion: `success`.

## Safety summary

- Tests use mocked subprocess outputs and synthetic strings only.
- No GUI GnuCash launch and no `$DISPLAY` dependency.
- No real/private/original/working/only-copy book opened/copied/searched/inspected/mutated.
- No GnuCash book, SQLite book, app DB, backup, CSV/export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, or amount evidence committed.
- `GNUCASH_WRITES_ENABLED=false` default preserved.
- `APP_ENV=test` and write gates not weakened.
- No release/tag/package/image published.
- #22 not closed.

## Issue update

Updated #22 with what changed, tests run, safety notes, keep-open recommendation, remaining blockers, commit SHA, and CI link:

https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4598613805

Recommendation in issue comment: keep #22 open.

## Remaining blockers for #22

#22 still needs the original Desktop-generated fixture scope:

1. Isolated disposable GUI/manual-safe GnuCash Desktop environment.
2. Synthetic/disposable SQLite fixture created/saved by real GnuCash Desktop with no private data.
3. Redacted metadata collection for that fixture.
4. Default-read-only validation against that fixture.
5. Compatibility docs/matrix update only after reviewed safe evidence exists.

## Recommendation for supervisor's next package

Keep #22 open and pick the next package around the isolated Desktop-generated synthetic fixture path:

- either build a disposable GUI/manual-safe fixture-generation runbook/container workflow without touching host/private books;
- or add another fail-closed preflight gate for accepting an operator-supplied Desktop-generated synthetic fixture before any metadata/read-only validation.

Do not close #22 until an actual Desktop-generated synthetic fixture exists and passes redacted metadata plus default-read-only validation.
