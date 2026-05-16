# Add real integration tests for controlled writes using disposable fixture

Labels: `safety, v0.2-writes, gnucash`

Milestone: `v0.2 controlled writes`

## Goal
Test controlled writes against a disposable real GnuCash SQL book copy.

## Requirements
- Writes disabled by default in normal test environment.
- Explicit write-test environment.
- Backup before write is verified.
- Audit log entry is verified.
- Created transaction can be read back.
- Invalid unbalanced transaction is rejected.
- Original fixture is not modified in-place.
