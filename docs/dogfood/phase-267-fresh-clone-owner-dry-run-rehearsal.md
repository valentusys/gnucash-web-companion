# Phase 267 — Fresh-clone owner dry-run rehearsal

Status: COMPLETE — synthetic/disposable fresh-clone owner dry-run rehearsal passed.

## Analyst objective

Rehearse the documented owner copied-book dry-run instructions from a fresh clone using only synthetic/disposable data, prove no mutation happened, verify evidence redaction, and confirm the default-disabled posture after the run.

## Scope executed

- Cloned the repository into a temporary directory from current `HEAD`.
- Copied only the committed synthetic fixture to an outside-git temporary target.
- Ran the documented owner dry-run command with explicit `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`.
- Wrote evidence to a temporary outside-git evidence file and validated it with the redaction checker.
- Compared target checksum before and after the dry-run.
- Ran the existing fresh-clone Docker/Caddy smoke with `GNUCASH_WRITES_ENABLED=false` to verify disabled validate/create/PATCH/DELETE probes return 403 after reset/default-disabled posture.

## Evidence summary

Fresh owner dry-run command:

```text
PASS: owner copied-book dry-run completed; mutation_requested=false; mutation_performed=false; preflight=ready; backup=created-before-step; default_disabled=verified-default-disabled; paths=redacted
```

Redaction checker accepted the temporary evidence. Bounded evidence fields showed:

```text
mode=dry-run
classification=synthetic
preflight_status=ready
backup_status=created-before-step
backup_count=1
mutation_requested=false
mutation_performed=false
create_command_status=not-run
patch_status=not-supported-by-default
delete_status=not-supported-by-default
disabled_reset_status=verified-default-disabled
redaction_status=validated-before-write
```

Checksum proof:

```text
fresh_clone_head=5fe33a0
before_sha12=c8f22b449c49
after_sha12=c8f22b449c49
backup_count=1
```

Fresh-clone default-disabled Docker/Caddy smoke:

```text
ok: health status=ok writes_enabled=false
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
PASS: read-only API smoke checks completed
PASS: read-only browser dogfood completed  # mobile 320x720
PASS: read-only browser dogfood completed  # desktop 1280x900
ok: no new raw screenshot/export/backup artifacts found
fresh-clone smoke PASS head=5fe33a0
```

## Safety checks

- No private, owner, original, only-copy, or production book was used.
- The target was a temporary outside-git copy of the committed synthetic fixture.
- No CREATE, PATCH, or DELETE command path was exposed or executed by the owner dry-run entrypoint.
- The target checksum was unchanged after dry-run.
- Redacted evidence was validated before any artifact was committed.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default Docker posture; disabled validate/create/PATCH/DELETE probes returned 403 in the fresh-clone smoke.

## Limitations

This is synthetic/disposable rehearsal evidence only. It does not prove real/private-book write safety, does not authorize CREATE/PATCH/DELETE, and does not establish production readiness, security audit status, public-internet safety, broad compatibility, or safe original/only-copy writes.
