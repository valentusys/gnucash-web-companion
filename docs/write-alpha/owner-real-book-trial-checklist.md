# Owner real-book trial checklist

Issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)
Status: preparation only; this checklist does not authorize mutation.

## 0. Scope lock

- [ ] Same-context owner/PM approval is present.
- [ ] Approval names the exact target class.
- [ ] Approval names exact operation count: CREATE 1, PATCH 0, DELETE 0, batch 0.
- [ ] Approval confirms no unattended real-book mutation.
- [ ] Approval confirms no release, tag, package, image, or public write beta.
- [ ] Approval confirms no production, stable, or security-audited claim.

If any checkbox above is empty, stop before mutation.

## 1. Pre-mutation safety

- [ ] Committed default remains `GNUCASH_WRITES_ENABLED=false`.
- [ ] Enabled write flow remains `APP_ENV=test` gated.
- [ ] GnuCash Desktop is closed for the target.
- [ ] Lock/no-concurrent-writer check passed.
- [ ] Independent backup exists before route backup.
- [ ] Restore path/proof was verified before mutation.
- [ ] Route backup can be taken immediately before CREATE.
- [ ] Evidence can be reported without raw private data.

If any checkbox above is empty, stop before mutation.

## 2. Route backup before CREATE

- [ ] Route backup taken immediately before CREATE.
- [ ] Route backup result recorded as redacted marker only.
- [ ] Route backup reference is an opaque ID only.
- [ ] No backup path, backup file, book name, or private path is posted or committed.

If route backup fails, stop before CREATE.

## 3. CREATE-only execution

- [ ] Exactly one CREATE was executed.
- [ ] PATCH count remained 0.
- [ ] DELETE count remained 0.
- [ ] Batch count remained 0.
- [ ] No retry created a second transaction without new owner/PM approval.

## 4. Post-CREATE evidence

- [ ] Read-back after CREATE completed.
- [ ] Audit evidence recorded.
- [ ] Audit evidence references route backup.
- [ ] Evidence is redacted and structural only.
- [ ] No raw account names, descriptions, memos, or amounts are included.
- [ ] No raw book, backup, screenshot, token, key, cert, or `.env` content is included.

## 5. Reset and disabled-write probes

- [ ] Runtime reset to `GNUCASH_WRITES_ENABLED=false`.
- [ ] No explicit write-enabled runtime remains active.
- [ ] Disabled validate/write preflight probe blocks writes, if route exists.
- [ ] Disabled CREATE probe blocks writes.
- [ ] Disabled PATCH probe blocks writes.
- [ ] Disabled DELETE probe blocks writes.
- [ ] Probe report includes only route family, status class, and safe error class.

## 6. Reporting boundary

Allowed in committed or issue-posted report:

- [ ] Target class label only.
- [ ] Operation counts: CREATE 1 / PATCH 0 / DELETE 0 / batch 0.
- [ ] Backup, restore, read-back, audit, reset, and probe boolean markers.
- [ ] Opaque route backup and audit references only.
- [ ] Disabled-write probe status classes only.

Forbidden in committed or issue-posted report:

- [ ] Raw private paths.
- [ ] Account names.
- [ ] Transaction descriptions.
- [ ] Memos.
- [ ] Amounts.
- [ ] Book names, raw books, or app DBs.
- [ ] Backup paths, backup names, or backup files.
- [ ] Screenshots containing private data.
- [ ] Tokens, keys, certs, or `.env` content.

## 7. Final stop rule

If any required safety marker is missing, do not continue with more mutations. Preserve backups, keep
writes disabled, and escalate to owner/PM with a redacted blocker report only.
