# Phase 68 Audit — Documentation Formatting

Date: 2026-05-18

## Executive summary

Phase 68 audited the human readability of markdown source for README, status, changelog, release docs, and docs/ markdown files.

The rendered documentation remains usable and the important safety/release messaging is still conservative: pre-alpha, read-only by default, no production-readiness or security-audit claim, no SaaS/GnuCash-replacement/collaborative-accounting positioning, and controlled writes remain experimental/post-MVP only.

The main formatting weakness is raw-source readability: many historical status/changelog/audit/handoff paragraphs are very long single lines. That is non-blocking for v0.1 safety, but it makes terminal/Obsidian/plain-text review harder before wider announcement. A small concrete link/fence cleanup was safe to accept in this phase, and a broader non-blocking GitHub issue was created for gradual cleanup.

## Verdict

Documentation formatting is acceptable with non-blocking cleanup needed before wider announcement.

This verdict is limited to markdown source/readability. It does not approve `v0.1.0-readonly` publication, does not replace the copied/disposable-data dogfood gate, and is not a production-readiness or security-audit claim.

## Blockers

No Phase 68 formatting blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.
3. #27 — full configured GnuCash book paths/URIs should be redacted or summarized in default-book seed logs before treating shared/local deployment posture as hardened.

## Important non-blockers

1. Raw markdown contains many very long prose/list lines, especially in `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, audit docs, and handoff docs. This hurts terminal/Obsidian/plain-text diff review but is not a release safety blocker.
2. A few historical code fences lacked useful language tags. This was easy and safe to fix for `docs/DEVELOPMENT.md`, `docs/handoff/phase-17.md`, and `docs/handoff/phase-22.md`.
3. A relative link-like example in `docs/handoff/phase-18.md` was correct for README context but misleading when scanned from the handoff file. It was clarified with the handoff-relative path.
4. Release docs are generally easy to scan and use short checklist items/code blocks; no severe release-doc formatting problem was found.
5. Tables inspected in audit docs use normal markdown table syntax and are readable enough for current pre-alpha docs.

## Product consistency

Checked files and areas:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/release/v0.0.2-prealpha-checklist.md`
- latest handoff `docs/handoff/phase-67.md`
- auditor roadmap entry for Phase 68
- markdown files under `docs/`

Findings:

- README and release docs continue to state pre-alpha/read-only-by-default positioning.
- README and release plan continue to state that GnuCash Desktop remains the authoritative editor.
- The docs do not promote the project as SaaS, a GnuCash replacement, or collaborative accounting.
- Existing v0.1 blockers #24/#25 remain visible and are not contradicted by formatting audit wording.
- No release/status wording was found that should override code/test evidence.

## Safety boundary

Findings:

- No product behavior changed in the audit phase.
- No write endpoint, write UI, write service, or write-scope expansion was added.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental/post-MVP only.
- No real GnuCash files, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real financial exports were added.

## Documentation formatting checks

| Check | Result | Evidence |
| --- | --- | --- |
| README raw markdown readable | Acceptable with cleanup needed | README has clear sections, but some status/comparison paragraphs are long single lines. |
| Long paragraphs not all one line | Needs gradual cleanup | Script found many lines over 180 characters across historical docs; this is non-blocking but hurts plain-text review. |
| Obsidian compatibility acceptable | Acceptable | Markdown is standard CommonMark-style headings/lists/tables/fences; no Obsidian-specific blocker found. |
| Tables render correctly | Acceptable | Audit/status tables use normal pipe-table syntax. |
| Code fences have language tags where useful | Mostly OK after small fix | Five unlabeled fences were found; safe historical docs fixes added `text` tags. |
| Russian/English docs link correctly | Acceptable | README links `README.ru.md` and `docs/localization.md`; no missing localization link was found in the static relative-link scan. |
| Release docs easy to scan | OK | v0.1 plan/checklist and v0.0.2 notes/checklist use headings, bullets, checklists, and tagged code fences. |
| Relative markdown links | Mostly OK after small fix | One handoff example was clarified to avoid misleading path interpretation from `docs/handoff/`. |

## Release/readme/docs consistency

Findings:

- `README.md` current-status and release-readiness sections remain coherent for pre-alpha / v0.1 planning state.
- `docs/release/v0.1.0-readonly-plan.md` and checklist remain conservative and readable enough for a release gate.
- `CHANGELOG.md` is useful but raw-source readability is reduced by long one-line phase entries in Unreleased.
- `PROJECT_STATUS.md` is durable and complete, but raw-source readability is also reduced by long lines. This is a maintainability issue, not a release safety blocker.

## GitHub project hygiene

Authenticated `gh` was available. Open issues were reviewed before issue creation.

Created issue:

- #28 — Improve markdown source readability before wider announcement (`documentation`, `audit`).

No issue was created for the individual historical fence/link nits because they were safely fixed directly and would be noisy as standalone issues.

## Security notes

This was not a professional security audit.

Formatting findings do not change the security posture. The docs still avoid security-audited/production-ready claims, still warn against public exposure of early builds, and still tell users to test copied/disposable books first.

## Test/CI notes

Phase 68 is audit/docs-only and does not make a release-readiness verdict or change product code. Relevant verification is static/docs-focused:

- `git status --short --branch` before edits.
- `git --version`.
- `gh --version` and `gh auth status`.
- custom markdown source scan for long lines, unlabeled code fences, and missing relative links.
- `gh issue list` to avoid duplicate/noisy issue creation.
- `git diff --check` after edits.

Full backend/frontend/Docker checks were not required for this formatting-only phase because no product code changed and no v0.1 readiness verdict was issued.

## Recommended next actions

1. Keep #24 and #25 as required gates before any `v0.1.0-readonly` tag/release.
2. Use #28 for gradual markdown source readability cleanup before wider announcement.
3. Prefer wrapping new prose in README/release/status docs at review-friendly widths.
4. Avoid a noisy whole-repo formatting churn unless maintainers explicitly request it.
5. Keep #27 visible as a security-hardening follow-up before treating deployment posture as hardened.

## Suggested / created GitHub issues

Created:

- #28 — Improve markdown source readability before wider announcement.

Suggested but not created:

- None. Individual historical fence/link nits were fixed directly and do not need separate issues.

## What not to do next

- Do not publish `v0.1.0-readonly` from this formatting verdict.
- Do not claim production readiness, audited security, broad compatibility, hosted SaaS readiness, collaborative accounting, or safe write mode.
- Do not expand controlled-write scope.
- Do not perform a noisy whole-repo rewrap without maintainer intent.
- Do not commit real financial data, real screenshots, `.env`, app DBs, backups, secrets, keys, certs, or real exports.
- Do not start Phase 69 unless explicitly requested.
