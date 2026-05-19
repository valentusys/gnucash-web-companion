# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Current release posture

- Status: pre-alpha / MVP in progress.
- Completed through Phase 162.
- Current public read-only pre-release: `v0.1.6-readonly`.
- Current published write-alpha pre-release: `v0.2.0-writealpha`, published after explicit authorization as pre-alpha/experimental and disabled by default.
- MVP v0.1 remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes, where present, are post-MVP/write-alpha, disabled by default, constrained by the existing backend test-environment gate when explicitly enabled, and not safe for real/private production books.
- Current compatibility evidence is synthetic/disposable fixture evidence only; broad GnuCash Desktop version support is not claimed.
- Latest tagged read-only smoke: Phase 162 verified published tag `v0.1.6-readonly` from a fresh checkout with synthetic/disposable data, dummy local-only secrets, Docker Compose, API smoke, browser dogfood, disabled validate/create/patch/delete write probes, and no raw screenshot/export/backup artifacts.
- No further tag, GitHub release, package, or publication is planned by this roadmap page unless a later explicit release phase and authorization say so.

## Recently completed maintenance phases

- Phase 153 — fresh-clone Docker smoke helper and synthetic/disposable clean-checkout evidence.
- Phase 154 — GnuCash Desktop compatibility blocker evidence refresh without broad Desktop/version claims.
- Phase 155 — multi-book read-only operator diagnostics and private-path redaction hardening.
- Phase 156 — dashboard drilldown links to existing read-only transaction filters.
- Phase 157 — scheduled/recurring transaction read-only clarity with URL-only filters and safe metadata.
- Phase 158 — mobile dogfood touch-target/no-overflow fix pass.
- Phase 159 — release-critical English/Russian frontend catalog coverage without claiming full localization.
- Phase 160 — full synthetic/disposable Docker/Caddy release-candidate dogfood with `GNUCASH_WRITES_ENABLED=false`.
- Phase 161 — authorized `v0.1.6-readonly` GitHub pre-release publication after final gate.
- Phase 162 — post-release baseline sync plus tagged `v0.1.6-readonly` fresh-checkout smoke.

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
- `docs/release/v0.2.0-writealpha-notes.md`
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
