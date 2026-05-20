# Phase 231 handoff — v0.2.5-writealpha release gate and publication

Date: 2026-05-21
Status: COMPLETE — final release gate passed; `v0.2.5-writealpha` published as a conservative GitHub pre-release.

## Summary

Phase 231 stayed within the Cycle 3 Phase 10 contract. It inspected current `main`, release/status artifacts, Phase 222–230 remediation and dogfood evidence, GitHub tag/release absence, local backend/frontend/Docker checks, public status guard, sensitive-file hygiene, and exact release/status commit CI.

Because all gates passed, the phase published only:

- annotated git tag `v0.2.5-writealpha`;
- GitHub pre-release `v0.2.5-writealpha` using `docs/release/v0.2.5-writealpha-notes.md`.

No product code, package, binary artifact, Docker image, production deployment, write-default change, write-scope expansion, `APP_ENV=test` gate weakening, real/private/only-copy book claim, production/security/stable/public-internet/broad-compatibility claim, or real/private-book write-safety claim was added.

## Files changed

- `docs/release/v0.2.5-writealpha-notes.md` — published release notes with conservative pre-alpha/write-alpha boundaries.
- `docs/release/v0.2.5-writealpha-checklist.md` — final release checklist.
- `docs/release/v0.2.5-writealpha-final-gate.md` — final gate decision.
- `docs/release/v0.2.5-writealpha-publication-evidence.md` — publication evidence.
- `docs/release/v0.2.5-writealpha-no-release-verdict.md` — historical Phase 221 no-release verdict marked superseded by Phase 231 publication.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, and `PROJECT_STATUS.md` — public status synchronized to Phase 231 and `v0.2.5-writealpha` as current published write-alpha pre-release.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations moved to Phase 231 / `v0.2.5-writealpha`.
- `docs/handoff/phase-231.md` — this handoff.

## Verification performed

Pre-commit/local release gate:

- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- Rendered Compose grep for `GNUCASH_WRITES_ENABLED` — API and web showed `"false"`.
- `.env.example` grep — `GNUCASH_WRITES_ENABLED=false`.
- `python3 scripts/check_public_status.py` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.
- Candidate local tag, remote tag, and GitHub release absence — confirmed before publication.

Publication gate:

- Phase 231 release/status commit pushed to `origin/main`.
- GitHub Actions for the exact release/status commit watched to success before tagging.
- Pre-tag recheck confirmed `HEAD == origin/main`, clean tracked tree except `.hermes/`, and absence of local/remote tag plus GitHub release.
- `git tag -a v0.2.5-writealpha -m "v0.2.5-writealpha"` — executed.
- `git push origin v0.2.5-writealpha` — executed.
- `gh release create v0.2.5-writealpha --title "v0.2.5-writealpha" --notes-file docs/release/v0.2.5-writealpha-notes.md --prerelease` — executed.
- Post-publication checks confirmed local tag, remote tag, and GitHub pre-release exist and target the release/status commit.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` write-alpha gate remains intact.
- Write-alpha remains experimental, pre-alpha, and synthetic/disposable or copied-test-book evidence only.
- No real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, or private financial data was added.
- The release notes explicitly avoid production readiness, stable release, security audit, hosted SaaS, public-internet safety, broad compatibility, and real/private-book write-safety claims.

## Risks / blockers

No Phase 231 release blocker remains. Remaining risk is the documented product-level boundary: write-alpha is still experimental, disabled by default, `APP_ENV=test` gated, and not safe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session.
