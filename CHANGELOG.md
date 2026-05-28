# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]
- Phase 430 / Phases 381–430 — completed the post-PR #40 50-phase run. PR #40 was merged, public docs were reconciled, Cycle 1/2/3/4/final PM decisions were `NO_RELEASE`, and one bounded copied-book session was accepted narrowly: exactly 2 CREATE, exactly 1 metadata/memo-only PATCH, 0 DELETE on a copied/restorable SQL working book outside git. No tag, GitHub release, package, image, stable-release publication, production deployment, original/private/only-copy mutation, default write enablement, `APP_ENV=test` weakening, or broad safety claim was added.

- Phase 385 / PR #40 / Phase 380 baseline — merged Phase 351–380 write-alpha evidence into `main` after analyst file-safety review, PM `MERGE_PR40` decision, clean mergeability, passing CI, public-status guard, diff hygiene, and sensitive-file checks. Phase 354 evidence remains exactly one copied-book CREATE followed by exactly one DELETE of the same write-alpha-owned disposable transaction; Phase 363 evidence remains exactly two CREATE operations plus exactly one metadata/memo-only PATCH, zero DELETE. Current public releases remain `v0.1.7-readonly` and `v0.2.8-writealpha`; no new release/tag/package/image/stable-release publication/production deployment, original/private/only-copy safety claim, default write enablement, or `APP_ENV=test` weakening was added.

- Phase 353 / Phases 351–353 — reviewed copied-book DELETE readiness and PM authorized exactly one DELETE only if a concrete write-alpha-owned target passed preflight, then stopped before mutation because the session provided only the copied GnuCash book and no matching app metadata DB with a `write_alpha_transaction_ownership` marker. Without same-runtime app metadata, no transaction can be proven write-alpha-created/test-owned; no DELETE/CREATE/PATCH was attempted, no backup/audit/runtime artifact was created in repo, `GNUCASH_WRITES_ENABLED=false` remains default, enabled write-alpha remains `APP_ENV=test` gated, and no original/private/only-copy, broad compatibility, or broad write-safety claim was added.

- Phase 330 / Phases 321–330 — completed Cycle 1 copied-book write-alpha dogfood with an owner-provided copied/restorable working book outside git. Analyst/intake/preflight/read-only smoke passed; PM authorized exactly one CREATE; exactly one CREATE was attempted/performed; backup, read-back, audit, ownership marker, lock release, compatibility, restore, redaction, and reset/default-disabled evidence passed; CREATE evidence was accepted narrowly; PM chose `NO_RELEASE`; no tag, GitHub release, package, image, stable release, production deployment, PATCH, DELETE, original/private/only-copy mutation, or broad write-safety claim was added.

- Phase 320 / Phases 307–320 — verified Phase 306 docs-only hardening, reconciled public status, recorded Cycle 2 and Cycle 3 no-release/no-publication decisions, added the owner-feedback gate and owner status digest, entered maintenance/wait mode for active write-alpha phase work, triaged open issues without noisy comments, and recorded the final next owner action. The current public experimental write-alpha pre-release remains unchanged; `GNUCASH_WRITES_ENABLED=false` remains default; enabled write-alpha remains `APP_ENV=test` gated; owner DELETE remains blocked/not run/no packet; no tag, release, package, image, production deployment, original/private/only-copy mutation, or broad write-safety claim was added.

- Phase 305 — completed the Cycle 2 analyst gate and selected write-alpha maintenance hardening.
  Phase 306 is constrained to one narrow non-mutating maintenance-hardening outcome around existing
  safety/runbook/test boundaries; owner DELETE execution/packets, new owner mutations, release preparation,
  default write changes, and `APP_ENV=test` gate weakening remain out of scope.

- Phase 304 — closed Cycle 1 without blockers and selected the next-cycle direction.
  PM chose continued owner copied-book hardening through narrow write-alpha maintenance hardening, with no
  owner DELETE execution, DELETE request packet, new owner mutation request, release preparation, default
  write change, or `APP_ENV=test` gate weakening.

- Phase 303 — added `docs/write-alpha/owner-next-steps.md` as the short owner-facing posture guide.
  It consolidates read-only as the practical path, dry-run-only evidence, narrow CREATE-one and
  CREATE-to-PATCH evidence, DELETE blocked/not run/no packet, original/only-copy prohibitions, and
  unchanged default/gate requirements.

- Phase 302 — kept owner copied-book DELETE blocked after an analyst readiness gate.
  Existing owner evidence supports dry-run, one CREATE-one, and one fresh CREATE-to-PATCH chain only;
  DELETE has no owner copied-book evidence, remains destructive, and no owner DELETE request packet was
  prepared. No DELETE execution, release, default write change, or broad write-safety claim was added.

- Phase 301 — completed the post-Cycle-1 default-read-only Docker/Caddy regression.
  API and browser dogfood passed on the committed synthetic fixture with `GNUCASH_WRITES_ENABLED=false`:
  login, dashboard, accounts, transactions, CSV export, reports, scheduled transactions, and write-alpha
  audit summary remained healthy; disabled validate/create/PATCH/DELETE probes returned 403; write UI stayed
  hidden; the auth cookie was not visible to browser JavaScript; and no runtime/private artifacts were committed.

- Phase 300 — executed the `v0.2.9-writealpha` publication step as no-publication.
  Local/remote tag and GitHub release checks confirmed `v0.2.9-writealpha` is absent; the existing public
  experimental write-alpha pre-release remains current. No release, tag, package, image, stable release, or
  production deployment was created.

- Phase 299 — completed the final `v0.2.9-writealpha` no-release gate.
  Backend, frontend, Docker config, public-status, diff hygiene, sensitive tracked-file scan, and latest
  GitHub Actions checks passed. Gate decision remained no release; no tag, release, package, image,
  stable release, or production deployment was created.

- Phase 298 — updated the current `v0.2.9-writealpha` no-release support document.
  The verdict explains why Phase 294/295 copied-book CREATE-to-PATCH evidence should not be published as
  a new release and confirms no release-candidate artifacts, tag, GitHub release, package, image, or
  stable release were created.

- Phase 297 — recorded the `v0.2.9-writealpha` release value decision: no release.
  PM decided the accepted CREATE-to-PATCH evidence is narrow copied-book evidence, not a user-facing
  runtime capability or broad safety correction, and publishing could overstate write safety. No tag,
  GitHub release, package, image, or stable release was published.

- Phase 296 — reconciled the copied-book write-alpha evidence matrix and posture.
  Public/status docs now distinguish synthetic/disposable evidence, maintainer copied-test-book/package
  rehearsal, owner dry-run, owner CREATE-one, synthetic PATCH, superseded/absent owner PATCH-one,
  accepted Phase 294/295 CREATE-to-PATCH fresh-chain evidence, and owner DELETE blocked/not run.
  Defaults/gates remain unchanged, no release was published, and no broad write-safety claim was added.

- Phase 295 — audited and narrowly accepted the Phase 294 owner copied-book CREATE-to-PATCH evidence.
  The accepted scope is exactly one CREATE plus exactly one metadata/memo-only PATCH on the same Phase 294
  write-alpha-created transaction in one copied/restorable working book outside git. DELETE remains not
  run/blocked; `GNUCASH_WRITES_ENABLED=false` remains default; enabled write-alpha remains `APP_ENV=test`
  gated; no release was published; and no production/security/public-internet/broad-compatibility or real/
  private/original/only-copy write-safety claim was added.

- Phase 294 — accepted one bounded owner copied-book CREATE-to-PATCH chain after exact confirmation.
  Exactly one CREATE was attempted/performed on a fresh copied/restorable working book outside git, followed
  by exactly one metadata/memo-only PATCH on that same write-alpha-created transaction. Backups before each
  mutation, read-back, audit/lock evidence, readable backup artifact checks, piecash plus `gnucash-cli`
  compatibility, restore verification, default-disabled reset, disabled validate/create/PATCH/DELETE probes,
  and redaction validation passed. DELETE was not run; private artifacts stayed outside git; defaults/gates
  remain unchanged; no release was published; and no production/security/public-internet/broad-compatibility
  or real/private/original/only-copy write-safety claim was added.

- Phase 293 — blocked the new owner CREATE-to-PATCH chain before mutation pending exact confirmation.
  The owner selected the fresh-chain direction after Phase 292, but the existing exact confirmations cannot
  be reused: the Phase 275 CREATE-one authorization was already consumed in Phase 276, and the Phase 285
  PATCH-one authorization targeted the Phase 276-created transaction that Phase 292 could not verify.
  Added `docs/write-alpha/owner-create-patch-chain-request.md` with the exact same-context block required
  before any new CREATE-to-PATCH chain. No CREATE/PATCH/DELETE was attempted, no private artifact was
  committed, defaults/gates remain unchanged, and no release was published.

- Phase 292 — blocked owner PATCH-one before mutation.
  Exact Phase 285 owner confirmation was present, and preflight against the outside-git copied target
  passed, but the required target transaction could not be verified: the app metadata ownership marker
  still references the accepted CREATE-one transaction while that transaction is absent from the current
  copied working book after prior restore/reset. No PATCH was attempted or performed, DELETE was not run,
  no release was published, and owner PATCH remains blocked until a copied/restorable working book that
  still contains the Phase 276 write-alpha-created transaction is provided/selected.

- Phase 291 — completed stop/continue decision.
  PM was invoked for owner dogfood/write-mode strategy. Active write-alpha progression is frozen until
  the owner provides redacted Phase 285 PATCH-one evidence or explicitly chooses read-only maintenance.
  No release was published and no new writes were authorized.

- Phase 290 — added practical-use verdict.
  The verdict states read-only use is the practical path; synthetic/disposable write-alpha remains
  development-only; owner dry-run and exactly one owner CREATE are accepted; owner PATCH evidence is
  absent; DELETE is blocked; original/only-copy writes are forbidden.

- Phase 289 — completed v0.2.x release candidate decision: no release.
  PM was invoked for write-alpha publication risk. No tag, GitHub release, package, or release notes
  were published because owner PATCH evidence is absent and DELETE remains blocked.

- Phase 288 — refreshed the write-alpha evidence matrix.
  Added a concise matrix separating synthetic/disposable evidence, copied-test-book/package rehearsal,
  owner dry-run, owner CREATE-one, synthetic PATCH-one, owner PATCH absence, and DELETE-blocked status
  without private details or overclaiming.

- Phase 287 — completed DELETE block decision.
  PM was invoked for destructive mutation risk review and decided DELETE remains blocked for owner
  copied-book dogfood. No DELETE was executed, no owner DELETE packet was prepared, and any future
  consideration would require a separate roadmap gate and explicit owner/PM authorization.

- Phase 286 — completed owner PATCH evidence intake with evidence absent.
  No exact owner PATCH confirmation block was provided after Phase 285, and no owner copied-book PATCH
  was run. Owner PATCH evidence is therefore not accepted and cannot support DELETE progression or release
  claims. Continue only to conservative documentation/decision closeout.

- Phase 285 — prepared `docs/write-alpha/owner-patch-one-request.md`.
  The packet requires an exact owner confirmation block before any owner PATCH execution, limits scope to
  one metadata/memo-only PATCH on the write-alpha-created test transaction in a copied/restorable working
  book, requests only redacted checklist evidence, and keeps amount/account/currency/split-count edits and
  DELETE forbidden. No owner PATCH was run.

- Phase 284 — invoked PM for the owner PATCH authorization gate.
  Verdict: authorized to prepare an owner PATCH-one request packet only, based on accepted dry-run,
  exactly one accepted owner CREATE, clean CREATE findings, a metadata/memo-only plan, and a passing
  synthetic PATCH rehearsal. No owner PATCH execution, DELETE, release, default write change, gate
  weakening, amount/account edits, or broad write-safety claim was authorized.

- Phase 283 — rehearsed PATCH-one on synthetic/disposable data only.
  A local Docker/Caddy write-alpha runtime created one write-alpha-owned synthetic transaction and PATCHed
  exactly that target once with metadata/memo-only markers; API/runtime read-back passed, amount/account
  fingerprint stayed unchanged, backup/audit/compatibility/restore/default-disabled reset evidence passed,
  and targeted backend PATCH route tests passed. No owner/private/original/only-copy book was used, owner
  PATCH remains not run and not authorized, DELETE remains blocked, and no release/default/gate/safety
  overclaim was added.

