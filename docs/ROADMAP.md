# Roadmap

This roadmap is intentionally conservative. Safety and trust come before feature breadth.

## Current release posture

- Status: pre-alpha / MVP in progress.
- Completed through Phase 255.
- Current public read-only pre-release: `v0.1.7-readonly`.
- Current published write-alpha pre-release: `v0.2.7-writealpha`, published in Phase 251 after the
  cycle-2 release gate, PM authorization, and exact release-commit CI as pre-alpha/experimental and
  disabled by default.
- MVP v0.1 remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes, where present, are post-MVP/write-alpha, disabled by default, constrained by
  the existing backend `APP_ENV=test` gate when explicitly enabled, and not safe for real/private
  production books.
- Current compatibility evidence is synthetic/disposable fixture evidence only; broad GnuCash
  Desktop version support is not claimed.
- Latest public release baseline: Phase 251 published `v0.2.7-writealpha` after PM authorization,
  local backend/frontend/Docker checks, exact release-commit CI, rendered `GNUCASH_WRITES_ENABLED=false`,
  public status guard, and sensitive tracked-file hygiene. Phase 232 reconciled public
  status/changelog wording after publication, Phase 233 improved raw markdown readability for
  README/status sources without changing safety posture, Phase 234 added a conservative copied-book
  write-alpha dogfood runbook, Phase 235 added a redacted local-only target preflight CLI for
  future copied/disposable testing, Phase 236 added a redacted dogfood evidence schema/helper for
  future evidence reports, Phase 237 added a local-only write-alpha environment reference and
  operator guard documentation, Phase 238 added a redacted non-mutating write-alpha readiness
  command, Phase 239 recorded a synthetic copied-book dry-run through Docker/Caddy using the
  redacted evidence schema without changing default read-only config or running real/private
  copied-book dogfood, Phase 240 prepared `v0.2.6-writealpha` release-candidate docs, and Phase 241
  called PM, reran the release gate, waited for exact release/status commit CI, and published
  `v0.2.6-writealpha` as a conservative GitHub pre-release. Cycle 2 then passed the Phase 242
  analyst gate, Phase 243 added app metadata-only write-alpha transaction ownership markers for
  CREATE, Phase 244 added a backend PATCH ownership guard, Phase 245 added a backend DELETE
  ownership guard, Phase 246 aligned the transaction detail UI with backend ownership state, Phase
  247 recorded synthetic/disposable ownership route-family dogfood, Phase 248 exposed safe ownership
  counters in the read-only audit summary, Phase 249 documented the operator-facing ownership
  boundary, Phase 250 prepared `v0.2.7-writealpha` release-candidate notes/checklist/final-gate,
  and Phase 251 published `v0.2.7-writealpha` as a conservative GitHub pre-release after PM
  authorization, full release gate, and exact commit CI. Phase 252 passed the Cycle 3 analyst gate,
  Phase 253 added a maintainer copied-book dogfood packet with dry-run first, original/only-copy
  books forbidden, copied/restorable outside-git targets plus independent backup required, optional
  one CREATE first, PATCH deferred to later explicit review, DELETE prohibited unless separately
  authorized for a write-alpha-created test transaction, redacted evidence, restore proof, cleanup,
  and reset to `GNUCASH_WRITES_ENABLED=false`. Phase 254 then added
  `scripts/write_alpha_copied_book_dogfood.py`, a local-only explicit-step wrapper with separate
  `--dry-run` and `--create-one` modes, required confirmations, preflight, pre-step backup,
  redacted evidence, unsafe-path rejection, and default-disabled reset proof. Phase 255 strengthened
  transaction create/write-alpha warnings for maintainer copied-book create-only dogfood: use only an
  outside-git copied/restorable test book, keep the original untouched, dry-run first, at most one
  CREATE test transaction, independent backup plus restore plan, audit/app-backup/lock evidence, and
  no production use. CREATE creates write-alpha-owned transactions; PATCH/DELETE are limited to
  write-alpha-owned transactions; historical/imported/manual transactions remain read-only in this
  app. Non-owned historical/imported/manual transactions are rejected before write-service
  construction for PATCH/DELETE. Phase 221 previously recorded a no-release verdict for
  the Phase 220 DELETE backup-count anomaly; Phases 222–230 remediated and re-verified that blocker
  only as synthetic/disposable backup-audit, default-disabled fresh-clone/upgrade, and final
  release-candidate dogfood evidence before publication.
