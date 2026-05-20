# Phase 176 — GnuCash Desktop open-and-integrity verification

Date: 2026-05-20
Status: COMPLETE — PASS with disposable GnuCash CLI tooling evidence; no broad compatibility claim
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 5 only)

## Goal

Verify that the disposable copied book mutated in the write-alpha dogfood path can still be opened/validated by GnuCash Desktop tooling or document an exact blocker/fallback.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-175.md`;
  - roadmap file named by the phase contract;
  - Phase 175 dogfood evidence, write-alpha smoke helper, disposable Desktop container probe, and compatibility notes.
- Recreated a safe disposable Phase 4-style mutation path from the committed synthetic fixture only:
  - copied the synthetic fixture to `/tmp`;
  - ran Phase 174 preflight with disposable-copy acknowledgement;
  - copied it to ignored `data/books/` runtime storage;
  - started local runtime with `APP_ENV=test` and explicit local-only `GNUCASH_WRITES_ENABLED=true`;
  - created exactly one balanced two-split transaction through the existing write-alpha API route.
- Copied the mutated disposable book to `/tmp` and validated it with GnuCash CLI 4.13 inside a temporary `debian:12-slim` Docker container.
- Ran read-only API smoke after the GnuCash CLI check with writes disabled by default.
- Removed ignored runtime book/app DB/backup/lock artifacts after the run.
- Updated compatibility notes narrowly: GnuCash CLI 4.13 accepted this disposable mutated SQLite book, but this is not Desktop-generated fixture evidence or a broad Desktop compatibility claim.

## Files changed

- `docs/dogfood/phase-176-write-alpha-desktop-verification.md`
- `docs/gnucash-compatibility.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-176.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `GNUCASH_WRITES_ENABLED=true` was used only as an explicit local runtime override with `APP_ENV=test`.
- Runtime target was an ignored disposable copy under `data/books/`.
- App DB, backups, and lock files stayed under ignored `data/` runtime paths and were removed after the run.
- GnuCash packages were installed only inside temporary Docker containers, not on the host.
- No real/private/only-copy book was opened or mutated.
- No PATCH or DELETE dogfood was run.
- No release/tag/package was published.
- No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Verification

Commands run:

```bash
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/write-alpha-create-smoke.py
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output <outside-git log path>
docker run --rm -v <temporary disposable directory>:/work:ro debian:12-slim sh -lc '<install GnuCash inside container>; gnucash-cli --logto stderr --report show --name "Balance Sheet" /work/mutated-disposable.gnucash.sqlite'
APP_ENV=test JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-api-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | <filter GNUCASH_WRITES_ENABLED>
```

Results:

- Source preflight passed with redacted summary only: `sha256_12=c8f22b449c49`.
- Mutated disposable book checksum was recorded outside git: `sha256_12=c25172f9a44a`.
- One successful write-alpha create mutation was observed via audit count; one ignored backup file was observed before cleanup.
- `gnucash-cli --version` inside the disposable container reported `GnuCash 4.13`.
- `gnucash-cli --report show --name "Balance Sheet" <redacted mutated disposable book>` exited `0` and returned bounded report metadata only.
- Read-only API smoke after the GnuCash CLI check passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Default Compose config still renders `GNUCASH_WRITES_ENABLED: "false"`.
- Ignored runtime artifacts were removed from `data/books`, `data/backups`, `data/app`, and `data/locks`.

## Next

Continue only with the next explicitly requested phase. Do not run backup/restore drill, PATCH dogfood, DELETE dogfood, release/tag publication, or broader UX/API hardening unless a later phase explicitly requests it.