- Phase 282 — prepared `docs/write-alpha/patch-one-copied-book-plan.md` without mutation.
  The plan permits only a later separately authorized one-PATCH metadata/memo update on a same-book
  write-alpha-owned test transaction in a copied/restorable working copy, with backup/read-back/
  compatibility/restore/reset/redaction evidence. Amount/account/currency/split-count edits, owner
  PATCH execution, DELETE, release, default write changes, `APP_ENV=test` gate weakening, and real/
  private/original/only-copy write-safety claims remain excluded.

- Phase 281 — completed the PATCH readiness analyst gate.
  Verdict: ready to prepare a no-mutation PATCH-one copied-book plan only. The accepted owner
  copied-book CREATE-one evidence satisfies the precondition for PATCH planning, and no CREATE
  bug or safety finding blocks planning. This does not authorize PATCH execution, owner PATCH
  request, DELETE work, release, default write change, `APP_ENV=test` gate weakening, amount/account
  edits, or any real/private/original/only-copy write-safety claim.


- Phase 280 — closed Cycle 2 and recommended one next action: start Phase 281 analyst PATCH-readiness
  review only. The CREATE-one evidence precondition for considering PATCH readiness is satisfied, but
  no PATCH execution, owner PATCH request packet, DELETE work, release, default write change,
  `APP_ENV=test` gate weakening, or broad safety claim was authorized. Owner PATCH/DELETE remain not
  run and unauthorized, and original/only-copy books remain forbidden.

- Phase 279 — invoked PM for the Cycle 2 release/no-release decision and recorded a no-release verdict.
  No `v0.2.9-writealpha` or `v0.2.10-writealpha` tag/GitHub release/package/image was published: the
  current changes are narrow evidence/posture progress rather than product behavior change, and an
  immediate release could overstate one copied-book CREATE evidence run. PATCH/DELETE remain not run
  and unauthorized, `GNUCASH_WRITES_ENABLED=false` remains default, `APP_ENV=test` gating remains
  intact, and no production/security/public-internet/broad-compatibility or real/private/original/
  only-copy write-safety claim was added.

- Phase 278 — refreshed the copied-book write-alpha posture.
  Public/status docs and `docs/write-alpha/copied-book-write-alpha-posture.md` now state that owner
  copied-book dry-run evidence is accepted as dry-run-only evidence, exactly one owner copied-book
  CREATE evidence run is accepted for one copied/restorable working copy outside git, and owner PATCH/
  DELETE remain not run and unauthorized. `GNUCASH_WRITES_ENABLED=false` remains default, `APP_ENV=test`
  gating remains intact, and no production/security/public-internet/broad-compatibility or real/private/
  original/only-copy write-safety claim was added.

- Phase 277 — reviewed the accepted owner copied-book CREATE-one evidence for concrete findings or bugs.
  No CREATE-one bug, failed check, restore mismatch, backup/audit mismatch, redaction concern,
  write-gate regression, or compatibility finding was identified, so no code change or regression test
  was needed. Owner dry-run remains accepted, exactly one owner copied-book CREATE evidence remains
  accepted, PATCH/DELETE remain not run and unauthorized, `GNUCASH_WRITES_ENABLED=false` remains default,
  `APP_ENV=test` gating remains intact, and no production/security/public-internet/broad-compatibility
  or real/private/only-copy write-safety claim was added.

- Phase 276 — accepted one owner copied-book CREATE-one evidence run after the exact Phase 275
  confirmation block was provided in the execution context. Exactly one CREATE was attempted and
  performed on a copied/restorable working copy outside git under `APP_ENV=test` with explicit temporary
  writes enabled; a pre-mutation backup was created, read-back passed, audit evidence showed one
  successful create, lock evidence was released/stale-safe, compatibility passed with piecash and
  installed `gnucash-cli`, restore verification from the pre-mutation backup passed, and reset/default-
  disabled probes returned 403 for validate/create/PATCH/DELETE. No PATCH/DELETE was run, no private
  artifact was committed, `GNUCASH_WRITES_ENABLED=false` remains default, `APP_ENV=test` gating remains
  intact, and no production/security/public-internet/broad-compatibility or real/private/only-copy
  write-safety claim was added.

- Phase 275 — rechecked the Phase 274 compatibility blocker and prepared the owner CREATE-one request packet.
  PM was invoked because this changed an owner-risk write authorization decision. Host `gnucash-cli`
  is now available as GnuCash 5.14, and a synthetic/disposable compatibility recheck passed with
  piecash and Desktop/CLI status `pass` while keeping `broad_compatibility_claimed=false`. The owner
  CREATE-one request packet is prepared, but no owner CREATE/PATCH/DELETE was run; CREATE execution
  still requires explicit owner confirmation in the execution context, PATCH/DELETE remain blocked,
  `GNUCASH_WRITES_ENABLED=false` remains default, `APP_ENV=test` gating remains intact, and no
  production/security/public-internet/broad-compatibility or real/private/only-copy write-safety claim
  was added.

- Phase 274 — completed the PM/analyst CREATE-one authorization gate with a conservative no-owner-mutation decision.
  PM was invoked because this was an owner-risk write authorization gate. Owner copied-book dry-run
  evidence is accepted and the synthetic CREATE-one rehearsal passed, but host Desktop/CLI compatibility
  remains blocked because `gnucash-cli` is unavailable, so owner copied-book CREATE is not authorized to
  request or run. Phase 275 was not started. No release/tag, owner/private/original/only-copy mutation,
  default write change, `APP_ENV=test` gate weakening, private artifact commit, or real/private/
  only-copy write-safety claim was added.

- Phase 273 — rehearsed CREATE-one on synthetic/disposable fixtures only.
  The wrapper create-one path, routed CREATE smoke, backup/audit/lock/read-back evidence, restore
  verification with read-only API probe, redaction checks, and default-disabled reset passed. The
  compatibility harness recorded piecash read-back pass but host Desktop/CLI blocked because
  `gnucash-cli` is unavailable, with no broad compatibility claim. No owner/private/original/only-copy
  book was used, no owner mutation was run, and CREATE/PATCH/DELETE owner mutations remain
  unauthorized.

- Phase 272 — prepared the CREATE-one copied-book readiness plan without mutation.
  The plan permits only a future one-minimal-two-split CREATE on an outside-git copied/restorable book
  after a later authorization gate and explicit owner request, requires backup/read-back/audit/lock/
  compatibility/restore/redaction/default-disabled evidence, and keeps PATCH/DELETE blocked. No
  product code, release/tag, owner/private/original/only-copy book mutation, default write change,
  `APP_ENV=test` gate weakening, or real/private/only-copy write-safety claim was added.

- Phase 271 — re-opened the owner copied-book dry-run evidence intake gate and accepted the newly
  provided redacted evidence as dry-run-only evidence.
  Redaction validation passed; safe evidence says dry-run passed, preflight was ready, a pre-step
  backup was created, mutation was not requested or performed, CREATE was not run, PATCH/DELETE were
  unsupported by default, redaction was validated before write, and default-disabled reset was
  verified. Private copied-book files, backups, and evidence remained outside git. CREATE-one planning
  may proceed only as no-mutation planning; owner CREATE/PATCH/DELETE remain unauthorized. No release,
  default write change, `APP_ENV=test` gate weakening, mutation, private artifact commit, or real/
  private/only-copy write-safety claim was added.

- Phase 270 — completed the Cycle 1 release/no-release decision with PM invoked.
  PM decision: no `v0.2.9-writealpha` release now because Phases 267–269 add useful synthetic
  rehearsal evidence and owner dry-run request documentation but no new product behavior and no owner
  copied-book dry-run evidence. Backend tests, frontend checks/build, Docker Compose config, public
  status guard, and diff check passed. No tag, GitHub release, package, image, production deployment,
  owner/private/original/only-copy book use, default write change, `APP_ENV=test` gate weakening,
  mutation, or real/private/only-copy write-safety claim was added.

- Phase 269 — added the owner copied-book dry-run request packet.
  `docs/write-alpha/owner-dry-run-request.md` gives the owner one dry-run-only command, local
  redaction validation, a safe redacted checklist to paste back, and stop conditions. It forbids
  original/only-copy books, raw private evidence, screenshots, CSV exports, app DBs, books, backups,
  secrets, and CREATE/PATCH/DELETE. No product code, release/tag, owner/private/original/only-copy
  book use, default write change, `APP_ENV=test` gate weakening, mutation, or real/private/only-copy
  write-safety claim was added.

- Phase 268 — passed the analyst owner dry-run readiness gate.
  The review covered the owner dry-run-only entrypoint, quickstart, redaction/evidence schema,
  troubleshooting abort guidance, Phase 267 fresh-clone rehearsal, and issue #36 evidence comments.
  Verdict: ready to ask the owner for copied-book dry-run only; CREATE/PATCH/DELETE remain blocked
  until owner redacted dry-run evidence is provided, accepted, and a separate authorization phase
  approves any narrower next step. No product code, release/tag, owner/private/original/only-copy book
  use, default write change, `APP_ENV=test` gate weakening, mutation, or real/private/only-copy
  write-safety claim was added.

- Phase 267 — rehearsed the owner copied-book dry-run path from a fresh clone with synthetic data.
  A temporary fresh checkout ran the documented dry-run-only entrypoint against an outside-git
  synthetic fixture copy, produced redacted evidence, created one pre-step backup, proved the target
  checksum was unchanged, and passed a fresh-clone default-disabled Docker/Caddy smoke where
  validate/create/PATCH/DELETE probes returned 403. No product code, release/tag, owner/private/
  original/only-copy book use, default write change, `APP_ENV=test` gate weakening, mutation, or
  real/private/only-copy write-safety claim was added.

- Phase 266 — refreshed the public docs drift guard for the current owner dry-run posture.
  README, README.ru, PROJECT_STATUS, docs/ROADMAP, `scripts/check_public_status.py`, and guard tests
  now agree that Phases 0–266 are complete, the already-published current write-alpha pre-release
  remains current, and the next owner-facing step remains copied-book dry-run only. No product code,
  release/tag, mutation, private-book use, default write change, `APP_ENV=test` gate weakening, or
  real/private/only-copy write-safety claim was added.

- Phase 265 — added owner dry-run troubleshooting and abort guidance.
  `docs/write-alpha/owner-dry-run-quickstart.md` now covers missing copied books, unsafe/original/
  only-copy paths, backup preflight failures, missing `APP_ENV=test`, unsafe write defaults,
  Docker/config/auth/health failures, redaction failures, missing no-mutation proof, and disabled-write
  endpoint success, with safe stop/review actions. It explicitly says not to proceed to CREATE unless
  dry-run is clean. No mutation, release, private-book use, default write change, gate weakening, or
  real/private/only-copy write-safety claim was added.

- Phase 264 — hardened owner dry-run evidence schema acceptance tests and nested payload redaction.
  Redaction tests now cover private path-like, amount-like, memo-like, account-name-like, and nested
  payload-like data; `scripts/redact_dogfood_evidence.py` now rejects or redacts strings/numeric
  values below sensitive container keys such as `payload`/`splits` so free-form payloads cannot bypass
  the schema. Bounded evidence fields remain usable. No mutation, release, private-book use, default
  write change, `APP_ENV=test` gate weakening, or real/private/only-copy write-safety claim was added.

- Phase 263 — added a single owner-facing copied-book dry-run-only entrypoint and quickstart.
  `scripts/write_alpha_owner_dry_run.py` has no CREATE/PATCH/DELETE mode, validates that
  `mutation_requested=false`, `mutation_performed=false`, and `create_command_status=not-run` before
  success, and writes redacted evidence only. Targeted tests and a synthetic outside-git fixture
  dry-run passed; redacted evidence was committed under `docs/dogfood/`. No owner/private/original/
  only-copy book was used, no release was published, `GNUCASH_WRITES_ENABLED=false` remains default,
  the `APP_ENV=test` gate remains intact, and no real/private/only-copy write-safety claim was added.

- Phase 262 — passed the current-state analyst gate after the current write-alpha publication. Public status docs,
  release list, open issues, recent CI, `.env.example`, rendered Docker Compose defaults, and the
  public-status guard are coherent. No safety blocker was found; `GNUCASH_WRITES_ENABLED=false`
  remains default, the enabled write-alpha posture remains `APP_ENV=test` gated, no real/private or
  only-copy write-safety claim was added, and the next owner-facing step remains copied-book dry-run
  preparation only, not CREATE-one.

## [v0.2.8-writealpha] - 2026-05-21

