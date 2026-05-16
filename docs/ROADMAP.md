# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Completed phases

### Phase 0 — Research and positioning

Completed competitive review and product positioning.

Artifacts:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/handoff/phase-0.md`

### Phase 1 — Open-source foundation

Completed licensing, contribution, security, issue/PR templates, CI foundation, and initial documentation.

### Phase 2 — Project skeleton

Completed runnable monorepo skeleton:

- SvelteKit frontend in `apps/web/`
- FastAPI backend in `apps/api/`
- Docker Compose and Caddy proxy scaffolding
- Basic health checks and CI wiring

### Phase 3 — App metadata DB and book registry foundation

Completed separate app metadata DB, SQLAlchemy models, default book seed, book registry, and access service foundation.

### Phase 4 — Authentication foundation

Completed login/logout/me endpoints, password hashing, JWT creation/verification, httpOnly cookie frontend flow, and admin bootstrap.

### Phase 5 — Read-only piecash service layer

Completed `GnuCashBookService`, DTOs, controlled errors, and read-only methods for accounts, transactions, summaries, and cashflow.

### Phase 6 — Books/accounts API and UI

Completed book-aware account endpoints and frontend account tree/detail views.

### Phase 7 — Transaction browsing API and UI

Completed paginated transaction listing, filters/search, transaction detail pages, and account transaction views.

### Phase 8 — Dashboard reports API and UI

Completed summary, cashflow, expenses-by-account, and recent transaction reports with frontend dashboard views.

### Phase 9 — Frontend foundation

Completed light/dark theme system, desktop/mobile navigation, reusable state components, PWA manifest, and accessibility pass.

### Phase 10 — Public repo hygiene and release readiness

Completed README/docs refresh, sensitive-file ignore checks, CI readiness review, release instructions, and public GitHub publication checklist.

## Next: v0.0.1 pre-alpha

Target: public GitHub repository publication and `v0.0.1` pre-alpha tag.

Scope:

- Publish repository with honest pre-alpha status.
- Keep README and docs aligned with read-only-first safety boundary.
- Ensure CI runs without secrets.
- Do not publish npm/PyPI packages.

## Next: v0.1 read-only MVP

Target: safe private self-hosted read-only browsing and reporting over one configured GnuCash book.

Remaining likely work:

- End-to-end Docker runtime testing on a clean machine.
- Test fixture book strategy and no-mutation verification improvements.
- UI polish based on real sample books.
- Privacy mode for sensitive numbers.
- Clear read-only indicators in all relevant UI views.
- Deployment hardening documentation.

## Later / explicitly not MVP

Possible future areas after v0.1, only with explicit design and safety review:

- Multi-book management UI.
- Advanced reports and charting.
- Improved multi-currency reports with explicit exchange-rate policy.
- Optional integrations.
- Carefully designed write mode.

Collaborative multi-user editing is not a core roadmap item.
