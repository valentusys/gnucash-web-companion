# Phase 67 Audit — Open-Source Hygiene

Date: 2026-05-18

## Executive summary

Phase 67 audited public repository hygiene for `gnucash-web-companion` against the auditor roadmap. The repository has the expected OSS basics: license, README, contributing guide, code of conduct, security policy, funding placeholder, issue/PR templates, meaningful open issues, safety-conscious docs, GitHub topics, and documented social-preview setup.

The project is not confusing from a public-readiness perspective as long as it continues to present itself as pre-alpha, read-only by default, not production-ready, and not security-audited. No product-code or write-scope change is warranted in this phase.

## Verdict

Good OSS hygiene, with minor cleanup completed in Phase 67.

This verdict is about repository/community hygiene only. It does not approve `v0.1.0-readonly` publication and does not reduce the existing release blockers.

## Blockers

No new Phase 67 open-source-hygiene blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.
3. #27 — full configured GnuCash book paths/URIs should be redacted or summarized in default-book seed logs before treating shared/local deployment posture as hardened.

## Important non-blockers

1. The GitHub issue templates referenced a `needs-triage` label that did not exist. This could make new issue metadata less consistent. The label was created as Phase 67 GitHub hygiene work.
2. The GitHub repository description was shorter than the README's recommended read-only description. It was updated to `Modern self-hosted read-only web companion for GnuCash books.`
3. Both `good first issue` and `good-first-issue` labels exist. This is mild label duplication, not a release blocker. Do not create a noisy issue unless maintainers want label consolidation later.
4. Milestones exist but currently have no open issues assigned. This is not harmful for pre-alpha, but future release management should assign issues deliberately rather than for appearance.
5. GitHub social preview configuration cannot be fully verified from repository files alone; `docs/community/social-preview.md` documents the manual setup and safety checklist.

## Product consistency

Checked files:

- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `AGENTS.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- latest handoff `docs/handoff/phase-66.md`
- auditor roadmap file for Phase 67

Findings:

- Public docs consistently describe the project as pre-alpha / MVP in progress.
- README says Phase 0–66 are complete and links to the Phase 66 audit before Phase 67 updates.
- README and release plan keep MVP v0.1 read-only by default.
- Docs continue to state that GnuCash Desktop remains the authoritative editor.
- The repository does not position the project as SaaS, a GnuCash replacement, or collaborative accounting.
- Existing release blockers #24/#25 remain visible and are not contradicted by the OSS hygiene status.

## Safety boundary

Findings:

- No product code was changed by the auditor.
- No write route, write UI, or controlled-write capability was expanded.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state in the audited docs.
- Controlled writes remain experimental/post-MVP only.
- No real GnuCash files, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real financial exports were added during this audit.

## Open-source hygiene checks

| Check | Result | Evidence |
| --- | --- | --- |
| LICENSE exists | OK | `LICENSE` contains AGPL-3.0 text. |
| README readable | OK | `README.md` has clear status, what it is/is not, quick start, safety warning, release readiness, screenshots, and links. |
| CONTRIBUTING exists | OK | `CONTRIBUTING.md` includes setup, PR guidance, read-only boundary, and sensitive-data policy. |
| CODE_OF_CONDUCT exists | OK | `CODE_OF_CONDUCT.md` uses Contributor Covenant 2.1. |
| SECURITY exists | OK | `SECURITY.md` is honest about pre-alpha, no production guarantee, and private vulnerability reporting. |
| FUNDING exists or intentionally absent | OK | `.github/FUNDING.yml` exists as commented placeholders and explicitly avoids real handles until provided. |
| GitHub topics set | OK | `accounting`, `fastapi`, `finance`, `gnucash`, `open-source`, `personal-finance`, `self-hosted`, `sqlite`, `sveltekit`. |
| Social preview configured or documented | Documented | `docs/community/social-preview.md` documents manual setup and synthetic-data safety requirements. Actual GitHub UI state was not treated as auditable from git files. |
| Issues open and useful | OK | Open issues #11, #12, #13, #17, #22, #24, #25, #26, #27 are meaningful backlog/release/safety items. |
| Labels meaningful | Mostly OK | Safety/read-only/release/audit/security/community labels exist. Missing `needs-triage` label was found and then created. |
| Milestones meaningful | Acceptable | Milestones exist for v0.1, v0.2, and post-MVP multi-book. They currently have no open issues assigned; not a blocker. |
| No issue backlog theater | OK | No fake/noisy issue creation was needed for Phase 67. |

## GitHub project hygiene

GitHub state inspected with authenticated `gh`:

- Repository is public and not archived.
- Topics are set and relevant.
- Open issues are real backlog/release/safety work, not empty theater.
- Labels include the project-specific categories needed by current workflow: `read-only`, `multi-book`, `gnucash`, `safety`, `v0.2-writes`, `pre-alpha`, `security`, `community`, `post-MVP`, `audit`, `release`.
- Phase 67 created the missing `needs-triage` label because both issue templates reference it.
- Phase 67 updated the GitHub repository description to include the read-only positioning.

## Security notes

This phase did not perform a professional security audit. It only checked OSS hygiene surface and release/safety positioning.

Security-related OSS files are present and conservative:

- `SECURITY.md` warns that the project is pre-alpha, not security-audited, and should not be exposed directly to the public internet.
- `CONTRIBUTING.md` and issue templates warn contributors not to attach real financial data or secrets.
- Existing #27 remains the tracked hardening issue for full-path default-book seed log redaction.

## Test/CI notes

Because Phase 67 is audit/docs/GitHub-hygiene only and does not change product code, the relevant local verification is:

- `git diff --check`
- optional docs/static inspection through direct file reads and `gh` queries

No readiness verdict for `v0.1.0-readonly` is made in this audit. Therefore this phase does not require the full backend/frontend/Docker suite as release evidence. The previous Phase 66 handoff records the full suite passing; Phase 67 does not rely on that to publish a release.

## Recommended next actions

1. Keep #24 and #25 as required gates before any `v0.1.0-readonly` tag/release.
2. Keep #27 visible as a security-hardening follow-up before treating deployment posture as hardened.
3. In a future explicit cleanup phase, consider consolidating `good first issue` vs `good-first-issue` labels if maintainers want stricter label hygiene.
4. Assign issues to milestones only when a concrete release/backlog decision is made; do not assign them only to make milestones look active.
5. Do not start Phase 68 automatically; wait for an explicit request.

## Suggested / created GitHub issues

Created issues: none.

Created/updated GitHub hygiene items:

- Created label `needs-triage` because `.github/ISSUE_TEMPLATE/bug_report.yml` and `.github/ISSUE_TEMPLATE/feature_request.yml` reference it.
- Updated repository description to `Modern self-hosted read-only web companion for GnuCash books.`

No new issue was created for label duplication or empty milestones because that would be noisy at the current pre-alpha stage.

## What not to do next

- Do not publish `v0.1.0-readonly` from this hygiene verdict.
- Do not claim production readiness, audited security, broad compatibility, hosted SaaS readiness, collaborative accounting, or safe write mode.
- Do not expand controlled-write scope.
- Do not create fake GitHub issues just to make the backlog appear busier.
- Do not commit real financial data, real screenshots, `.env`, app DBs, backups, secrets, keys, certs, or real exports.
- Do not start Phase 68 unless explicitly requested.
