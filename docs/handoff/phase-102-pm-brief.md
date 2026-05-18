# Phase 102 PM Brief — Compatibility fixture/version matrix v3 (#22)

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-101.md`
Current planning HEAD: `4726f12`

## Decision

Plan Phase 102 as the next practical non-publishing roadmap phase: expand safe GnuCash compatibility fixture/version-matrix evidence for GitHub #22 using only disposable/generated fixtures or explicitly provided copied test books.

Current `main` is already complete through Phase 101, so the earlier roadmap slots Phase 95 through Phase 101 are not available as the next phase. Publication of `v0.1.1-readonly` remains unauthorized; therefore this phase must not publish a tag/release and must not repeat a publish step. The next useful task is compatibility evidence, because GitHub #22 remains open and the current matrix is still intentionally narrow.

## Why this phase now

`PROJECT_STATUS.md` and `docs/handoff/phase-101.md` show:

- Phase 99 already completed a non-publishing pre-publish dry-run and authorization guard.
- Phase 100 already completed a synthetic install/API smoke without publication.
- Phase 101 honestly recorded the copied personal-book dogfood gate as blocked because no safe copied book path was provided.
- `v0.1.1-readonly` publication still requires separate explicit authorization from Val.
- GitHub #22 remains open for broader compatibility evidence.

The analyst roadmap lists Phase 102 as the next practical non-publishing step after the copied personal-book gate. This is not audit-only and should produce concrete test/tooling/docs evidence around read-only compatibility while preserving conservative claims.

## Goal

Expand safe compatibility evidence for GnuCash SQL SQLite books by adding one meaningful new version/backend row or, if the environment lacks a usable GnuCash Desktop/source, recording an honest environment blocker while improving the reproducible generated/disposable compatibility path.

Preferred implementation direction:

- Inspect existing compatibility tooling and docs.
- If `gnucash` or a safe versioned disposable fixture source is available, generate or validate a synthetic SQLite fixture for that version and collect redacted metadata.
- If no real GnuCash Desktop/version source is available, make a practical non-private improvement to the generated/disposable compatibility evidence path, such as richer metadata/test coverage or a documented reproducible local command, and record the environment blocker honestly.
- Keep compatibility claims narrow and evidence-based.

Expected evidence artifacts:

- updated `docs/gnucash-compatibility.md`;
- updated/new compatibility evidence doc if useful;
- `docs/handoff/phase-102.md`.

## Non-goals

- Do not publish `v0.1.1-readonly`.
- Do not create or push any tag.
- Do not create or edit a GitHub release.
- Do not publish packages or external release artifacts.
- Do not commit new binary SQLite fixture files unless explicitly justified, small/synthetic, and safe; prefer generated/ignored/temp fixtures.
- Do not use real/private GnuCash books.
- Do not search private directories for books.
- Do not add PostgreSQL/MySQL/MariaDB or XML compatibility claims unless actually tested in this phase.
- Do not claim broad support for all GnuCash versions.
- Do not enable writes or expand controlled-write scope.
- Do not implement family-wallet, collaborative accounting, banking integration, CSV/OFX import, or v0.2 write features.
- Do not make production-readiness or audited-security claims.

## Acceptance criteria

- Engineer starts from current `main`, verifies a clean working tree, and confirms Phase 101 is complete.
- Engineer reads `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-101.md`, `docs/audits/2026-05-18-analyst-10-phase-plan.md`, `docs/gnucash-compatibility.md`, `docs/gnucash-version-fixture-plan.md`, and existing compatibility scripts/tests.
- Engineer identifies the available safe compatibility path:
  - If a real GnuCash Desktop/version source or explicitly provided disposable fixture is available, add at least one narrowly described compatibility row with version/backend/schema metadata and read-only smoke/test evidence.
  - If not available, record the blocker honestly and still deliver a concrete generated/disposable compatibility-path improvement, not just an audit note.
- Metadata output remains redacted and safe: no private paths, account names, transaction descriptions, amounts, memos, split rows, screenshots, app DB data, backups, `.env`, secrets, tokens, certs, or keys.
- Read-only service coverage is added or extended where code/test changes are made: account tree, transactions, transaction detail/split coverage, reports, CSV export, and checksum/no-mutation behavior as applicable.
- `docs/gnucash-compatibility.md` is updated with exactly what is proven and what remains untested.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 102 complete and identify the next practical step.
- `docs/handoff/phase-102.md` is created with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, risks/follow-up, and commit/push evidence.
- GitHub #22 is updated with non-sensitive evidence if `gh` is authenticated; close #22 only if its accepted scope is genuinely satisfied.
- No tag, GitHub release, package, GnuCash book, app DB, backup, `.env`, private path, private screenshot, private CSV export, secret, token, cert, key, or real/private financial data is committed.

## Safety checks

- Keep MVP read-only by default and keep `GNUCASH_WRITES_ENABLED=false` for any local validation.
- GnuCash Desktop remains the authoritative editor.
- Work only with generated synthetic/disposable fixtures or explicitly provided copied test books outside git.
- Do not inspect or search private directories for books.
- Do not commit fixture binaries unless the engineer proves they are synthetic, small, safe, and necessary; generated/ignored/temp paths are preferred.
- Preserve `.gitignore` protections for `data/books/*`, `data/backups/*`, `data/app/*`, `.env`, `secrets/`, generated fixtures, and credential files.
- Use Decimal/string expectations for money; never introduce float money handling.
- Do not fake currency conversion or broaden compatibility claims beyond tested evidence.
- Do not run any publish command. Publication still requires separate explicit authorization from Val.

## Verification required from engineer

Run these checks from the repository root unless noted:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD
git tag --list 'v0.1.1-readonly'
gh auth status || true
gh release view v0.1.1-readonly || true
gnucash --version || true
```

Compatibility-specific checks should be chosen based on actual changes. Expected minimum shape:

```bash
cd apps/api && pytest -q tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py
```

If compatibility code/tests are changed, run the full backend suite:

```bash
cd apps/api && pytest -q
```

If frontend, Docker, or deployment docs are touched, run the relevant checks from `AGENTS.md`:

```bash
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Always run before commit:

```bash
git diff --check
```

## Files/docs to update

Expected files:

- `docs/gnucash-compatibility.md` — update matrix/evidence/limitations with narrow Phase 102 results.
- `docs/gnucash-version-fixture-plan.md` — update only if the implementation changes the recommended safe fixture process.
- Compatibility scripts/tests under `apps/api/scripts/` and `apps/api/tests/` — only as needed for concrete evidence/tooling.
- `docs/handoff/phase-102.md` — new implementation handoff.
- `PROJECT_STATUS.md` — mark Phase 102 outcome and next planned phase after implementation.
- `CHANGELOG.md` — update only if the phase produces user-facing tooling/test/docs value worth noting.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- GitHub #22 is the primary issue for this phase.
- Update #22 with Phase 102 evidence if `gh` is authenticated.
- Close #22 only if the phase genuinely satisfies its accepted scope; otherwise leave it open with the remaining compatibility gap.
- GitHub #38 remains open/blocked unless Val provides a safe copied/disposable GnuCash SQL book path outside git.
- GitHub #39 remains closed unless concrete CSV export regression evidence is found.
- Do not create new GitHub issues unless a concrete new bug is discovered and cannot fit an existing issue.
- Do not publish `v0.1.1-readonly` without separate explicit authorization from Val.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-101.md`, `docs/audits/2026-05-18-analyst-10-phase-plan.md`, `docs/gnucash-compatibility.md`, `docs/gnucash-version-fixture-plan.md`, and existing compatibility scripts/tests.
3. Confirm Phase 101 completed as a blocked copied-book dogfood gate and that publication remains unauthorized.
4. Run non-mutating release-boundary checks: branch/HEAD, tag absence, GitHub release absence, and `gnucash --version || true`.
5. Inspect existing compatibility tooling, especially `apps/api/scripts/collect_gnucash_compatibility_metadata.py`, `apps/api/scripts/create_compatibility_fixture_v1.py`, `apps/api/tests/test_gnucash_compatibility_metadata.py`, and `apps/api/tests/test_compatibility_fixture_v1.py`.
6. Determine whether a safe versioned GnuCash Desktop/generated fixture source is available in the environment without searching private directories.
7. If available, generate/validate only synthetic/disposable SQLite fixture evidence, collect redacted metadata, run read-only service smoke/tests, and update the compatibility matrix with a narrow row.
8. If unavailable, record the environment blocker honestly and implement a concrete safe improvement to the generated/disposable compatibility path or tests, so the phase is still practical and not audit-only.
9. Keep all metadata/docs redacted: no private paths, real account names, descriptions, amounts, memos, screenshots, CSV rows, app DB data, backups, `.env`, secrets, tokens, certs, or keys.
10. Update `docs/gnucash-compatibility.md` and any affected compatibility docs/tests with precise claims only.
11. Create `docs/handoff/phase-102.md` with implementation summary, verification summary, safety statement, GitHub/backlog note, changed files, risks/follow-up, and commit/push evidence.
12. Update `PROJECT_STATUS.md`; update `CHANGELOG.md` only if warranted by the actual implementation.
13. Update GitHub #22 with non-sensitive evidence if `gh` is authenticated; close it only if the accepted scope is truly done.
14. Do not create tags, GitHub releases, packages, binary real-book fixtures, app DBs, backups, screenshots, private CSV exports, `.env`, or secret artifacts.
15. Run `git diff --check`, commit and push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 102 title and verdict: completed, blocked by environment, partially completed, or failed.
- What compatibility evidence was added or why a real-version fixture was blocked.
- Paths to updated compatibility docs/tests and `docs/handoff/phase-102.md`.
- Whether GitHub #22 was updated or closed; if left open, the exact remaining gap.
- Confirmation that no tag/release/package was published.
- Verification summary: branch/HEAD, tag/release absence, `gnucash --version` availability, targeted compatibility tests, full backend/frontend/Docker checks where applicable, and `git diff --check`.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; no broad compatibility/production/security claims; no real/private data or binary real-book fixture was committed.
- Commit hash and push status.
