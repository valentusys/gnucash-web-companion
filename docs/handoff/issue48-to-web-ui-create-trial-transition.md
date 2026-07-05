# Issue #48 to #49 web UI CREATE trial transition

Date: 2026-07-05

Issues:

- [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
- [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Transition verdict

#48 is sufficiently validated for the **preview-only owner web transaction-entry UI**. It may remain open as a
non-mutating preview/UI evidence tracker, but further #48 polishing should pause unless bugs are found.

The next product value is a separate, bounded, owner-approved web UI CREATE trial on a test copy or
owner-selected target under #49.

## #48 evidence accepted for preview-only UI

#48 now has redacted evidence for:

- backend `create-preview` endpoint;
- `/transactions/new` preview-only UI;
- disabled/inert Future Create control;
- approval packet;
- stale-preview warning;
- account selector UX;
- accessibility/mobile polish;
- manual browser smoke PASS;
- deterministic synthetic browser smoke PASS;
- static/backend guards proving the preview path remains read-only and non-mutating.

This evidence does **not** approve CREATE, PATCH, DELETE, batch mutation, public write beta, release publication,
or production/stable/security-audited claims.

## #49 strict scope

#49 is the future owner-approved web UI CREATE execution trial. Creating #49 does not grant mutation approval.

Any future mutating session must require fresh same-context owner/PM approval with:

- exact target class;
- exact CREATE count;
- first trial default: `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`;
- explicit acknowledgement that writes are enabled only for the bounded session;
- reset to `GNUCASH_WRITES_ENABLED=false` after the session.

Allowed target classes only after approval:

- test copy;
- owner-selected real-book target.

## Required #49 preflight before any CREATE

Before any CREATE, the exact target must pass:

- target file exists and is readable;
- target is outside the repository;
- GnuCash Desktop is closed;
- no concurrent writer/lock is present;
- no `.LCK`/`.LNK` is present;
- no Syncthing conflict copy exists before/after if applicable;
- independent backup exists;
- restore proof is available.

Abort before mutation if any item is not ready.

## Required #49 web UI execution flow

The future trial should reuse the #48 preview and approval packet. The Create button may become active only when
all conditions hold:

- writes enabled;
- owner-approved bounded session;
- valid non-stale preview;
- preview-reviewed checkbox checked;
- exact CREATE count is 1;
- target preflight passed.

Default state remains disabled/inert, and no active create path should be reachable in read-only mode.

The future trial must also perform:

- UI preview before CREATE;
- CREATE only from reviewed current preview, not stale preview;
- backup immediately before CREATE;
- read-back after CREATE;
- redacted audit evidence;
- disabled-write probes after reset for validate/preflight, CREATE, PATCH, and DELETE;
- manual Desktop verification for the first UI CREATE trial.

## Reporting boundary

GitHub/tracked reporting remains redacted-only:

- target class only;
- no raw private paths, account names, descriptions, memos, amounts, GUIDs, book names, backups, screenshots,
  tokens, keys, certs, or `.env` content;
- private details only in Telegram/local UI/private owner context.

## Safety summary for this transition

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- no private-book dogfood.
- no release/public write beta.
- no production/stable/security-audited claim.
- no private details leaked.
