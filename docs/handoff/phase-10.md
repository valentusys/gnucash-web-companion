# Phase 10 handoff — Public GitHub publication readiness

Date: 2026-05-16

## Scope

Phase 10 prepared the repository for public GitHub publication. This was a hygiene, documentation, CI, and release-readiness phase only.

No product features were added.

## Completed checklist

- `README.md` refreshed with honest pre-alpha / MVP-in-progress status.
- `LICENSE` exists.
- `SECURITY.md` exists and now avoids placeholder security contact claims.
- `CONTRIBUTING.md` exists and reflects current backend/frontend setup.
- `CODE_OF_CONDUCT.md` exists.
- `CHANGELOG.md` includes `0.0.1` pre-alpha entry dated `2026-05-16`.
- `.env.example` documents current environment variables and warns to use a test copy of a book.
- `.gitignore` blocks:
  - `.env`
  - `data/books/*.sqlite`
  - `data/books/*.sqlite3`
  - `data/books/*.gnucash`
  - `data/books/*.db`
  - `data/backups/*`
  - common key/cert files
  - `secrets`, `secrets/`, `credentials`, `credentials/`
- GitHub Actions CI refreshed:
  - required-file checks
  - sensitive tracked-file check
  - frontend install/check/build when `apps/web` exists
  - backend install/tests when `apps/api` exists
  - Docker Compose config validation
  - no secrets required
- Issue templates exist.
- PR template exists.
- `FUNDING.yml` exists as a safe placeholder.
- `docs/ARCHITECTURE.md` updated to current Phase 9/10 architecture.
- `docs/GNUCASH_SAFETY.md` reviewed; still current for read-only piecash boundary and multi-currency limitations.
- `docs/MVP.md` updated to current MVP-in-progress state.
- `docs/ROADMAP.md` updated with completed phases and next release targets.
- README does not promise screenshots; it explicitly says screenshots are not included yet.
- Repository description and topics are proposed in README.

## Suggested GitHub repository description

Modern self-hosted read-only web companion for GnuCash books, built with SvelteKit, FastAPI, and piecash.

## Suggested GitHub topics

- `gnucash`
- `personal-finance`
- `accounting`
- `self-hosted`
- `sveltekit`
- `fastapi`
- `open-source`
- `finance`
- `sqlite`

## v0.0.1 pre-alpha tag instructions

After the Phase 10 commit is pushed and CI is green:

```bash
git checkout main
git pull origin main
git tag -a v0.0.1 -m "v0.0.1 pre-alpha"
git push origin v0.0.1
```

Optional GitHub release command, if the owner wants a release object:

```bash
gh release create v0.0.1 \
  --title "v0.0.1 pre-alpha" \
  --notes "Initial public skeleton / MVP foundation. Pre-alpha; read-only-first; use a test copy of your GnuCash book." \
  --prerelease
```

Do not publish npm or PyPI packages unless explicitly requested.

## Safety notes for publication

- Do not commit real GnuCash books.
- Do not commit personal financial data.
- Do not commit `.env` or secrets.
- Keep all public docs honest: pre-alpha, read-only-first, no production guarantee.
- Prefer GitHub private vulnerability reporting / advisories for security reports.

## Verification performed

Local verification in this phase should include:

```bash
git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.' || true
python -m pytest tests/ -q           # from apps/api
npm run check                        # from apps/web
npm run test:auth-routes             # from apps/web
npm run build                        # from apps/web
```

Docker runtime is still not tested on the current machine because Docker is unavailable locally; CI validates compose syntax.