- Phase 261 — called PM for the Cycle 3 release/no-release gate, received `AUTHORIZE_RELEASE`, reran
  the full local release gate, checked tag/release absence, waited for exact release/status commit CI,
  and published `v0.2.8-writealpha` as a conservative GitHub pre-release. Publication created only an
  annotated git tag and GitHub pre-release; owner copied-book dogfood may still be pending, the next
  owner action remains dry-run only, `GNUCASH_WRITES_ENABLED=false` remains default, the `APP_ENV=test`
  gate remains intact, and no real/private/only-copy write-safety claim was added.

- Phase 260 — prepared unpublished `v0.2.8-writealpha` release-candidate notes, checklist, and
  final-gate draft because the Cycle 3 maintainer copied-book package is strong enough for a candidate:
  dry-run/create-one wrapper evidence, restore verification, bounded compatibility checks, synthetic
  end-to-end package rehearsal, and a conservative owner dry-run-only decision gate. No tag/release was
  published in Phase 260, owner copied-book dogfood may still be pending, CREATE-one is not the
  immediate owner ask, `GNUCASH_WRITES_ENABLED=false` remains default, the `APP_ENV=test` gate remains
  intact, and no real/private/only-copy write-safety claim was added.


- Phase 259 — completed the owner copied-book decision gate. Verdict: ready to ask the owner for a
  local copied-book dry-run only, with original untouched and private data kept outside git; not ready
  to ask for CREATE-one as the first owner action. CREATE-one can be considered only after owner
  dry-run evidence is reviewed and confirms preflight, independent backup, redaction, local-only
  runtime, restore plan, and reset to `GNUCASH_WRITES_ENABLED=false`. No owner/private/original/
  only-copy book was used or requested, no release/tag was published, and no real/private/only-copy
  write-safety claim was added.

- Phase 258 — ran the maintainer copied-book package rehearsal on synthetic/disposable fixture copies.
  The dry-run wrapper passed, Docker/Caddy create-one passed with read-back, backup/audit/lock evidence,
  restore verification passed with checksum and piecash read-back, a temporary Debian GnuCash CLI probe
  passed, and reset read-only API smoke verified validate/create/PATCH/DELETE all return 403 when
  `GNUCASH_WRITES_ENABLED=false`. Host `gnucash-cli` remained unavailable for the compatibility
  harness and is recorded as blocked rather than compatibility evidence. No owner/private/original/
  only-copy book, release/tag, default-write change, `APP_ENV=test` gate weakening, raw path/account/
  memo/amount evidence, broad compatibility claim, or real/private/only-copy write-safety claim was
  added.

- Phase 257 — added `scripts/write_alpha_restore_verify.py`, a local-only restore verification
  harness for copied/disposable write-alpha dogfood. It restores only an outside-git copied working
  book from an outside-git pre-mutation backup, verifies checksum/read-back state, supports an
  optional read-only web/API probe, writes redacted JSON evidence, and checks the committed/default
  `GNUCASH_WRITES_ENABLED=false` posture. This is not production disaster-recovery evidence and adds
  no mutation expansion, release/tag, default-write change, `APP_ENV=test` gate weakening, raw path/
  account/memo/amount evidence, or real/private/only-copy write-safety claim.

- Phase 256 — added `scripts/write_alpha_compatibility_check.py`, a local-only best-effort
  compatibility harness for post-mutation copied/disposable dogfood. It opens the target read-only
  with piecash, optionally runs already-available `gnucash-cli` report probing, records clear
  `pass`/`blocked`/`fail` redacted JSON evidence, and explicitly keeps
  `broad_compatibility_claimed=false`. Missing Desktop/CLI tooling is recorded as a blocker, not as
  compatibility evidence. No tool installation, mutation, release/tag, write-default change,
  `APP_ENV=test` gate weakening, raw path/account/memo/amount evidence, broad Desktop/version claim,
  or real/private/only-copy write-safety claim was added.

- Phase 255 — strengthened transaction create/write-alpha UI warnings for future maintainer
  copied-book create-only dogfood. English/Russian release-critical copy now says the write form is
  only for outside-git copied/restorable test books with originals untouched, at most one CREATE test
  transaction after dry-run, independent backup plus restore plan, audit/app-backup/lock evidence,
  and no production use. Backend write gates remain authoritative; no new write capability, default
  write change, `APP_ENV=test` gate weakening, mutation run, or real/private/only-copy write-safety
  claim was added.

- Phase 254 — added `scripts/write_alpha_copied_book_dogfood.py`, a local-only explicit-step wrapper
  for future copied-book dogfood. It supports separate `--dry-run` and `--create-one` modes, requires
  copied/disposable/original-untouched/outside-git confirmations plus an extra mutation confirmation
  for `--create-one`, calls redacted preflight, creates a pre-step backup, writes redacted JSON
  evidence, rejects unsafe paths, and verifies the committed/default `GNUCASH_WRITES_ENABLED=false`
  posture after each run. No DELETE mode, default-write change, `APP_ENV=test` gate weakening,
  real/private-book use, or real/private/only-copy write-safety claim was added.

- Phase 253 — added `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`, a complete
  owner/maintainer packet for future copied-book dogfood. It defaults to dry-run first, forbids
  original and only-copy books, requires outside-git copied/restorable targets with independent
  backups, limits optional mutation to one CREATE first, defers PATCH to later explicit review,
  prohibits DELETE unless separately authorized for a write-alpha-created test transaction, requires
  redacted evidence and restore proof, and ends with cleanup plus reset to `GNUCASH_WRITES_ENABLED=false`.
  No dogfood run, mutation, release/tag, default-write change, `APP_ENV=test` gate weakening,
  private-book use, or real/private/only-copy write-safety claim was added.

## [v0.2.7-writealpha] - 2026-05-21

- Phase 251 — called PM for the Cycle 2 release/no-release gate, received `AUTHORIZE_RELEASE`, reran
  the final local release gate, waited for exact release/status commit CI, and published
  `v0.2.7-writealpha` as a conservative GitHub pre-release. Publication created only an annotated
  tag and GitHub pre-release; no package, image, production deployment, write default change,
  `APP_ENV=test` gate weakening, production/security/public-internet/broad-compatibility claim, or
  real/private/only-copy write-safety claim was added.

- Phase 250 — prepared `v0.2.7-writealpha` release-candidate notes, checklist, and final-gate draft
  because Cycle 2 produced meaningful ownership-boundary safety work: app metadata-only ownership
  markers, backend PATCH/DELETE ownership guards, aligned frontend controls, synthetic/disposable
  ownership route-family dogfood, safe audit-summary ownership counters, and synchronized operator
  warnings. The candidate is not published; Phase 251 must call PM and rerun the release gate before
  any tag/GitHub release. No write default change, `APP_ENV=test` gate weakening,
  production/security/public-internet/broad-compatibility claim, real/private-book use, or
  real/private/only-copy write-safety claim was added.

- Phase 249 — documented the write-alpha ownership boundary across operator docs. The docs now state
  that CREATE creates write-alpha-owned transactions, PATCH/DELETE are limited to those
  write-alpha-owned transactions for the same app metadata book, and historical/imported/manual
  GnuCash transactions remain read-only in this app. The warnings also repeat that ownership guards
  do not make real/private, original, production, shared, or only-copy books safe for write-alpha.
  No release, product-code change, write default change, `APP_ENV=test` gate weakening, or
  production/safety overclaim was added.

- Phase 248 — extended the read-only write-alpha audit summary endpoint/UI with safe ownership
  evidence: app-metadata write-alpha-created marker count, non-owned mutation rejection count from
  redacted audit rows, and last successful mutation type. The UI renders only bounded counters and
  action labels alongside existing safe transaction ID prefixes/backup refs; raw audit payloads,
  amounts, memos, account names, and paths remain hidden. Viewer/outsider access stays blocked, and
  no write default, `APP_ENV=test` gate, real/private-book use, or release/tag was added.

- Phase 247 — ran synthetic/disposable Docker/Caddy ownership route-family dogfood after the new
  backend ownership guards. One write-alpha-owned synthetic transaction was created, PATCHed, and
  DELETEd; separate PATCH/DELETE attempts against one non-owned fixture transaction returned 403
  without backup growth. Backup/audit/lock/restore evidence was recorded only as redacted
  counts/statuses, the stack was reset to `GNUCASH_WRITES_ENABLED=false`, disabled
  validate/create/PATCH/DELETE probes returned 403, and no real/private/only-copy write-safety claim
  was added.

- Phase 246 — aligned the transaction detail UI with the backend write-alpha ownership boundary. The
  detail API now exposes a safe app-metadata-only `is_write_alpha_owned` hint; the Svelte detail page
  shows experimental delete controls only when write mode is explicitly enabled, an active book is
  present, and the transaction is write-alpha-owned. Non-owned historical/manual transactions show
  explanatory read-only copy instead of edit/delete controls. Backend PATCH/DELETE ownership guards
  remain authoritative, `GNUCASH_WRITES_ENABLED=false` remains default, the `APP_ENV=test` gate is
  unchanged, and no real/private/only-copy write-safety claim was added.

- Phase 245 — added the backend write-alpha DELETE ownership guard. Enabled DELETE now checks the app
  metadata `write_alpha_transaction_ownership` row for the same book and transaction before
  constructing the GnuCash write service; non-owned historical/imported/manual transactions return
  403 without backup, lock, audit row, or GnuCash mutation. Write-alpha-created synthetic
  transactions still pass the existing lock/backup/delete/audit flow and successful allowed DELETE
  refreshes `last_mutated_at`. Viewer/outsider access and default-disabled writes remain blocked
  before ownership checks. No broad delete support, undo feature, release, write default change,
  `APP_ENV=test` gate weakening, real/private-book use, or real/private/only-copy write-safety claim
  was added.

- Phase 244 — added the backend write-alpha PATCH ownership guard. Enabled PATCH now checks the app
  metadata `write_alpha_transaction_ownership` row for the same book and transaction before
  constructing the GnuCash write service; non-owned historical/imported/manual transactions return
  403 without backup, lock, audit row, or GnuCash mutation. Write-alpha-created synthetic
  transactions still pass the existing description/date/split-memo-only PATCH path and refresh
  `last_mutated_at`. Viewer/outsider access and default-disabled writes remain blocked before
  ownership checks. No amount/account mutation expansion, DELETE ownership guard, release, write
  default change, `APP_ENV=test` gate weakening, real/private-book use, or real/private/only-copy
  write-safety claim was added.

- Phase 243 — added an app metadata-only write-alpha transaction ownership marker for successful
  CREATE requests. The model links `book_id`, `transaction_id`, `created_by_user_id`,
  `created_by_write_alpha`, `created_at`, and `last_mutated_at` so later PATCH/DELETE phases can
  reject historical/manual transactions. The CREATE path now records ownership after successful
  synthetic/disposable write-alpha creates, with tests and operator documentation. No write default,
  `APP_ENV=test` gate, amount/account mutation scope, release, GnuCash-book metadata write, or
  real/private/only-copy write-safety claim was added.

## [v0.2.6-writealpha] - 2026-05-21

- Phase 241 — called PM for the Cycle 1 release/no-release gate, received `AUTHORIZE_RELEASE`, reran
  the final local release gate, waited for exact release/status commit CI, and published
  `v0.2.6-writealpha` as a conservative GitHub pre-release. Publication created only an annotated
  tag and GitHub pre-release; no package, image, production deployment, write default change,
  `APP_ENV=test` gate weakening, production/security/public-internet/broad-compatibility claim, or
  real/private/only-copy write-safety claim was added.

- Phase 240 — prepared release-candidate notes, checklist, and final-gate draft for the write-alpha
  maintenance candidate because Phases 232–239 added meaningful operator-safety tooling and evidence:
  copied-book runbook, redacted preflight, evidence redaction schema/helper, environment guidance,
  readiness inspection, and synthetic no-mutation Docker/Caddy dry-run. The candidate was not tagged
  or published in Phase 240; publication required the later PM/release gate completed in Phase 241.
  `GNUCASH_WRITES_ENABLED=false` remains default, `APP_ENV=test` gating remains intact, and no
  production/security/public-internet/broad-compatibility or real/private/only-copy write-safety
  claim was added.

- Phase 239 — ran a synthetic copied-book dry-run through Docker/Caddy using a disposable fixture
  copy and the Phase 236 evidence schema. Preflight/readiness reported redacted no-mutation status,
  Docker/Caddy read-only API and browser smoke passed with `GNUCASH_WRITES_ENABLED=false`, disabled
  validate/create/PATCH/DELETE probes returned 403, checksum evidence confirmed no runtime book
  mutation, and no backups/locks/audit rows were produced. No create/PATCH/DELETE write-alpha
  mutation, release, default-write change, `APP_ENV=test` gate weakening, real/private book use, or
  raw path/account/memo/amount evidence was added.

