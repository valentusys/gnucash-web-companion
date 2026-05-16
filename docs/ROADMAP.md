# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Phase 0 — Research and positioning

Complete. See:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/handoff/phase-0.md`

## Phase 1 — Open-source foundation

Complete when the repository has licensing, contribution, security, issue/PR templates, CI skeleton, and project-status documentation.

## Phase 2 — Project skeleton

Planned:

- SvelteKit skeleton in `apps/web/`.
- FastAPI skeleton in `apps/api/`.
- Docker/dev environment.
- Sample fixture strategy.
- Initial OpenAPI schemas.

## Phase 3 — Read-only GnuCash access

Planned:

- piecash read-only opening validation.
- Account and transaction read models.
- Exact amount representation.
- Tests proving no book mutation.

## Phase 4 — Read-only UI MVP

Planned:

- UI shell.
- Account tree.
- Transaction search.
- Basic dashboard/report views.
- Privacy mode.

## v0.1 — Read-only MVP release

Target: safe private self-hosted read-only browsing and reporting over one configured GnuCash book.

## Later / explicitly not MVP

- Carefully designed write mode.
- Multi-book UI.
- Advanced reports.
- Optional integrations.

Collaborative multi-user editing is not a core roadmap item.
