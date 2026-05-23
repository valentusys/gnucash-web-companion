# Owner feedback gate for future write-alpha dogfood

Status: Phase 312 maintenance guidance.

## Purpose

This page defines when active write-alpha dogfood may resume after the Phase 295–320 closeout cycle.

## Current default

Do not start a new owner write-alpha mutation flow from repository momentum alone.

Future write-alpha dogfood requires fresh owner live-stand feedback or an explicit same-context owner confirmation for the exact proposed scope.

## Allowed without owner confirmation

These tasks remain allowed as normal maintenance:

- read-only bug fixes;
- documentation corrections that keep the current safety posture;
- tests that use committed synthetic fixtures or disposable generated data;
- public status guard maintenance;
- issue triage that does not request new owner mutations.

## Not allowed without a new explicit gate

Do not perform, request, or imply approval for:

- writes on original/private/only-copy books;
- owner CREATE, PATCH, or DELETE mutation steps;
- owner DELETE request packets;
- any mutation on a copied book whose backup/restore state is not freshly verified;
- publication of a new write-alpha release based only on old copied-book evidence.

## Minimum future gate

Before any future owner copied-book write-alpha mutation, create a new same-context packet that states:

1. the exact target type: copied/restorable test book only;
2. the exact mutation count and type;
3. the backup, read-back, audit, lock, restore, reset, and redaction evidence required;
4. that `GNUCASH_WRITES_ENABLED=false` must be restored afterward;
5. that enabled write-alpha remains `APP_ENV=test` gated;
6. that the result will not prove safety for original/private/only-copy books.
