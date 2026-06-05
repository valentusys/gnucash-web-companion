# PROJECT_STATUS

Last updated: 2026-06-04

## Quick navigation

Use this file as the high-level ledger of project decisions. For detailed evidence, prefer the linked
handoff, release, dogfood, and audit docs rather than duplicating long blocks here.

- Public overview: [README.md](README.md), [README.ru.md](README.ru.md), and
  [CHANGELOG.md](CHANGELOG.md).
- Current public release status:
  [v0.5.0-public-readonly-beta](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.5.0-public-readonly-beta)
  remains the public read-only beta; `v0.5.1-public-readonly-beta` is not published.
- Current safety posture: writes are disabled by default; see
  [docs/write-alpha/copied-book-write-alpha-posture.md](docs/write-alpha/copied-book-write-alpha-posture.md)
  for controlled-write boundaries.
- Active issue queue:
  [#36](https://github.com/valentusys/gnucash-web-companion/issues/36) controlled-write readiness
  gates. [#22](https://github.com/valentusys/gnucash-web-companion/issues/22) and
  [#28](https://github.com/valentusys/gnucash-web-companion/issues/28) are closed.
- Latest handoffs/docs: `docs/handoff/release-no-release-decision-docs-r4.md`,
  `docs/handoff/issue22-reconcile-and-issue36-owner-writebeta-final-report.md`,
  `docs/release/v0.4-owner-writebeta-readiness-unreleased.md`,
  `docs/release/owner-writebeta-owner-approval-boundary.md`,
  `docs/handoff/issue36-current-state-reconcile.md`,
  `docs/handoff/issue36-package-4-owner-writebeta-pm-decision.md`, and
  `docs/handoff/issue36-package-5-release-artifacts-or-skip.md`.

## Current status snapshot

- Public read-only beta: `v0.5.0-public-readonly-beta` remains current.
- Not published: `v0.5.1-public-readonly-beta`; no public write beta; no stable, production-ready, or
  security-audited release claim.
- Write-mode default: `GNUCASH_WRITES_ENABLED=false` remains default; enabled write-alpha/writebeta
  work remains experimental and `APP_ENV=test` gated.
- Current open queue: #36 controlled-write readiness gates. #22 compatibility fixtures and #28 are
  closed. For #36, the W3 copied-book dogfood gate is now accepted narrowly for the staged
  outside-git copied/restorable target and exact PM-authorized counts: 2 CREATE, 1 metadata/memo-only
  PATCH on a write-alpha-created transaction, and 1 DELETE of a write-alpha-created disposable
  transaction. #36 remains open for supported-version compatibility, real-book/owner-only decisions,
  and release/no-release gates. No release was published; `NO_RELEASE` remains current.
- Current #36 docs reconciliation: owner-writebeta remains maintenance-only and unreleased until
  explicit owner approval. The guard state still requires default `GNUCASH_WRITES_ENABLED=false`,
  enabled write-alpha/writebeta `APP_ENV=test` gating, no public write beta, no real/private/original/
  working/only-copy safety claim, and no stable, production-ready, or security-audited wording. The
  owner-approval docs now state that clean checks are repository hygiene only, not release
  authorization, and that a future release-candidate task must start from an explicit owner/PM scope
  decision rather than infer approval from readiness docs.
- Recently closed queues: #13, #41, #42, #43.

## Repository

- Issue #22 Desktop-generated synthetic SQLite fixture gate completed with decision
  `CLOSE_22_NARROW_DESKTOP_SYNTHETIC_SQLITE_EVIDENCE_ONLY`. With explicit operator approval, GUI
  automation tooling was installed and GnuCash 5.14 Desktop created a disposable synthetic SQLite book
  in isolated Xvfb with isolated home/config/cache paths. The raw DB stayed outside git. Redacted
  metadata recorded SQLite `versions` markers (`Gnucash = 3000000`, `Gnucash-Resave = 19920`) and safe
  table counts only; fail-closed preflight accepted the candidate; default-read-only service validation
  opened accounts/summary/report paths with `GNUCASH_WRITES_ENABLED=false` and checksum unchanged. No
  private/owner/source-only book was opened/copied/mutated, and no raw DB/evidence was committed. #22 is
  closed narrowly; #36/v0.4 owner-writebeta remains blocked from release-confidence use of broad
  compatibility or write compatibility.

- Daytime W3 copied-book dogfood completed for #36 on a staged outside-git copied/restorable target.
  The PM authorized exact counts in the same execution context: CREATE 2, metadata/memo-only PATCH 1,
  and DELETE 1. The W3 helper reported 4 successful routed audit entries, route backups present,
  read-back for retained/deleted write-alpha-created transactions, restore from pre-batch backup,
  read-only compatibility open, and default-disabled CREATE/PATCH/DELETE probes returning 403. Raw
  evidence remains outside git; committed docs are redacted. No original/private/working/only-copy book
  was mutated; no public write beta, owner-writebeta release, stable release, production claim, or
  security-audited claim was made. Handoffs: `docs/handoff/daytime-w3-gate.md`,
  `docs/handoff/daytime-w3-authorization.md`, and `docs/handoff/daytime-w3-dogfood-worker.md`.

- Overnight worker `overnight-2026-06-02-worker-20` completed a non-mutating #36 remaining-gates
  audit packet. Added `docs/write-alpha/issue-36-remaining-gates.md` with the exact accepted evidence,
  closure blockers, future copied/restorable mutation evidence requirements, real/private/original/
  only-copy boundary, no-release/public posture, and closure-decision requirements. The committed
  write-safety guard now fails closed if this packet loses keep-open, same-context owner + PM
  authorization, `GNUCASH_WRITES_ENABLED=false`, `APP_ENV=test`, no-public-write, `NO_RELEASE`, or
  CREATE 0 / PATCH 0 / DELETE 0 markers. Mutation counts stayed zero; no private/original/working book
  was opened, copied, or mutated; #36 remains open.

- Overnight worker `overnight-2026-06-02-worker-19` completed a non-mutating #36 conservative
  write-compatibility wording guard. `scripts/check_write_safety_defaults.py` now checks
  `docs/write-alpha/evidence-matrix.md` and `docs/v0.2-controlled-writes.md` for required caveats:
  supported-version write compatibility remains pending, claims stay tied to synthetic/disposable or
  copied/restorable evidence only, current DELETE evidence is not a real-book claim, and public write
  beta/production/security-audited wording remains blocked. Focused guard tests cover broad
  compatibility-claim rejection and missing-caveat rejection. Mutation counts: CREATE 0 / PATCH 0 /
  DELETE 0; no real/private/original/working/only-copy book was opened, copied, or mutated; no write
  gate/default was weakened; #36 remains open.

- Overnight worker `overnight-2026-06-02-worker-18` completed a #28 compatibility Markdown
  readability guard package. `docs/gnucash-compatibility.md` now has a wrapped top status/blocker
  section with #22 Desktop fixture, synthetic/disposable-only evidence, and unclaimed-backend posture
  visible before the matrix tables. `scripts/check_markdown_readability.py` now includes the
  compatibility doc and the current handoff in its default scan, requires top #22 Desktop fixture
  blocker navigation, and bounds compatibility-doc long-line scanning to the current readable
  status/matrix preamble while allowing table rows. `scripts/check_public_status.py` now accepts
  wrapped compatibility required fragments. No compatibility/support safety wording was broadened.

- Overnight worker `overnight-2026-06-02-worker-17` completed a #22 compatibility-status claim
  guard package. `scripts/check_public_status.py` now reads `docs/gnucash-compatibility.md`, requires
  explicit Desktop-generated fixture blocker language, requires synthetic/disposable-only evidence
  wording, requires PostgreSQL/MySQL/MariaDB unclaimed-backend wording, and fails closed for affirmative
  GnuCash Desktop version or broad SQL-backend support claims. Focused guard tests were added in
  `apps/api/tests/test_public_status_guard.py`. No Desktop fixture was generated, no book/private
  evidence was opened/copied/mutated, and #22 remains open until an isolated Desktop-generated
  synthetic SQLite fixture exists and passes fail-closed preflight plus default-read-only validation.

- Overnight worker `overnight-2026-06-02-worker-16` completed a non-mutating #36 maintainer
  review/recovery procedure audit packet. `docs/write-alpha-recovery-procedure.md` now contains
  pre-milestone human review checkpoints, a hard-stop/recovery decision tree, exact evidence required
  before any future copied-book/write milestone, rollback/read-back/audit expectations, explicit
  separation between accepted non-mutating evidence and future mutation evidence, and #36
  keep-open/no-release posture. `docs/write-alpha-maintainer-checklist.md` and the evidence matrix
  now list this packet as review-only evidence. Mutation counts: CREATE 0 / PATCH 0 / DELETE 0; no
  real/private/original/working/only-copy book was opened, copied, or mutated; no write gate/default
  was weakened; #36 remains open.

- Overnight worker `overnight-2026-06-02-worker-15` completed a non-mutating #36 maintainer
  readiness audit/checklist package. `docs/write-alpha-maintainer-checklist.md` now consolidates
  accepted #36 evidence links, current keep-open recommendation, no-release/no-public-write posture,
  `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` boundaries, owner-input/real-book/copy-book
  constraints, and exact next worker packages. `scripts/check_write_safety_defaults.py` now also
  guards required #36 audit checklist wording, with synthetic test coverage. Mutation counts: CREATE 0
  / PATCH 0 / DELETE 0; no real/private/original/working/only-copy book was opened, copied, or
  mutated; no write gate/default was weakened; #36 remains open.

- Overnight worker 12 added a compatibility matrix report renderer/checker to the existing #22
  matrix helper. The pure helper renders conservative operator summaries from already-redacted rows
  and validates that summaries preserve synthetic/disposable tested evidence, manual fixture blockers,
  unclaimed backends, and Desktop candidate gate status. It fails closed for broad compatibility
  wording and private-looking path/account/memo/description/amount evidence. No Desktop fixture was
  generated, no private/original/only-copy book was opened/copied/mutated, and #22 remains open for
  isolated Desktop-generated synthetic fixture creation plus redacted metadata and read-only
  validation. Handoff: `docs/handoff/overnight-2026-06-02-worker-12.md`.

- Overnight worker `overnight-2026-06-02-worker-11` completed a #28 markdown readability guard
  package. Added `scripts/check_markdown_readability.py` plus focused regression tests so selected
  public/status docs and the current handoff fail closed for missing top status/safety signal,
  missing PROJECT_STATUS or handoff issue navigation, missing safety-warning preservation guidance,
  and unstructured long prose outside allowlisted code fences, URLs, tables, and command-like lines.
  Public status remains conservative: `v0.5.0-public-readonly-beta` remains current,
  `v0.5.1-public-readonly-beta` is not published, `GNUCASH_WRITES_ENABLED=false` remains default,
  enabled writes remain experimental/`APP_ENV=test` gated, and no public write beta/stable/
  production/security-audited claim was added. Handoff:
  `docs/handoff/overnight-2026-06-02-worker-11.md`.

- Overnight worker `overnight-2026-06-02-worker-10` completed a #36 concurrency/lock-contention
  readiness guard. The existing pure/non-mutating backup/restore evidence validator now fails closed
  unless synthetic evidence includes serialized per-book lock acquisition, active-lock contention
  blocked/rejected, no overlapping write execution, contention/rejection audit-trail, and
  default-disabled no-write probe markers. Docs and the evidence matrix list these markers as future
  write-milestone prerequisites. Mutation counts: CREATE 0 / PATCH 0 / DELETE 0; no
  real/private/original/only-copy book was opened, copied, or mutated; no write gate/default was
  weakened; #36 remains open for future copied/restorable mutation evidence gates requiring explicit
  same-context authorization. Handoff: `docs/handoff/overnight-2026-06-02-worker-10.md`.

- Overnight worker `overnight-2026-06-02-worker-09` completed a #36 recovery/hard-stop
  readiness expectations guard. The existing pure/non-mutating backup/restore evidence validator now
  fails closed unless synthetic evidence includes explicit abort/hard-stop after failed restore,
  read-back, or audit; backup preservation; no retry on the same copy before recovery; maintainer
  review or owner escalation; and default write-disabled reset/probe markers. Docs and the evidence
  matrix list these markers as future write-milestone prerequisites. Mutation counts: CREATE 0 /
  PATCH 0 / DELETE 0; no real/private/original/only-copy book was opened, copied, or mutated; no
  write gate/default was weakened; #36 remains open for concurrency/lock-contention and future
  copied/restorable mutation evidence gates. Handoff:
  `docs/handoff/overnight-2026-06-02-worker-09.md`.

- Overnight worker `overnight-2026-06-02-worker-08` completed a #28 `PROJECT_STATUS.md`
  navigation/current-status cleanup. The file now starts with public overview links, direct active-issue
  links (#22/#28/#36), current public release status, conservative write-mode safety posture, and latest
  handoff pointers before the long historical ledger. A focused markdown readability regression test now
  guards these navigation links and safety/status claims. Public status remains unchanged:
  `v0.5.0-public-readonly-beta` remains current, `v0.5.1-public-readonly-beta` is not published,
  `GNUCASH_WRITES_ENABLED=false` remains default, enabled writes remain experimental/`APP_ENV=test`
  gated, and no public write beta/stable/production/security-audited claim was added. Handoff:
  `docs/handoff/overnight-2026-06-02-worker-08.md`.

- Overnight worker `overnight-2026-06-02-worker-07` completed a #36 backup/restore readiness
  evidence checklist guard. Added a pure non-mutating `validate_backup_restore_readiness_evidence`
  helper plus synthetic tests and docs requiring copied/disposable fixture classification, outside-git
  or approved-temp backup location, restore hash/row-count/schema-marker evidence, no private/raw
  evidence, default write-disabled posture, and a recovery/hard-stop note before future write
  milestones. Missing markers fail closed and reports do not echo raw paths/account/memo/amount data.
  Mutation counts: CREATE 0 / PATCH 0 / DELETE 0; no GnuCash book was opened, copied, or mutated.
  Handoff: `docs/handoff/overnight-2026-06-02-worker-07.md`.

- Overnight worker `overnight-2026-06-02-worker-06` completed a #28 README.ru source-readability
  slice. `README.ru.md` now keeps the top public-status posture compact, links detailed phase/release
  history to `PROJECT_STATUS.md`, release docs, and handoffs, and preserves conservative wording:
  `v0.5.0-public-readonly-beta` remains current, `v0.5.1-public-readonly-beta` is not published,
  `v0.4.0-owner-writebeta` remains deferred, `GNUCASH_WRITES_ENABLED=false` remains default, enabled
  writes remain experimental/`APP_ENV=test` gated, and real/private/original/only-copy books remain
  unsafe write targets. A focused README.ru readability regression test was added. Handoff:
  `docs/handoff/overnight-2026-06-02-worker-06.md`.

- Overnight worker `overnight-2026-06-02-worker-04` completed a #22 Desktop-generated
  fixture candidate acceptance preflight package using only synthetic/tmp JSON metadata. Added
  `scripts/preflight_desktop_fixture_candidate.py` plus matrix helper coverage so future
  operator-supplied Desktop synthetic candidates fail closed unless they include explicit
  Desktop-generated/synthetic markers, bounded `GnuCash X.Y` version evidence, SQLite backend,
  synthetic/disposable scope, synthetic-disposable evidence marker, and a default-read-only validation
  marker. Copied/private scope, unsupported backends, path/private-looking fields,
  account/memo/description-like values, and amount-like values are rejected without echoing private
  content. This is an acceptance gate only: no GUI was launched, no Desktop-generated fixture was
  produced, no real/private/only-copy book was opened/copied/mutated, and #22 remains open for actual
  isolated disposable GUI/manual-safe Desktop fixture creation plus redacted metadata and read-only
  validation. Handoff: `docs/handoff/overnight-2026-06-02-worker-04.md`.

- Overnight worker `overnight-2026-06-02-worker-03` completed a #22 Desktop tooling
  probe/checker hardening package using mocked command outputs only. The safe Desktop tooling probe
  now treats successful `--version` output as unsafe unless it is bounded, non-private-looking, and
  has an unambiguous `GnuCash X.Y` version token; overlong, path/account/memo/description/amount-like,
  or ambiguous strings fail closed. The post-mutation compatibility checker now also fails closed if
  `gnucash-cli --version` evidence is unsafe/ambiguous even when the mocked report command succeeds.
  No GUI was launched, no real/private/only-copy book was opened/copied/mutated, no Desktop-generated
  fixture was committed, and #22 remains open for isolated disposable GUI/manual-safe Desktop fixture
  creation plus redacted metadata collection and default-read-only validation. Handoff:
  `docs/handoff/overnight-2026-06-02-worker-03.md`.

- Overnight worker `overnight-2026-06-02-worker-02` completed a #36 default-disabled reset probe
  package. Owner-writebeta route tests now prove a simulated post-mutation `verify-reset`/`reset-disabled`
  path returns to `disabled`, clears stale active-arm preview/confirmation refs, preserves the default
  `GNUCASH_WRITES_ENABLED=false` blocked reason, and leaves validate/CREATE/PATCH/DELETE probes
  403/read-only after reset. Mutation counts: CREATE 0 / PATCH 0 / DELETE 0; no GnuCash book was opened
  or mutated. Handoff: `docs/handoff/overnight-2026-06-02-worker-02.md`.

- Overnight worker `overnight-2026-06-02-worker-01` completed a #28 changelog/release-doc
  readability slice. `CHANGELOG.md` now starts with quick navigation and grouped current-release
  posture before the long history; `docs/release/v0.5.0-public-readonly-beta-notes.md` and final-gate
  evidence gained source-readable navigation/sections. Public release truth is unchanged:
  `v0.5.0-public-readonly-beta` remains current, `v0.5.1-public-readonly-beta` is not published,
  `GNUCASH_WRITES_ENABLED=false` remains default, and no public write beta/stable/production/security-
  audited claim was added.

- Autonomous multiqueue run completed six safe packages across #22/#28/#36 and recorded
  `docs/handoff/autonomous-multiqueue-final-report.md`. #22 remains open with exact headless Desktop
  fixture blocker evidence (`gnucash-cli` 5.14 available; GUI `gnucash` cannot initialize without
  `$DISPLAY`; no Desktop-generated synthetic SQLite fixture yet). #28 received three markdown
  readability packages for README top status, PROJECT_STATUS quick navigation, and developer
  readability guard tests. #36 received a non-mutating readiness status refresh plus route-level
  fail-closed tests/fix requiring `mutating` state before owner-writebeta verify-reset. Full local gate
  passed: backend `643 passed`, web check/auth-routes/build passed, Compose config passed, public-status
  guard passed, diff check passed, tracked hygiene passed. Latest CI for `29bee81` passed. Open issues
  remain #22/#28/#36; open PRs: none. PM decision: NO_RELEASE. GnuCash mutations: CREATE 0 / PATCH 0 /
  DELETE 0; no private/runtime evidence touched; `GNUCASH_WRITES_ENABLED=false` remains default.

- Autonomous true 6h final report for #22 recorded five substantial safe compatibility workflow cycles and PM `NO_RELEASE`. Completed redaction/validator hardening, fixture-scope boundary docs/tests, Desktop tooling probe redaction and local command/version blocker evidence, safer GitHub compatibility issue template, full local gate, #22 update comment, and CI confirmation for latest commit `e9d53fc`. #22 remains open because a tested Desktop-generated synthetic SQLite fixture still requires isolated disposable GUI/manual-safe Desktop fixture creation plus default-read-only validation. Mutation counts: CREATE 0 / PATCH 0 / DELETE 0. No book/private evidence was touched; writes remain disabled by default; no release was published.

- Autonomous true 6h cycle 5 for #22 added schema-like gates to `scripts/validate_compatibility_report.py`: all report fields must be strings, non-notice text fields are bounded, backend and fixture-scope values must be from allowed enums, and conservative evidence-class matching still applies. Validator tests passed (`6 passed`) and generated safe reports validate successfully. No book/private evidence was touched; writes remain disabled by default; no release was published.

- Autonomous true 6h cycle 4 for #22 hardened the GitHub compatibility-report issue template. `.github/ISSUE_TEMPLATE/compatibility-report.yml` now requests only safe metadata fields (OS, browser, Docker/runtime, GnuCash version, backend, fixture scope, generic error class) and explicitly forbids books, app DBs, backups, exports, screenshots, `.env`, tokens, private paths, account names, transaction descriptions, memos, and amounts. Template tests passed (`3 passed`). No book/private evidence was touched; writes remain disabled by default; no release was published.

- Autonomous true 6h cycle 3 for #22 hardened the safe Desktop tooling probe. `apps/api/scripts/probe_gnucash_desktop_tooling.py` now redacts private-looking path/account/memo/description/amount output even if a `--version` command unexpectedly prints it; regression tests passed (`8 passed`). The local non-mutating probe found `gnucash-cli` 5.14 available and `gnucash` present but headless GUI initialization blocked; this is command/version evidence only, not Desktop-generated fixture evidence. No book was opened or searched; writes remain disabled by default; no release was published.

- Autonomous true 6h cycle 2 for #22 added code-backed fixture-scope boundary vocabulary. `apps/api/app/compatibility_matrix.py` now exposes conservative meanings for `synthetic`, `disposable`, `copied-restorable`, and `unknown`, with tests proving the mapped evidence classes remain non-claiming and docs defining that private row data remains forbidden and report metadata alone does not become a tested matrix row. Focused matrix tests passed (`8 passed`). No book/private evidence was touched; writes remain disabled by default; no release was published.

- Autonomous true 6h cycle 1 for #22 hardened public compatibility report redaction/validation. `scripts/safe_compatibility_report.py` now redacts account-like, memo-like, description-like, amount-like, and path-like operator-provided values; `scripts/validate_compatibility_report.py` rejects unsafe account/memo/description-like report values while preserving conservative evidence-class checks. Focused tests passed (`9 passed`). No book/app DB/backup/export/screenshot/private evidence was touched; writes remain disabled by default; no release was published.

- Autonomous long run for #13 completed admin-only app-metadata management for already-mounted local copied/test SQLite GnuCash books plus safe invalid-schema diagnostics: registration with path-safe SQLite/GnuCash schema validation, registered-book listing, set/change default metadata book, remove-from-registry without deleting the underlying GnuCash file, and `invalid_gnucash_schema` blocking before GnuCash service-layer opens. Non-admin access is blocked; private paths remain redacted; diagnostics inspect SQLite table names only; required local checks passed; #13 was updated and closed. Pushed commits include `b991a70`, `f03c71b`, and `f54584c`; CI passed for `f54584c` at https://github.com/valentusys/gnucash-web-companion/actions/runs/26742008787. GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0. `GNUCASH_WRITES_ENABLED=false` remains default. No upload, accounting write, file deletion, public write beta, stable/production release, tag, or release publication was added.

- Issue #43 is accepted for closure after the focused completion run. The local evidence-helper audit payload bug was fixed and tested (`AuditLog.payload_json`), synthetic/helper rehearsal passed, and a fresh copied/restorable owner-book rerun completed routed owner-writebeta/write-alpha counts: CREATE 2, metadata-only PATCH 1, DELETE 1. Final DELETE verify-reset/reset-disabled evidence was captured (`reset_required` -> `disabled`), read-back/audit/backup/restore evidence passed, and disabled CREATE/PATCH/DELETE probes returned 403. PM decision remains NO_RELEASE; no tag/release was published. Public/default posture remains read-only; real working/private/original/only-copy mutation remains blocked.

- Earlier Issue #43 copied-book dogfood resumed after a fresh owner-provided outside-git copied/restorable SQL book was staged on this host. Redacted preflight passed and the PM-locked routed mutation counts executed through owner-writebeta/write-alpha: CREATE 2, metadata/memo-only PATCH 1, DELETE 1. Post-run read-back, 4 route backup refs, 4 successful audit rows, restore verification, piecash compatibility read, and disabled CREATE/PATCH/DELETE probes passed. #43 stayed open because the local evidence helper aborted after the successful DELETE on an audit payload field-name bug before capturing the final DELETE owner-writebeta verify/reset transition. Release decision remained NO_RELEASE. Real working/private/original/only-copy book mutation remained blocked. Public read-only beta remained `v0.5.0-public-readonly-beta`; no `v0.5.1` or owner-writebeta release was published.

- Issue #43 focused Phases A-M completed with final NO_RELEASE. Routed owner-writebeta foundation was added: redacted preflight/status, preview, confirmation, verify-reset/reset-disabled API endpoints; active-session guard integration for existing write-alpha CREATE/PATCH/DELETE routes; conservative owner-writebeta UI information shell; and A-M audit/handoff/release decision docs. Copied-book dogfood was initially not run because an owner-provided outside-git copied/restorable book was not staged on this host. Mutation counts: CREATE 0, PATCH 0, DELETE 0. Real working/private/original/only-copy book mutation remains blocked. Public read-only beta remains `v0.5.0-public-readonly-beta`; no `v0.5.1` or owner-writebeta release was published.

- Phases 731–830 completed. Live checks confirmed `v0.5.1-public-readonly-beta` is absent and `v0.5.0-public-readonly-beta` remains the current public read-only beta. Issues #41/#42 are closed after Phase 731–830 verification; #43 remains open for owner-writebeta routed/copied-book work. No release was published. Mutation counts: CREATE 0, PATCH 0, DELETE 0. Real working-book mutation remains blocked.

- GitHub: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Status: beta/pre-alpha mix / `v0.5.0-public-readonly-beta` remains the current public read-only beta pre-release;
  `v0.2.8-writealpha` remains the current public experimental write-alpha pre-release. Completed through Phase 830. Phases 731–830 reconciled the missing `v0.5.1-public-readonly-beta` claim as FINAL_NO_RELEASE, strengthened owner-writebeta state-machine primitives/tests, closed #41/#42 after verification, kept #43 open for owner-writebeta routed/copied-book work, and preserved default-disabled/test-gated write posture. No GitHub release was published; mutation counts remain CREATE 0, PATCH 0, DELETE 0; no original/private/working book was touched. Completed through Phase 630 was the prior public-status guard baseline before this run. Phases 531–630 produced public-readonly support/safety artifacts, a tracked-file hygiene
  guard, owner-writebeta workflow posture docs, deployment diagnostics/privacy guidance, and a final
  PM NO_RELEASE decision plus follow-up GitHub issues #41, #42, and #43. No new GitHub pre-release was published: `v0.4.0-owner-writebeta` remains
  deferred, no public write beta was created, and no Phase 631+ was opened. Mutation counts in
  Phases 531–630: CREATE 0, PATCH 0, DELETE 0; the original/working/private GnuCash book was not
  touched. `GNUCASH_WRITES_ENABLED=false` remains default and enabled write-alpha remains
  `APP_ENV=test` gated. Phases 481–530 published `v0.5.0-public-readonly-beta` as a conservative
  read-only GitHub pre-release and deferred `v0.4.0-owner-writebeta`. No stable release,
  production deployment, default write enablement, private evidence, or broad safety claim was added.
  Phases 431–480 had
  previously completed the owner-writebeta/public-readonly-beta roadmap run with final NO_RELEASE and
  produced safe v0.4/v0.5 exit criteria, non-mutating owner write-session preflight/manifest prototype,
  UI warning copy, owner-writebeta posture docs, and public read-only beta draft install/security/
  feedback docs. Mutation counts in Phases 481–530: CREATE 0, PATCH 0, DELETE 0. Phase 231 ran the `v0.2.5-writealpha` final release gate after Phase 230 green
  release-candidate dogfood, confirmed local/backend/frontend/Docker/public-status/sensitive-file
  gates, waited for exact release/status commit CI, and published only the annotated tag plus GitHub
  pre-release. Phase 232 reconciled public status/changelog wording after publication. Phase 233
  improved raw markdown readability for README/README.ru/CHANGELOG/PROJECT_STATUS while preserving
  safety wording. Phase 234 added a conservative copied-book write-alpha dogfood runbook for future
  local-only copied/disposable testing without running real/private copied-book dogfood. Phase 235
  added a redacted local-only preflight CLI for future copied/disposable write-alpha targets. Phase
  236 added a redacted dogfood evidence schema and helper so later dogfood reports can reject or
  redact raw path-like, amount-like, memo/account-name, and payload-like data before commit. Phase
  237 added an explicitly unsafe-for-real-books `.env.writealpha.example` reference and
  `docs/write-alpha/environment.md` operator guidance for local-only write-alpha testing without
  changing default read-only config. Phase 238 added a redacted, non-mutating
  `scripts/write_alpha_readiness.py` readiness command plus backend helper/tests so operators can
  inspect write-alpha prerequisites — writes enabled flag, `APP_ENV=test` gate, derived backup
  policy, app DB reachability, default book read-only openability, and no-mutation proof — without
  constructing the write service or exposing raw paths. Phase 239 ran a synthetic copied-book
  no-mutation dry-run through Docker/Caddy using the Phase 236 evidence schema: preflight/readiness
  passed or blocked exactly as expected, default-disabled API/browser smoke passed, disabled
  validate/create/PATCH/DELETE probes returned 403, checksum evidence matched before/after, and no
  backups/locks/audit rows were produced. Phase 240 prepared `v0.2.6-writealpha` release-candidate
  notes, checklist, and final-gate draft because Cycle 1 produced meaningful operator-safety tooling
  and synthetic no-mutation dry-run evidence. Phase 241 called PM, received authorization, reran the
  final gate, waited for exact release/status commit CI, and published `v0.2.6-writealpha` as a
  conservative GitHub pre-release. Phase 242 passed the Cycle 2 analyst gate with no blocking
  release/safety/private-data/write-mode issue. Phase 243 added an app metadata-only write-alpha
  transaction ownership model and CREATE-path ownership marker so later PATCH/DELETE phases can be
  constrained to transactions created by write-alpha. Phase 244 added the backend PATCH ownership
  guard: enabled write-alpha PATCH now requires a same-book app-metadata ownership marker before the
  write service is constructed, rejects historical/imported/manual non-owned transactions with 403,
  preserves the existing metadata/memo-only PATCH scope, and updates `last_mutated_at` after allowed
  PATCH. Phase 245 added the backend DELETE ownership guard: enabled write-alpha DELETE now requires
  the same same-book app-metadata ownership marker before constructing the write service, rejects
  historical/imported/manual non-owned transactions with 403 before backup/lock/audit/mutation,
  still allows DELETE for write-alpha-created synthetic transactions, and refreshes
  `last_mutated_at` after allowed DELETE. Phase 246 aligned the frontend transaction detail page with
  those backend ownership boundaries: edit/delete controls are hidden for non-owned historical/manual
  transactions, write-alpha-owned synthetic transactions can show experimental controls only under
  explicit write mode, and non-owned transactions show safe explanatory read-only copy. Backend
  ownership guards remain authoritative. Phase 247 ran synthetic/disposable Docker/Caddy ownership
  route-family dogfood: one write-alpha-owned synthetic transaction was created, PATCHed, and
  DELETEd; non-owned PATCH/DELETE probes returned 403 without backup growth; backup/audit/lock/restore
  evidence was recorded as redacted counts/statuses; and the reset default-disabled API smoke verified
  validate/create/PATCH/DELETE probes still return 403. Phase 248 extended the read-only
  write-alpha audit summary endpoint/UI with safe ownership evidence — write-alpha-created marker
  count, non-owned mutation rejection count, and last successful mutation type — while continuing to
  render only bounded counters/action labels, safe transaction ID prefixes, opaque backup refs, and
  safe errors. Raw payloads, amounts, memos, account names, and paths remain hidden. Phase 249
  documented the write-alpha ownership boundary and operator warnings across write-alpha docs:
  CREATE creates write-alpha-owned transactions, PATCH/DELETE are limited to write-alpha-owned
  transactions for the same app metadata book, and historical/imported/manual GnuCash transactions
  remain read-only in this app. The warnings also state that this does not make real/private,
  original, production, shared, or only-copy books safe for write-alpha. Phase 250 prepared
  `v0.2.7-writealpha` release-candidate notes, checklist, and final-gate draft because the Cycle 2
  gates are satisfied: backend ownership guards are implemented, synthetic route-family dogfood
  passed, and operator docs are synchronized. Phase 251 called PM, received `AUTHORIZE_RELEASE`,
  reran the final local release gate, waited for exact release/status commit CI, and published
  `v0.2.7-writealpha` as a conservative GitHub pre-release. Phase 252 passed the Cycle 3 analyst gate
  for maintainer copied-book dogfood packaging. Phase 253 added a maintainer copied-book dogfood
  packet that defaults to dry-run first, forbids original and only-copy books, requires outside-git
  copied/restorable targets plus independent backup, restricts the optional mutation path to one
  CREATE first, defers PATCH to later explicit review, prohibits DELETE unless separately authorized
  for a write-alpha-created test transaction, requires redacted evidence and restore proof, and ends
  with cleanup plus reset to `GNUCASH_WRITES_ENABLED=false`. Phase 254 added
  `scripts/write_alpha_copied_book_dogfood.py`, a local-only copied-book dogfood wrapper with
  explicit `--dry-run` and `--create-one` modes, required confirmations, redacted preflight,
  pre-step backup creation, redacted evidence writing, unsafe-path rejection, and default-disabled
  reset proof after each run. Phase 255 strengthened the transaction create/write-alpha UI warnings
  for maintainer copied-book create-only dogfood: the EN/RU copy now requires an outside-git
  copied/restorable test book with the original untouched, dry-run first, at most one CREATE test
  transaction, independent backup plus restore plan, audit/app-backup/lock evidence, and no
  production use. Phase 256 added a redacted best-effort post-mutation compatibility harness that
  opens a copied/disposable target read-only with piecash, optionally runs already-available
  `gnucash-cli` report probing, records `pass`/`blocked`/`fail`, treats missing Desktop/CLI tooling as
  a blocker rather than compatibility evidence, and explicitly avoids broad Desktop/version claims.
  Phase 257 added a redacted restore verification harness for copied-book dogfood that restores only
  an outside-git copied working book from an outside-git pre-mutation backup, verifies checksum and
  piecash read-back state, optionally runs a read-only web/API probe, records bounded restore
  evidence, and checks the committed/default disabled-write posture without claiming production
  disaster recovery. Phase 258 rehearsed the full maintainer copied-book package on synthetic/
  disposable fixture copies: dry-run and create-one wrapper steps passed, Docker/Caddy create smoke
  read-back passed with one routed CREATE plus backup/audit/lock evidence, restore verification passed
  with checksum and piecash read-back, a temporary Debian GnuCash CLI report probe passed, and reset
  default-disabled API smoke verified validate/create/PATCH/DELETE 403 probes. The host compatibility
  harness still records missing host `gnucash-cli` as blocked rather than broad compatibility evidence,
  and no owner/private/original/only-copy book, release/tag, default write change, `APP_ENV=test` gate
  weakening, raw private evidence, or real/private/only-copy write-safety claim was added. Phase 259
  completed the owner copied-book decision gate: the next reasonable owner ask is dry-run only with an
  outside-git copied/restorable book and the original untouched; CREATE-one is not the immediate ask and
  can be considered only after owner dry-run evidence confirms preflight, independent backup,
  redaction, local-only runtime, restore plan, and reset to `GNUCASH_WRITES_ENABLED=false`. No owner
  dogfood was executed, no private data was requested, no release/tag was published, and no
  real/private/only-copy write-safety claim was added. Phase 260 prepared unpublished
  `v0.2.8-writealpha` release-candidate notes, checklist, and final-gate draft because the Cycle 3
  copied-book package is strong enough for a conservative candidate while owner copied-book dogfood may
  still be pending. Phase 261 called PM, received `AUTHORIZE_RELEASE`, reran the full release gate,
  checked tag/release absence, waited for exact release/status commit CI, and published
  `v0.2.8-writealpha` as a conservative GitHub pre-release. Phase 261 did not authorize owner
  CREATE-one as the next immediate action, did not use owner/private/original/only-copy books, and did
  not add any real/private/only-copy write-safety claim. Phase 262 passed the current-state analyst
  gate after `v0.2.8-writealpha`: public docs, releases, open issues, recent CI, `.env.example`,
  rendered Compose defaults, and public-status guard were coherent; no safety blocker was found; the
  next owner-facing step remains copied-book dry-run preparation only.
  `GNUCASH_WRITES_ENABLED=false` remains
  default, `APP_ENV=test` write-alpha gating remains intact, and no production/security/public-internet/broad-compatibility or real/private-book write-safety claim is added. Phase 263 added the single owner-facing dry-run-only entrypoint `scripts/write_alpha_owner_dry_run.py`, documented it in `docs/write-alpha/owner-dry-run-quickstart.md`, updated the maintainer copied-book packet to point to that command, added no-mutation tests, and recorded redacted synthetic dry-run evidence. The entrypoint has no CREATE/PATCH/DELETE mode and validates `mutation_requested=false`, `mutation_performed=false`, and `create_command_status=not-run` before success.
- Phase 275 rechecked the Phase 274 compatibility blocker after host `gnucash-cli` became available.
  `/usr/bin/gnucash-cli` reports GnuCash 5.14, and the redacted compatibility harness passed on a
  synthetic/disposable outside-git fixture copy with piecash status pass, Desktop/CLI status pass, and
  `broad_compatibility_claimed=false`. PM was invoked because this is an owner-risk write decision and
  authorized preparing the owner CREATE-one request packet only. No owner copied-book CREATE/PATCH/DELETE
  was run; CREATE execution still requires explicit owner confirmation in the execution context;
  PATCH/DELETE remain blocked; `GNUCASH_WRITES_ENABLED=false` remains default; `APP_ENV=test` remains
  required when writes are explicitly enabled; and no broad compatibility or real/private/only-copy
  write-safety claim was added.
- Phase 276 accepted one owner copied-book CREATE-one evidence run after the exact Phase 275 confirmation
  block was provided in the current execution context. Exactly one CREATE was attempted and performed on
  a copied/restorable working copy outside git under `APP_ENV=test` with temporary explicit writes enabled;
  pre-mutation backup, read-back, one-success audit evidence, released/stale-safe lock evidence,
  compatibility through piecash plus installed `gnucash-cli`, restore verification from pre-mutation
  backup, default-disabled reset, and disabled validate/create/PATCH/DELETE probes all passed. No
  PATCH/DELETE was run, no private artifact was committed, `GNUCASH_WRITES_ENABLED=false` remains
  default, enabled write-alpha remains `APP_ENV=test` gated, and no production/security/public-internet/
  broad-compatibility or real/private/only-copy write-safety claim was added.
- Phase 277 reviewed the accepted owner copied-book CREATE-one evidence for concrete findings or bugs.
  No CREATE-one bug, failed check, restore mismatch, backup/audit mismatch, redaction concern,
  write-gate regression, or compatibility finding was identified, so no code or regression-test change
  was needed. Owner dry-run remains accepted, exactly one owner copied-book CREATE evidence remains
  accepted, PATCH/DELETE remain not run and unauthorized, `GNUCASH_WRITES_ENABLED=false` remains default,
  enabled write-alpha remains `APP_ENV=test` gated, and no production/security/public-internet/broad-
  compatibility or real/private/only-copy write-safety claim was added.
- Phase 278 refreshed the copied-book write-alpha posture in public/status docs and
  `docs/write-alpha/copied-book-write-alpha-posture.md`: owner copied-book dry-run evidence is accepted
  as dry-run-only evidence, exactly one owner copied-book CREATE evidence run is accepted for one
  copied/restorable working copy outside git, and owner PATCH/DELETE remain not run and unauthorized.
  `GNUCASH_WRITES_ENABLED=false` remains default, enabled write-alpha remains `APP_ENV=test` gated, and
  no production/security/public-internet/broad-compatibility or real/private/original/only-copy write-
  safety claim was added.
- Phase 279 invoked PM for the Cycle 2 release/no-release decision and recorded a no-release
  verdict in `docs/release/v0.2.10-writealpha-no-release-verdict.md`. No `v0.2.9-writealpha` or
  `v0.2.10-writealpha` tag/GitHub release/package/image was published because the new state is narrow
  evidence/posture progress rather than a product behavior change, and a release could overstate one
  copied-book CREATE evidence run. PATCH/DELETE remain not run and unauthorized, `GNUCASH_WRITES_ENABLED=false`
  remains default, enabled write-alpha remains `APP_ENV=test` gated, and no production/security/public-
  internet/broad-compatibility or real/private/original/only-copy write-safety claim was added.
- Phase 280 closed Cycle 2 and recommended exactly one next action: start Phase 281 analyst
  PATCH-readiness review only. The CREATE-one evidence precondition for considering PATCH readiness is
  satisfied, but no PATCH execution, owner PATCH packet, DELETE work, release, default write change,
  `APP_ENV=test` gate weakening, or broad safety claim was authorized. Owner PATCH/DELETE remain not
  run and unauthorized, and original/only-copy books remain forbidden.

- Phase 281 completed the PATCH readiness analyst gate: accepted owner copied-book CREATE-one evidence
  allows no-mutation PATCH-one planning only. PATCH execution, owner PATCH request, DELETE work, release,
  default write changes, `APP_ENV=test` gate weakening, amount/account edits, and real/private/original/
  only-copy write-safety claims remain unauthorized.

- Phase 282 prepared `docs/write-alpha/patch-one-copied-book-plan.md` without mutation. The plan
  limits any later separately authorized PATCH to metadata/memo-only changes on a same-book write-alpha-
  owned test transaction in a copied/restorable working copy, with backup/read-back/compatibility/restore/
  reset/redaction evidence. Owner PATCH remains not requested or authorized; DELETE remains blocked.
- Phase 283 rehearsed PATCH-one on synthetic/disposable data only. One write-alpha-owned synthetic
  transaction was created and PATCHed exactly once with metadata/memo-only markers; amount/account
  fingerprint stayed unchanged, backup/audit/read-back/compatibility/restore/default-disabled reset
  evidence passed, and targeted backend PATCH tests passed. Owner PATCH remains not run/unauthorized;
  DELETE remains blocked.
- Phase 284 invoked PM and authorized preparing an owner PATCH-one request packet only. Owner PATCH execution still requires later exact owner confirmation; DELETE remains blocked; defaults and gates remain unchanged.
- Phase 285 prepared the owner PATCH-one request packet with an exact confirmation block. No owner PATCH was run; DELETE remains blocked; amount/account/currency/split-count edits remain forbidden.
- Phase 286 recorded owner PATCH evidence as absent: no exact owner PATCH confirmation was provided and no owner PATCH was run. Owner PATCH evidence is not accepted and cannot support DELETE progression or release claims.
- Phase 287 PM/Analyst decision: DELETE remains blocked for owner copied-book dogfood. No DELETE was executed and no owner DELETE packet was prepared.
- Phase 288 refreshed `docs/write-alpha/evidence-matrix.md`: owner dry-run accepted, exactly one owner CREATE accepted, synthetic PATCH passed, owner PATCH absent, DELETE blocked.
- Phase 289 PM decision: no v0.2.x release. No tag, GitHub release, package, or release notes were published.
- Phase 290 practical verdict: use read-only as the practical path; synthetic/disposable write-alpha remains development-only; owner PATCH absent; DELETE blocked; original/only-copy writes forbidden.
- Phase 291 PM decision: freeze active write-alpha progression until the owner provides redacted Phase 285 PATCH-one evidence or explicitly chooses read-only maintenance. No release was published and no new writes were authorized.
- Phase 292 PATCH-one execution gate: exact Phase 285 owner confirmation was present, but the private working target could not verify the required precondition because the app metadata ownership marker points to the accepted CREATE-one transaction while that transaction is absent from the current copied working book after prior restore/reset. No PATCH was attempted or performed, DELETE was not run, writes were reset/observed disabled, and owner PATCH remains blocked pending a copied/restorable working book that still contains the Phase 276 write-alpha-created transaction.
- Phase 293 fresh CREATE-to-PATCH chain gate: the owner selected the fresh-chain direction after Phase 292, but mutation was blocked before execution because this is a new owner mutation scope. The Phase 275 CREATE-one exact authorization was already consumed in Phase 276, and the Phase 285 PATCH-one authorization targeted the Phase 276-created transaction that Phase 292 could not verify. Prepared `docs/write-alpha/owner-create-patch-chain-request.md` with the exact same-context confirmation block required before any new chain. No CREATE/PATCH/DELETE was attempted or performed, defaults/gates remain unchanged, and no release was published.
- Phase 294 owner copied-book CREATE-to-PATCH chain evidence: exact same-context owner confirmation was present, preconditions passed, and exactly one CREATE plus exactly one metadata/memo-only PATCH on that same Phase 294 write-alpha-created transaction were attempted and performed on a fresh copied/restorable working book outside git. Backups before both mutations, read-back, audit/lock evidence, readable backup artifact checks, piecash plus installed `gnucash-cli` compatibility, restore verification, reset/default-disabled verification, disabled validate/create/PATCH/DELETE probes, and redaction validation passed. DELETE was not run, private artifacts stayed outside git, defaults/gates remain unchanged, no release was published, and no production/security/public-internet/broad-compatibility or real/private/original/only-copy write-safety claim was added.
- Phase 295 audited the Phase 294 owner copied-book CREATE-to-PATCH evidence and accepted it narrowly:
  exactly one CREATE plus exactly one metadata/memo-only PATCH on the same Phase 294 write-alpha-created
  transaction in one copied/restorable working book outside git. DELETE remains not run/blocked,
  `GNUCASH_WRITES_ENABLED=false` remains default, enabled write-alpha remains `APP_ENV=test` gated, no
  private artifacts were committed, latest visible Phase 294 CI was green, public-status guard passed,
  and no production/security/public-internet/broad-compatibility or real/private/original/only-copy
  write-safety claim was added.
- Phase 296 reconciled `docs/write-alpha/evidence-matrix.md` and
  `docs/write-alpha/copied-book-write-alpha-posture.md` after the Phase 295 audit. The posture now
  distinguishes synthetic/disposable evidence, maintainer copied-test-book/package rehearsal,
  owner dry-run, owner CREATE-one, synthetic PATCH, superseded/absent owner PATCH-one, the accepted
  Phase 294/295 CREATE-to-PATCH fresh-chain evidence, and owner DELETE blocked/not run. Defaults/gates
  remain unchanged and no broad write-safety claim was added.
- Phase 297 invoked PM for the `v0.2.9-writealpha` release value decision and recorded NO_RELEASE in
  `docs/release/v0.2.9-writealpha-release-decision.md`. The accepted CREATE-to-PATCH evidence is narrow
  copied-book evidence rather than a user-facing runtime capability or broad safety correction; publishing
  could overstate safety. No tag, GitHub release, package, or image was published.
- Phase 298 implemented the Phase 297 decision by updating
  `docs/release/v0.2.9-writealpha-no-release-verdict.md` as current no-release support documentation.
  No release-candidate notes, checklist, final gate, tag, GitHub release, package, image, or stable
  release were created.
- Phase 299 ran the final `v0.2.9-writealpha` no-release gate. Backend, frontend, Docker config,
  public-status guard, diff hygiene, sensitive tracked-file scan, and latest GitHub Actions checks passed.
  Gate decision remained NO_RELEASE; no tag, release, package, image, stable release, or production
  deployment was created.
- Phase 300 executed the publication step for the no-release decision: `v0.2.9-writealpha` was not
  published. Local/remote tag and GitHub release checks confirmed `v0.2.9-writealpha` absent, while
  `v0.2.8-writealpha` remains the current public experimental write-alpha pre-release.
- Phase 301 ran the post-Cycle-1 default-read-only Docker/Caddy regression on the committed synthetic
  fixture copied to the ignored runtime book path. API and browser dogfood passed with
  `GNUCASH_WRITES_ENABLED=false`: login, dashboard, accounts, transactions, CSV export, reports,
  scheduled transactions, and write-alpha audit summary were healthy; disabled validate/create/PATCH/
  DELETE probes returned 403; write UI stayed hidden; the auth cookie was not visible through
  `document.cookie`; and no screenshots, CSVs, app DBs, books, backups, or private artifacts were
  committed.
- Phase 302 completed the owner DELETE readiness analyst gate and kept owner DELETE blocked. Existing
  owner evidence supports dry-run, one CREATE-one, and one fresh CREATE-to-PATCH chain only; DELETE has
  no owner copied-book evidence, remains destructive, and no owner DELETE request packet was prepared.
  No DELETE execution, write-enabled run, release, default write change, APP_ENV gate weakening, or
  broad write-safety claim was added.
- Phase 303 added `docs/write-alpha/owner-next-steps.md` as the practical owner-facing summary for the
  current posture: use read-only mode for practical work; dry-run is accepted only as dry-run evidence;
  one CREATE-one and one CREATE-to-PATCH chain are accepted narrowly; owner DELETE remains blocked/not
  run/no packet; original/private/production/only-copy write-alpha remains forbidden; defaults and gates
  remain unchanged.
- Phase 304 closed Cycle 1 without blockers and selected the next-cycle direction: continue owner
  copied-book hardening through narrow write-alpha maintenance hardening. The decision explicitly did
  not select owner DELETE execution, DELETE request packets, new owner mutations, release preparation,
  broad feature work, default write changes, or APP_ENV gate weakening.
- Phase 305 completed the Cycle 2 analyst gate and selected option B: write-alpha maintenance hardening.
  Phase 306 must implement exactly one narrow non-mutating maintenance-hardening outcome around existing
  safety/runbook/test boundaries; owner DELETE execution/packets, new owner mutations, release
  preparation, default write changes, and APP_ENV gate weakening remain out of scope.
- Phase 306 added `docs/write-alpha/default-disabled-reset-checklist.md` and linked it from the owner
  next-steps guide. This non-mutating maintenance-hardening doc consolidates reset/default-disabled
  verification after separately authorized synthetic/disposable or copied/restorable write-alpha
  investigations without changing code, requesting mutations, preparing DELETE, or altering gates.

## Current baseline

- Phases 481–530 completed the public-readonly/owner-writebeta run. PR #40 was verified MERGED. PM selected dual-track with v0.5 first where safe, authorized `v0.5.0-public-readonly-beta` as a conservative GitHub pre-release, and kept `v0.4.0-owner-writebeta` deferred. No real working-book trial was authorized. Mutation counts in this run: CREATE 0, PATCH 0, DELETE 0. Final checks passed: backend pytest (590), frontend check/auth-routes/build, Docker Compose config, public-status guard, diff hygiene, and tracked hygiene review. `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` write gating was not weakened.


Completed through Phase 530.

Current public release state:

- `v0.1.7-readonly` is the current public read-only pre-alpha GitHub pre-release after Phase 171
  publication, prepared/published only after Val authorization and final release-gate checks.
- `v0.2.8-writealpha` is the current public experimental write-alpha GitHub pre-release after Phase
  261 publication, Phase 262 current-state analyst gate, Phase 263 owner dry-run-only entrypoint
  cleanup, Phase 264 evidence-redaction hardening, Phase 265 abort guidance, and Phase 266 public
  status guard refresh. It is pre-alpha, disabled by default, `APP_ENV=test` gated when explicitly
  enabled, based on synthetic/disposable Cycle 3 copied-book package plus Phase 263 synthetic
  dry-run-only entrypoint evidence plus Phase 267 fresh-clone synthetic rehearsal evidence; Phase 268
  says the owner may be asked for dry-run only, Phase 269 provides the request packet, Phase 271
  accepted owner copied-book dry-run evidence as dry-run-only evidence, Phase 272 prepared a no-mutation
  CREATE-one readiness plan, Phase 273 passed synthetic/disposable CREATE-one rehearsal, Phase 274 kept
  owner copied-book CREATE blocked pending compatibility closure, and Phase 275 prepared the owner
  CREATE-one request packet after a synthetic/disposable `gnucash-cli` compatibility pass. Phase 276 then
  accepted exactly one owner copied-book CREATE-one evidence run with backup/read-back/audit/lock/
  compatibility/restore/reset evidence. Phase 277 found no concrete CREATE-one bug to fix, and Phase
  278 refreshed the copied-book write-alpha posture. Phase 279 invoked PM and recorded a no-release verdict. Phase 280 closed Cycle 2 and recommended Phase 281 analyst PATCH-readiness review only; Phases 281–292 prepared and then blocked owner PATCH before mutation; Phase 293 blocked a fresh CREATE-to-PATCH chain before mutation pending exact same-context owner confirmation. Owner PATCH/DELETE remain not accepted/run. It is not
  production-ready, not stable, not security-audited, not public-internet safe, and not safe for
  real/private or only-copy books.
- `v0.2.7-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 251 publication. It is pre-alpha, disabled by default, `APP_ENV=test` gated
  when explicitly enabled, based on synthetic/disposable Cycle 2 ownership-guard evidence only, not
  production-ready, not stable, not security-audited, not public-internet safe, and not safe for
  real/private or only-copy books.
- `v0.2.6-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 241 publication. It is pre-alpha, disabled by default, `APP_ENV=test` gated
  when explicitly enabled, based on synthetic/disposable no-mutation Cycle 1 evidence and
  operator-safety tooling only, not production-ready, not stable, not security-audited, not
  public-internet safe, and not safe for real/private or only-copy books.
- `v0.2.5-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 231 publication. It is pre-alpha, disabled by default, `APP_ENV=test`
  gated when explicitly enabled, based on synthetic/disposable and copied-test-book evidence only,
  not production-ready, not stable, not security-audited, not public-internet safe, and not safe for
  real/private or only-copy books.
- Phase 232 reconciled the public repository status after the Phase 231 publication:
  README/README.ru/PROJECT_STATUS/CHANGELOG/docs/ROADMAP and the public-status guard now agree that
  `v0.2.5-writealpha` is published while preserving default-disabled, `APP_ENV=test`-gated,
  synthetic/disposable or copied-test-book-only evidence boundaries.
- Phase 233 reformatted README, README.ru, CHANGELOG, and PROJECT_STATUS raw markdown source for
  terminal/editor readability while preserving links, content, safety warnings, and the current
  no-production/no-security/no-real-private-book-write-safety posture.
- Phase 234 added `docs/write-alpha/copied-book-dogfood-runbook.md`, a conservative maintainer
  runbook for future local-only copied/disposable write-alpha dogfood. It requires outside-git copied
  books, independent backups before mutation, explicit `GNUCASH_WRITES_ENABLED=true` plus
  `APP_ENV=test`, one mutation at a time, stop conditions, redacted evidence, restore verification,
  and reset back to default false; no real/private copied-book dogfood was run.
- Phase 235 added `scripts/write_alpha_preflight.py`, a local-only redacted target preflight CLI for
  future copied/disposable write-alpha dogfood. It requires an explicit existing readable target
  outside the git working tree, validates that backups are outside git or ignored, blocks unsafe
  write-alpha environment values unless `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`, warns on
  original/production-looking names without printing raw paths, and performs no opening, copying, or
  mutation.
- Phase 236 added `docs/write-alpha/dogfood-evidence-schema.md` and
  `scripts/redact_dogfood_evidence.py` to standardize future dogfood evidence fields and reject or
  redact path-like values, amount-like values, memo/account-name fields, and payload-like values. No
  copied/private book was used and no dogfood mutation was run.
- Phase 237 added `.env.writealpha.example` as an explicitly unsafe-for-real-books operator reference
  and `docs/write-alpha/environment.md` for local-only write-alpha environment guidance. The guidance
  says not to copy the template blindly to `.env`, requires both `GNUCASH_WRITES_ENABLED=true` and
  `APP_ENV=test` for explicit write-alpha testing, allows only synthetic/disposable/copied-test
  books, forbids public exposure and original/only-copy books, and keeps `.env.example` plus Docker
  Compose defaults read-only.
- Phase 238 added `scripts/write_alpha_readiness.py` and `app.write_alpha_readiness`, a redacted
  non-mutating readiness inspection path for operator preflight. It reports writes-enabled flag,
  `APP_ENV=test` gate status, derived backup policy, app metadata DB reachability, default book
  read-only openability/readability, and explicit `mutation_performed=false`; it works while writes
  are disabled, exposes no raw private paths, and does not construct `GnuCashWriteService`.
- Phase 239 recorded `docs/dogfood/phase-239-write-alpha-dry-run.md`, a synthetic copied-book
  no-mutation dry-run through Docker/Caddy. The phase used a disposable fixture copy, ran redacted
  preflight/readiness, confirmed default-disabled Docker/Caddy API and browser smoke with disabled
  validate/create/PATCH/DELETE 403 probes, verified the runtime book checksum was unchanged, and
  observed zero backup/lock/audit-row artifacts. No write-alpha mutation, release, real/private book,
  raw financial data, or default/gate change was added.
- Phase 240 prepared `docs/release/v0.2.6-writealpha-notes.md`,
  `docs/release/v0.2.6-writealpha-checklist.md`, and
  `docs/release/v0.2.6-writealpha-final-gate.md` as release-candidate-only artifacts for a possible
  later write-alpha maintenance pre-release. The rationale was that Phases 232–239 produced
  meaningful operator-safety tooling and synthetic no-mutation Docker/Caddy evidence, not merely
  internal churn. No tag, GitHub release, package, write default change, `APP_ENV=test` gate
  weakening, real/private-book write-safety claim, production/security claim, or publication
  authorization was added in Phase 240.
- Phase 241 called PM, received `AUTHORIZE_RELEASE`, reran the final release gate, updated
  `docs/release/v0.2.6-writealpha-notes.md`, checklist, final-gate, publication evidence, public
  status docs, and public-status guard, waited for exact release/status commit CI, and published
  `v0.2.6-writealpha` as a conservative GitHub pre-release. Publication created only an annotated
  tag and GitHub pre-release; no package, image, production deployment, write default change,
  `APP_ENV=test` gate weakening, real/private-book write-safety claim, production/security claim, or
  private data artifact was added.
- Phase 242 passed the Cycle 2 analyst gate in `docs/audits/phase-242-cycle-2-gate.md`; no blocking
  release/safety/private-data/write-mode issue was found, and Cycle 2 ownership-boundary work was
  allowed to start.
- Phase 243 added `docs/write-alpha/transaction-ownership.md` and an app metadata-only
  `write_alpha_transaction_ownership` model. Successful write-alpha CREATE now records safe ownership
  metadata linking `book_id`, `transaction_id`, `created_by_user_id`, `created_by_write_alpha`,
  `created_at`, and `last_mutated_at` for later PATCH/DELETE guards. The marker is stored only in the
  app metadata DB, existing audit logs remain compatible, and no GnuCash-book metadata write,
  amount/account mutation expansion, write default change, `APP_ENV=test` gate weakening,
  release/tag, real/private-book use, or real/private/only-copy write-safety claim was added.
- Phase 244 added the backend PATCH ownership guard. After the existing write-enabled, edit-access,
  and `APP_ENV=test` gates pass, PATCH now requires a same-book
  `write_alpha_transaction_ownership` row with `created_by_write_alpha=true` before constructing the
  GnuCash write service. Non-owned historical/imported/manual fixture transactions return 403 without
  backup, lock, audit row, or GnuCash mutation; write-alpha-created synthetic transactions still pass
  the existing description/date/split-memo-only PATCH flow and refresh `last_mutated_at`. Viewer access
  and default-disabled writes remain blocked before ownership checks. No amount/account mutation
  expansion, DELETE ownership guard, release/tag, real/private-book use, or real/private/only-copy
  write-safety claim was added.
- Phase 245 added the backend DELETE ownership guard. After the existing write-enabled, edit-access,
  and `APP_ENV=test` gates pass, DELETE now requires a same-book
  `write_alpha_transaction_ownership` row with `created_by_write_alpha=true` before constructing the
  GnuCash write service. Non-owned historical/imported/manual fixture transactions return 403 without
  backup, lock, audit row, or GnuCash mutation; write-alpha-created synthetic transactions can still
  be deleted through the existing lock → backup → piecash delete → audit → unlock flow, and successful
  allowed DELETE refreshes `last_mutated_at` in app metadata. Viewer access and default-disabled writes
  remain blocked before ownership checks. No broad delete support, undo feature, release/tag,
  real/private-book use, or real/private/only-copy write-safety claim was added.
- Phase 246 aligned the frontend transaction detail page with the Phase 244/245 backend ownership
  guards. The transaction detail API now exposes a safe app-metadata-only `is_write_alpha_owned` hint;
  the UI shows experimental delete controls only when write mode is explicitly enabled, an active book
  is present, and the transaction is write-alpha-owned. Non-owned historical/manual transactions show
  explanatory read-only copy instead of edit/delete controls. Backend PATCH/DELETE ownership guards
  remain authoritative, and no write default change, `APP_ENV=test` gate weakening, broad editor,
  release/tag, real/private-book use, or real/private/only-copy write-safety claim was added.
- Phase 247 recorded `docs/dogfood/phase-247-ownership-route-family.md`, a synthetic/disposable
  Docker/Caddy ownership route-family dogfood pass. One write-alpha-owned synthetic transaction was
  created, PATCHed, and DELETEd; one non-owned fixture transaction rejected PATCH and DELETE with 403
  without backup growth; backup/audit evidence showed one allowed create, one allowed PATCH, and one
  allowed DELETE; lock evidence was stale-released/not active; DELETE restore read-back passed after
  restoring the disposable runtime copy; and the reset default-disabled API smoke verified disabled
  validate/create/PATCH/DELETE probes still return 403. No real/private/only-copy book, raw
  path/account/memo/amount/payload evidence, release/tag, default write change, `APP_ENV=test` gate
  weakening, or real/private-book write-safety claim was added.
- Phase 248 extended the read-only write-alpha audit summary endpoint and operator UI with safe
  ownership evidence. The API now returns an `ownership_summary` containing the app-metadata
  write-alpha-created transaction marker count, the non-owned mutation rejection count visible in the
  filtered redacted audit rows, and the last successful mutation type. The UI renders only those
  bounded counters/action labels plus existing safe transaction prefixes, opaque backup refs, and
  safe errors. Viewer/outsider access remains blocked, raw audit payloads/amounts/memos/account
  names/paths are not rendered, and no write default change, `APP_ENV=test` gate weakening,
  release/tag, real/private-book use, or real/private/only-copy write-safety claim was added.
- Phase 249 documented the write-alpha ownership boundary and operator warnings in
  `docs/write-alpha/transaction-ownership.md`, `docs/write-alpha/copied-book-dogfood-runbook.md`,
  `docs/write-alpha/environment.md`, and the redacted dogfood evidence schema. The docs now state
  that CREATE creates app-metadata write-alpha-owned transactions, PATCH/DELETE are limited to those
  write-alpha-owned transactions for the same app metadata book, and historical/imported/manual
  GnuCash transactions remain read-only in this app. The warnings also state that ownership guards do
  not make real/private, original, production, shared, or only-copy books safe for write-alpha. No
  release, product-code change, write default change, `APP_ENV=test` gate weakening, or
  production/safety overclaim was added.
- Phase 250 prepared `docs/release/v0.2.7-writealpha-notes.md`,
  `docs/release/v0.2.7-writealpha-checklist.md`, and
  `docs/release/v0.2.7-writealpha-final-gate.md` as release-candidate-only artifacts for a possible
  later write-alpha maintenance pre-release. The release-candidate decision is justified by the
  implemented backend PATCH/DELETE ownership guards, the Phase 247 synthetic/disposable ownership
  route-family dogfood pass, and synchronized Phase 249 ownership-boundary operator docs. No PM was
  called, no tag/GitHub release/package/image was published, and no write default change,
  `APP_ENV=test` gate weakening, real/private-book use, production/security/public-internet/broad
  compatibility claim, or real/private/only-copy write-safety claim was added.
- Phase 251 called PM for the Cycle 2 release/no-release gate, received `AUTHORIZE_RELEASE`, reran
  the final local release gate, updated `docs/release/v0.2.7-writealpha-notes.md`, checklist,
  final-gate, publication evidence, public status docs, and public-status guard, waited for exact
  release/status commit CI, and published `v0.2.7-writealpha` as a conservative GitHub pre-release.
  Publication created only an annotated tag and GitHub pre-release; no package, image, production
  deployment, write default change, `APP_ENV=test` gate weakening, real/private-book write-safety
  claim, production/security claim, or private data artifact was added.
- Phase 252 passed the Cycle 3 analyst gate in `docs/audits/phase-252-cycle-3-gate.md`. The audit
  allowed maintainer copied-book dogfood package work to start and did not authorize real/private,
  original, only-copy book writes, release publication, write default changes, `APP_ENV=test` gate
  weakening, or production/security/write-safety claims.
- Phase 253 added `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`, a complete
  owner/maintainer procedure for future copied-book dogfood. The packet defaults to dry-run first,
  forbids original and only-copy books, requires outside-git copied/restorable targets with
  independent backups, limits optional mutation to one CREATE first, defers PATCH to later explicit
  review, prohibits DELETE unless separately authorized for a write-alpha-created test transaction,
  requires redacted evidence and restore proof, and ends with cleanup plus reset to
  `GNUCASH_WRITES_ENABLED=false`. No dogfood run, mutation, release/tag, default-write change,
  `APP_ENV=test` gate weakening, private-book use, or real/private/only-copy write-safety claim was
  added.
- Phase 254 added `scripts/write_alpha_copied_book_dogfood.py`, a local-only explicit-step wrapper
  for future copied-book dogfood. The wrapper supports separate `--dry-run` and `--create-one` modes,
  requires copied/disposable/original-untouched/outside-git confirmations, requires an extra explicit
  mutation confirmation for `--create-one`, calls the Phase 235 redacted preflight, creates a
  pre-step backup before dry-run/create-one, delegates the actual CREATE to a caller-supplied or
  default local smoke command, writes redacted JSON evidence, rejects unsafe paths, and verifies the
  committed/default `GNUCASH_WRITES_ENABLED=false` posture after each run. Script tests cover dry-run,
  create-one command delegation, missing mutation confirmation, unsafe inside-repo targets, and
  unsafe write-alpha environment values; synthetic local wrapper dogfood passed for dry-run and
  create-one with a harmless delegated command. No real/private/only-copy book, raw path/account/memo/
  amount evidence, DELETE mode, release/tag, default-write change, `APP_ENV=test` gate weakening, or
  real/private/only-copy write-safety claim was added.
- Phase 255 strengthened the transaction create/write-alpha UI warnings for future maintainer
  copied-book create-only dogfood. The shared warning component now includes explicit create-only
  dogfood copy; EN/RU release-critical strings require an outside-git copied/restorable test book with
  the original untouched, dry-run first unless explicitly continuing, at most one CREATE test
  transaction, independent backup plus restore plan, audit/app-backup/lock-release evidence, and no
  production use. The transaction create help, acknowledgement, browser confirmation, and safe server
  acknowledgement error were aligned, with frontend static route checks pinning the warning keys and
  copy. Backend gates remain authoritative. No new write capability, write-default change,
  `APP_ENV=test` gate weakening, mutation run, release/tag, real/private-book use, or
  real/private/only-copy write-safety claim was added.
- Phase 256 added `scripts/write_alpha_compatibility_check.py` and
  `docs/write-alpha/compatibility-check-harness.md`, a local-only best-effort compatibility harness
  for post-mutation copied/disposable dogfood. The harness opens the target read-only with piecash,
  optionally runs an already-available `gnucash-cli --report show --name "Balance Sheet"` probe,
  writes redacted JSON evidence with `pass`/`blocked`/`fail` semantics, and records missing Desktop/CLI
  tooling as a blocker rather than compatibility evidence. The maintainer packet now places this check
  between CREATE/PATCH/DELETE mutation evidence and restore verification. No GnuCash Desktop install,
  mutation, release/tag, default-write change, `APP_ENV=test` gate weakening, raw path/account/memo/
  amount evidence, broad Desktop/version compatibility claim, or real/private/only-copy write-safety
  claim was added.
- Phase 257 added `scripts/write_alpha_restore_verify.py` and
  `docs/write-alpha/restore-verification-harness.md`, a local-only restore verification harness for
  copied/disposable write-alpha dogfood. The harness requires explicit copied/disposable,
  original-untouched, restore-over-copy, and pre-mutation-backup confirmations; rejects target and
  backup files inside the git checkout; restores only the copied working book from the pre-mutation
  backup; verifies backup/restored checksum equality and optional expected full sha256; opens the
  restored copy read-only with piecash; optionally runs a read-only web/API probe command with output
  redacted; validates redacted evidence before writing; and checks the committed/default
  `GNUCASH_WRITES_ENABLED=false` posture. No mutation expansion, production disaster-recovery claim,
  release/tag, default-write change, `APP_ENV=test` gate weakening, raw path/account/memo/amount/API
  payload evidence, or real/private/only-copy write-safety claim was added.
- Phase 258 recorded `docs/dogfood/phase-258-synthetic-copied-book-package.md`, a synthetic/
  disposable full copied-book package rehearsal before any owner copied-book attempt. The dry-run
  wrapper passed, Docker/Caddy create-one passed with create smoke read-back, one routed CREATE,
  backup/audit/lock evidence, restore verification passed with checksum match and piecash read-back,
  a temporary Debian GnuCash CLI report probe passed, and the runtime reset to
  `GNUCASH_WRITES_ENABLED=false` with validate/create/PATCH/DELETE disabled-write 403 probes through
  Caddy. The host compatibility harness still records missing host `gnucash-cli` as blocked rather
  than broad compatibility evidence. No owner/private/original/only-copy book, release/tag, default
  write change, `APP_ENV=test` gate weakening, raw private evidence, production/security/public-
  internet/broad compatibility claim, or real/private/only-copy write-safety claim was added.
- Phase 259 recorded `docs/audits/phase-259-owner-copied-book-decision.md`, an owner copied-book
  decision gate. Verdict: ready to ask the owner for local copied-book dry-run only, with an
  outside-git copied/restorable book and the original untouched. It is not ready to ask for CREATE-one
  as the first owner action; CREATE-one can be considered only after owner dry-run evidence is reviewed
  and confirms preflight, independent backup, redaction, local-only runtime, restore plan, and reset
  to `GNUCASH_WRITES_ENABLED=false`. No owner dogfood was executed, no private paths/data were
  requested, no release/tag was published, and no real/private/only-copy write-safety claim was added.
- Phase 260 prepared `docs/release/v0.2.8-writealpha-notes.md`,
  `docs/release/v0.2.8-writealpha-checklist.md`, and
  `docs/release/v0.2.8-writealpha-final-gate.md` as unpublished release-candidate artifacts because
  the Cycle 3 maintainer copied-book package is strong enough for a conservative candidate: wrapper
  dry-run/create-one evidence, restore verification, bounded compatibility harnesses, synthetic
  end-to-end package rehearsal, and the dry-run-only owner decision gate are all documented. Owner
  copied-book dogfood may still be pending, CREATE-one is not the immediate owner ask, and no
  release/tag, write default change, `APP_ENV=test` gate weakening, owner/private/original/only-copy
  book use, production/security/public-internet/broad-compatibility claim, or real/private/only-copy
  write-safety claim was added.
- Phase 261 called PM for the Cycle 3 release/no-release gate, received `AUTHORIZE_RELEASE`, reran
  the full local release gate, checked local/remote tag and GitHub release absence, waited for exact
  release/status commit CI, and published `v0.2.8-writealpha` as a conservative GitHub pre-release.
  Publication created only an annotated git tag and GitHub pre-release; no package, image, production
  deployment, write default change, `APP_ENV=test` gate weakening, owner/private/original/only-copy
  book use, production/security/public-internet/broad compatibility claim, or real/private/only-copy
  write-safety claim was added. The final next owner action is copied-book dry-run only; CREATE-one
  can be considered only after owner dry-run evidence review.

- Phase 263 added `scripts/write_alpha_owner_dry_run.py` and
  `docs/write-alpha/owner-dry-run-quickstart.md` as the single owner-facing copied-book dry-run-only
  path. The command has no CREATE/PATCH/DELETE mode, delegates only to the no-mutation wrapper path,
  validates `mutation_requested=false`, `mutation_performed=false`, and
  `create_command_status=not-run`, and writes redacted evidence only. Targeted tests passed, a
  synthetic outside-git fixture dry-run passed, and
  `docs/dogfood/phase-263-owner-dry-run-synthetic-evidence.json` passed redaction validation. No
  owner/private/original/only-copy book was used, no release/tag was published, `GNUCASH_WRITES_ENABLED=false`
  remains default, the `APP_ENV=test` gate remains intact, and no real/private/only-copy write-safety
  claim was added.


- Phase 264 hardened owner dry-run evidence schema acceptance tests and nested payload redaction. The
  redaction helper now rejects or redacts strings and numeric values below sensitive container keys such
  as `payload`/`splits`, preventing free-form request/response payload data from bypassing the schema
  through neutral child key names. Tests cover private path-like, amount-like, memo-like, account-name-like,
  and nested payload-like failure cases while preserving useful bounded evidence fields. No mutation,
  release/tag, owner/private/original/only-copy book use, write default change, `APP_ENV=test` gate
  weakening, or real/private/only-copy write-safety claim was added.


- Phase 265 added owner dry-run troubleshooting and abort guidance to
  `docs/write-alpha/owner-dry-run-quickstart.md` and linked it from the maintainer copied-book packet.
  The guidance covers missing copied books, unsafe/original/only-copy paths, backup preflight failures,
  missing `APP_ENV=test`, unsafe write defaults, Docker/config/auth/health failures, redaction failures,
  missing no-mutation proof, and disabled-write endpoint success, always recommending stop/review
  rather than weakening gates or proceeding to CREATE. No mutation, release/tag, owner/private/
  original/only-copy book use, write default change, `APP_ENV=test` gate weakening, or real/private/
  only-copy write-safety claim was added.

- `v0.2.4-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 211 publication. It is pre-alpha, disabled by default, `APP_ENV=test`
  gated when explicitly enabled, based on synthetic/disposable evidence only for that cycle, not
  production-ready, not security-audited, and not safe for real/private or only-copy books.
- `v0.2.3-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 201 publication. It is pre-alpha, disabled by default, `APP_ENV=test`
  gated when explicitly enabled, based on synthetic/disposable evidence only for that cycle, not
  production-ready, not security-audited, and not safe for real/private or only-copy books.
- `v0.2.2-writealpha` remains available as an earlier public experimental write-alpha GitHub
  pre-release after Phase 191 publication. It is pre-alpha, disabled by default, `APP_ENV=test`
  gated when explicitly enabled, based on synthetic/disposable evidence only for that cycle, not
  production-ready, not security-audited, and not safe for real/private or only-copy books.
- `v0.2.1-writealpha` remains available as the previous public experimental write-alpha GitHub
  pre-release after Phase 182 publication, prepared in Phase 181 and published only after explicit
  Val authorization, a fresh green pre-publish gate, tag/release absence checks, green GitHub
  Actions on the exact release commit, rendered `GNUCASH_WRITES_ENABLED=false`, and sensitive
  tracked-file hygiene. It is pre-alpha, disabled by default, `APP_ENV=test` gated when explicitly
  enabled, not production-ready, not security-audited, and not safe for real/private or only-copy
  books.
- `v0.1.6-readonly` remains available as the previous public read-only pre-alpha GitHub pre-release,
  published in Phase 161 after Val authorization and final release-gate checks.
- `v0.1.5-readonly` remains available as an earlier public read-only pre-alpha GitHub pre-release,
  published in Phase 152 after Val authorization and final release-gate checks.
- Previous public read-only pre-release `v0.1.3-readonly` remains available and was published in
  Phase 125 after Val authorization and cleanup of the temporary live personal-book deployment.
- Local/GitHub tag `v0.1.3-readonly` is created by Phase 125 on the release-doc/status commit and
  published as a GitHub pre-release from `docs/release/v0.1.3-readonly-notes.md`.
- The release scope includes the Phase 118–121 live-stand read-only fixes, Phase 122 release gate,
  and the disabled-by-default/test-fixture-only write-alpha safety hardening from Phases 123–124
  without any production write-mode claim.
- Phase 126 is a released `v0.2.0-writealpha` read-only polish/triage phase: transaction query
  search now also checks transaction notes when piecash exposes them; GitHub #11/#12 were resolved
  or de-scoped without changing write routes.
- Phase 127 is a released `v0.2.0-writealpha` compatibility-evidence refresh for GitHub #22: local
  `gnucash`/`gnucash-cli` Desktop tooling is still unavailable, so docs record a safe blocker/manual
  procedure instead of claiming Desktop-generated fixture evidence; regression coverage pins the
  missing-tooling behavior.
- Phase 128 is a released `v0.2.0-writealpha` write-alpha concurrency/error-path safety expansion
  for create only: copied/disposable fixture tests now prove two parallel create POSTs produce one
  success and one lock-contention failure, synthetic post-backup write failure releases the lock,
  records failed audit with intact backup, and leaves the book unmutated, and read-only/viewer book
  access returns 403 before write-service construction. Writes remain disabled by default and
  limited to `APP_ENV=test` copied/disposable fixture scope when explicitly enabled.
- Phase 129 is a released `v0.2.0-writealpha` docs-only write-alpha recovery and maintainer-review
  gate: it adds a synthetic/disposable-scope recovery procedure for containment, backup selection,
  stale-lock cleanup, restore, integrity checks, and damaged-book triage, plus a maintainer
  checklist for default-disabled config, `APP_ENV=test` gating, disposable fixtures, lifecycle
  evidence, recovery docs, and sensitive-data hygiene. No product code changed, writes remain
  disabled by default, and no real-book write safety is claimed.
- Phase 130 is a released `v0.2.0-writealpha` write-alpha PATCH transaction hardening phase:
  experimental `PATCH /books/{book_id}/transactions/{transaction_id}` remains disabled by default
  and executable only with `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` against
  copied/disposable fixtures; backend hardening now returns 404 for missing transactions before
  lock/backup/mutation, preserves description/date/split-memo-only edits, records backup paths on
  failed post-backup PATCH audits, and adds disposable-fixture route tests for successful PATCH,
  validation failure, missing transaction, no backup leak, lock release, synthetic post-backup
  failure, intact backup, and concurrent PATCH+CREATE lock contention. No
  DELETE/import/recurring/account-write, tag, release, or real-book write claim was added.
- Phase 131 is a released `v0.2.0-writealpha` authorized write-alpha DELETE transaction phase:
  experimental `DELETE /books/{book_id}/transactions/{transaction_id}` remains disabled by default
  and executable only with `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` against
  copied/disposable fixtures; backend implementation performs missing-transaction validation before
  lock/backup/mutation, then lock → backup → piecash delete → audit → unlock, records failed audits
  with backup path when a post-backup delete failure occurs, verifies successful deletion removes
  the transaction and preserves the original in backup evidence, rejects read-only/viewer access
  before write-service construction, and covers concurrent DELETE+CREATE lock contention. The
  frontend transaction detail delete form is hidden unless write mode is explicitly enabled and
  requires acknowledgement plus browser confirmation. No import/recurring/account-write, tag,
  release, or real-book write safety claim was added; Phase 132 publication was later authorized and
  completed as `v0.2.0-writealpha` GitHub pre-release.
- Phase 132 is the published `v0.2.0-writealpha` release-gate artifacts phase: release notes,
  checklist, final-gate, README, CHANGELOG, PROJECT_STATUS, and handoff now record the write-alpha
  candidate as pre-alpha/experimental, disabled by default with `GNUCASH_WRITES_ENABLED=false`,
  executable only under the existing `APP_ENV=test` gate when explicitly enabled, based only on
  synthetic/disposable fixture evidence, not production-ready, not security-audited, not safe for
  real/private-book writes, and later published as a GitHub pre-release after explicit Val
  authorization and final checks. The publication added a tag/GitHub pre-release only; no
  package/upload, write default change, gate weakening, product-code change, or real/private data
  artifact was added.
- Phase 133 is a post-release read-only UX polish phase: `EmptyState.svelte` and `ErrorState.svelte`
  now expose accessible labels/actions and clearer edge-case copy, the global error page maps
  API/network/403/404/server failures to user-safe retry/back actions, and `/books`, `/scheduled`,
  `/transactions`, and `/accounts` now render informative empty states for no accessible books, no
  schedules, no transactions, no matching filters, and no accounts. Frontend route checks pin the
  empty/error-state behavior. No backend API, write endpoint, write-mode UI expansion, release
  publication, real-book artifact, export, screenshot, `.env`, app DB, backup, token, key, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 134 is a post-release read-only UX loading-state polish phase: `LoadingState.svelte` now
  provides structured skeleton variants for `/dashboard`, `/accounts`, `/transactions`, and
  `/books`; those pages show shape-matched skeleton placeholders during SvelteKit navigation/data
  reloads, including active-book switches, so users see stable read-only layouts while data for the
  selected accessible book loads. Frontend route checks pin the skeleton variants and navigation
  loading wiring. No backend API, write endpoint, write-mode UI expansion, release publication,
  real-book artifact, export, screenshot, `.env`, app DB, backup, token, key, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 135 is a post-release read-only mobile navigation polish phase: `DesktopNav.svelte` is
  hidden below the `md` breakpoint, `MobileNav.svelte` owns the small-screen shell with a
  touch-friendly open/close menu for book, locale, theme, and logout controls, primary mobile links
  and shared switchers now declare at least 44px touch targets, the app shell reserves enough bottom
  space for the fixed mobile navigation, and transaction detail splits use mobile cards instead of
  horizontal table scrolling at 320px widths. Frontend route checks pin the mobile/desktop
  breakpoint split, menu controls, touch-target classes, layout overflow guard, and transaction
  split mobile cards. No backend API, write endpoint, write-mode UI expansion, release publication,
  real-book artifact, export, screenshot, `.env`, app DB, backup, token, key, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 136 is a docs-only GnuCash compatibility matrix refresh: `docs/gnucash-compatibility.md` now
  makes the matrix evidence boundaries explicit, adds a dedicated GnuCash Desktop versions tested
  section, and states that no real Desktop release has been validated by the automated suite yet;
  `docs/gnucash-version-fixture-plan.md` now inventories all current synthetic/disposable fixture
  evidence and keeps future Desktop-generated fixture work gated on disposable provenance plus
  tests; `README.md` links to the compatibility matrix from current status and repeats the
  synthetic-only evidence warning. No fixture generation, Desktop-version testing, backend/frontend
  code, write-alpha expansion, release publication, real-book artifact, export, screenshot, `.env`,
  app DB, backup, token, key, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 137 is a docs-only local secure deployment hardening refresh:
  `docs/deployment/local-secure-deployment.md` now covers localhost, LAN, and VPN deployment-mode
  CORS recommendations, JWT secret generation and conservative rotation, app metadata DB
  backup/restore expectations, and a concrete self-hosting pre-deployment checklist; `.env.example`
  comments now point operators toward fresh JWT secrets and exact CORS origins for LAN/VPN. No
  backend/frontend product code, endpoint, write-alpha capability, release publication, real-book
  artifact, app DB, backup, `.env`, token, key, screenshot, export, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 138 is a docs-only public status synchronization phase after Phases 133–137: `README.md`,
  `README.ru.md`, `CHANGELOG.md`, and `docs/ROADMAP.md` now reflect the completed read-only UX
  polish, compatibility-documentation refresh, local deployment hardening guide, current release
  posture, synthetic/disposable evidence boundaries, and
  no-production/no-security-audit/no-real-book-write-safety limits. No backend/frontend product
  code, endpoint, write-alpha capability, release publication, real-book artifact, app DB, backup,
  `.env`, token, key, screenshot, export, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 139 is a synthetic/disposable Docker/Caddy dogfood refresh after Phases 133–138: local
  Docker Compose was run with `GNUCASH_WRITES_ENABLED=false`, the read-only API smoke passed for
  health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export,
  reports summary, and disabled validate/create/patch write probes, and the headless browser dogfood
  passed login, protected redirect, dashboard, accounts, books, scheduled, account detail,
  transaction filters, transaction detail, CSV export, hidden write UI, and no-artifact checks.
  Evidence is documented in `docs/dogfood/phase-139-synthetic-dogfood.md`. No backend/frontend
  product code, endpoint, write-alpha capability, release publication, real-book artifact, app DB,
  backup, `.env`, token, key, screenshot, export, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 140 is a maintenance release readiness audit for a possible `v0.1.4-readonly`: write-gating
  tests, frontend route checks, Docker Compose config validation, recent GitHub CI,
  disabled-by-default write config, tracked sensitive-file hygiene, and Phases 133–135
  documentation/test evidence were checked. Verdict: `not ready` because public release/status docs
  are not fully synchronized yet (`README.md` still says Phase 0–137 and `CHANGELOG.md` lacks Phase
  138/139 entries). No product code, write-alpha behavior, release, tag, package, real/private data,
  or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 141 prepared conservative `v0.1.4-readonly` release artifacts without publication:
  `docs/release/v0.1.4-readonly-notes.md`, `docs/release/v0.1.4-readonly-checklist.md`, and
  `docs/release/v0.1.4-readonly-final-gate.md` described the candidate as pre-alpha, read-only by
  default, unpublished, not production-ready, not security-audited, and pending explicit
  authorization before any tag/GitHub release. `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and
  `docs/handoff/phase-141.md` were synchronized. Verification passed for backend health/auth tests,
  frontend check, frontend auth-route checks, Docker Compose config validation, tag/release absence,
  diff whitespace, and tracked-file sensitive hygiene. No product code, write-alpha behavior,
  release, tag, package, real/private data, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 142 published `v0.1.4-readonly` as an authorized GitHub pre-release after final release-gate
  checks. The phase re-confirmed clean `main`, `HEAD == origin/main`, release artifacts present,
  tag/release absence before publication, GitHub CI success, Docker Compose config validity,
  disabled-write tests, frontend checks, `GNUCASH_WRITES_ENABLED=false` default, diff whitespace,
  and sensitive tracked-file hygiene. Publication created only the annotated git tag and GitHub
  pre-release; docs/status/handoff/publication evidence were synchronized. No product code,
  write-alpha expansion, runtime default change, package, binary artifact, Docker image, production
  deployment, real/private data, or production-readiness claim was added.
- Phase 143 is a post-`v0.1.4-readonly` read-only runtime status banner v2 phase: the app shell now
  passes the active accessible book into `ReadOnlyStatusBanner`, and the banner displays compact
  mobile-safe chips for read-only default status, current book name/fallback, and a safe `/books`
  review link. Localized safety copy now explicitly states `GNUCASH_WRITES_ENABLED=false` as the
  safe default, and frontend route/static checks pin active-book wiring, `/books` navigation, and no
  browser-storage persistence. No backend API, write endpoint, write-mode UI expansion,
  release/tag/package, localStorage-sensitive state, real/private book, screenshot, export, `.env`,
  app DB, backup, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 144 is a post-`v0.1.4-readonly` account tree discoverability and heavy-account UX polish
  phase: the accounts tree now provides a local accessible search filter over account name, full
  path, type, and currency; filtered results preserve matching descendants under their parent paths
  and show filtered/total counts so large read-only account trees can be narrowed without changing
  the book or calling backend write/API paths. Frontend route/static checks pin the filter behavior,
  count/status copy, parent-path preservation, and no browser-storage persistence. No backend API,
  write endpoint, write-mode UI expansion, release/tag/package, localStorage-sensitive state,
  real/private account names, screenshot, export, `.env`, app DB, backup, token, key, cert, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 145 is a post-`v0.1.4-readonly` transaction list usability and filter/export confidence
  phase: the transactions page now shows a localized current-view summary above the table with
  visible page range, newest-first date ordering, active-filter/no-filter status, explicit
  list/pagination/CSV filter parity, and the 10,000-row CSV export cap reminder.
  `docs/transactions-filters.md` documents the display-only URL-filter behavior, and frontend
  route/static checks pin the status summary plus localized cap/parity copy. Backend
  transaction/export regression tests still pass. No backend API, write endpoint, CSV export
  body/header behavior, write-mode UI expansion, release/tag/package, browser-storage persistence,
  raw CSV artifact, real/private transaction data, `.env`, app DB, backup, token, key, cert, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 146 is a post-`v0.1.4-readonly` transaction detail and split readability polish phase: the
  transaction detail page now uses a bounded responsive metadata layout for date/currency/split
  count/short ID, split rows expose read-only account, memo, short account ID, amount, and raw
  GnuCash reconciliation state as readable mobile cards and a fixed desktop table, and zero-split
  responses render a safe empty state instead of inventing balancing data. The API split DTO now
  includes read-only `reconcile_state` for detail visibility; backend regression coverage pins that
  value and frontend route/static checks pin no horizontal overflow and hidden-by-default write
  controls. No write endpoint, write-mode UI expansion, release/tag/package, browser-storage
  persistence, screenshot/export/raw financial artifact, real/private book data, `.env`, app DB,
  backup, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 147 is a post-`v0.1.4-readonly` dashboard/reporting limitation clarity phase: dashboard
  summary limitations now explicitly state `reporting_basis=base_currency_only`, no currency
  conversion, and base-currency-only account/split inclusion; mixed-currency books name detected
  excluded currencies instead of implying conversion, and unknown `XXX` base-currency/zero-total
  cases explain that zero may reflect no matching base-currency accounts rather than an empty book.
  The dashboard UI displays reporting basis and conversion status before rendering backend
  limitations, and backend/frontend tests pin the no-conversion wording. No FX conversion, external
  rates, production accounting guarantee, write endpoint, release/tag/package, browser-storage
  persistence, screenshot/export/raw financial artifact, real/private book data, `.env`, app DB,
  backup, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 148 is a post-`v0.1.4-readonly` books page self-hosting readiness slice: `/books` metadata
  now includes app-metadata-only operator guidance that states listing does not open GnuCash data
  and that upload/delete/default-changing/registry-edit actions are intentionally unsupported in
  MVP; the UI shows current vs default labels, read-only/access/storage/status metadata, safe
  read-only view links, and localized self-hosting guidance without rendering private `uri_or_path`
  values or raw backend guidance copy. Backend and frontend tests pin the
  metadata/read-only/no-management-action behavior. No book upload/delete/default-change/registry
  edit, write endpoint, release/tag/package, browser-storage persistence, screenshot/export/raw
  financial artifact, real/private book data, `.env`, app DB, backup, token, key, cert, or
  `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 149 is a post-`v0.1.4-readonly` Russian localization coverage slice for the new read-only UX
  from Phases 143–148: the existing English/Russian message catalog now covers account-tree
  filtering labels/statuses/empty states/loading copy, dashboard
  conservative/reporting-basis/currency-conversion labels, transaction detail/split readability
  labels/helper/empty states/reconciliation labels, and hidden-by-default write-alpha DELETE
  warnings. `docs/localization.md`, README/README.ru, CHANGELOG, static route checks, status, and
  handoff were synchronized. English remains canonical, Russian remains partial/opt-in, and no
  full-app localization rewrite, backend API localization, write expansion, release/tag/package,
  browser-storage persistence, screenshot/export/raw financial artifact, real/private data, `.env`,
  app DB, backup, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 150 is a post-`v0.1.4-readonly` synthetic Docker/browser dogfood refresh after the Phase
  143–149 read-only UX/localization work: local Docker Compose/Caddy was run against a
  synthetic/disposable fixture copied into ignored runtime data with `GNUCASH_WRITES_ENABLED=false`;
  read-only API smoke passed for health, login/auth, books/default book, accounts, transactions,
  transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes;
  headless browser dogfood passed login, protected redirect, dashboard, accounts, books, scheduled,
  account detail, transaction filters, transaction detail, CSV export, hidden write UI, and
  no-artifact checks. Evidence is documented in `docs/dogfood/phase-150-synthetic-dogfood.md`. No
  product code, write endpoint, write-mode UI expansion, release/tag/package, browser-storage
  persistence, screenshot/export/raw financial artifact, app DB, backup, real/private GnuCash book,
  `.env`, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 151 is a post-`v0.1.4-readonly` maintenance release readiness artifact phase for possible
  `v0.1.5-readonly`: `docs/release/v0.1.5-readonly-notes.md`,
  `docs/release/v0.1.5-readonly-checklist.md`, and `docs/release/v0.1.5-readonly-final-gate.md`
  summarized Phases 143–150, kept conservative pre-alpha/read-only/default-write-disabled safety
  language, and recorded the candidate as ready for a later authorized publish phase but still
  unpublished. README, CHANGELOG, PROJECT_STATUS, and `docs/handoff/phase-151.md` were synchronized.
  No product code, write endpoint, write-mode UI expansion, release/tag/package, browser-storage
  persistence, screenshot/export/raw financial artifact, app DB, backup, real/private GnuCash book,
  `.env`, token, key, cert, or `GNUCASH_WRITES_ENABLED=false` default changed.
- Phase 152 is the authorized publication phase for `v0.1.5-readonly`: the final gate was re-run
  from clean `main` at `a94a0a3`, local backend/frontend/Docker checks passed, rendered Compose
  config kept `GNUCASH_WRITES_ENABLED=false`, tracked sensitive-file hygiene passed, GitHub Actions
  for the release commit passed, and `v0.1.5-readonly` was published as an annotated tag and GitHub
  pre-release. README, CHANGELOG, release notes/checklist/final-gate, publication evidence,
  PROJECT_STATUS, and `docs/handoff/phase-152.md` were synchronized. No package, binary artifact,
  Docker image, production deployment, product code, write endpoint, write-mode UI expansion,
  runtime default change, browser-storage persistence, screenshot/export/raw financial artifact, app
  DB, backup, real/private GnuCash book, `.env`, token, key, cert, or
  production-readiness/security-audit claim was added.
- Phase 153 is a fresh-clone Docker install smoke phase after the `v0.1.5-readonly` publication:
  `scripts/smoke/fresh-clone-docker-smoke.sh` now provides a reproducible clean-checkout command
  path that clones the repo to a temporary directory, copies only the committed synthetic fixture
  into ignored runtime data, writes dummy local-only `.env` values with
  `GNUCASH_WRITES_ENABLED=false`, validates and starts Docker Compose on a non-conflicting local
  port, runs the existing API smoke and headless browser dogfood helpers, verifies hidden write UI
  and disabled validate/create/patch probes, checks for no new raw screenshot/export/backup
  artifacts, then tears down Docker and removes the temporary clone by default. Evidence is
  documented in `docs/dogfood/phase-153-fresh-clone-docker-smoke.md`. No product code,
  release/tag/package/image, production deployment hardening claim, public-internet exposure claim,
  write expansion, runtime default change, real/private book, committed `.env`, app DB, backup,
  screenshot, raw CSV export, token, key, cert, private path, or private financial data was added.
- Phase 154 is a GnuCash compatibility fixture path v5 blocker refresh for GitHub #22: the safe
  Desktop tooling probe now records phase-154 metadata, missing-command reasons,
  `desktop_generated_fixture_possible_now=false`, and optional non-mutating `apt-cache policy`
  package-candidate hints. Local evidence confirms `gnucash` and `gnucash-cli` are absent on `PATH`;
  package metadata shows a candidate but no package was installed, no book was opened, no private
  directories were searched, and no Desktop-generated synthetic SQLite fixture was produced.
  Compatibility docs and tests now make clear that package availability alone is not compatibility
  evidence; future Desktop rows require a disposable Desktop/CLI environment, a synthetic SQLite
  book, redacted metadata collection, and read-only service validation. No
  PostgreSQL/MySQL/MariaDB/XML support claim, broad all-version compatibility claim,
  release/tag/package, write behavior, real/private book, `.env`, app DB, backup, screenshot/export,
  token, key, cert, path, account name, description, memo, amount, or private data was added.
- Phase 155 is a multi-book read-only operator UX slice for GitHub #13: `/books` and backend book
  metadata now expose safe access/storage diagnostics for accessible configured books, including
  `available`, `missing_file`, `not_configured`, and `remote_or_unchecked` status, explicit
  `access_status`, private-path-redaction metadata, and safe operator next actions. Raw
  `uri_or_path` values are no longer returned by the book metadata API response, the listing still
  does not open GnuCash data, unauthorized/archived books remain hidden or blocked, and the UI
  continues to expose only safe read-only view links with no
  upload/delete/default-changing/registry-edit controls. No write behavior, release/tag/package,
  real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, account name,
  description, memo, amount, or private data was added.
- Phase 156 is a dashboard drilldown and reporting-evidence slice: dashboard summary, recent
  transactions, expenses-by-account, and cashflow sections now expose active-book-preserving
  read-only `/transactions` links built from existing URL filters (`date_from`, `date_to`,
  `account_id`, `limit=50`, `offset=0`), with copy that keeps dashboard totals base-currency-only
  and no-conversion. Frontend route checks pin URL construction, component wiring, no invented
  totals/recomputation copy, expense account filter links, and cashflow month date-range links;
  `docs/money-model.md` documents the drilldown limitations and CSV parity. No new accounting
  engine, FX conversion, forecasting, write route, browser filter persistence, release/tag/package,
  real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, or private
  financial data was added.
- Phase 157 is a scheduled/recurring transaction read-only clarity v2 slice: `/scheduled` now
  exposes URL-only display filters for enabled/disabled and template-reference metadata,
  deterministic safe sorting by start date/name/enabled-first, filtered-empty vs true-empty states,
  and stronger no-leak/no-browser-storage copy for template split amounts, accounts, memos,
  transaction descriptions, and raw SQL. Backend regression coverage pins deterministic ordering and
  DTO redaction of unsafe template/source attributes, while frontend route checks pin the filters,
  counts, clear-filter link, and no editor/persistence/fake-next-run behavior. No scheduled editor,
  next-run prediction, template split exposure, write path, browser persistence,
  release/tag/package, real/private book, `.env`, app DB, backup, screenshot/export, token, key,
  cert, or private financial data was added.
- Phase 158 is a transaction/account mobile dogfood fix pass: transaction/account CSV export actions
  and transaction empty-state recovery links now declare touch-friendly `inline-flex min-h-11`
  controls, and `scripts/smoke/read-only-browser-dogfood.py` defaults to a 320x720 mobile viewport
  with horizontal-overflow and CSV export touch-target assertions across dashboard, accounts, books,
  scheduled, account detail, transactions, and transaction detail. Synthetic Docker/Caddy browser
  dogfood passed at 320px width with `GNUCASH_WRITES_ENABLED=false`, hidden write UI, CSV export
  success, and no screenshot/download/export artifacts. No redesign, heavy UI library, write-mode
  expansion, release/tag/package, real/private book, `.env`, app DB, backup, screenshot/export,
  token, key, cert, private path, or private financial data was added.
- Phase 159 is a release-critical localization pass that routes additional web frontend user-facing
  copy through the typed English/Russian catalog: dashboard report cards, drilldown helper copy,
  recent transactions, expenses-by-account, cashflow widgets, `/scheduled` title/safety
  copy/URL-only filters/safe metadata labels/empty states, and landing-page sign-in copy now use
  `t(locale, key)` with simple named interpolation where needed. Frontend static checks and Svelte
  checks pin the localization surface. English remains canonical, Russian remains partial/opt-in,
  backend/API errors are not localized, and no write behavior, release/tag/package, browser-storage
  persistence, real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert,
  private path, or private financial data was added.
- Phase 160 is a full release-candidate synthetic/disposable Docker/Caddy dogfood pass after Phases
  153–159: local Compose ran with the committed synthetic fixture copied into ignored runtime data
  and `GNUCASH_WRITES_ENABLED=false`; API smoke passed for health, login/auth, books/default book,
  accounts, transactions, transaction detail, CSV export, reports summary, and disabled
  validate/create/patch probes; an additional DELETE write probe returned HTTP 403; headless browser
  dogfood at 320x720 passed login, protected redirect, dashboard, accounts, books, scheduled,
  account detail, transaction filters, transaction detail, CSV export, hidden write UI, no-overflow
  checks, and no-artifact checks. Evidence is documented in
  `docs/dogfood/phase-160-release-candidate-dogfood.md`. No copied-book dogfood was run because no
  explicit safe copied book path was provided. No release/tag/package/image, write expansion,
  real/private book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, or
  private financial data was added.
- Phase 161 is the authorized publication phase for `v0.1.6-readonly`: the final read-only
  maintenance release gate was re-run from clean `main` at `d56c335`, local backend/frontend/Docker
  checks passed, rendered Compose config kept `GNUCASH_WRITES_ENABLED=false`, tracked sensitive-file
  hygiene passed, GitHub Actions for the release commit passed, and `v0.1.6-readonly` was published
  as an annotated tag and GitHub pre-release. README, CHANGELOG, release notes/checklist/final-gate,
  publication evidence, PROJECT_STATUS, and `docs/handoff/phase-161.md` were synchronized. No
  package, binary artifact, Docker image, production deployment, product code, write endpoint,
  write-mode UI expansion, runtime default change, browser-storage persistence,
  screenshot/export/raw financial artifact, app DB, backup, real/private GnuCash book, `.env`,
  token, key, cert, or production-readiness/security-audit claim was added.
- Phase 162 is a post-`v0.1.6-readonly` baseline sync and tagged smoke phase: `docs/ROADMAP.md` no
  longer says the current baseline is Phase 137/138 or `v0.1.3-readonly`, and the published
  `v0.1.6-readonly` tag was verified from a fresh checkout with the committed synthetic fixture,
  dummy local-only `.env`, Docker Compose/Caddy, API smoke, browser dogfood,
  `GNUCASH_WRITES_ENABLED=false` in rendered/runtime config, disabled validate/create/patch/delete
  write probes, and no raw screenshot/export/backup artifacts. Evidence is documented in
  `docs/dogfood/phase-162-v0.1.6-tagged-smoke.md`. The smoke helper now covers DELETE disabled-write
  probes for old tagged checkouts and future API smokes. No product behavior, write capability,
  release/tag/package/image, production deployment, real/private GnuCash book, app DB, backup,
  committed `.env`, screenshot/export, token, key, cert, private path, account name, transaction
  description, memo, amount, or production/security claim was added.
- Phase 163 is a disposable GnuCash Desktop compatibility fixture path blocker phase for GitHub #22:
  `apps/api/scripts/probe_gnucash_desktop_disposable_container.py` now probes GnuCash Desktop/CLI
  tooling inside a temporary `debian:12-slim` Docker container instead of installing host packages;
  local evidence confirms Debian 12 can install GnuCash 4.13 tooling in isolation
  (`gnucash`/`gnucash-cli` available), but `gnucash-cli --help` exposes report/quote commands rather
  than a safe noninteractive create/save-as SQLite fixture path, so no Desktop-generated synthetic
  fixture was created and no Desktop-version compatibility row is claimed.
  `docs/gnucash-desktop-tooling-phase-163.md`, `docs/gnucash-compatibility.md`, and
  `docs/gnucash-version-fixture-plan.md` record the blocker and exact prerequisites for a future
  disposable GUI/manual or confirmed noninteractive creation path. No host package install, product
  behavior, write capability, release/tag/package/image, production deployment, real/private GnuCash
  book, app DB, backup, committed `.env`, screenshot/export, token, key, cert, private path, account
  name, transaction description, memo, amount, or broad
  all-version/PostgreSQL/MySQL/MariaDB/XML/Desktop support claim was added.
- Phase 164 is a book-context and access edge-case hardening phase for GitHub #13: the web app now
  classifies invalid, stale/no-longer-accessible, and no-accessible-book selected-book cookie
  states, safely replaces the non-secret `selected_book_id` cookie with an accessible fallback or
  clears it when none exists, and redirects protected read-only views to `/books?book_context=...`
  so users can review current/default labels before opening
  dashboard/accounts/transactions/scheduled views. `/books` shows a localized recovery notice, while
  backend access rules continue to hide archived books, block unauthorized books, omit raw
  `uri_or_path`, and report missing/not-configured book storage only through redacted metadata
  diagnostics. `docs/book-switcher-readonly-model.md` documents the selected-book cookie, fallback
  order, recovery behavior, and no-management/no-write boundaries. No
  upload/delete/default-changing/registry-edit UI, direct file browser, collaborative/family-wallet
  workflow, GnuCash write path, release/tag/package, localStorage/sessionStorage book-sensitive
  state, real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, private
  path, or private financial data was added.
- Phase 165 is a large account-tree usability/performance evidence phase: the synthetic benchmark
  helper can now generate wide/deep synthetic account hierarchies and record account hierarchy
  metadata, local benchmark evidence documents a 146-account synthetic hierarchy with successful
  read-only account-tree loads around 186–199 ms median in TestClient, and `AccountTreeNode.svelte`
  caps visual indentation for very deep hierarchies while preserving full-path hover text. Frontend
  static checks pin the overflow guard and browser-storage-free local filter contract. No cache
  layer, account editing, production scalability claim, release/tag/package, real/private account
  name/book, app DB, backup, `.env`, screenshot/export, token, key, cert, private path, or private
  financial data was added.
- Phase 166 is a synchronous read-only CSV export reliability and user-feedback hardening phase:
  backend regression tests now pin header-only empty filtered exports, account-scoped filtered
  export parity, and consistent advisory CSV metadata headers, while transaction and account-detail
  export controls show localized row-count, header-only empty-export, 10,000-row cap/truncation,
  string-amount, and no-currency-conversion guidance derived from existing read-only list/count
  metadata. `docs/transactions-filters.md` documents the UX behavior and account-scoped parity. No
  import, background export queue, cap change, raw CSV artifact, browser filter persistence, fake
  currency conversion, write behavior, release/tag/package, real/private book, app DB, backup,
  `.env`, screenshot/export, token, key, cert, private path, or private financial data was added;
  `GNUCASH_WRITES_ENABLED=false` remains the default.
- Phase 167 is a local/LAN auth/session hardening phase: SvelteKit now rejects unsafe state-changing
  app-route requests with a mismatched browser `Origin` header, while allowing safe methods and
  originless local probes; the web auth cookie lifetime now follows `JWT_TOKEN_EXPIRE_MINUTES` from
  Docker Compose with a 30-minute fallback instead of staying hard-coded; backend auth tests pin
  expired JWT rejection; and `docs/security/auth-cookie-deployment.md` documents the conservative
  pre-alpha cookie/session/same-origin model without claiming a production security audit. Auth
  tokens remain httpOnly cookies only, no auth localStorage/sessionStorage was added, placeholder
  JWT secrets remain rejected, wildcard CORS warnings remain documented for non-development LAN/VPN
  use, no OAuth/SSO/multi-user role expansion was added, and `GNUCASH_WRITES_ENABLED=false` remains
  the default.
- Phase 168 is a first-run and broken-configuration operator UX phase: `/health` now includes
  redacted auth-bootstrap diagnostics for placeholder/missing `JWT_SECRET` and missing
  `APP_ADMIN_PASSWORD_HASH`/`APP_ADMIN_PASSWORD`, default-book diagnostics distinguish unreadable
  files from missing mounts without exposing full paths, startup logs emit safe first-run
  configuration warnings, `/login` reports backend auth-configuration failures as operator-fixable
  setup problems, `/books` and the global error page point operators toward safe `.env`,
  book-volume, and `/health` checks, and `docs/operations/troubleshooting.md` documents the
  troubleshooting path. No setup wizard, config-writing UI, secret display, book upload/management,
  public-hosting hardening claim, production-readiness claim, real/private data artifact, `.env`,
  app DB, backup, token, key, cert, screenshot/export, or `GNUCASH_WRITES_ENABLED=false` default
  change was added.
- Phase 169 is a release-critical Russian localization completion slice: login
  validation/auth/service-configuration failures now use the existing English/Russian catalog via
  the `ui_locale` cookie, and the global error component/page localize 403, 404, generic
  API/network, and 5xx first-run operator guidance while preserving safe `/health`, local `.env`,
  book-volume, read-only, English-canonical, partial/opt-in localization wording. Existing CSV
  export states and book-context recovery notices remain catalog-backed. No backend API localization
  rewrite, marketing/full-translation claim, write behavior, release/tag/package, browser-storage
  persistence, real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert,
  private path, or `GNUCASH_WRITES_ENABLED=false` default change was added.
- Phase 170 is a full cycle 2 synthetic/disposable Docker/Caddy dogfood pass after Phases 162–169:
  local Compose ran with the committed synthetic fixture copied into ignored runtime data and
  `GNUCASH_WRITES_ENABLED=false`; `/api/health` confirmed the default book was present/readable and
  writes disabled; API smoke passed for health, login/auth, books/default book, accounts,
  transactions, transaction detail, CSV export, reports summary, and disabled
  validate/create/patch/delete write probes; headless browser dogfood passed at both 320x720 and
  1280x900 for login, protected redirect, dashboard, accounts, books, scheduled, account detail,
  transaction filters, transaction detail, CSV export, hidden write UI, auth-cookie no-readability,
  no-overflow checks, and no-artifact checks. Evidence is documented in
  `docs/dogfood/phase-170-cycle-2-release-candidate-dogfood.md`. No copied-book dogfood was run
  because no explicit safe copied book path was provided. No release/tag/package/image, write
  expansion, real/private book, app DB, backup, committed `.env`, screenshot/export, token, key,
  cert, private path, or production/security claim was added.
- Phase 171 is the authorized publication phase for `v0.1.7-readonly`: the final read-only
  maintenance release gate was re-run from clean `main` at `cec8e5e`, local backend/frontend/Docker
  checks passed, rendered Compose config kept `GNUCASH_WRITES_ENABLED=false`, tracked sensitive-file
  hygiene passed, starting-head and release-commit GitHub Actions passed, and `v0.1.7-readonly` was
  published as an annotated tag and GitHub pre-release from release commit
  `d248b5a355ed2b57913d0c408e643b5f6cfcfe5b`. README, CHANGELOG, release notes/checklist/final-gate,
  publication evidence, PROJECT_STATUS, and `docs/handoff/phase-171.md` were synchronized. No
  package, binary artifact, Docker image, production deployment, product code, write endpoint,
  write-mode UI expansion, runtime default change, browser-storage persistence,
  screenshot/export/raw financial artifact, app DB, backup, real/private GnuCash book, `.env`,
  token, key, cert, or production-readiness/security-audit claim was added.
- Phase 172 is a docs-only public status reconciliation after the published `v0.1.7-readonly` and
  `v0.2.0-writealpha` pre-releases: README, README.ru, CHANGELOG, PROJECT_STATUS, and
  `docs/release/v0.2.0-writealpha-*` now consistently state that Phase 0–172 are complete, the
  current public read-only release is `v0.1.7-readonly`, and `v0.2.0-writealpha` is already
  published as an experimental pre-release. Stale current-state wording that still looked like
  `v0.2.0-writealpha` was merely prepared/unpublished/not authorized was corrected while preserving
  the historical note that Phase 132 itself did not publish it. No product code, runtime config,
  Docker default, tag/release publication, package, real/private book, `.env`, app DB, backup,
  screenshot/export, token, key, cert, or write-safety claim changed; `GNUCASH_WRITES_ENABLED=false`
  remains default and write-alpha remains unsafe for real/private or only-copy books.
- Phase 173 is an executable-design phase for write-alpha copied-book dogfood:
  `docs/dogfood/write-alpha-copied-book-runbook.md` defines the local-only command path, hard stop
  conditions, external copied/disposable provenance, ignored runtime copy under `data/books/`,
  `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true`, backup/restore
  expectations, one minimal create transaction shape, GnuCash Desktop verification,
  teardown/no-artifact checks, and redacted evidence template.
  `apps/api/scripts/check_dogfood_book_candidate.py` now has a `--write-alpha-plan` preflight
  interface backed by tests; it validates only path classes and acknowledgement, never
  opens/parses/copies/writes a book, and emits no absolute private paths/account names/amounts. No
  write dogfood was run, no real/private/only-copy book was used, no write default changed, no
  release/tag/package was published, and no runtime book/app DB/backup artifact was committed.
- Phase 174 is a write-alpha copied-book preflight harness phase:
  `apps/api/app/dogfood_preflight.py` and `apps/api/scripts/check_dogfood_book_candidate.py` now
  provide a stricter dry-run preflight that fails closed for missing source files, missing
  disposable-copy acknowledgement, repo-contained sources, `.env`/app DB/backup-like sources,
  runtime targets outside ignored `data/books/`, backup targets outside ignored `data/backups/`, or
  non-ignored runtime/backup artifacts. Ready output is redacted to file class, path classes, byte
  size, short checksum, and dry-run status; tests and
  `docs/dogfood/phase-174-write-alpha-preflight.md` document synthetic pass/fail evidence. No write
  mutation was run, no real/private/only-copy book was used, no product runtime behavior/default
  changed, and no runtime book/app DB/backup artifact was committed.
- Phase 175 is a write-alpha controlled create dogfood phase: a committed synthetic fixture was
  copied to a temporary external disposable source, passed the Phase 174 redacted preflight, then
  was copied into ignored `data/books/` runtime storage and exercised once with `APP_ENV=test` plus
  explicit local-only `GNUCASH_WRITES_ENABLED=true`. Exactly one balanced two-split create succeeded
  through the existing write-alpha API route; API read-back passed; validation rejected unbalanced
  and invalid/placeholder-style probes; one backup and one successful `transaction.create` audit row
  were observed; a flock probe confirmed the write lock was released; and a restored read-only smoke
  passed with default disabled writes. Runtime book/app DB/backups/locks were removed after the run,
  no PATCH/DELETE dogfood or release publication occurred, and no raw financial data/book/backup
  artifact was committed.
- Phase 176 is a GnuCash Desktop/tooling verification phase for the write-alpha disposable path: a
  committed synthetic fixture was copied to a temporary external disposable source, passed the Phase
  174 redacted preflight, mutated exactly once through the existing write-alpha create route under
  `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true`, then copied to `/tmp` and
  opened by GnuCash CLI 4.13 inside a temporary `debian:12-slim` Docker container via `gnucash-cli
  --report show --name "Balance Sheet"`. The command exited `0` with bounded report metadata only,
  and a read-only API smoke after the CLI check passed with default disabled writes and
  validate/create/PATCH/DELETE probes returning 403. This is narrow disposable CLI-tooling evidence
  only, not a broad Desktop compatibility or real/private-book write-safety claim. Runtime book/app
  DB/backups/locks were removed after the run; no Desktop-generated fixture, raw book, backup, app
  DB, screenshot, export, private path, account name, amount, release, or tag was committed.
- Phase 177 is a write-alpha backup and restore drill for the disposable create path: a committed
  synthetic fixture was copied to a temporary external disposable source, passed the Phase 174
  redacted preflight, mutated once through the existing write-alpha create route under
  `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true`, and the generated pre-write
  backup was restored to an ignored disposable runtime path. The backup/restored checksum matched
  the pre-write synthetic source and differed from the mutated copy; a read-only API smoke against
  the restored copy passed with default disabled writes, validate/create/PATCH/DELETE probes
  returned 403, and an API absence probe found no restored-copy match for the synthetic created
  transaction. Lock behavior is documented: the current file-lock service can leave a stale lock
  file after releasing `flock`, so recovery teardown should stop runtime, verify no active holder,
  then remove ignored lock files. Runtime book/app DB/backups/locks were removed after the run; no
  production/private-book disaster recovery claim, raw book, backup, app DB, screenshot, export,
  private path, account name, amount, release, or tag was committed.
- Phase 178 is a write-alpha UX guardrails phase from copied-book dogfood findings: write-enabled
  warnings, create acknowledgement, final create confirmation, localized DELETE guardrails, and
  write-alpha form error handling now make the disposable boundary clearer by naming explicit
  `APP_ENV=test`, ignored disposable runtime copies, never source/only-copy targets, and
  backup/audit/lock-release evidence. Safe frontend error mapping avoids rendering raw path-like
  backend detail strings in create/delete forms. Static route checks pin the default-hidden write
  UI, guardrail copy, no browser-storage leak, and safe error behavior; default-false browser
  dogfood passed with write controls hidden. No write feature, backend mutation semantics, Docker
  default, `APP_ENV=test` gate, release/tag/package, real/private book, app DB, backup, `.env`,
  screenshot/export, token, key, cert, private path, or private financial data changed.
- Phase 179 is a write-alpha API hardening phase from copied-book dogfood findings: backend
  write-alpha lock-contention and path-like `GnuCashWriteError` handling now returns/audits
  user-safe generic error text without embedding book/lock paths, while preserving explicit
  `backup_path` evidence for post-backup failures. Regression tests cover path-like post-backup
  create failures, active lock contention, disabled-write short-circuit before service construction,
  and existing concurrent create locking behavior. Create/PATCH/DELETE scope is unchanged; no
  endpoint, direct SQL mutation, Docker default, `APP_ENV=test` gate, release/tag/package,
  real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, private path, or
  private financial data changed.
- Phase 180 is a combined read-only plus write-alpha regression dogfood phase: local Docker/Caddy
  default-read-only dogfood passed with `GNUCASH_WRITES_ENABLED=false`, API read-only flows passed,
  validate/create/PATCH/DELETE probes returned 403, and browser dogfood passed with hidden write UI
  and no screenshot/download/CSV artifacts. A separate explicit local-only `APP_ENV=test` plus
  `GNUCASH_WRITES_ENABLED=true` disposable write-alpha create smoke executed exactly one synthetic
  create; the host helper stopped at the known root-owned lock-file readability check after create,
  so it was not rerun, and container-side redacted inspection confirmed one successful audit row,
  one backup file, and no active lock hold. The stack was returned to default false and read-only
  API smoke passed again with disabled write probes. Runtime book/app DB/backups/locks were removed
  after verification; no release/tag/package, real/private/only-copy book, raw book, backup, app DB,
  `.env`, screenshot/export, token, key, cert, private path, or private financial data was
  committed.
- Phase 181 is a final release-readiness gate and publication decision artifact phase:
  `v0.2.1-writealpha` release notes/checklist/final-gate were prepared as an unpublished candidate
  after Phases 173–180 because the copied/disposable dogfood evidence and write-alpha UX/API
  hardening are meaningful, but no tag or GitHub release was created because explicit owner
  publication authorization was not part of this phase. The gate verdict was `Ready for release
  after explicit owner authorization — prepared but unpublished`; `GNUCASH_WRITES_ENABLED=false`
  remained default, write execution remained gated by explicit local enablement plus `APP_ENV=test`,
  and write-alpha evidence remained synthetic/disposable or copied-test-book only with no
  production/security/real-private-book safety claim.
- Phase 182 is the authorized publication phase for `v0.2.1-writealpha`: the fresh pre-publish gate
  on current `main` passed, local/remote tag and GitHub release absence were confirmed, local
  backend/frontend/Docker checks passed, rendered Compose kept `GNUCASH_WRITES_ENABLED=false`,
  tracked sensitive-file hygiene passed, GitHub Actions for the exact release/status commit passed,
  and `v0.2.1-writealpha` was published as an annotated tag and GitHub pre-release from the prepared
  notes. No package, binary artifact, Docker image, production deployment, product-code change,
  write-default change, write-scope expansion, real/private book, app DB, backup, `.env`,
  screenshot/export, token, key, cert, or production-readiness/security-audit claim was added.
- Phase 183 is a write-alpha restore UX/API evidence tightening phase: `WriteLockService.inspect()`
  and the write-alpha create smoke helper now distinguish active lock holds from stale released lock
  files and unreadable/root-owned lock files using redacted statuses and safe operator guidance;
  recovery docs and the write-mode warning explain stopped-runtime stale-lock cleanup without raw
  paths or private-book recommendations; tests pin active/stale/unreadable/no-lock behavior and the
  existing active-lock route still returns path-safe HTTP 409. No automatic lock deletion,
  production lock-management UI, write endpoint expansion, default-write enablement,
  release/tag/package, real/private/only-copy book, runtime DB/book/backup/lock artifact, `.env`,
  token, key, cert, screenshot/export, or private financial data was added.
- Phase 184 is a write-alpha PATCH disposable dogfood phase: the committed synthetic fixture was
  copied through a temporary external disposable source into ignored runtime storage, preflighted as
  external/ignored, then exercised once through the existing experimental PATCH metadata/split-memo
  route under explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`. Redacted evidence
  confirms one successful PATCH, API/runtime read-back of synthetic markers only, unchanged split
  amount fingerprint, one backup, one successful `transaction.patch` audit row, one safe
  missing-transaction failed audit without backup, and non-active stale-released lock evidence from
  inside the API container. The stack was returned to default write-disabled mode and read-only API
  smoke passed with validate/create/PATCH/DELETE probes returning 403. Runtime book/app
  DB/backups/locks were removed after verification; no new write endpoint, amount/account PATCH,
  release/tag/package, real/private/only-copy book, raw artifact, `.env`, token, key, cert,
  screenshot/export, path, account name, original description, original memo, amount, or private
  financial data was committed.
- Phase 185 is a write-alpha DELETE disposable dogfood with restore proof phase: the committed
  synthetic fixture was copied through a temporary external disposable source into ignored runtime
  storage, preflighted as external/ignored, then exercised once through the existing experimental
  DELETE route under explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`. Redacted
  evidence confirms one successful DELETE, API/runtime absence of the deleted synthetic transaction
  in the mutated copy, exactly one backup, exactly one successful `transaction.delete` audit
  increment, backup/restored checksum equality, restored runtime/API read-back of the deleted
  transaction, and non-active stale-released lock evidence from inside the API container. The stack
  was returned to default write-disabled mode and read-only API smoke passed with
  validate/create/PATCH/DELETE probes returning 403. Runtime book/app DB/backups/locks were removed
  after verification; no new write endpoint, bulk/account/recurring delete, release/tag/package,
  real/private/only-copy book, raw artifact, `.env`, token, key, cert, screenshot/export, path,
  account name, original description, memo, amount, or private financial data was committed.
- Phase 186 is a write-alpha audit trail review UI phase for disposable runs: `GET
  /books/{book_id}/write-alpha-audit-summary` now returns a read-only app-metadata-only summary of
  `transaction.create`, `transaction.patch`, and `transaction.delete` audit rows for editor/owner
  operators, exposing only action, result, timestamp, bounded transaction ID prefix, redacted backup
  presence, and safe error text. `/books/write-alpha-audit` renders the active-book operator view
  with explicit synthetic/disposable and non-production-audit copy; `/books` links to it for the
  active book. Backend tests pin unauthenticated/viewer/unauthorized blocking plus redaction of
  backup paths, private paths, raw request payload fields, memos, and amounts; frontend static
  checks pin safe fields and no browser storage/forms. Synthetic app-DB-only dogfood passed without
  opening or mutating a GnuCash book. `GNUCASH_WRITES_ENABLED=false` remains default; no new write
  endpoint, release/tag/package, real/private/only-copy book, runtime DB/book/backup artifact,
  `.env`, token, key, cert, screenshot/export, private path, account name, memo, amount, or private
  financial data was committed.
- Phase 187 is a multi-book read-only access regression and UX hardening phase after write-alpha
  work: backend regression tests now cover accessible independent books, archived/unauthorized book
  blocking, missing/not-configured storage diagnostics, transaction/account/scheduled/report route
  families, path-safe service errors, and no raw `uri_or_path` exposure. The book switcher now uses
  the existing server-side `/books/{book_id}/select` safe-link route instead of setting
  `selected_book_id` directly in client JavaScript, preserving route/query recovery while validating
  access server-side. The write-alpha new-transaction page still redirects when
  `GNUCASH_WRITES_ENABLED=false` and, if explicitly enabled, resolves accounts through
  `getActiveBookContext` so stale/unauthorized selected-book cookies recover through the same
  authenticated API context. Frontend static checks pin server-validated selection, no client-side
  selected-book cookie writes, no localStorage/sessionStorage sensitive state, hidden-by-default
  write UI, and active-book routing. No upload/delete/default-changing/registry-edit UI,
  collaborative/family-wallet flow, write default change, release/tag/package, real/private book,
  app DB, backup, `.env`, token, key, cert, screenshot/export, private path, account name, memo,
  amount, or private financial data was added.
- Phase 188 is a read-only reporting correctness edge-case phase: dashboard/reporting tests now pin
  mixed-currency split exclusion and disclosure, unknown `XXX` base-currency zero-total warnings,
  zero-balance split fallback, signed negative/contra asset/liability balances, Decimal/string JSON
  amounts, and no fake FX conversion. Report limitations now disclose excluded currencies seen in
  transaction splits as well as account listings. Dashboard drilldown static checks pin URL-filter
  parity for `account_id`, date ranges, `limit=50`, `offset=0`, and no `Number()` usage on
  dashboard/reporting paths. `docs/money-model.md` documents mixed-currency split exclusion and
  unknown-base zero-total semantics. `GNUCASH_WRITES_ENABLED=false` remains default; no write
  behavior, release/tag/package, real/private book, app DB, backup, `.env`, token, key, cert,
  screenshot/export, private path, account name, memo, amount, or private financial data was added.
- Phase 189 is a fresh-clone install smoke v2 phase: `scripts/smoke/fresh-clone-docker-smoke.sh` was
  run against current public read-only tag `v0.1.7-readonly`, current public write-alpha tag
  `v0.2.1-writealpha`, and current `main`, each from a temporary clone with only the committed
  synthetic fixture, dummy local-only secrets, and `GNUCASH_WRITES_ENABLED=false`. All three passed
  Docker Compose config/startup, `/api/health`, login/auth, books, accounts, transactions,
  transaction detail, CSV export, reports summary, browser dogfood, hidden write UI, disabled
  validate/create/PATCH/DELETE probes returning 403, and no-artifact checks. Teardown left no
  fresh-clone temp directories and no `gwc_fresh_clone` Docker containers/volumes/networks. No smoke
  helper/product code change, write-enabled run, release/tag/package/image, real/private book,
  runtime artifact, `.env`, token, key, cert, screenshot/export, private path, account name, memo,
  amount, or private financial data was added.
- Phase 190 is a combined cycle-2 release-candidate dogfood phase: local Docker/Caddy
  default-read-only dogfood passed with `GNUCASH_WRITES_ENABLED=false`; API read-only flows passed;
  validate/create/PATCH/DELETE probes returned 403; browser dogfood passed at mobile 320x720 and
  desktop 1280x900 with hidden write UI, auth cookie not readable from `document.cookie`, CSV fetch
  success, no-overflow checks, and no screenshot/download/CSV artifacts. Separate explicit
  local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` disposable write-alpha smokes
  collected bounded create/PATCH/DELETE route-family evidence: create success audit/backup, PATCH
  expected failed missing-transaction audit plus success audit/backup, DELETE success audit/backup,
  and non-active stale lock evidence from inside the API container. Host-side root-owned runtime
  readability limited the smoke helpers' final lock/restore checks, so no new restore claim is made
  here; the stack was returned to default false and read-only API smoke passed again with disabled
  write probes. Runtime book/app DB/backups/locks were removed after verification; no product code
  change, release/tag/package/image, real/private/only-copy book, raw artifact, `.env`, token, key,
  cert, screenshot/export, private path, account name, memo, amount, production/security claim, or
  real/private-book write-safety claim was added.
- Phase 191 is the cycle-2 release-readiness gate and publication phase: README, README.ru,
  CHANGELOG, release docs, dogfood evidence, GitHub releases/actions, open issues, and current
  `main` were compared against actual repository state; target `v0.2.2-writealpha` was selected
  because cycle-2 includes write-alpha evidence and safety/operator hardening after
  `v0.2.1-writealpha`; local backend/frontend/Docker checks, `GNUCASH_WRITES_ENABLED=false`
  defaults, `git diff --check`, sensitive tracked-file hygiene, tag/release absence, and GitHub
  Actions on the exact release/status commit passed; then `v0.2.2-writealpha` was published as a
  conservative GitHub pre-release. Publication created only the annotated tag and GitHub
  pre-release; no package, image, production deployment, write default change, write-scope
  expansion, real/private book, app DB, backup, `.env`, token, key, cert, screenshot/export, private
  path, amount, production/security claim, public-internet safety claim, or real/private-book
  write-safety claim was added.
- Phase 192 is a CI/toolchain warning cleanup phase after `v0.2.2-writealpha`: GitHub Actions
  JavaScript actions now use Node 24-compatible major versions (`actions/checkout@v5`,
  `actions/setup-node@v6`, and `actions/setup-python@v6`) in the existing foundation, frontend,
  backend, and Docker Compose jobs, addressing the known non-blocking Node.js 20 deprecation
  warnings observed around Phase 191/first Phase 192 CI while preserving the same
  backend/frontend/Docker checks and without changing product code, Docker runtime defaults, writes
  configuration, releases/tags, issues, or sensitive artifacts. Local verification passed for
  backend pytest, frontend check/auth-routes/build, Docker Compose config with rendered
  `GNUCASH_WRITES_ENABLED: "false"`, `.env.example` default false, `git diff --check`, and sensitive
  tracked-file hygiene; exact pushed CI passed without Node.js 20 action deprecation warnings.
- Phase 193 is a root-owned ignored runtime cleanup and lock recovery UX phase:
  `scripts/ops/runtime-cleanup.py` and `apps/api/app/runtime_cleanup.py` now provide a
  stopped-runtime-only helper for redacted dry-run/cleanup of allowed ignored `data/books`,
  `data/app`, `data/backups`, and `data/locks` classes, including stale lock cleanup, unreadable
  lock cleanup after explicit stopped-runtime acknowledgement, active flock-held lock preservation,
  fail-closed non-repo data-root checks, and optional `--via-compose` execution for host-side
  permission problems. Tests cover missing acknowledgement, active/stale/unreadable locks,
  unsupported lock children, output redaction, and allowlist failure cases; manual dogfood used
  synthetic ignored placeholders only and left runtime data clean. `GNUCASH_WRITES_ENABLED=false`
  remains default; no write route, release/tag, real/private book, app DB, backup, `.env`, token,
  key, cert, screenshot, export, raw path, account name, memo, amount, production/security claim, or
  real/private-book write-safety claim was added.
- Phase 194 is a write-alpha smoke helper resilience phase: create/PATCH/DELETE smoke scripts now
  collect backup, audit, and lock evidence through shared redacted helpers that fall back to
  read-only probes inside the running API container when host-side runtime artifacts are root-owned
  or unreadable. The helpers preserve exactly-once route execution, avoid rerunning mutating routes
  after evidence failures, keep output path-safe, map `/data/...` backup paths to ignored host
  runtime paths when readable, and emit DELETE restore proof only when a restore copy is actually
  performed. Targeted tests cover container fallback, redaction, and restore-skip copy; local
  synthetic/disposable dogfood passed default read-only smoke, create, PATCH, DELETE+restore, and
  final default read-only smoke with validate/create/PATCH/DELETE returning 403.
  `GNUCASH_WRITES_ENABLED=false` remains default; no write route semantics, write scope,
  release/tag, real/private/only-copy book, app DB, backup, `.env`, token, key, cert, screenshot,
  export, raw path, account name, memo, amount, production/security claim, or real/private-book
  write-safety claim was added.
- Phase 195 is a write-alpha audit summary operator UX hardening phase: the existing read-only `GET
  /books/{book_id}/write-alpha-audit-summary` endpoint now supports safe action/result/time-window
  filters, bounded filtered/returned counts, and grouped action/result counts while still reading
  app metadata only and returning redacted fields only. `/books/write-alpha-audit` now exposes
  URL-only GET filters, count/status cards, filtered empty-state copy, and bounded mobile layout
  classes without localStorage/sessionStorage or mutation controls. Backend tests pin owner/editor
  access, viewer/unauthorized blocking, filter behavior, empty state, safe invalid-filter errors,
  and absence of backup paths, private paths, raw payload fields, account names, memos, and amounts.
  Frontend static checks pin authenticated active-book loading, safe fields, URL-only filters,
  count/status UI, no horizontal overflow guards, and no browser storage.
  `GNUCASH_WRITES_ENABLED=false` remains default; no raw audit payloads, backup paths,
  export/editor, write gate/default change, release/tag, real/private book, app DB, backup artifact,
  `.env`, token, key, cert, screenshot/export, private path, account name, memo, amount, or private
  financial data was added.
- Phase 196 is a first-run/read-only deployment confidence pass after `v0.2.2-writealpha`: `/health`
  now exposes a redacted `first_run` block with stable safe checks for JWT placeholder/missing
  state, admin bootstrap credentials, default book presence/readability, unsafe wildcard CORS
  outside development-like environments, and write-disabled status. `/login` fetches those
  diagnostics server-side and renders localized EN/RU mobile-safe operator guidance before
  authentication, while keeping messages secret/path/token/app-DB/book-data redacted and preserving
  httpOnly cookie auth with no localStorage/sessionStorage. Troubleshooting docs now document the
  `first_run` shape and CORS/write-mode triage. Synthetic Docker/Caddy first-run smoke used only
  dummy local secrets and a copied committed fixture, confirmed diagnostics on `/api/health` and
  `/login`, and read-only API smoke confirmed validate/create/PATCH/DELETE probes still return 403.
  `GNUCASH_WRITES_ENABLED=false` remains default; no setup wizard, config-writing UI, auth-model
  change, production/security claim, release/tag, real/private book, app DB, backup artifact,
  `.env`, token, key, cert, screenshot/export, private path, account name, memo, amount, or private
  financial data was added.
- Phase 197 is a disposable GnuCash Desktop fixture compatibility blocker refresh for GitHub #22: a
  temporary `debian:12-slim` container probe again confirmed GnuCash/GnuCash CLI 4.13 tooling can be
  installed in isolation, but `gnucash-cli --help` still exposes report/quote commands rather than a
  safe noninteractive create/save-as SQLite fixture path, so no Desktop-generated synthetic fixture
  was created and no Desktop-version compatibility row is claimed. The exact next requirement is an
  isolated disposable GUI/manual-safe Desktop session that creates/saves a synthetic SQLite fixture
  outside git, followed by phase-197 redacted metadata collection with `--fixture-origin
  desktop-generated-synthetic` and read-only API validation with `GNUCASH_WRITES_ENABLED=false`. The
  metadata collector now records provenance/redaction metadata and tests prove private paths,
  account names/descriptions, transaction descriptions, split memos, split amounts, and other row
  values are excluded. No host package install, product behavior change, write behavior change,
  release/tag, real/private book, app DB, backup artifact, `.env`, token, key, cert,
  screenshot/export, broad Desktop/version/backend claim, or private financial data was added.
- Phase 198 is a multi-book read-only registry diagnostics hardening phase for GitHub #13: backend
  `/books` metadata now adds safe status severity, access-role labels/descriptions, and
  `can_open_read_only_views` so accessible independent books expose actionable diagnostics while
  missing/not-configured books do not advertise broken data-view actions. `/books` UI renders the
  safe role/status diagnostics, hides data-view links for unavailable books, keeps mobile-friendly
  wrapping controls, and the server-validated book-select route refuses accessible-but-unavailable
  books with a safe return to `/books`. Backend route-family tests cover accounts, transactions,
  scheduled metadata, reports, and CSV export boundaries across accessible, archived, unauthorized,
  missing, and not-configured books; frontend static checks pin selected-book cookie recovery, no
  raw `uri_or_path`, no client-side selected-book cookie writes, and no sensitive browser storage.
  `GNUCASH_WRITES_ENABLED=false` remains default; no registry management UI,
  upload/delete/default-changing controls, collaborative/family-wallet workflow, release/tag,
  real/private book, app DB, backup artifact, `.env`, token, key, cert, screenshot/export, raw path,
  or private financial data was added.
- Phase 199 is a full default-read-only Docker/Caddy regression dogfood phase after cycle-3 Phases
  192–198: local Compose ran with the committed synthetic fixture copied into ignored runtime data
  and `GNUCASH_WRITES_ENABLED=false`; rendered config showed writes disabled for API and web;
  read-only API smoke passed for health, login/auth, books/default book, accounts, transactions,
  transaction detail, CSV export, reports summary, and disabled validate/create/PATCH/DELETE probes
  returning 403; browser dogfood passed at mobile `320x720` and desktop `1280x900` with hidden write
  UI, auth cookie not readable from `document.cookie`, CSV fetch success, no-overflow checks, and no
  screenshot/download/CSV artifacts. Teardown removed the ignored runtime book, app DB, and dummy
  local `.env`. No write-enabled mode, release/tag/package/image, real/private/only-copy book,
  committed app DB/backup/runtime artifact, token, key, cert, private path, or private financial
  data was added.
- Phase 200 is a bounded write-alpha disposable CRUD/restore dogfood phase after cycle-3 helper/UX
  fixes: explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` was used only on
  ignored synthetic runtime copies, with a fresh prepared copy for each route family. Create, PATCH,
  and DELETE route-family smokes each executed exactly once per prepared copy; create and PATCH
  collected safe failed-validation/missing-transaction evidence, all successful writes had backup
  and audit evidence, DELETE completed a host-readable backup restore proof with read-back, and all
  lock probes reported stale released locks rather than active holds. The stack was reset to default
  false, rendered Compose showed `GNUCASH_WRITES_ENABLED: "false"` for API and web, read-only API
  smoke passed with validate/create/PATCH/DELETE returning 403, and stopped-runtime cleanup removed
  ignored runtime book/app DB/backups/locks plus the dummy local `.env`. No write route expansion,
  release/tag/package/image, production/private-book safety claim, real/private/only-copy book,
  committed runtime artifact, raw path, account name, memo, amount, token, key, cert, or private
  financial data was added.
- Phase 212 is a public status drift guard phase after `v0.2.4-writealpha`: `docs/ROADMAP.md`,
  README/README.ru, CHANGELOG, PROJECT_STATUS, release-support docs, CI, and backend tests now pin
  the current public posture to Phase 211 release baseline, `v0.1.7-readonly`, `v0.2.4-writealpha`,
  `GNUCASH_WRITES_ENABLED=false`, and conservative no-production/no-security/no-stable-claim
  wording. The guard reads only declared public docs/config files and does not inspect `.env`,
  runtime books, app DBs, backups, or private paths. No product runtime behavior, write route, write
  default, `APP_ENV=test` gate, release/tag, package/image, real/private book, app DB, backup,
  `.env`, token, key, cert, screenshot/export, or private financial data was changed.
- Phase 213 is a `v0.2.4-writealpha` tagged fresh-clone smoke phase:
  `scripts/smoke/fresh-clone-docker-smoke.sh` verified the published tag and current `HEAD` from
  temporary fresh clones using only the committed synthetic fixture, dummy local-only secrets,
  Docker Compose/Caddy, `GNUCASH_WRITES_ENABLED=false`, read-only API smoke, disabled
  validate/create/PATCH/DELETE probes returning 403, and browser dogfood at mobile `320x720` and
  desktop `1280x900` widths with auth cookie not readable from `document.cookie`. The helper now
  runs both browser widths, and browser dogfood treats wide viewports as desktop. No write-enabled
  mode, product behavior change, release/tag, package/image, real/private book, app DB, backup,
  `.env`, screenshot/export, token, key, cert, raw private path, account name, memo, amount, or
  private financial data was added.
- Phase 215 is a read-only unavailable-book error contract hardening phase: read-only data route
  families now require accessible local book storage before constructing GnuCash services and return
  deterministic path-safe `503` responses for missing/not-configured books, while metadata-only
  `/books` remains available for recovery diagnostics without raw `uri_or_path` exposure. The web
  503 page sends operators back to `/books`, and browser/API dogfood verified a synthetic
  accessible-but-missing book recovery path at mobile and desktop widths with default
  `GNUCASH_WRITES_ENABLED=false`, hidden write UI, disabled validate/create/PATCH/DELETE probes
  returning 403, no screenshots/downloads/CSV artifacts, and no real/private data. No book
  upload/delete/default-changing/registry-edit UI, write-enabled mode, release/tag/package/image,
  production/security claim, broad compatibility claim, or real/private-book write safety claim was
  added.
- Phase 216 is a read-only CSV/export and list parity regression phase: backend tests now pin
  transaction-note query matching parity between list and CSV export plus account-scoped
  empty/header-only export metadata, while frontend route/static checks reject browser storage for
  financial filters and `Number()`/`parseFloat()`/`parseInt()` money-string coercion on
  transaction/account export UI. Synthetic Docker/Caddy dogfood used only the committed fixture
  copied to ignored runtime data with dummy local-only credentials and fetched CSV through smoke
  helpers without saving raw export artifacts. `GNUCASH_WRITES_ENABLED=false` remains default; no
  import, export queue, cap increase, FX conversion, write behavior, release/tag/package/image,
  real/private book, app DB, backup, `.env`, screenshot/download/raw CSV artifact, token, key, cert,
  account name, memo, amount, or private financial data was added.
- Phase 217 is a write-alpha backup-failure and no-mutation drill phase: create, PATCH, and DELETE
  route-family regression tests now inject backup creation failures with path-like details and prove
  the routes fail before opening the book for write or mutating the disposable synthetic fixture,
  record failed audit rows without backup paths, return path-safe API/audit errors, and release the
  per-book lock. Existing post-backup injected create/PATCH/DELETE failure tests continue to prove
  backup evidence is retained and the fixture remains unchanged. Default-read-only
  validate/create/PATCH/DELETE route coverage still returns 403 before book resolution/write-service
  construction. `GNUCASH_WRITES_ENABLED=false` remains default and write-alpha remains executable
  only under explicit `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` on copied/disposable
  synthetic fixtures; no new write endpoint, amount/account PATCH, account/import/scheduled write,
  release/tag/package/image, real/private/only-copy book, app DB, backup artifact, `.env`,
  screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security
  claim, or real/private-book write-safety claim was added.
- Phase 214 is a synthetic local upgrade smoke phase: `scripts/smoke/synthetic-upgrade-smoke.sh`
  verified upgrade from `v0.2.4-writealpha` runtime state to current `main` using a temporary clone,
  committed synthetic fixture copy, dummy app metadata DB, dummy local-only credentials, Docker
  Compose/Caddy, `GNUCASH_WRITES_ENABLED=false`, read-only
  accounts/transactions/reports/scheduled/audit-summary routes, selected-book recovery, and disabled
  validate/create/PATCH/DELETE probes returning 403. No write-enabled mode, migration wizard,
  release/tag, package/image, real/private book, app DB, backup, `.env`, screenshot/export, token,
  key, cert, raw private path, account name, memo, amount, or private financial data was added.
- Previous public release `v0.1.2-readonly` remains available and points to its Phase 117 release
  commit.
- Previous public release `v0.1.1-readonly` remains available and points to
  `a4d04150c043ad4da3dea577b30ed7ffd2032df0`, after Phase 104.

Completed phases:

- Phase 0 — competitive review and product positioning
- Phase 1 — open-source foundation
- Phase 2 — SvelteKit + FastAPI + Docker skeleton
- Phase 3 — app metadata DB and book registry foundation
- Phase 4 — authentication foundation
- Phase 5 — read-only piecash service layer
- Phase 6 — books/accounts API and UI
- Phase 7 — transaction browsing API and UI
- Phase 8 — dashboard reports API and UI
- Phase 9 — frontend theme, mobile shell, PWA manifest
- Phase 10 — public repo hygiene and release readiness
- Phase 11 — integration QA and MVP hardening
- Phase 12 — controlled transaction writes implemented as post-MVP capability
- Phase 13 — agent project context
- Phase 14 — MVP read-only scope lock and write gating
- Phase 15 — public pre-alpha release readiness
- Phase 16 — project lead subagent profile
- Phase 17 — synthetic GnuCash fixture and read-only integration validation
- Phase 18 — README screenshots and mobile preview with synthetic data
- Phase 19 — multi-currency limitation tests and auth cookie security documentation
- Phase 20 — multi-book UI foundation
- Phase 21 — file-based write lock replacement
- Phase 22 — real controlled write integration tests
- Phase 23 — backup restore smoke test
- Phase 24 — CSV export for transactions
- Phase 25 — documentation, release, and roadmap sync
- Phase 26 — audit-driven status sync
- Phase 27 — discoverability and community announcement readiness
- Phase 28 — GnuCash compatibility matrix
- Phase 29 — audit-driven release documentation sync
- Phase 30 — transaction amount range filters for CSV export
- Phase 31 — read-only safety status banner
- Phase 32 — backend write-gating regression coverage
- Phase 33 — controlled-writes documentation cleanup and status sync
- Phase 34 — README/public status baseline sync after Phase 33 audit finding
- Phase 35 — audit-driven Phase 34 public baseline and controlled-writes docs sync
- Phase 36 — write-mode UI warning and explicit confirmation
- Phase 37 — independent audit and baseline sync
- Phase 38 — personal dogfood readiness
- Phase 39 — read-only smoke test automation
- Phase 40 — v0.0.2-prealpha release candidate cleanup
- Phase 41 — release gate audit for v0.0.2-prealpha
- Phase 42 — publish v0.0.2-prealpha
- Phase 43 — local deployment hardening guide
- Phase 44 — backup and recovery runbook
- Phase 45 — GnuCash compatibility fixture plan
- Phase 46 — Compatibility fixture implementation v1
- Phase 47 — auditor pass after compatibility work
- Phase 48 — UX polish for read-only core
- Phase 49 — transaction search/filter hardening
- Phase 50 — book switcher stabilization
- Phase 51 — auditor pass after UX/book/filter work
- Phase 52 — Russian localization planning and i18n foundation
- Phase 53 — community announcement draft
- Phase 54 — observability and diagnostics
- Phase 55 — v0.1 read-only scope freeze audit
- Phase 56 — v0.1 read-only release planning
- Phase 57 — v0.1.0-readonly release-gate audit
- Phase 58 — v0.1.0-readonly release publication audit
- Phase 59 — post-release regression risk audit
- Phase 60 — dogfood readiness audit
- Phase 61 — dogfood results audit
- Phase 62 — deployment safety audit
- Phase 63 — backup/recovery audit
- Phase 64 — compatibility audit
- Phase 65 — test coverage audit
- Phase 66 — security posture audit
- Phase 67 — open-source hygiene audit
- Phase 68 — documentation formatting audit
- Phase 69 — localization/i18n audit
- Phase 70 — community announcement audit
- Phase 71 — performance risk audit
- Phase 72 — data model and money correctness audit
- Phase 73 — multi-book access model audit
- Phase 74 — controlled writes boundary audit
- Phase 75 — v0.1.1 maintenance release audit
- Phase 76 — v0.2 planning audit
- Phase 77 — real read-only dogfood on copied/disposable GnuCash SQL book
- Phase 78 — Docker `/login` redirect-loop fix and browser/UI dogfood rerun
- Phase 79 — accept dogfood evidence, write v0.1 release notes, and final release gate
- Phase 80 — publish v0.1.0-readonly pre-release
- Phase 81 — redact default-book seed logs and close post-release security hardening issue #27
- Phase 82 — expand read-only multi-book access boundary regression coverage and close #35
- Phase 83 — replace frontend `Number()` money display decisions and close #34
- Phase 84 — define tested CSV export truncation/timeout behavior and close #32
- Phase 85 — post-v0.1 copied personal-book dogfood attempt with safe blocker tracking
- Phase 86 — Phase 85 dogfood blocker triage and safe copied-book preflight helper
- Phase 87 — large-book read-only benchmark v1
- Phase 88 — account with many splits performance test
- Phase 89 — dashboard aggregate performance and correctness pass
- Phase 90 — transaction active filter summary UX improvement
- Phase 91 — read-only book management metadata UI
- Phase 92 — compatibility fixture v2 / version matrix progress
- Phase 93 — Russian localization small slice
- Phase 94 — post-v0.1 maintenance release decision
- Phase 95 — CSV export row-count/header mismatch fix
- Phase 96 — synthetic large-export benchmark and UX confirmation
- Phase 97 — v0.1.1-readonly release-prep checklist and notes
- Phase 98 — v0.1.1-readonly release-gate verification
- Phase 99 — v0.1.1-readonly pre-publish dry-run and authorization guard
- Phase 100 — non-publishing synthetic install/upgrade smoke
- Phase 101 — copied personal-book dogfood rerun gate blocked by missing safe copied book path
- Phase 102 — compatibility fixture/version matrix v3 safe provenance refresh
- Phase 103 — read-only transaction date-range preset UX from GitHub #11
- Phase 104 — read-only transaction query semantics over split memos from GitHub #11
- Phase 105 — v0.1.1-readonly release/docs correction after publication
- Phase 106 — read-only transaction state/reconciliation filters from GitHub #11
- Phase 107 — transaction filter URL presets and clear-all reset UX from GitHub #11
- Phase 108 — account detail transaction filter/export parity from GitHub #11
- Phase 109 — scheduled/recurring transaction read-only awareness from GitHub #12
- Phase 110 — books metadata UX hardening from GitHub #13
- Phase 111 — compatibility fixture v4 safe Desktop-tooling evidence from GitHub #22
- Phase 112 — LAN/VPN deployment safety behavior from GitHub #26
- Phase 113 — Russian localization glossary and transaction filter/export UI slice from GitHub
  #17/#29
- Phase 114 — synthetic browser dogfood refresh after UX/filter changes
- Phase 115 — v0.1.2-readonly maintenance release prep and final gate without publication
- Phase 116 — GitHub #38 copied personal-book dogfood with redacted read-only evidence
- Phase 117 — publish v0.1.2-readonly pre-release
- Phase 118 — transaction table column width and horizontal scroll fix
- Phase 119 — strip Root Account prefix from displayed account full names
- Phase 120 — account detail performance optimization
- Phase 121 — dashboard summary zero-value fallback fix
- Phase 122 — read-only stability gate and v0.1.3-readonly prep
- Phase 123 — write-alpha safety foundation without default enablement
- Phase 124 — write-alpha controlled transaction create hardening
- Phase 125 — publish v0.1.3-readonly pre-release
- Phase 126 — read-only transaction filter polish and GitHub #11/#12 triage
- Phase 127 — GnuCash Desktop compatibility evidence refresh for GitHub #22
- Phase 128 — Write-alpha concurrency and error-path expansion
- Phase 129 — Write-alpha recovery documentation and maintainer review gate
- Phase 130 — Write-alpha PATCH transaction hardening
- Phase 131 — Write-alpha DELETE transaction and validation hardening
- Phase 132 — v0.2.0-writealpha release gate artifacts; later published as authorized pre-release
- Phase 133 — read-only UX empty/error state polish
- Phase 134 — read-only UX skeleton loading states
- Phase 135 — read-only UX mobile navigation polish
- Phase 136 — GnuCash compatibility matrix documentation refresh
- Phase 137 — local secure deployment hardening guide
- Phase 138 — public README/CHANGELOG/roadmap/status documentation sync
- Phase 139 — synthetic dogfood refresh
- Phase 140 — v0.1.4-readonly maintenance release readiness audit
- Phase 141 — v0.1.4-readonly release artifact preparation
- Phase 142 — v0.1.4-readonly release gate and authorized publication
- Phase 143 — read-only runtime status banner v2
- Phase 144 — account tree discoverability and heavy-account UX polish
- Phase 145 — transaction list usability and filter/export confidence
- Phase 146 — transaction detail and split readability polish
- Phase 147 — dashboard/reporting limitation clarity
- Phase 148 — books page self-hosting readiness slice
- Phase 149 — Russian localization coverage for new read-only UX
- Phase 150 — Synthetic Docker/browser dogfood refresh
- Phase 151 — v0.1.5-readonly maintenance release readiness artifacts
- Phase 152 — Conditional v0.1.5-readonly release publication
- Phase 153 — Fresh-clone Docker install smoke
- Phase 154 — GnuCash compatibility fixture path v5 blocker refresh
- Phase 155 — Multi-book read-only operator UX slice
- Phase 156 — Dashboard drilldown and reporting evidence
- Phase 157 — Scheduled transactions read-only clarity v2
- Phase 158 — Transaction/account mobile dogfood fix pass
- Phase 159 — Release-critical frontend localization pass
- Phase 160 — Release-candidate synthetic Docker/browser dogfood
- Phase 161 — v0.1.6-readonly maintenance release gate and authorized publication
- Phase 162 — post-v0.1.6 baseline sync and tagged read-only smoke
- Phase 163 — disposable GnuCash Desktop container tooling blocker for GitHub #22
- Phase 164 — Book context and access edge-case hardening
- Phase 165 — Large account tree usability and benchmark
- Phase 166 — CSV export reliability and user feedback hardening
- Phase 167 — Auth/session hardening for local/LAN pre-alpha
- Phase 168 — First-run and broken-configuration operator UX
- Phase 169 — Russian localization release-critical completion slice
- Phase 170 — Full synthetic dogfood after cycle 2 changes
- Phase 171 — v0.1.7-readonly release gate and authorized publication
- Phase 172 — Public status reconciliation after v0.1.7/v0.2.0 publications
- Phase 173 — Write-alpha copied-book dogfood design
- Phase 174 — Write-alpha copied-book preflight harness
- Phase 175 — Write-alpha controlled create dogfood on disposable copy
- Phase 176 — GnuCash Desktop/tooling verification for disposable write-alpha mutated copy
- Phase 177 — Write-alpha backup and restore drill
- Phase 178 — Write-alpha UX guardrails from dogfood findings
- Phase 179 — Write-alpha API hardening from dogfood findings
- Phase 180 — Full read-only plus write-alpha regression dogfood
- Phase 181 — Final release-readiness gate and unpublished v0.2.1-writealpha decision artifact
- Phase 182 — Authorized v0.2.1-writealpha publication under fresh gate
- Phase 183 — Write-alpha restore UX/API evidence tightening
- Phase 184 — Write-alpha PATCH disposable dogfood
- Phase 185 — Write-alpha DELETE disposable dogfood with restore proof
- Phase 186 — Write-alpha audit trail review UI for disposable runs
- Phase 187 — Multi-book read-only access regression and UX hardening
- Phase 188 — Read-only reporting correctness edge cases
- Phase 189 — Fresh-clone install smoke v2 with published/current tags
- Phase 190 — Combined release-candidate dogfood after cycle-2 changes
- Phase 191 — Cycle-2 release-readiness gate and publication
- Phase 192 — CI/toolchain warning cleanup
- Phase 193 — Root-owned runtime cleanup and lock recovery UX
- Phase 194 — Write-alpha smoke helper resilience
- Phase 195 — Write-alpha audit summary operator UX hardening
- Phase 196 — First-run/read-only deployment confidence pass
- Phase 197 — Disposable GnuCash Desktop fixture compatibility blocker refresh
- Phase 198 — Multi-book read-only registry diagnostics hardening
- Phase 199 — Full default-read-only regression dogfood
- Phase 200 — Bounded write-alpha disposable CRUD/restore dogfood

- Phase 87 completed the large-book read-only benchmark v1 on generated synthetic data only: a local
  CLI now creates a disposable synthetic GnuCash SQLite book and measures accounts tree,
  transactions first page, transaction filters, account detail transactions, dashboard summary, and
  CSV export through read-only authenticated API paths. Results are documented in
  `docs/performance/phase-87-large-book-benchmark.md`. The 1,000-transaction run found no endpoint
  failure, but account-detail transactions measured above one second locally and CSV export returned
  only 500 rows while reporting `csv_total=1000` and `truncated=false`; GitHub #39 tracks that
  follow-up. GitHub #30 was closed as the benchmark now exists. No real/private data was committed,
  no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 88 completed the account-with-many-splits performance test on generated synthetic data only:
  the benchmark fixture now includes 1,000 transactions, one 60-split transaction, account-detail
  pagination checks for offsets 0 and 50, and transaction-detail rendering for the many-splits
  transaction. Results are documented in `docs/performance/phase-88-many-splits-benchmark.md`. The
  many-splits detail path rendered 60 splits without endpoint failure in the local/TestClient run;
  account-detail pagination remains above one second locally and is documented as a limitation
  rather than a scalability claim. GitHub #31 was closed with evidence. GitHub #39 remains open for
  the CSV export row-count/header mismatch. No real/private data was committed, no new tag/release
  was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 89 completed the dashboard aggregate performance and correctness pass on generated synthetic
  data only: dashboard summary now exposes `reporting_basis=base_currency_only`,
  `includes_currency_conversion=false`, and no-conversion/mixed-currency limitations, the web
  dashboard displays those limitations, report date validation now returns clearer `422` client
  errors, and the large-book benchmark now covers dashboard summary, cashflow-by-month,
  expenses-by-account, and recent-transactions. Results are documented in
  `docs/performance/phase-89-dashboard-aggregate-benchmark.md`. All dashboard endpoints returned
  `200` in the 1,000-transaction local/TestClient benchmark; cashflow-by-month and
  recent-transactions remain service-layer scans and are documented as pre-alpha evidence rather
  than a production scalability claim. GitHub #33 was closed with evidence. GitHub #39 remains open
  for the CSV export row-count/header mismatch. No real/private data was committed, no new
  tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 90 completed a narrow transaction search/filter UX improvement from GitHub #11: the
  transaction filter form now shows a readable active filter summary for search, account, date
  range, and amount range, explicitly stating that the same filters apply to the read-only list and
  CSV export. Frontend route checks cover the summary and CSV parity copy. No backend write changes
  were made, CSV export query-string parity remains intact, no real/private data was committed, no
  new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 91 completed the read-only book management metadata UI from the roadmap and GitHub #13
  subset: the web app now exposes `/books` from desktop/mobile navigation, lists only accessible
  configured books, marks the current/default book, and shows book name, base currency, storage
  type, read-only status, and access status without upload, deletion, registry editing, GnuCash data
  editing, collaborative, or family-wallet framing. Existing backend access-boundary tests continue
  to prove unauthorized and archived books are hidden/blocked; frontend route checks cover the new
  page and nav links. GitHub #13 was updated with evidence and remains open for future admin-only
  registration/default/deletion-from-registry workflows. No real/private data was committed, no new
  tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 92 completed a narrow compatibility-fixture/version-matrix maintenance result: a tested
  metadata collector now records safe schema/version evidence from copied/disposable GnuCash SQLite
  books while redacting the input path and excluding account names, transaction descriptions,
  amounts, memos, split rows, screenshots, app DB data, and secrets. `docs/gnucash-compatibility.md`
  now includes a narrow Phase 92 matrix row for the local generated-fixture metadata procedure, and
  `docs/gnucash-version-fixture-plan.md` now documents the copied/test-book collection process.
  GnuCash Desktop was not installed in this environment, so no desktop-version compatibility pass is
  claimed. No real/private data was committed, no new tag/release was published, writes remain
  disabled by default, and no v0.2 work was started.

- Phase 93 completed a narrow Russian localization slice: desktop/mobile navigation now localizes
  the `/books` label, the read-only `/books` metadata page uses English/Russian catalog strings for
  headings, helper copy, read-only badges, access/status labels, empty state, and the GnuCash
  Desktop authoritative-editor safety note, and `README.ru.md` plus `docs/localization.md` document
  that English remains canonical and translation is incomplete. Frontend route/static checks cover
  the new catalog strings and localized `/books` usage. No real/private data was committed, no new
  tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 94 completed the post-v0.1 maintenance-release decision from the roadmap without
  analyst/auditor involvement or audit-only artifacts: `docs/release/v0.1.1-readonly-decision.md`
  records the verdict `More fixes required before maintenance release`. The reviewed
  post-`v0.1.0-readonly` change set is meaningful, but GitHub #39 remains an open read-only CSV
  export correctness blocker because benchmark evidence repeatedly showed the CSV body capped at 500
  rows while headers report a 10,000-row cap and `truncated=false`. No `v0.1.1-readonly`
  notes/checklist were created, no tag/release was published, no real/private data was committed,
  writes remain disabled by default, and no v0.2 work was started.

- Phase 95 fixed the read-only CSV export row-count/header mismatch tracked by GitHub #39: CSV
  export now asks the service layer for up to the documented export cap instead of inheriting the
  historical 500-row service clamp used by normal list-style callers. Regression coverage proves a
  501-row synthetic export returns 501 data rows with `X-CSV-Export-Limit: 10000`,
  `X-CSV-Export-Total: 501`, and `X-CSV-Export-Truncated: false`; the benchmark helper also records
  the CSV limit header. A targeted 1,000-transaction synthetic benchmark returned 1,000 CSV data
  rows with `csv_limit=10000`, `csv_total=1000`, and `truncated=False`. No frontend proxy change was
  needed because it already forwards CSV metadata headers; frontend route checks still verify that
  behavior. No real/private data was committed, no tag/release was published, writes remain disabled
  by default, and no v0.2 work was started.

- Phase 96 confirmed the Phase 95 / GitHub #39 fix through the generated synthetic large-book
  benchmark path and a narrow frontend UX copy check. The 1,000-transaction synthetic benchmark
  returned 1,000 CSV data rows with `csv_limit=10000`, `csv_total=1000`, `truncated=False`,
  `csv_expected_body_rows=1000`, and `csv_body_matches_expected=True`; results are documented in
  `docs/performance/phase-96-large-export-benchmark.md`. Benchmark JSON now records expected
  body-row consistency fields, and the transaction export helper copy now states that export is
  read-only, filtered, capped at 10,000 rows, synchronous, and may require narrower filters if a
  request times out or is truncated. GitHub #39 remains closed; GitHub #38 remains open and separate
  for copied personal-book dogfood. No real/private data was committed, no tag/release was
  published, writes remain disabled by default, and no v0.2 work was started.

- Phase 97 prepared conservative `v0.1.1-readonly` release-prep artifacts without publishing a
  tag/release: `docs/release/v0.1.1-readonly-notes.md` and
  `docs/release/v0.1.1-readonly-checklist.md`. The notes/checklist summarize post-`v0.1.0-readonly`
  maintenance value, especially the Phase 95 CSV export fix and Phase 96 synthetic benchmark
  confirmation, while keeping pre-alpha/read-only/default-write-disabled safety language and
  explicitly requiring a later Phase 98 release gate before publication. GitHub #39 remains closed;
  GitHub #38 remains open/blocked for copied personal-book dogfood. No real/private financial data,
  GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, or keys
  were committed; writes remain disabled by default; controlled writes remain post-MVP/experimental;
  no v0.2 work was started.

- Phase 98 completed the `v0.1.1-readonly` final release-gate verification without publishing a
  tag/release: `docs/release/v0.1.1-readonly-final-gate.md` records the verdict `Ready for later
  authorized publish phase`. Backend tests passed (`329 passed, 27 warnings`), frontend
  check/auth-routes/build passed, Docker Compose config validation passed, recent GitHub Actions
  `main` runs were successful, no local tag or GitHub release named `v0.1.1-readonly` exists, GitHub
  #39 remains closed, and GitHub #38 remains open/blocked for copied personal-book dogfood. No
  backend/frontend/config/write-mode code was changed; writes remain disabled by default; controlled
  writes remain post-MVP/experimental; no real/private financial data, GnuCash books, `.env`, app
  DBs, backups, screenshots, exports, secrets, tokens, certs, or keys were committed; no v0.2 work
  was started.

- Phase 99 completed a safe non-publishing `v0.1.1-readonly` pre-publish dry-run and authorization
  guard: `docs/release/v0.1.1-readonly-prepublish-dry-run.md` records the verdict `Ready for
  explicit authorized publish`, confirms release notes/checklist/final-gate artifact presence,
  confirms no local tag or GitHub release named `v0.1.1-readonly` exists, records recent GitHub
  Actions state, records would-run publish commands as `NOT EXECUTED`, and records that publication
  authorization is absent in this phase. GitHub #39 remains closed; GitHub #38 remains open/blocked
  for copied personal-book dogfood. No backend/frontend/config/write-mode code was changed; no tag,
  GitHub release, package, or release artifact was published; writes remain disabled by default;
  controlled writes remain post-MVP/experimental; no real/private financial data, GnuCash books,
  `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, or keys were committed; no
  v0.2 work was started.

- Phase 100 completed a non-publishing synthetic/disposable install smoke on current `main`:
  `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md` records branch/HEAD, tag/release
  absence, synthetic fixture source, Docker Compose config validation, local Docker startup with
  `GNUCASH_WRITES_ENABLED=false`, and read-only API smoke coverage for health, login/auth,
  books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and
  disabled validate/create/patch write probes. The phase also fixed narrow smoke-tooling drift so
  `scripts/smoke/read-only-api-smoke.py --help` is non-mutating and added
  transaction-detail/CSV-export checks to the existing smoke script. A true upgrade from
  `v0.1.1-readonly` was not feasible because no such tag/release exists and publication remains
  unauthorized. GitHub #39 remains closed; GitHub #38 remains open/blocked for copied personal-book
  dogfood. No tag, GitHub release, package, or release artifact was published; writes remain
  disabled by default; controlled writes remain post-MVP/experimental; no real/private financial
  data, personal GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens,
  certs, keys, or private paths were committed; no v0.2 work was started.

- Phase 101 completed the copied personal-book dogfood rerun gate for GitHub #38 as an honest
  blocked result: `docs/dogfood/phase-101-personal-copied-book-results.md` records `BLOCKED — safe
  copied book path not provided`. No explicit safe copied GnuCash SQL book path was provided via
  controller/user context or `GNUCASH_DOGFOOD_BOOK_PATH`, no copy-confirmation flag was present, and
  no private directories were searched. Therefore the local copied-book dogfood smoke was not run
  and #38 remains open/blocked. Release-boundary and tooling checks passed: clean `main` starting
  state, no local `v0.1.1-readonly` tag, no GitHub release named `v0.1.1-readonly`, Docker Compose
  config validation, smoke script help, and smoke script compile. No tag, GitHub release, package,
  GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private
  path, account name, transaction description, memo, amount, or real/private financial data was
  committed; writes remain disabled by default; controlled writes remain post-MVP/experimental; no
  personal-book dogfood success is claimed; no v0.2 work was started.

- Phase 102 completed the compatibility fixture/version matrix v3 safe provenance refresh for GitHub
  #22 without a real Desktop-generated fixture: `gnucash --version` is unavailable in this
  environment, so no broad GnuCash Desktop version compatibility row is claimed. The
  generated/disposable compatibility path was improved instead:
  `collect_gnucash_compatibility_metadata.py` and `create_compatibility_fixture_v1.py` now record
  safe runtime provenance (collector/generator version, OS, Python, SQLite, and piecash versions),
  and regression tests prove the copied-book collector still redacts private paths and does not
  serialize account names or transaction descriptions. `docs/gnucash-compatibility.md`,
  `docs/gnucash-version-fixture-plan.md`, and `docs/gnucash-compatibility-fixture-v1.md` document
  the narrow Phase 102 evidence and remaining gap. GitHub #22 was updated and left open for future
  real GnuCash Desktop/generated version coverage. No tag, GitHub release, package, GnuCash book,
  app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account
  name, transaction description, memo, amount, or real/private financial data was committed; writes
  remain disabled by default; controlled writes remain post-MVP/experimental; no v0.2 work was
  started.

- Phase 103 completed a narrow read-only transaction date-range preset UX slice from GitHub #11: the
  transactions page now exposes accessible preset links for `This month`, `Last month`, `Year to
  date`, and `Clear dates`; presets populate only the existing `date_from`/`date_to` query
  parameters, preserve search/account/amount filters, reset offset to the first page, and keep the
  existing custom date inputs visible. Active filter summary and CSV export parity remain on the
  same read-only filter contract, and frontend route/static checks cover preset labels, preset URL
  construction, custom date inputs, and CSV filter preservation. GitHub #11 was updated with
  evidence and left open for broader future read-only search/filter improvements. No backend write
  path was changed, no tag, GitHub release, package, GnuCash book, app DB, backup, `.env`,
  screenshot, CSV export, secret, token, cert, key, private path, account name, transaction
  description, memo, amount, or real/private financial data was committed; writes remain disabled by
  default; controlled writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 104 completed a narrow read-only transaction query semantics slice from GitHub #11: the
  existing `query` filter now matches transaction descriptions and split memo fields
  case-insensitively through the shared GnuCash service-layer matcher used by transaction lists,
  count/pagination totals, account transaction lists, and CSV export. Regression coverage proves
  memo-only query matches return the expected transaction, counts stay consistent, CSV export
  includes memo-matched transactions with corrected metadata headers, description-only search still
  works, and unmatched queries return no results. Frontend search helper copy now states
  `Description or split memo...`; active filter summary and CSV export parity remain on the existing
  `query` contract with no browser storage or new search parameter. GitHub #11 was updated with
  evidence and left open for remaining read-only search/filter enhancements such as transaction
  state filters, saved presets, and broader notes/full-text semantics. No backend write path was
  changed, no tag, GitHub release, package, GnuCash book, app DB, backup, `.env`, screenshot, CSV
  export, secret, token, cert, key, private path, account name, transaction description, memo,
  amount, or real/private financial data was committed; writes remain disabled by default;
  controlled writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 106 completed a narrow read-only transaction state/reconciliation filter slice from GitHub
  #11: transaction list, count/pagination, account-scoped transaction lists, and CSV export now
  accept the shared `transaction_state` query parameter with supported values `unreconciled`,
  `cleared`, `reconciled`, and `voided`, mapped to confirmed GnuCash split `reconcile_state` values
  `n`, `c`, `y`, and `v`. Unsupported values fail fast with HTTP 400 before opening/querying the
  book. The web transaction filters now expose a state dropdown, active-filter summary, and
  URL/export preservation for the new parameter, while `docs/transactions-filters.md` documents the
  read-only split-state semantics. Backend and frontend regression coverage proves
  list/count/account-scope/CSV parity and disabled-write safety. GitHub #11 remains open for
  remaining filter/preset scope. No backend write path was changed, no tag, GitHub release, package,
  GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private
  path, account name, transaction description, memo, amount, or personal financial data was
  committed; writes remain disabled by default; controlled writes remain post-MVP/experimental; no
  v0.2 work was started.

- Phase 107 completed a narrow read-only transaction filter URL/reset UX slice from GitHub #11: the
  transactions page now exposes an explicit URL-based `Clear filters` link that removes search,
  account, date, amount, and state filters while resetting to `offset=0`, date preset URL
  construction is pinned to preserve `query`, `account_id`, `min_amount`, `max_amount`, and
  `transaction_state`, pagination still preserves active filters, and CSV export keeps the same
  active filter query string without pagination parameters. `docs/transactions-filters.md` now
  documents URL-only presets/reset behavior and states that transaction search strings, account IDs,
  amount ranges, dates, and state filters are not saved in localStorage/sessionStorage, app
  metadata, or user profiles. Frontend route/static checks cover Clear filters, date preset
  preservation, CSV parity, and browser-storage restrictions; backend disabled-write regression and
  full API tests passed. GitHub #11 was updated with evidence and remains open for remaining
  read-only search/filter scope. No backend write path was changed, no tag, GitHub release, package,
  GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private
  path, account name, transaction description, memo, amount, or personal financial data was
  committed; writes remain disabled by default; controlled writes remain post-MVP/experimental; no
  v0.2 work was started.

- Phase 108 completed account detail transaction filter/export parity from GitHub #11: the account
  detail page now reuses the approved read-only transaction filters for its fixed account scope,
  supports search, date presets/custom dates, amount range, and split reconciliation state filters,
  preserves those filters through pagination, shows filtered counts and a clear empty-state
  explanation, and exports the same account-scoped filtered view through the existing CSV export
  endpoint with a fixed `account_id`. `TransactionFilters` now supports a locked account scope so
  account detail cannot accidentally switch or leak to another account. Backend regression coverage
  proves combined account-scoped filters keep count/list parity and do not return matches from other
  accounts; frontend route/static checks pin account detail URL/export/filter behavior. GitHub #11
  was updated with evidence and remains open for remaining roadmap search/filter scope. No backend
  write path was changed, no tag, release, package, GnuCash book, app DB, backup, `.env`,
  screenshot, CSV export, secret, token, cert, key, private path, account name, transaction
  description, memo, amount, or personal financial data was committed; writes remain disabled by
  default; controlled writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 109 completed scheduled/recurring transaction read-only awareness from GitHub #12: the
  backend now exposes `GET /scheduled-transactions` and `GET
  /books/{book_id}/scheduled-transactions` for safe scheduled transaction summary metadata through
  the authenticated book-aware API context, and the web app now has a protected `/scheduled` page
  for the active accessible book. The implementation intentionally shows only
  id/name/enabled/date/count/auto-create/auto-notify/advance-day/template-presence/recurrence
  metadata and does not expose template split details, raw SQL, account names, memos, descriptions,
  amounts, private paths, or fake next-run predictions. `docs/scheduled-transactions.md` documents
  the unsupported/editor boundary and GnuCash Desktop remains the authoritative
  scheduled-transaction editor. GitHub #12 was updated with evidence and remains open only if future
  scope requires richer verified schedule calculations/editor-adjacent UX. No backend write path was
  changed, no tag, release, package, GnuCash book, app DB, backup, `.env`, screenshot, CSV export,
  secret, token, cert, key, private path, account name, transaction description, memo, amount, or
  personal financial data was committed; writes remain disabled by default; controlled writes remain
  post-MVP/experimental; no v0.2 work was started.

- Phase 110 completed books metadata UX hardening from GitHub #13: `GET /books` and `GET
  /books/{book_id}` now include explicit app-metadata-only `access_role`, `read_only`, `status`, and
  empty `management_actions` fields for visible books without opening GnuCash data. The `/books`
  page now renders access role/status/read-only metadata, stronger no-management-action copy,
  empty/inaccessible guidance, and safe links that verify the selected book against the
  authenticated accessible list before setting the existing non-secret selected-book cookie and
  redirecting only to read-only views (`/dashboard`, `/accounts`, `/transactions`, `/scheduled`).
  Regression coverage confirms archived and unauthorized books stay hidden/blocked. GitHub #13 was
  updated with evidence and remains open for future admin-only
  registration/default/deletion-from-registry workflows. No backend write path was changed, no
  upload/delete/registry-edit/default-changing UI was added, no tag, release, package, GnuCash book,
  app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account
  name, transaction description, memo, amount, or personal financial data was committed; writes
  remain disabled by default; controlled writes remain post-MVP/experimental; no v0.2 work was
  started.

- Phase 111 completed compatibility fixture v4 safe Desktop-tooling evidence from GitHub #22: the
  local environment was probed with `apps/api/scripts/probe_gnucash_desktop_tooling.py`, which
  records only `gnucash`/`gnucash-cli` command availability and bounded `--version` output while
  redacting executable paths, opening no books, and searching no private directories. The local
  result was `desktop_tooling_available=false` (`gnucash` and `gnucash-cli` not found), so no
  Desktop-generated fixture or broad Desktop-version matrix row is claimed. Compatibility docs now
  distinguish generated/piecash fixture evidence, copied/disposable metadata evidence, and absent
  Desktop tooling; regression tests cover safe probe metadata and existing fixture no-mutation
  coverage. GitHub #22 was updated with evidence and remains open for future real Desktop-generated
  synthetic SQLite fixture coverage. No tag, release, package, GnuCash book, app DB, backup, `.env`,
  screenshot, CSV export, secret, token, cert, key, private path, account name, transaction
  description, memo, amount, or personal financial data was committed; writes remain disabled by
  default; controlled writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 112 completed LAN/VPN deployment safety behavior from GitHub #26: backend health/startup
  diagnostics now include a safe CORS deployment posture check, and startup logs emit a non-secret
  `cors_deployment_warning` when `CORS_ORIGINS` contains `*` while `APP_ENV` is not
  development-like. Local development/test defaults remain usable, `.env.example` and
  deployment/development docs now provide exact localhost/LAN/VPN origin examples, and the docs
  continue to warn that CORS narrowing is not production hardening and the pre-alpha app must not be
  exposed directly to the public internet. Regression tests cover risky wildcard warnings,
  narrowed-origin behavior, and log redaction. GitHub #26 was updated with evidence and closed. No
  tag, release, package, GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret,
  token, cert, key, private path, account name, transaction description, memo, amount, or personal
  financial data was committed; writes remain disabled by default; controlled writes remain
  post-MVP/experimental; no v0.2 work was started.

- Phase 113 completed the Russian localization glossary and narrow transaction filter/export UI
  slice from GitHub #17/#29: `docs/localization.md` now includes an accounting/safety glossary with
  canonical English and preferred Russian terms for read-only boundaries, GnuCash Desktop authority,
  production/security caveats, split reconciliation states, CSV export, and partial translation. The
  transaction filter component and transaction/account CSV export copy now use the existing
  English/Russian message catalog for filter headings/help, active filter summaries, state labels,
  clear/reset, and export helper/button copy. English remains canonical, Russian remains
  opt-in/partial, URL-only filter behavior is unchanged, and no browser storage or write-mode
  behavior was added. No tag, release, package, GnuCash book, app DB, backup, `.env`, screenshot,
  CSV export, secret, token, cert, key, private path, account name, transaction description, memo,
  amount, or personal financial data was committed; writes remain disabled by default; controlled
  writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 114 completed a synthetic browser dogfood refresh after the recent read-only
  UX/filter/books/scheduled/localization changes: Docker/Caddy was run locally with
  `GNUCASH_WRITES_ENABLED=false` against a synthetic/disposable fixture copied into ignored runtime
  data, `scripts/smoke/read-only-api-smoke.py` passed core API/CSV/disabled-write checks, and the
  new durable `scripts/smoke/read-only-browser-dogfood.py` drove headless Chromium through login,
  protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters,
  transaction detail, and authenticated CSV export route checks. Evidence is documented in
  `docs/dogfood/phase-114-synthetic-browser-dogfood.md`; no screenshots, raw CSV exports, app DBs,
  GnuCash books, backups, `.env`, secrets, tokens, certs, keys, private paths, or real/private
  financial data were committed. This is synthetic/disposable dogfood only; GitHub #38 remains
  open/blocked for personal copied-book dogfood until Val provides a safe copied SQL book path
  outside git.

- Phase 115 completed conservative `v0.1.2-readonly` maintenance release prep without publication:
  `docs/release/v0.1.2-readonly-notes.md`, `docs/release/v0.1.2-readonly-checklist.md`, and
  `docs/release/v0.1.2-readonly-final-gate.md` summarize Phases 106–114 and record the verdict
  `Ready for later authorized publish phase`. Full backend tests, frontend check/auth-routes/build,
  Docker Compose config validation, GitHub Actions state check, tag/release absence checks, and
  sensitive tracked-file scan passed. No tag, GitHub release, package, GnuCash book, app DB, backup,
  `.env`, screenshot, CSV export, secret, token, cert, key, private path, or real/private financial
  data was committed; writes remain disabled by default; no v0.2 work was started; publication still
  requires separate explicit Val authorization.

- Phase 116 completed GitHub #38 copied personal-book dogfood with Val's provided safe copied
  archive: the archive was unpacked only to private temporary storage outside git, mounted read-only
  into local Docker/Caddy with `GNUCASH_WRITES_ENABLED=false`, and verified through API and headless
  browser dogfood. `/api/health`, login, dashboard, accounts, account detail, transactions,
  transaction detail, filters, CSV export, hidden write UI, and disabled write endpoints all passed;
  redacted evidence is documented in `docs/dogfood/phase-116-personal-book-dogfood.md`. GitHub #38
  was closed after redacted evidence. No tag, release, package, GnuCash book, source zip, app DB,
  backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name,
  transaction description, memo, amount, or real/private financial data was committed; writes remain
  disabled by default; no v0.2 work was started.

- Phase 117 publishes `v0.1.2-readonly` as the next read-only maintenance pre-release after the
  Phase 116/#38 PASS. The release executor re-checked clean tree, `HEAD == origin/main`, issue #38
  closed, tag/release absence, recent GitHub Actions success, Docker Compose config validity, diff
  whitespace, and sensitive tracked-file hygiene before committing release/status documentation,
  pushing `main`, creating the annotated tag, pushing the tag, and creating the GitHub pre-release
  from `docs/release/v0.1.2-readonly-notes.md`. No packages, GnuCash books, source zip, app DB,
  backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name,
  transaction description, memo, amount, or real/private financial data were committed;
  `GNUCASH_WRITES_ENABLED=false` remains default; no v0.2 work was started.

- Phase 118 completed a narrow frontend CSS/static-regression fix for desktop transaction table
  sizing: `TransactionTable.svelte` now uses a fixed full-width desktop table with predictable
  Date/Description/Account/Counter account/Amount column widths, no desktop
  `overflow-x-auto`/`min-w-full` horizontal shifting, and safe truncation/title text for long
  descriptions and account names while preserving separate mobile card behavior. The account tree
  desktop grid was also narrowed to shrink safely with `minmax(0,1fr)` and truncating account-name
  cells. Static frontend route checks pin the table/account-tree sizing contract. No
  API/data/schema/write behavior changed, no release/tag/package was published, and
  `GNUCASH_WRITES_ENABLED=false` remains default.

- Phase 119 completed a narrow read-only account display cleanup: backend `account_full_name()` now
  omits the synthetic GnuCash ROOT account named `Root Account` from colon-separated paths while
  preserving the child account path and existing IDs/parent references/API shape. Account tree,
  transaction list/detail split names, counter account names, account detail labels,
  expenses-by-account reports, and CSV/account fields continue to consume the same cleaned
  `full_name`/`account_name`/`counter_account_name` strings. Backend regression and fixture tests
  were updated so expected values are `Assets:Bank:Checking`, `Expenses:Food`, etc. rather than
  `Root Account:...`. No write path, schema, DTO, frontend auth/storage, release/tag/package,
  private data, or `GNUCASH_WRITES_ENABLED=false` default changed.

- Phase 120 completed a read-only account-detail performance optimization: account-scoped
  transaction list/count now uses a scoped piecash SQLAlchemy transaction candidate query through
  `splits.account_guid` instead of iterating the full book transaction collection when `account_id`
  is present, while preserving existing query/date/amount/state/pagination and CSV export semantics.
  Regression coverage proves the account-scoped service path does not touch `book.transactions`,
  unknown account scope still returns empty results, and the benchmark plan now includes account
  filtered list plus account CSV export evidence. Synthetic 1,000-transaction benchmark evidence is
  documented in `docs/performance/phase-120-account-detail-benchmark.md`: account detail page
  medians were about 292–297 ms locally versus historical Phase 88 medians above one second, and
  account-scoped CSV returned `csv_total=961` with matching body rows. This is bounded local
  synthetic evidence only, not a production scalability claim. No global dashboard/list
  optimization, cache layer, API contract change, write path, release/tag/package, private data, or
  `GNUCASH_WRITES_ENABLED=false` default changed.

- Phase 121 fixed the Conservative dashboard summary zero-value fallback bug for books/fixtures
  where base-currency transactions exist but account balance fields report zero.
  `get_report_summary()` still prefers existing account-balance totals when available, but now also
  accumulates base-currency asset/liability split totals through the requested `as_of_date` and
  falls back to those split-derived totals only when both account-balance asset/liability totals are
  zero and relevant base-currency balance splits exist. Month-to-date income/expense handling
  remains Decimal/string-only and base-currency-only; legitimate empty-book zero summaries remain
  zero; no currency conversion, float money handling, frontend display workaround, write path,
  release/tag/package, private data, or `GNUCASH_WRITES_ENABLED=false` default changed. Regression
  coverage uses synthetic current-period/base-currency transactions with known non-zero assets,
  liabilities, net worth, income, and expenses.

- Phase 122 completed a read-only stability gate and prepared unpublished `v0.1.3-readonly`
  maintenance release artifacts after Phases 118–121: `docs/release/v0.1.3-readonly-notes.md`,
  `docs/release/v0.1.3-readonly-checklist.md`, and `docs/release/v0.1.3-readonly-final-gate.md`.
  Full backend tests, frontend check/auth-routes/build, Docker Compose config validation, GitHub
  Actions state check, tag/release absence checks for `v0.1.3-readonly`, `git diff --check`, and a
  sensitive tracked-file hygiene scan were run for the gate. The candidate remains unpublished and
  pending explicit authorization; no tag, GitHub release, package, GnuCash book, app DB, backup,
  `.env`, screenshot, CSV export, secret, token, cert, key, private path, real/private financial
  data, write-mode behavior, or `GNUCASH_WRITES_ENABLED=false` default changed.

- Phase 123 started the post-MVP/write-alpha safety foundation without enabling writes by default:
  backend regression coverage now proves default write-disabled configuration in `Settings`,
  `.env.example`, and Docker Compose; disabled validate/create/patch routes return 403 before
  resolving books or constructing a write service; write-lock failures after entering the create
  route are audited as failed attempts with no backup path; and service validation explicitly covers
  split count, zero-sum, invalid decimal, missing account, invalid date, and placeholder-account
  rejection. `docs/v0.2-controlled-writes.md` now records a Phase 123 readiness gate snapshot and
  remaining BLOCKED gaps before any real-user write enablement. No frontend/write UI was touched, no
  write feature was enabled or broadened, no release/tag/package was published, no real/private data
  was committed, and `GNUCASH_WRITES_ENABLED=false` remains the default.

- Phase 124 hardened the first write-alpha controlled transaction create safety flow without default
  enablement: enabled write routes are now additionally limited to `APP_ENV=test` copied/disposable
  fixture scope, so a casual `GNUCASH_WRITES_ENABLED=true` flip in normal development/runtime
  returns 403 before constructing the write service. Backend route-level integration coverage now
  exercises an enabled create against a copied synthetic GnuCash SQLite fixture and verifies
  book-state read-back, backup creation, audit success payload, released write lock, and validation
  failure with failed audit/no backup/no lock leak. `docs/v0.2-controlled-writes.md` labels the
  Phase 124 create path as test-environment-only write-alpha evidence. No
  edit/delete/import/scheduled/account-write capability was added, no frontend write UI was touched,
  no release/tag/package was published, no real/private data was committed, and
  `GNUCASH_WRITES_ENABLED=false` remains the default.

- Phase 128 expanded write-alpha create-route safety evidence without default enablement:
  route-level tests use only copied/disposable `tmp_path` fixtures to cover two parallel POST
  creates with one success and one lock-contention failure, synthetic post-backup write failure with
  released lock, failed audit row, intact backup, and no book mutation, plus read-only/viewer access
  rejection before write-service construction. The file-based write lock now rejects same-process
  re-entrant acquisition for the same book key. `docs/v0.2-controlled-writes.md` records the updated
  create-only readiness snapshot. No PATCH/DELETE/import/scheduled/account write expansion, frontend
  write UI, release/tag/package publication, real/private data use, `GNUCASH_WRITES_ENABLED=false`
  default change, or `APP_ENV=test` gate weakening occurred.

Next planned phase:

- Continue only with the next explicitly requested phase. Controlled writes remain
  post-MVP/experimental, disabled by default, constrained to `APP_ENV=test` copied/disposable
  fixtures when explicitly enabled, and not safe for production/private/only-copy books. Phase 197
  produced blocker evidence only for GitHub #22: no Desktop-generated synthetic fixture exists yet,
  and no broad Desktop/version/backend compatibility claim should be made until an isolated
  disposable GUI/manual-safe Desktop fixture is created, redacted, and read-only-smoked.

## MVP product model

MVP v0.1:

- one installation
- one local admin user
- one default GnuCash book
- read-only access to GnuCash data

Future:

- one installation
- multiple users
- multiple independent books
- users can access only assigned books

Advanced future:

- shared editing of one book only as serialized/locked mode
- no real-time collaborative editing

Important positioning:

- Not a family-wallet baseline.
- Not collaborative accounting on top of GnuCash.
- A GnuCash book is treated as a monopolistic accounting ledger.
- Multi-user expansion is primarily through multiple independent books.

## Phase 15 — Public pre-alpha release readiness

Status: complete. Phase commit pushed and `v0.0.1-prealpha` tag pushed.

Release candidate: `v0.0.1-prealpha`.

GitHub issues:

- `gh` is installed in `~/.local/bin/gh` and authenticated for `valentusys`.
- GitHub labels and milestones were created from `docs/github/`.
- GitHub issues #1–#10 were created from `docs/github/issues/`.
- Issues #1, #2, and #4 were closed as completed by Phase 17 / release automation.

Release:

- `v0.0.1-prealpha` tag was pushed with git.
- GitHub pre-release was created with `gh`.
- Release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.0.1-prealpha
- Automation notes are in `docs/github/manual-release-instructions.md`.

Artifacts:

- `docs/v0.2-controlled-writes.md`
- `docs/release/v0.0.1-prealpha-checklist.md`
- `docs/release/v0.0.1-prealpha-notes.md`
- `docs/github/labels-to-create.md`
- `docs/github/milestones-to-create.md`
- `docs/github/issues/*.md`
- `docs/github/manual-release-instructions.md`
- `docs/handoff/phase-15.md`

## Phase 16 — Project Lead subagent profile

Status: complete. Phase commit pushed.

Created:

- `docs/agents/project-lead.md` — durable Project Lead / Руководитель проекта profile for future
  Hermes subagent use.
- Hermes skill `gnucash-web-companion-project-lead` — reusable project lead context for future
  sessions.

Purpose:

- plan phases
- review scope and safety boundaries
- manage release/backlog guidance
- prevent product drift away from read-only MVP positioning
- keep controlled writes post-MVP and disabled by default

The Project Lead is not a coding implementer and should not spawn further subagents.

## Phase 17 — Synthetic GnuCash Fixture and Read-Only Integration Validation

Status: complete. Phase commit pushed.

Goal: create a disposable synthetic GnuCash SQLite fixture using piecash and validate the read-only
service layer against it with real integration tests.

Artifacts:

- `apps/api/scripts/create_test_fixture.py` — standalone script that generates the synthetic
  fixture.
- `apps/api/tests/fixtures/test-book.gnucash.sqlite` — 208 KB synthetic GnuCash book (9 user
  accounts + 1 ROOT, 5 transactions, SEK).
- `apps/api/tests/test_integration_fixture.py` — 19 integration tests validating the full read-only
  path.
- `apps/api/tests/test_gnucash_book.py` — replaced placeholder skipped test with fixture existence
  check.

Test results: 187 passed (167 existing + 19 new integration + 1 updated), 0 failed.

Deviation from spec: the spec assumed 9 accounts (1 ROOT + 8 children) but piecash `book.accounts`
returns 10 non-ROOT accounts (ROOT is only in `book.root_account`). The service layer returns 10
accounts. Tests assert `account_count == 10`. The account tree has 4 top-level nodes (ROOT is not in
`_accounts()` so its children become roots).

## Phase 18 — README Screenshots and Mobile Preview with Synthetic Data

Status: complete. Phase commit pushed.

Goal: add visual proof of the current UI to the README using only synthetic fixture data.

Artifacts:

- `docs/images/` — 7 screenshot files (login, dashboard desktop/mobile, accounts tree, transactions
  list, transaction detail, dark mode). Total ~453 KB.
- `README.md` — updated with `## Screenshots` section containing all 7 images via relative paths.

Screenshots: login (20 KB), dashboard-desktop (85 KB), dashboard-mobile (35 KB), accounts-tree (91
KB), transactions-list (96 KB), transaction-detail (42 KB), dark-mode (85 KB).

Deviations: transaction detail used GUID-based URL (`/transactions/89bdbe5a...`) instead of
`/transactions/1` since the synthetic fixture uses GUIDs. Used Chromium headless with CDP via Python
instead of `browser_vision` tool (display not available). Used form-based login via CDP instead of
cookie injection.

Verification: all 7 screenshots < 300 KB, no real financial data, no production code changes, README
renders images with relative paths.

Related issue: GitHub #3.

## Phase 19 — Multi-Currency Limitation Tests and Auth Cookie Security Documentation

Status: complete. Phase commit pushed.

Goal: add mixed-currency integration tests and document auth cookie security for self-hosted
deployment.

Artifacts:

- `apps/api/scripts/create_multicurrency_fixture.py` — script to generate the multi-currency
  fixture.
- `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite` — 208 KB synthetic book (13
  accounts: 10 SEK + 3 EUR; 6 transactions: 5 SEK + 1 EUR).
- `apps/api/tests/test_multicurrency_reports.py` — 11 integration tests validating multi-currency
  exclusion.
- `docs/security/auth-cookie-deployment.md` — cookie attributes, deployment warnings, no production
  guarantee.
- `README.md` — new `## Security and Deployment` section with link to the doc.

Test results: 198 passed (187 existing + 11 new), 0 failed.

Related issues: GitHub #6, GitHub #10.

## Phase 20 — Multi-Book UI Foundation

Status: complete. Phase commit pushed locally (gh auth invalid, push skipped).

Goal: add a minimal book switcher to the frontend and wire it to existing GET /books API, migrating
page-level data loads from default-book alias routes to explicit book-aware routes.

Artifacts:

- `apps/web/src/lib/components/BookSwitcher.svelte` — new component, dropdown for multi-book, plain
  text for single-book.
- `apps/web/src/lib/api/server.ts` — added `getActiveBookId(cookies)` helper.
- `apps/web/src/routes/+layout.server.ts` — fetches books, resolves active book from
  cookie/default/first.
- `apps/web/src/routes/+layout.svelte` — passes book context to nav components.
- `apps/web/src/lib/components/DesktopNav.svelte` — integrated BookSwitcher.
- `apps/web/src/lib/components/MobileNav.svelte` — integrated BookSwitcher.
- `apps/web/src/routes/dashboard/+page.server.ts` — book-aware report routes.
- `apps/web/src/routes/accounts/+page.server.ts` — book-aware account tree route.
- `apps/web/src/routes/accounts/[id]/+page.server.ts` — book-aware account detail + transactions
  routes.
- `apps/web/src/routes/transactions/+page.server.ts` — book-aware transaction list + accounts
  routes.
- `apps/web/src/routes/transactions/[id]/+page.server.ts` — book-aware transaction detail route.
- `apps/api/tests/test_multi_book_access.py` — 8 new tests for multi-book access filtering.

Test results: 207 passed (199 + 8 new), 1 pre-existing failure (test_gnucash_book.py relative path).
Frontend: check 0 errors, build success, auth-routes passed.

Deviations: page-level loads no longer return books/activeBook/showBookSelector (layout provides
them instead). `getActiveBookId()` validates cookie value as positive integer.

Related issues: GitHub #5.

## Phase 21 — File-Based Write Lock Replacement

Status: complete. Phase commit pushed.

Goal: replace in-process `threading.Lock`-based write lock with `fcntl.flock()`-based file locking
for multi-worker safety.

Artifacts:

- `apps/api/app/services/write_lock.py` — rewritten to use `fcntl.flock()` on per-book lock files
  under `/data/locks/`. Book IDs are sanitized (path separators → underscores) to produce flat
  filenames.
- `apps/api/tests/test_write_lock.py` — 10 new tests covering acquire/release, non-blocking
  behavior, context manager (normal + exception), independent books, lock file creation, idempotent
  release, blocking acquire, and auto-creation of nested lock directories.
- `apps/api/tests/test_transaction_writes.py` — updated old `TestWriteLockService` tests to use
  `tmp_path`-based lock directories; patched singleton in `test_create_endpoint_exists` to use a
  tmp-based file lock service.

Test results: 218 passed (208 existing + 10 new), 0 failed. Frontend: check 0 errors, build success,
auth-routes passed. Docker config valid.

Deviation from spec: added book_id sanitization in `_lock_path()` to handle absolute paths and URIs
(which contain `/` and `:` characters) by replacing them with underscores. This prevents path
traversal when `book_key` is a filesystem path like `/data/books/test.gnucash.sqlite`.

Related issues: GitHub #7 (closed).

## Phase 23 — Backup Restore Smoke Test

Status: complete. Phase commit pushed.

Goal: add automated tests verifying backups created before write operations can be restored,
confirming original GnuCash book state is fully recoverable.

Artifacts:

- `apps/api/tests/test_backup_restore.py` — 6 integration tests across 2 test classes covering
  backup file validity, backup pre-write state, restore undoes write (transaction count), restore
  preserves account count, restore preserves original transaction data, and original fixture
  immutability.

Test results: 254 passed (248 existing + 6 new), 0 failed. Frontend: check 0 errors, build success,
auth-routes passed. Docker config valid.

Deviations: 6 tests implemented vs 4 minimum. Added
`test_restore_preserves_original_transaction_data` and `test_original_fixture_never_modified` for
stronger safety coverage.

Production code changes: none. Zero production code changes; restore is `shutil.copy2` overwrite
matching the production backup model.

Related issues: GitHub #9 (closed).

## Phase 24 — CSV Export for Transactions

Status: complete. Phase commit pushed.

Goal: add read-only CSV export endpoint to backend and export button to frontend transactions page.

Artifacts:

- `apps/api/app/routers/transactions.py` — added `GET /books/{book_id}/transactions/export` endpoint
  (read-only, book-aware, respects all list filters, 10,000 row cap).
- `apps/api/tests/test_transaction_export.py` — 8 backend tests covering auth requirement, CSV
  headers, transaction data, date filter, account filter, query filter, access denial, and
  Content-Disposition filename.
- `apps/web/src/routes/transactions/+page.svelte` — added «Экспорт CSV» button that preserves
  current filters (query, date_from, date_to, account_id) in the export URL.
- `docs/handoff/phase-24.md` — handoff document.

Test results: 262 passed (254 existing + 8 new), 0 failed. Frontend: check 0 errors, build success,
auth-routes passed. Docker config valid.

Deviations: 8 tests implemented vs 7 minimum. Export endpoint placed before `{transaction_id}` route
to avoid path collision (`/export` would match as `transaction_id="export"`). No new dependencies
required (uses stdlib `csv` + `io`).

Production code changes: read-only only. Zero write-path changes. No new dependencies.

Related issues: none.

## Phase 25 — Documentation, Release, and Roadmap Sync

Status: complete. Phase commits pushed: `bbd1c8b`, `fa328d6`.

Goal: sync public docs, changelog, controlled-write notes, release candidate notes, and backlog
after Phases 17–24 without creating a tag or release.

Artifacts:

- `README.md` — updated current status and release-candidate links for `v0.0.2-prealpha`.
- `CHANGELOG.md` — added Unreleased entries for Phases 17–24.
- `docs/v0.2-controlled-writes.md` — updated completed and pending write-safety checklist items.
- `docs/release/v0.0.2-prealpha-notes.md` — created candidate notes only; no tag/release published.
- `docs/handoff/phase-25.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issues opened after Phase 25 / audit: GitHub #16, GitHub #17.

## Phase 26 — Audit-Driven Status Sync

Status: complete. Phase commit pushed.

Goal: fix audit-identified status/release documentation drift without changing product code or
publishing tags/releases.

Artifacts:

- `docs/audits/2026-05-17-audit.md` — independent audit report.
- `README.md` — advanced current status to Phase 0–25 and clarified `v0.0.1-prealpha` vs
  `v0.0.2-prealpha` candidate state.
- `PROJECT_STATUS.md` — advanced status baseline through Phase 25.
- `docs/agents/project-lead.md` — removed stale GitHub auth blocker and marked old Phase 18
  recommendation as historical.
- `docs/handoff/phase-26.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issues: GitHub #16, GitHub #17.

## Phase 27 — Discoverability and Community Announcement Readiness

Status: complete. Phase commit pushed.

Goal: complete the non-blocking discoverability work before wider announcement while preserving
pre-alpha/read-only positioning.

Artifacts:

- `README.md` — added short pitch, “Who this is for / not for”, comparison with `gnucash-web`,
  GnuDash, and Fava/Beancount, and community draft links.
- `docs/community/announcement-draft.md` — conservative announcement draft with safety warnings.
- `docs/community/social-preview.md` — manual GitHub social preview setup and safety checklist.
- GitHub topics configured: `gnucash`, `personal-finance`, `accounting`, `self-hosted`, `sveltekit`,
  `fastapi`, `open-source`, `finance`, `sqlite`.
- `docs/handoff/phase-27.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issue: GitHub #16.

## Phase 28 — GnuCash Compatibility Matrix

Status: complete. Phase commit pushed.

Goal: document and test the current GnuCash SQL fixture compatibility baseline without claiming
broad version support.

Artifacts:

- `docs/gnucash-compatibility.md` — compatibility matrix for committed synthetic fixtures, untested
  backends, user guidance, and future compatibility work.
- `apps/api/tests/test_gnucash_compatibility.py` — tests verifying fixture `versions` table markers
  and doc coverage.
- `README.md` — link to compatibility/safety docs.
- `docs/handoff/phase-28.md` — handoff document.

Test results: 264 passed, frontend check/auth-routes/build OK, Docker config validation OK.

Related issue: GitHub #15.

## Phase 29 — Audit-Driven Release Documentation Sync

Status: complete. Phase commit pushed.

Goal: run the required independent audit before Phase 29 and fix accepted release/status
documentation blockers instead of expanding feature scope.

Artifacts:

- `docs/audits/2026-05-17-audit.md` — refreshed independent audit report for Phase 29.
- `README.md` — current status advanced through Phase 29 and linked to the latest audit.
- `CHANGELOG.md` — Unreleased entries updated through Phase 29.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated for Phases 25–29 and current
  compatibility limits.
- `docs/ROADMAP.md` — roadmap refreshed so `v0.0.1-prealpha` is no longer described as the next
  unpublished step.
- `docs/handoff/phase-28.md` — replaced stale pending commit placeholder with `343e098`.
- `docs/handoff/phase-29.md` — handoff document.

Test results: backend 264 passed (27 warnings), frontend check/auth-routes/build OK, Docker config
validation OK.

Related issues: none created; audit blocker was fixed immediately in Phase 29.

## Phase 30 — Transaction Amount Range Filters for CSV Export

Status: complete. Phase commit pushed.

Goal: expose read-only transaction amount range filters in the frontend and preserve them in CSV
export URLs.

Artifacts:

- `apps/web/src/lib/components/TransactionFilters.svelte` — added `min_amount` and `max_amount`
  controls with client-side min/max validation.
- `apps/web/src/routes/transactions/+page.server.ts` — passes amount range filters to the backend
  list endpoint and page data.
- `apps/web/src/routes/transactions/+page.svelte` — preserves amount filters across
  pagination/export and shows active filter count on the CSV export button.
- `apps/api/app/routers/transactions.py` — rejects inverted amount ranges before querying GnuCash.
- `apps/api/tests/test_transaction_export.py` — added export amount range and inverted-range tests.
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/release/v0.0.2-prealpha-notes.md`, and
  `docs/handoff/phase-30.md` — status/release docs updated.

Test results: backend full suite, frontend check/auth-routes/build, and Docker config validation all
passed.

Related issue: GitHub #14.

## Phase 31 — Read-Only Safety Status Banner

Status: complete. Phase commit pushed.

Goal: add a small global UI reminder that the MVP is read-only by default and that GnuCash Desktop
remains the authoritative editor.

Artifacts:

- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte` — reusable authenticated-app banner with
  explicit read-only/default-write safety language.
- `apps/web/src/routes/+layout.svelte` — displays the banner in the authenticated app shell above
  page content.
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/release/v0.0.2-prealpha-notes.md`, and
  `docs/handoff/phase-31.md` — status/release docs updated.

Test results: backend full suite, frontend check/auth-routes/build, and Docker config validation all
passed.

Related issues: none; this completed a small release-readiness/read-only MVP polish item from the
roadmap.

## Phase 32 — Backend Write-Gating Regression Coverage

Status: complete. Phase commits pushed.

Goal: convert the Phase 1 background-mission ad-hoc write-gating audit into committed regression
tests for validate/create/patch controlled-write endpoints with writes disabled.

Artifacts:

- `docs/handoff/phase-32.md` — PM brief for the next engineer phase.
- `apps/api/tests/test_transaction_writes.py` — disabled-write regression coverage for
  validate/create/patch routes, including a guard that fails if `_write_service_for` is constructed
  while writes are disabled.
- `CHANGELOG.md` — Unreleased safety/testing entry for Phase 32.
- `docs/v0.2-controlled-writes.md` — documented that disabled-write bypass regression coverage
  exists while writes remain experimental and disabled by default.

Result: `Settings.gnucash_writes_enabled` remains `False` by default, all three controlled-write
routes return read-only 403 responses with writes disabled, and committed tests prove
`_write_service_for` / `GnuCashWriteService` is not constructed for those requests.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend
check/auth-routes/build passed; Docker config validation passed.

Related issue: GitHub #18 (write-gating verification follow-up; status managed by audit/release
triage).

## Phase 33 — Controlled-Writes Documentation Cleanup and Status Sync

Status: complete. Phase commit pushed.

Goal: clean stale controlled-writes documentation and synchronize the public status baseline after
disabled-write regression coverage without expanding controlled-write scope.

Artifacts:

- `docs/v0.2-controlled-writes.md` — replaced stale active legacy-lock wording with current
  `fcntl.flock()` file-locking status, documented Phase 23 restore smoke coverage and Phase 32
  disabled-write bypass regression coverage, and moved completed limitations into a resolved
  historical section.
- `README.md` — then-current status baseline advanced without claiming a `v0.0.2-prealpha`
  tag/release exists.
- `CHANGELOG.md` — added Phase 33 documentation/status cleanup entry.
- `docs/release/v0.0.2-prealpha-notes.md` and `docs/ROADMAP.md` — synchronized Phase 32 safety
  coverage and retained pre-alpha/read-only positioning.
- `docs/handoff/phase-33.md` — implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental/post-MVP and disabled by default; no product code or frontend auth
storage paths were changed; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #23 closed by Phase 33; GitHub #19 reopened by the phase 7 audit for
follow-up public status synchronization; GitHub #18 intentionally unchanged by this documentation
phase.

## Phase 34 — README/Public Status Baseline Sync After Phase 33 Audit Finding

Status: complete. Phase commit pushed.

Goal: synchronize public status/readiness documentation through the Phase 33 baseline after the
phase 7 audit reopened GitHub issue #19 for stale README wording.

Artifacts:

- `README.md` — current status advanced to the then-current Phase 33 baseline while retaining
  pre-alpha, not production-ready, not security-audited, read-only-by-default, and unpublished
  `v0.0.2-prealpha` language.
- `CHANGELOG.md` — added Phase 34 documentation/status sync entry.
- `docs/release/v0.0.2-prealpha-notes.md` — updated candidate scope from Phases 17–32 to Phases
  17–33 and added Phase 33 documentation cleanup note; no tag or release was published.
- `docs/ROADMAP.md` — release-governance grouping updated to include Phase 33/34 status baseline
  cleanup.
- `docs/handoff/phase-34.md` — engineer implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental/post-MVP and disabled by default; no product code or frontend auth
storage paths were changed; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #19 closed by Phase 34; GitHub #18, #20, #21, and #22 intentionally remain
open.

## Phase 35 — Audit-Driven Phase 34 Public Baseline and Controlled-Writes Docs Sync

Status: complete. Phase commit pushed.

Goal: resolve the accepted phase 10 audit documentation blockers by synchronizing public
current-status wording through the Phase 34/35 baseline and removing the stale controlled-writes
limitation that described frontend amount range filters as missing.

Artifacts:

- `README.md` — current status advanced so Phase 34 is no longer missing from the public baseline,
  while retaining pre-alpha, not production-ready, not security-audited, read-only-by-default, and
  unpublished `v0.0.2-prealpha` language.
- `docs/v0.2-controlled-writes.md` — updated known limitations to state that Phase 30 added frontend
  amount range filters for browsing and CSV export; moved that work into resolved historical
  limitations.
- `CHANGELOG.md` — added Phase 35 documentation/status sync and controlled-writes limitation cleanup
  entries.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated through Phase 35 without
  publishing a tag or GitHub release.
- `docs/ROADMAP.md` — release-governance grouping updated to include Phase 35 documentation cleanup.
- `docs/handoff/phase-35.md` — implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental/post-MVP and disabled by default; no code path or write-gating route
order was changed; no frontend auth storage path was changed; no real financial/secrets artifacts
were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #19 closed by Phase 35; GitHub #18, #20, #21, and #22 intentionally remain
open.

## Phase 36 — Write-Mode UI Warning and Explicit Confirmation

Status: complete. Phase commit pushed.

Goal: resolve GitHub #21 by adding explicit warning and acknowledgement coverage around the
experimental controlled-write UI without expanding write capabilities or changing backend
write-gating.

Artifacts:

- `apps/web/src/lib/components/WriteModeWarning.svelte` — prominent reusable warning that controlled
  writes are experimental post-MVP, disabled by default, for disposable/test copies with backups
  only, and subordinate to GnuCash Desktop.
- `apps/web/src/routes/transactions/+page.svelte` — enabled write entry point remains hidden unless
  frontend `GNUCASH_WRITES_ENABLED === 'true'` and now includes warning text/panel when shown.
- `apps/web/src/routes/transactions/new/+page.svelte` — warning panel before the form plus required
  acknowledgement checkbox before final create submission; validation action remains available with
  `formnovalidate`.
- `apps/web/src/routes/transactions/new/+page.server.ts` — final create action rejects missing
  acknowledgement before validate/create API calls.
- `apps/web/scripts/test-auth-routes.mjs` — static route checks now verify disabled-write redirect,
  enabled warning copy, and acknowledgement coverage.
- `CHANGELOG.md`, `docs/v0.2-controlled-writes.md`, `docs/release/v0.0.2-prealpha-notes.md`, and
  `docs/handoff/phase-36.md` — Phase 36 status/safety docs updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the default documented state; controlled
writes remain experimental/post-MVP and disabled by default; backend disabled-write guards remain
covered by `TestWritesDisabledByDefault`; no auth localStorage/sessionStorage path was introduced;
no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #21 closed by Phase 36; GitHub #18, #20, and #22 intentionally remain open.

## Phase 37 — Independent Audit and Baseline Sync

Status: complete. Phase commit pushed.

Goal: run the required independent audit after Phase 36 and synchronize public baseline/status
documentation without adding features, publishing a release, or expanding controlled writes.

Artifacts:

- `docs/audits/2026-05-18-phase-37-audit.md` — independent Phase 37 audit artifact.
- `README.md` — current status advanced to Phase 0–36 complete and latest audit link updated to the
  Phase 37 audit.
- `CHANGELOG.md` — added Phase 37 Unreleased entry.
- `docs/handoff/phase-37.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental/post-MVP and disabled by default; Phase 37 made documentation/status-only
fixes after the audit and did not change write code, auth storage, or release artifacts.

Test results: disabled-write regression subset passed; frontend check/auth-routes/build passed;
Docker config validation passed.

Related issues: GitHub #19 closed by Phase 37; GitHub #18, #20, and #22 intentionally remain open.

## Phase 38 — Personal Dogfood Readiness

Status: complete. Phase commit pushed.

Goal: prepare safe personal read-only dogfood instructions for testing against a copied GnuCash SQL
book without adding features, expanding write scope, or publishing a release.

Artifacts:

- `docs/dogfood/personal-readonly-dogfood.md` — step-by-step local dogfood guide covering
  copied-book setup, `data/books/`, `GNUCASH_WRITES_ENABLED=false`, Docker startup, screen checks,
  CSV export handling, write-UI-hidden confirmation, shutdown, cleanup, and safe reporting rules.
- `scripts/smoke/read-only-smoke-check.md` — manual smoke checklist for read-only dogfood readiness;
  automation remains planned for Phase 39.
- `CHANGELOG.md` — added Phase 38 Unreleased entry.
- `docs/handoff/phase-38.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 38 added documentation/checklists
only and did not change product code, backend write-gating, frontend write UI, auth storage, or
release artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed.

Related issues: no Phase 38-specific GitHub issue found in the current open issue list; GitHub #18,
#20, and #22 intentionally remain open.

## Phase 39 — Read-Only Smoke Test Automation

Status: complete. Phase commit pushed.

Goal: add a minimal automated API smoke script for local read-only Docker deployments without
requiring real financial data or expanding write scope.

Artifacts:

- `scripts/smoke/read-only-api-smoke.py` — stdlib-only Python smoke script for local API
  deployments; checks `/health`, login, `/auth/me`, default book discovery through `/books`, book
  metadata, accounts, transactions, reports summary, and disabled-write 403 responses for
  validate/create/patch/delete controlled-write endpoints.
- `scripts/smoke/read-only-smoke-check.md` — updated manual checklist with the Phase 39 automated
  API smoke command and environment variables.
- `CHANGELOG.md` — added Phase 39 Unreleased entry.
- `docs/handoff/phase-39.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 39 adds smoke automation only and
does not enable writes, add write capability, change auth storage, publish a release, or add real
financial/secrets artifacts.

Test results: script help/compile check passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed.

Related issues: no Phase 39-specific GitHub issue found in the current open issue list; GitHub #18,
#20, and #22 intentionally remain open.

## Phase 40 — v0.0.2-prealpha Release Candidate Cleanup

Status: complete. Phase commit pushed.

Goal: prepare honest release-candidate documentation for `v0.0.2-prealpha` without publishing a tag
or GitHub release.

Artifacts:

- `docs/release/v0.0.2-prealpha-checklist.md` — new release-candidate checklist covering scope,
  exclusions, required gate, automated checks, optional local smoke, and release command placeholder
  reserved for the explicit publish phase.
- `docs/release/v0.0.2-prealpha-notes.md` — updated through Phase 40 with dogfood/smoke work and
  release-gate language.
- `README.md` — current status advanced through Phase 40 and linked to the `v0.0.2-prealpha`
  checklist.
- `CHANGELOG.md` — added Phase 40 Unreleased entry.
- `docs/handoff/phase-40.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 40 is
documentation/release-candidate cleanup only and does not enable writes, expand write scope, publish
a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #20 updated with Phase 40 status; GitHub #18 and #22 intentionally remain
open.

## Phase 41 — Release Gate Audit for v0.0.2-prealpha

Status: complete. Phase commit pushed.

Goal: run the external release-gate audit before any `v0.0.2-prealpha` tag or GitHub release is
published, then fix only accepted audit blockers/mismatches.

Artifacts:

- `docs/audits/2026-05-18-v0.0.2-release-gate.md` — independent release-gate audit artifact with
  verdict `Ready after listed blockers`.
- `README.md` — current status advanced through Phase 41 and latest audit link updated to the
  release-gate audit.
- `docs/release/v0.0.2-prealpha-notes.md` — Phase 41 audit note added and stale related-doc links
  fixed before use as release notes.
- `CHANGELOG.md` — added Phase 41 Unreleased entry.
- `docs/handoff/phase-41.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 41 did not enable writes, expand
write scope, publish a release/tag, or add real financial/secrets artifacts. Disabled
validate/create/patch write gating was re-verified.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.
Post-push GitHub CI should be checked before Phase 42 publication.

Related issues: GitHub #18 closed after release-gate re-verification; GitHub #20 updated with Phase
41 gate status; GitHub #22 remains open for compatibility fixtures.

## Phase 42 — Publish v0.0.2-prealpha

Status: complete. Phase commit pushed, annotated tag pushed, and GitHub pre-release published.

Goal: publish `v0.0.2-prealpha` only after confirming the Phase 41 release gate was complete and
post-push GitHub CI for the gate commit was green.

Artifacts:

- Git tag: `v0.0.2-prealpha`.
- GitHub pre-release:
  https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.0.2-prealpha
- `README.md` — current status and release readiness now point to the published `v0.0.2-prealpha`
  release.
- `CHANGELOG.md` — moved accumulated pre-alpha changes into the `0.0.2-prealpha` release section and
  added the Phase 42 publication entry.
- `docs/handoff/phase-42.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 42 did not enable writes, expand
write scope, or add real financial/secrets artifacts.

Test results: post-Phase-41 GitHub CI was green before publication; backend full suite passed;
frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #20 updated and closed after successful `v0.0.2-prealpha` publication.

## Phase 43 — Local Deployment Hardening Guide

Status: complete. Phase commit pushed.

Goal: add practical, conservative instructions for safely running the pre-alpha app locally or on a
trusted LAN/VPN without implying production readiness.

Artifacts:

- `docs/deployment/local-secure-deployment.md` — local-only and LAN/VPN-only deployment guide
  covering reverse proxy/HTTPS notes, `.env` secrets, data/backup/app DB locations, GnuCash
  copied-book handling, public-internet warning, read-only smoke verification, and keeping
  `GNUCASH_WRITES_ENABLED=false`.
- `README.md` — current status advanced through Phase 43 and linked to the local secure deployment
  guide from quick-start and security/deployment sections.
- `CHANGELOG.md` — added Phase 43 Unreleased entry.
- `docs/handoff/phase-43.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 43 is documentation-only and does
not enable writes, expand write scope, publish a release/tag, or add real financial/secrets
artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issues: no Phase 43-specific GitHub issue found in the current open issue list; GitHub #22,
#17, #13, #12, and #11 remain open for later roadmap work.

## Phase 44 — Backup and Recovery Runbook

Status: complete. Phase commit pushed.

Goal: document conservative backup and recovery procedures for read-only deployments and future
experimental controlled-write testing without claiming production-grade disaster recovery.

Artifacts:

- `docs/operations/backup-and-recovery.md` — manual backup/recovery runbook covering app metadata DB
  backups, copied GnuCash book backups, Docker data paths, backup frequency, restore dry-runs,
  controlled-write pre-write backup expectations, restored-book verification, and explicit
  non-guarantees.
- `README.md` — current status advanced through Phase 44 and linked to the backup/recovery runbook
  from safety/deployment documentation.
- `docs/deployment/local-secure-deployment.md` — Phase 43 placeholder for a later runbook replaced
  with the actual Phase 44 runbook link.
- `CHANGELOG.md` — added Phase 44 Unreleased entry.
- `docs/handoff/phase-44.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 44 is documentation-only and does
not enable writes, expand write scope, publish a release/tag, or add real financial/secrets
artifacts.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no Phase 44-specific GitHub issue found in the current open issue list; GitHub #22,
#17, #13, #12, and #11 remain open for later roadmap work.

## Phase 45 — GnuCash Compatibility Fixture Plan

Status: complete. Phase commit pushed.

Goal: advance GitHub issue #22 by defining a safe, conservative plan for real-version GnuCash
compatibility fixtures without committing binary fixtures, real data, or expanding write scope.

Artifacts:

- `docs/gnucash-version-fixture-plan.md` — new planning document covering target GnuCash version
  families, OS/source metadata, synthetic fixture data model, safe generation/storage policy, and
  acceptance tests for future fixture implementation.
- `docs/gnucash-compatibility.md` — linked the Phase 45 fixture plan from future compatibility work.
- `README.md` — current status advanced through Phase 45 and linked the fixture plan under
  compatibility/safety docs.
- `CHANGELOG.md` — added Phase 45 Unreleased entry.
- `docs/handoff/phase-45.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 45 is documentation/planning-only
and does not add fixture binaries, enable writes, expand write scope, publish a release/tag, or add
real financial/secrets artifacts.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 45 plan and remains open for Phase 46
implementation.

## Phase 46 — Compatibility Fixture Implementation v1

Status: complete. Phase commit pushed.

Goal: add the first generated disposable compatibility fixture path beyond mocks without committing
a new binary GnuCash file or expanding write scope.

Artifacts:

- `apps/api/scripts/create_compatibility_fixture_v1.py` — deterministic generator for a synthetic
  disposable GnuCash SQLite fixture and non-sensitive metadata/sha256 output.
- `apps/api/tests/test_compatibility_fixture_v1.py` — read-only compatibility tests for generation
  metadata, checksum no-mutation behavior, account tree, transaction list, split transaction detail,
  reports basic, and loading a copied generated fixture.
- `docs/gnucash-compatibility-fixture-v1.md` — documentation for the generator path, data model,
  validation coverage, and safety limits.
- `.gitignore` — ignores `apps/api/tests/generated-fixtures/` so locally generated SQLite fixtures
  are not committed.
- `docs/gnucash-compatibility.md`, `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-46.md` —
  status and compatibility docs synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 46 does not add write capability,
enable writes, publish a release/tag, or add real financial/secrets artifacts. The generated fixture
is synthetic and generated in temp/ignored paths; no new binary GnuCash fixture is committed.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 46 implementation status and remains open for
future desktop-version fixture coverage unless maintainers decide this generator path is sufficient
for the issue.

## Phase 47 — Auditor Pass After Compatibility Work

Status: complete. Phase commit pushed.

Goal: independently audit the Phase 46 compatibility fixture work for fixture safety, personal-data
hygiene, unwanted binary commits, honest compatibility documentation, and README overclaim risk.

Artifacts:

- `docs/audits/2026-05-18-phase-47-audit.md` — independent Phase 47 audit artifact with verdict
  `Ready for pre-alpha release` and no blockers.
- `README.md` — current status advanced through Phase 47 and latest-audit link updated to the Phase
  47 audit.
- `CHANGELOG.md` — added Phase 47 Unreleased entry.
- `docs/handoff/phase-47.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 47 did not enable writes, expand
write scope, publish a release/tag, or add real financial/secrets artifacts. Only existing committed
fixture binaries are the historical synthetic test fixtures; the Phase 46 generated fixture output
path remains ignored and no generated binary was committed.

Test results: Phase 46 compatibility fixture tests passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 47 audit result and remains open for future
desktop-version fixture coverage unless maintainers decide the generated fixture path is sufficient
for the issue.

## Phase 48 — UX Polish for Read-Only Core

Status: complete. Phase commit pushed.

Goal: improve read-only daily usability with small frontend-only polish while avoiding any
write-scope expansion.

Artifacts:

- `apps/web/src/lib/components/TransactionFilters.svelte` — adds explanatory read-only filter copy,
  filtered-view status, and a disabled/explicit reset-filters button when no filters are active.
- `apps/web/src/lib/components/TransactionCard.svelte` and `TransactionTable.svelte` — improve empty
  transaction states and mobile transaction card copy.
- `apps/web/src/routes/transactions/+page.svelte` — clarifies CSV export filter count/status and
  documents the 10,000-row cap next to the export action.
- `apps/web/src/routes/accounts/+page.svelte` — adds an account-tree empty state for missing/empty
  read-only book views.
- `apps/web/src/routes/accounts/[id]/+page.svelte` — replaces the plain back link with clearer
  account breadcrumbs.
- `CHANGELOG.md` and `docs/handoff/phase-48.md` — phase status and handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 48 is frontend UX-only and does
not add write capability, account editing, import/sync, release/tag publication, or real
financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: none identified in the roadmap for Phase 48.

## Phase 49 — Transaction Search/Filter Hardening

Status: complete. Phase commit pushed.

Goal: make read-only transaction search and filters more reliable and understandable while keeping
API/frontend/CSV export behavior aligned.

Artifacts:

- `apps/api/app/routers/transactions.py` — adds shared transaction-filter validation so list,
  account-scoped list, book-scoped list, and CSV export reject invalid/inverted date ranges and
  inverted amount ranges before querying GnuCash.
- `apps/api/tests/test_transactions.py` — adds list-view regression coverage for inverted date and
  amount ranges.
- `apps/api/tests/test_transaction_export.py` — adds CSV export regression coverage for inverted
  date ranges and combined query/date/account/amount filter parity.
- `apps/web/src/lib/components/TransactionFilters.svelte` — adds client-side inverted date range
  validation with accessible inline error state alongside existing amount validation.
- `apps/web/scripts/test-auth-routes.mjs` — extends frontend route checks to assert transaction
  filter URL/CSV parity and frontend range validation coverage.
- `docs/transactions-filters.md` — documents supported filters, validation, URL/pagination behavior,
  and CSV export parity.
- `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-49.md` — phase status and documentation
  synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 49 does not add write capability,
enable write mode, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #11 updated with the Phase 49 hardening summary and left open for broader
future read-only search/filter enhancements.

## Phase 50 — Book Switcher Stabilization

Status: complete. Phase commit pushed.

Goal: stabilize the existing multi-book UI foundation at a safe read-only level without adding book
upload, book registration UI, collaborative editing, or write-scope expansion.

Artifacts:

- `apps/web/src/lib/api/server.ts` — adds shared accessible-book context resolution that prefers the
  selected accessible book, then accessible default, then first accessible book; stale/unauthorized
  selected-book cookies are refreshed or cleared before book-aware API routes are built.
- `apps/web/src/routes/+layout.server.ts`, `dashboard/+page.server.ts`, `accounts/+page.server.ts`,
  `accounts/[id]/+page.server.ts`, `transactions/+page.server.ts`, and
  `transactions/[id]/+page.server.ts` — use shared active-book context so page data routes no longer
  trust raw `selected_book_id` directly.
- `apps/web/src/lib/components/BookSwitcher.svelte` — labels the current book clearly, preserves
  route/query string on switch, marks the default book, and frames multi-book as independent
  read-only books.
- `apps/web/scripts/test-auth-routes.mjs` — adds static frontend checks for book context fallback,
  route usage, route/query preservation, and no collaborative/upload framing.
- `docs/book-switcher-readonly-model.md` — documents read-only multi-book behavior, access boundary,
  fallback order, and non-goals.
- `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/handoff/phase-50.md` — phase status
  and documentation synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 50 does not add write capability,
book upload, import/sync, account editing, collaborative editing, release/tag publication, or real
financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #13 updated with the Phase 50 stabilization summary and remains open for
future admin-only book management UI.

## Phase 51 — Auditor Pass After UX/Book/Filter Work

Status: complete. Phase commit pushed.

Goal: independently audit the Phase 48–50 UX, transaction filter/export, and book-switcher work to
confirm read-only scope, independent-books framing, filter/export safety, and documentation
consistency.

Artifacts:

- `docs/audits/2026-05-18-phase-51-audit.md` — independent Phase 51 audit artifact with verdict
  `Ready for pre-alpha release` and no blockers.
- `README.md` — current status advanced through Phase 51 and latest-audit link updated to the Phase
  51 audit.
- `CHANGELOG.md` — added Phase 51 Unreleased entry.
- `docs/handoff/phase-51.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 51 did not enable writes, expand
write scope, add book upload/import/management UI, add collaborative editing, publish a release/tag,
or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issues: GitHub #11 and #13 updated with the Phase 51 audit result and remain open for
broader future search/filter and admin-only book-management work.

## Phase 52 — Russian Localization Planning and i18n Foundation

Status: complete. Phase commit pushed.

Goal: start SvelteKit i18n carefully without translating the whole project or making Russian the
default.

Artifacts:

- `apps/web/src/lib/i18n/messages.ts` and `apps/web/src/lib/i18n/index.ts` — typed English-default
  locale catalog with opt-in Russian strings.
- `apps/web/src/routes/locale/+server.ts` — safe locale cookie handler for switching UI language
  without browser localStorage/sessionStorage.
- `apps/web/src/lib/components/LocaleSwitcher.svelte` — small locale switcher used on login and
  authenticated navigation.
- Login, navigation, read-only safety banner, dashboard title, accounts title, and transactions
  title now use the i18n catalog while English remains the default.
- `README.ru.md` — initial Russian README stub with explicit canonical-English and safety caveats.
- `docs/localization.md` — localization approach, reviewed Russian safety text policy, and
  non-goals.
- `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-52.md` — phase status and documentation
  synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default; Phase 52 does not enable writes, expand
write scope, publish a release/tag, add real financial/secrets artifacts, or make Russian the
default. English docs remain canonical and Russian safety text is manually reviewed.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #17 updated with the Phase 52 localization foundation summary and remains open
for broader future translation work.

## Phase 53 — Community Announcement Draft

Status: complete. Phase commit pushed.

Goal: prepare a cautious community announcement package for interested GnuCash/self-hosted testers
without production marketing or write-safety overclaims.

Artifacts:

- `docs/community/announcement-draft.md` — refreshed conservative announcement draft with short
  pitch, current working scope, not-ready scope, safety warning, target tester profile, feedback
  prompts, and suggested posts for r/GnuCash, r/selfhosted, later Show HN, and
  Mastodon/Linux/self-hosted communities.
- `docs/community/where-to-share.md` — channel guidance, posting gates, anti-channels, feedback
  prompts, and safety checklist for community sharing.
- `README.md` — current status advanced through Phase 53 and community docs linked.
- `CHANGELOG.md` — Unreleased entry added for Phase 53.
- `docs/handoff/phase-53.md` — PM/engineer handoff and verification report.

Safety result: Phase 53 is documentation/community-planning only. MVP remains read-only by default;
`GNUCASH_WRITES_ENABLED=false` remains the safe/default state; controlled writes remain experimental
post-MVP and disabled by default. No write scope, release/tag, product code, real financial data,
`.env`, app DB, backup, secret, key, token, certificate, real screenshot, or real export was added.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issue: GitHub #16 received a Phase 53 follow-up comment and remains closed.

## Phase 54 — Observability and Diagnostics

Status: complete. Phase commit pushed.

Goal: make self-hosted deployment errors easier to diagnose with safe startup diagnostics, a richer
non-sensitive health endpoint, default-book/app-DB checks, and troubleshooting documentation.

Artifacts:

- `apps/api/app/diagnostics.py` — safe diagnostics helpers for default book existence, app metadata
  DB reachability, health payload construction, and structured startup logging.
- `apps/api/app/main.py` — startup now logs a `startup_diagnostics` JSON event, and `/health`
  returns app DB/default-book/write-mode checks without exposing secrets or full paths.
- `apps/api/tests/test_health.py` — regression tests for richer health payloads, understandable
  missing-book diagnostics, and secret/path-safe startup logs.
- `docs/operations/troubleshooting.md` — self-hosted troubleshooting guide covering health payloads,
  missing default book checks, app DB reachability, startup diagnostics logs, and safe bug-report
  contents.
- `README.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`, and `docs/handoff/phase-54.md` — status and
  troubleshooting docs synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 54 does not add write capability,
enable write mode, publish a release/tag, add telemetry, or add real financial/secrets artifacts.
Health/startup diagnostics intentionally avoid full book paths, credentials, JWT secrets, admin
passwords, database URLs, and real data.

Test results: health diagnostics tests passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: no Phase 54-specific GitHub issue was identified in the open issue list.

## Phase 55 — v0.1 Read-Only Scope Freeze Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to prepare a real `v0.1.0-readonly` milestone plan without
publishing a release or expanding write scope.

Artifacts:

- `docs/audits/2026-05-18-phase-55-v0.1-readonly-scope-freeze.md` — independent scope-freeze audit
  artifact with verdict `Ready to prepare v0.1 read-only`.
- `docs/ROADMAP.md` — stale release-posture wording fixed so `v0.0.2-prealpha` is no longer
  described as unpublished.
- `README.md` — current status advanced through Phase 55 and latest-audit link updated to the Phase
  55 audit.
- `CHANGELOG.md` — Unreleased entry added for Phase 55.
- `docs/handoff/phase-55.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 55 did not enable writes, expand
write scope, publish a release/tag, add production/security-audited claims, or add real
financial/secrets artifacts.

Test results: disabled-write regression subset passed; backend full suite passed; frontend
check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no new Phase 55 issue was required. GitHub #22, #17, #13, #12, and #11 remain open
backlog items to consider during v0.1 planning.

## Phase 56 — v0.1 Read-Only Release Planning

Status: complete. Phase commit pushed.

Goal: create a conservative `v0.1.0-readonly` release plan and checklist after the Phase 55 audit
verdict allowed v0.1 planning, without publishing a tag/release or expanding write scope.

Artifacts:

- `docs/release/v0.1.0-readonly-plan.md` — included/excluded scope, open backlog triage, minimum
  checks, dogfood requirements, compatibility scope, upgrade path, release blockers, rollback plan,
  and required next governance step.
- `docs/release/v0.1.0-readonly-checklist.md` — release-gate checklist for scope, docs, automated
  checks, runtime smoke/dogfood, compatibility, sensitive-data hygiene, GitHub/project hygiene,
  publication gate, and rollback readiness.
- `README.md` — current status advanced through Phase 56 and v0.1 planning docs linked.
- `CHANGELOG.md` — Unreleased entry added for Phase 56.
- `docs/ROADMAP.md` — next posture advanced from planning to a future v0.1 release-gate audit.
- `docs/handoff/phase-56.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 56 did not enable writes, expand
write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real
financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config
validation passed; `git diff --check` passed.

Related issues: no Phase 56-specific GitHub issue was required. The plan explicitly triages open
issues #22, #17, #13, #12, and #11 for v0.1 in/out scope.

## Phase 57 — v0.1.0-readonly Release-Gate Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to publish `v0.1.0-readonly` without publishing a
tag/release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-57-audit.md` — independent Phase 57 release-gate audit artifact with verdict
  `Not ready for v0.1.0-readonly`.
- `README.md` — current status advanced through Phase 57 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for Phase 57.
- `docs/handoff/phase-57.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 57 did not enable writes, expand
write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real
financial/secrets artifacts.

Release-gate result: v0.1 publication is blocked by process/docs evidence gaps, not by a discovered
read-only boundary break. Required blockers are conservative `v0.1.0-readonly` release notes and a
recorded runtime smoke/dogfood pass on copied or disposable data.

Test results: disabled-write regression subset and backend full suite passed. Frontend
check/auth-routes/build, Docker config validation, and `git diff --check` are recorded in the Phase
57 handoff.

Related issues: GitHub #24 and #25 created for the Phase 57 release-gate blockers.

## Phase 58 — v0.1.0-readonly Release Publication Audit

Status: complete. Phase commit pushed.

Goal: audit the expected `v0.1.0-readonly` publication state from the auditor roadmap without
publishing a tag/release or expanding write scope.

Artifacts:

- `docs/audits/phase-58-audit.md` — independent Phase 58 publication audit artifact with verdict
  `Not ready / publication audit blocked`.
- `README.md` — current status advanced through Phase 58 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 58 publication audit result.
- `docs/handoff/phase-58.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 58 did not enable writes, expand
write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real
financial/secrets artifacts.

Release-publication result: no `v0.1.0-readonly` git tag or GitHub release exists, which is
consistent with the unresolved Phase 57 blockers. Publication remains blocked by missing
conservative v0.1 release notes and missing copied/disposable-data runtime smoke/dogfood evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 58 handoff.

Related issues: no new issue created; GitHub #24 and #25 were updated with Phase 58 audit comments
and remain the meaningful release-publication blockers.

## Phase 59 — Post-Release Regression Risk Audit

Status: complete. Phase commit pushed.

Goal: audit whether commits after `v0.1.0-readonly` accidentally changed release assumptions,
without publishing a tag/release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-59-audit.md` — independent Phase 59 post-release regression-risk audit artifact
  with verdict `Not applicable as a post-v0.1 regression audit; stay pre-release for v0.1`.
- `README.md` — current status advanced through Phase 59 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 59 regression-risk audit
  result.
- `docs/handoff/phase-59.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 59 did not enable writes, expand
write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real
financial/secrets artifacts.

Post-release regression result: a true post-v0.1 regression audit is not applicable yet because no
`v0.1.0-readonly` git tag or GitHub release exists. README and PROJECT_STATUS continue to
distinguish latest public release (`v0.0.2-prealpha`) from current `main`; publication remains
blocked by missing conservative v0.1 release notes and missing copied/disposable-data runtime
smoke/dogfood evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 59 handoff.

Related issues: no new issue created; GitHub #24 and #25 were updated with Phase 59 audit comments
and remain the meaningful v0.1 publication blockers.

## Phase 60 — Dogfood Readiness Audit

Status: complete. Phase commit pushed.

Goal: audit whether the maintainer can safely start read-only dogfood on a copied real GnuCash SQL
book, without performing the dogfood run, publishing a release, expanding write scope, or weakening
safety language.

Artifacts:

- `docs/audits/phase-60-audit.md` — independent Phase 60 dogfood-readiness audit artifact with
  verdict `Ready for maintainer dogfood`.
- `README.md` — current status advanced through Phase 60 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 60 dogfood-readiness audit
  result.
- `docs/handoff/phase-60.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 60 did not enable writes, expand
write scope, publish a v0.1 tag/release, add production/security-audited claims, run dogfood against
a real book, or add real financial/secrets artifacts.

Dogfood-readiness result: maintainer dogfood instructions exist and cover copied-book setup,
`GNUCASH_DEFAULT_BOOK_PATH`, disabled writes, Docker startup, dashboard/accounts/transactions
checks, CSV export, shutdown, cleanup, and public-internet warnings. This confirms readiness to
execute dogfood; it does not record a completed dogfood pass and does not close the release blocker
tracked in GitHub #25.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 60 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 60 dogfood-readiness
audit result and remains open until actual copied/disposable-data runtime evidence is recorded.
GitHub #24 also remains open for conservative v0.1 release notes.

## Phase 61 — Dogfood Results Audit

Status: complete. Phase commit pushed.

Goal: audit reported results from real copied-book dogfooding, without running dogfood, publishing a
release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-61-audit.md` — independent Phase 61 dogfood-results audit artifact with verdict
  `Blocked: no completed copied-book dogfood results are available to audit`.
- `README.md` — current status advanced through Phase 61 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 61 dogfood-results audit
  result.
- `docs/handoff/phase-61.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 61 did not enable writes, expand
write scope, publish a v0.1 tag/release, run dogfood against a real book, or add real
financial/secrets artifacts.

Dogfood-results result: no actual copied-book dogfood results are recorded yet, so crashes, missing
account types, wrong balances, split-transaction behavior, multi-currency surprises, slow pages, CSV
export issues, auth/session problems, and misleading UI copy cannot be audited. GitHub #25 remains
open as the meaningful tracker for copied/disposable-data runtime evidence; no duplicate issue was
created.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 61 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 61 blocked
dogfood-results audit result and remains open. GitHub #24 also remains open for conservative v0.1
release notes.

## Phase 62 — Deployment Safety Audit

Status: complete. Phase commit pushed.

Goal: audit whether local/self-hosted deployment docs are safe for the current pre-alpha/read-only
posture without publishing a release, expanding write scope, or implying public-internet readiness.

Artifacts:

- `docs/audits/phase-62-audit.md` — independent Phase 62 deployment-safety audit artifact with
  verdict `No deployment-safety blocker found for local/private read-only testing`.
- `README.md` — current status advanced through Phase 62 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 62 deployment-safety audit
  result.
- `docs/handoff/phase-62.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 62 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim public-internet safety, or add real financial/secrets
artifacts.

Deployment-safety result: docs are conservative for localhost, LAN, and VPN-only read-only testing.
They warn against direct public-internet exposure, require a strong JWT secret, recommend
HTTPS/VPN/LAN posture, document Docker volume/data paths, document backup locations, and distinguish
the app metadata DB from copied GnuCash books. A non-blocking CORS visibility follow-up was created
as GitHub #26.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 62 handoff.

Related issues: GitHub #26 created for CORS origin narrowing visibility. GitHub #24 and #25 remain
release blockers for conservative v0.1 release notes and copied/disposable-data runtime
smoke/dogfood evidence.

## Phase 63 — Backup/Recovery Audit

Status: complete. Phase commit pushed.

Goal: audit backup and recovery documentation from the auditor roadmap without publishing a release,
expanding write scope, or implying production disaster-recovery guarantees.

Artifacts:

- `docs/audits/phase-63-audit.md` — independent Phase 63 backup/recovery audit artifact with verdict
  `Backup/recovery documentation is acceptable for cautious local/private read-only testing after
  the accepted grep-command docs fix`.
- `docs/operations/backup-and-recovery.md` — corrected the Compose V2 write-disabled verification
  example.
- `docs/deployment/local-secure-deployment.md` — corrected the matching write-disabled verification
  example used by deployment docs.
- `README.md` — current status advanced through Phase 63 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 63 backup/recovery audit
  result.
- `docs/handoff/phase-63.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 63 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production-grade disaster recovery, or add real
financial/secrets artifacts.

Backup/recovery result: the runbook documents backing up copied GnuCash books, backing up
`data/app/app.db`, preserving experimental controlled-write backups, dry-run restore, manual
recovery, read-only smoke verification, and explicit limitations. No new GitHub issue was created
because the only Phase 63 finding was fixed directly as a small docs correction; #24 and #25 remain
the release blockers.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 63 handoff.

Related issues: no new issue created. GitHub #24 and #25 remain release blockers; GitHub #26 remains
a non-blocking deployment-hardening visibility item.

## Phase 22 — Real Controlled Write Integration Tests

Status: complete. Phase commit pushed.

Goal: add integration tests that exercise the controlled write path against a real disposable
GnuCash SQLite fixture using piecash, validating the full write flow end-to-end.

Artifacts:

- `apps/api/tests/test_write_integration.py` — 30 integration tests across 8 test classes covering
  create, patch, backup, audit, lock lifecycle, lock contention, rejection scenarios, read-back
  verification, and original fixture immutability against real piecash books.

Test results: 248 passed (218 existing + 30 new), 0 failed. Frontend: check 0 errors, build success,
auth-routes passed. Docker config valid.

Deviations: ROOT account has `placeholder=0` (not 1 as spec assumed) but is rejected because it's
not in `book.accounts` (it's `book.root_account`), achieving the same test goal. 30 tests
implemented vs 15 minimum.

Production code changes: none. Zero production code changes required; write service works correctly
against real piecash books.

Related issues: GitHub #8 (closed).

## Phase 64 — Compatibility Audit

Status: complete. Phase commit pushed.

Goal: audit GnuCash compatibility claims from the auditor roadmap without publishing a release,
expanding write scope, or claiming broad all-book/all-version support.

Artifacts:

- `docs/audits/phase-64-audit.md` — independent Phase 64 compatibility-claims audit artifact with
  verdict `No compatibility-claims blocker found for the current pre-alpha/read-only posture`.
- `README.md` — current status advanced through Phase 64 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 64 compatibility audit
  result.
- `docs/handoff/phase-64.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 64 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim XML/PostgreSQL/MySQL/MariaDB/all-version
compatibility, or add real financial/secrets artifacts.

Compatibility result: README, release planning docs, and compatibility docs avoid broad
compatibility claims. Tested coverage remains limited to documented synthetic GnuCash SQL SQLite
fixture paths. GitHub #22 remains open for real GnuCash Desktop version fixture coverage. v0.1
publication remains blocked by #24/#25.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 64 handoff.

Related issues: no new issue created; GitHub #22 was updated with the Phase 64 audit result and
remains open. GitHub #24 and #25 remain release blockers; GitHub #26 remains a non-blocking
deployment-hardening visibility item.

## Phase 65 — Test Coverage Audit

Status: complete. Phase commit pushed.

Goal: audit whether the current tests support the repository's maturity claims from the auditor
roadmap without adding product features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-65-audit.md` — independent Phase 65 test-coverage audit artifact with a
  claim-to-test-coverage matrix and verdict: automated coverage supports the current
  pre-alpha/read-only posture, but does not unblock `v0.1.0-readonly` publication.
- `README.md` — current status advanced through Phase 65 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 65 test-coverage audit
  result.
- `docs/handoff/phase-65.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 65 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit/broad
compatibility, or add real financial/secrets artifacts.

Coverage result: backend tests, frontend check/auth-route/build coverage, Docker Compose validation,
and CI workflow coverage support the current conservative pre-alpha/read-only claims. The audit
found no new test-coverage blocker, but kept #24/#25 as release blockers because automated tests do
not replace conservative v0.1 release notes or copied/disposable-data runtime smoke/dogfood
evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 65 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 65 audit result and
remains open. GitHub #24 and #25 remain release blockers; GitHub #22 and #26 remain open for
compatibility/deployment-hardening follow-up.

## Phase 66 — Security Posture Audit

Status: complete. Phase commit pushed.

Goal: audit the current security posture from the auditor roadmap without pretending to perform a
professional security audit, adding product features, expanding write scope, or publishing a
release.

Artifacts:

- `docs/audits/phase-66-audit.md` — independent Phase 66 security-posture audit artifact with
  verdict: ready to continue pre-alpha security hardening, not security-audited, and not ready to
  claim audited security.
- `README.md` — current status advanced through Phase 66 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 66 security-posture audit
  result.
- `docs/handoff/phase-66.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 66 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real
financial/secrets artifacts.

Security-posture result: auth tokens remain stored in httpOnly cookies rather than browser auth
storage; placeholder JWT secrets are rejected; dependency files exist for future security scanning;
CORS wildcard development defaults remain documented and tracked in #26; and #27 was created for the
meaningful hardening finding that default-book seeding logs full configured GnuCash book paths/URIs.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 66 handoff.

Related issues: GitHub #27 created for seed-log path redaction; GitHub #26 updated and kept open for
CORS origin narrowing visibility. GitHub #24 and #25 remain v0.1 release blockers; GitHub #22
remains open for compatibility follow-up.

## Phase 67 — Open-Source Hygiene Audit

Status: complete. Phase commit pushed.

Goal: audit public project health from the auditor roadmap without adding product features,
expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-67-audit.md` — independent Phase 67 open-source hygiene audit artifact with
  verdict: good OSS hygiene, with minor cleanup completed.
- `README.md` — current status advanced through Phase 67 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 67 OSS hygiene audit result.
- `docs/handoff/phase-67.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 67 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real
financial/secrets artifacts.

Open-source hygiene result: license, README, contributing guide, code of conduct, security policy,
funding placeholder, issue/PR templates, GitHub topics, documented social-preview setup, and
meaningful open issues are present. The missing `needs-triage` label referenced by issue templates
was created. The GitHub repository description was updated to include read-only positioning: `Modern
self-hosted read-only web companion for GnuCash books.`

Test results: `git diff --check` and GitHub hygiene verification are recorded in the Phase 67
handoff. No v0.1 readiness verdict was made and no product code changed, so the full
backend/frontend/Docker suite was not rerun for this audit-only phase.

Related issues: no new issue created; label/repository-description hygiene was fixed directly.
GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path
redaction; GitHub #26 and #22 remain open for deployment/compatibility follow-up.

## Phase 68 — Documentation Formatting Audit

Status: complete. Phase commit pushed.

Goal: audit human readability of markdown source from the auditor roadmap without adding product
features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-68-audit.md` — independent Phase 68 documentation-formatting audit artifact
  with verdict: documentation formatting is acceptable with non-blocking cleanup needed before wider
  announcement.
- `README.md` — current status advanced through Phase 68 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 68 documentation-formatting
  audit result.
- `docs/handoff/phase-68.md` — PM/auditor/engineer handoff and verification report.
- `docs/DEVELOPMENT.md`, `docs/handoff/phase-17.md`, `docs/handoff/phase-18.md`, and
  `docs/handoff/phase-22.md` — small historical markdown readability/link clarifications accepted by
  PM.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 68 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real
financial/secrets artifacts.

Documentation-formatting result: markdown source readability is acceptable for current pre-alpha
docs, but many historical docs have very long raw-source lines. The phase fixed five unlabeled
historical code fences and clarified one handoff-relative image path example. GitHub #28 now tracks
broader gradual markdown source readability cleanup before wider announcement.

Test results: custom markdown static scan and `git diff --check` are recorded in the Phase 68
handoff. Full backend/frontend/Docker suite was not rerun because this phase is audit/docs-only,
changed no product code, and made no v0.1 release-readiness verdict.

Related issues: GitHub #28 created for gradual markdown source readability cleanup. GitHub #24 and
#25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26
and #22 remain open for deployment/compatibility follow-up.

## Phase 69 — Localization/i18n Audit

Status: complete. Phase commit pushed.

Goal: audit Russian localization planning and implementation from the auditor roadmap without adding
product features, expanding write scope, making Russian the default locale, or publishing a release.

Artifacts:

- `docs/audits/phase-69-audit.md` — independent Phase 69 localization/i18n audit artifact with
  verdict: localization/i18n posture is acceptable for the current pre-alpha read-only scope, with
  non-blocking glossary follow-up required before localization grows.
- `README.md` — current status advanced through Phase 69 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 69 localization/i18n audit
  result.
- `docs/handoff/phase-69.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 69 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, make Russian the
default locale, or add real financial/secrets artifacts.

Localization result: English remains canonical; `README.ru.md` is intentionally a short starter
reference and does not contradict English safety/read-only positioning; Russian UI strings are
opt-in and preserve the read-only/default-write/GnuCash Desktop authority boundary; complete
translation remains non-blocking for v0.1 unless PM changes release criteria. GitHub #29 now tracks
the non-blocking glossary gap for accounting/safety terminology.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` are recorded in the Phase 69 handoff.

Related issues: GitHub #29 created for a localization glossary. GitHub #17 remains open for broader
Russian documentation/UI localization planning. GitHub #24 and #25 remain v0.1 release blockers;
GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, and #28 remain open for
deployment/compatibility/markdown follow-up.

## Phase 70 — Community Announcement Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to be shared with interested communities from the auditor
roadmap without publishing a release, expanding write scope, or using production-style marketing.

Artifacts:

- `docs/audits/phase-70-audit.md` — independent Phase 70 community-announcement audit artifact with
  verdict: ready only in limited circles.
- `README.md` — current status advanced through Phase 70 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 70 community-announcement
  audit result.
- `docs/handoff/phase-70.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 70 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real
financial/secrets artifacts.

Community-announcement result: README explains who the project is and is not for; README screenshots
are labeled as synthetic fixture data; `docs/community/announcement-draft.md` exists and uses
feedback-wanted conservative copy; `docs/community/where-to-share.md` limits ready-now sharing to
narrow technical/GnuCash circles; README related-project comparison is fair and does not overclaim.
Broad launch-style promotion remains inappropriate while #24/#25 are open.

Test results: documentation/static announcement-readiness checks, backend full suite, frontend
check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in
the Phase 70 handoff.

Related issues: no new issue created; existing #24, #25, #28, and #29 cover meaningful
release/community follow-ups without adding noisy backlog theater. GitHub #24 and #25 remain v0.1
release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, #28, and #29
remain open for deployment/compatibility/markdown/localization follow-up.

## Phase 71 — Performance Risk Audit

Status: complete. Phase commit pushed.

Goal: audit whether obvious read-only performance risks are tracked before any broader
v0.1/large-book confidence claims.

Artifacts:

- `docs/audits/phase-71-audit.md` — independent Phase 71 performance-risk audit artifact with
  verdict: needs performance-risk tracking before broader confidence claims.
- `README.md` — current status advanced through Phase 71 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 71 performance-risk audit
  result.
- `docs/handoff/phase-71.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 71 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, claim known
large-book scalability, or add real financial/secrets artifacts.

Performance-risk result: transaction list routes have pagination caps and CSV export has a
documented 10,000-row cap, but the read-only service layer can still scan/sort matched transactions
and dashboard aggregates iterate accounts/transactions/splits. No large-book benchmark evidence
exists yet, so large-book scalability must not be claimed.

Test results: static performance-risk audit checks, backend full suite, frontend
check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in
the Phase 71 handoff.

Related issues: GitHub #30, #31, #32, and #33 were created for large-book benchmark, many-splits
benchmark, CSV timeout/truncation behavior, and dashboard aggregate performance tracking. GitHub #24
and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub
#26, #22, #28, and #29 remain open for deployment/compatibility/markdown/localization follow-up.

## Phase 72 — Data Model and Money Correctness Audit

Status: complete. Phase commit pushed.

Goal: audit money handling from the auditor roadmap without adding product features, expanding write
scope, publishing a release, or claiming v0.1 readiness.

Artifacts:

- `docs/audits/phase-72-audit.md` — independent Phase 72 data model and money-correctness audit
  artifact with verdict: no new blocker for the current pre-alpha/read-only posture.
- `docs/money-model.md` — canonical money representation, CSV export, sign-convention, split-amount,
  and multi-currency behavior notes.
- `README.md` — current status advanced through Phase 72 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 72 audit/docs result.
- `docs/handoff/phase-72.md` — PM/auditor/engineer handoff and verification report.
- `docs/ARCHITECTURE.md` — linked to the canonical money model.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 72 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, add fake
currency conversion, or add real financial/secrets artifacts.

Money-correctness result: backend core read-only money paths use Decimal/string DTOs, reject floats
in service-layer money conversion, serialize JSON money as strings, and write CSV export amounts
from string DTOs. Multi-currency report totals remain conservative and exclude non-base-currency
values instead of converting them. Canonical docs now clarify sign and split amount conventions.

Test results: static money-correctness audit searches, backend full suite, frontend
check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in
the Phase 72 handoff.

Related issues: GitHub #34 was created for frontend display-only `Number()` money hygiene. GitHub
#24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction;
GitHub #26, #22, #28, #29, and #30–#33 remain open for
deployment/compatibility/markdown/localization/performance follow-up.

## Phase 73 — Multi-book Access Model Audit

Status: complete. Phase commit pushed.

Goal: audit the multi-book access model from the auditor roadmap without adding product feature
scope, expanding writes, publishing a release, or implying collaborative accounting/family-wallet
semantics.

Artifacts:

- `docs/audits/phase-73-audit.md` — independent Phase 73 multi-book access model audit artifact with
  verdict: no new blocker for the current pre-alpha/read-only posture.
- `docs/book-switcher-readonly-model.md` — clarified archived-book visibility and future
  archive/visibility-management documentation expectations.
- `README.md` — current status advanced through Phase 73 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 73 audit/docs result.
- `docs/handoff/phase-73.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 73 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, add
collaborative accounting/family-wallet framing, or add real financial/secrets artifacts.

Multi-book access result: user-book access remains explicit through `UserBookAccess`; `GET /books`
returns only non-archived books visible to the current user; book-aware account, transaction, CSV
export, and report routes resolve a viewable book before opening GnuCash data; the frontend switcher
shows only accessible books from the authenticated `GET /books` context and keeps independent
read-only wording. Archive/visibility route semantics need stronger dedicated regression coverage
and are tracked in #35.

Test results: static multi-book access/documentation audit checks, backend full suite, frontend
check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in
the Phase 73 handoff.

Related issues: GitHub #35 was created for archived-book/full route-family multi-book access
boundary test hardening. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open
for seed-log path redaction; GitHub #26, #22, #28, #29, #30–#34 remain open for
deployment/compatibility/markdown/localization/performance/money follow-up.

## Phase 74 — Controlled Writes Boundary Audit

Status: complete. Phase commit pushed.

Goal: re-audit the controlled-writes boundary from the auditor roadmap without enabling writes,
expanding write scope, publishing a release, or implying write-mode safety for real books.

Artifacts:

- `docs/audits/phase-74-audit.md` — independent Phase 74 controlled-writes boundary audit artifact
  with verdict: keep writes experimental.
- `README.md` — current status advanced through Phase 74 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 74 audit result.
- `docs/handoff/phase-74.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 74 did not enable writes, expand
write scope, publish a v0.1 tag/release, claim production readiness/security audit, claim safe write
mode, or add real financial/secrets artifacts.

Controlled-writes boundary result: backend validate/create/patch routes call the write feature gate
before resolving books or constructing `GnuCashWriteService`; frontend write UI is hidden unless
explicitly enabled and requires warning/acknowledgement; write integration tests and backup/restore
tests use disposable copied fixtures; file-based locking and backup restore smoke coverage are
documented. Remaining v0.2 write-readiness gaps are tracked in #36.

Test results: static controlled-writes boundary audit checks, backend full suite, frontend
check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in
the Phase 74 handoff.

Related issues: GitHub #36 was created for remaining controlled-write v0.2 readiness gates. GitHub
#24 and #25 remain v0.1 release blockers; GitHub #22 remains open for real GnuCash version fixture
coverage; GitHub #27 remains open for seed-log path redaction; GitHub #26, #28, #29, #30–#35 remain
open for deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 75 — v0.1.1 Maintenance Release Audit

Status: complete. Phase commit pushed.

Goal: audit whether a `v0.1.1-readonly` maintenance release is needed from the auditor roadmap
without preparing or publishing any release, expanding write scope, or implying that
`v0.1.0-readonly` already exists.

Artifacts:

- `docs/audits/phase-75-audit.md` — independent Phase 75 maintenance-release audit artifact with
  verdict: no release needed.
- `README.md` — current status advanced through Phase 75 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 75 audit result.
- `docs/handoff/phase-75.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 75 did not enable writes, expand
write scope, publish a v0.1/v0.1.1 tag or release, prepare a maintenance release, claim production
readiness/security audit, or add real financial/secrets artifacts.

Maintenance-release result: no `v0.1.1-readonly` maintenance release is needed/applicable because
`v0.1.0-readonly` has not been published as a git tag or GitHub release. There is no post-v0.1
dogfood bugfix/docs/small read-only UX fix stream to package. Initial v0.1 publication remains
blocked by #24/#25.

Test results: git/GitHub release/tag checks, static release/docs/write-boundary audit checks,
backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git
diff --check` are recorded in the Phase 75 handoff.

Related issues: no new issue was created because #24 and #25 already cover the meaningful initial
v0.1 release blockers, and a v0.1.1 placeholder issue would be noisy before v0.1.0 exists. GitHub
#36 remains open for controlled-write v0.2 readiness gates; GitHub #22 remains open for real GnuCash
version fixture coverage; GitHub #27 remains open for seed-log path redaction; GitHub #26, #28, #29,
#30–#35 remain open for deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 76 — v0.2 Planning Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to create or promote v0.2 controlled-writes planning from
the auditor roadmap without enabling writes, expanding write scope, creating a misleading write
milestone, publishing a release, or implying write-mode safety for real books.

Artifacts:

- `docs/audits/phase-76-audit.md` — independent Phase 76 v0.2 planning audit artifact with verdict:
  not ready; keep write mode experimental.
- `README.md` — current status advanced through Phase 76 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 76 planning-audit result.
- `docs/handoff/phase-76.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled
writes remain experimental post-MVP and disabled by default. Phase 76 did not enable writes, expand
write scope, create a v0.2 milestone, publish a release, claim production readiness/security audit,
claim safe write mode, or add real financial/secrets artifacts.

Planning result: at the time of Phase 76, the project was not ready to create or promote a v0.2
controlled-writes planning milestone. `v0.1.0-readonly` had not yet been published and remained
blocked by #24/#25; actual copied-book dogfood evidence was still missing; #36 remained open for
remaining write-readiness gates; #22 remained open for real GnuCash version fixture coverage.
Existing write-boundary safeguards supported only the current experimental/post-MVP posture.

Test results: git/GitHub release/tag checks, static release/docs/write-boundary audit checks,
backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git
diff --check` are recorded in the Phase 76 handoff.

Related issues: no new issue was created because #36 already tracks the meaningful v0.2
write-readiness gates. #36 was updated to record the Phase 76 planning-audit verdict and correct
missing `GNUCASH_WRITES_ENABLED=false` wording. GitHub #24 and #25 remain initial v0.1 release
blockers; GitHub #22 remains open for real GnuCash version fixture coverage; GitHub #27 remains open
for seed-log path redaction; GitHub #26, #28, #29, #30–#35 remain open for
deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 77 — Real Read-only Dogfood on Copied/Disposable GnuCash Book

Status: complete. Phase commit pushed.

Goal: run the application locally against a copied/disposable GnuCash SQL book, record actual
usability evidence, verify runtime writes-disabled behavior, identify release blockers, and avoid
creating another audit-only phase.

Artifacts:

- `docs/dogfood/phase-77-readonly-dogfood.md` — dogfood environment, copied/disposable book source
  class, writes-disabled proof, API/browser checks, safe log snippets, issues, and release verdict.
- `docs/audits/phase-77-audit.md` — independent evidence review and release verdict.
- `docs/handoff/phase-77.md` — PM/engineer/auditor handoff and verification report.
- `CHANGELOG.md` — Unreleased entry for the Phase 77 dogfood result.

Safety result: `GNUCASH_WRITES_ENABLED=false` was verified in Docker Compose-resolved runtime config
and `/api/health`; validate/create/patch write endpoint probes returned read-only 403 responses.
Phase 77 did not enable writes, expand write scope, add features, write to the GnuCash book, touch a
real/original book, commit runtime data/secrets, or publish a release.

Dogfood result: Docker API-level dogfood passed against a copied/disposable SQL fixture: login,
`/auth/me`, book discovery, accounts, account detail, transactions, transaction detail, reports
summary, search/filter, CSV export, and disabled-write probes all worked. Browser/UI dogfood failed
because `/login` redirects to itself and the web container is unhealthy.

Release result: not ready for `v0.1.0-readonly`. GitHub #37 is a new release blocker for browser
dogfood. GitHub #25 remains open because Phase 77 is API-success/browser-fail evidence, not a full
copied/disposable-data browser dogfood pass. GitHub #24 remains open for conservative release notes.

Test results: Docker config validation, Docker API runtime health, API smoke script, manual API
dogfood, browser redirect-loop evidence, backend full suite, frontend check/auth-routes/build,
Docker Compose config validation, and `git diff --check` are recorded in the Phase 77 handoff.

Related issues: GitHub #37 was created for the `/login` redirect loop. GitHub #25 remains open as
the umbrella copied/disposable-data runtime dogfood gate; #24 remains the release-notes blocker;
#22, #26–#36 remain open as applicable follow-up.

## Phase 78 — Fix Docker /login Redirect Loop and Rerun Browser Dogfood

Status: complete. Phase commit pushed.

Goal: fix release blocker #37, verify the Docker web UI can load `/login` through Caddy, and rerun
browser/UI dogfood on copied/disposable data with writes disabled.

Artifacts:

- `apps/web/src/routes/+layout.server.ts` — root layout now returns public unauthenticated layout
  data before token/book-context lookup, preventing `/login` self-redirects while preserving
  protected-route auth behavior.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` — server-side CSV export proxy
  for the existing UI export link, using the httpOnly auth cookie server-side and streaming the API
  CSV response.
- `apps/web/scripts/test-auth-routes.mjs` — regression coverage for unauthenticated public layout
  behavior, protected-route redirect expectations, authenticated book-context loading, and CSV
  export proxy auth behavior.
- `docs/dogfood/phase-78-browser-dogfood.md` — reproduction evidence, root cause, fix,
  Docker/browser dogfood, write-disabled runtime probes, and checks.
- `docs/handoff/phase-78.md` — PM/engineer handoff and verification report.
- `CHANGELOG.md` — Unreleased entry for the Phase 78 fix and dogfood result.

Safety result: `GNUCASH_WRITES_ENABLED=false` was verified in Docker Compose-resolved runtime config
and `/api/health`; validate/create/patch write endpoint probes returned read-only 403 responses with
valid payloads. Browser UI showed the write entry point hidden (`new_button_visible=false`). Phase
78 did not enable writes, expand write scope, start v0.2 work, commit runtime data/secrets/real
books, or publish a release.

Dogfood result: Docker/browser dogfood through Caddy passed on the copied/disposable fixture.
`/login` returned 200; unauthenticated `/dashboard` redirected to `/login?next=%2Fdashboard`;
Chromium login reached dashboard; dashboard, accounts, account detail, transactions, transaction
detail, and CSV export route loaded; API smoke passed.

Release result: at the time of Phase 78, #37 was fixed, #25 remained open pending PM/release-gate
acceptance of Phase 78 browser dogfood evidence and any remaining copied-real-book limitation, #24
remained open because release notes were not completed in that phase, and `v0.1.0-readonly` had not
yet been published. It was published later in Phase 80.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, Docker browser dogfood through Caddy, API smoke, write-disabled probes, and `git diff
--check` are recorded in the Phase 78 handoff.

Related issues: GitHub #37 was closed/updated as fixed by Phase 78. GitHub #25 remains the
copied/disposable-data runtime dogfood gate. GitHub #24 remains the release-notes blocker; #22,
#26–#36 remain open as applicable follow-up.

## Phase 79 — Accept Dogfood Evidence and Final v0.1.0-readonly Release Gate

Status: complete. Phase commit pushed.

Goal: accept Phase 78 copied/disposable-data dogfood evidence, create conservative `v0.1.0-readonly`
release notes, run the final release gate, update release/status artifacts, and close satisfied
release-blocker issues without publishing a tag or GitHub release.

Artifacts:

- `docs/release/v0.1.0-readonly-notes.md` — conservative release notes: pre-alpha, read-only by
  default, not production-ready, not security-audited, test copied/disposable books first, no
  SaaS/GnuCash replacement/collaborative-editing claim, no broad compatibility guarantee, writes
  disabled by default.
- `docs/release/v0.1.0-readonly-checklist.md` — final checklist status and Phase 79 evidence.
- `docs/release/v0.1.0-readonly-final-gate.md` — final gate verdict: ready for publication as a
  separate explicit next step.
- `docs/handoff/phase-79.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — release/status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default; controlled
writes remain experimental/post-MVP and disabled by default. Phase 79 did not enable writes, add
features, start v0.2 work, publish a tag/release, claim production readiness/security audit, claim
collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime
artifacts.

Release result: Phase 78 dogfood evidence was accepted for #25 because it used copied/disposable
data and passed Docker/Caddy browser dogfood, API smoke, CSV export, hidden write UI, and disabled
write probes. `v0.1.0-readonly` is ready for a separate explicit publication step. No v0.1 tag or
GitHub release exists yet.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config
validation, `git diff --check`, GitHub Actions CI, v0.1 tag lookup, and GitHub release lookup are
recorded in the Phase 79 handoff/final gate.

Related issues: GitHub #24 was closed as satisfied by release notes. GitHub #25 was closed as
satisfied by accepted Phase 78 copied/disposable-data runtime dogfood. GitHub #37 remains
closed/fixed. GitHub #22 and #26–#36 remain open as non-blocking follow-up for broader
hardening/future releases.

## Phase 80 — Publish v0.1.0-readonly Pre-release

Status: complete. Annotated tag and GitHub pre-release published; status docs committed and pushed.

Goal: perform the narrow publish-only `v0.1.0-readonly` phase after the Phase 79 release gate
verdict was ready for publication.

PM decision: publish exactly the existing release artifact on the Phase 79 gate commit. Do not
expand scope, add writes, start v0.2 work, create an audit-only phase, or change the conservative
release language.

Publication evidence:

- Annotated git tag: `v0.1.0-readonly`.
- Tagged commit: `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` (`docs: record phase 79 ci result`).
- Remote tag: `refs/tags/v0.1.0-readonly` pushed to `origin`.
- GitHub pre-release:
  https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly
- Release notes source: `docs/release/v0.1.0-readonly-notes.md`.
- Published at: `2026-05-18T06:04:26Z`.

Artifacts updated after publication:

- `README.md` — current release/status links now point to `v0.1.0-readonly`.
- `CHANGELOG.md` — Unreleased Phase 80 publication evidence entry.
- `PROJECT_STATUS.md` — baseline advanced through Phase 80 and next work guidance updated.
- `docs/handoff/phase-80.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default; controlled
writes remain experimental/post-MVP and disabled by default. Phase 80 did not enable writes, add
application behavior beyond publishing the existing release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts.

Test and release verification results are recorded in `docs/handoff/phase-80.md`. Local required
checks passed before publication, Phase 79 main-branch CI was green before tagging, the v0.1
tag/release absence was verified before publication, and the tag/release presence was verified after
publication.

Related issues: no issues were closed in Phase 80. Open follow-up issues #22 and #26–#36 remain
non-blocking for this conservative pre-alpha read-only publication.

## Phase 81 — Default-book Seed Log Redaction

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open release-hardening
backlog by fixing GitHub #27 without starting audit-only work, write-mode work, a new tag/release,
or v0.2 planning.

PM decision: choose #27 because it is low-risk, concrete, testable, post-release security/logging
hardening. The expected result is a tested behavior change: default-book seed logs must not expose
full filesystem paths, connection URIs, hosts, usernames, passwords/tokens, or query parameters.

Artifacts:

- `apps/api/app/services/seed.py` — added `_safe_book_log_label()` and changed default-book seed
  logging/name derivation to use sanitized filename/label for log-visible data while preserving the
  configured path/URI in `Book.uri_or_path`.
- `apps/api/tests/test_seed.py` — added regression tests for redacting full filesystem paths and
  connection URI details from seed logs.
- `docs/handoff/phase-81.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 81
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts.

Verification result: backend tests, frontend check/auth-routes/build, Docker Compose config
validation, `git diff --check`, release state verification, pushed commit verification, and clean
working tree verification are recorded in `docs/handoff/phase-81.md`.

Related issues: GitHub #27 closed as completed with evidence. Open follow-up issues #22, #26,
#28–#36 remain non-blocking backlog for later narrow phases.

## Phase 82 — Read-only Multi-book Boundary Regression Coverage

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open
read-only/release-hardening backlog by satisfying GitHub #35 with backend regression coverage,
without starting audit-only work, write-mode work, a new tag/release, or v0.2 planning.

PM decision: choose #35 because it is low-risk, concrete, testable, and protects the read-only
multi-book boundary after the v0.1.0-readonly publication. The expected result is a tested
safety/behavior guard: archived books must be hidden/blocked, and unauthorized users must be denied
across book-aware read-only route families before any GnuCash data is exposed.

Artifacts:

- `apps/api/tests/test_multi_book_access.py` — added an archived-book fixture with explicit user
  access, regression coverage that `GET /books` excludes archived books, `GET /books/{book_id}`
  returns `404` for archived books, and parametrized coverage for unauthorized `403` / archived
  `404` behavior across accounts, transactions, CSV export, account transactions, and all book-aware
  report route families.
- `docs/handoff/phase-82.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 82
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts.

Verification result: targeted multi-book tests, backend tests, frontend check/auth-routes/build,
Docker Compose config validation, `git diff --check`, release state verification, pushed commit
verification, and clean working tree verification are recorded in `docs/handoff/phase-82.md`.

Related issues: GitHub #35 closed as completed with evidence. Open follow-up issues #22, #26,
#28–#34, and #36 remain non-blocking backlog for later narrow phases.

## Phase 83 — Frontend Decimal-string Money Display Hardening

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open
read-only/release-hardening backlog by satisfying GitHub #34 with frontend decimal-string money
display helpers, without starting audit-only work, write-mode work, a new tag/release, or v0.2
planning.

PM decision: choose #34 because it is low-risk, concrete, testable, and aligns the frontend
read-only UI with the project money rule. The expected result is a tested user-facing/display
hardening change: frontend amount/balance/total/net decisions should not convert money strings
through JS `Number()`.

Artifacts:

- `apps/web/src/lib/money.js` — added decimal-string parse/compare/sign/percentage helpers using
  `BigInt` rather than JS `Number()` for money strings.
- `apps/web/scripts/test-money-strings.mjs` and `apps/web/package.json` — added lightweight helper
  coverage via `npm run test:money-strings`.
- `apps/web/src/lib/components/SummaryGrid.svelte`, `RecentTransactions.svelte`,
  `CashflowSummary.svelte`, `ExpensesByAccount.svelte`, and `TransactionFilters.svelte` — replaced
  money-string `Number()` decisions with decimal-string helpers for sign colors/trends, expense bar
  widths, and client-side amount-range prevalidation.
- `docs/handoff/phase-83.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 83
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts.

Verification result: helper tests, frontend check/auth-routes/build, backend tests, Docker Compose
config validation, `git diff --check`, release state verification, pushed commit verification, and
clean working tree verification are recorded in `docs/handoff/phase-83.md`.

Related issues: GitHub #34 closed as completed with evidence. Open follow-up issues #22, #26,
#28–#33, and #36 remain non-blocking backlog for later narrow phases.

## Phase 84 — CSV Export Truncation and Timeout Behavior

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open
read-only/release-hardening backlog by satisfying GitHub #32 with tested CSV export
cap/truncation/timeout behavior, without starting audit-only work, write-mode work, a new
tag/release, or v0.2 planning.

PM decision: choose #32 because it is low-risk, concrete, testable, and improves a
user/operator-facing read-only export boundary after the v0.1.0-readonly publication. The expected
result is a tested maintenance/UX behavior: CSV export remains capped at 10,000 rows, reports
whether the filtered set was truncated, documents/labels synchronous timeout behavior, and tells
users to narrow filters if a large export times out.

Artifacts:

- `apps/api/app/routers/transactions.py` — successful CSV exports now include `X-CSV-Export-Limit`,
  `X-CSV-Export-Total`, `X-CSV-Export-Truncated`, and `X-CSV-Export-Timeout-Policy` response
  headers.
- `apps/api/tests/test_transaction_export.py` — added disposable fake-data regression coverage for
  truncated and non-truncated CSV export responses.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` — forwards the CSV export
  metadata headers through the SvelteKit/browser download proxy.
- `apps/web/scripts/test-auth-routes.mjs` — verifies the proxy keeps forwarding the export metadata
  headers.
- `apps/web/src/routes/transactions/+page.svelte` — user-facing CSV export status now says large
  exports are synchronous and should be narrowed if they time out.
- `docs/transactions-filters.md` — documents the 10,000-row cap, truncation headers, and synchronous
  request-timeout policy.
- `docs/handoff/phase-84.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 84
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts.

Verification result: targeted CSV export tests, frontend auth-route/proxy checks, frontend
check/build, backend tests, Docker Compose config validation, `git diff --check`, release state
verification, pushed commit verification, and clean working tree verification are recorded in
`docs/handoff/phase-84.md`.

Related issues: GitHub #32 closed as completed with evidence. Open follow-up issues #22, #26,
#28–#31, #33, and #36 remain non-blocking backlog for later narrow phases.

## Phase 85 — Post-v0.1 Personal Copied-Book Dogfood

Status: complete with blocker recorded. Phase commit pushed.

Goal: attempt exactly the roadmap Phase 85 dogfood pass against a copied personal GnuCash SQL book
outside git, using the published/read-only app posture, without analyst/auditor involvement, write
enablement, private-data commits, a new release/tag, or v0.2 work.

PM decision: run only the safe copied personal-book dogfood scenario. The original book must remain
untouched, writes must stay disabled, access must be local-only, and no screenshots/exports/private
financial data may be committed. If no safe copied personal SQL book is available, record that as a
blocker rather than pretending a real-book pass succeeded.

Artifacts:

- `docs/dogfood/phase-85-personal-copied-book-results.md` — redacted dogfood result artifact. It
  records that no safe copied personal SQL book was available to this environment outside git, so
  the real-book Docker/browser/API checklist is blocked rather than passed.
- `docs/handoff/phase-85.md` — PM/engineer handoff, safety scope, blocked runtime checklist,
  verification, issue, commit, and push evidence.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 85
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real
financial/secrets/runtime artifacts. No private account names, private amounts, private paths,
screenshots, CSV exports, `.env`, app DB, backup, real GnuCash book, token, cert, or key were
committed.

Verification result: required backend tests, frontend check/auth-routes/build, Docker Compose config
validation, `git diff --check`, release state verification, pushed commit verification, and clean
working tree verification are recorded in `docs/handoff/phase-85.md`. Docker/browser/API smoke
against the copied personal book is explicitly blocked because no safe copied personal SQL book is
available in this environment.

Related issues: GitHub #38 opened to track rerunning the copied personal-book dogfood checklist when
a safe copied personal SQL book is available. No existing issue was closed without runtime evidence.

## Phase 86 — Fix Phase 85 Dogfood Blockers

Status: complete. Phase commit pushed.

Goal: triage Phase 85 findings and fix only the highest-priority concrete dogfood blocker, without
analyst/auditor involvement, new features, write-mode work, broad refactor, v0.2 work, or a new
release/tag.

PM decision: Phase 85 produced no reproducible application bug such as a dashboard crash,
transaction-detail failure, filter crash, CSV export failure, wrong empty state, or account display
bug. The only finding was a release-blocking dogfood input/environment blocker: no safe copied
personal GnuCash SQL book was available outside git. Because there was no code bug to fix, Phase 86
used the allowed maintenance fallback and added a narrow tested preflight helper for #38 so future
copied-book dogfood attempts can classify candidate availability safely before runtime work begins.

Artifacts:

- `apps/api/app/dogfood_preflight.py` — redacted helper that classifies a copied-book candidate as
  blocked/ready without opening the book or exposing full paths.
- `apps/api/scripts/check_dogfood_book_candidate.py` — operator CLI wrapper that prints only
  filename-level safe summaries and exits non-zero when the candidate is blocked.
- `apps/api/tests/test_dogfood_preflight.py` — regression tests for missing candidate, candidate
  inside git, and valid outside-repo candidate, including private-path redaction assertions.
- `docs/handoff/phase-86.md` — PM/engineer handoff with triage, safety, verification, issue, commit,
  and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — post-release status sync.

Safety result: writes remain disabled by default. The helper does not parse, copy, export,
screenshot, or commit any GnuCash book data; it only checks path existence and whether the candidate
is outside the git working tree. No real financial data, `.env`, app DB, backup, secret, token,
private key, private screenshot, CSV export, or real GnuCash book was committed. No v0.2 work or
release publication was done.

Verification result: the new regression test and required backend/frontend/docker/git checks are
recorded in `docs/handoff/phase-86.md`. Docker/browser/API personal-book dogfood remains blocked
until #38 has a safe copied book; Phase 86 does not claim a real-book pass.

Related issues: GitHub #38 updated with Phase 86 triage and preflight-helper evidence, but kept open
because the real copied personal-book dogfood rerun still requires a safe copied book.

## Phase 87 — Large-book Read-only Benchmark v1

Status: complete. Phase commit pushed.

Goal: add a generated synthetic large-book benchmark for read-only API paths without using private
books, enabling writes, publishing a release, or starting v0.2 work.

Artifacts:

- `apps/api/app/performance/large_book_benchmark.py` — synthetic benchmark fixture and authenticated
  read-only API measurement helper.
- `apps/api/scripts/run_large_book_benchmark.py` — local benchmark CLI.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for benchmark plan/scope.
- `docs/performance/phase-87-large-book-benchmark.md` — benchmark evidence and limitations.
- `docs/handoff/phase-87.md` — PM/engineer handoff.

Safety result: generated synthetic data only, no committed generated binary fixture, no write-mode
work, no v0.2 work, no tag/release.

Related issues: GitHub #30 closed as completed. GitHub #39 opened for CSV export row-count/header
mismatch.

## Phase 88 — Account with Many Splits Performance Test

Status: complete. Phase commit pushed.

Goal: extend the synthetic read-only benchmark to include many-splits transaction detail and account
transaction pagination evidence.

Artifacts:

- `apps/api/app/performance/large_book_benchmark.py` — now creates one 60-split transaction and
  measures account-detail pagination plus many-splits transaction detail.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for many-splits scope.
- `docs/performance/phase-88-many-splits-benchmark.md` — benchmark evidence and limitations.
- `docs/handoff/phase-88.md` — PM/engineer handoff.

Safety result: generated synthetic data only, no committed generated binary fixture, no write-mode
work, no v0.2 work, no tag/release.

Related issues: GitHub #31 closed as completed. GitHub #39 remains open for CSV export
row-count/header mismatch.

## Phase 89 — Dashboard Aggregate Performance and Correctness Pass

Status: complete. Phase commit pushed.

Goal: make dashboard aggregates less likely to be slow or misleading on larger books by hardening
conservative reporting claims and expanding synthetic benchmark coverage.

PM decision: implement exactly the roadmap Phase 89 dashboard aggregate pass. Dashboard claims must
remain conservative: no fake currency conversion, base-currency-only reporting, visible
limitations/empty/error behavior, and measured read-only aggregate endpoints rather than broad
performance claims.

Artifacts:

- `apps/api/app/routers/reports.py` — centralized dashboard report date parsing/range validation and
  clear `422` client errors.
- `apps/api/app/services/gnucash_book.py` — summary DTO now includes
  `reporting_basis="base_currency_only"`, `includes_currency_conversion=false`, and explicit
  no-conversion/mixed-currency limitation text.
- `apps/api/app/schemas/gnucash.py` — summary schema includes the conservative reporting metadata.
- `apps/api/tests/test_reports.py` — regression coverage for empty summary, mixed-currency
  exclusion, date error quality, cashflow, expenses, recent transactions, and book-aware report
  endpoints.
- `apps/api/app/performance/large_book_benchmark.py` — benchmark now covers dashboard summary,
  cashflow-by-month, expenses-by-account, and recent-transactions.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for the expanded dashboard
  benchmark plan.
- `apps/web/src/lib/api/types.ts` — frontend summary type includes conservative reporting metadata.
- `apps/web/src/routes/dashboard/+page.svelte` — dashboard renders the summary limitation visibly
  above summary cards.
- `docs/performance/phase-89-dashboard-aggregate-benchmark.md` — benchmark command, local results,
  findings, and limitations.
- `docs/handoff/phase-89.md` — PM/engineer handoff.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — status sync.

Benchmark result: the 1,000-transaction synthetic TestClient benchmark returned `200` for dashboard
summary, cashflow-by-month, expenses-by-account, and recent-transactions. Summary and
expenses-by-account were below one second locally; cashflow-by-month and recent-transactions were
also below one second locally but remain service-layer scans and are not a production scalability
guarantee.

Safety result: generated synthetic data only. `GNUCASH_WRITES_ENABLED=false` remains the
documented/configured default. Phase 89 did not enable writes, add write scope, publish a new
tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative
editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: targeted report/benchmark tests and required backend/frontend/docker/git checks
are recorded in `docs/handoff/phase-89.md`.

Related issues: GitHub #33 closed as completed with Phase 89 evidence. GitHub #39 remains open for
the existing CSV export row-count/header mismatch.

## Phase 94 — Post-v0.1 Maintenance Release Decision

Status: complete. Phase commit pushed.

Goal: decide whether enough post-`v0.1.0-readonly` changes exist to prepare `v0.1.1-readonly`,
without analyst/auditor involvement, audit-only artifacts, tag/release publication, write-mode
enablement, v0.2 work, or private data artifacts.

PM decision: more fixes are required before maintenance release. Do not prepare or publish
`v0.1.1-readonly` yet.

Artifacts:

- `docs/release/v0.1.1-readonly-decision.md` — durable maintenance-release decision artifact
  reviewing Phases 81–93, release/tag state, open blockers, and minimum requirements before a future
  release-prep phase.
- `docs/handoff/phase-94.md` — PM/engineer handoff with decision, safety scope, verification, GitHub
  state, commit, and push evidence.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — status sync through Phase 94.

Release decision result: the post-release change set is meaningful, including seed-log redaction,
multi-book boundary hardening, money-display hardening, CSV export header/truncation signaling,
benchmark evidence, transaction-filter UX, read-only book metadata UI, compatibility metadata
collection, and a narrow Russian localization slice. However, GitHub #39 remains an open read-only
CSV export correctness blocker because benchmark evidence repeatedly showed the CSV body capped at
500 rows while export headers report a 10,000-row cap and `truncated=false`. Fix #39 with regression
coverage before creating `v0.1.1-readonly` notes/checklist.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 94
did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production
readiness/security audit, claim broad compatibility, or add real financial/secrets/runtime
artifacts.

Verification result: required backend/frontend/docker/git checks plus release/tag/open-issue
verification are recorded in `docs/handoff/phase-94.md`.

Related issues: GitHub #39 updated with Phase 94 release-decision evidence and kept open as the
maintenance-release prep blocker. GitHub #38 remains open for the separate copied personal-book
dogfood rerun when a safe copied SQL book is available.

## Phase 97 — v0.1.1-readonly Release-Prep Checklist and Notes

Status: complete. Phase commit pushed.

Goal: prepare conservative `v0.1.1-readonly` release notes and a release-prep checklist after the
Phase 95 GitHub #39 CSV export fix and Phase 96 synthetic benchmark confirmation, without publishing
a tag/release.

PM decision: release-prep only. Do not publish `v0.1.1-readonly`, do not run the final release gate
in this phase, do not claim production readiness/security audit/broad compatibility/personal-book
dogfood success, and keep #38 separate unless a safe copied personal SQL book becomes available
outside git.

Artifacts:

- `docs/release/v0.1.1-readonly-notes.md` — originally prepared in Phase 97 as conservative release
  notes for a future GitHub pre-release; Phase 105 later corrected this file after the release was
  published.
- `docs/release/v0.1.1-readonly-checklist.md` — release-prep checklist separating completed Phase
  95/96 evidence, required Phase 98 gate checks, intentionally unauthorized publication steps, known
  limitations, and open issues.
- `docs/handoff/phase-97.md` — PM/engineer handoff with implementation summary, safety statement,
  verification, release/GitHub state, commit, and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status sync through Phase 97.

Release-prep result: at the time of Phase 97, the candidate notes/checklist summarized
post-`v0.1.0-readonly` maintenance value, especially the Phase 95 CSV export fix and Phase 96
synthetic benchmark confirmation, and correctly stated the then-current state: `v0.1.1-readonly` had
not yet been published and still required Phase 98 release-gate verification before any authorized
publication. Phase 105 later corrected the notes after publication.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 97
did not enable writes, add write scope, publish a tag/release, start v0.2 work, claim production
readiness/security audit/broad compatibility/personal-book dogfood success, or add real
financial/secrets/runtime artifacts.

Verification result: `git diff --check` passed. Backend/frontend/Docker checks were not run because
Phase 97 changed only docs/release/status/handoff artifacts and did not touch backend, frontend, or
config code; those checks are required for Phase 98 release-gate verification.

Related issues: GitHub #39 remains closed based on Phase 95/96 synthetic evidence. GitHub #38
remains open/blocked pending a safe copied personal GnuCash SQL book outside git.

## Phase 98 — v0.1.1-readonly Release-Gate Verification

Status: complete. Phase commit pushed.

Goal: run the final `v0.1.1-readonly` release-gate verification before any publication and record an
honest ready/blocked verdict artifact.

PM decision: release-gate only. Do not publish `v0.1.1-readonly`, do not create a tag/release, do
not enable writes, do not broaden release claims, and keep #38 separate unless a safe copied
personal SQL book becomes available outside git.

Artifacts:

- `docs/release/v0.1.1-readonly-final-gate.md` — final release-gate artifact with branch/HEAD
  evidence, command summary, GitHub Actions/release-state evidence, read-only/write-disabled
  confirmation, sensitive-data hygiene summary, and verdict.
- `docs/handoff/phase-98.md` — PM/engineer handoff with implementation summary, safety statement,
  verification, release/GitHub state, commit, and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status sync through Phase 98.

Release-gate result: at the time of Phase 98, the verdict was `Ready for later authorized publish
phase`. Backend, frontend, Docker config, GitHub Actions recent `main` runs, tag/release absence,
issue-state, disabled-write/read-only safety, and hygiene checks passed. `v0.1.1-readonly` was not
yet published in Phase 98 and publication still required a later explicit publish authorization.
Phase 105 later corrected release/status docs after the release was published.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 98
did not enable writes, add write scope, publish a tag/release, start v0.2 work, claim production
readiness/security audit/broad compatibility/personal-book dogfood success, or add real
financial/secrets/runtime artifacts.

Verification result: backend full suite passed (`329 passed, 27 warnings`); frontend
check/auth-routes/build passed; Docker Compose config validation passed; `git diff --check` passed
before commit; GitHub Actions recent `main` runs were successful; at that Phase 98 point no
`v0.1.1-readonly` local tag or GitHub release existed.

Related issues: GitHub #39 remains closed based on Phase 95/96 synthetic evidence and Phase 98
release-gate checks. GitHub #38 remains open/blocked pending a safe copied personal GnuCash SQL book
outside git.

## Phase 105 — v0.1.1-readonly Release/Docs Correction

Status: complete. Phase commit pushed.

Goal: fix the release/docs drift found in `docs/audits/2026-05-19-analyst-report.md` after
`v0.1.1-readonly` had already been published while local/public notes still described it as
release-prep-only.

PM decision: documentation/release-metadata correction only. Do not change product code, do not
create a new tag/release/package, do not move the existing tag, do not enable or expand write mode,
and do not commit private financial data or secrets.

Artifacts:

- `README.md` — now names `v0.1.1-readonly` as the current public read-only pre-alpha release while
  preserving pre-alpha/read-only/not-production/security warnings.
- `PROJECT_STATUS.md` — records that `v0.1.1-readonly` is published, tag/release exists, and the tag
  points after Phase 104.
- `CHANGELOG.md` — adds a `0.1.1-readonly` release section with the actual tag scope, including
  Phase 103/104 read-only transaction date-preset and split-memo search changes.
- `docs/release/v0.1.1-readonly-notes.md` — corrected from release-prep language to honest published
  pre-release notes.
- GitHub release body for `v0.1.1-readonly` — synchronized in place from the corrected local notes
  with `gh release edit`; no new release or tag was created.
- `docs/handoff/phase-105.md` — implementation/evidence/checks/results updated.

Release/docs correction result: stale release-state claims were corrected. The current public
release is `v0.1.1-readonly`, published as a GitHub pre-release on 2026-05-18. The tag points to
`a4d04150c043ad4da3dea577b30ed7ffd2032df0` after Phase 104, so the release notes now explicitly
include Phase 103/104 read-only transaction-filter/search changes.

Lesson/guardrail: always update release/status documentation immediately in the same phase as any
factual release-state change. Do not leave README, PROJECT_STATUS, CHANGELOG, local release notes,
or GitHub release notes to be corrected later.

Safety result: no product code was changed. No tag, release, package, app behavior, backend/frontend
route, Docker runtime config, write service, or write flag was changed.
`GNUCASH_WRITES_ENABLED=false` remains the documented/configured default; controlled writes remain
post-MVP/experimental. No real/private financial data, GnuCash books, app DBs, backups, `.env`,
screenshots, exports, secrets, tokens, certs, keys, private paths, account names, transaction
descriptions, memos, or amounts were committed.

Verification result: docs-only validation passed, including `git diff --check`, changed-file scope
check, stale release-state grep, GitHub release view after sync, and
`JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config
--quiet`. Full backend/frontend suites were intentionally not run because Phase 105 changed only
release/status docs and GitHub release metadata, not product code.

## Phase 114 — Synthetic Browser Dogfood Refresh

Status: complete. Phase commit pushed.

Goal: rerun a current Docker/Caddy browser/UI and API dogfood pass using synthetic/disposable data
after the UX/filter/books/scheduled/localization changes, without using personal books, enabling
writes, publishing a release, or committing runtime artifacts.

PM decision: execute analyst roadmap Phase 9 as a practical dogfood artifact. Use
generated/disposable data only; record redacted evidence; treat failures as narrow bugs or explicit
blockers; keep #38 separate for future personal copied-book dogfood.

Artifacts:

- `scripts/smoke/read-only-browser-dogfood.py` — durable headless Chromium/CDP browser dogfood
  helper for local Docker/Caddy deployments. It checks login, protected redirects, authenticated
  core pages, read-only write-UI hiding, transaction filters, account/transaction detail navigation,
  CSV export through the authenticated UI/proxy route, and no screenshot/download/export artifacts.
- `docs/dogfood/phase-114-synthetic-browser-dogfood.md` — redacted runtime evidence for
  Docker/API/browser dogfood on synthetic data.
- `docs/handoff/phase-114-pm-brief.md` and `docs/handoff/phase-114.md` — PM brief and engineer
  handoff.
- `PROJECT_STATUS.md` and `CHANGELOG.md` — status sync through Phase 114.

Dogfood result: local Docker/Caddy ran at `http://127.0.0.1:18080` with
`GNUCASH_WRITES_ENABLED=false` and a synthetic/disposable fixture copy. API smoke passed health,
login, `/auth/me`, books, accounts, transactions, transaction detail, CSV export, reports summary,
and disabled validate/create/patch probes returning 403. Browser dogfood passed login, protected
redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction
detail, authenticated CSV export, httpOnly-cookie invisibility to `document.cookie`, and no
screenshot/download/export file creation.

Safety result: no personal/private book was used or searched for. No screenshot, CSV export, app DB,
GnuCash book, backup, `.env`, secret, token, cert, key, private path, real account name, real
transaction description, real memo, real amount, or personal financial data was committed. Writes
remain disabled by default; controlled writes remain post-MVP/experimental; no tag/release/package
was published; no v0.2 work was started.

Verification result: Docker Compose config validation, API smoke, browser dogfood, backend full
tests, frontend route checks/check/build, and `git diff --check` are recorded in
`docs/handoff/phase-114.md`.

Related issues: GitHub #11/#12/#13 updated with Phase 114 synthetic dogfood evidence for the
recently touched surfaces. GitHub #38 remains open/blocked because this was not personal copied-book
dogfood.

## Phase 118 — Transaction Table Column Width and Horizontal Scroll Fix

Status: complete. Phase commit pushed.

Goal: stabilize desktop transaction table columns and remove needless horizontal shifting while
keeping mobile transaction cards usable.

Artifacts:

- `apps/web/src/lib/components/TransactionTable.svelte` — fixed-width desktop column contract for
  Date, Description, Account, Counter account, and Amount; long descriptions/account names truncate
  safely with title text; mobile table remains hidden in favor of existing cards.
- `apps/web/src/lib/components/AccountTree.svelte` and
  `apps/web/src/lib/components/AccountTreeNode.svelte` — desktop account tree columns now use
  bounded shrinkable grid sizing and truncation to avoid narrow desktop overflow.
- `apps/web/scripts/test-auth-routes.mjs` — static regression checks for transaction table no-scroll
  sizing and account tree narrow-layout safeguards.
- `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/handoff/phase-118.md` — phase status and handoff
  synchronized.

Safety result: frontend CSS/UI-only changes. No API, data model, GnuCash adapter, schema, write
path, auth storage, release/tag/package, real/private book, app DB, backup, screenshot, CSV export,
`.env`, secret, token, cert, key, private path, account name, transaction description, memo, amount,
or personal financial data was added. `GNUCASH_WRITES_ENABLED=false` remains default and controlled
writes remain post-MVP/experimental.

Verification result: backend full tests, frontend check/auth-routes/build, Docker Compose config
validation, and `git diff --check` passed.

## Phase 127 — GnuCash Desktop Compatibility Evidence Refresh

Status: complete. Phase commit pushed.

Goal: refresh GitHub #22 GnuCash Desktop compatibility evidence, or document the exact blocker
without fabricating Desktop-generated fixture claims.

Artifacts:

- `docs/gnucash-compatibility.md` — compatibility matrix now includes Phase 127 as a blocker row: no
  Desktop-generated fixture was produced because local `gnucash` and `gnucash-cli` tooling are
  unavailable.
- `docs/gnucash-version-fixture-plan.md` — records Phase 127 local evidence and a manual synthetic
  Desktop-fixture procedure for a disposable environment with Desktop/CLI installed.
- `apps/api/tests/test_compatibility_fixture_v1.py` — adds regression coverage that missing Desktop
  tooling is represented as a safe blocker, not Desktop evidence, and does not serialize private
  paths.
- `docs/handoff/phase-127.md` — implementation/evidence/checks/results.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status sync through Phase 127.

Compatibility result: `gnucash --version` and `gnucash-cli --version` both returned
command-not-found in this execution environment. The safe tooling probe reported
`desktop_tooling_available=false`. Therefore no synthetic Desktop-generated GnuCash book was
created, no new fixture binary was committed, and GitHub #22 remains blocked on a disposable
environment that actually has GnuCash Desktop/CLI available.

Safety result: no real/private GnuCash books were used or searched for. No app DB, backup, `.env`,
secret, token, cert, key, screenshot, CSV/media/export, private path, account name, transaction
description, memo, amount, SQL dump, fixture binary, tag, release, or package was committed.
`GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` write gate was not changed.

Verification result: targeted compatibility test, backend full suite, frontend check/build, `git
diff --check`, and sensitive tracked-file scan passed. Docker Compose config validation also passed
as an extra safety check.

Related issues: GitHub #22 updated with Phase 127 blocker/manual-procedure evidence and kept open
until real Desktop-generated synthetic fixture evidence exists.

## Phase 129 — Write-alpha Recovery Documentation and Maintainer Review Gate

Status: complete. Phase commit pushed.

Goal: close the write-alpha documentation gap before any future real-user write consideration by
adding recovery and maintainer-review documentation only.

Artifacts:

- `docs/write-alpha-recovery-procedure.md` — experimental write-alpha recovery procedure for
  synthetic/disposable books only, covering containment, backup selection, stale-lock cleanup,
  restore, read-only integrity checks, and damaged-book triage.
- `docs/write-alpha-maintainer-checklist.md` — checkable maintainer gate for default-disabled
  config, `APP_ENV=test` route gating, disposable fixture scope, lifecycle evidence, recovery docs,
  and sensitive-data hygiene.
- `README.md` — controlled-write warning now explicitly says write-alpha is experimental, disabled
  by default, test-environment-gated when enabled, synthetic/disposable-first, and not
  production-safe.
- `docs/v0.2-controlled-writes.md` — readiness gate updated through Phase 129 and remaining gaps
  clarified.
- `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-129.md` — status and handoff
  synchronized.

Safety result: docs-only phase. No product code, runtime config, route, service, frontend behavior,
write default, `APP_ENV=test` gate, tag, release, package, upload, app DB, GnuCash book, backup,
`.env`, secret, token, credential, cert, key, screenshot, CSV/media/private export, private path, or
real/private financial data was added or changed. No real-book write safety is claimed.

Verification result: backend full tests, frontend check/build, `git diff --check`, sensitive
tracked-file scan, and manual markdown review passed.

## Phase 130 — Write-alpha PATCH Transaction Hardening

Status: complete. Phase commit pushed.

Goal: harden the experimental transaction edit/PATCH write-alpha path with the full safety lifecycle
while keeping writes disabled by default and test-fixture-only when explicitly enabled.

Artifacts:

- `apps/api/app/services/gnucash_write.py` — PATCH now distinguishes missing transactions from
  validation failures before lock/backup, exposes a narrow `_do_patch_transaction` helper for
  description/date/split-memo-only metadata edits, and preserves backup-path propagation for
  post-backup PATCH failures.
- `apps/api/app/routers/transactions.py` — failed PATCH audits now record backup paths from
  `GnuCashWriteError` when failures occur after backup creation.
- `apps/api/tests/test_transaction_writes.py` — route-level copied/disposable fixture coverage for
  successful PATCH backup/audit/lock lifecycle, 404 missing transaction before mutation/backup,
  validation failure with no mutation/no backup/no lock leak/failed audit, synthetic post-backup
  failure with intact backup and released lock, and concurrent PATCH+CREATE lock contention.
- `docs/v0.2-controlled-writes.md` — Phase 130 readiness gate and PATCH lifecycle evidence
  documented without any real-book safety claim.
- `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-130.md` — status and
  handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the default and the `APP_ENV=test` write-alpha
gate was not weakened. Tests use only copied/disposable fixtures under `tmp_path`; no real/private
GnuCash books, app DBs, backups, `.env`, secrets, tokens, certs, keys, CSV/media/private exports,
screenshots, or private financial data were committed. No DELETE/import/recurring/account-write,
tag, GitHub release, package, upload, production-readiness claim, audited-security claim, or
real-book write-safety claim was added.

Verification result: targeted transaction write tests, backend full tests, frontend
check/auth-routes/build, Docker Compose config validation, `git diff --check`, and sensitive
tracked-file scan passed.

## Phase 132 — v0.2.0-writealpha Release Gate Artifacts and Later Authorized Publication

Status: complete. Phase commit pushed after local verification.

Goal: prepare release-gate artifacts for `v0.2.0-writealpha`; a later explicit Val authorization
allowed publishing the tag/GitHub pre-release without changing write-mode defaults or product code.

Artifacts:

- `docs/release/v0.2.0-writealpha-notes.md` — conservative notes for the authorized pre-release;
  clearly states pre-alpha, experimental, disabled by default, `APP_ENV=test` write gate,
  synthetic/disposable fixture evidence only, not production-ready, not security-audited, no direct
  public-internet exposure, and no real-book write-safety claim.
- `docs/release/v0.2.0-writealpha-checklist.md` — release-prep checklist with candidate scope,
  evidence from Phases 126–131, required checks, reserved publish commands, safety checklist, and
  known limitations.
- `docs/release/v0.2.0-writealpha-final-gate.md` — final-gate artifact recording clean tracked
  tree/HEAD-origin parity before Phase 132 artifacts, tag/release absence, recent GitHub Actions
  status, backend/frontend/docker/git checks, sensitive tracked-file scan, and later publication
  verdict `Authorized for publication after Phase 132 gate — pre-release published`.
- `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-132.md` — status and
  handoff synchronized.

Safety result: Phase 132 itself was docs/release/status-only; the later authorized publication
created only the git tag and GitHub pre-release. No package, upload,
backend/frontend/config/product-code change, write default change, `APP_ENV=test` gate weakening,
app DB, GnuCash book, backup, `.env`, secret, token, credential, cert, key, CSV/private export,
screenshot, private path, or real/private financial data was added. `GNUCASH_WRITES_ENABLED=false`
remains default.

Verification result: backend full tests, frontend check/auth-routes/build, Docker Compose config
validation, `git diff --check`, refined sensitive tracked-file scan, tag/release absence checks, and
recent GitHub Actions state check passed.

## Phase 134 — Read-only UX Skeleton Loading States

Status: complete. Phase commit pushed.

Goal: improve perceived performance on core read-only pages by adding skeleton loading states for
dashboard, accounts, transactions, and books, especially during active-book switching/navigation
data reloads.

Artifacts:

- `apps/web/src/lib/components/LoadingState.svelte` — extended from a generic spinner into
  accessible, animated skeleton variants for dashboard summary/cards/chart placeholders,
  account-tree rows, transaction filters/table/cards, and book-list cards.
- `apps/web/src/routes/dashboard/+page.svelte` — shows the dashboard skeleton while SvelteKit is
  navigating back to `/dashboard`, including book-switch reloads.
- `apps/web/src/routes/accounts/+page.svelte` — shows account-tree skeleton placeholders while
  `/accounts` data reloads.
- `apps/web/src/routes/transactions/+page.svelte` — shows filter/table/card skeleton placeholders
  while `/transactions` data reloads.
- `apps/web/src/routes/books/+page.svelte` — shows book-list skeleton placeholders while `/books`
  data reloads.
- `apps/web/scripts/test-auth-routes.mjs` — static route checks pin the structured skeleton variants
  and navigation-loading wiring.
- `docs/handoff/phase-134.md` and `PROJECT_STATUS.md` — phase status and handoff synchronized.

Safety result: frontend read-only UX only. No backend API, service, schema, GnuCash adapter, write
route, write service, write lock, audit, backup, runtime config, release/tag/package, real/private
book, app DB, backup, screenshot, CSV/private export, `.env`, secret, token, cert, key, private
path, account name, transaction description, memo, amount, or private financial data was added.
`GNUCASH_WRITES_ENABLED=false` remains default and controlled writes remain post-MVP/experimental.

Verification result: frontend route checks, frontend `svelte-check`, Docker Compose config
validation, `git diff --check`, and sensitive tracked-file scan passed.

## Phase 137 — Local Secure Deployment Hardening Guide

Status: complete. Phase commit pushed.

Goal: update and expand the safe deployment guide for localhost, LAN, and VPN self-hosting scenarios
without changing backend/frontend code or making production-readiness claims.

Artifacts:

- `docs/deployment/local-secure-deployment.md` — expanded CORS recommendations for
  localhost/LAN/VPN, JWT secret generation and conservative rotation guidance, app metadata DB
  backup procedure, and a concrete pre-deployment checklist.
- `.env.example` — comments now recommend fresh JWT secrets, rotation after
  exposure/shared-environment changes, and exact CORS origins for LAN/VPN testing.
- `docs/handoff/phase-137.md` — implementation/evidence/checks/results.
- `PROJECT_STATUS.md` — status sync through Phase 137.

Safety result: docs/config-example comments only. No backend/frontend product code, endpoint, write
route, write service, runtime default, release/tag/package, app DB, GnuCash book, backup, `.env`,
secret, token, cert, key, screenshot, CSV/private export, private path, account name, transaction
description, memo, amount, or private financial data was added. `GNUCASH_WRITES_ENABLED=false`
remains the documented default. The guide stays limited to pre-alpha localhost/LAN/VPN self-hosted
testing with test copies first and no production guarantee.

Verification result: targeted backend health tests passed, full backend suite passed (`377 passed,
32 warnings`), Docker Compose config validation passed, `git diff --check` passed, and safety grep
for production-readiness claims / real secret patterns in changed docs passed.

## Phase 138 — Public README/CHANGELOG/Roadmap Status Sync

Status: complete. Phase commit pushed.

Goal: synchronize README, Russian README, CHANGELOG, roadmap, project status, and handoff after
Phases 133–137 without changing backend/frontend code or publishing a release.

Artifacts:

- `README.md` — current status now says Phase 0–137 are complete, distinguishes the current
  read-only pre-alpha release from the published write-alpha pre-release, links current
  release/compatibility docs, and summarizes Phases 133–137.
- `README.ru.md` — synchronized public Russian status with the English README at summary level:
  current release posture, recent phases, safety boundaries, partial localization scope, and
  canonical docs links.
- `CHANGELOG.md` — added Unreleased entries for Phases 133–137.
- `docs/ROADMAP.md` — refreshed current release posture, recent maintenance phases, completed
  groups, near-term backlog posture, and explicit non-MVP boundaries.
- `docs/handoff/phase-138.md` — implementation/evidence/checks/results.
- `PROJECT_STATUS.md` — status sync through Phase 138.

Safety result: documentation/status only. No backend/frontend product code, endpoint, write route,
write service, runtime default, release/tag/package, app DB, GnuCash book, backup, `.env`, secret,
token, cert, key, screenshot, CSV/private export, private path, account name, transaction
description, memo, amount, or private financial data was added. `GNUCASH_WRITES_ENABLED=false`
remains the documented default. Docs remain pre-alpha, test-copies-first, not production-ready, not
security-audited, and with no real/private-book write-safety claim.

Verification result: targeted backend health tests passed, frontend `npm run check` passed, README
local-link check passed, README external public-link check passed with localhost example URLs
intentionally skipped, `git diff --check` passed, and safety scans over changed docs found no
private-data artifact or new production-readiness claim.

## Phase 140 — Maintenance Release Readiness Audit

Status: complete. Phase commit pushed after verification.

Goal: independently audit readiness for a possible `v0.1.4-readonly` maintenance release without
changing product code, creating a tag, publishing a release, or expanding write-alpha behavior.

Artifacts:

- `docs/audits/2026-05-19-phase-139-audit.md` — audit report with verdict `not ready`.
- `docs/handoff/phase-140.md` — implementation/evidence/checks/results.
- `PROJECT_STATUS.md` — status sync through Phase 140.

Audit result: the release-readiness verdict is `not ready`. Local write-gating checks, frontend
route checks, Docker Compose config validation, recent GitHub CI, disabled-by-default write
configuration, tracked sensitive-file hygiene, and roadmap Phases 1–3 / project Phases 133–135
documentation and test evidence passed. The blocker is release/status documentation drift:
`README.md` still states Phase 0–137 are complete and lists recent post-release maintenance only
through Phase 137, while `CHANGELOG.md` `Unreleased` lacks Phase 138/139 entries. This is a
release-documentation blocker, not a product-code or data-safety breach.

Safety result: audit/status docs only. No backend/frontend product code, endpoint, write route,
write service, runtime default, release/tag/package, app DB, GnuCash book, backup, `.env`, secret,
token, key, cert, screenshot, CSV/private export, private path, account name, transaction
description, memo, amount, or private financial data was added. `GNUCASH_WRITES_ENABLED=false`
remains the documented/configured default. Docs remain pre-alpha, test-copies-first, not
production-ready, not security-audited, and with no real/private-book write-safety claim.

Verification result: targeted disabled-write tests passed (`8 passed, 1 warning`); frontend `npm run
test:auth-routes` passed; Docker Compose config validation passed; latest five GitHub Actions `main`
CI runs were `completed success` after waiting for the Phase 139 run; tracked sensitive-file scan
found only intentional test fixtures and `data/app/.gitkeep`; `git diff --check` passed before
commit.

## Phase 141 — v0.1.4-readonly Release Artifact Preparation

Status: complete. Phase commit pushed after verification.

Goal: prepare conservative release artifacts for a possible `v0.1.4-readonly` maintenance
pre-release without creating a tag, GitHub release, package, upload, or write-mode change.

Artifacts:

- `docs/release/v0.1.4-readonly-notes.md` — pre-alpha/read-only release notes with explicit
  not-production-ready, not-security-audited, test-copy-first, no-public-internet, and
  no-safe-write-mode language.
- `docs/release/v0.1.4-readonly-checklist.md` — checkable release-prep checklist, candidate scope,
  evidence, safety checks, and publish commands reserved for a later explicit authorization phase.
- `docs/release/v0.1.4-readonly-final-gate.md` — final gate with verdict `Ready for later authorized
  publish phase — unpublished`.
- `README.md` — current status and release-readiness links synchronized through Phase 141, while
  keeping `v0.1.3-readonly` as the current public read-only release until a later publish phase.
- `CHANGELOG.md` — added the `[0.1.4-readonly]` candidate section and separated the existing
  published `v0.2.0-writealpha` write-alpha history.
- `PROJECT_STATUS.md` and `docs/handoff/phase-141.md` — status and handoff synchronized.

Release result: `v0.1.4-readonly` is prepared but unpublished. No tag, GitHub release, package,
uploaded artifact, product code, write-alpha expansion, runtime default, real/private data, or
release publication was created. Publication remains a separate future phase requiring explicit
authorization and immediate re-check of clean `main`, `HEAD == origin/main`, tag/release absence,
CI/local checks, `GNUCASH_WRITES_ENABLED=false`, and sensitive-data hygiene.

Safety result: documentation/release-status only. No backend/frontend product code, endpoint, write
route, write service, runtime default, app DB, GnuCash book, backup, `.env`, secret, token, key,
cert, screenshot, CSV/private export, private path, account name, transaction description, memo,
amount, or private financial data was added. `GNUCASH_WRITES_ENABLED=false` remains the
documented/configured default. Docs remain pre-alpha, test-copies-first, not production-ready, not
security-audited, and with no real/private-book write-safety claim.

Verification result: `cd apps/api && pytest tests/test_health.py tests/test_auth.py -q` passed (`17
passed, 1 warning`); `cd apps/web && npm run check` passed (`0 errors and 0 warnings`); `cd apps/web
&& npm run test:auth-routes` passed; Docker Compose config validation passed; tag/release absence
checks passed; `git diff --check` passed; tracked sensitive-file scan found only intentional
allowlisted fixtures/placeholders.

## Phase 142 — v0.1.4-readonly Release Gate and Authorized Publication

Status: complete. Phase commit pushed; tag and GitHub pre-release published after final gate.

Goal: perform the final release gate for `v0.1.4-readonly` and publish only if authorized and safe.

Artifacts:

- `docs/release/v0.1.4-readonly-publication-evidence.md` — publication evidence, final gate summary,
  release URL, and safety notes.
- `docs/release/v0.1.4-readonly-notes.md` — updated from prepared/unpublished candidate to published
  GitHub pre-release status.
- `docs/release/v0.1.4-readonly-checklist.md` — updated with Phase 142 publication preconditions and
  executed publish commands.
- `docs/release/v0.1.4-readonly-final-gate.md` — updated verdict to published after the Phase 142
  gate.
- `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-142.md` —
  release/status/handoff synchronized.
- Git tag and GitHub pre-release `v0.1.4-readonly` — published after the Phase 142 commit was pushed
  and CI passed.

Release result: `v0.1.4-readonly` is published as an authorized GitHub pre-release. No package,
binary artifact, Docker image, product code, write-alpha expansion, runtime default change,
production deployment, real/private data, or production-readiness claim was added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
remains experimental, post-MVP, disabled by default, and outside this read-only release scope. Docs
remain pre-alpha, test-copies-first, not production-ready, not security-audited, and with no
real/private-book write-safety claim.

Verification result: targeted disabled-write tests passed (`8 passed, 1 warning`); frontend `npm run
check` passed (`0 errors and 0 warnings`); frontend auth-route checks passed; Docker Compose config
validation passed; rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"`; latest five
GitHub Actions `main` CI runs were `completed success` before publication; `git diff --check`
passed; tracked sensitive-file hygiene scan passed with only known allowlisted
fixtures/placeholders/docs images and no new real/private data artifacts.

## Phase 151 — v0.1.5-readonly Maintenance Release Readiness Artifacts

Status: complete. Phase commit pushed after verification.

Goal: prepare conservative release-readiness artifacts for a possible `v0.1.5-readonly` maintenance
pre-release without publishing a tag/release/package or changing read-only/write-disabled posture.

Artifacts:

- `docs/release/v0.1.5-readonly-notes.md` — conservative candidate notes for the unpublished
  maintenance pre-release, summarizing Phases 143–150 and keeping
  pre-alpha/read-only/default-write-disabled/not-production/not-security-audited/test-copy-first
  language.
- `docs/release/v0.1.5-readonly-checklist.md` — release-prep checklist with candidate scope,
  evidence, safety checks, reserved publish commands, current blocker, and known limitations.
- `docs/release/v0.1.5-readonly-final-gate.md` — final-gate artifact recording clean starting
  `main`, tag/release absence, local verification, sensitive tracked-file scan, GitHub CI success,
  and verdict `Ready for later authorized publish phase — prepared but unpublished`.
- `README.md` — current status still names `v0.1.4-readonly` as the current public release and links
  the unpublished `v0.1.5-readonly` candidate artifacts separately.
- `CHANGELOG.md` — added Phase 151 and an unpublished `0.1.5-readonly` candidate section without
  implying publication.
- `PROJECT_STATUS.md` and `docs/handoff/phase-151.md` — status and handoff synchronized.

Release result: `v0.1.5-readonly` is prepared but unpublished. No tag, GitHub release, package,
uploaded artifact, Docker image, production deployment, product code, write-alpha expansion, runtime
default change, or real/private data artifact was created. Publication remains a separate future
phase requiring explicit authorization and immediate re-check of clean `main`, `HEAD ==
origin/main`, tag/release absence, CI for the Phase 151 release commit, local checks,
`GNUCASH_WRITES_ENABLED=false`, and sensitive-data hygiene.

Safety result: documentation/release-status only. No backend/frontend product code, endpoint, write
route, write service, runtime default, app DB, GnuCash book, backup, `.env`, secret, token, key,
cert, screenshot, CSV/private export, private path, account name, transaction description, memo,
amount, or private financial data was added. `GNUCASH_WRITES_ENABLED=false` remains the
documented/configured default. Docs remain pre-alpha, test-copies-first, not production-ready, not
security-audited, and with no real/private-book write-safety claim.

Verification result: targeted disabled-write/config tests passed, backend full suite passed,
frontend check/auth-routes/build passed, Docker Compose config validation passed, rendered Compose
config kept `GNUCASH_WRITES_ENABLED: "false"`, tag/release absence checks passed, `git diff --check`
passed, tracked sensitive-file hygiene scan passed, and GitHub Actions for the Phase 151 pushed
commit were watched to success. Publication remains a separate later authorized phase with a fresh
final gate immediately before publishing.

## Phase 152 — Conditional v0.1.5-readonly Release Publication

Status: complete. Phase commit pushed; tag and GitHub pre-release published after final gate.

Goal: publish `v0.1.5-readonly` only if Phase 151 release-readiness remained warranted and the final
gate was green; otherwise commit a no-release decision artifact.

Artifacts:

- `docs/release/v0.1.5-readonly-publication-evidence.md` — publication evidence, final gate summary,
  release URL, and safety notes.
- `docs/release/v0.1.5-readonly-notes.md` — updated from unpublished candidate to published GitHub
  pre-release status.
- `docs/release/v0.1.5-readonly-checklist.md` — updated with Phase 152 publication result and
  executed publish commands.
- `docs/release/v0.1.5-readonly-final-gate.md` — updated verdict to `Published as authorized GitHub
  pre-release`.
- `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-152.md` —
  release/status/handoff synchronized.
- Git tag and GitHub pre-release `v0.1.5-readonly` — published after the Phase 152 release commit
  was pushed and CI passed.

Release result: `v0.1.5-readonly` is published as an authorized GitHub pre-release. No no-release
blocker was needed. No package, binary artifact, Docker image, product code, write-alpha expansion,
runtime default change, production deployment, real/private data, or production-readiness claim was
added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
remains experimental, post-MVP, disabled by default, and outside this read-only release scope. Docs
remain pre-alpha, test-copies-first, not production-ready, not security-audited, and with no
real/private-book write-safety claim.

Verification result: targeted disabled-write tests passed (`63 passed, 32 warnings`); backend full
suite passed (`380 passed, 32 warnings`); frontend `npm run check` passed (`0 errors and 0
warnings`); frontend auth-route checks passed; frontend production build passed; Docker Compose
config validation passed; rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"`;
tag/release absence checks passed before publication; `git diff --check` passed; tracked
sensitive-file hygiene scan passed; GitHub Actions for the Phase 152 release commit passed before
tag/release publication; release view/tag checks passed after publication.

## Phase 156 — Dashboard Drilldown and Reporting Evidence

Status: complete. Phase commit pushed after verification.

Goal: improve read-only dashboard usefulness by linking dashboard summary/report cards to existing
filtered transaction views while preserving accounting limitations.

Artifacts:

- `apps/web/src/routes/dashboard/+page.server.ts` — builds active-book-preserving `/transactions`
  drilldown URLs from existing URL filters (`date_from`, `date_to`, `account_id`, `limit=50`,
  `offset=0`) for current-month summary cards, recent transactions, expense accounts, and cashflow
  months.
- `apps/web/src/routes/dashboard/+page.svelte`, `SummaryGrid.svelte`, `RecentTransactions.svelte`,
  `ExpensesByAccount.svelte`, and `CashflowSummary.svelte` — render dashboard drilldown links and
  conservative no-FX/no-recomputed-total copy.
- `apps/web/scripts/test-auth-routes.mjs` — pins URL construction, component wiring, expense account
  and cashflow drilldowns, and no-conversion/no-invented-total copy.
- `docs/money-model.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/handoff/phase-156.md` —
  document the drilldown limitations, CSV parity, safety boundaries, and handoff.

Safety result: dashboard drilldowns use existing read-only transaction filters only. No backend
accounting engine, FX conversion, forecasting, write route, production correctness guarantee,
browser filter persistence, release/tag/package, real/private book, `.env`, app DB, backup,
screenshot/export, token, key, cert, or private financial data was added.
`GNUCASH_WRITES_ENABLED=false` remains the documented/configured default.

Verification result: frontend route/static checks passed, frontend `npm run check` passed, backend
full suite passed, frontend build passed, Docker Compose config validation passed, rendered Compose
config kept `GNUCASH_WRITES_ENABLED: "false"`, `git diff --check` passed, and tracked sensitive-file
hygiene scan passed.

## Phase 161 — v0.1.6-readonly Maintenance Release Gate and Authorized Publication

Status: complete. Phase commit pushed; tag and GitHub pre-release published after final gate.

Goal: prepare the next read-only maintenance release after Phases 153–160 and publish only if the
final release gate is green and publication is authorized.

Artifacts:

- `docs/release/v0.1.6-readonly-notes.md` — conservative release notes for the published
  pre-release.
- `docs/release/v0.1.6-readonly-checklist.md` — release-prep checklist, scope, safety checks, and
  publication commands.
- `docs/release/v0.1.6-readonly-final-gate.md` — final release-gate verdict and verification
  evidence.
- `docs/release/v0.1.6-readonly-publication-evidence.md` — publication evidence, release URL, and
  post-publication checks.
- `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-161.md` —
  release/status/handoff synchronized.
- Git tag and GitHub pre-release `v0.1.6-readonly` — published after the Phase 161 release commit
  was pushed and CI passed.

Release result: `v0.1.6-readonly` is published as an authorized GitHub pre-release. Publication
created only the annotated tag and GitHub pre-release. No package, binary artifact, Docker image,
production deployment, product code, write-alpha expansion, runtime default change, or real/private
data artifact was added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
remains experimental, post-MVP, disabled by default, and outside this read-only release scope. Docs
remain pre-alpha, test-copies-first, not production-ready, not security-audited, and with no
real/private-book write-safety claim.

Verification result: backend full suite passed (`386 passed, 32 warnings`); frontend `npm run check`
passed (`0 errors and 0 warnings`); frontend auth-route checks passed; frontend production build
passed; Docker Compose config validation passed; rendered Compose config kept
`GNUCASH_WRITES_ENABLED: "false"`; tag/release absence checks passed before publication; `git diff
--check` passed; tracked sensitive-file hygiene scan passed; GitHub Actions for the Phase 161
release commit passed before tag/release publication; release view/tag checks passed after
publication.

## Phase 181 — Final Release-Readiness Gate and Publication Decision Artifact

Status: complete. Phase commit pushed after verification.

Goal: produce the final release-readiness gate for the completed Phase 173–180 write-alpha dogfood
cycle, compare status/release/changelog docs against code/evidence/GitHub state/safety defaults, and
stop before publication unless explicitly authorized.

Artifacts:

- `docs/release/v0.2.1-writealpha-notes.md` — conservative unpublished candidate notes for a
  possible future write-alpha maintenance pre-release.
- `docs/release/v0.2.1-writealpha-checklist.md` — candidate scope, evidence, safety checklist, and
  reserved publish commands.
- `docs/release/v0.2.1-writealpha-final-gate.md` — final gate with verdict `Ready for release after
  explicit owner authorization — prepared but unpublished`.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-181.md`
  — public status, changelog, project status, and handoff synchronized through Phase 181.

Release result: `v0.2.1-writealpha` is prepared but unpublished. A write-alpha maintenance candidate
is warranted by copied/disposable preflight/dogfood/restore/tooling evidence and the Phase 178–179
UX/API hardening, but Phase 181 did not include explicit owner authorization to publish. Therefore
no tag, GitHub release, package, binary artifact, image, production deployment, or upload was
created.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
execution remains experimental, requires explicit local enablement plus `APP_ENV=test`, and is
supported only by synthetic/disposable or copied-test-book evidence. No real/private/only-copy write
safety, production readiness, security audit, hosted SaaS readiness, broad Desktop/backend
compatibility, or direct-public-internet safety claim was added.

Verification result: local backend/frontend/Docker checks passed, rendered Compose config kept
`GNUCASH_WRITES_ENABLED: "false"`, recent GitHub releases/actions were reviewed, `git diff --check`
passed, and tracked sensitive-file hygiene scan passed. GitHub Actions on the pushed Phase 181
commit must still be green before any future authorized tag/release publication.

## Phase 182 — Authorized v0.2.1-writealpha Publication Under Fresh Gate

Status: complete. Phase commit pushed; tag and GitHub pre-release published after final gate.

Goal: publish the already prepared `v0.2.1-writealpha` only if a fresh pre-publish gate on current
`main` is green and confirms absence of the local/remote tag and GitHub release.

Artifacts:

- `docs/release/v0.2.1-writealpha-publication-evidence.md` — fresh gate, release URL, safety notes,
  and publication evidence.
- `docs/release/v0.2.1-writealpha-notes.md` — updated from unpublished candidate to published GitHub
  pre-release status.
- `docs/release/v0.2.1-writealpha-checklist.md` — updated with Phase 182 publication result and
  executed publish commands.
- `docs/release/v0.2.1-writealpha-final-gate.md` — refreshed with the Phase 182 gate and publication
  decision.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-182.md`
  — release/status/handoff synchronized.
- Git tag and GitHub pre-release `v0.2.1-writealpha` — published after the Phase 182 release/status
  commit was pushed and CI passed.

Release result: `v0.2.1-writealpha` is published as an authorized GitHub pre-release. No no-release
blocker was needed. Publication created only the annotated git tag and GitHub pre-release. No
package, binary artifact, Docker image, production deployment, product code, write-scope expansion,
runtime default change, or real/private data artifact was added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
execution remains experimental and requires explicit local enablement plus `APP_ENV=test`; evidence
remains synthetic/disposable or copied-test-book only. No production readiness, security audit,
hosted SaaS readiness, broad GnuCash compatibility, public-internet safety, or
real/private/only-copy write-safety claim was added.

Verification result: fresh pre-publish gate passed: clean tracked tree except ignored `.hermes/`,
`HEAD == origin/main`, local/remote tag absence, GitHub release absence, `gh` authenticated, GitHub
Actions on the exact release commit passed, backend suite passed, frontend check/auth-routes/build
passed, Docker Compose config validation passed, rendered Compose kept `GNUCASH_WRITES_ENABLED:
"false"`, `.env.example` kept `GNUCASH_WRITES_ENABLED=false`, `git diff --check` passed, and tracked
sensitive-file hygiene scan passed. Post-publication tag/release view checks passed.

## Phase 183 — Write-alpha Restore UX/API Evidence Tightening

Status: complete. Phase commit pushed after verification.

Goal: close the Phase 177/180 practical recovery risk around stale released lock files and
root-owned/unreadable runtime lock files without expanding write-alpha scope.

Artifacts:

- `apps/api/app/services/write_lock.py` — added path-safe `WriteLockService.inspect()` with
  `active`, `stale_released`, `unreadable`, and `not_present` statuses; it never deletes lock files
  and never returns filesystem paths.
- `scripts/smoke/write-alpha-create-smoke.py` — write-alpha create smoke now emits redacted lock
  evidence status so stale released lock files are not treated as active lock holds.
- `apps/api/tests/test_write_lock.py` and `apps/api/tests/test_write_alpha_smoke_lock_evidence.py` —
  targeted coverage for active, stale released, unreadable, and absent lock evidence plus safe
  operator messages.
- `apps/web/src/lib/components/WriteModeWarning.svelte` and `apps/web/scripts/test-auth-routes.mjs`
  — write-mode warning now includes stale-lock/root-owned host-permission recovery guidance, pinned
  by static checks.
- `docs/write-alpha-recovery-procedure.md` — recovery runbook now documents active-vs-stale lock
  inspection, API-container/root-owned lock workflow, and stopped-runtime cleanup boundaries.
- `docs/dogfood/phase-183-write-alpha-lock-recovery-evidence.md` and `docs/handoff/phase-183.md` —
  redacted evidence and handoff.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No automatic lock cleanup, production
lock-management UI, create/PATCH/DELETE expansion, write default change, release/tag/package,
real/private/only-copy book, runtime book/app DB/backup/lock artifact, `.env`, token, key, cert,
screenshot/export, raw path, account name, memo, amount, or private financial data was added.

Verification result: targeted lock tests passed (`18 passed`); active-lock route regression passed
(`1 passed` with existing piecash warnings); smoke helper py_compile passed; frontend
auth-route/static checks passed; redacted temporary lock-evidence probe showed `not_present`,
`stale_released`, and `active`; Docker Compose config validation passed and rendered
`GNUCASH_WRITES_ENABLED: "false"`; `git diff --check` passed; tracked sensitive-file hygiene scan
passed.

## Phase 184 — Write-alpha PATCH Disposable Dogfood

Status: complete. Phase commit pushed after verification.

Goal: capture real synthetic/disposable dogfood evidence for the existing experimental PATCH
transaction metadata/split-memo route without expanding write functionality.

Artifacts:

- `scripts/smoke/write-alpha-patch-smoke.py` — redacted smoke helper for one local disposable PATCH
  run; it checks safe missing-transaction behavior, successful metadata/split-memo PATCH,
  API/runtime marker read-back, backup, audit, and lock evidence.
- `docs/dogfood/phase-184-write-alpha-patch-dogfood.md` — bounded evidence artifact with preflight,
  write-enabled PATCH run, reset-to-default read-only smoke, and teardown/no-artifact result.
- `PROJECT_STATUS.md` and `docs/handoff/phase-184.md` — status and handoff synchronized.

Dogfood result: a committed synthetic fixture was copied to a temporary external disposable source,
preflighted as external/ignored, copied into ignored `data/books/main.gnucash.sqlite`, and patched
exactly once under explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`. The PATCH smoke
passed with redacted output: one metadata/split-memo PATCH succeeded; API read-back matched
synthetic markers only; runtime SQLite marker read-back passed; split amount fingerprint was
unchanged; one backup existed; one successful `transaction.patch` audit row and one safe failed
missing-transaction audit row existed; the API-container lock probe reported `stale_released`, not
active. After restart with default write-disabled runtime, read-only API smoke passed and
validate/create/PATCH/DELETE probes returned 403. Runtime book/app DB/backups/locks were removed
after verification.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No new endpoint, amount/account
PATCH, release/tag/package, real/private/only-copy book, runtime book, app DB, backup, lock
artifact, `.env`, token, key, cert, screenshot/export, raw path, account name, original description,
original memo, amount, or private financial data was committed.

Verification result: PATCH smoke helper py_compile passed; write-alpha preflight passed;
write-enabled PATCH smoke passed; default read-only API smoke passed including disabled
validate/create/PATCH/DELETE probes; targeted backend PATCH route tests passed; smoke lock evidence
tests passed; frontend auth-route/static checks passed; Docker Compose config validation passed and
rendered `GNUCASH_WRITES_ENABLED: "false"`; no ignored runtime artifact remained after teardown;
`git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 185 — Write-alpha DELETE Disposable Dogfood with Restore Proof

Status: complete. Phase commit pushed after verification.

Goal: capture bounded synthetic/disposable dogfood evidence for the existing experimental DELETE
transaction route and prove restore from the generated pre-write backup, without expanding write
functionality or claiming real/private-book write safety.

Artifacts:

- `scripts/smoke/write-alpha-delete-restore-smoke.py` — redacted smoke helper for one local
  disposable DELETE run plus restore proof; it checks pre-delete read-back, post-delete absence,
  backup, audit, checksum restore equality, restored API read-back, and lock evidence.
- `docs/dogfood/phase-185-write-alpha-delete-restore-dogfood.md` — bounded evidence artifact with
  preflight, write-enabled DELETE run, restore proof, reset-to-default read-only smoke, and
  teardown/no-artifact result.
- `PROJECT_STATUS.md` and `docs/handoff/phase-185.md` — status and handoff synchronized.

Dogfood result: a committed synthetic fixture was copied to a temporary external disposable source,
preflighted as external/ignored, copied into ignored `data/books/main.gnucash.sqlite`, and deleted
exactly once under explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`. The
DELETE+restore smoke passed with redacted output: one existing synthetic transaction DELETE
succeeded; API/runtime absence was confirmed in the mutated copy; exactly one backup existed; one
successful `transaction.delete` audit increment was observed; backup checksum matched the pre-delete
runtime checksum; restore copied the backup back over the ignored runtime book; restored checksum
matched backup checksum; restored API detail read-back passed; and the API-container lock probe
reported `stale_released`, not active. After restart with default write-disabled runtime, read-only
API smoke passed and validate/create/PATCH/DELETE probes returned 403. Runtime book/app
DB/backups/locks were removed after verification.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No new endpoint, bulk delete, account
delete, recurring delete, release/tag/package, real/private/only-copy book, runtime book, app DB,
backup, lock artifact, `.env`, token, key, cert, screenshot/export, raw path, account name, original
description, memo, amount, or private financial data was committed.

Verification result: DELETE+restore smoke helper py_compile passed; write-alpha preflight passed;
write-enabled DELETE+restore smoke passed; default read-only API smoke passed including disabled
validate/create/PATCH/DELETE probes; targeted backend DELETE route tests passed; frontend
auth-route/static checks passed; Docker Compose config validation passed and rendered
`GNUCASH_WRITES_ENABLED: "false"`; no ignored runtime artifact remained after teardown; `git diff
--check` passed; tracked sensitive-file hygiene scan passed.

## Phase 186 — Write-alpha Audit Trail Review UI for Disposable Runs

Status: complete. Phase commit pushed after verification.

Goal: make write-alpha run audit evidence operator-visible in a safe form without exposing private
paths/raw amounts and without turning it into a production audit feature.

Artifacts:

- `apps/api/app/routers/transactions.py` — added read-only `GET
  /books/{book_id}/write-alpha-audit-summary` endpoint over app metadata audit rows only.
- `apps/api/app/schemas/gnucash_writes.py` — added redacted audit summary DTOs with action, result,
  timestamp, bounded transaction ID prefix, backup-present boolean, and safe error text.
- `apps/api/tests/test_write_alpha_audit_summary.py` — auth/access/redaction tests for the summary
  endpoint.
- `apps/web/src/routes/books/write-alpha-audit/+page.server.ts` and `+page.svelte` — operator UI for
  active-book audit evidence with explicit disposable-run/non-production-audit copy.
- `apps/web/src/routes/books/+page.svelte`, `apps/web/src/lib/api/types.ts`, and
  `apps/web/scripts/test-auth-routes.mjs` — link/type/static-check support.
- `docs/dogfood/phase-186-write-alpha-audit-summary-dogfood.md` and `docs/handoff/phase-186.md` —
  synthetic app-DB-only dogfood evidence and handoff.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. The endpoint is read-only app
metadata only and does not construct write services, open GnuCash books, or mutate GnuCash data.
Viewer/unauthorized access is blocked. DTO/UI do not expose backup paths, private file paths, raw
request payloads, account names, memos, or amounts. No new write endpoint, release/tag/package,
real/private/only-copy book, runtime DB/book/backup artifact, `.env`, token, key, cert,
screenshot/export, private path, account name, memo, amount, or private financial data was
committed.

Dogfood result: synthetic app-DB-only probe passed with admin 200, viewer 403, three
create/PATCH/DELETE audit rows summarized, and explicit no-path/no-raw-payload checks true. No
GnuCash book was read or mutated.

Verification result: backend audit summary tests passed (`3 passed`); frontend auth-route/static
checks passed; frontend `npm run check` passed (`0 errors and 0 warnings`); synthetic app-DB dogfood
passed; standard backend/frontend/build/Docker/diff/hygiene results are recorded in the final Phase
186 report.

## Phase 188 — Read-only Reporting Correctness Edge Cases

Status: complete. Phase commit pushed after verification.

Goal: strengthen money/accounting correctness for read-only dashboard/reporting before any next
release claim.

Artifacts:

- `apps/api/app/services/gnucash_book.py` — report summary limitations now disclose excluded
  currencies detected from transaction splits as well as account listings.
- `apps/api/tests/test_reports.py` — synthetic edge-case tests for mixed-currency excluded splits,
  zero-balance split fallback, signed negative/contra asset/liability balances, and Decimal/string
  response amounts.
- `apps/web/src/routes/dashboard/+page.server.ts` and `apps/web/scripts/test-auth-routes.mjs` —
  dashboard drilldown URL-filter parity checks for account/date/limit/offset filters and no
  `Number()` use in dashboard reporting paths.
- `docs/money-model.md` — documented mixed-currency split exclusion and unknown-base zero-total
  semantics.
- `docs/handoff/phase-188.md` and `PROJECT_STATUS.md` — status and handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. Reports remain base-currency-only and
no-conversion; no FX conversion, forecasting, external rates, accounting-engine rewrite, write
behavior, release/tag/package, real/private book, runtime DB/book/backup artifact, `.env`, token,
key, cert, screenshot/export, raw path, account name, memo, amount, or private financial data was
added.

Verification result: targeted backend report tests passed (`47 passed`, existing piecash/SQLAlchemy
warnings only); frontend auth-route/static checks passed; `Number(` search over dashboard route and
component paths returned no matches; final standard checks are recorded in the final Phase 188
report.

## Phase 189 — Fresh-clone Install Smoke v2 with Published/Current Tags

Status: complete. Phase commit pushed after verification.

Goal: verify install/upgrade confidence for current published releases and current `main` without
reading private data.

Artifacts:

- `docs/dogfood/phase-189-fresh-clone-smoke-v2.md` — fresh-clone evidence for current public
  read-only tag, current public write-alpha tag, and current `main`.
- `docs/handoff/phase-189.md` — phase handoff.
- `PROJECT_STATUS.md` — status synchronized.

Dogfood result: fresh-clone Docker smoke passed for `v0.1.7-readonly`
(`d248b5a355ed2b57913d0c408e643b5f6cfcfe5b`), `v0.2.1-writealpha`
(`8c316b9f5c8028b519b603da0ba3cb37542bc4c0`), and current `main`
(`04751c3fe472fd7751746df525383214c3eb907c`) using only
`apps/api/tests/fixtures/test-book.gnucash.sqlite` copied into ignored runtime data inside temporary
clones. Each run used dummy local-only clone-local `.env` secrets, kept
`GNUCASH_WRITES_ENABLED=false`, and passed Docker Compose config/startup, `/api/health`, API smoke,
browser dogfood, disabled validate/create/PATCH/DELETE probes, hidden write UI, and no-artifact
checks. Post-run teardown scan found no remaining `/tmp/gwc-fresh-clone-smoke.*` directories and no
`gwc_fresh_clone` Docker containers/volumes/networks.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No write-enabled run, product code
change, smoke helper change, release/tag/package/image, real/private book, runtime book/app
DB/backup artifact, `.env`, token, key, cert, screenshot/export, private path, account name, memo,
amount, or private financial data was committed.

Verification result: three fresh-clone smokes passed; Docker Compose config validation on the
working tree passed and rendered `GNUCASH_WRITES_ENABLED: "false"`; `git diff --check` passed;
tracked sensitive-file hygiene scan passed.

## Phase 190 — Combined Release-Candidate Dogfood After Cycle-2 Changes

Status: complete. Phase commit pushed after verification.

Goal: gather final practical evidence after cycle-2 Phases 183–189: default read-only Docker/Caddy
regression plus explicit disposable write-alpha smoke for the touched create/PATCH/DELETE route
family.

Artifacts:

- `docs/dogfood/phase-190-cycle-2-release-candidate-dogfood.md` — combined read-only and write-alpha
  dogfood evidence.
- `docs/handoff/phase-190.md` — phase handoff.
- `PROJECT_STATUS.md` — status synchronized.

Dogfood result: default Docker/Caddy read-only smoke passed using only
`apps/api/tests/fixtures/test-book.gnucash.sqlite` copied into ignored runtime data. API smoke
passed for health, login/auth, books, accounts, transactions, transaction detail, CSV export,
reports summary, and disabled validate/create/PATCH/DELETE probes returning 403. Browser dogfood
passed at mobile `320x720` and desktop `1280x900` with hidden write UI, auth cookie not readable
from `document.cookie`, CSV fetch success, no-overflow checks, and no screenshot/download/CSV
artifacts. Separate explicit local-only write-alpha runs under `APP_ENV=test` plus
`GNUCASH_WRITES_ENABLED=true` collected bounded create/PATCH/DELETE evidence: success audit rows
with backup evidence for create/PATCH/DELETE, expected safe missing-transaction failed audit for
PATCH, backup files present, and no active lock hold from API-container inspection. Host-side
root-owned runtime readability limited helper final lock/restore checks, so this phase does not add
a new restore claim.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default before and after the write-enabled
smokes. No release/tag/package/image, product code change, real/private/only-copy book, runtime
book/app DB/backup/lock artifact, `.env`, token, key, cert, screenshot/export, private path, account
name, memo, amount, production/security claim, or real/private-book write-safety claim was added.

Verification result: default false Compose config passed before and after; read-only API smoke
passed before and after; mobile and desktop browser dogfood passed; explicit write-alpha config
showed `GNUCASH_WRITES_ENABLED: "true"` only for local disposable write smoke runs; redacted
container inspection verified audit/backup/lock evidence; teardown/no-artifact scan found zero
non-placeholder runtime files under `data/books`, `data/app`, `data/backups`, and `data/locks`.
Final standard checks are recorded in the final Phase 190 report.

## Phase 191 — Cycle-2 Release-Readiness Gate and Publication

Status: complete. Phase commit pushed; tag and GitHub pre-release published after exact
release-commit CI passed.

Goal: perform the final cycle-2 release-readiness gate and publish only if evidence warrants it and
the exact release commit is green.

Artifacts:

- `docs/release/v0.2.2-writealpha-notes.md` — conservative pre-alpha/write-alpha release notes.
- `docs/release/v0.2.2-writealpha-checklist.md` — release-prep checklist and safety checklist.
- `docs/release/v0.2.2-writealpha-final-gate.md` — final gate and publication decision.
- `docs/release/v0.2.2-writealpha-publication-evidence.md` — local checks, exact-commit CI, and
  publication evidence.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-191.md`
  — status/handoff synchronized.
- Git tag and GitHub pre-release `v0.2.2-writealpha` — published after the Phase 191 release/status
  commit was pushed and CI passed.

Release result: `v0.2.2-writealpha` is published as a conservative GitHub pre-release. A write-alpha
maintenance pre-release was warranted because cycle-2 includes write-alpha evidence and
safety/operator hardening beyond `v0.2.1-writealpha`; a read-only maintenance tag would not match
the scope. Publication created only the annotated git tag and GitHub pre-release. No package, binary
artifact, Docker image, production deployment, product-code change, write-scope expansion, runtime
default change, or real/private data artifact was added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
execution remains experimental and requires explicit local enablement plus `APP_ENV=test`; cycle-2
evidence remains synthetic/disposable only. No production readiness, security audit, hosted SaaS
readiness, broad GnuCash compatibility, public-internet safety, or real/private/only-copy
write-safety claim was added.

Verification result: release-readiness gate passed: clean tracked tree except ignored `.hermes/`,
`HEAD == origin/main` before release artifacts, local/remote tag absence, GitHub release absence,
`gh` authenticated, backend suite passed, frontend check/auth-routes/build passed, Docker Compose
config validation passed, rendered Compose kept `GNUCASH_WRITES_ENABLED: "false"`, `.env.example`
kept `GNUCASH_WRITES_ENABLED=false`, `git diff --check` passed, tracked sensitive-file hygiene scan
passed, GitHub Actions on the exact release/status commit passed before tagging, and
post-publication tag/release checks passed. GitHub Actions emitted a non-blocking Node.js 20
deprecation warning for `actions/checkout@v4`.

## Phase 192 — CI/toolchain warning cleanup

Status: complete. Phase commit pushed after verification; GitHub Actions run on the exact commit
passed.

Goal: remove the known non-blocking Node.js 20 deprecation warning in GitHub Actions after
`v0.2.2-writealpha` without changing product behavior.

Artifacts:

- `.github/workflows/ci.yml` — existing checkout/setup steps in the foundation, frontend, backend,
  and Docker Compose jobs now use Node 24-compatible action major versions (`actions/checkout@v5`,
  `actions/setup-node@v6`, and `actions/setup-python@v6`); the existing job layout and checks are
  unchanged.
- `CHANGELOG.md` — Unreleased support note for the CI/toolchain cleanup.
- `docs/handoff/phase-192.md` — before/after evidence and handoff.
- `PROJECT_STATUS.md` — status synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example` and rendered Docker
Compose config. No product code, API/UI business logic, Docker runtime default, write enablement,
release/tag publication, GitHub issue change, real/private book, app DB, backup, `.env`, token, key,
cert, screenshot/export, or private financial artifact was added.

Verification result: local backend pytest passed; frontend `npm run check`, `npm run
test:auth-routes`, and `npm run build` passed; Docker Compose config validation passed; rendered
Compose kept `GNUCASH_WRITES_ENABLED: "false"`; `.env.example` kept `GNUCASH_WRITES_ENABLED=false`;
`git diff --check` passed; sensitive tracked-file hygiene scan passed; the exact pushed CI run
passed without Node.js 20 action deprecation warnings.

## Phase 198 — Multi-book read-only registry diagnostics hardening

Status: complete. Phase commit pushed after verification.

Goal: improve safe multi-book readiness around GitHub #13 without management/write expansion, so
operators see actionable diagnostics while users never see raw paths or inaccessible books.

Artifacts:

- `apps/api/app/routers/books.py` — safe `status_severity`, access-role labels/descriptions, and
  `can_open_read_only_views` metadata for accessible books without exposing `uri_or_path` or opening
  GnuCash data during listing.
- `apps/api/tests/test_multibook_readonly_access.py` — expanded multi-book diagnostics and
  route-family boundary coverage.
- `apps/web/src/routes/books/+page.svelte`, `apps/web/src/routes/books/+page.server.ts`, and
  `apps/web/src/routes/books/[bookId]/select/+server.ts` — safe role/status diagnostics,
  unavailable-book diagnostics-only copy, touch-friendly links, and server-validated safe-link
  recovery.
- `apps/web/src/lib/api/types.ts`, `apps/web/src/lib/i18n/messages.ts`, and
  `apps/web/scripts/test-auth-routes.mjs` — typed/frontend/static-check support.
- `docs/dogfood/phase-198-multibook-readonly-diagnostics.md` and `docs/handoff/phase-198.md` —
  synthetic evidence and handoff.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No GnuCash writes were enabled or
executed. No registry management UI, upload/delete/default-changing controls,
collaborative/family-wallet workflow, release/tag, real/private book, app DB, backup artifact,
`.env`, token, key, cert, screenshot/export, raw path, or private financial data was added.

Verification result: backend multi-book tests passed (`76 passed`); frontend auth-route/static
checks passed; frontend `npm run check` passed; frontend build passed; Docker Compose config
validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"`; `git diff --check` passed; tracked
sensitive-file hygiene scan passed. Synthetic multi-book dogfood evidence is documented in
`docs/dogfood/phase-198-multibook-readonly-diagnostics.md`.

## Phase 199 — Full default-read-only regression dogfood

Status: complete. Phase commit pushed after verification.

Goal: confirm that the default read-only product path remains stable after cycle-3 Phases 192–198 on
synthetic/disposable Docker/Caddy across API, mobile browser, and desktop browser coverage.

Artifacts:

- `docs/dogfood/phase-199-default-readonly-regression.md` — redacted local default-read-only
  Docker/Caddy API and browser evidence.
- `docs/handoff/phase-199.md` — phase handoff.
- `PROJECT_STATUS.md` — status synchronized.

Dogfood result: local Docker/Caddy ran with only `apps/api/tests/fixtures/test-book.gnucash.sqlite`
copied into ignored `data/books/main.gnucash.sqlite`, dummy local-only `.env` values, and
`GNUCASH_WRITES_ENABLED=false`. API smoke passed for health, login/auth, books/default book,
accounts, transactions, transaction detail, CSV export, reports summary, and disabled
validate/create/PATCH/DELETE probes returning 403. Browser dogfood passed at `320x720` and
`1280x900` with hidden write UI, auth cookie not readable from `document.cookie`, CSV fetch success,
no-overflow checks, and no screenshot/download/CSV artifacts.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and rendered false for API and web. No
write-enabled mode was run. No real/private/only-copy book, release/tag/package/image, app
DB/backup/runtime artifact, `.env`, token, key, cert, private path, or private financial data was
committed. After `docker compose down --remove-orphans`, ignored runtime book/app DB and the dummy
local `.env` were removed; runtime directories had zero non-placeholder entries.

Verification result: Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED:
"false"`; read-only API smoke passed; mobile and desktop browser dogfood passed; targeted backend
health/write-gating tests passed; full backend pytest passed; frontend `npm run check`,
auth-route/static checks, and build passed; `git diff --check` passed; tracked sensitive-file
hygiene scan passed.

## Phase 200 — Bounded write-alpha disposable CRUD/restore dogfood

Status: complete. Phase commit pushed after verification.

Goal: collect final cycle-3 write-alpha evidence on synthetic/disposable data only after helper/UX
fixes, including create/PATCH/DELETE, audit, backup, lock, restore where actually completed, and
return to default false.

Artifacts:

- `docs/dogfood/phase-200-write-alpha-cycle-3-dogfood.md` — redacted local write-alpha CRUD/restore
  evidence.
- `docs/handoff/phase-200.md` — phase handoff.
- `PROJECT_STATUS.md` — status synchronized.

Dogfood result: an external disposable copy of the committed synthetic fixture passed the
write-alpha dry-run preflight with redacted path classes, then fresh ignored runtime copies under
`data/books/main.gnucash.sqlite` were prepared separately for create, PATCH, and DELETE route-family
smokes. Each route-family smoke executed exactly once per prepared copy under explicit local-only
`APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`. Create succeeded once and safe validation probes
failed as expected; PATCH recorded safe missing-transaction evidence plus one successful
metadata/split-memo PATCH; DELETE succeeded once and completed a host-readable backup restore proof
with API read-back. Successful writes had backup and audit evidence, failed
validation/missing-transaction cases were safe, and all lock evidence was `stale_released`, not
actively held.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and was rendered for API and web after
reset. Write-enabled mode was local-only, explicit, and limited to ignored disposable synthetic
runtime copies. No real/private/only-copy book, write-route expansion, production/private-book
safety claim, release/tag/package/image, committed app DB/book/backup/lock/runtime artifact, `.env`,
token, key, cert, screenshot/export, raw path, account name, description, memo, amount, or private
financial data was added.

Verification result: write-alpha preflight passed; Docker Compose config validation passed;
write-enabled rendered config showed `GNUCASH_WRITES_ENABLED: "true"` only during explicit
`APP_ENV=test` disposable smokes; create/PATCH/DELETE+restore smoke helpers passed; final rendered
Compose showed `GNUCASH_WRITES_ENABLED: "false"`; read-only API smoke passed with
validate/create/PATCH/DELETE returning 403; stopped-runtime cleanup removed ignored runtime files;
targeted backend health/write-gating tests passed; full backend pytest passed; frontend `npm run
check`, auth-route/static checks, and build passed; `git diff --check` passed; tracked
sensitive-file hygiene scan passed.

## Phase 201 — Cycle-3 release-readiness gate and publication

Status: complete. Phase commit pushed; tag and GitHub pre-release published after exact
release-commit CI passed.

Goal: perform the final cycle-3 release-readiness gate and publish only if evidence warrants it and
the exact release commit is green.

Artifacts:

- `docs/release/v0.2.3-writealpha-notes.md` — conservative pre-alpha/write-alpha release notes.
- `docs/release/v0.2.3-writealpha-checklist.md` — release-prep checklist and safety checklist.
- `docs/release/v0.2.3-writealpha-final-gate.md` — final gate and publication decision.
- `docs/release/v0.2.3-writealpha-publication-evidence.md` — local checks, exact-commit CI, and
  publication evidence.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-201.md`
  — status/handoff synchronized.
- Git tag and GitHub pre-release `v0.2.3-writealpha` — published after the Phase 201 release/status
  commit was pushed and CI passed.

Release result: `v0.2.3-writealpha` is published as a conservative GitHub pre-release. A write-alpha
maintenance pre-release was warranted because cycle-3 includes material
operator/readiness/write-alpha evidence beyond `v0.2.2-writealpha`: CI warning cleanup, runtime
cleanup and lock recovery tooling, resilient smoke helpers, audit-summary and first-run diagnostics,
multi-book diagnostics, default-read-only regression dogfood, and bounded write-alpha CRUD/restore
dogfood. Publication created only the annotated git tag and GitHub pre-release. No package, binary
artifact, Docker image, production deployment, product-code change, write-scope expansion, runtime
default change, or real/private data artifact was added.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Write-alpha
execution remains experimental and requires explicit local enablement plus `APP_ENV=test`; cycle-3
evidence remains synthetic/disposable only. No production readiness, security audit, hosted SaaS
readiness, broad GnuCash compatibility, public-internet safety, or real/private/only-copy
write-safety claim was added.

Verification result: release-readiness gate passed: clean tracked tree except ignored `.hermes/`,
`HEAD == origin/main` before release artifacts, local/remote tag absence, GitHub release absence,
`gh` authenticated, backend suite passed, frontend check/auth-routes/build passed, Docker Compose
config validation passed, rendered Compose kept `GNUCASH_WRITES_ENABLED: "false"`, `.env.example`
kept `GNUCASH_WRITES_ENABLED=false`, `git diff --check` passed, tracked sensitive-file hygiene scan
passed, GitHub Actions on the exact release/status commit passed before tagging, and
post-publication tag/release checks passed.

## Phase 202 — Read-only first-run health drill

Status: complete. Phase commit pushed after verification.

Goal: harden the default read-only first-run diagnostics path so a new operator can distinguish
missing/unreadable default book, placeholder JWT/admin bootstrap configuration, unsafe CORS posture,
and write-disabled status without exposing paths or secrets.

Artifacts:

- `apps/api/app/diagnostics.py` — `/health` first-run diagnostics now include redacted per-check
  safe next actions and default-book `path_kind` values for not configured, missing file, unreadable
  file, and local file states.
- `apps/api/tests/test_health.py` — targeted coverage for safe next actions,
  missing/unreadable/default-book diagnostics, placeholder JWT/admin cases, CORS warning,
  write-disabled default, and explicit write-mode warning without changing the action-required list.
- `apps/web/src/routes/login/+page.svelte` and `apps/web/src/lib/api/types.ts` — `/login` renders
  redacted per-check next actions from `/health` without browser storage.
- `apps/web/scripts/test-auth-routes.mjs` — static route check pins mobile-safe first-run status
  labels and safe next actions.
- `docs/handoff/phase-202.md` and `PROJECT_STATUS.md` — status and handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. Write endpoints still return 403 in
default read-only smoke. `APP_ENV=test` write-alpha gating was not changed. Auth remains
httpOnly-cookie based; no localStorage/sessionStorage for auth or financial state was added. No
real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account
name, memo, amount, or private financial data was committed.

Verification result: targeted backend health/auth/books/write-gating tests passed; full backend
pytest passed; frontend check/auth-route/static checks/build passed; Docker Compose config
validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"`; local Docker/Caddy read-only API
smoke passed on the committed synthetic fixture copied to ignored runtime data, including
validate/create/PATCH/DELETE 403 probes; `git diff --check` passed; tracked sensitive-file hygiene
scan passed; ignored runtime data and dummy local `.env` were removed after smoke.

## Phase 203 — Disposable Desktop fixture capture path

Status: complete. Phase commit pushed after verification.

Goal: advance GnuCash Desktop compatibility evidence by creating a safe path to capture or document
a Desktop-generated synthetic SQLite fixture without touching real/private books.

Artifacts:

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py` — strict path-redacted candidate
  acceptance/rejection for `desktop-generated-synthetic` inputs, including GnuCash version
  requirement, synthetic/disposable filename requirement, SQLite suffix check, and
  backup/app/secrets/.env/non-disposable path-class rejection.
- `apps/api/tests/test_gnucash_compatibility_metadata.py` — deterministic accepted/rejected
  candidate coverage plus no private path/name serialization.
- `docs/gnucash-desktop-fixture-capture.md` — manual-safe disposable Desktop fixture capture runbook
  and suggested GitHub #22 update text.
- `docs/gnucash-compatibility.md` and `docs/gnucash-version-fixture-plan.md` — compatibility docs
  updated with Phase 203 blocker/capture-path evidence and safe current candidate command paths,
  with no new Desktop-version support claim.
- `docs/handoff/phase-203.md` — phase handoff.
- GitHub issue #22 — concise evidence comment added:
  `https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4498500834`.
- `PROJECT_STATUS.md` — status synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No Desktop-generated fixture was
produced, supplied, copied into runtime storage, or committed. No real/private book, app DB, backup,
`.env`, screenshot/export, token, key, cert, raw path, account name, transaction description, memo,
amount, row value, or private financial data was committed. The helper rejects unsafe candidate path
classes before reading metadata and accepted metadata remains bounded/redacted.

Verification result: targeted compatibility metadata/helper tests passed; compatibility docs/tests
passed; full backend pytest passed; frontend `npm run check`, `npm run test:auth-routes`, and `npm
run build` passed; Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED:
"false"`; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 204 — Compatibility matrix regression from fixture metadata

Status: complete. Phase commit pushed after verification.

Goal: turn the Phase 203 fixture/provenance result into automated read-only compatibility regression
coverage and honest matrix docs without adding backend support or broad version claims.

Artifacts:

- `apps/api/app/compatibility_matrix.py` — classifies redacted fixture metadata as tested synthetic
  evidence, blocked/manual Desktop fixture work, or unclaimed backend with conservative display
  copy.
- `apps/api/tests/test_compatibility_matrix.py` — pins metadata ingestion, unsupported-backend
  messaging, compatibility matrix section separation, and broad-support wording guards.
- `docs/gnucash-compatibility.md` — reorganized into tested synthetic/disposable evidence,
  blocked/manual fixture work, and unclaimed backends/formats.
- `docs/gnucash-version-fixture-plan.md` — records the Phase 204 matrix-regression guard.
- `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-204.md` — status/handoff
  synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No fixture binary, real/private book,
app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account name, transaction
description, memo, amount, row value, or private financial data was committed.
PostgreSQL/MySQL/MariaDB and XML remain explicitly unclaimed; Desktop-generated metadata remains
blocked/manual until separate default-read-only validation passes.

Verification result: targeted compatibility matrix/metadata/backend docs tests passed; full backend
pytest passed; frontend `npm run check`, `npm run test:auth-routes`, and `npm run build` passed;
Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"`; touched
markdown link check passed; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 205 — Multi-book read-only recovery polish

Status: complete. Phase commit pushed after verification.

Goal: improve read-only multi-book recovery and navigation for inaccessible, archived, missing, and
stale selected-book contexts without adding management actions.

Artifacts:

- `apps/web/src/lib/api/server.ts` — active-book resolution now ignores accessible-but-unavailable
  books for read-only data views, classifies unavailable selected-book cookies separately, and
  safely falls back to an openable accessible book or clears the selected-book cookie when no
  openable book exists.
- `apps/web/src/routes/books/[bookId]/select/+server.ts` — server-validated book selection still
  blocks unavailable books, now preserves safe query strings for
  dashboard/accounts/transactions/scheduled paths while rejecting external or management
  destinations.
- `apps/web/src/routes/books/+page.svelte` and `apps/web/src/lib/i18n/messages.ts` — `/books` shows
  a distinct safe unavailable-book recovery notice and keeps private paths redacted.
- `apps/web/scripts/test-auth-routes.mjs` — route/static checks pin openable-book fallback,
  unavailable-book notices, safe query-preserving selection links, no client-side selected-book
  cookie writes, and no management actions.
- `docs/handoff/phase-205.md` and `PROJECT_STATUS.md` — status/handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. Access checks remain
backend-enforced; archived and unauthorized books stay hidden or blocked by API route families; auth
remains httpOnly-cookie based; no localStorage/sessionStorage, write route, registry management UI,
upload/delete/default-changing controls, real/private book, app DB, backup, `.env`,
screenshot/export, token, key, cert, raw private path, or private financial data was added.

Verification result: targeted backend multi-book access tests passed; frontend route/static checks
passed; frontend `npm run check` passed; full backend/frontend/Docker checks and read-only smoke are
recorded in `docs/handoff/phase-205.md`.

## Phase 206 — Transaction and scheduled read-only edge-case polish

Status: complete. Phase commit pushed after verification.

Goal: harden transaction and scheduled read-only pages for empty, large, many-split, filtered,
reconciliation-state, and no-template cases discovered by synthetic fixtures.

Artifacts: `apps/api/app/schemas/gnucash.py`, `apps/api/app/services/gnucash_book.py`, targeted
scheduled/transaction tests, `apps/web/src/lib/components/Money.svelte`,
`apps/web/src/lib/components/TransactionSplits.svelte`,
`apps/web/src/routes/scheduled/+page.svelte`, `apps/web/scripts/test-auth-routes.mjs`,
`docs/dogfood/phase-206-readonly-edge-case-dogfood.md`, and `docs/handoff/phase-206.md`.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No scheduled writes, template split
exposure, import/export expansion, currency conversion, browser financial persistence, real/private
book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw private path, account name,
memo, amount, or private financial data was committed.

Verification result: targeted backend transaction/scheduled/export/write-gating tests passed; full
backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config validation
passed with rendered writes disabled; Docker/Caddy API and browser dogfood passed on the committed
synthetic fixture at mobile and desktop widths with disabled validate/create/PATCH/DELETE probes
returning 403.

## Phase 207 — Write-alpha audit-summary redaction hardening

Status: complete. Phase commit pushed after verification.

Goal: strengthen the read-only write-alpha audit-summary endpoint/UI so prior disposable write runs
are inspectable without leaking payloads, backup paths, amounts, memos, account names, or private
paths.

Artifacts:

- `apps/api/app/routers/transactions.py` — audit-summary rows now sanitize payload result,
  timestamp, transaction ID prefix, and error text; path-like or
  amount/account/memo/description-bearing payload values are replaced with bounded safe metadata.
  The response also includes safe time-window and status-summary metadata.
- `apps/api/app/schemas/gnucash_writes.py` and `apps/web/src/lib/api/types.ts` — DTO/type shape
  updated for `time_window` and `status_summary`.
- `apps/api/tests/test_write_alpha_audit_summary.py` — coverage added for malicious payload
  result/timestamp/transaction-id/error redaction, safe path-like filter failure, bounded
  counts/status/time-window metadata, and viewer/outsider 403 access.
- `apps/web/src/routes/books/write-alpha-audit/+page.svelte` — UI copy now renders
  requested/returned time windows and bounded status rows while continuing to display only redacted
  summary fields.
- `apps/web/scripts/test-auth-routes.mjs` — frontend static checks pin the safe audit-summary fields
  and count/status/time-window UX.
- `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-207.md` — status/handoff
  synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. The audit-summary route remains
read-only/app-metadata-only and performs no GnuCash book mutation. Raw audit payloads, backup paths,
private paths, amounts, memos, account names, and request/update/delete summaries are not rendered.
No write route, write-scope expansion, lock deletion, production write-safety claim, real/private
book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path, or private
financial data was added.

Verification result: targeted audit-summary tests passed; full backend pytest passed; frontend
check/auth-routes/build passed; Docker Compose config validation passed and rendered
`GNUCASH_WRITES_ENABLED=false`; disabled-write route probes passed through the read-only API smoke;
`git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 208 — Frontend safety/locale polish for operator flows

Status: complete. Phase commit pushed after verification.

Goal: polish English/Russian safety copy for operator-facing read-only/write-alpha warnings without
claiming full localization or changing backend behavior.

Artifacts:

- `apps/web/src/lib/i18n/messages.ts` — added/updated catalog-backed English/Russian operator safety
  copy for read-only release-critical warnings, write-alpha warnings/acknowledgements/final
  confirmations, books audit-evidence link text, and write-alpha audit-summary labels/help/error
  states.
- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte`,
  `apps/web/src/lib/components/WriteModeWarning.svelte`,
  `apps/web/src/routes/transactions/new/+page.svelte`, `apps/web/src/routes/books/+page.svelte`, and
  `apps/web/src/routes/books/write-alpha-audit/+page.svelte` — switched relevant visible
  safety/operator strings from hardcoded English to typed catalog keys while keeping English
  canonical and Russian partial/opt-in.
- `apps/web/scripts/test-auth-routes.mjs` — static checks now pin localized safety catalog usage,
  release-critical wording boundaries, hidden-by-default write UI, no raw audit payloads, and no
  localStorage/sessionStorage use outside the existing theme preference exception.
- `docs/localization.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `docs/handoff/phase-208.md` —
  localization/status/handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No backend API localization, write
route behavior, write gate, release/tag, product marketing claim,
production-readiness/security-audit claim, real/private book, app DB, backup artifact, `.env`,
screenshot/export, token, key, cert, raw path, account name, memo, amount, browser
auth/locale/financial storage, or private financial data was added. Russian remains a conservative
operator-safety slice only, not a full localization guarantee.

Verification result: full backend pytest passed; frontend `npm run check`, `npm run
test:auth-routes`, and `npm run build` passed; Docker Compose config validation passed; `git diff
--check` passed; default-read-only browser dogfood passed on the committed synthetic fixture copied
into ignored runtime data with hidden write UI, httpOnly auth-cookie check, mobile no-overflow
checks, CSV route check, and no screenshot/download/CSV artifacts.

## Phase 209 — Default-read-only full dogfood refresh

Status: complete. Phase commit pushed after verification.

Goal: re-run a full default-read-only Docker/Caddy API and browser dogfood after Phases 202–208 to
prove the safe default still works.

Artifacts:

- `scripts/smoke/read-only-api-smoke.py` — full API smoke now explicitly covers scheduled
  transaction metadata and the read-only write-alpha audit-summary endpoint in addition to
  health/login/books/accounts/transactions/details/CSV/reports and disabled
  validate/create/PATCH/DELETE probes.
- `docs/dogfood/phase-209-default-readonly-dogfood.md` — redacted local default-read-only
  Docker/Caddy API and browser evidence.
- `docs/handoff/phase-209.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Dogfood result: local Docker/Caddy ran with only `apps/api/tests/fixtures/test-book.gnucash.sqlite`
copied into ignored `data/books/main.gnucash.sqlite`, dummy local-only `.env` values, and
`GNUCASH_WRITES_ENABLED=false`. API smoke passed for health, login/auth, books/default book,
accounts, transactions, transaction detail, CSV export, reports summary, scheduled transaction
metadata, write-alpha audit summary, and disabled validate/create/PATCH/DELETE probes returning 403.
Browser dogfood passed at `320x720` and `1280x900` with hidden write UI, auth cookie not readable
from `document.cookie`, CSV fetch success, no-overflow checks, and no screenshot/download/CSV
artifacts.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and rendered false for API and web. No
write-enabled mode was run. No real/private/only-copy book, release/tag/package/image, committed
runtime artifact, `.env`, backup, token, key, cert, private path, account name, memo, amount, or
private financial data was added. The ignored smoke runtime book and generated app DB were removed
after teardown; a pre-existing ignored local `data/app/app.db` was restored and remains untracked
local state.

Verification result: Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED:
"false"`; read-only API smoke passed; mobile and desktop browser dogfood passed; full backend pytest
passed; frontend `npm run check`, auth-route/static checks, and build passed; `git diff --check`
passed; tracked sensitive-file hygiene scan passed.

## Phase 210 — Bounded disposable write-alpha CRUD/restore refresh

Status: complete. Phase commit pushed after verification.

Goal: collect one fresh bounded write-alpha evidence pass after cycle-1 hardening, using only
ignored synthetic/disposable runtime copies and then returning to default false.

Artifacts:

- `docs/dogfood/phase-210-write-alpha-cycle-1-dogfood.md` — redacted local write-alpha
  create/PATCH/DELETE+restore evidence, default-false reset evidence, and cleanup notes.
- `docs/handoff/phase-210.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Dogfood result: a committed synthetic fixture was copied to a temporary external disposable source
and then into ignored `data/books/main.gnucash.sqlite` before each route-family smoke. The
write-alpha preflight dry-run passed for external source, ignored runtime book, and ignored backup
classes. Local Docker/Caddy ran only with explicit `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`
and dummy local-only secrets. Create, PATCH, and DELETE route-family smokes each executed exactly
one successful mutation on its prepared copy; expected validation/missing-transaction failures
failed safely; backup and audit evidence increased as expected; API/runtime read-back checks passed;
DELETE restore proof used a host-readable backup and passed restored API read-back; lock evidence
was stale-released/not active.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. The stack was reset to default false,
rendered Compose showed `GNUCASH_WRITES_ENABLED: "false"` for API and web, and read-only API smoke
passed with validate/create/PATCH/DELETE probes returning 403. Cleanup removed ignored runtime
book/backups/locks/generated smoke app DB, using the stopped-runtime cleanup helper with
`--via-compose` fallback for root-owned ignored backup artifacts; a pre-existing ignored local
`data/app/app.db` was restored and remains untracked local state. No real/private/only-copy book,
enabled-by-default config, write endpoint expansion, release/tag/package/image, committed runtime
artifact, `.env`, backup, token, key, cert, raw path, account name, memo, amount, or private
financial data was added.

Verification result: write-alpha preflight dry-run passed; create smoke passed; PATCH smoke passed;
DELETE restore smoke passed; rendered false reset check passed; read-only API smoke passed; full
backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config validation
passed; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 211 — v0.2.4-writealpha release gate/publication

Status: complete. Release/status commit pushed, exact-commit CI passed, tag pushed, and GitHub
pre-release published.

Goal: perform the final release gate for cycle 1 and publish `v0.2.4-writealpha` only if Phases
202–210 produced safe material changes/evidence and exact release-commit CI is green.

Artifacts:

- `docs/release/v0.2.4-writealpha-notes.md` — conservative pre-alpha/write-alpha release notes.
- `docs/release/v0.2.4-writealpha-checklist.md` — release-prep and safety checklist.
- `docs/release/v0.2.4-writealpha-final-gate.md` — final gate and publication decision.
- `docs/release/v0.2.4-writealpha-publication-evidence.md` — final gate, CI, tag/release, and
  publication evidence.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, and `docs/handoff/phase-211.md` — status/handoff
  synchronized.

Release result: `v0.2.4-writealpha` was published as a GitHub pre-release after local
backend/frontend/Docker checks passed, rendered Compose kept `GNUCASH_WRITES_ENABLED=false`, tracked
sensitive-file hygiene passed, the release/status commit was pushed to `origin/main`, and GitHub
Actions on the exact release/status commit completed successfully. Publication created only the
annotated git tag and GitHub pre-release.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. Write-alpha execution remains
experimental and requires explicit local enablement plus `APP_ENV=test`. The release is pre-alpha,
not production-ready, not security-audited, and not safe for real/private or only-copy books. No
stable release, package, binary, Docker image, production deployment, write default change,
write-scope expansion, real/private book, app DB, backup, `.env`, screenshot/export, token, key,
cert, raw private path, account name, memo, amount, or private financial data was added.

Verification result: backend pytest passed; frontend check/auth-routes/build passed; Docker Compose
config validation passed; rendered write-default grep showed `GNUCASH_WRITES_ENABLED: "false"` for
API and web; `.env.example` default false was confirmed; `git diff --check` passed; tracked
sensitive-file hygiene scan passed; exact release/status commit GitHub Actions passed; local/remote
tag and GitHub pre-release were verified after publication.

## Phase 212 — Public status drift guard

Status: complete. Public status/release-support docs synchronized after `v0.2.4-writealpha`;
automated guard added to CI/local checks.

Goal: remove stale public roadmap/status drift after the Phase 211 `v0.2.4-writealpha` publication
and prevent README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release-support docs from diverging on
current release posture.

Artifacts:

- `scripts/check_public_status.py` — narrow public status guard for current Phase 211 release
  baseline, `v0.1.7-readonly`, `v0.2.4-writealpha`, `GNUCASH_WRITES_ENABLED=false`, and conservative
  no-production/no-security/no-stable-claim wording.
- `apps/api/tests/test_public_status_guard.py` — targeted regression tests proving the guard rejects
  stale current `Phase 172` / `v0.2.0-writealpha` posture and affirmative production claims, while
  reading only declared public docs/config files.
- `.github/workflows/ci.yml` — foundation job now runs the public status guard.
- `docs/ROADMAP.md`, `README.md`, `README.ru.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — public
  status synchronized to completed Phase 212 while keeping the current release baseline at Phase 211
  / `v0.2.4-writealpha`.
- `docs/handoff/phase-212.md` — phase handoff.

Safety result: no product runtime behavior, write route, write default, `APP_ENV=test` gate,
release/tag, package/image, production/stable/security claim, real/private book, app DB, backup,
`.env`, token, key, cert, screenshot/export, or private financial data was changed. The guard reads
only declared public documentation/configuration files and does not inspect `.env`, runtime books,
app DBs, backups, or private paths.

Verification result: new public status guard passed; targeted backend pytest for the guard and
safety/status tests passed; full backend pytest passed; frontend check/auth-routes/build passed;
Docker Compose config validation passed; `.env.example` and rendered Compose default
`GNUCASH_WRITES_ENABLED=false` were confirmed; `git diff --check` passed; tracked sensitive-file
hygiene scan passed.

## Phase 213 — v0.2.4 tagged fresh-clone smoke

Status: complete. Published `v0.2.4-writealpha` and current `HEAD` fresh-clone Docker/Caddy smokes
passed with committed synthetic fixture data and default-disabled writes.

Goal: verify the published `v0.2.4-writealpha` tag through an independent fresh-clone/tag path after
the cycle-1 release, using only synthetic/disposable data, dummy local-only secrets, read-only
API/browser flows, and disabled write probes.

Artifacts:

- `scripts/smoke/fresh-clone-docker-smoke.sh` — now runs browser dogfood at both mobile `320x720`
  and desktop `1280x900` widths for every fresh-clone smoke.
- `scripts/smoke/read-only-browser-dogfood.py` — treats viewports below `768px` as mobile and wider
  viewports as desktop for CDP emulation.
- `docs/dogfood/phase-213-v0.2.4-tagged-fresh-clone-smoke.md` — redacted smoke evidence for the
  published tag and current `HEAD` comparison.
- `docs/handoff/phase-213.md` — phase handoff.

Safety result: `GNUCASH_WRITES_ENABLED=false` remained default and was never changed to true. No
write-enabled mode, product runtime behavior change, release/tag, package/image, real/private/copied
personal book, only-copy book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw
private path, account name, memo, amount, or private financial data was added. Temporary clones and
Docker runtime were removed by helper teardown.

Verification result: `v0.2.4-writealpha` fresh-clone smoke passed; current `HEAD` comparison
fresh-clone smoke passed; both included Docker config/startup, `/api/health` with writes disabled,
read-only API smoke, validate/create/PATCH/DELETE returning 403, mobile and desktop browser dogfood,
auth cookie not readable from `document.cookie`, and no-artifact checks.

## Phase 214 — synthetic upgrade and app-metadata preservation smoke

Status: complete. Synthetic Docker upgrade smoke from `v0.2.4-writealpha` runtime state to current
`main` passed with dummy app metadata DB preservation and default-disabled writes.

Goal: verify a safe local upgrade path using only ignored synthetic runtime copies and dummy
local-only credentials, without losing app metadata access, default book access, selected-book
recovery, or the GnuCash read-only boundary.

Artifacts:

- `scripts/smoke/synthetic-upgrade-smoke.sh` — new synthetic upgrade helper for previous-ref to
  current-ref Docker/Caddy smoke.
- `apps/api/tests/test_upgrade_metadata_preservation.py` — targeted regression tests for safe
  app-metadata preservation and idempotent startup seed behavior.
- `docs/dogfood/phase-214-synthetic-upgrade-smoke.md` — redacted smoke command/result and safety
  evidence.
- `docs/handoff/phase-214.md` — phase handoff.

Safety result: `GNUCASH_WRITES_ENABLED=false` remained default and was never changed to true. The
smoke used only a temporary clone, committed synthetic fixture copy, dummy app metadata, and dummy
local-only credentials. No real/private book, real app DB, backup, `.env`, screenshot/export, token,
key, cert, raw private path, account name, memo, amount, migration wizard, release/tag,
package/image, or private financial data was added.

Verification result: synthetic upgrade smoke passed for login, default/selected book metadata, app
metadata DB readability, accounts, transactions, reports, scheduled metadata, write-alpha
audit-summary, safe selected-book recovery, Docker Compose config, and disabled
validate/create/PATCH/DELETE probes returning 403.

## Phase 218 — Write-alpha audit-summary pagination and operator review UX

Status: complete. Phase commit pushed after verification.

Goal: make the read-only write-alpha audit-summary usable for bounded operator review of large
synthetic app-metadata audit tables while preserving redaction and app-metadata-only behavior.

Artifacts:

- `apps/api/app/routers/transactions.py`, `apps/api/app/schemas/gnucash_writes.py`, and
  `apps/api/tests/test_write_alpha_audit_summary.py` — API pagination metadata and large synthetic
  redaction/access tests.
- `apps/web/src/routes/books/write-alpha-audit/`, `apps/web/src/lib/api/types.ts`,
  `apps/web/src/lib/i18n/messages.ts`, and `apps/web/scripts/test-auth-routes.mjs` — URL-only
  pagination/review UI and static safety guards.
- `docs/dogfood/phase-218-audit-summary-pagination-dogfood.md` — synthetic app-metadata-only dogfood
  evidence.
- `docs/handoff/phase-218.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Dogfood result: targeted backend synthetic app-metadata-only audit-summary tests passed for
owner/editor paged review, viewer/unauthorized blocking, large synthetic table bounded pages,
adjacent page separation, count/status summaries, and malicious row redaction. Frontend static route
checks passed for authenticated active-book loading, URL-only filters/pagination, safe field
rendering, mobile-safe controls, no browser storage, and no mutation/export/raw payload UI.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and no write-enabled mode was run. The
audit-summary route remains read-only and app-metadata-only; it does not open, parse, copy, mutate,
back up, restore, export, or lock a GnuCash book. No real/private book, real app DB, backup
artifact, `.env`, screenshot/export, token, key, cert, raw private path, account name, memo, amount,
production/security claim, or real/private-book write-safety claim was added.

Verification result: backend audit-summary tests passed; frontend auth-route/static checks passed;
full backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config
validation passed; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 219 — Accounting/safety localization glossary applied slice

Status: complete. Phase commit prepared after full standard verification.

Goal: turn the existing localization glossary issues into a practical EN/RU
operator-safety/accounting wording slice for visible release-critical flows.

Artifacts:

- `apps/web/src/lib/i18n/safety-glossary.ts` — small typed glossary catalog for release-critical
  safety/accounting terms and covered message keys.
- `apps/web/src/lib/i18n/messages.ts` — limited `/books` visible copy update from broad “management”
  wording to metadata-only wording in EN/RU.
- `apps/web/scripts/test-auth-routes.mjs` — frontend catalog/static checks for glossary terms,
  unsafe softened production/security/safe-write claims, and no browser storage.
- `docs/localization.md` — support update with canonical English and partial Russian glossary
  status.
- `docs/handoff/phase-219.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No backend API localization overhaul,
product behavior change, write-default change, `APP_ENV=test` gate change,
release/tag/package/image, real/private book, app DB, backup artifact, `.env`, screenshot/export,
token, key, cert, raw private path, account name, memo, amount, production/security claim, or
real/private-book write-safety claim was added. The new static checks reject unsafe softened wording
and new browser storage use in the localization slice.

Verification result: full backend pytest passed; frontend check/auth-routes/build passed; Docker
Compose config validation passed; `git diff --check` passed. Docs-link check was limited to
confirming no dedicated link-check script exists and the docs update references only tracked paths.

## Phase 220 — Cycle-2 full default-readonly and bounded write-alpha dogfood

Status: complete with no-release blocker. Phase commit prepared after dogfood and standard
verification.

Goal: collect a fresh release-candidate evidence pack after Phases 212–219 with default read-only
Docker/Caddy API/browser dogfood and a separate bounded synthetic/disposable write-alpha safety
drill.

Artifacts:

- `docs/dogfood/phase-220-cycle-2-release-candidate-dogfood.md` — redacted dogfood evidence,
  including default-read-only pass and the write-alpha DELETE backup-count blocker.
- `docs/handoff/phase-220.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Dogfood result: local Docker/Caddy default read-only mode passed with the committed synthetic
fixture copied into ignored runtime data and `GNUCASH_WRITES_ENABLED=false`. API smoke passed for
health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export,
reports summary, scheduled transaction metadata, write-alpha audit summary, and
validate/create/PATCH/DELETE disabled-write probes returning 403. Browser dogfood passed at
`320x720` and `1280x900` with hidden write UI, auth-cookie no-readability, CSV fetch, no-overflow
checks, and no screenshot/download/CSV artifacts.

Write-alpha result: a separate explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`
drill used only synthetic/disposable ignored runtime copies. Preflight, create smoke, and PATCH
smoke passed. DELETE route execution succeeded and redacted inspection confirmed API/runtime
absence, bounded backup evidence, one successful DELETE audit row, and stale-released/not-active
lock evidence, but the helper failed because backup file count did not increase by exactly one after
DELETE. Redacted inspection showed three successful backup-bearing route-family audit entries but
only two backup files. This is a no-release blocker until investigated and re-smoked.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and was re-confirmed after reset.
`APP_ENV=test` was not weakened. Smoke runtime book/backups/locks/generated app DB were cleaned; a
pre-existing ignored local app DB was restored as untracked local state. No real/private/only-copy
book, release/tag/package/image, committed runtime artifact, `.env`, backup, token, cookie, key,
cert, raw private path, account name, memo, amount, production/security claim, or real/private-book
write-safety claim was added.

Verification result: rendered Compose false before and after passed; read-only API smoke passed
before and after write-alpha reset; mobile and desktop browser dogfood passed; write-alpha
preflight/create/PATCH passed; write-alpha DELETE+restore smoke recorded the backup-count blocker
after successful DELETE; full backend pytest passed; frontend check/auth-routes/build passed; Docker
Compose config validation passed; `git diff --check` passed; tracked sensitive-file hygiene scan
passed.

## Phase 221 — v0.2.5-writealpha release gate / no-release verdict

Status: complete. Release gate failed safely; phase commit prepared after verification. No tag or
GitHub pre-release was published.

Goal: perform the final release gate for cycle 2 and publish conservative `v0.2.5-writealpha` only
if Phases 212–220 produced safe, meaningful changes/evidence with intact read-only defaults.

Artifacts:

- `docs/release/v0.2.5-writealpha-notes.md` — conservative no-release notes for the evaluated
  candidate.
- `docs/release/v0.2.5-writealpha-checklist.md` — release checklist with failed write-alpha evidence
  gate.
- `docs/release/v0.2.5-writealpha-final-gate.md` — final gate with explicit FAIL verdict.
- `docs/release/v0.2.5-writealpha-no-release-verdict.md` — blocker and next safe engineering phase.
- `docs/handoff/phase-221.md` — phase handoff.
- `README.md`, `README.ru.md`, `docs/ROADMAP.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public status
  synchronized to completed Phase 221 while keeping `v0.2.4-writealpha` as the current published
  write-alpha pre-release.

Gate result: local standard checks and default-read-only safety checks passed, candidate tag/release
absence was confirmed, and `GNUCASH_WRITES_ENABLED=false` remained default. The release was blocked
because Phase 220 found a bounded write-alpha DELETE backup-count anomaly after successful
synthetic/disposable DELETE route execution: successful backup-bearing route-family audit rows
exceeded backup file count. Therefore `v0.2.5-writealpha` was not published.

Safety result: no write route, write scope, write default, `APP_ENV=test` gate, product behavior,
package/image, tag/release, real/private/only-copy book, app DB, backup artifact, `.env`,
screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security
claim, or real/private-book write-safety claim was added.

Verification result: full backend pytest passed; frontend check/auth-routes/build passed; Docker
Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED=false`; `.env.example` default
false was confirmed; `git diff --check` passed; public status guard passed; tracked sensitive-file
hygiene scan passed; local/remote tag and GitHub release for `v0.2.5-writealpha` remained absent.

## Phase 222 — DELETE backup artifact/accounting reconciliation

Status: complete. Backup artifact collision/overwrite cause fixed with targeted regression coverage;
phase commit prepared after full verification.

Goal: investigate and resolve the Phase 220 write-alpha DELETE backup-count mismatch where
successful backup-bearing route-family audit rows exceeded readable backup files.

Artifacts:

- `apps/api/app/services/backup.py` — backup filenames now include microseconds, deterministic
  suffix fallback, and exclusive-create copy so existing backup artifacts are not overwritten
  silently.
- `apps/api/tests/test_backup_restore.py` — regression freezes the backup clock and proves three
  rapid backups for one synthetic fixture copy produce three distinct readable artifacts with no
  overwrite.
- `docs/dogfood/phase-222-delete-backup-reconciliation.md` — redacted investigation/fix evidence.
- `docs/handoff/phase-222.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Finding: the Phase 220 evidence shape is explained by second-precision backup filename collisions
for rapid same-named disposable runtime copies plus overwrite-capable `shutil.copy2`. The fix
hardens backup evidence identity only; create/PATCH/DELETE mutation semantics, write scope,
defaults, and gates are unchanged.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No write endpoint, write route family, release/tag/package/image, real/private/only-copy book,
runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path,
account name, memo, amount, production/security claim, or real/private-book write-safety claim was
added.

Verification result: targeted backend tests passed for backup uniqueness/no-overwrite and
default-disabled write probes; smoke helpers compiled; full backend pytest passed; frontend
check/auth-routes/build passed; Docker Compose config validation passed; `git diff --check` passed;
tracked sensitive-file hygiene scan passed. Later roadmap phases still need to rerun bounded
synthetic/disposable write-alpha route-family dogfood before any release gate.

## Phase 223 — Backup naming collision and monotonic evidence hardening

Status: complete. Backup artifact identity and redacted operator evidence were hardened after the
Phase 222 collision fix.

Goal: prove rapid create/PATCH/DELETE route-family writes cannot collide, overwrite, or produce
ambiguous backup evidence, while keeping operator output redacted.

Artifacts:

- `apps/api/app/routers/transactions.py` and `apps/api/app/schemas/gnucash_writes.py` — audit rows
  now store a bounded opaque `backup_artifact_ref` derived from backup evidence; read-only audit
  summary exposes that ref without raw paths or filenames.
- `apps/api/tests/test_transaction_writes.py` — route-family regression freezes the backup clock and
  performs fast create/PATCH/DELETE writes against a synthetic disposable fixture, proving three
  unique readable backup artifacts and matching audit rows.
- `apps/api/tests/test_write_alpha_audit_summary.py` — redaction tests now pin opaque backup refs,
  no raw backup paths/filenames, and no financial/private payload leakage.
- `apps/web/src/lib/api/types.ts`, `apps/web/src/lib/i18n/messages.ts`, and
  `apps/web/src/routes/books/write-alpha-audit/+page.svelte` — operator UI can display the opaque
  backup ref while preserving redaction.
- `docs/dogfood/phase-223-backup-identity-evidence.md` — redacted backup identity evidence note.
- `docs/handoff/phase-223.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Finding: Phase 222 already fixed overwrite-capable naming. Phase 223 adds deterministic route-family
coverage and redacted monotonic evidence so operators can distinguish successful backup artifacts by
opaque refs without exposing raw artifact paths, filenames, account names, memos, amounts, or
private financial data.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
Write-alpha execution remains limited to explicit `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`
synthetic/disposable scope. No write endpoint, write scope expansion, release/tag/package/image,
real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`,
screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security
claim, or real/private-book write-safety claim was added.

Verification result: targeted backup service, route-family, and audit-summary tests passed; full
backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config validation
passed with rendered `GNUCASH_WRITES_ENABLED=false`; `git diff --check` passed; tracked
sensitive-file hygiene scan passed.

## Phase 224 — Write-alpha DELETE restore proof v2

Status: complete. A bounded synthetic/disposable DELETE route-family dogfood rerun passed after the
Phase 222/223 backup evidence hardening.

Goal: rerun exactly one explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` DELETE
smoke on an ignored synthetic runtime copy and prove backup restore/read-back reliability before
later route-family matrix/release-gate phases.

Artifacts:

- `docs/dogfood/phase-224-delete-restore-v2.md` — redacted DELETE restore proof evidence.
- `docs/handoff/phase-224.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Finding: exactly one routed DELETE succeeded against the ignored synthetic runtime copy. API and
runtime SQLite absence checks confirmed deletion; exactly one successful `transaction.delete` audit
row and one corresponding backup artifact were identified. The host-side helper could not perform
the restore copy because the backup artifact was root-owned, so the successful mutation was not
rerun; a follow-up API-container restore proof used the same single backup artifact, matched restore
checksum evidence, and read the restored deleted transaction back through SQLite and the API.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No create/PATCH route, write endpoint, release/tag/package/image, real/private/only-copy book,
committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw
path, account name, memo, amount, production/security claim, or real/private-book write-safety claim
was added.

Verification result: write-alpha DELETE smoke passed for one DELETE, API/runtime absence, one backup
increment, one success-audit increment, backup transaction evidence, and stale-released/non-active
lock evidence; container-side restore proof passed on the same backup; default read-only API smoke
passed after reset with validate/create/PATCH/DELETE returning 403; stopped-runtime cleanup passed
with `--via-compose` for root-owned artifacts; full backend pytest passed; frontend
check/auth-routes/build passed; Docker Compose config validation passed; `git diff --check` passed.

## Phase 225 — Combined create/PATCH/DELETE backup-audit matrix

Status: complete. A fresh bounded synthetic/disposable write-alpha create, PATCH, and DELETE
backup-audit matrix passed after the Phase 222/223/224 backup evidence hardening.

Goal: produce aligned route-family backup/audit/read-back/lock evidence for create, PATCH, and
DELETE without expanding write scope or claiming real/private-book write safety.

Artifacts:

- `docs/dogfood/phase-225-write-alpha-matrix.md` — redacted combined write-alpha route-family matrix
  evidence.
- `docs/handoff/phase-225.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Finding: create, PATCH, and DELETE each passed once on isolated ignored synthetic/disposable runtime
copies. Every successful routed write had one backup file count and one successful audit row with
backup evidence in its isolated run. Create validation probes rejected
unbalanced/invalid-account/placeholder-style payloads before mutation; PATCH missing-transaction
returned 404 with no backup and one failed no-backup audit row; DELETE restore/read-back passed from
the host-readable backup. Locks were stale-released/not active after each route family, and helpers
did not rerun successful mutations after evidence collection.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
Write-enabled runs were explicit, local, synthetic/disposable only, and cleaned afterward. No write
endpoint, write feature expansion, release/tag/package/image, real/private/only-copy book, committed
runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path,
account name, memo, amount, production/security claim, or real/private-book write-safety claim was
added.

Verification result: write-alpha create, PATCH, and DELETE smoke helpers passed; redacted per-run
count checks showed one backup and one success-audit per successful route-family write; default
read-only API smoke passed after reset with validate/create/PATCH/DELETE returning 403;
stopped-runtime cleanup passed and final dry-run reported zero runtime artifacts; targeted backend
route-family pytest passed; full backend/frontend/Docker/diff/sensitive-file checks passed.

## Phase 226 — Read-only regression after write-alpha remediation

Status: complete. Default-read-only Docker/Caddy API and browser regression passed after write-alpha
backup/evidence remediation.

Goal: confirm that write-alpha backup/evidence remediation did not regress the default read-only
product path.

Artifacts:

- `docs/dogfood/phase-226-default-readonly-regression.md` — redacted default-read-only regression
  evidence.
- `docs/handoff/phase-226.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status synchronized.

Finding: Docker/Caddy ran with the committed synthetic fixture copied into ignored runtime storage
and `GNUCASH_WRITES_ENABLED=false` rendered for API and web. API smoke passed health, login/auth,
books/default book, accounts, transactions, transaction detail, CSV export, reports summary,
scheduled transaction metadata, write-alpha audit summary, and validate/create/PATCH/DELETE
disabled-write probes returning 403. Browser dogfood passed at `320x720` and `1280x900` with write
UI hidden, auth cookie not readable from `document.cookie`, CSV fetch success without saved raw
artifact, no horizontal overflow, and no screenshot/download/CSV artifacts.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default. No write-enabled run was performed.
Runtime used only a committed synthetic fixture copied into ignored `data/books/`; smoke app
DB/runtime book artifacts were removed by stopped-runtime cleanup. No real/private/only-copy book,
committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw
path, account name, memo, amount, production/security claim, or real/private-book write-safety claim
was added.

Verification result: Docker Compose config validation passed with rendered false for API/web;
read-only API smoke passed; mobile and desktop browser dogfood passed; stopped-runtime cleanup final
dry-run reported zero runtime artifacts; full backend pytest passed; frontend
check/auth-routes/build passed; `git diff --check` passed; tracked sensitive-file hygiene scan
passed.

## Phase 227 — Operator-facing no-release blocker closure UX

Status: complete. Operator/release docs now explain the resolved Phase 220 no-release blocker
narrowly as synthetic/disposable backup-audit evidence remediation.

Goal: make the blocker closure understandable in release-support and troubleshooting/runbook
artifacts without claiming production write safety.

Artifacts:

- `docs/release/v0.2.5-writealpha-blocker-closure.md` — concise blocker-closure note.
- `docs/release/v0.2.5-writealpha-no-release-verdict.md` and
  `docs/release/v0.2.5-writealpha-final-gate.md` — later-context addenda preserving the Phase 221
  no-release result.
- `docs/operations/backup-and-recovery.md` and `docs/operations/troubleshooting.md` —
  operator-facing backup/audit evidence expectations and safe troubleshooting wording.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `scripts/check_public_status.py`,
  and `apps/api/tests/test_public_status_guard.py` — public/status guard synchronization to Phase
  227 while retaining `v0.2.4-writealpha` as the current published write-alpha release.
- `docs/handoff/phase-227.md` — phase handoff.

Finding: the Phase 220 blocker is closed only as synthetic/disposable evidence remediation after
Phases 222–226. Documentation now states that matching redacted audit rows and readable backup
artifacts were re-established after the backup identity fix, while `v0.2.5-writealpha` remains
unpublished and `v0.2.4-writealpha` remains the current public write-alpha release.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No UI/product behavior, write route, write scope, release/tag/package/image, real/private/only-copy
book, committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert,
raw path, account name, memo, amount, production/security claim, public-internet-safety claim, or
real/private-book write-safety claim was added.

Verification result: public status guard passed; markdown readability/link spot check passed; full
backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config validation and
rendered-false grep passed; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 228 — Fresh-clone and upgrade smoke after remediation

Status: complete. Current `HEAD` passed fresh-clone Docker/Caddy smoke and synthetic
`v0.2.4-writealpha` runtime-state upgrade smoke with default-disabled writes.

Goal: verify a clean checkout and synthetic upgrade path after the write-alpha backup/audit
remediation, before any release gate.

Artifacts:

- `docs/dogfood/phase-228-fresh-clone-upgrade-after-remediation.md` — redacted fresh-clone and
  synthetic upgrade evidence.
- `docs/handoff/phase-228.md` — phase handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — factual status synchronization.

Finding: `scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref
HEAD --port 18084` passed for current `HEAD` `059b40f` with the committed synthetic fixture copied
into a temporary ignored runtime path, read-only API smoke, browser dogfood at `320x720` and
`1280x900`, hidden write UI, auth-cookie no-readability, CSV fetch without saved raw artifact, and
validate/create/PATCH/DELETE disabled-write probes returning 403.
`scripts/smoke/synthetic-upgrade-smoke.sh --repo /home/val/gnucash-web-companion --previous-ref
v0.2.4-writealpha --current-ref HEAD --port 18085` passed from previous checkout `05f9080` to
current `059b40f`, preserving dummy app metadata DB readability, default book access, selected-book
recovery, read-only route access, write-alpha audit summary, and disabled
validate/create/PATCH/DELETE probes returning 403 after upgrade.

Safety result: `GNUCASH_WRITES_ENABLED=false` remained active throughout, and `APP_ENV=test` was not
weakened. Temporary clones used only the committed synthetic fixture, dummy local-only credentials,
and ignored runtime paths; helper teardown removed Docker runtime and temp clones. No write-enabled
run, migration feature work, release/tag/package/image, real/private/only-copy book, committed
runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path,
account name, memo, amount, production/security claim, broad migration guarantee, or
real/private-book write-safety claim was added.

Verification result: fresh-clone smoke passed; synthetic upgrade smoke passed; post-smoke Docker
cleanup check reported no `gwc_fresh_clone`/`gwc_synthetic_upgrade` leftovers; public status guard
passed; full backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config
validation and rendered-false grep passed; `git diff --check` passed; tracked sensitive-file hygiene
scan passed.

## Phase 229 — Public status and release-doc drift guard refresh

Status: complete. Public status and release-support drift guard expectations refreshed after Phases
222–228; no release or tag was published.

Goal: refresh public status guard expectations after the Phase 222–228 write-alpha backup/audit
remediation so release docs cannot drift again before the later release-gate phase.

Artifacts:

- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`, and
  `docs/release/v0.2.5-writealpha-*` — public/release-support posture synchronized to completed
  Phase 229 while retaining `v0.2.4-writealpha` as the current published write-alpha pre-release and
  `v0.1.7-readonly` as the current read-only pre-release.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — guard
  expectations updated to Phase 229 and expanded to cover the `v0.2.5-writealpha` no-release/support
  docs, while still reading only declared public docs/config files.
- `docs/handoff/phase-229.md` — phase handoff.

Finding: public docs now agree that Phase 229 is complete, `v0.2.5-writealpha` remains unpublished
with no tag or GitHub release from this phase, and the Phase 220 no-release blocker closure is
described only as synthetic/disposable evidence remediation. The current public release state
remains `v0.1.7-readonly` for read-only and `v0.2.4-writealpha` for write-alpha until a later
authorized release phase succeeds.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
The status guard reads only tracked public docs/config files and does not inspect `.env`, runtime
books, app DBs, backups, private paths, screenshots, exports, tokens, or secrets. No product
behavior, write route, write scope, release/tag/package/image, real/private/only-copy book,
committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw
path, account name, memo, amount, production/security claim, public-internet-safety claim, or
real/private-book write-safety claim was added.

Verification result: public status guard passed; backend public-status guard tests passed; full
backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config validation
passed; `git diff --check` passed; tracked sensitive-file hygiene scan passed.

## Phase 230 — Final release-candidate dogfood pack

Status: complete. Final release-candidate dogfood evidence passed for a later `v0.2.5-writealpha`
attempt; no release or tag was published.

Goal: produce the final release-candidate evidence pack after the Phase 222–229 backup/audit
remediation and status-drift refresh.

Artifacts:

- `docs/dogfood/phase-230-cycle-3-release-candidate-dogfood.md` — redacted default-read-only
  API/browser dogfood, write-alpha create/PATCH/DELETE matrix, DELETE restore proof, default-false
  reset, cleanup, and Phase 10 release input.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public/status
  guard synchronization to Phase 230 while retaining `v0.2.4-writealpha` as the current published
  write-alpha release.
- `docs/handoff/phase-230.md` — phase handoff.

Finding: default-read-only Docker/Caddy dogfood passed with `GNUCASH_WRITES_ENABLED=false`,
including read-only API smoke, disabled validate/create/PATCH/DELETE probes returning 403, and
browser dogfood at `320x720` and `1280x900` with hidden write UI, auth-cookie no-readability, CSV
fetch without saved artifact, and no horizontal overflow. Separate explicit local `APP_ENV=test`
plus `GNUCASH_WRITES_ENABLED=true` write-alpha smokes passed once each for create, PATCH, and DELETE
on fresh ignored synthetic/disposable runtime copies; every successful write had matching
backup/audit evidence, DELETE restore proof passed, locks were stale-released/not active, and
successful mutations were not rerun after evidence collection. The stack was reset to default false
and read-only API smoke passed again.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
Write-alpha execution stayed bounded to explicit local synthetic/disposable copies under ignored
runtime storage. No product feature, write scope expansion, release/tag/package/image,
real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`,
screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security
claim, public-internet-safety claim, broad compatibility claim, or real/private-book write-safety
claim was added.

Verification result: default-read-only API/browser dogfood passed; create/PATCH/DELETE write-alpha
smoke helpers passed; DELETE restore proof passed; default-false reset read-only API smoke passed;
stopped-runtime cleanup final dry-run reported zero runtime artifacts; public status guard passed;
full backend pytest passed; frontend check/auth-routes/build passed; Docker Compose config
validation and rendered-false grep passed; `git diff --check` passed; tracked sensitive-file hygiene
scan passed.

## Phase 231 — v0.2.5-writealpha release gate and publication

Status: complete. `v0.2.5-writealpha` was published as a conservative GitHub pre-release after the
final Cycle 3 release gate and exact release/status commit CI.

Goal: inspect current `main`, Phase 222–230 remediation/dogfood evidence, release/status artifacts,
GitHub tag/release absence, local backend/frontend/Docker checks, public status guard,
sensitive-file hygiene, and exact release-commit CI; publish only if all gates pass.

Artifacts:

- `docs/release/v0.2.5-writealpha-notes.md` — conservative pre-alpha write-alpha release notes with
  disabled-by-default and `APP_ENV=test` safety boundaries.
- `docs/release/v0.2.5-writealpha-checklist.md` — final release checklist.
- `docs/release/v0.2.5-writealpha-final-gate.md` — final gate decision.
- `docs/release/v0.2.5-writealpha-publication-evidence.md` — publication evidence for tag/GitHub
  pre-release.
- `docs/release/v0.2.5-writealpha-no-release-verdict.md` — historical Phase 221 no-release verdict
  marked superseded by Phase 231 publication.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public/status
  guard synchronization to Phase 231 and `v0.2.5-writealpha` as the current published write-alpha
  pre-release.
- `docs/handoff/phase-231.md` — phase handoff.

Finding: the Phase 220 no-release blocker is closed in the narrow synthetic/disposable evidence
sense. Phase 222 fixed backup artifact collision/overwrite risk, Phases 223–225 proved
backup/audit/restore evidence, Phase 226 rechecked the default read-only path, Phase 228 rechecked
fresh-clone/upgrade with disabled writes, Phase 229 refreshed drift guards, and Phase 230 produced a
green final release-candidate dogfood pack. Phase 231 local checks and exact release/status commit
CI passed before publication.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
Publication created only an annotated tag and GitHub pre-release. No package, binary artifact,
Docker image, production deployment, write-default change, write-scope expansion,
real/private/only-copy book, runtime book, app DB, backup artifact, `.env`, screenshot/export,
token, key, cert, raw path, account name, memo, amount,
production/security/stable/public-internet/broad-compatibility claim, or real/private-book
write-safety claim was added.

Verification result: backend pytest passed; frontend check/auth-routes/build passed; Docker Compose
config passed; rendered Compose and `.env.example` kept `GNUCASH_WRITES_ENABLED=false`; public
status guard passed; `git diff --check` passed; sensitive tracked-file hygiene scan passed;
tag/release absence was confirmed before publication; exact release/status commit GitHub Actions
passed; `HEAD == origin/main` and clean tracked tree were verified after push/publication.

## Phase 232 — Public status and changelog reconciliation after v0.2.5

Status: complete. Public repository status was reconciled after the published `v0.2.5-writealpha`
pre-release.

Goal: verify README, README.ru, PROJECT_STATUS, CHANGELOG, docs/ROADMAP, release notes, and GitHub
release state agree that `v0.2.5-writealpha` is published while write-alpha remains
default-disabled, `APP_ENV=test` gated, and backed only by synthetic/disposable or copied-test-book
evidence.

Artifacts:

- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, and `PROJECT_STATUS.md` — public
  status synchronized to completed Phase 232 while keeping `v0.2.5-writealpha` as the current
  published write-alpha pre-release and `v0.1.7-readonly` as the current read-only pre-release.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — guard
  expectations moved to Phase 232 while keeping the release baseline at Phase 231 publication.
- `docs/handoff/phase-232.md` — phase handoff.

Finding: current public-state wording no longer implies `v0.2.5-writealpha` is merely prepared,
draft, or unpublished. Historical no-release/prepared wording remains only where it describes
earlier phase state. GitHub release state confirms `v0.2.5-writealpha` exists as the current
write-alpha pre-release.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No product code, release/tag/package/image, write-mode behavior change, real/private/only-copy book,
committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw
path, account name, memo, amount, production/security/stable/public-internet/broad-compatibility
claim, or real/private-book write-safety claim was added.

Verification result: public status guard passed; GitHub release lookup confirmed `v0.2.5-writealpha` exists
as a non-draft pre-release; backend public-status guard tests and full backend pytest passed; frontend
`npm run check`, `npm run test:auth-routes`, and `npm run build` passed; Docker Compose config
validation passed and rendered `GNUCASH_WRITES_ENABLED=false`; `git diff --check` passed;
`.env.example` still contains `GNUCASH_WRITES_ENABLED=false`; targeted stale-current grep found only
historical earlier-phase references, not current posture drift; sensitive tracked-file hygiene scan
passed.

## Phase 233 — README and markdown source readability pass

Status: complete. README and key status markdown sources were reformatted for raw terminal/editor
readability.

Goal: materially advance GitHub issue #28 by making README, README.ru, CHANGELOG, and PROJECT_STATUS
readable as raw markdown, not only as rendered GitHub HTML.

Artifacts:

- `README.md` and `README.ru.md` — long current-status, release, comparison, safety, and guidance
  lines wrapped into readable paragraphs/lists while preserving links and safety wording.
- `CHANGELOG.md` — long release/history bullets wrapped for raw markdown readability; Phase 233 entry
  added under Unreleased.
- `PROJECT_STATUS.md` — long status/history paragraphs wrapped; current baseline advanced to Phase
  233 and this phase section added.
- `docs/ROADMAP.md`, `scripts/check_public_status.py`, and
  `apps/api/tests/test_public_status_guard.py` — public status guard synchronized because the current
  completed phase advanced to Phase 233.
- `docs/handoff/phase-233.md` — phase handoff.

Finding: the raw source no longer depends on very long single-line paragraphs for the in-scope public
status documents. The pass preserved existing links/content and did not rewrite product positioning.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened. No
product code, release/tag/package/image, write-mode behavior change, real/private/only-copy book,
committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw
path, account name, memo, amount, production/security/stable/public-internet/broad-compatibility
claim, or real/private-book write-safety claim was added.

Verification result: markdown link sanity check passed for the reformatted files; public status guard
passed; backend public-status guard tests passed; `git diff --check` passed; `.env.example` still
contains `GNUCASH_WRITES_ENABLED=false`; tracked sensitive-file hygiene scan passed.

## Phase 234 — Copied-book write-alpha dogfood runbook v1

Status: complete. A conservative copied/disposable write-alpha dogfood runbook was added for future
maintainer use; no real/private copied-book dogfood was performed.

Goal: create a narrow runbook for future copied-book write-alpha dogfood that is usable by a
maintainer while avoiding any implication that real/private or only-copy books are safe write targets.

Artifacts:

- `docs/write-alpha/copied-book-dogfood-runbook.md` — requires copied/disposable books outside git,
  original/only-copy books forbidden, an independent backup before mutation, local-only Docker,
  explicit `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test`, one mutation at a time, strict stop
  conditions, redaction rules, restore verification, and reset to `GNUCASH_WRITES_ENABLED=false`.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public status
  synchronized to completed Phase 234 while keeping `v0.2.5-writealpha` as the current published
  write-alpha pre-release and `v0.1.7-readonly` as the current read-only pre-release.
- `docs/handoff/phase-234.md` — phase handoff.

Finding: the runbook is preparatory and conservative. It tells maintainers to stop before mutation if
an original/only-copy book, inside-git copy, non-test app environment, missing backup, public exposure,
inconsistent audit/backup/lock/restore evidence, or unredactable private evidence appears.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened. No
copied-book dogfood, product code, UI feature, release/tag/package/image, write-mode default change,
real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`, screenshot/CSV
export, token, key, cert, raw path, account name, memo, amount, production/security/stable/public-internet/broad-compatibility claim, or real/private-book write-safety claim was added.

Verification result: documentation review passed; `python3 scripts/check_public_status.py` passed;
`cd apps/api && pytest tests/test_public_status_guard.py -q` passed; `git diff --check` passed;
`.env.example` still contains `GNUCASH_WRITES_ENABLED=false`.

## Phase 235 — Copied/disposable target preflight CLI

Status: complete. A local-only redacted preflight CLI was added for future copied/disposable
write-alpha dogfood targets; no copied/private book was opened, copied, or mutated.

Goal: implement a preflight that helps an operator reject unsafe write-alpha targets before any
copied-book dogfood run while preserving the default-disabled and `APP_ENV=test` write-alpha gates.

Artifacts:

- `scripts/write_alpha_preflight.py` — requires an explicit target path, rejects missing/unreadable
  files and targets inside the git working tree, validates backup destinations as outside git or
  git-ignored, blocks unless `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`, emits redacted normal
  output, and warns on original/production-looking names without printing raw paths.
- `apps/api/tests/test_write_alpha_preflight_cli.py` — targeted regression coverage for missing,
  inside-git, unsafe environment, unsafe backup destination, ready redacted warning output, and CLI
  nonzero/ redaction behavior.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public status
  synchronized to completed Phase 235 while preserving the current public release posture.
- `docs/handoff/phase-235.md` — phase handoff.

Finding: the CLI is a local preflight only. It does not enable writes automatically, upload a book,
open a book with piecash, copy a book, create backups, or mutate GnuCash data.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No real/private/only-copy book, copied-book dogfood run, product runtime default change, release/tag,
app DB, backup artifact, `.env`, screenshot/CSV export, token, key, cert, raw path, account name,
memo, amount, production/security/stable/public-internet/broad-compatibility claim, or
real/private-book write-safety claim was added.

Verification result: targeted preflight tests passed; public status guard and public-status tests
passed; `git diff --check` passed; sensitive tracked-file hygiene scan passed; `.env.example` still
contains `GNUCASH_WRITES_ENABLED=false`; Docker Compose config rendered successfully with dummy local
secrets.

## Phase 236 — Redacted dogfood evidence schema

Status: complete. A redacted dogfood evidence schema and helper were added for future
copied/disposable reports; no copied/private book was opened, copied, backed up, or mutated.

Goal: standardize future dogfood evidence so phase/scenario/classification/commands/result/redacted
artifact refs, backup/audit counts, lock/restore/default-reset statuses, and pass/fail state can be
recorded without leaking private financial data.

Artifacts:

- `docs/write-alpha/dogfood-evidence-schema.md` — required field schema, JSON placeholder example,
  review checklist, and explicit ban on raw paths, account names, descriptions, memos, amounts,
  payloads, screenshots, CSV exports, books, backups, app DBs, `.env`, tokens, keys, or certs.
- `scripts/redact_dogfood_evidence.py` — local JSON helper with reject/redact modes for path-like,
  amount-like, sensitive-key, and float values.
- `apps/api/tests/test_redact_dogfood_evidence.py` — targeted helper regression coverage for safe
  schema evidence, reject mode, redact mode, and CLI non-leak behavior.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public status
  synchronized to completed Phase 236 while preserving the current public release posture.
- `docs/handoff/phase-236.md` — phase handoff.

Finding: the helper is a redaction/rejection guard only. It does not open GnuCash books, parse
financial rows, create backups, acquire locks, call write routes, or mutate data.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` was not weakened.
No real/private/only-copy book, copied-book dogfood run, product runtime default change, release/tag,
app DB, backup artifact, `.env`, screenshot/CSV export, token, key, cert, raw path, account name,
memo, amount, production/security/stable/public-internet/broad-compatibility claim, or
real/private-book write-safety claim was added.

Verification result: targeted redaction-helper tests passed; public status guard and public-status
tests passed; `git diff --check` passed; sensitive tracked-file hygiene scan passed; `.env.example`
still contains `GNUCASH_WRITES_ENABLED=false`; Docker Compose config rendered successfully with dummy
local secrets.

## Phase 237 — Write-alpha environment template and operator guard documentation

Status: complete. A local-only write-alpha environment reference and operator guidance were added;
normal read-only defaults were not changed and no write mode was enabled.

Goal: provide safe operator-facing environment guidance for explicit write-alpha testing without
making write mode easy to enable accidentally.

Artifacts:

- `.env.writealpha.example` — clearly marked as a dangerous reference, not a default template; it
  requires `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`, forbids blind copy to `.env`, forbids
  real/private/original/only-copy books, and keeps the example local-only with exact origins.
- `docs/write-alpha/environment.md` — operator guidance for default read-only posture, required
  write-alpha gates, allowed synthetic/disposable/copied-test books only, no public exposure,
  original-book exclusion, reset expectations, and verification commands.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`,
  `scripts/check_public_status.py`, and `apps/api/tests/test_public_status_guard.py` — public status
  synchronized to completed Phase 237 while preserving the current public release posture.
- `docs/handoff/phase-237.md` — phase handoff.

Finding: `.env.writealpha.example` is intentionally not a safe default and is not referenced by
Docker Compose. It is an operator reference for future explicit local write-alpha tests only.

Safety result: `.env.example` still contains `GNUCASH_WRITES_ENABLED=false`, Docker Compose still
renders `GNUCASH_WRITES_ENABLED=false` by default, and the backend `APP_ENV=test` write-alpha gate was
not weakened. No real/private/only-copy book, copied-book dogfood run, product runtime default
change, release/tag, app DB, backup artifact, `.env`, screenshot/CSV export, token, key, cert, raw
path, account name, memo, amount, production/security/stable/public-internet/broad-compatibility
claim, or real/private-book write-safety claim was added.

Verification result: Docker Compose config rendered successfully with dummy local secrets and showed
`GNUCASH_WRITES_ENABLED=false`; public status guard passed; public-status tests passed; `git diff
--check` passed; sensitive tracked-file hygiene scan passed with `.env.writealpha.example` allowlisted
as an intended operator reference.

## Phase 262 — current-state analyst gate after v0.2.8

Phase 262 passed the post-`v0.2.8-writealpha` current-state analyst gate. The review covered
README, README.ru, PROJECT_STATUS, CHANGELOG, docs/ROADMAP, recent git history, GitHub releases,
open issues, recent CI, `.env.example`, rendered Docker Compose defaults, and the public-status
guard. The repository is coherent after publication: `v0.2.8-writealpha` is published as the current
experimental write-alpha pre-release, `v0.1.7-readonly` remains the current public read-only
pre-release, issue #36 remains the controlled-write readiness tracker, and recent `main` CI was green
through Phase 261.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example` and rendered Compose,
the backend write-alpha posture remains `APP_ENV=test` gated when explicitly enabled, and the public
docs still avoid production/security/public-internet/broad-compatibility and real/private/only-copy
write-safety claims. Owner copied-book dogfood remains pending/absent in the repository evidence; the
next approved owner-facing step remains dry-run preparation only, not CREATE-one.

Verification result: `git status --short`, `git log --oneline -20`, `gh release list --limit 10`,
`gh issue list --state open --limit 50`, `gh run list --limit 10`, rendered Compose grep for
`GNUCASH_WRITES_ENABLED`/`APP_ENV`, `python3 scripts/check_public_status.py`, and `git diff --check`
were run. The local pre-existing untracked `.hermes/` runtime logs were not used as evidence and were
not committed.

Artifacts:

- `docs/audits/phase-262-current-state-gate.md`
- `docs/handoff/phase-262.md`

## Phase 307 — Phase 306 docs-only verification

Status: complete. Phase 306 reset/default-disabled checklist hardening was verified as a docs-only outcome. Link target, public status guard, diff hygiene, and sensitive tracked-file hygiene passed; no mutation or release work occurred.

Artifacts:

- `docs/handoff/phase-307.md`

## Phase 308 — Public status reconciliation

Status: complete. Public status sources were reconciled to completed Phase 308 while preserving `v0.1.7-readonly` and `v0.2.8-writealpha` as the current public releases.

Artifacts:

- `docs/handoff/phase-308.md`

## Phase 309 — Cycle 2 release/no-release decision

Status: complete. PM decision: `NO_RELEASE`. Cycle 2 maintenance documentation and verification did not warrant a release.

Artifacts:

- `docs/release/cycle-2-release-decision.md`
- `docs/handoff/phase-309.md`

## Phase 310 — Cycle 2 no-publication execution

Status: complete. The no-release decision was executed as no-publication; no tag, release, package, image, stable release, or production deployment was created.

Artifacts:

- `docs/release/cycle-2-no-release-verdict.md`
- `docs/handoff/phase-310.md`

## Phase 311 — Cycle 3 analyst gate

Status: complete. Cycle 3 selected exactly one practical maintenance task: an owner-feedback gate for future write-alpha dogfood progression.

Artifacts:

- `docs/audits/phase-311-cycle-3-gate.md`
- `docs/handoff/phase-311.md`

## Phase 312 — Owner-feedback gate

Status: complete. Added the owner-feedback gate for future write-alpha dogfood. New owner mutation scope now requires fresh live-stand feedback or exact same-context confirmation.

Artifacts:

- `docs/write-alpha/owner-feedback-gate.md`
- `docs/handoff/phase-312.md`

## Phase 313 — Regression and hygiene pass

Status: complete. Public status, diff hygiene, and sensitive tracked-file hygiene were included in the final gate; no runtime/private artifacts were staged.

Artifacts:

- `docs/handoff/phase-313.md`

## Phase 314 — Owner-facing status digest

Status: complete. Added a concise owner status digest: read-only use is the practical path; write-alpha waits for fresh owner need and a new exact confirmation packet.

Artifacts:

- `docs/write-alpha/owner-status-digest.md`
- `docs/handoff/phase-314.md`

## Phase 315 — Cycle 3 release/no-release decision

Status: complete. PM decision: `NO_RELEASE`. Guidance-only maintenance changes do not warrant a release.

Artifacts:

- `docs/release/cycle-3-release-decision.md`
- `docs/handoff/phase-315.md`

## Phase 316 — Cycle 3 no-publication execution

Status: complete. The no-release decision was executed as no-publication; `v0.2.8-writealpha` remains the current public experimental write-alpha pre-release.

Artifacts:

- `docs/release/cycle-3-no-release-verdict.md`
- `docs/handoff/phase-316.md`

## Phase 317 — Maintenance-mode decision

Status: complete. PM decision: enter maintenance/wait mode for active write-alpha phase work until fresh owner live-stand feedback or a new exact same-context confirmation packet exists.

Artifacts:

- `docs/audits/phase-317-maintenance-decision.md`
- `docs/handoff/phase-317.md`

## Phase 318 — Maintenance-mode implementation

Status: complete. Added `docs/MAINTENANCE_MODE.md` and updated public/status docs to avoid implying active write-alpha phase momentum.

Artifacts:

- `docs/MAINTENANCE_MODE.md`
- `docs/handoff/phase-318.md`

## Phase 319 — Open-issue triage without noise

Status: complete. Open issues #36, #22, #28, #17, #29, and #13 were inspected. No comments were posted because GitHub CLI auth is invalid and no closure/comment was necessary.

Artifacts:

- `docs/handoff/phase-319.md`

## Phase 320 — Final 30-phase summary and next owner action

Status: complete. Final summary recorded. Active write-alpha phase work is in maintenance/wait mode. No immediate owner action is required; continue read-only use/testing and provide fresh live-stand feedback before any future write-alpha mutation.

Artifacts:

- `docs/handoff/phase-320-final-summary.md`
- `docs/handoff/phase-320.md`

Safety result for Phases 307–320: `GNUCASH_WRITES_ENABLED=false` remains default, enabled write-alpha remains `APP_ENV=test` gated, owner DELETE remains blocked/not run/no packet, no original/private/only-copy mutation was run or authorized, no release/tag/package/image/production deployment was created, and no production/security/public-internet/broad-compatibility or real/private-book write-safety claim was added.

## Phase 331 — PATCH readiness analyst gate

Status: complete. Analyst found Cycle 2 ready for PM PATCH authorization: the existing Cycle 1 write-alpha-created test transaction was verifiable as present and write-alpha-owned, with metadata/memo-only scope and no original/only-copy target.

Artifacts:

- `docs/audits/phase-331-patch-readiness.md`
- `docs/handoff/phase-331.md`

## Phase 332 — PM PATCH authorization gate

Status: complete. PM authorized exactly one metadata/memo-only copied-book PATCH on the verified write-alpha-owned test transaction. DELETE and release remained out of scope.

Artifacts:

- `docs/write-alpha/phase-332-patch-authorization.md`
- `docs/handoff/phase-332.md`

## Phase 333 — Execute exactly one copied-book PATCH

Status: complete. Exactly one PATCH attempt was made and succeeded. The mutation was metadata/memo-only, amount/account/currency/split-count fingerprints stayed unchanged, and read-back/audit/backup/default-disabled reset evidence passed.

Artifacts:

- `docs/dogfood/phase-333-copied-book-patch-one.md`
- `docs/handoff/phase-333.md`

## Phase 334 — Post-PATCH compatibility and restore proof

Status: complete. Post-PATCH piecash and installed `gnucash-cli` checks passed, and restore verification from the pre-PATCH backup passed on a separate copied/restorable restore target.

Artifacts:

- `docs/dogfood/phase-334-patch-compat-restore.md`
- `docs/handoff/phase-334.md`

## Phase 335 — PATCH evidence analyst acceptance

Status: complete. Analyst accepted Cycle 2 PATCH evidence narrowly for exactly one metadata/memo-only PATCH on a write-alpha-owned copied-book test transaction.

Artifacts:

- `docs/audits/phase-335-patch-evidence-audit.md`
- `docs/handoff/phase-335.md`

## Phase 336 — Copied-book CREATE/PATCH posture update

Status: complete. Evidence matrix and copied-book posture docs now distinguish synthetic/disposable evidence, bounded owner copied-book CREATE/PATCH evidence, and DELETE blocked/not run.

Artifacts:

- `docs/write-alpha/evidence-matrix.md`
- `docs/write-alpha/copied-book-write-alpha-posture.md`
- `docs/handoff/phase-336.md`

## Phase 337 — Optional regression fix from CREATE/PATCH dogfood

Status: complete/no-op. No reproducible product bug was found during Cycle 2 dogfood, so no code or regression-test change was needed.

Artifacts:

- `docs/handoff/phase-337.md`

## Phase 338 — Cycle-2 release/no-release decision

Status: complete. PM chose NO_RELEASE because Cycle 2 produced narrow private copied-book dogfood evidence and posture docs only.

Artifacts:

- `docs/release/phase-338-release-decision.md`
- `docs/handoff/phase-338.md`

## Phase 339 — Execute Cycle-2 release/no-release

Status: complete. No tag, GitHub release, package, image, stable release, or production deployment was created.

Artifacts:

- `docs/handoff/phase-339.md`

## Phase 340 — Cycle-2 stop summary

Status: complete. Cycle 2 stops here unless the owner explicitly requests DELETE planning. DELETE was not started.

Artifacts:

- `docs/handoff/phase-340-final-summary.md`
- `docs/handoff/phase-340.md`

Safety result for Phases 331–340: exactly one PATCH attempted/performed; DELETE not run; `GNUCASH_WRITES_ENABLED=false` remains default; enabled write-alpha remains `APP_ENV=test` gated; original/read-only upload and independent upload backup were not mutated; no release/tag/package/image/production deployment was created; and no production/security/public-internet/broad-compatibility or real/private-book write-safety claim was added.

## Phase 341 — DELETE risk analyst gate

Status: complete. Analyst verdict: DELETE planning-only allowed, synthetic-only, conservative; DELETE execution remains blocked.

Artifacts:

- `docs/audits/phase-341-delete-risk-gate.md`
- `docs/handoff/phase-341.md`

## Phase 342 — PM DELETE planning decision

Status: complete. PM approved DELETE planning only and explicitly did not authorize DELETE execution.

Artifacts:

- `docs/write-alpha/phase-342-delete-planning-decision.md`
- `docs/handoff/phase-342.md`

## Phase 343 — DELETE plan and abort criteria

Status: complete. Conservative DELETE copied-book plan recorded with target limits, backups, restore/read-back requirements, evidence redaction, and abort criteria.

Artifacts:

- `docs/write-alpha/delete-copied-book-plan.md`
- `docs/handoff/phase-343.md`

## Phase 344 — DELETE dry-run capability review

Status: complete. Existing mutation-capable DELETE route was rejected for planning dry-run; PM approved implementing a narrow non-mutating helper.

Artifacts:

- `docs/handoff/phase-344.md`

## Phase 345 — Optional DELETE dry-run helper implementation

Status: complete. Added `scripts/write_alpha_delete_dry_run.py` and tests proving no book/app DB mutation, no delete-route call, and stable audit row count.

Artifacts:

- `scripts/write_alpha_delete_dry_run.py`
- `apps/api/tests/test_write_alpha_delete_dry_run.py`
- `docs/handoff/phase-345.md`

## Phase 346 — DELETE dry-run synthetic rehearsal

Status: complete. Non-mutating DELETE dry-run passed on synthetic/disposable fixtures only; no owner copied book was used.

Artifacts:

- `docs/dogfood/phase-346-delete-dry-run-synthetic.md`
- `docs/handoff/phase-346.md`

## Phase 347 — DELETE planning analyst verdict

Status: complete. DELETE remains blocked and not recommended now; future consideration requires fresh owner DELETE execution authorization and PM approval.

Artifacts:

- `docs/audits/phase-347-delete-planning-verdict.md`
- `docs/handoff/phase-347.md`

## Phase 348 — Final write-alpha practical posture

Status: complete. Owner-facing practical posture summary recorded.

Artifacts:

- `docs/write-alpha/practical-posture-summary.md`
- `docs/handoff/phase-348.md`

## Phase 349 — Future release/no-release decision

Status: complete. PM decision: `NO_RELEASE`; Cycle 3 planning/helper work should not be published as a new release.

Artifacts:

- `docs/release/phase-349-release-decision.md`
- `docs/handoff/phase-349.md`

## Phase 350 — Execute final decision and stop

Status: complete. No-release decision executed; no tag, release, package, image, stable release, or production deployment was created. Cycle 3 stops here.

Artifacts:

- `docs/release/phase-350-no-release-verdict.md`
- `docs/handoff/phase-350.md`

Safety result for Phases 341–350: DELETE planning only; no DELETE execution; helper/dry-run synthetic-only and non-mutating; `GNUCASH_WRITES_ENABLED=false` remains default; enabled write-alpha remains `APP_ENV=test` gated; original/read-only upload and independent upload backup were not mutated; no release/tag/package/image/production deployment was created; and no production/security/public-internet/broad-compatibility or real/private-book write-safety claim was added.


## Standing constraints

- MVP v0.1 is strictly read-only for GnuCash.
- `GNUCASH_WRITES_ENABLED=false` by default.
- Do not commit real financial data, GnuCash books, backups, `.env`, credentials, tokens,
  certificates, or private keys.
- Money values must use string/Decimal representation, not floats.
- Auth tokens must stay in httpOnly cookies, not localStorage/sessionStorage.
- Frontend never reads GnuCash files/databases directly.
- `piecash` stays inside backend service layers.
- App metadata stays separate from GnuCash books.
- Do not add banking integrations, CSV/OFX import, heavy UI libraries, or collaborative editing in
  MVP.
- Do not fake currency conversion.
- Keep docs honest: pre-alpha, test copies first, no production guarantee.

## Standard checks

Backend:

```bash
cd apps/api && pytest -q
```

Frontend:

```bash
cd apps/web && npm run check && npm run test:auth-routes && npm run build
```

Docker config:

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
```

## Phase 351-380 completion summary

Completed through Phase 430 on the phase-351-380 background roadmap branch. Phase 354 executed a copied-book CREATE-to-DELETE chain on an owner-provided copied/restorable book outside git: exactly one CREATE and exactly one DELETE of that same write-alpha-owned disposable transaction; backup/read-back/audit/ownership/restore/compatibility/reset evidence passed. Phase 363 executed the PM-authorized small batch: exactly two CREATE operations and exactly one metadata/memo-only PATCH, zero DELETE; backup/read-back/audit/ownership/restore/compatibility/reset evidence passed. Phases 359, 369, and 379 PM decisions were NO_RELEASE; Phase 380 executed final no-release and stopped. No original/private/only-copy book, raw evidence, backup, app DB, GnuCash book, private paths/account names/memos/amounts, .env, secrets, tag, GitHub release, package, image, stable-release publication, production deployment, default write enablement, or APP_ENV=test weakening was committed.
