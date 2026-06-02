# Overnight worker 11 handoff — #28 markdown readability guard

Worker task ID: `overnight-2026-06-02-worker-11`

UTC handoff time: 2026-06-02T06:28:32Z

## Scope completed

Added a concrete, local, test-backed markdown readability guard for selected public/status docs and
the current worker handoff.

Changed files:

- `README.md`
- `PROJECT_STATUS.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/development/markdown-readability.md`
- `docs/handoff/overnight-2026-06-02-worker-11.md`
- `scripts/check_markdown_readability.py`

## TDD evidence

RED:

```text
cd apps/api && pytest tests/test_markdown_readability_docs.py -q
....FFF
FileNotFoundError: scripts/check_markdown_readability.py
3 failed, 4 passed
```

GREEN:

```text
cd apps/api && pytest tests/test_markdown_readability_docs.py -q
7 passed in 0.03s
```

## Guard behavior

`scripts/check_markdown_readability.py` checks selected public/status Markdown and this current
handoff without external services. It fails closed for:

- missing top status/safety signal in selected public/status docs;
- missing active issue navigation in `PROJECT_STATUS.md`;
- missing issue/handoff navigation in current overnight handoff docs;
- missing guidance that safety warnings must be preserved;
- unstructured long prose outside allowlisted code fences, URLs, tables, and command-like lines.

The checker intentionally avoids noisy historical whole-file reflow by checking current top
navigation/readability for long archives plus focused current handoff/status files.

## Verification

Focused package checks:

```text
python3 scripts/check_markdown_readability.py
markdown-readability-guard: ok (5 docs checked)

cd apps/api && pytest tests/test_markdown_readability_docs.py -q
7 passed in 0.03s
```

Final required verification:

```text
cd apps/api && pytest tests/test_markdown_readability_docs.py -q
7 passed in 0.03s

python3 scripts/check_markdown_readability.py
markdown-readability-guard: ok (6 docs checked)

python3 scripts/check_public_status.py
public-status-guard: ok

python3 scripts/check_tracked_hygiene.py
Tracked hygiene check passed (1738 tracked paths inspected).

git diff --check
passed

JWT_SECRET=*** APP_ADMIN_PASSWORD=*** docker compose config --quiet
passed
```

Static added-line security scan:

```text
git diff | grep '^+' | grep -iE '(api_key|secret|password|token|passwd)\s*=\s*["'"''][^"'"'']{6,}["'"'']' || true
git diff | grep '^+' | grep -E 'os\.system\(|subprocess.*shell=True|\beval\(|\bexec\(|pickle\.loads?\(|execute\(f"|\.format\(.*SELECT|\.format\(.*INSERT' || true
```

No findings.

Independent reviewer note: project `AGENTS.md` forbids `delegate_task` unless explicitly overridden,
so no reviewer subagent was launched.

## Safety summary

- CREATE/PATCH/DELETE performed: 0/0/0.
- No real/private/original/working/only-copy GnuCash book was opened, copied, or mutated.
- No app DBs, books, backups, CSV exports, screenshots, `.env`, tokens, keys, certs, private paths,
  account names, memos, descriptions, amounts, or raw private evidence were added.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test`, owner-writebeta, write-alpha, and public-readonly gates were not weakened.
- No release/tag/package/image was published.
- No v0.5.1, public-write-beta, stable, production, or security-audited claim was added.

## Issue #28 update

Recommendation: keep #28 open unless the maintainer decides this guard satisfies the remaining
pre-announcement scope.

Completed in this package: a test-backed readability guard and docs guidance now cover top
status/safety signals, issue/handoff navigation, safety-warning preservation, and unstructured long
prose in selected public/status docs.

Remaining #28 scope if kept open:

- gradual cleanup of older historical `PROJECT_STATUS.md`, `CHANGELOG.md`, release docs, and handoff
  prose when those files are touched for substantive reasons;
- maintainer decision on whether the new guard is sufficient before wider announcement.

## Commit / CI

Implementation commit SHA: `768fba553aecdf4f894a2bef92b63cf6bbd97633`.

Handoff SHA update: `f81c3eacd62537786299f712c5e75e66c65d695a`.

CI: success for pushed `a98629ce54d7aee5631ea2df7aba96fe1b47aee0` on main:
https://github.com/valentusys/gnucash-web-companion/actions/runs/26802760504.

## Next supervisor recommendation

Keep #28 open for maintainer review or gradual historical-doc cleanup. Continue using
`scripts/check_markdown_readability.py` for docs-heavy public/status changes before announcement.
