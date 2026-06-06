# Restore safety boundary for #36

Status: non-mutating guard document. This is not execution approval, not destructive restore approval, and not real-book safety evidence.

## Boundary

- Accepted restore evidence for #36 must be restore-to-copy evidence only unless a later PM/owner decision explicitly changes scope.
- Restore-to-copy means a copied/restorable fixture or synthetic/disposable target is restored or verified without touching an original/private/real-working/only-copy book.
- It is not destructive restore and must not overwrite a real working book.
- It is not real-book safety evidence and must not be cited as production, stable, or security-audited readiness.
- Every future restore packet needs an independent backup and redacted evidence only.

## Required posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Enabled write-alpha/writebeta route execution remains `APP_ENV=test` gated.
- Mutation counts for this boundary package: CREATE 0 / PATCH 0 / DELETE 0.
- No public write beta and default NO_RELEASE posture remain in effect.

## Evidence allowed in public docs

Allowed public evidence is limited to command names, pass/fail status, redacted fixture class, route family/count, and redacted safety outcome. Public docs must not include GnuCash books, SQLite books, app DBs, backups, CSV exports, screenshots, `.env`, tokens, keys, certs, private paths, account names, transaction descriptions, memos, amounts, or raw private evidence.

## Docs/tests-only readiness wording

Generated docs/tests-only readiness tasks may inspect tracked wording and guard assertions only. They must report review-only evidence with these negative labels: `NOT_RESTORE_DRILL`, `NO_BACKUP_ARTIFACT_CREATED`, `DO_NOT_ENABLE_WRITES`, and `NO_PRIVATE_DATA_REVIEWED`.

This wording check must not run restore commands, create backup artifacts, open books, mutate GnuCash data, inspect runtime logs, or collect private path evidence. It must also document no retry on the same copied/restorable fixture after failed restore, read-back, or audit evidence; recover/regenerate the disposable target and re-run read-only checks first. Any disabled-write reset probe is a documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`, not an executed mutation. If tracked docs and tests cannot prove the boundary, the safe outcome is a checkpoint rather than broadening into dogfood, backup creation, restore execution, or private-data inspection.

## Closure implication

Restore readiness helps #36 only when paired with current state-machine, default-disabled, compatibility, copied/restorable authorization, and PM closure evidence. By itself this boundary keeps #36 open.
