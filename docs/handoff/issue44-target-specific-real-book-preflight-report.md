# Issue #44 target-specific real-book preflight report

Date: 2026-06-11
Issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)
Verdict: **BLOCKED_WITH_EXACT_TARGET_REASON**

## Redacted target summary

- Redacted target class: `owner-primary-real-gnucash-sqlite-book`
- Target outside git: yes
- Target readable: no
- Lock/no-writer check passed: no
- Independent backup exists: no
- Restore proof verified: no
- Route backup capability: yes
- Read-back capability: yes
- Audit/reset/probe capability: yes
- Operation counts: CREATE 0 / PATCH 0 / DELETE 0 / batch 0

## Exact blocker

The owner supplied a private directory-level handle, but no concrete target file copy was safely selected
and verified in this run. Because the target file copy was not verified, the preflight cannot prove target
readability, target-specific lock/no-writer state, independent backup existence, or restore proof.

The first CREATE trial remains blocked until a later same-context owner/PM step provides or confirms:

1. exact private target file copy to use, kept out of committed and GitHub-posted evidence;
2. independent backup exists for that target;
3. restore proof/path was verified before mutation;
4. GnuCash Desktop is closed for that target;
5. no concurrent writer or lock is active for that target.

## Safety statement

No CREATE, PATCH, DELETE, batch, dogfood, release, tag, package, image publication, or public write beta
was performed by this preflight. No raw private paths, account names, descriptions, memos, amounts,
books, backups, screenshots, tokens, keys, certs, or `.env` content are included in this tracked report.