- No further tag, GitHub release, package, or publication is planned by this roadmap page unless a
  later explicit release phase and authorization say so.

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
- Phase 211 — authorized `v0.2.4-writealpha` GitHub pre-release publication after exact
  release-commit CI.
- Phase 212 — public status drift guard for README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release
  docs.
- Phase 213 — `v0.2.4-writealpha` tagged fresh-clone Docker/Caddy smoke with default-disabled
  writes.
- Phase 214 — synthetic Docker upgrade smoke preserving dummy app metadata, selected-book recovery,
  read-only routes, audit-summary access, and disabled writes.
- Phase 221 — `v0.2.5-writealpha` release gate recorded an explicit no-release verdict because Phase
  220 write-alpha DELETE backup-count evidence was not release-green.
- Phase 227 — operator/release docs recorded the Phase 220 blocker closure narrowly as
  synthetic/disposable evidence remediation, with `v0.2.4-writealpha` still current.
- Phase 228 — current-HEAD fresh-clone and `v0.2.4-writealpha` to current-HEAD synthetic upgrade
  smokes passed with default-disabled writes and no release publication.
- Phase 229 — public status and release-support drift guard refreshed after Phases 222–228 while
  `v0.2.4-writealpha` was still current and before `v0.2.5-writealpha` publication.
- Phase 230 — final release-candidate dogfood pack passed: default-read-only API/browser evidence,
  bounded synthetic/disposable create/PATCH/DELETE write-alpha evidence, DELETE restore proof,
  default-false reset, cleanup, and no release/tag publication in that phase.
- Phase 231 — authorized `v0.2.5-writealpha` GitHub pre-release publication after final release
  gate, local checks, public status guard, sensitive-file hygiene, and exact release/status commit
  CI.
- Phase 232 — reconciled public status/changelog wording after `v0.2.5-writealpha` publication,
  keeping default-disabled/`APP_ENV=test`/synthetic-disposable evidence boundaries explicit.
- Phase 233 — reformatted README, README.ru, CHANGELOG, and PROJECT_STATUS for raw markdown
  readability while preserving safety wording and release posture.
- Phase 234 — added a conservative copied-book write-alpha dogfood runbook for future local-only
  copied/disposable testing without performing real/private copied-book writes.
- Phase 235 — added a redacted local-only write-alpha target preflight CLI that rejects missing,
  unreadable, inside-git, unsafe-backup, and unsafe-environment cases before any mutation.
- Phase 236 — added a redacted dogfood evidence schema and helper that rejects or redacts raw
  paths, amount-like values, memo/account-name fields, and payload-like values before future
  dogfood evidence is committed.
- Phase 237 — added an explicitly unsafe-for-real-books `.env.writealpha.example` reference and
  `docs/write-alpha/environment.md` operator guidance for local-only write-alpha testing; defaults
  remain read-only and no write mode was enabled.
- Phase 238 — added a redacted non-mutating `scripts/write_alpha_readiness.py` command for checking
  write-alpha prerequisites; it reports gate/config/readiness status without constructing the write
  service or mutating books.
- Phase 239 — ran a synthetic copied-book dry-run through Docker/Caddy with preflight/readiness,
  default-disabled API/browser smoke, disabled validate/create/PATCH/DELETE probes, checksum
  no-mutation proof, and redacted Phase 236-schema evidence.
