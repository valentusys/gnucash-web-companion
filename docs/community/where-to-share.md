# Where to Share — gnucash-web-companion

> Planning document only. Do not post anywhere without maintainer review.

## Sharing principle

Share cautiously with people who can give useful feedback on GnuCash compatibility, read-only UX, self-hosting, documentation, and safety. Do not market the project as production-ready. Do not imply write mode is safe for real books.

## Ready-now channels for narrow feedback

### r/GnuCash

Why:

- Highest relevance for real GnuCash users.
- Good place to validate whether read-only browser/mobile access solves a real problem.
- Useful for compatibility fixture suggestions.

How to frame:

- GnuCash Desktop remains the authoritative editor.
- Read-only by default.
- Test disposable copies only.
- Ask for compatibility, UX, and docs feedback.

Avoid:

- Calling it a replacement for GnuCash.
- Suggesting general-purpose editing/write support.
- Asking non-technical users to trust real books.

### Small GnuCash/Linux/self-hosted Mastodon circles

Why:

- Lower-pressure feedback loop than large aggregators.
- Good for short safety-conscious updates and early docs review.

How to frame:

- Pre-alpha, read-only-first, self-hosted.
- Ask for cautious testers and docs review.
- Link to the repo and release notes/checklist.

Avoid:

- Viral launch language.
- Screenshots containing real financial data.

## Later channels, only after maintainer review

### r/selfhosted

Why:

- Strong audience for Docker Compose, LAN/VPN deployment, backup/recovery, and security warnings.

Gate before posting:

- Local secure deployment guide is current.
- Backup/recovery runbook is current.
- README status points to the current public pre-alpha.
- Known limitations are visible.
- Maintainer is ready to answer deployment and security questions.

### Hacker News Show HN

Why:

- Broad audience can find architecture, security, and positioning gaps quickly.

Gate before posting:

- Use only after deliberately deciding broader attention is useful.
- Current release/tag and README status are accurate.
- No open release-blocking safety/doc mismatch is known.
- The announcement clearly says pre-alpha, not production-ready, not security-audited.
- Maintainer is ready for high-volume feedback and issue triage.

## Do not share yet / not recommended now

- Product Hunt or launch-style platforms: too marketing-heavy for pre-alpha financial software.
- Paid/hosted SaaS directories: contradicts self-hosted companion positioning.
- General personal-finance groups that expect production-ready software.
- Any channel where readers may treat the app as safe for their only GnuCash book.

## Feedback prompts to use

- Which GnuCash versions/backends should be prioritized for disposable compatibility fixtures?
- Does the read-only account/transaction/dashboard flow match how you inspect books?
- Are the Docker/self-host deployment instructions clear enough for local/LAN/VPN testing?
- Are the backup/recovery and safety warnings understandable?
- What documentation would you need before trying this on a copied book?

## Safety checklist before each post

- [ ] The post says pre-alpha.
- [ ] The post says not production-ready and not security-audited.
- [ ] The post says test with a disposable copy first.
- [ ] The post keeps GnuCash Desktop as the authoritative editor.
- [ ] The post says read-only by default.
- [ ] The post describes controlled writes only as experimental post-MVP and disabled by default.
- [ ] The post does not imply collaborative accounting, hosted SaaS, family-wallet baseline, banking integrations, import/sync, or safe write mode.
- [ ] Any screenshot/export uses only synthetic/disposable data.