- Phase 238 — added `scripts/write_alpha_readiness.py` and backend readiness helper coverage for a
  non-mutating, redacted write-alpha operator preflight. The command reports whether
  `GNUCASH_WRITES_ENABLED=true`, the `APP_ENV=test` gate, derived backup policy, app metadata DB,
  and default book read-only open check are ready, always records `mutation_performed=false`, works
  when writes are disabled, and does not construct the write service. No write default,
  `APP_ENV=test` gate, release, real/private-book use, or raw-path output was added.

- Phase 237 — added `.env.writealpha.example` as an explicitly unsafe-for-real-books operator
  reference and `docs/write-alpha/environment.md` for local write-alpha environment guardrails. The
  docs state not to copy the template blindly to `.env`, require both `GNUCASH_WRITES_ENABLED=true`
  and `APP_ENV=test` for explicit write-alpha testing, allow only synthetic/disposable/copied-test
  books, forbid public exposure and original/only-copy books, and preserve the normal
  `.env.example`/Docker Compose `GNUCASH_WRITES_ENABLED=false` defaults. No write mode was enabled,
  no Docker default changed, and no real/private-book safety claim was added.

- Phase 236 — added `docs/write-alpha/dogfood-evidence-schema.md` plus
  `scripts/redact_dogfood_evidence.py` and targeted tests so future copied/disposable dogfood
  evidence can record phase/scenario/classification/commands/result/redacted artifact refs,
  backup/audit counts, lock/restore/default-reset statuses, while rejecting or redacting raw paths,
  amount-like values, memo/account-name fields, and payload-like values before commit. No mutation,
  copied-book dogfood, release, default write enablement, `APP_ENV=test` gate change, or
  real/private/only-copy write-safety claim was added.

- Phase 235 — added `scripts/write_alpha_preflight.py`, a local-only redacted preflight CLI for
  future copied/disposable write-alpha dogfood targets. It requires an explicit existing readable
  target outside the git working tree, validates backup destinations as outside git or git-ignored,
  blocks unsafe write-alpha environment values unless `GNUCASH_WRITES_ENABLED=true` and
  `APP_ENV=test`, warns on original/production-looking names without printing raw paths, and performs
  no book opening, copying, upload, mutation, or automatic write enablement.
  `GNUCASH_WRITES_ENABLED=false` remains the default and no real/private/only-copy write-safety claim
  was added.

- Phase 234 — added `docs/write-alpha/copied-book-dogfood-runbook.md`, a conservative maintainer
  runbook for future local-only copied/disposable write-alpha dogfood. The runbook forbids original
  and only-copy books, requires outside-git copies plus independent backups before mutation,
  explicit `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test` for a local test run, one mutation at a
  time, strict stop conditions, redacted evidence, restore verification, and reset back to
  `GNUCASH_WRITES_ENABLED=false`. No real/private copied-book dogfood, product code, UI feature,
  release, write default, `APP_ENV=test` gate change, or real/private/only-copy write-safety claim
  was added.

- Phase 233 — reformatted README, README.ru, CHANGELOG, and PROJECT_STATUS raw markdown source for
  terminal/editor readability, advancing GitHub issue #28 without product behavior changes. Long
  single-line paragraphs and packed list items were wrapped while preserving links, status content,
  safety warnings, `GNUCASH_WRITES_ENABLED=false`, the `APP_ENV=test` write-alpha gate, and the
  existing no-production/no-security/no-real-private-book-write-safety posture.

- Phase 232 — reconciled public repository status after the published `v0.2.5-writealpha`
  pre-release. README/README.ru/PROJECT_STATUS/CHANGELOG/docs/ROADMAP and the public-status guard now
  agree that Phase 232 is complete, `v0.2.5-writealpha` is the current published write-alpha
  pre-release, write-alpha evidence remains synthetic/disposable or copied-test-book only,
  `GNUCASH_WRITES_ENABLED=false` remains default, and explicit write-alpha execution still requires
  `APP_ENV=test`. Historical no-release/prepared wording remains only where it describes older phases,
  and no product code, release, tag, write-mode behavior change, or real/private/only-copy
  write-safety claim was added.

- Phase 231 — ran the final Cycle 3 release gate and published `v0.2.5-writealpha` as a conservative
  GitHub pre-release after local backend/frontend/Docker checks, public status guard, sensitive
  tracked-file hygiene, candidate tag/release absence checks, and exact release/status commit CI.
  Publication created only the annotated tag and GitHub pre-release; `GNUCASH_WRITES_ENABLED=false`
  remains default, `APP_ENV=test` write-alpha gating remains intact, and no package, image,
  production deployment, stable/security/public-internet/broad-compatibility claim, or
  real/private/only-copy write-safety claim was added.

- Phase 230 — produced the final Cycle 3 release-candidate dogfood pack for a later
  `v0.2.5-writealpha` attempt. Default-read-only Docker/Caddy API/browser dogfood passed with
  `GNUCASH_WRITES_ENABLED=false`, disabled validate/create/PATCH/DELETE probes returned 403, browser
  dogfood passed at mobile and desktop viewports, and separate explicit local `APP_ENV=test` plus
  `GNUCASH_WRITES_ENABLED=true` synthetic/disposable create/PATCH/DELETE smokes passed with matching
  backup/audit evidence and DELETE restore proof. The stack was reset to default false, cleanup left
  no runtime artifacts, and no release was published.

### Added

- Phase 229 — refreshed public status and release-doc drift guards after the Phase 222–228
  write-alpha backup/audit remediation.
  README/README.ru/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release-support docs and the public status
  guard now agree that Phase 229 is complete, `v0.1.7-readonly` remains the current read-only
  pre-release, `v0.2.4-writealpha` remains the current published write-alpha pre-release until a
  later authorized release phase, `v0.2.5-writealpha` has no tag or GitHub release,
  `GNUCASH_WRITES_ENABLED=false` remains default, and write-alpha remains experimental,
  `APP_ENV=test`/synthetic-disposable only, not production-ready, not security-audited, and not safe
  for real/private or only-copy books. No product behavior, release, tag, write default, or
  `APP_ENV=test` gate changed.

- Phase 228 — reran clean-checkout and synthetic upgrade smokes after the write-alpha backup/audit
  remediation. Current `HEAD` passed fresh-clone Docker/Caddy read-only API and mobile/desktop
  browser dogfood with `GNUCASH_WRITES_ENABLED=false`; the synthetic upgrade path from
  `v0.2.4-writealpha` runtime state to current `HEAD` preserved dummy app metadata/default
  book/selected-book recovery/read-only routes/audit-summary access, and
  validate/create/PATCH/DELETE probes returned 403 after upgrade. Temporary clones/runtime data were
  removed; no write-enabled smoke, release, tag, migration feature work, or real/private-book safety
  claim was added.

- Phase 227 — updated operator-facing release-support/troubleshooting/runbook wording for the
  resolved Phase 220 no-release blocker. The docs now describe the closure narrowly as
  synthetic/disposable backup-audit evidence remediation after Phases 222–226, keep
  `v0.2.4-writealpha` as the current published write-alpha release, and repeat that write-alpha
  remains experimental, disabled by default, `APP_ENV=test`/disposable-only, not production-ready,
  not security-audited, and not safe for real/private or only-copy books. No UI/product behavior,
  release, tag, write default, or write scope changed.

- Phase 226 — confirmed the default read-only Docker/Caddy product path after write-alpha
  backup/evidence remediation. With a committed synthetic fixture copied into ignored runtime
  storage and `GNUCASH_WRITES_ENABLED=false` rendered for API and web, API smoke passed health,
  login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports,
  scheduled metadata, write-alpha audit summary, and disabled validate/create/PATCH/DELETE probes
  returning 403; browser dogfood passed at `320x720` and `1280x900` with hidden write UI,
  auth-cookie no-readability, CSV fetch without saved raw artifact, no horizontal overflow, and
  cleanup/no-artifact checks. No write-enabled run, release, or real/private-book safety claim was
  added.
- Phase 225 — produced a fresh bounded write-alpha create/PATCH/DELETE backup-audit matrix after
  backup evidence hardening. Each route family ran once on an isolated ignored synthetic/disposable
  runtime copy with explicit local `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true`; every successful
  write had one backup file count and one successful audit row, expected
  validation/missing-transaction probes failed safely without backups, DELETE restore/read-back
  passed, locks were stale-released/not active, default-false reset passed, and runtime artifacts
  were cleaned. No write scope expansion, write default change, release, or real/private-book safety
  claim was added.
- Phase 224 — reran bounded write-alpha DELETE restore proof after backup evidence hardening. One
  explicit local `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true` DELETE succeeded against an ignored
  synthetic/disposable runtime copy; API/runtime absence, one successful audit row, one backup
  artifact, container-side restore checksum/read-back, stale-released lock evidence, default-false
  reset, disabled validate/create/PATCH/DELETE probes, and stopped-runtime cleanup all passed. No
  create/PATCH rerun, write default change, release, or real/private-book safety claim was added.
- Phase 223 — hardened backup identity/evidence after the Phase 222 collision fix. Rapid
  create/PATCH/DELETE write-alpha route-family regression coverage now freezes the backup clock and
  proves unique readable backup artifacts, audit rows preserve exact backup paths internally, and
  the read-only audit summary exposes only opaque backup refs so operators can distinguish artifacts
  without raw paths/filenames or financial data. No write endpoint, write default, `APP_ENV=test`
  gate, release, or real/private-book safety claim changed.
- Phase 222 — reconciled the Phase 220 write-alpha DELETE backup-count anomaly. Targeted
  regression/code inspection found that second-precision backup filenames could collide for rapid
  same-named synthetic runtime copies and `shutil.copy2` could silently overwrite earlier backup
  evidence. Backup creation now uses microsecond timestamps, deterministic suffix fallback, and
  exclusive-create copy so successful backup-bearing create/PATCH/DELETE audit rows cannot collapse
  into fewer artifacts. No write endpoint, write default, `APP_ENV=test` gate, release, or
  real/private-book safety claim changed.
- Phase 221 — ran the final cycle-2 release gate for candidate `v0.2.5-writealpha` and recorded an
  explicit no-release verdict. Local backend/frontend/Docker/default-write/sensitive-file checks
  passed and tag/release absence was confirmed, but Phase 220's bounded write-alpha DELETE
  backup-count anomaly remains a release blocker, so no `v0.2.5-writealpha` tag, GitHub pre-release,
  package, image, production deployment, write-default change, or real/private-book write-safety
  claim was created.
- Phase 220 — collected cycle-2 release-candidate dogfood evidence: full default-read-only
  Docker/Caddy API and mobile/desktop browser smokes passed with `GNUCASH_WRITES_ENABLED=false`,
  including scheduled metadata, write-alpha audit summary, hidden write UI, auth-cookie
  no-readability, CSV fetch, and disabled validate/create/PATCH/DELETE probes returning 403. A
  separate explicit local `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true` synthetic/disposable
  write-alpha drill passed create and PATCH but exposed a DELETE backup-count anomaly after a
  successful DELETE, so the phase records a no-release blocker instead of publishing a release.
- Phase 219 — added a glossary-backed EN/RU operator-safety/accounting wording slice for
  release-critical read-only/write-alpha terms, including a typed frontend safety glossary, static
  catalog checks for read-only default, `GNUCASH_WRITES_ENABLED=false`, disposable/test-copy
  write-alpha boundaries, not-production/not-security-audited wording, no-currency-conversion copy,
  and GnuCash Desktop authoritative-editor wording. `/books` visible copy now says metadata instead
  of broad management. No product behavior, backend API localization overhaul, write-default change,
  or release was published.
- Phase 218 — added bounded limit/offset pagination and mobile-safe operator review controls for the
  read-only write-alpha audit-summary endpoint/UI, with large synthetic app-metadata tests proving
  redacted pages, count/status summaries, owner/editor access, viewer/unauthorized blocking,
  URL-only filters, and no browser storage. No write-enabled mode or release was published.
- Phase 215 — hardened unavailable/missing/not-configured book behavior across read-only API route
  families and web recovery: data routes now return deterministic path-safe 503 before opening
  unavailable GnuCash storage, `/books` remains metadata-only with safe diagnostics, the 503 error
  page links operators back to `/books`, and local Docker/Caddy API/browser dogfood passed with a
  synthetic unavailable book and default `GNUCASH_WRITES_ENABLED=false`. No write-enabled mode or
  release was published.
