# Overnight worker 05 — #22 CI fix and handoff completion

Worker task ID: `overnight-2026-06-02-worker-05`

Package: CI fix and handoff completion for Desktop fixture candidate preflight.

Target issue: #22 Add compatibility fixtures from real GnuCash versions.

Timestamp: 2026-06-02T14:38:38+10:00

## Summary

Worker 05 diagnosed the worker 04 CI failure, preserved the Desktop fixture candidate preflight behavior, documented the missing worker 04 handoff from public repo/log evidence, and added this worker 05 handoff.

The code fix was already present on `origin/main` before the handoff-doc commit:

- Fix commit: `2e86634e8004d1f5161e7beb9fd3eb188c9f68e4`
- Commit title: `test: align matrix cli preflight fixture`
- Changed file: `apps/api/tests/test_compatibility_matrix_cli.py`

Final handoff-doc commit: `5a2747eb85dc356f1e3e122249b6d85db612e7c4`.

## CI failure root cause

Failed run investigated:

https://github.com/valentusys/gnucash-web-companion/actions/runs/26798298673

`gh run view 26798298673 --log-failed --repo valentusys/gnucash-web-companion` initially hit one TLS handshake timeout, then a retry returned the failed backend test log.

Failure:

```text
FAILED tests/test_compatibility_matrix_cli.py::test_matrix_cli_requires_explicit_validation_flag_for_tested_desktop_row
AssertionError: assert 'manual_fixture_blocked' == 'tested_synthetic_fixture'
```

Root cause: worker 04 changed Desktop-generated synthetic matrix rows to require both the explicit CLI `--read-only-validation-passed` flag and the new metadata-level candidate preflight fields. The CLI test used the flag but omitted the new safe metadata markers, so the stricter implementation correctly classified it as `manual_fixture_blocked`.

Smallest safe fix: update only the CLI test fixture metadata to include the required synthetic/disposable markers:

- `fixture_scope`: `synthetic`
- `synthetic_disposable_evidence`: `operator-created-disposable-empty-book`
- `default_read_only_validation`: `passed`

No production code was weakened.

## Files changed by worker 05 package

Code fix commit `2e86634e8004d1f5161e7beb9fd3eb188c9f68e4`:

- `apps/api/tests/test_compatibility_matrix_cli.py`

Handoff-doc commit `5a2747eb85dc356f1e3e122249b6d85db612e7c4`:

- `docs/handoff/overnight-2026-06-02-worker-04.md`
- `docs/handoff/overnight-2026-06-02-worker-05.md`

## Verification commands and results

Required verification from `/home/val/projects/gnucash-web-companion`:

```bash
cd apps/api && pytest tests/test_compatibility_matrix.py tests/test_compatibility_matrix_cli.py tests/test_gnucash_compatibility_metadata.py tests/test_write_alpha_compatibility_check.py tests/test_safe_compatibility_report.py tests/test_validate_compatibility_report.py -q
```

Result: `40 passed, 21 warnings in 1.92s` (existing piecash/SQLAlchemy warnings only).

```bash
git diff --check
```

Result: passed.

```bash
python3 scripts/check_public_status.py
```

Result: `public-status-guard: ok`.

```bash
python3 scripts/check_tracked_hygiene.py
```

Result: `Tracked hygiene check passed (1730 tracked paths inspected).`

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Result: passed.

Static added-line scan for hardcoded secrets, shell injection, eval/exec, pickle, and SQL formatting patterns: no findings.

## CI status

Fix commit CI:

- Run: https://github.com/valentusys/gnucash-web-companion/actions/runs/26798667904
- Status: completed, conclusion: success.

Final handoff-doc commit CI:

- Run: https://github.com/valentusys/gnucash-web-companion/actions/runs/26798850525
- Status: in progress at issue-update time for commit `87bc5e458f8ce8fe5435f3e1884856f42eab4df2`.

## GitHub issue update

Issue #22 update: https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4598784094.

Recommendation left in issue: keep #22 open because the real issue scope still needs isolated Desktop-generated synthetic fixture evidence and default-read-only validation.

## Safety summary

- No real/private/original/working/only-copy GnuCash book was touched.
- No GnuCash book, SQLite book, app DB, backup, CSV/export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence was committed.
- The fix uses only synthetic/disposable metadata marker strings.
- `GNUCASH_WRITES_ENABLED=false` default preserved.
- `APP_ENV=test` and write gates were not weakened.
- No public write beta was enabled.
- No production/stable/security-audited claims were made.
- No release, tag, package, or image was published.
- #22 remains open.

## Remaining blockers for #22

#22 is not complete. Remaining blockers:

1. Isolated disposable GUI/manual-safe GnuCash Desktop environment.
2. Synthetic/disposable SQLite fixture created/saved by real GnuCash Desktop with no private data.
3. Redacted metadata collection for that fixture.
4. Default-read-only validation against that fixture.
5. Compatibility docs/matrix update only after reviewed safe evidence exists.

## Next supervisor recommendation

Keep #22 open. Next package should produce or document the isolated Desktop-generated synthetic fixture workflow without touching host/private books, then run redacted metadata collection plus default-read-only validation before any compatibility matrix row is promoted.
