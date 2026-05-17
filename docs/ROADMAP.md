# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Current release posture

- Status: pre-alpha / MVP in progress.
- Latest published pre-release: `v0.0.2-prealpha`.
- Published release notes: `docs/release/v0.0.2-prealpha-notes.md`.
- Phase 55 scope-freeze audit verdict: ready to prepare a `v0.1.0-readonly` milestone plan, not ready to publish v0.1 yet.
- Phase 56 created the `v0.1.0-readonly` plan and checklist.
- Phase 57 completed the dedicated release-gate audit and found v0.1 publication blocked until conservative release notes and copied/disposable-data runtime smoke/dogfood evidence are completed.
- MVP v0.1 remains read-only by default; controlled writes are experimental, post-MVP, and disabled by `GNUCASH_WRITES_ENABLED=false` unless explicitly enabled in a disposable environment.

## Completed phase groups

### Foundation and read-only MVP baseline — Phases 0–11

Completed product positioning, open-source repository foundation, SvelteKit/FastAPI/Docker skeleton, separate app metadata DB, authentication, read-only piecash service layer, account/transaction/report browsing UI, mobile/theme shell, public repo hygiene, and integration QA hardening.

Key artifacts:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/ARCHITECTURE.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/handoff/phase-0.md` through `docs/handoff/phase-11.md`

### Controlled-write safety groundwork, still post-MVP — Phases 12–14, 21–23, and 32

Implemented controlled write code and safety tests only as future/post-MVP work. The MVP remains read-only by default.

Completed:

- feature flag gating for writes with default `GNUCASH_WRITES_ENABLED=false`
- file-based per-book write locking
- disposable-book write integration tests
- backup restore smoke tests
- disabled-write bypass regression coverage for validate/create/patch routes

Do not treat this as production-safe write support.

### Release governance and agent continuity — Phases 15–16, 25–29, 33–35, 40–42, and 55

Completed public pre-alpha release setup, Project Lead context, release/status documentation synchronization, audit-driven fixes, discoverability docs, compatibility matrix, Phase 29 audit documentation refresh, Phase 33/34 public status baseline cleanup, Phase 35 audit-driven controlled-writes limitation cleanup, `v0.0.2-prealpha` release governance/publication, and the Phase 55 v0.1 read-only scope-freeze audit.

Key artifacts:

- `docs/release/v0.0.1-prealpha-checklist.md`
- `docs/release/v0.0.1-prealpha-notes.md`
- `docs/release/v0.0.2-prealpha-checklist.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/audits/2026-05-17-audit.md`
- `docs/audits/2026-05-18-phase-55-v0.1-readonly-scope-freeze.md`
- `docs/agents/project-lead.md`
- `docs/handoff/phase-15.md` through `docs/handoff/phase-16.md`
- `docs/handoff/phase-25.md` through `docs/handoff/phase-29.md`
- `docs/handoff/phase-33.md` through `docs/handoff/phase-35.md`

### Read-only release-value improvements — Phases 17–20, 24, 27–28, and 30–31

Completed:

- synthetic disposable GnuCash SQLite fixtures
- real read-only adapter validation against fixtures
- README screenshots using synthetic data only
- multi-currency limitation tests/docs
- multi-book UI foundation
- read-only transaction CSV export
- transaction amount range filters for browsing and CSV export
- global read-only safety status banner in the authenticated web shell
- community announcement readiness docs
- GnuCash compatibility matrix for committed synthetic fixtures

## Completed: v0.0.2 pre-alpha publication

`v0.0.2-prealpha` was published in Phase 42 after the Phase 41 release-gate audit, green local checks, and green GitHub CI. Do not publish further tags or releases unless a later explicit release phase says so.

## Next: v0.1 read-only release gate

Target: safe private self-hosted read-only browsing and reporting over one configured GnuCash book. Phase 55 found the project ready to prepare a `v0.1.0-readonly` plan/checklist, Phase 56 created those planning artifacts, and Phase 57 blocked publication until release notes and runtime smoke/dogfood evidence are completed. The project is still not approved to publish v0.1.

Remaining likely work:

- conservative `v0.1.0-readonly` release notes
- end-to-end Docker runtime testing on a clean machine or explicitly accepted limitation
- UI polish based on synthetic/sample books only
- privacy mode for sensitive numbers
- deployment hardening documentation
- conservative release notes with no production/security-audit claims

## Later / explicitly not MVP

Possible future areas after v0.1, only with explicit design and safety review:

- full book management UI
- advanced reports and charting
- improved multi-currency reports with explicit exchange-rate policy
- optional integrations
- carefully designed write mode after compatibility and recovery review

Collaborative multi-user editing is not a core roadmap item. Banking integrations, CSV/OFX import, hosted SaaS positioning, and family-wallet baseline positioning remain out of MVP scope.
