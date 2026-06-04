# Night maintenance autonomy queue

This sample queue is for conservative overnight maintenance where workers should
prefer docs, tests, and guard improvements over product behavior changes.

## Task: guard-readability-maintenance
- target: static guards and docs readability
- goal: Tighten or refresh existing public-status/readability guard coverage when docs drift is found.
- allowed scope: scripts/check_public_status.py, scripts/check_markdown_readability.py, apps/api/tests/test_public_status_guard.py, apps/api/tests/test_markdown_readability_docs.py, docs/**/*.md
- non-goals: product write behavior; GnuCash mutations; private evidence; release/tag/package/image publication; production/stable/security-audited claims
- verification commands:
  - cd apps/api && pytest tests/test_public_status_guard.py tests/test_markdown_readability_docs.py -q
  - python3 scripts/check_public_status.py
  - python3 scripts/check_markdown_readability.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, conservative-doc-guards
- stop/continue recommendation: continue if guard tests and hygiene pass

## Task: api-test-maintenance
- target: API regression tests
- goal: Fix flaky or stale API tests without expanding write scope or weakening assertions.
- allowed scope: apps/api/tests/**, scripts/test helpers, docs/handoff maintenance notes
- non-goals: backend feature expansion; write route broadening; dogfood; real/private book usage; releases; tags; packages; images
- verification commands:
  - cd apps/api && pytest -q
  - python3 scripts/check_write_safety_defaults.py
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, preserve-write-defaults
- stop/continue recommendation: checkpoint if any test requires private data or write-default changes

## Task: ci-state-handoff
- target: CI and handoff documentation
- goal: Record the final local/CI state in a tracked handoff only if there are safe tracked changes to explain.
- allowed scope: docs/handoff/** only
- non-goals: GitHub issue closure/reopen; release publication; tags; packages; images; private logs
- verification commands:
  - python3 scripts/check_tracked_hygiene.py
  - git diff --check
- safety flags: no-private-data, no-release, handoff-only
- stop/continue recommendation: stop after handoff or if no safe task remains
