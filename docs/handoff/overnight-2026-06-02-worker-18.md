# Worker handoff: overnight-2026-06-02-worker-18

UTC handoff time: 2026-06-02T10:33:00Z

## Package

Compatibility Markdown readability guard package for issue #28.

## Scope completed

Non-mutating #28 Markdown readability package. It edited public/status docs, guard scripts, tests,
and current handoff text only. No GnuCash book, SQLite book, app DB, backup, export, screenshot,
private path, account name, memo, amount, or raw private evidence was created, opened, copied,
mutated, committed, or posted.

Changed files:

- `docs/gnucash-compatibility.md`
- `scripts/check_markdown_readability.py`
- `apps/api/tests/test_markdown_readability_docs.py`
- `scripts/check_public_status.py`
- `docs/handoff/overnight-2026-06-02-worker-17.md`
- `PROJECT_STATUS.md`
- `docs/handoff/overnight-2026-06-02-worker-18.md`

## What changed

- Reflowed the top of `docs/gnucash-compatibility.md` so the current #22 blocker, synthetic-only
  evidence boundary, and unclaimed PostgreSQL/MySQL/MariaDB boundary are visible in raw Markdown
  before the long matrix tables.
- Added `docs/gnucash-compatibility.md` to `scripts/check_markdown_readability.py` default docs.
- Updated the readability guard to require top #22 Desktop fixture blocker navigation in the
  compatibility doc.
- Moved the current handoff default from worker 13 to worker 17 and reflowed worker 17 long prose so
  the new guard passes.
- Updated the public-status guard compatibility check to accept required fragments across wrapped
  Markdown lines.
- Added focused tests proving the compatibility doc is guarded and fails closed when top blocker
  navigation is missing.
- Updated `PROJECT_STATUS.md` with this package and current handoff pointer.

## Verification

Completed locally:

```text
cd apps/api && pytest -q tests/test_markdown_readability_docs.py tests/test_public_status_guard.py
40 passed in 0.10s

python3 scripts/check_markdown_readability.py
markdown-readability-guard: ok (9 docs checked)

python3 scripts/check_public_status.py
public-status-guard: ok

python3 scripts/check_tracked_hygiene.py
Tracked hygiene check passed (1747 tracked paths inspected).

git diff --check
passed
```

## Safety summary

- CREATE/PATCH/DELETE performed: 0/0/0.
- No real/private/original/working/only-copy GnuCash book was opened, copied, or mutated.
- No Desktop fixture was generated.
- No write-alpha/create/patch/delete harness was run.
- `GNUCASH_WRITES_ENABLED=false` default preserved.
- `APP_ENV=test`, owner-writebeta, write-alpha, and public-readonly gates were not weakened.
- No release/tag/package/image was published.
- No broad Desktop-version, all-backend, public-write, stable, production, real-book safety, or
  security-audited claim was added.

## Issue #28 update

Recommendation: keep #28 open unless a maintainer decides the remaining wider-announcement Markdown
cleanup is sufficient. This package improves and guards the compatibility doc source readability;
older historical handoffs/status archives can still be cleaned opportunistically without whole-repo
reflow.

## Commit / CI

- Implementation commit: fill after commit.
- Issue comment: fill after issue update.
- CI: fill after push if GitHub Actions run is available.

## Remaining blockers for #28

- Optional broader raw-Markdown cleanup for older release/status/handoff pages not covered by the
  current guard.
- Preserve current release/no-release and safety language while cleaning source readability.

## Next supervisor recommendation

Continue to #36 with non-mutating controlled-write readiness guard/docs work if #28 broader cleanup
is not urgent.
