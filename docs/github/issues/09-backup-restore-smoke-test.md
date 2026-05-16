# Add safe backup restore smoke test

Labels: `safety, v0.2-writes`

Milestone: `v0.2 controlled writes`

## Goal
Verify that backups created before write operations can actually be restored.

## Requirements
- Use disposable fixture only.
- Create backup.
- Simulate write.
- Restore backup.
- Confirm original state can be read again.
