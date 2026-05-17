# Announcement Draft — gnucash-web-companion

> Draft only. Do not post without maintainer review. Keep the wording conservative and update status links before posting.

## Short pitch

`gnucash-web-companion` is a modern self-hosted, read-only-first web companion for existing GnuCash SQL books. It lets you browse accounts, transactions, dashboards, basic reports, filtered transaction lists, and CSV exports from a browser while keeping GnuCash Desktop as the authoritative editor.

## What works today

- Read-only access to a configured GnuCash SQL book through the backend service layer.
- Login with auth tokens stored in httpOnly cookies.
- Dashboard summaries, account tree/detail, transaction list/detail, filters, and CSV export.
- Read-only book switcher foundation for already-accessible independent books.
- Docker Compose scaffolding, local/LAN/VPN deployment guidance, backup/recovery runbook, smoke-test documentation, and synthetic/disposable fixture validation.
- English UI by default with an initial opt-in Russian localization foundation.
- Public pre-alpha release: `v0.0.2-prealpha`.

## What is not ready

- Not production-ready and not security-audited.
- Not a GnuCash replacement, hosted finance SaaS, family-wallet app, or collaborative accounting system.
- No safe general-purpose write mode for real books; controlled-write code is experimental post-MVP only and disabled by default with `GNUCASH_WRITES_ENABLED=false`.
- Compatibility is still limited to the documented synthetic/disposable fixture paths and tested SQLite scenarios.
- Public-internet exposure is not recommended for early builds.

## Who should test

This may be useful for people who:

- already use GnuCash and want browser/mobile read-only access on their own infrastructure;
- are comfortable testing pre-alpha software against a disposable copy of a GnuCash book;
- can run Docker Compose and review conservative self-host deployment notes;
- want to help validate GnuCash compatibility, read-only UX, deployment docs, and safety boundaries.

This is not for people who need:

- production-ready accounting software;
- audited security guarantees;
- collaborative multi-user editing;
- banking integrations or CSV/OFX imports;
- safe write-mode access to their only copy of a GnuCash book.

## Safety warning to include in any announcement

- Use a disposable/test copy first.
- Keep regular tested backups.
- Do not expose early builds directly to the public internet.
- Keep `GNUCASH_WRITES_ENABLED=false` unless you are deliberately testing experimental post-MVP write code on disposable data.
- Do not enable write mode against your only GnuCash book.
- This is pre-alpha software, not production-ready, and not security-audited.

## Feedback wanted

- Does the read-only browser/mobile workflow match real GnuCash usage?
- Are deployment, backup/recovery, and dogfood docs clear enough for cautious self-host testing?
- Which GnuCash versions/backends should be prioritized for disposable compatibility fixtures?
- Are the safety warnings clear without being misleading or alarmist?
- Are account/transaction filters, CSV export, and book-switching behavior understandable?
- Are there documentation gaps that would block a careful pre-alpha tester?

## Suggested post — r/GnuCash

Title:

```text
Pre-alpha self-hosted read-only web companion for GnuCash SQL books — feedback wanted
```

Body:

```text
Hello r/GnuCash — I’m building gnucash-web-companion, a pre-alpha self-hosted web companion for existing GnuCash SQL books.

The goal is intentionally narrow: read-only browser/mobile access to accounts, transactions, dashboards, basic reports, filtered transaction lists, and CSV export while GnuCash Desktop remains the authoritative editor.

This is not a GnuCash replacement, not production-ready, and not security-audited. Please test only with a disposable copy first. Controlled-write code exists only as experimental post-MVP work and is disabled by default with GNUCASH_WRITES_ENABLED=false.

Repository: https://github.com/valentusys/gnucash-web-companion
Current pre-alpha release: v0.0.2-prealpha

Feedback wanted: GnuCash compatibility, read-only UX, deployment docs, fixture/testing ideas, and safety review.
```

## Suggested post — r/selfhosted

Title:

```text
Pre-alpha: self-hosted read-only web companion for GnuCash books
```

Body:

```text
I’m working on gnucash-web-companion, a pre-alpha self-hosted web app for browsing existing GnuCash SQL books from a browser/mobile UI.

It is read-only by default, keeps GnuCash Desktop as the authoritative editor, stores app metadata separately from the GnuCash book, and currently supports dashboards, accounts, transactions, filters, and CSV export.

Important caveats: not production-ready, not security-audited, do not expose early builds directly to the public internet, and test only with a disposable copy first. Experimental controlled-write code is disabled by default and is not part of the read-only MVP.

Repository: https://github.com/valentusys/gnucash-web-companion

Feedback wanted from self-hosters: deployment docs, Docker Compose ergonomics, LAN/VPN-only guidance, backup/recovery notes, and safety concerns.
```

## Suggested post — Hacker News Show HN later

Use this only after the maintainer deliberately decides that the project is ready for wider attention.

Title:

```text
Show HN: gnucash-web-companion — read-only self-hosted web UI for GnuCash books
```

Body:

```text
I built gnucash-web-companion, a self-hosted web companion for existing GnuCash SQL books.

It is intentionally read-only by default: browse accounts, transactions, dashboards, reports, filters, and CSV exports in a browser while GnuCash Desktop remains the authoritative editor.

It is still pre-alpha, not production-ready, and not security-audited. The safest way to try it is with a disposable copy of a book on local/LAN/VPN-only infrastructure. Experimental write code is disabled by default and is outside the read-only MVP.

Repo: https://github.com/valentusys/gnucash-web-companion

I’d appreciate feedback on the self-hosting model, GnuCash compatibility assumptions, read-only UX, and safety/docs gaps.
```

## Suggested post — Mastodon / Linux / self-hosted communities

```text
I’m building gnucash-web-companion: a pre-alpha, self-hosted, read-only-first web companion for existing GnuCash SQL books.

It can browse accounts, transactions, dashboards, reports, filters, and CSV exports while GnuCash Desktop remains the editor/source of truth.

Caveats: not production-ready, not security-audited, test only with a disposable copy first, and keep write mode disabled. Feedback wanted on GnuCash compatibility, self-host deployment docs, read-only UX, and safety warnings.

https://github.com/valentusys/gnucash-web-companion
```

## Maintainer pre-post checklist

- [ ] Confirm the current release/tag/status links are still accurate.
- [ ] Confirm no wording claims production readiness or audited security.
- [ ] Confirm write mode is described only as experimental, post-MVP, and disabled by default.
- [ ] Confirm feedback request is narrow and actionable.
- [ ] Confirm screenshots/exports, if shared, use only synthetic/disposable data.