- Phase 214 — added and ran a synthetic Docker upgrade smoke from `v0.2.4-writealpha` runtime state
  to current `main`, preserving dummy app metadata DB access, default book access, selected-book
  recovery, read-only accounts/transactions/reports/scheduled/audit-summary routes, and disabled
  validate/create/PATCH/DELETE probes returning 403 with `GNUCASH_WRITES_ENABLED=false`. No
  write-enabled mode or release was published.
- Phase 213 — verified the published `v0.2.4-writealpha` tag from a fresh clone with the committed
  synthetic fixture, dummy local-only secrets, Docker/Caddy, read-only API smoke, mobile and desktop
  browser dogfood, and disabled validate/create/PATCH/DELETE probes returning 403; hardened the
  smoke helper to run both browser widths. No write-enabled mode or release was published.
- Phase 212 — synchronized public status/roadmap documentation after `v0.2.4-writealpha` and added a
  public status drift guard for README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release docs. The guard
  checks the current Phase 211 release baseline, `v0.1.7-readonly`, `v0.2.4-writealpha`,
  `GNUCASH_WRITES_ENABLED=false`, and conservative no-production/no-security/no-stable-claim wording
  without reading `.env`, runtime books, app DBs, backups, or private paths. No release was
  published.

## [0.2.4-writealpha] - 2026-05-21

### Added

- Phase 211 — published `v0.2.4-writealpha` as a conservative pre-alpha write-alpha GitHub
  pre-release after the cycle-1 release gate passed, local backend/frontend/Docker checks passed,
  rendered `GNUCASH_WRITES_ENABLED=false` was confirmed, sensitive tracked-file hygiene passed, and
  GitHub Actions on the exact release/status commit completed successfully. Publication created only
  the annotated tag and GitHub pre-release.
- Phase 210 — reran bounded local write-alpha create/PATCH/DELETE+restore dogfood after cycle-1
  hardening, using fresh ignored synthetic runtime copies under explicit `APP_ENV=test` plus
  `GNUCASH_WRITES_ENABLED=true`; validation/missing-transaction failures failed safely, exactly one
  mutation per route-family copy succeeded, backup/audit/lock/read-back/restore evidence stayed
  redacted, runtime artifacts were cleaned, and the stack was reset to default false with
  validate/create/PATCH/DELETE probes returning 403.
- Phase 209 — reran full default-read-only Docker/Caddy API and browser dogfood after the cycle-1
  hardening phases, using only the committed synthetic fixture copied into ignored runtime data;
  health/login/books/accounts/transactions/details/CSV/reports/scheduled/audit-summary flows passed,
  validate/create/PATCH/DELETE probes returned 403, mobile and desktop browser dogfood passed with
  hidden write UI and no artifacts, and runtime smoke data was cleaned.
- Phase 208 — polished operator-facing EN/RU safety copy in the app shell, `/books`,
  login/health/error catalog entries, write-mode warnings, and write-alpha audit-summary UI without
  claiming full localization or changing backend behavior; static checks now guard pre-alpha,
  not-production, not-security-audited, default-disabled, disposable-only wording and no
  browser-storage persistence.
- Phase 207 — hardened the read-only write-alpha audit-summary endpoint/UI so disposable write-run
  evidence exposes only bounded counts/status/time windows and redacted rows; malicious payload
  timestamps/results/transaction IDs/error text and path-like filters fail safely, while
  viewer/outsider access remains 403.
- Phase 206 — hardened transaction and scheduled read-only edge cases with redacted scheduled
  template-reference status, no-template leakage tests, many-split Decimal/reconciliation-state
  coverage, bounded Money/split/scheduled layouts, and synthetic Docker/Caddy mobile/desktop dogfood
  confirming hidden write UI, CSV filter parity, no-overflow checks, no artifacts, and disabled
  validate/create/PATCH/DELETE probes.
- Phase 205 — polished multi-book read-only recovery and navigation for inaccessible, archived,
  missing, and stale selected-book contexts without adding
  upload/delete/default-changing/registry-edit actions or exposing private paths.
- Phase 204 — added compatibility-matrix regression coverage from redacted fixture metadata,
  classifying rows as tested synthetic evidence, blocked/manual Desktop fixture work, or unclaimed
  backend, and reorganized compatibility docs so PostgreSQL/MySQL/MariaDB, XML, broad
  Desktop-version support, production readiness, and real/private-book compatibility remain
  unclaimed.
- Phase 203 — advanced the disposable GnuCash Desktop fixture capture path with deterministic
  provenance/redaction checks and an explicit blocker when safe noninteractive Desktop-generated
  SQLite fixture creation is unavailable.
- Phase 202 — hardened default read-only first-run diagnostics for health/login/books error states,
  keeping missing/default-book, placeholder auth configuration, CORS warning, and write-disabled
  guidance path-safe and secret-free.

### Release notes

- `v0.2.4-writealpha` remains pre-alpha and experimental. `GNUCASH_WRITES_ENABLED=false` remains the
  default; write-alpha execution remains gated by explicit local enablement plus `APP_ENV=test`.
- New write-alpha evidence is synthetic/disposable only. It does not establish safe writes for
  real/private or only-copy books.
- Publication created only a GitHub pre-release and annotated git tag; no package, binary artifact,
  Docker image, production deployment, write default change, write-scope expansion, or real/private
  data artifact was published.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Write-alpha remains unsafe for real/private or only-copy books; evidence is synthetic/disposable
  only for this cycle.
- No broad GnuCash Desktop/backend compatibility, hosted SaaS readiness, collaborative accounting,
  CSV/OFX import, banking integration, or production-safe write mode is claimed.

## [0.2.3-writealpha] - 2026-05-20

### Added

- Phase 201 — published `v0.2.3-writealpha` as a conservative pre-alpha write-alpha GitHub
  pre-release after the cycle-3 release-readiness gate passed, local backend/frontend/Docker checks
  passed, rendered `GNUCASH_WRITES_ENABLED=false` was confirmed, sensitive tracked-file hygiene
  passed, and GitHub Actions on the exact release/status commit completed successfully. Publication
  created only the annotated tag and GitHub pre-release.
- Phase 200 — completed bounded cycle-3 write-alpha create/PATCH/DELETE disposable route-family
  dogfood on fresh ignored synthetic runtime copies, with backup/audit evidence, DELETE restore
  proof, stale-released/non-active lock evidence, default-disabled reset, and clean teardown.
- Phase 199 — completed full default-read-only Docker/Caddy API and browser regression dogfood at
  mobile and desktop widths, with validate/create/PATCH/DELETE probes returning 403 and no committed
  runtime artifacts.
- Phase 198 — hardened multi-book read-only registry diagnostics, role/status copy, unavailable-book
  actions, and selected-book recovery without exposing raw paths or adding registry/write
  management.
- Phase 197 — refreshed GnuCash Desktop fixture compatibility blocker evidence with disposable
  GnuCash 4.13 container tooling and redacted metadata/provenance tests, without claiming broad
  Desktop support.
- Phase 196 — added redacted first-run/read-only deployment diagnostics for
  JWT/admin/default-book/CORS/write-disabled triage through `/health` and `/login`.
- Phase 195 — hardened the read-only write-alpha audit-summary operator UX with safe
  action/result/time-window filters and bounded redacted counts/status metadata.
- Phase 194 — made write-alpha create/PATCH/DELETE smoke helpers resilient to root-owned host-side
  runtime artifacts by collecting redacted backup/audit/lock evidence inside the API container
  without rerunning mutating routes.
- Phase 193 — added stopped-runtime-only cleanup and lock recovery tooling for ignored root-owned
  runtime artifacts and stale/unreadable locks.
- Phase 192 — updated GitHub Actions JavaScript-action wiring to Node 24-compatible major versions
  to remove the known non-blocking Node.js 20 deprecation warnings seen after `v0.2.2-writealpha`;
  product behavior, Docker runtime defaults, release state, and `GNUCASH_WRITES_ENABLED=false`
  remain unchanged.

### Release notes

- `v0.2.3-writealpha` remains pre-alpha and experimental. `GNUCASH_WRITES_ENABLED=false` remains the
  default; write-alpha execution remains gated by explicit local enablement plus `APP_ENV=test`.
- New write-alpha evidence is synthetic/disposable only. It does not establish safe writes for
  real/private or only-copy books.
- Publication created only a GitHub pre-release and annotated git tag; no package, binary artifact,
  Docker image, production deployment, write default change, write-scope expansion, or real/private
  data artifact was published.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Write-alpha remains unsafe for real/private or only-copy books; evidence is synthetic/disposable
  only for this cycle.
- No broad GnuCash Desktop/backend compatibility, hosted SaaS readiness, collaborative accounting,
  CSV/OFX import, banking integration, or production-safe write mode is claimed.

## [0.2.2-writealpha] - 2026-05-20

### Added

- Phase 191 — published `v0.2.2-writealpha` as a conservative pre-alpha write-alpha GitHub
  pre-release after the cycle-2 release-readiness gate passed, local backend/frontend/Docker checks
  passed, rendered `GNUCASH_WRITES_ENABLED=false` was confirmed, sensitive tracked-file hygiene
  passed, and GitHub Actions on the exact release/status commit completed successfully. Publication
  created only the annotated tag and GitHub pre-release.
- Phase 190 — reran combined cycle-2 release-candidate dogfood: default read-only API/browser smokes
  passed with validate/create/PATCH/DELETE probes returning 403, and separate explicit local-only
  create/PATCH/DELETE write-alpha route-family evidence was collected on synthetic/disposable
  runtime copies.
- Phase 189 — ran fresh-clone Docker smokes against `v0.1.7-readonly`, `v0.2.1-writealpha`, and
  current `main`, all with synthetic fixture data, dummy local-only secrets, default
  `GNUCASH_WRITES_ENABLED=false`, disabled write probes, browser dogfood, and no-artifact teardown.
- Phase 188 — strengthened read-only reporting correctness for mixed-currency split exclusion,
  unknown `XXX` base-currency warnings, zero-balance fallback, signed contra balances,
  Decimal/string amounts, and drilldown URL parity.
- Phase 187 — hardened multi-book read-only access and selected-book recovery after write-alpha work
  while keeping write UI hidden under default false.
- Phase 186 — added a read-only, redacted write-alpha audit summary endpoint/UI for disposable
  write-alpha runs, with auth/access controls and no
  backup-path/private-path/raw-payload/memo/amount leakage.
- Phase 185 — ran bounded synthetic/disposable DELETE dogfood with restore proof, backup/audit
  evidence, default-disabled reset, and teardown.
- Phase 184 — ran bounded synthetic/disposable PATCH metadata/split-memo dogfood with read-back,
  backup/audit evidence, safe missing-transaction behavior, default-disabled reset, and teardown.
- Phase 183 — tightened write-alpha stale-lock/root-owned-lock recovery evidence: backend and
  smoke-helper lock inspection now distinguish active, stale released, unreadable, and absent lock
  states with path-safe operator messages; recovery docs and write-mode warning copy were updated
  without automatic lock deletion, write-scope expansion, default-write enablement, or
  real/private-book claims.

### Release notes

- `v0.2.2-writealpha` remains pre-alpha and experimental. `GNUCASH_WRITES_ENABLED=false` remains the
  default; write-alpha execution remains gated by explicit local enablement plus `APP_ENV=test`.
- New write-alpha evidence is synthetic/disposable only. It does not establish safe writes for
  real/private or only-copy books.
- Publication created only a GitHub pre-release and annotated git tag; no package, binary artifact,
  Docker image, production deployment, write default change, write-scope expansion, or real/private
  data artifact was published.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Write-alpha remains unsafe for real/private or only-copy books; evidence is synthetic/disposable
  only for this cycle.
- No broad GnuCash Desktop/backend compatibility, hosted SaaS readiness, collaborative accounting,
  CSV/OFX import, banking integration, or production-safe write mode is claimed.

## [0.2.1-writealpha] - 2026-05-20

### Added

- Phase 182 — published `v0.2.1-writealpha` as an authorized pre-alpha write-alpha GitHub
  pre-release after re-running the fresh gate: clean `main`, `HEAD == origin/main`, local and remote
  tag absence, GitHub release absence, green GitHub Actions on the exact release commit,
  backend/frontend/Docker checks, rendered `GNUCASH_WRITES_ENABLED=false`, and tracked
  sensitive-file hygiene. Publication created only the annotated tag and GitHub pre-release.
- Phase 181 — prepared the conservative release notes, checklist, and final gate for the candidate,
  with explicit
  pre-alpha/experimental/default-disabled/not-production/not-security-audited/no-real-private-book-write-safety
  wording.
