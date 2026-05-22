# Phase 278 handoff — Copied-book write-alpha posture update

Status: COMPLETE — copied-book write-alpha posture refreshed without broad safety claims.

## Objective

Update public/private docs to accurately reflect current copied-book evidence after Phase 276 and Phase 277.

## Result

Added `docs/write-alpha/copied-book-write-alpha-posture.md` and synchronized public status wording.

Current posture is now explicit:

- owner copied-book dry-run evidence is accepted as dry-run-only evidence;
- exactly one owner copied-book CREATE evidence run is accepted for one copied/restorable working copy outside git;
- no owner PATCH evidence exists;
- no owner DELETE evidence exists;
- PATCH/DELETE remain blocked unless later roadmap gates authorize them and the owner gives exact confirmation;
- `GNUCASH_WRITES_ENABLED=false` remains default;
- enabled write-alpha still requires `APP_ENV=test`;
- no production, stable, security-audited, public-internet, broad compatibility, or real/private/original/only-copy write-safety claim is made.

## Files updated

- `docs/write-alpha/copied-book-write-alpha-posture.md`
- `README.md`
- `README.ru.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/ROADMAP.md`
- `scripts/check_public_status.py`
- `docs/handoff/phase-278.md`

## Verification

- `python3 scripts/check_public_status.py`
- `git diff --check`

## Next gate

Phase 279 must invoke PM for the Cycle 2 release/no-release decision. Do not publish unless release gates pass and PM explicitly authorizes publication.
