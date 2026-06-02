# Overnight worker 04 — #22 Desktop fixture candidate acceptance preflight

Worker task ID: `overnight-2026-06-02-worker-04`

Target issue/package: #22 Add compatibility fixtures from real GnuCash versions — Desktop-generated fixture acceptance preflight gate.

## Summary of changes

- Added a fail-closed Desktop-generated synthetic fixture candidate metadata gate in `apps/api/app/compatibility_matrix.py`.
- Added `scripts/preflight_desktop_fixture_candidate.py`, a non-mutating CLI that reads redacted JSON metadata only and never opens a GnuCash book.
- Hardened matrix classification so `--read-only-validation-passed` alone is not enough for a tested Desktop row: Desktop-generated metadata stays blocked/manual unless the candidate preflight markers also pass.
- Updated compatibility docs and project status to keep #22 blockers explicit: this is an acceptance gate only, not a fixture-generation result or Desktop-version support claim.
- Fixed the matrix CLI regression test after CI showed its old happy-path metadata lacked the new preflight markers.

No GUI GnuCash was launched. No real/private/original/working/only-copy GnuCash book was opened, copied, searched, inspected, or mutated.

## Files changed

- `apps/api/app/compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix_cli.py`
- `scripts/preflight_desktop_fixture_candidate.py`
- `docs/gnucash-compatibility.md`
- `PROJECT_STATUS.md`
- `docs/handoff/overnight-2026-06-02-worker-04.md`

## RED/GREEN TDD evidence

RED before implementation:

```bash
cd apps/api && pytest \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_accepts_only_synthetic_disposable_metadata \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_fails_closed_for_missing_markers \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_rejects_private_or_copied_evidence \
  tests/test_compatibility_matrix.py::test_desktop_fixture_metadata_stays_blocked_when_preflight_marker_missing \
  -q
```

Result before implementation: collection/import failed because `CandidatePreflightError` and `validate_desktop_fixture_candidate_preflight` did not exist.

GREEN after implementation:

```bash
cd apps/api && pytest \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_accepts_only_synthetic_disposable_metadata \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_fails_closed_for_missing_markers \
  tests/test_compatibility_matrix.py::test_desktop_fixture_candidate_preflight_rejects_private_or_copied_evidence \
  tests/test_compatibility_matrix.py::test_desktop_fixture_metadata_can_only_be_tested_after_explicit_read_only_validation \
  tests/test_compatibility_matrix.py::test_desktop_fixture_metadata_stays_blocked_when_preflight_marker_missing \
  -q
```

Result: `5 passed`.

Additional CLI/doc-focused matrix run:

```bash
cd apps/api && pytest tests/test_compatibility_matrix.py tests/test_compatibility_matrix_cli.py -q
```

Result: `16 passed`.

## Verification run

Required/local checks run from `/home/val/projects/gnucash-web-companion`:

```bash
cd apps/api && pytest tests/test_compatibility_matrix.py tests/test_gnucash_compatibility_metadata.py tests/test_write_alpha_compatibility_check.py tests/test_safe_compatibility_report.py tests/test_validate_compatibility_report.py -q
cd ../..
git diff --check
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
JWT_SECRET=*** APP_ADMIN_PASSWORD=*** docker compose config --quiet
```

Results:

- Focused compatibility/preflight subset: `37 passed` (existing piecash/SQLAlchemy warnings only).
- `git diff --check`: passed.
- `python3 scripts/check_public_status.py`: `public-status-guard: ok`.
- `python3 scripts/check_tracked_hygiene.py`: `Tracked hygiene check passed (1730 tracked paths inspected).`
- `docker compose config --quiet`: passed.
- Added-line static security scan for hardcoded secrets, shell injection, eval/exec, pickle, and SQL formatting patterns: no findings.
- Full backend suite after CI regression diagnosis:

```bash
cd apps/api && pytest tests/ -q
```

Result: `653 passed, 38 warnings`.

Independent reviewer subagent was not used because repository `AGENTS.md` explicitly says not to use `delegate_task` unless the user overrides it. Local static scan and test gates passed.

## CI

First pushed implementation commit: `a394543655a9693f2bdd53b805e06271181ef4fb`.

CI run for first commit failed because `tests/test_compatibility_matrix_cli.py::test_matrix_cli_requires_explicit_validation_flag_for_tested_desktop_row` still used old metadata without the new preflight markers:

https://github.com/valentusys/gnucash-web-companion/actions/runs/26798298673

Fix commit: `2e86634e8004d1f5161e7beb9fd3eb188c9f68e4`.

CI run for the fix commit passed:

https://github.com/valentusys/gnucash-web-companion/actions/runs/26798667904

## Safety summary

- Tests use synthetic dictionaries and tmp_path JSON only.
- The new preflight CLI reads JSON metadata only; it never opens, copies, searches, inspects, or mutates a GnuCash book.
- No GUI GnuCash launch and no `$DISPLAY` dependency.
- No real/private/original/working/only-copy book opened/copied/searched/inspected/mutated.
- No GnuCash book, SQLite book, app DB, backup, CSV/export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence committed.
- `GNUCASH_WRITES_ENABLED=false` default preserved.
- `APP_ENV=test` and write gates not weakened.
- No release/tag/package/image published.
- #22 not closed.

## Issue update

Updated #22 with what changed, tests run, safety notes, keep-open recommendation, remaining blockers, commits, and CI link.

Recommendation in issue comment: keep #22 open.

## Remaining blockers for #22

#22 still needs the original Desktop-generated fixture scope:

1. Isolated disposable GUI/manual-safe GnuCash Desktop environment.
2. Synthetic/disposable SQLite fixture created/saved by real GnuCash Desktop with no private data.
3. Redacted candidate metadata that passes `scripts/preflight_desktop_fixture_candidate.py`.
4. Default-read-only validation against that fixture with `GNUCASH_WRITES_ENABLED=false`.
5. Compatibility docs/matrix update only after reviewed safe evidence exists.

## Recommendation for supervisor's next package

Keep #22 open. The next package should either:

- produce the actual isolated disposable GUI/manual-safe Desktop-generated synthetic SQLite fixture and run the new preflight plus default-read-only validation; or
- further document/rehearse the isolated GUI/manual-safe fixture-generation runbook without touching host/private books.

Do not close #22 until an actual Desktop-generated synthetic fixture exists and passes redacted preflight plus default-read-only validation.