- Phase 180 — reran combined default-read-only Docker/Caddy API/browser dogfood plus a separate
  explicit local synthetic/disposable write-alpha create smoke; default validate/create/PATCH/DELETE
  probes returned 403 and no runtime artifacts were committed.
- Phase 179 — hardened backend write-alpha lock-contention and path-like error handling without
  expanding create/PATCH/DELETE scope, keeping backup/audit evidence for post-backup failures.
- Phase 178 — improved write-alpha UX guardrails and safe frontend error handling so
  disposable/test-copy boundaries are clearer and raw path-like backend details are not rendered.
- Phase 177 — completed a disposable backup/restore drill proving the pre-write state can be
  restored and read-only-smoked again with validate/create/PATCH/DELETE probes returning 403 under
  default false.
- Phase 176 — verified the disposable write-alpha mutated book with GnuCash CLI tooling inside a
  temporary Debian container, recording only narrow bounded evidence and no broad Desktop
  compatibility claim.
- Phase 175 — ran exactly one controlled write-alpha create dogfood on a synthetic/disposable copied
  book under explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`, then verified backup,
  audit, lock release, restore, and return to default disabled writes.
- Phase 174 — implemented the redacted write-alpha copied-book preflight harness that fails closed
  for unsafe source/runtime/backup paths and emits only bounded metadata.
- Phase 173 — added the local-only copied/disposable write-alpha dogfood runbook and safe preflight
  interface without running a write or changing defaults.

### Release notes

- `v0.2.1-writealpha` remains pre-alpha and experimental. `GNUCASH_WRITES_ENABLED=false` remains the
  default; write-alpha execution remains gated by explicit local enablement plus `APP_ENV=test`.
- Write-alpha evidence is synthetic/disposable or copied-test-book evidence only. It does not
  establish safe writes for real/private or only-copy books.
- Publication created only a GitHub pre-release and annotated git tag; no package, binary artifact,
  Docker image, production deployment, write default change, write-scope expansion, or real/private
  data artifact was published.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Write-alpha remains unsafe for real/private or only-copy books; evidence is synthetic/disposable
  or copied-test-book only.
- No broad GnuCash Desktop/backend compatibility, hosted SaaS readiness, collaborative accounting,
  CSV/OFX import, banking integration, or production-safe write mode is claimed.

## [0.1.7-readonly] - 2026-05-20

### Added

- Phase 171 — published `v0.1.7-readonly` as an authorized GitHub pre-release after re-running the
  final release gate: clean `main`, `HEAD == origin/main`, local backend/frontend/Docker checks,
  rendered `GNUCASH_WRITES_ENABLED=false`, tag/release absence, sensitive tracked-file hygiene, and
  GitHub Actions for the release commit passed. Publication created only the annotated tag and
  GitHub pre-release; no package, image, production deployment, write expansion, runtime default
  change, or real/private data artifact was added.
- Phase 170 — reran the full cycle 2 synthetic/disposable Docker/Caddy read-only dogfood after
  Phases 162–169: local Compose ran with `GNUCASH_WRITES_ENABLED=false`, `/api/health` confirmed the
  default book was present/readable and writes disabled, API smoke covered health, login/auth,
  books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and
  disabled validate/create/patch/delete write probes, and headless browser dogfood passed at both
  320x720 and 1280x900 for login, protected redirect, dashboard, accounts, books, scheduled, account
  detail, transaction filters, transaction detail, CSV export, hidden write UI, no-overflow checks,
  and no raw screenshot/download/export artifacts. This is local synthetic evidence only; no
  release, copied-book dogfood, write expansion, or real/private data artifact was added.
- Phase 169 — completed a release-critical Russian localization slice for visible read-only/operator
  paths without claiming full translation: login validation/auth/service-configuration failures now
  use the English/Russian catalog from the `ui_locale` cookie, and the global error component/page
  localize 403, 404, generic API/network, and 5xx first-run guidance while preserving read-only,
  `/health`, `.env`, book-volume, and English-canonical safety wording.
- Phase 168 — improved first-run and broken-configuration operator UX: `/health` now reports
  redacted JWT/admin bootstrap diagnostics plus unreadable default-book state, startup logs emit
  safe first-run warnings without paths/secrets, `/login` gives operator-fixable guidance for auth
  configuration failures, `/books` and the global error page point operators to safe `.env`, book
  volume, and `/health` checks, and `docs/operations/troubleshooting.md` documents the read-only
  troubleshooting path.
- Phase 167 — hardened local/LAN auth/session defaults without claiming a production security audit:
  SvelteKit now rejects mismatched-Origin unsafe state-changing app requests, the web auth cookie
  lifetime follows `JWT_TOKEN_EXPIRE_MINUTES` from Compose instead of a hard-coded value, backend
  auth tests pin expired JWT rejection, and security docs describe the pre-alpha same-origin/session
  model.
- Phase 166 — hardened synchronous read-only CSV export feedback: backend regression tests now pin
  empty filtered exports and account-scoped filter/header parity, while transaction and
  account-detail export actions show localized row-count, header-only empty-export, 10,000-row
  cap/truncation, string-amount, and no-currency-conversion guidance. CSV export remains
  synchronous, read-only, URL-filtered, and capped without committing raw CSV artifacts.
- Phase 165 — added large account-tree usability/performance evidence: the synthetic benchmark
  helper can generate wide/deep synthetic account hierarchies, record account hierarchy metadata,
  and document a 146-account local TestClient read-only account-tree pass; the account tree UI now
  caps deep hierarchy indentation while preserving full-path hover text, with static checks pinning
  no-overflow/no-browser-storage behavior.
- Phase 164 — hardened read-only book-context recovery for GitHub #13: invalid, stale, or
  inaccessible selected-book cookies now produce a safe `/books` review path with a
  corrected/cleared non-secret cookie and user-facing recovery notice, while archived/unauthorized
  books remain hidden/blocked and raw `uri_or_path` values stay out of API/UI.
  `docs/book-switcher-readonly-model.md` now documents the selected-book cookie, fallback order,
  recovery behavior, and no-management/no-write boundaries.
- Phase 163 — added a disposable Debian 12 container probe for GnuCash Desktop/CLI tooling as the
  next GitHub #22 compatibility-fixture step. The probe installs GnuCash packages only inside a
  temporary container and records bounded command/version/help/package metadata. Local evidence
  confirms GnuCash 4.13 tooling is available in that disposable container, but no safe
  noninteractive create/save-as SQLite fixture command was identified, so no Desktop-generated
  fixture or Desktop-version compatibility claim was added.
- Phase 162 — synchronized stale roadmap baseline after `v0.1.6-readonly` publication and verified
  the published `v0.1.6-readonly` tag from a fresh Docker checkout with the committed synthetic
  fixture, dummy local-only `.env`, `GNUCASH_WRITES_ENABLED=false`, API smoke, browser dogfood,
  disabled validate/create/patch/delete probes, and no raw screenshot/export/backup artifacts. The
  smoke helper now covers DELETE disabled-write probes for old tagged checkouts and future API
  smokes. No product behavior, release/tag/package/image, production deployment, write expansion, or
  real/private data artifact was added.

### Release notes

- `v0.1.7-readonly` was published as a GitHub pre-release on 2026-05-20 after Phase 171 final-gate
  verification. No package, binary artifact, Docker image, or production deployment was published.
- The candidate remains pre-alpha and read-only by default. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP/write-alpha work and outside any safe
  production write-mode claim.
- Publication was performed only after clean `main`, `HEAD == origin/main`, tag/release absence,
  green GitHub CI for the release HEAD, local checks, disabled-write defaults, and sensitive-data
  hygiene were re-confirmed.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- Phase 170 dogfood evidence is synthetic/disposable only and does not establish production or broad
  real-book readiness.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.6-readonly] - 2026-05-20

### Added

- Phase 161 — published `v0.1.6-readonly` as an authorized GitHub pre-release after re-running the
  final release gate: clean `main`, `HEAD == origin/main`, local backend/frontend/Docker checks,
  rendered `GNUCASH_WRITES_ENABLED=false`, tag/release absence, sensitive tracked-file hygiene, and
  GitHub Actions for the release commit passed. Publication created only the annotated tag and
  GitHub pre-release; no package, image, production deployment, write expansion, runtime default
  change, or real/private data artifact was added.
- Phase 160 — reran the full release-candidate synthetic/disposable Docker/Caddy dogfood after
  Phases 153–159: local Compose ran with `GNUCASH_WRITES_ENABLED=false`, API smoke covered health,
  login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports
  summary, and disabled validate/create/patch write probes; an additional DELETE write probe
  returned HTTP 403; headless browser dogfood at 320x720 covered login, protected redirect,
  dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail,
  CSV export, hidden write UI, mobile overflow checks, and no-artifact checks. This is local
  synthetic evidence only; no release/package/image, copied-book dogfood, write expansion, or
  real/private data artifact was added.
- Phase 159 — expanded the release-critical English/Russian localization slice without claiming full
  translation: dashboard report cards/drilldown helper copy/recent/expense/cashflow widgets,
  `/scheduled` title/safety copy/URL-only filters/safe metadata labels/empty states, and
  landing-page sign-in copy now use the typed message catalog with simple named interpolation.
  English remains canonical, Russian remains partial/opt-in, backend/API errors are not localized,
  and no write behavior changed.
- Phase 158 — fixed and pinned a narrow-width mobile account/transaction dogfood issue:
  transaction/account CSV export and transaction empty-state recovery actions now declare
  touch-friendly 44px targets, and browser dogfood defaults to a 320x720 mobile viewport with
  horizontal-overflow and export-touch-target assertions across read-only account/transaction flows.
- Phase 157 — improved scheduled/recurring transaction read-only clarity: `/scheduled` now has
  URL-only display filters for enabled/disabled and template-reference metadata, deterministic safe
  sorting by start date/name/enabled-first, filtered vs true empty states, and stronger copy that no
  template split amounts/accounts/memos/descriptions/raw SQL are exposed or persisted in browser
  storage. Backend regression coverage pins safe DTO redaction and deterministic ordering.
- Phase 156 — added dashboard drilldowns for read-only reporting evidence: summary current-month
  cards, recent transactions, expense-account rows, and cashflow months now link to
  active-book-preserving `/transactions` views built from existing URL filters (`date_from`,
  `date_to`, `account_id`, `limit=50`, `offset=0`), with copy that keeps totals
  base-currency-only/no-conversion and documents that drilldowns are evidence views, not
  browser-side recomputations or new accounting logic.
- Phase 155 — improved the multi-book read-only operator UX slice for GitHub #13: `GET /books`/`GET
  /books/{id}` now return safe storage diagnostics (`available`, `missing_file`, `not_configured`,
  or `remote_or_unchecked`), access status, private-path-redaction metadata, and safe next actions
  without exposing `uri_or_path` or opening GnuCash data during listing; `/books` renders the
  diagnostics and keeps upload/delete/default-changing/registry-edit actions unavailable.
- Phase 154 — refreshed GnuCash Desktop compatibility blocker evidence for GitHub #22 without
  creating a Desktop-generated fixture: the safe probe now records phase-154 metadata,
  missing-command reasons, `desktop_generated_fixture_possible_now=false`, and optional non-mutating
  `apt-cache policy` package-candidate hints. Local evidence confirms `gnucash` and `gnucash-cli`
  are absent on `PATH`; package metadata alone is not compatibility evidence, no package was
  installed, no book was opened, and no broad all-version/PostgreSQL/MySQL/MariaDB/XML/Desktop
  support claim was added.
- Phase 153 — added a reproducible fresh-clone Docker smoke helper and recorded a
  synthetic/disposable clean-checkout pass: the helper clones the repo to a temporary directory,
  copies only the committed synthetic fixture into ignored runtime data, writes dummy local-only
  `.env` values with `GNUCASH_WRITES_ENABLED=false`, validates and starts Docker Compose, runs API
  smoke and browser dogfood, verifies hidden write UI and disabled validate/create/patch probes,
  checks no new raw screenshot/export/backup artifacts, then tears down Docker and removes the
  temporary clone by default. No package, image, production deployment hardening claim, write
  expansion, or real/private data artifact was added.

### Release notes

- `v0.1.6-readonly` was published as a GitHub pre-release on 2026-05-20 after Phase 161 final-gate
  verification. No package, binary artifact, Docker image, or production deployment was published.
- The candidate remains pre-alpha and read-only by default. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP/write-alpha work and outside any safe
  production write-mode claim.
- Publication was performed only after clean `main`, `HEAD == origin/main`, tag/release absence,
  green GitHub CI for the release HEAD, local checks, disabled-write defaults, and sensitive-data
  hygiene were re-confirmed.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- Phase 160 dogfood evidence is synthetic/disposable only and does not establish production or broad
  real-book readiness.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.5-readonly] - 2026-05-19

### Added

- Published `v0.1.5-readonly` as an authorized GitHub pre-release in Phase 152 after the final
  release gate passed.
- Prepared release notes, checklist, and final-gate artifacts for a possible `v0.1.5-readonly`
  maintenance pre-release without creating a tag, GitHub release, package, Docker image, binary
  artifact, production deployment, or write-mode change.
- Candidate scope covers Phases 143–150: app-shell read-only/current-book banner, account-tree
  filtering, transaction list/export clarity, transaction detail/split readability,
  dashboard/reporting limitation clarity, `/books` self-hosting guidance, Russian localization
  coverage, and synthetic Docker/browser dogfood refresh.

### Release notes

- `v0.1.5-readonly` was published as a GitHub pre-release on 2026-05-19 after Phase 152 final-gate
  verification. No package, binary artifact, Docker image, or production deployment was published.
- The candidate remains pre-alpha and read-only by default. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP/write-alpha work and outside any safe
  production write-mode claim.
- Publication was performed only after clean `main`, `HEAD == origin/main`, tag/release absence,
  green GitHub CI for the release HEAD, local checks, disabled-write defaults, and sensitive-data
  hygiene were re-confirmed.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- Phase 150 dogfood evidence is synthetic/disposable only and does not establish production or broad
  real-book readiness.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.4-readonly] - 2026-05-19

### Added

- Phase 142 — published `v0.1.4-readonly` as an authorized GitHub pre-release after the final
  release gate confirmed clean `main`, `HEAD == origin/main`, successful GitHub Actions, local
  backend/frontend/Docker checks, `GNUCASH_WRITES_ENABLED=false`, and tracked sensitive-file
  hygiene.
- Phase 141 — prepared conservative `v0.1.4-readonly` release artifacts without publishing: release
  notes, release-prep checklist, final gate, README links, project status, and phase handoff
  described the candidate as pre-alpha, read-only by default, not production-ready, not
  security-audited, unpublished, and pending explicit authorization before any tag/GitHub release.
- Phase 139 — reran synthetic/disposable Docker/Caddy dogfood with `GNUCASH_WRITES_ENABLED=false`;
  read-only API smoke covered health, login/auth, books/default book, accounts, transactions,
  transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes;
  browser dogfood covered login, protected redirect, dashboard, accounts, books, scheduled
  awareness, account detail, transaction filters, transaction detail, CSV export, hidden write UI,
  and no-artifact checks.
- Phase 138 — synchronized public README, Russian README, changelog, roadmap, project status, and
  handoff after the recent read-only maintenance and documentation phases.
- Phase 137 — refreshed local secure deployment documentation without product-code changes:
  `docs/deployment/local-secure-deployment.md` now gives concrete localhost/LAN/VPN CORS
  recommendations, JWT secret generation and conservative rotation guidance, app metadata DB backup
  expectations for `data/app/app.db`, and a checkable self-hosting pre-deployment checklist;
  `.env.example` comments now point to fresh JWT secrets and exact CORS examples.
- Phase 136 — refreshed GnuCash compatibility documentation without new fixture or Desktop-version
  claims: `docs/gnucash-compatibility.md` now makes synthetic/disposable evidence boundaries
  explicit and lists Desktop versions as not yet validated by automation, while
  `docs/gnucash-version-fixture-plan.md` inventories current synthetic/disposable fixture evidence
  and keeps future Desktop-generated fixture work gated on safe provenance.
- Phase 135 — polished read-only mobile navigation: the desktop nav is hidden below the `md`
  breakpoint, the mobile shell owns touch-friendly book/locale/theme/logout controls, shared
  controls meet the 44px touch-target expectation, the shell reserves enough bottom space for fixed
  mobile navigation, and transaction-detail splits render as mobile cards at narrow widths.
- Phase 134 — added shape-matched read-only loading skeletons for dashboard, accounts, transactions,
  and books during SvelteKit navigation/data reloads, including active-book switching.
- Phase 133 — improved read-only empty and error states: accessible empty/error components now
  provide clearer labels/actions, the global error page maps API/network/403/404/server failures to
  user-safe retry/back actions, and books/scheduled/transactions/accounts routes show informative
  empty states for no accessible books, no schedules, no transactions, no matching filters, and no
  accounts.

### Release notes

- `v0.1.4-readonly` was published as a GitHub pre-release on 2026-05-19 after Phase 142 final-gate
  verification. No package, binary artifact, Docker image, or production deployment was published.
- This remains a conservative pre-alpha/read-only candidate. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP/write-alpha work, test-fixture-only
  when enabled, and outside any safe production write-mode claim.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- Phase 139 dogfood evidence is synthetic/disposable only and does not establish production or broad
  real-book readiness.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.2.0-writealpha] - 2026-05-19

### Added

- Phase 132 — published `v0.2.0-writealpha` as an authorized pre-alpha GitHub pre-release: release
  notes, checklist, and final-gate docs summarize write-alpha CRUD as experimental, disabled by
  default with `GNUCASH_WRITES_ENABLED=false`, executable only under the `APP_ENV=test` gate when
  explicitly enabled, supported only by synthetic/disposable fixture evidence, not production-ready,
  not security-audited, not safe for real/private books, and published after final checks.
- Phase 131 — completed the authorized write-alpha DELETE transaction slice without default
  enablement: `DELETE /books/{book_id}/transactions/{transaction_id}` requires
  `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test`, uses copied/disposable fixtures only in tests,
  creates a backup before deletion, holds/releases the per-book lock, records success/failure audit
  rows, returns 404 for missing transactions before backup/lock/mutation, rejects read-only/viewer
  access before write-service construction, and exposes a hidden-by-default frontend delete form
  with explicit acknowledgement and browser confirmation.
- Phase 130 — hardened the experimental write-alpha PATCH transaction path without default
  enablement: `PATCH /books/{book_id}/transactions/{transaction_id}` remains limited to
  `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` copied/disposable fixtures, preserves
  description/date/split-memo-only edits, reports missing transactions as 404 before
  lock/backup/mutation, records backup paths on failed post-backup PATCH audits, and adds
  disposable-fixture lifecycle coverage for successful PATCH, validation failure, missing
  transaction, synthetic post-backup failure, lock release, no backup leak, and concurrent
  PATCH+CREATE lock contention.
- Phase 129 — added write-alpha recovery and maintainer-review documentation without product-code
  changes or default write enablement: `docs/write-alpha-recovery-procedure.md` covers containment,
  backup selection, stale-lock cleanup, restore, integrity checks, and damaged-book triage for
  synthetic/disposable books only, while `docs/write-alpha-maintainer-checklist.md` provides a
  checkable gate for default-disabled config, `APP_ENV=test`, disposable fixtures, lifecycle
  evidence, recovery docs, and sensitive-data hygiene.
- Phase 128 — expanded write-alpha create-route safety coverage without default enablement: added
  copied/disposable fixture concurrency coverage for two parallel POST writes, synthetic post-backup
  error-path coverage proving lock release/failed audit/intact backup/no book mutation, and
  read-only/viewer book-access rejection before write-service construction.
- Phase 127 — refreshed GnuCash Desktop compatibility evidence for GitHub #22:
  `gnucash`/`gnucash-cli` remain unavailable in the execution environment, so the matrix records a
  Desktop-tooling blocker rather than a fabricated Desktop-generated fixture claim.
- Phase 126 — completed read-only GitHub #11/#12 triage: transaction query matching now includes
  transaction notes when exposed by the GnuCash/piecash object, docs clarify
  description/notes/split-memo search semantics, saved filter presets are de-scoped in favor of
  URL-only presets for privacy, and scheduled/recurring awareness was closed as already covered.

### Known limitations

- Write-alpha remains experimental, disabled by default, and executable only with `APP_ENV=test`
  when explicitly enabled.
- Real/private-book write safety is not established and not claimed.
- Not production-ready and not security-audited.

## [0.1.3-readonly] - 2026-05-19

### Added

- Phase 122 — prepared and verified the `v0.1.3-readonly` maintenance release gate across backend
  tests, frontend checks/build, Docker Compose config validation, tag/release absence checks, GitHub
  Actions state, and sensitive tracked-file hygiene.
- Phase 123 — started the post-MVP/write-alpha safety foundation without enabling writes by default:
  added regression coverage for disabled-by-default config and route short-circuiting,
  write-lock-failure audit evidence, and explicit create-validation guards, and updated
  controlled-write readiness gates. No write capability was enabled or broadened.
- Phase 124 — hardened the write-alpha controlled transaction create path without default
  enablement: enabled write routes are now limited to `APP_ENV=test` copied/disposable fixture
  scope, route-level integration coverage verifies create book-state read-back, backup, audit
  success, lock release, and validation-failure audit/no-backup behavior, and controlled-write docs
  now label this as experimental test-fixture-only evidence.
- Phase 125 — published `v0.1.3-readonly` as a GitHub pre-release after stopping the live
  personal-book Docker deployment, removing ignored local runtime `.env`/copied-book/tmp artifacts,
  re-checking clean `main`, `HEAD == origin/main`, tag/release absence, recent GitHub Actions
  success, Docker Compose config validity, whitespace diff check, and sensitive tracked-file
  hygiene. No packages were published.

### Fixed

- Phase 121 — fixed Conservative dashboard summary zero-value fallback when base-currency
  transactions exist but account balance fields report zero: summary now falls back to split-derived
  asset/liability totals through `as_of_date` only when account-balance asset/liability totals are
  both zero, while preserving legitimate empty zero summaries, Decimal/string money handling, and
  no-conversion behavior.
- Phase 120 — optimized read-only account-detail transaction list/count by selecting account-scoped
  transaction candidates through splits before applying existing filters/pagination/CSV semantics;
  added synthetic account-detail filtered-list and CSV benchmark evidence without production
  scalability claims.
- Phase 119 — stripped the synthetic GnuCash `Root Account:` prefix from displayed account full-name
  paths in the service layer while preserving child paths, account IDs, parent references, and API
  response shape; backend fixture/regression tests now expect cleaned names such as
  `Assets:Bank:Checking`.
- Phase 118 — stabilized the desktop transaction table with fixed full-width columns, safe
  truncation for long descriptions/account names, and no needless desktop horizontal scroll; also
  narrowed account-tree desktop grid sizing to avoid narrow-layout overflow. Frontend static route
  checks pin the CSS-only regression contract.

### Release notes

- `v0.1.3-readonly` was published as a GitHub pre-release on 2026-05-19 after the owner live-stand
  review and cleanup of the temporary local personal-book deployment.
- This remains a conservative pre-alpha/read-only release. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP work, test-fixture-only when enabled,
  and outside any safe production write-mode claim.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.2-readonly] - 2026-05-19

### Added

- Phase 117 — published `v0.1.2-readonly` as an annotated git tag and GitHub pre-release after
  preflight confirmed clean `main`, `HEAD == origin/main`, GitHub #38 closed, tag/release absence,
  recent GitHub Actions success, Docker Compose config validity, whitespace diff check, and
  sensitive tracked-file hygiene. No packages were published.
- Phase 116 — completed GitHub #38 copied personal-book dogfood with a local-only Docker/Caddy
  read-only run against Val's provided safe copied book archive, recording only redacted
  route/status evidence and no private book data, app DB, screenshots, CSV exports, `.env`, paths,
  names, descriptions, memos, amounts, secrets, tags, releases, or packages.
- Phase 115 — prepared conservative `v0.1.2-readonly` release notes, release-prep checklist, and
  final-gate artifact for the maintenance pre-release without publishing a tag, GitHub release,
  package, or changing the default read-only/write-disabled posture.
- Phase 114 — added a durable headless Chromium/CDP browser dogfood helper and recorded a
  synthetic/disposable Docker/Caddy UI/API dogfood refresh covering login, dashboard, accounts,
  books, scheduled awareness, transaction filters, account/transaction detail, CSV export, and
  disabled-write probes with `GNUCASH_WRITES_ENABLED=false`.
- Phase 113 — added a Russian accounting/safety glossary and localized the transaction filter/CSV
  export UI slice through the existing message catalog, while keeping English canonical, translation
  partial, URL-only filters, and read-only/export warnings intact.
- Phase 112 — added safe CORS deployment posture diagnostics to `/health` and startup logs, warning
  when `CORS_ORIGINS` contains `*` while `APP_ENV` is not development-like, and documented exact
  localhost/LAN/VPN origin examples without production-readiness claims.
- Phase 111 — added a safe GnuCash Desktop/CLI tooling availability probe for compatibility
  evidence, documented that the local environment has no `gnucash`/`gnucash-cli`, and kept
  Desktop-generated compatibility claims explicitly blocked until a disposable Desktop environment
  exists.
- Phase 110 — hardened the read-only `/books` metadata UX with explicit access role/status/read-only
  metadata, safe book-context links to existing read-only views, stronger no-management-action copy,
  and regression coverage that archived/unauthorized books remain hidden or blocked.
- Phase 109 — added a conservative read-only scheduled/recurring transaction awareness API and
  `/scheduled` UI page that expose only safe summary metadata, avoid next-run predictions and
  template split details, and keep GnuCash Desktop as the authoritative editor.

### Fixed

- Phase 105 — synchronized local release/status documentation and the existing GitHub release body
  for the already published `v0.1.1-readonly` pre-release. This corrected stale release-prep-only
  wording, updated README/PROJECT_STATUS/release notes to name `v0.1.1-readonly` as the current
  public read-only pre-alpha release, and documented the guardrail that release/status docs must be
  updated in the same phase as factual release-state changes. No product code, tag, release,
  package, write-mode setting, private data, or real GnuCash book was changed.

### Release notes

- `v0.1.2-readonly` was published as a GitHub pre-release on 2026-05-19 after Phase 116 copied
  personal-book dogfood passed with redacted evidence and GitHub #38 was closed.
- This remains a conservative pre-alpha/read-only release. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP work outside this release scope.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version compatibility is claimed.
- Phase 116 personal copied-book dogfood evidence is intentionally redacted and does not include
  private paths, account names, transaction descriptions, memos, amounts, SQL dumps, screenshots,
  CSV bodies, app DB contents, tokens, or secrets.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.1-readonly] - 2026-05-18

### Fixed

- Phase 81 — redacted default-book seed logs so startup logs no longer expose full configured book
  paths or connection URI details.
- Phase 82 — expanded read-only multi-book access-boundary regression coverage for archived and
  unauthorized books across route families.
- Phase 83 — hardened frontend money-display decisions to avoid using `Number()` for money-string
  display logic.
- Phase 84 — added CSV export response headers and frontend proxy forwarding for export limit,
  total, truncation, and timeout policy metadata.
- Phase 95 — fixed GitHub #39: read-only CSV export now fetches up to the documented 10,000-row
  export cap instead of inheriting the historical 500-row list-service clamp. Regression coverage
  and synthetic benchmark evidence confirmed correct row-count/header behavior.
- Phase 96 — confirmed the Phase 95 CSV export fix through the generated synthetic large-book
  benchmark path; a 1,000-transaction generated run returned 1,000 CSV data rows with matching
  expected-body metadata.

### Added

- Phase 86 — added a redacted copied-book preflight helper for future safe personal-book dogfood
  attempts.
- Phase 87 through Phase 89 — expanded generated/synthetic benchmark coverage for large books,
  many-splits transactions, and dashboard aggregate paths without broad production-performance
  claims.
- Phase 90 — added a readable transaction active-filter summary and copy stating that the same
  filters apply to the read-only list and CSV export.
- Phase 91 — added a read-only `/books` metadata page for accessible configured books without
  upload, deletion, registry editing, GnuCash data editing, collaborative, or family-wallet
  workflow.
- Phase 92 — added safe GnuCash compatibility metadata collection for copied/disposable SQLite books
  without exposing private paths or financial details.
- Phase 93 — added a narrow Russian localization slice while keeping English canonical and
  translation status honest.
- Phase 103 — added read-only transaction date-range preset links for `This month`, `Last month`,
  `Year to date`, and `Clear dates`; presets use the existing date query parameters, preserve other
  active filters, and keep CSV export parity.
- Phase 104 — broadened the existing read-only transaction `query` filter so transaction list/count,
  account transaction lists, and CSV export match split memo text as well as transaction
  descriptions, case-insensitively.

### Release notes

- `v0.1.1-readonly` was published as a GitHub pre-release on 2026-05-18 and the tag points to
  `a4d04150c043ad4da3dea577b30ed7ffd2032df0`, after Phase 104. Its published scope therefore
  includes the Phase 103/104 read-only transaction date-preset and split-memo search changes.
- This remains a conservative pre-alpha/read-only release. `GNUCASH_WRITES_ENABLED=false` remains
  the default; controlled-write code is experimental post-MVP work outside this release scope.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`,
  app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out
  of git.
