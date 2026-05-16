# Replace in-process write lock before production write mode

Labels: `safety, v0.2-writes`

Milestone: `v0.2 controlled writes`

## Goal
Replace the current in-process write lock before any real write-mode use.

## Why
In-process lock is insufficient for multi-worker or multi-host deployments.

## Options
- File lock
- SQLite app.db lock table with transaction semantics
- Postgres advisory lock if app metadata DB moves to Postgres

## Acceptance criteria
- Concurrent writes are serialized across workers.
- Lock release on failure is tested.
- Lock timeout behavior is documented.
