# Phase 213 — v0.2.4 tagged fresh-clone smoke

Date: 2026-05-21
Status: COMPLETE — fresh-clone/tag Docker smoke passed for `v0.2.4-writealpha`; current `main` comparison passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md` (Cycle 2, Phase 2 only)

## Goal

Verify the published `v0.2.4-writealpha` tag through a fresh clone/tag path with the committed synthetic fixture and default-disabled writes, producing an independent post-release install/dogfood artifact.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-212.md`, and the cycle-2 roadmap file.
- Hardened the existing fresh-clone smoke helper so each run executes browser dogfood at both mobile `320x720` and desktop `1280x900` widths.
- Adjusted browser dogfood CDP emulation so wide viewports are treated as desktop rather than mobile.
- Ran the helper against:
  - published tag `v0.2.4-writealpha`;
  - current `HEAD` comparison.
- Documented the evidence in `docs/dogfood/phase-213-v0.2.4-tagged-fresh-clone-smoke.md`.
- Updated public/status docs for completed Phase 213 without publishing a tag/release.

## Files changed

- `scripts/smoke/fresh-clone-docker-smoke.sh`
- `scripts/smoke/read-only-browser-dogfood.py`
- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/ROADMAP.md`
- `docs/dogfood/phase-213-v0.2.4-tagged-fresh-clone-smoke.md`
- `docs/handoff/phase-213.md`

No product runtime behavior, write route, write default, `APP_ENV=test` gate, release/tag, package/image, or real/private data path changed.

## Fresh-clone smoke evidence

Commands/results:

```text
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref v0.2.4-writealpha --port 18081
# passed; fresh-clone smoke PASS head=8b6412b

scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18082
# passed; fresh-clone smoke PASS head=fedc892
```

Both runs used only the committed synthetic fixture copied into ignored runtime data inside a temporary clone, dummy local-only secrets, Caddy/Docker, and `GNUCASH_WRITES_ENABLED=false`.

Covered checks:

- Docker Compose config validation with writes disabled.
- `/api/health` reporting `writes_enabled=false`.
- Read-only API smoke: health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, scheduled metadata, and write-alpha audit-summary read-only endpoint.
- Disabled validate/create/PATCH/DELETE probes returning HTTP 403.
- Extra wrapper DELETE probe for older tagged helper compatibility.
- Browser dogfood at mobile and desktop widths with hidden write UI, no-overflow checks, CSV fetch, and auth cookie not readable from `document.cookie`.
- No raw screenshot/export/backup artifacts found in the fresh clone.
- Helper teardown removed temporary clones and Docker runtime.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remained default and was not overridden to true.
- No write-enabled mode was run.
- No real/private/copied personal book, only-copy book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw private path, account name, memo, amount, or private financial data was committed.
- Local smoke logs stayed under untracked `.hermes/`.
- No new release/tag/publication was created.

## Verification summary

Commands/results:

```text
python3 -m py_compile scripts/smoke/read-only-browser-dogfood.py && bash -n scripts/smoke/fresh-clone-docker-smoke.sh
# passed

scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref v0.2.4-writealpha --port 18081
# passed

scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18082
# passed
```

Additional commands/results:

```text
python3 scripts/check_public_status.py
# passed

cd apps/api && pytest tests/test_public_status_guard.py -q
# 6 passed

cd apps/api && pytest -q
# 487 passed, 34 warnings

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# passed: API and web render GNUCASH_WRITES_ENABLED: "false"

git diff --check
# passed

python3 sensitive tracked-file hygiene scan
# passed

docker ps/volume/network filters for gwc_fresh_clone
# no leftover fresh-clone containers, volumes, or networks
```

## Risks / follow-up

- Evidence is local synthetic/disposable fresh-clone smoke only. It does not make `v0.2.4-writealpha` production-ready, security-audited, or safe for real/private or only-copy books.
- The published tag itself still contains the older browser result label (`mobile_viewport`) for wide widths; the Phase 213 wrapper nevertheless ran the tagged checkout at `1280x900`, and current `main` now labels wide emulation as desktop going forward.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
