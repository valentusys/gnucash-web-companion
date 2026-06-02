# Overnight worker 12 handoff — #22 compatibility matrix report guard

Worker task ID: `overnight-2026-06-02-worker-12`

UTC handoff time: 2026-06-02T06:49:51Z

## Scope completed

Added a non-mutating compatibility matrix report renderer/checker to the existing #22 matrix helper.
The helper works from already-redacted/classified synthetic metadata rows only.

Changed files:

- `PROJECT_STATUS.md`
- `apps/api/app/compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix.py`
- `docs/gnucash-compatibility.md`
- `docs/handoff/overnight-2026-06-02-worker-12.md`

## TDD evidence

RED:

```text
cd apps/api && pytest tests/test_compatibility_matrix.py::test_compatibility_matrix_report_renders_conservative_operator_summary tests/test_compatibility_matrix.py::test_compatibility_matrix_report_checker_fails_closed_for_unsafe_claims_and_private_values tests/test_compatibility_matrix.py::test_unsafe_broad_support_phrase_list_covers_report_checker_policy -q
ImportError: cannot import name 'CompatibilityReportError' from 'app.compatibility_matrix'
1 error
```

GREEN:

```text
cd apps/api && pytest tests/test_compatibility_matrix.py::test_compatibility_matrix_report_renders_conservative_operator_summary tests/test_compatibility_matrix.py::test_compatibility_matrix_report_checker_fails_closed_for_unsafe_claims_and_private_values tests/test_compatibility_matrix.py::test_unsafe_broad_support_phrase_list_covers_report_checker_policy -q
3 passed in 0.07s
```

Focused full matrix regression:

```text
cd apps/api && pytest tests/test_compatibility_matrix.py -q
16 passed in 0.11s
```

## Guard behavior

`render_compatibility_matrix_report(rows)` renders a conservative operator summary from classified
`CompatibilityMatrixRow` values.

`check_compatibility_matrix_report(report)` validates rendered summaries and fails closed unless they
preserve all of these boundaries:

- tested synthetic/disposable evidence only;
- manual fixture blocker wording;
- unclaimed backend boundary;
- Desktop fixture candidate gate status;
- no broad production, stable, security, public-write, all-version, or real-book claim.

The checker also rejects private-looking path, account, memo, description, and amount evidence in the
rendered summary.

## Verification

Final required verification before the implementation commit:

```text
cd apps/api && pytest tests/test_compatibility_matrix.py -q
16 passed in 0.11s

cd apps/api && pytest tests/test_markdown_readability_docs.py -q
7 passed in 0.03s

python3 scripts/check_markdown_readability.py
markdown-readability-guard: ok (6 docs checked)

python3 scripts/check_public_status.py
public-status-guard: ok

python3 scripts/check_tracked_hygiene.py
Tracked hygiene check passed (1740 tracked paths inspected).

git diff --check
passed

JWT_SECRET=*** APP_ADMIN_PASSWORD=*** docker compose config --quiet
passed
```

Static added-line security scan:

```text
git diff -- apps/api/app/compatibility_matrix.py apps/api/tests/test_compatibility_matrix.py docs/gnucash-compatibility.md PROJECT_STATUS.md | grep '^+' | grep -iE '(api_key|secret|password|token|passwd)\s*=\s*["'"''][^"'"'']{6,}["'"'']|os\.system\(|subprocess.*shell=True|\beval\(|\bexec\(|pickle\.loads?\(|execute\(f"|\.format\(.*SELECT|\.format\(.*INSERT' || true
```

No findings.

Independent reviewer note: the task explicitly said not to use `delegate_task`, and `AGENTS.md` also
forbids subagents unless explicitly overridden. No reviewer subagent was launched.

## Safety summary

- CREATE/PATCH/DELETE GnuCash mutations performed: 0/0/0.
- No real/private/original/working/only-copy GnuCash book was opened, copied, searched, or mutated.
- No GnuCash book, SQLite book, app DB, backup, CSV export, screenshot, `.env`, token, key, cert,
  private path, account name, transaction description, memo, amount, or raw private evidence was added.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` and write gates were not weakened.
- No public write beta, release, tag, package, image, stable, production, or security-audited claim was
  added.

## Issue #22 update

Recommendation: keep #22 open.

Completed in this package: a report renderer/checker now turns existing synthetic/redacted matrix rows
into a conservative operator summary and rejects broad support wording or private-looking evidence.

Remaining #22 blockers:

1. Isolated disposable GUI/manual-safe GnuCash Desktop environment.
2. Synthetic/disposable SQLite fixture created and saved by real GnuCash Desktop with no private data.
3. Redacted metadata collection for that fixture.
4. Metadata preflight plus default-read-only validation with `GNUCASH_WRITES_ENABLED=false`.
5. Reviewed compatibility docs/matrix update only after that safe evidence exists.

## Commit / CI

Implementation commit SHA: `62c02c30326699f163954489090ece0adbb6bc6c`.

Handoff commit SHA: `28b71c713e3d5af608c24648d176f22e3a6a99a9`.

CI for pushed handoff SHA update `18640c1505c090ae9c3db97fe169ba7d2ffa09e0`: completed/success:
https://github.com/valentusys/gnucash-web-companion/actions/runs/26803543504.

## Next supervisor recommendation

Keep #22 open. This package improves operator-facing readiness but does not complete the original
Desktop-generated real-version fixture evidence scope.
