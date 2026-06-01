# Autonomous 6h cycle 4

Selected issue/task: #28 markdown readability cleanup after #22/#36 progress.

PM scope:
- Improve `docs/development/markdown-readability.md` with concrete status/readability triage guidance.
- Add a small regression test so future docs cleanup preserves safety and release/no-release visibility.

Non-goals:
- No broad README/PROJECT_STATUS rewrite.
- No historical claim changes.
- No safety-warning removal.
- No release/tag.

Acceptance criteria:
- Guidance tells maintainers to split long status docs instead of rewriting/hiding state.
- Guidance explicitly protects release/no-release decisions, current tags, issue state, safety blockers, mutation counts, and evidence classes.
- Test verifies the guide preserves key safety wording and triage workflow.

Files changed:
- `docs/development/markdown-readability.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/autonomous-6h-cycle-4.md`

Tests run:
- `cd apps/api && pytest tests/test_markdown_readability_docs.py -q` — passed, 1 test.

Safety notes:
- Docs/test only; no GnuCash books, app DBs, backups, exports, screenshots, `.env`, secrets, tokens, private paths/account names/memos/descriptions/amounts, or raw evidence committed.
- `GNUCASH_WRITES_ENABLED=false` default unchanged.

Issue update/closure decision:
- Update #28 after commit/push.
- #28 remains open because broader README/PROJECT_STATUS/CHANGELOG readability cleanup is still possible.

Next candidate task:
- Final verification and handoff, plus issue comments. If safe time remained, next slice would be more #36 docs for remaining gates.
