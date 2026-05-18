# Phase 115 PM Brief — v0.1.2-readonly maintenance release prep, no publish

Date: 2026-05-19
Roadmap item: analyst Phase 10
Target release candidate: `v0.1.2-readonly`

## Decision

Prepare conservative release-prep and release-gate artifacts for a possible `v0.1.2-readonly` maintenance pre-release, but do not publish a tag, GitHub release, package, or any other release artifact that changes public release state.

## Why

Phases 106–114 produced meaningful user-facing read-only improvements after `v0.1.1-readonly`: transaction state filters, URL-only filter reset/presets, account-detail filter/export parity, scheduled-transaction awareness, `/books` metadata hardening, LAN/VPN CORS diagnostics, Russian glossary/UI slice, and synthetic browser dogfood evidence. This is enough to prepare an honest maintenance candidate for later explicit authorization.

## Goal

Create release-prep documentation and a final gate verdict for `v0.1.2-readonly` based on completed Phases 106–114.

## Non-goals

- Do not create or push a `v0.1.2-readonly` tag.
- Do not create a GitHub release or publish packages.
- Do not enable `GNUCASH_WRITES_ENABLED` or expand write-mode scope.
- Do not add v0.2 features.
- Do not claim production readiness, security audit completion, broad GnuCash compatibility, or personal-book dogfood success.

## Acceptance criteria

- `docs/release/v0.1.2-readonly-notes.md` honestly summarizes the candidate scope, limitations, upgrade notes, and publication status.
- `docs/release/v0.1.2-readonly-checklist.md` documents completed evidence, required publish authorization, and exact publish commands that were not executed.
- `docs/release/v0.1.2-readonly-final-gate.md` records checks and a verdict of either ready for authorized publish or blocked.
- `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-115.md` are updated in the same phase.
- No tag/release/package is published.

## Safety checks

- Keep `GNUCASH_WRITES_ENABLED=false` as the default release posture.
- Do not commit real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, keys, or private paths.
- Keep release notes conservative: pre-alpha, read-only by default, not production-ready, not security-audited, test disposable/copy books first, do not expose directly to the public internet.
- Do not claim personal copied-book dogfood for #38.
- Do not weaken GnuCash Desktop authoritative-editor language.

## Verification

Run, if available:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
git ls-files | grep -E '(^|/)(\.env|app\.db|.*\.gnucash(\.sqlite)?|.*\.csv|.*\.pem|.*\.key|.*\.crt)$' || true
git tag --list 'v0.1.2-readonly'
gh release view v0.1.2-readonly || true
gh run list --limit 10 --json status,conclusion,headBranch,displayTitle,url
```

## Files/docs to update

- `docs/release/v0.1.2-readonly-notes.md`
- `docs/release/v0.1.2-readonly-checklist.md`
- `docs/release/v0.1.2-readonly-final-gate.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-115.md`

## GitHub/backlog

- Use `gh` only for read-only release/backlog state checks unless a narrow evidence comment is useful.
- Do not close #38; personal copied-book dogfood remains blocked until Val provides a safe copied SQL book path outside git.
- Do not close broad future-scope issues (#11/#12/#13/#17/#22/#29) unless their issue text is fully satisfied; this release prep does not require closure.
