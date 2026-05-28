# Real working-book eligibility

Real working-book mutation remains blocked unless all items pass in the same context:
- PM authorizes one exact operation, preferably one minimal CREATE;
- owner provides exact phase confirmation wording;
- independent verified backup exists outside the app and outside the working target;
- GnuCash Desktop is confirmed closed against the book;
- target fingerprint and app metadata identity match the preflight packet;
- preflight and dry-run pass;
- operation preview is exact;
- immediate read-back, audit row, lock lifecycle, compatibility check, restore-to-copy proof and default-disabled reset pass;
- no private evidence is committed.

Forbidden: only-copy book, silent writes, DELETE/PATCH on real working book without separate PM rejection of CREATE-only conservatism, restore over the real book during proof, public write safety claim.
