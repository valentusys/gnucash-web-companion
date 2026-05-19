# Phase 162 — v0.1.6-readonly tagged smoke

Date: 2026-05-20
Status: PASS
Scope: cycle 2/3 roadmap phase 1/10 only

## Goal

Confirm that the published `v0.1.6-readonly` tag starts through the documented read-only Docker path from a fresh checkout, using only synthetic/disposable data and dummy local-only secrets.

## Source and checkout

- Repository source for the fresh clone: `/home/val/gnucash-web-companion`
- Ref tested: `v0.1.6-readonly`
- Checked-out commit: `6ea3cfb`
- Full tag target checked locally: `6ea3cfb23bf3ff8c573a72303a53fe93be6b4f1a`
- Smoke command log: `/home/val/.hermes/logs/gnucash-web-companion/phase-162/v0.1.6-tagged-smoke.log`

The temporary checkout was removed by the smoke helper after `docker compose down --volumes --remove-orphans`.

## Runtime setup

The smoke helper:

- cloned the repository to a temporary directory outside git;
- checked out `v0.1.6-readonly`;
- copied only the committed synthetic fixture to ignored runtime data as `data/books/main.gnucash.sqlite`;
- wrote a temporary local `.env` inside the temporary clone only;
- started Docker Compose behind Caddy on `http://127.0.0.1:18086`;
- used dummy local-only admin credentials;
- removed the temporary clone after the run.

Synthetic runtime fixture evidence:

- Runtime fixture filename: `main.gnucash.sqlite`
- Fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`

## Checks run

```bash
scripts/smoke/fresh-clone-docker-smoke.sh \
  --repo /home/val/gnucash-web-companion \
  --ref v0.1.6-readonly \
  --port 18086
```

Covered checks:

- Docker Compose config validation for the tagged checkout.
- Rendered/runtime write posture: `GNUCASH_WRITES_ENABLED=false` confirmed by Compose validation and `/api/health` returning `writes_enabled=false`.
- Docker/Caddy startup and `/api/health` readiness.
- API smoke:
  - health;
  - login;
  - `/auth/me`;
  - default book discovery through `/books` and `/books/1`;
  - accounts;
  - transactions;
  - transaction detail;
  - CSV export;
  - reports summary;
  - disabled validate/create/patch write probes returning HTTP 403.
- Additional Phase 162 wrapper probe for tagged checkouts whose smoke helper predates DELETE coverage:
  - disabled DELETE transaction probe returning HTTP 403 with read-only/write-disabled explanation.
- Headless browser dogfood at 320x720:
  - login page;
  - protected redirect;
  - authenticated login with auth cookie not readable from `document.cookie`;
  - dashboard;
  - accounts;
  - books;
  - scheduled;
  - account detail;
  - transaction filters;
  - transaction detail;
  - CSV export route;
  - hidden write UI;
  - no horizontal overflow on covered mobile paths.
- No raw screenshot/export/backup artifacts created in the temporary clone.

## Result

PASS. The published `v0.1.6-readonly` tag started from a fresh checkout through Docker Compose/Caddy and passed the documented read-only API and browser smoke path with synthetic/disposable data only.

## Safety notes

- No real/private GnuCash book was used.
- No `.env`, app DB, copied runtime book, backup, screenshot, raw CSV export, token, key, cert, private path, account name, transaction description, memo, amount, or private financial data was committed.
- This is still pre-alpha local synthetic smoke evidence only.
- No production-readiness, security-audit, public-internet, broad real-book compatibility, or safe production write-mode claim is made.
- No tag, GitHub release, package, Docker image, or binary artifact was published in Phase 162.
- Controlled writes remain post-MVP/write-alpha, disabled by default, and constrained to test/disposable fixture scope when explicitly enabled.

## Tooling fix made on main

The published tag’s bundled API smoke helper predates the DELETE disabled-write check, so Phase 162 added a small wrapper-level DELETE probe to `scripts/smoke/fresh-clone-docker-smoke.sh` for tagged checkouts and added DELETE coverage to `scripts/smoke/read-only-api-smoke.py` on `main` for future smokes. This does not change product behavior.
