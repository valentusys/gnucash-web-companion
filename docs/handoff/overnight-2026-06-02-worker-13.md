# Worker handoff: overnight-2026-06-02-worker-13

## Scope

Issue: #28 Improve markdown source readability before wider announcement.

Package: CHANGELOG and release-doc readability guard package.

## Implementation commit

- Primary implementation commit: `d252204` (`docs: harden release markdown readability guard`).
- Handoff commit: created after the implementation commit so this file can record the implementation SHA.

## Changed files

- `CHANGELOG.md`
- `docs/release/v0.5.0-public-readonly-beta-notes.md`
- `docs/release/v0.5.0-public-readonly-beta-final-gate.md`
- `scripts/check_markdown_readability.py`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-2026-06-02-worker-13.md`

## TDD cycle

RED:

```bash
cd apps/api && pytest tests/test_markdown_readability_docs.py::test_release_docs_have_conservative_readable_status_boundaries -q
```

Observed failure: the new test expected the release notes and final gate to be part of the
readability guard's default checked docs, but `DEFAULT_DOCS` only covered README/README.ru,
PROJECT_STATUS, CHANGELOG, the readability guide, and worker-11 handoff.

GREEN:

```bash
cd apps/api && pytest tests/test_markdown_readability_docs.py::test_release_docs_have_conservative_readable_status_boundaries -q
```

Observed result: `1 passed`.

## Verification

Required local checks passed:

```bash
python3 scripts/check_markdown_readability.py
cd apps/api && pytest tests/test_markdown_readability_docs.py -q
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
git diff --check
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Observed summary:

- `markdown-readability-guard: ok (7 docs checked)`
- `8 passed` for `tests/test_markdown_readability_docs.py`
- `public-status-guard: ok`
- `Tracked hygiene check passed (1741 tracked paths inspected).`
- `git diff --check`: passed with no output
- Docker Compose config validation: passed with no output

## Safety summary

- No GnuCash books, SQLite books, app DBs, backups, CSV exports, screenshots, `.env`, tokens,
  keys, certs, private paths, account names, transaction descriptions, memos, amounts, or raw
  private evidence were added.
- No application behavior changed beyond the scoped markdown readability guard/tests.
- `GNUCASH_WRITES_ENABLED=false` remains the documented default.
- `APP_ENV=test` and write gates were not changed.
- Release/status wording remains conservative:
  - `v0.5.0-public-readonly-beta` is the current public read-only beta.
  - `v0.5.1-public-readonly-beta` is not published.
  - No public write beta, stable release, production-ready claim, or security-audited claim was added.

## Issue update

Issue #28 should stay open after this package. This worker cleaned CHANGELOG and the v0.5.0 release
notes/final gate source plus guard coverage, but the original issue describes broader gradual markdown
readability work across README/release/status docs before wider announcement.

Remaining blockers for closing #28:

- Finish a broader pass over other public/status docs when they are touched for substantive reasons.
- Avoid noisy whole-repository reflow unless a maintainer explicitly requests a formatting-only cleanup.

## CI

GitHub Actions CI for pushed handoff commit `2653832754598d537d1dd2ed81a27b9585a94998`:

- Run: https://github.com/valentusys/gnucash-web-companion/actions/runs/26804377323
- Workflow: CI
- Status: completed
- Conclusion: success

## Next supervisor recommendation

Keep #28 open. Continue with targeted readability cleanup only when docs are touched for real release,
status, or announcement work. Do not publish or claim `v0.5.1` from this package.