- GitHub #38 remains open/blocked until a safe copied personal GnuCash SQL book is available outside
  git for a local-only dogfood rerun.
- Compatibility evidence remains intentionally narrow; no broad
  PostgreSQL/MySQL/MariaDB/XML/all-version or arbitrary real-world-book compatibility is claimed.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time
  multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.0-readonly] - 2026-05-18

### Added

- Phase 43 — local secure deployment guide for conservative localhost, LAN, and VPN-only self-host
  testing while keeping writes disabled by default.
- Phase 44 — backup and recovery runbook for app metadata DB, copied GnuCash books, Docker data
  paths, restore dry-runs, and experimental controlled-write pre-write backup expectations.
- Phase 45 — GnuCash real-version compatibility fixture plan covering target versions, fixture data
  model, safe generation/storage policy, and acceptance tests for issue #22.
- Phase 46 — generated disposable GnuCash SQLite compatibility fixture v1 path with read-only
  service tests for account tree, transaction list, split detail, reports, and checksum no-mutation
  behavior.
- Phase 48 through Phase 50 — read-only core UX polish, transaction search/filter hardening, and
  book switcher stabilization.
- Phase 52 and Phase 53 — Russian localization planning/i18n foundation plus conservative community
  announcement materials.
- Phase 54 — structured safe startup diagnostics, richer non-sensitive `/health` payload, and
  self-hosted troubleshooting guidance.
