# Phase 189 — fresh-clone install smoke v2 with published/current tags

Date: 2026-05-20
Status: COMPLETE — fresh-clone Docker smoke passed for current published read-only tag, current published write-alpha tag, and current main
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 8 only)

## Goal

Verify install/upgrade confidence for current published releases and current `main` without reading private data.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-188.md`;
  - roadmap file named by the phase contract;
  - relevant fresh-clone smoke helper and earlier fresh-clone/tagged-smoke evidence.
- Ran `scripts/smoke/fresh-clone-docker-smoke.sh` against three targets:
  - `v0.1.7-readonly` at `d248b5a355ed2b57913d0c408e643b5f6cfcfe5b` on `http://127.0.0.1:18087`;
  - `v0.2.1-writealpha` at `8c316b9f5c8028b519b603da0ba3cb37542bc4c0` on `http://127.0.0.1:18092`;
  - current `main`/`HEAD` at `04751c3fe472fd7751746df525383214c3eb907c` on `http://127.0.0.1:18089`.
- Each run used only `apps/api/tests/fixtures/test-book.gnucash.sqlite` copied to ignored runtime data inside a temporary clone.
- Each run used dummy local-only `.env` secrets inside the temporary clone and kept `GNUCASH_WRITES_ENABLED=false`.
- Each run covered Docker Compose config validation/startup, `/api/health`, API read-only smoke, disabled validate/create/PATCH/DELETE probes, browser dogfood, hidden write UI, and no-artifact checks.
- Verified teardown left no `/tmp/gwc-fresh-clone-smoke.*` directories and no running `gwc_fresh_clone` Docker containers/volumes/networks.

## Files changed

- `docs/dogfood/phase-189-fresh-clone-smoke-v2.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-189.md`

No product code or smoke helper changes were needed.

## Verification summary

Commands/results recorded for this phase:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref v0.1.7-readonly --port 18087
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref v0.2.1-writealpha --port 18092
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18089
# post-run teardown scan for temp clone directories and gwc_fresh_clone Docker state
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# Sensitive tracked-file hygiene scan from phase execution playbook
```

Results:

- `v0.1.7-readonly` fresh-clone smoke passed; API smoke and browser dogfood passed; disabled validate/create/PATCH/DELETE probes returned 403; no-artifact check passed.
- `v0.2.1-writealpha` fresh-clone smoke passed under default read-only posture; API smoke and browser dogfood passed; disabled validate/create/PATCH/DELETE probes returned 403; no-artifact check passed.
- Current `main` fresh-clone smoke passed; API smoke and browser dogfood passed; disabled validate/create/PATCH/DELETE probes returned 403; no-artifact check passed.
- Post-run host teardown scan found no remaining fresh-clone temp dirs and no running Docker containers/volumes/networks with `gwc_fresh_clone` names.
- Docker Compose config validation on the working tree passed and rendered `GNUCASH_WRITES_ENABLED: "false"`.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No explicit write-enabled run was performed in this phase.
- No real/private book, app DB, backup, `.env`, token, key, cert, screenshot, raw CSV export, private path, account name, memo, amount, or private financial data was committed.
- No release, tag, package, Docker image, public deployment, or production/security/real-book write-safety claim was added.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start combined release-candidate dogfood or release-readiness work from this phase.
