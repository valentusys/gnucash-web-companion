# Issue #45 CREATE-only operating policy v1

Date: 2026-06-16
Issue: [#45 Owner real-book CREATE-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/45)
Verdict: **CREATE_ONLY_POLICY_V1_DOCUMENTED**

## Scope and evidence basis

Policy v1 is based on owner-manual-verified real-book CREATE evidence:

- #44 first real-book CREATE trial succeeded and was manually verified in GnuCash Desktop.
- #45 first CREATE-only operating session succeeded and was manually verified.
- #45 next CREATE-only operating session succeeded and was manually verified.
- Latest CREATE session evidence: read-back passed, audit captured, default-disabled reset passed, and
  disabled-write probes passed.

This task executed **no mutation**.

## Policy v1 permits only

- owner-only real-book CREATE-only sessions;
- explicit same-context owner approval per session;
- bounded CREATE count per session;
- individual CREATE operations, not batch;
- route backup before each CREATE;
- read-back after each CREATE;
- redacted audit evidence after each CREATE;
- reset writes to disabled after each session;
- disabled-write probes after reset;
- owner manual GnuCash Desktop verification after each session.

## Policy v1 forbids

- PATCH;
- DELETE;
- batch operations;
- unattended mutation;
- dogfood loops;
- release/tag/package/image publication;
- public write beta;
- production, stable, or security-audited claims;
- committing or posting raw private paths, account names, descriptions, memos, amounts, books, backups,
  screenshots, tokens, keys, certs, or `.env` content.

## Backup policy

Policy v1 keeps **route backup before each CREATE** as the default safe policy.

A future per-session backup relaxation may be considered only after more successful owner-verified sessions
and explicit owner approval. No backup relaxation was made in this task.

## Counts for this policy-documentation task

- CREATE executed: 0
- PATCH executed: 0
- DELETE executed: 0
- batch executed: 0
- release/tag/package/image publication: 0

## Redacted reporting and safety summary

- Tracked docs and #45 comments use only redacted target class and safe operational summaries.
- No raw private evidence, account names, amounts, memos, descriptions, backups, screenshots, books,
  tokens, keys, certs, or `.env` content are included.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- #45 is not blanket CREATE approval; every future session still requires explicit same-context owner
  approval with a bounded CREATE count.

## Exact next allowed step

The next allowed step is a future bounded owner-only real-book CREATE-only session under Policy v1, with
fresh explicit same-context owner approval for the session count and with PATCH/DELETE/batch still forbidden.
