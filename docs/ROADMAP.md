# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Current release posture

- Status: pre-alpha / MVP in progress.
- Completed through Phase 228.
- Current public read-only pre-release: `v0.1.7-readonly`.
- Current published write-alpha pre-release: `v0.2.4-writealpha`, published in Phase 211 after the cycle-1 release gate and exact release-commit CI as pre-alpha/experimental and disabled by default.
- MVP v0.1 remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes, where present, are post-MVP/write-alpha, disabled by default, constrained by the existing backend `APP_ENV=test` gate when explicitly enabled, and not safe for real/private production books.
- Current compatibility evidence is synthetic/disposable fixture evidence only; broad GnuCash Desktop version support is not claimed.
- Latest public release baseline: Phase 211 published `v0.2.4-writealpha` after local backend/frontend/Docker checks, exact release-commit CI, rendered `GNUCASH_WRITES_ENABLED=false`, and sensitive tracked-file hygiene. Phase 212 added this public status drift guard; Phase 213 verified the published tag from a fresh clone with default-disabled writes; Phase 214 verified synthetic local upgrade from that tag/runtime state to current `main`; Phase 221 evaluated `v0.2.5-writealpha` and recorded a no-release verdict because Phase 220 found a bounded write-alpha DELETE backup-count anomaly. Phases 222–228 remediated, documented, and smoke-verified that blocker closure only as synthetic/disposable backup-audit plus default-disabled fresh-clone/upgrade evidence. No new release was published.
- No further tag, GitHub release, package, or publication is planned by this roadmap page unless a later explicit release phase and authorization say so.

## Recently completed maintenance phases

- Phase 202 — default read-only first-run diagnostics hardening.
- Phase 203 — disposable Desktop fixture capture path blocker refresh.
- Phase 204 — compatibility-matrix regression coverage from redacted metadata.
- Phase 205 — multi-book read-only recovery polish.
- Phase 206 — transaction/scheduled read-only edge-case hardening plus dogfood.
- Phase 207 — write-alpha audit-summary redaction and bounded metadata hardening.
- Phase 208 — EN/RU operator safety copy polish without full-localization claims.
- Phase 209 — full default-read-only Docker/Caddy dogfood with disabled write probes.
- Phase 210 — bounded synthetic/disposable write-alpha create/PATCH/DELETE+restore dogfood.
- Phase 211 — authorized `v0.2.4-writealpha` GitHub pre-release publication after exact release-commit CI.
- Phase 212 — public status drift guard for README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release docs.
- Phase 213 — `v0.2.4-writealpha` tagged fresh-clone Docker/Caddy smoke with default-disabled writes.
- Phase 214 — synthetic Docker upgrade smoke preserving dummy app metadata, selected-book recovery, read-only routes, audit-summary access, and disabled writes.
- Phase 221 — `v0.2.5-writealpha` release gate recorded an explicit no-release verdict because Phase 220 write-alpha DELETE backup-count evidence was not release-green.
- Phase 227 — operator/release docs recorded the Phase 220 blocker closure narrowly as synthetic/disposable evidence remediation, with `v0.2.4-writealpha` still current.
- Phase 228 — current-HEAD fresh-clone and `v0.2.4-writealpha` to current-HEAD synthetic upgrade smokes passed with default-disabled writes and no release publication.

## Completed phase groups

### Foundation and read-only MVP baseline — Phases 0–11

Completed product positioning, open-source repository foundation, SvelteKit/FastAPI/Docker skeleton, separate app metadata DB, authentication, read-only piecash service layer, account/transaction/report browsing UI, mobile/theme shell, public repo hygiene, and integration QA hardening.

Key artifacts:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/ARCHITECTURE.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/handoff/phase-0.md` through `docs/handoff/phase-11.md`

### Controlled-write safety groundwork, still post-MVP

Implemented controlled write code and safety tests only as future/post-MVP work. The MVP remains read-only by default.

Completed safety foundations include:

- feature flag gating for writes with default `GNUCASH_WRITES_ENABLED=false`;
- file-based per-book write locking;
- disposable-book write integration tests;
- backup restore smoke tests;
- disabled-write bypass regression coverage;
- write-alpha create/PATCH/DELETE hardening only under explicit test/disposable fixture scope.

Do not treat this as production-safe write support.

### Release governance and public status synchronization

Completed release/status documentation synchronization, project-lead context, conservative pre-alpha release gates, public pre-release publication phases, and post-release documentation/status correction phases.

Key release artifacts:

- `docs/release/v0.0.1-prealpha-notes.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/release/v0.1.0-readonly-notes.md`
- `docs/release/v0.1.1-readonly-notes.md`
- `docs/release/v0.1.2-readonly-notes.md`
- `docs/release/v0.1.3-readonly-notes.md`
- `docs/release/v0.1.7-readonly-notes.md`
- `docs/release/v0.2.0-writealpha-notes.md`
- `docs/release/v0.2.4-writealpha-notes.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`

### Read-only release-value improvements

Completed read-only value work includes:

- synthetic/disposable GnuCash SQLite fixtures;
- read-only adapter validation against fixtures;
- README screenshots using synthetic data only;
- multi-currency limitation tests/docs;
- multi-book UI foundation and read-only book metadata UX;
- transaction search/filtering, URL-only presets, account-scoped filter/export parity, and CSV export;
- scheduled/recurring transaction read-only awareness;
- dashboard/report correctness and known no-conversion limitations;
- read-only safety banner, empty/error states, skeleton loading states, and mobile navigation polish;
- conservative local/LAN/VPN deployment and backup/recovery documentation.

## Near-term backlog posture

Continue only with explicitly requested phases. Good next work should be concrete and bounded, such as:

- read-only UX fixes from real/synthetic dogfood;
- safe copied/disposable-book compatibility evidence if an explicit safe source is provided;
- local/LAN/VPN deployment smoke evidence with redacted artifacts;
- documentation updates that are tied to a real status/release/safety change.

Avoid audit-only loops unless explicitly requested. Avoid expanding write-alpha code unless a phase explicitly authorizes it and preserves disabled-by-default/test-disposable boundaries.

## Later / explicitly not MVP

Possible future areas after explicit design and safety review:

- full book management UI;
- advanced reports and charting;
- improved multi-currency reports with explicit exchange-rate policy;
- optional integrations;
- carefully designed write mode after compatibility, recovery, and maintainer review gates.

Collaborative multi-user editing is not a core roadmap item. Banking integrations, CSV/OFX import, hosted SaaS positioning, direct public-internet deployment posture, and family-wallet baseline positioning remain out of MVP scope.
