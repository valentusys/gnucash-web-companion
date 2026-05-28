# Owner-writebeta state machine

Foundation states: disabled → preflight → preview → confirmation → mutating → verification → reset_required → complete → disabled. Any failed safety proof may transition to failed_hard_stop, which blocks further writes until a future PM-approved recovery process. The implementation stores opaque refs only: operation, backup, audit, restore. It does not store paths, account names, descriptions, memos, amounts, books, backups, or raw evidence.