- Phase 240 — prepared `v0.2.6-writealpha` release-candidate notes/checklist/final-gate draft only;
  no tag, GitHub release, write default change, `APP_ENV=test` gate weakening, or real/private-book
  safety claim was added.
- Phase 241 — called PM, received `AUTHORIZE_RELEASE`, reran the final gate, waited for exact
  release/status commit CI, and published `v0.2.6-writealpha` as a conservative GitHub pre-release
  with no package/image/default/gate/safety-claim expansion.
- Phase 250 — prepared `v0.2.7-writealpha` release-candidate notes/checklist/final-gate only after
  confirming backend ownership guards, synthetic/disposable route-family dogfood, and synchronized
  ownership docs. No tag, GitHub release, PM authorization, write default change, `APP_ENV=test`
  gate weakening, or real/private-book safety claim was added.
- Phase 251 — called PM, received `AUTHORIZE_RELEASE`, reran the final local release gate, waited for
  exact release/status commit CI, and published `v0.2.7-writealpha` as a conservative GitHub
  pre-release.
- Phase 252 — passed the Cycle 3 analyst gate for maintainer copied-book dogfood package work.
- Phase 253 — added `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`, defaulting to
  dry-run first and requiring copied/restorable outside-git targets, independent backup, redacted
  evidence, restore proof, cleanup, and reset to default false; no mutation or release was run.

## Completed phase groups

### Foundation and read-only MVP baseline — Phases 0–11

Completed product positioning, open-source repository foundation, SvelteKit/FastAPI/Docker skeleton,
separate app metadata DB, authentication, read-only piecash service layer,
account/transaction/report browsing UI, mobile/theme shell, public repo hygiene, and integration QA
hardening.

Key artifacts:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/ARCHITECTURE.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/handoff/phase-0.md` through `docs/handoff/phase-11.md`

### Controlled-write safety groundwork, still post-MVP

Implemented controlled write code and safety tests only as future/post-MVP work. The MVP remains
read-only by default.

Completed safety foundations include:

- feature flag gating for writes with default `GNUCASH_WRITES_ENABLED=false`;
- file-based per-book write locking;
- disposable-book write integration tests;
- backup restore smoke tests;
- disabled-write bypass regression coverage;
- write-alpha create/PATCH/DELETE hardening only under explicit test/disposable fixture scope.

Do not treat this as production-safe write support.

### Release governance and public status synchronization

Completed release/status documentation synchronization, project-lead context, conservative pre-alpha
release gates, public pre-release publication phases, and post-release documentation/status
correction phases.

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
- transaction search/filtering, URL-only presets, account-scoped filter/export parity, and CSV
  export;
- scheduled/recurring transaction read-only awareness;
- dashboard/report correctness and known no-conversion limitations;
- read-only safety banner, empty/error states, skeleton loading states, and mobile navigation
  polish;
- conservative local/LAN/VPN deployment and backup/recovery documentation.

## Near-term backlog posture

Continue only with explicitly requested phases. Good next work should be concrete and bounded, such
as:

- read-only UX fixes from real/synthetic dogfood;
- safe copied/disposable-book compatibility evidence if an explicit safe source is provided;
- local/LAN/VPN deployment smoke evidence with redacted artifacts;
- documentation updates that are tied to a real status/release/safety change.

Avoid audit-only loops unless explicitly requested. Avoid expanding write-alpha code unless a phase
explicitly authorizes it and preserves disabled-by-default/test-disposable boundaries.

## Later / explicitly not MVP

Possible future areas after explicit design and safety review:

- full book management UI;
- advanced reports and charting;
- improved multi-currency reports with explicit exchange-rate policy;
- optional integrations;
- carefully designed write mode after compatibility, recovery, and maintainer review gates.

Collaborative multi-user editing is not a core roadmap item. Banking integrations, CSV/OFX import,
hosted SaaS positioning, direct public-internet deployment posture, and family-wallet baseline
positioning remain out of MVP scope.