- Phase 77 and Phase 78 — copied/disposable-data Docker/API/browser dogfood evidence, including the
  `/login` redirect-loop fix and CSV export proxy behavior.
- Phase 79 — conservative `v0.1.0-readonly` release notes and final release-gate artifact.
- Phase 80 — published `v0.1.0-readonly` as an annotated git tag on commit
  `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` and created the GitHub pre-release using
  `docs/release/v0.1.0-readonly-notes.md`.

### Security

- Multiple audit phases re-verified read-only/default-write-disabled posture, httpOnly auth-cookie
  expectations, private-data hygiene, conservative deployment warnings, and limited compatibility
  claims.
- `GNUCASH_WRITES_ENABLED=false` remained the default; controlled writes remained
  experimental/post-MVP.

### Known limitations

- Pre-alpha only; no production-readiness or security-audit guarantee.
- Users should test with copied/disposable data first and avoid direct public-internet exposure.
- GitHub #38 remains open for copied personal-book dogfood when a safe copied SQL book is available.

## [0.0.2-prealpha] - 2026-05-18

### Added

- Phase 17 — synthetic GnuCash fixture and read-only integration validation.
- Phase 18 — README screenshots and mobile preview with synthetic data.
- Phase 19 — multi-currency limitation tests and auth cookie security documentation.
- Phase 20 — multi-book UI foundation (book switcher, book-aware routes).
- Phase 21 — file-based write lock replacement (`fcntl.flock()` for multi-worker safety).
- Phase 22 — real controlled write integration tests against disposable piecash books.
- Phase 23 — backup restore smoke test (automated restore verification).
- Phase 24 — CSV export for transactions (read-only, filter-preserving, 10,000 row cap).
- Phase 25 — documentation, release, and roadmap sync for the next pre-alpha candidate.
- Phase 26 — audit-driven status sync after independent review.
- Phase 27 — discoverability and community announcement readiness docs.
- Phase 28 — GnuCash compatibility matrix for committed synthetic fixtures.
- Phase 29 — audit-driven release documentation sync for Phases 26–28.
- Phase 30 — frontend amount range filters for read-only transaction browsing and CSV export.
- Phase 31 — global read-only safety status banner in the authenticated web shell.
- Phase 32 — backend write-gating regression coverage for disabled validate/create/patch routes.
- Phase 33 — controlled-writes documentation cleanup and public status sync after disabled-write
  regression coverage.
- Phase 34 — public README/status baseline sync through the Phase 33 baseline.
- Phase 35 — audit-driven public status sync through Phase 34 and controlled-writes limitation
  cleanup.
- Phase 36 — write-mode UI warning and explicit confirmation for experimental controlled writes.
- Phase 37 — independent audit and baseline sync after Phase 36.
- Phase 38 — personal read-only dogfood guide and manual smoke checklist for copied GnuCash books.
- Phase 39 — automated read-only API smoke script for local Docker deployments.
- Phase 40 — `v0.0.2-prealpha` release-candidate checklist and notes cleanup without publishing a
  tag/release.
- Phase 41 — `v0.0.2-prealpha` release-gate audit and release-documentation hygiene cleanup without
  publishing a tag/release.
- Phase 42 — published `v0.0.2-prealpha` after the Phase 41 gate and green local/GitHub checks.

### Security

- Auth cookie deployment documentation (httpOnly, sameSite, secure flags, no production guarantee).
- Multi-currency reporting limitations documented and tested.
- Independent audit report refreshed for Phase 29 with read-only/default-write checks.
- Authenticated app shell now displays a persistent read-only-by-default reminder.
- Disabled-write API regression tests now prove validate/create/patch return read-only 403 responses
  without constructing the write service.
- Controlled-writes documentation now reflects file-based locking, backup restore smoke coverage,
  and disabled-write bypass regression coverage as completed safety work while write mode remains
  experimental and disabled by default.
- Controlled-writes limitations now correctly state that frontend amount range filters exist for
  read-only browsing and CSV export.
- Experimental write mode now shows a prominent UI warning and requires explicit acknowledgement
  before final create submission while remaining disabled by default.
- Release-gate audit re-verified disabled-write gating and tracked-file sensitive-data hygiene
  before `v0.0.2-prealpha` publication.

### Known limitations

- Pre-alpha only; no production-readiness guarantee.
- piecash write compatibility not guaranteed for all GnuCash versions.
- Transaction amount range filters are available for browsing and CSV export; advanced export
  customization is still limited.
- Multi-book UI is structural; full multi-user access control is post-MVP.
- Compatibility matrix currently covers committed synthetic SQLite fixtures only;
  PostgreSQL/MySQL/MariaDB, XML books, and multiple desktop-generated versions are not yet
  validated.

## [0.0.1] - 2026-05-16

### Added

- Initial public skeleton / MVP foundation.
- AGPL-3.0 license.
- README with project overview, honest pre-alpha status, safety warnings, and release/tag
  instructions.
- SECURITY.md with private vulnerability reporting guidance and pre-alpha safety warnings.
- CONTRIBUTING.md with current backend/frontend setup and sensitive data policy.
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1).
- `.env.example` with documented bootstrap and GnuCash book configuration.
- `.gitignore` rules for environment files, GnuCash book files, backups, and secrets.
- GitHub issue templates, pull request template, and funding metadata placeholder.
- GitHub Actions CI for required-file checks, sensitive tracked-file checks, frontend checks,
  backend tests, and Docker Compose validation.
- Documentation for architecture, MVP scope, roadmap, security model, GnuCash safety, development,
  competitive review, and product positioning.
- SvelteKit frontend skeleton with login flow, dashboard, accounts, transactions, theme system,
  mobile navigation, and PWA manifest foundation.
- FastAPI backend skeleton with health endpoint, authentication, app metadata database, book
  registry/access services, and read-only book APIs.
- `piecash` integration through a read-only service layer for GnuCash SQL books.
- Read-only account, transaction, and report DTOs/API endpoints.
- Docker Compose deployment scaffold with API, web, and Caddy proxy services.
- Backend pytest suite and frontend route/type/build checks.

### Security

- MVP GnuCash access is documented and implemented as read-only-first.
- App metadata is stored separately from the GnuCash book.
- Auth token is stored in an httpOnly cookie by the frontend, not browser local/session storage.
- No telemetry added.

### Known limitations

- Pre-alpha only; no production-readiness guarantee.
- Users should test with a copy or fixture book before real data.
- Basic reports aggregate only configured base-currency values; no automatic currency conversion.
- Docker Compose config is validated in CI, but deployments still need environment-specific testing.
