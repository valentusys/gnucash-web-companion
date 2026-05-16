# Phase 1 Handoff: Open-source Foundation

## Status

Phase 1 prepared the repository to be publishable on GitHub as an early open-source project.

No business features were implemented. No auth, account, transaction, or GnuCash data-access code was added.

## Created foundation

Repository structure:

- `apps/web/` placeholder for future SvelteKit frontend.
- `apps/api/` placeholder for future FastAPI backend.
- `docker/` placeholder for future Docker/dev infrastructure.
- `data/.gitkeep` for local development data directory.
- `.github/` issue templates, PR template, funding placeholders, and CI skeleton.

Top-level project files:

- `README.md`
- `LICENSE` — AGPL-3.0
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.env.example`
- `.gitignore`

Docs added:

- `docs/ARCHITECTURE.md`
- `docs/MVP.md`
- `docs/ROADMAP.md`
- `docs/SECURITY_MODEL.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/DEVELOPMENT.md`

## Placeholders still present

- `apps/web/` has no SvelteKit app yet.
- `apps/api/` has no FastAPI app yet.
- `docker/` has no compose/Dockerfiles yet.
- CI only echoes/path-checks until app skeletons exist.
- Funding accounts are placeholders/commented out.
- Security contact email is a placeholder and must be replaced before serious public use.
- Quick start commands are placeholders until Phase 2.

## Decisions preserved

- MVP remains read-only.
- GnuCash book remains the source of truth.
- App metadata stays separate from the GnuCash book.
- Default product model remains single-book.
- Multi-book is only future-ready architecture, not MVP UI scope.
- Collaborative multi-user editing remains an anti-goal.

## Recommended next phase

Phase 2 should create the actual project skeleton without implementing business features:

1. Initialize SvelteKit in `apps/web/`.
2. Initialize FastAPI in `apps/api/`.
3. Add Docker/dev compose.
4. Add minimal health endpoint and frontend placeholder page.
5. Add test/lint/typecheck commands so CI can become real.
6. Add fixture strategy, but do not commit real financial data.
