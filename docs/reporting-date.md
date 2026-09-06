# Reporting calendar date

The API process's local calendar date is the installation reporting date. This
preserves the previous Python `date.today()` behavior; there is no new timezone
setting and no browser-inferred timezone. Operators who need a particular zone
must configure the API runtime's standard OS/process timezone (for example its
existing `TZ` environment), not just the web/SSR process. This change does not
alter the host timezone or deployment configuration.

Summary defaults, report month defaults and scheduled forecast defaults use the
same `reporting_clock.reporting_today()` function. Explicit `as_of_date` and
explicit report date ranges remain authoritative.

`GET /books/{book_id}/reports/reporting-date` returns `as_of_date` as YYYY-MM-DD
and `basis=api_local_calendar`. It requires authentication and book view access,
but does not open/query the GnuCash source or require a configured reporting
currency. It can therefore supply the date when financial summary data is
unavailable. It is metadata, not evidence that the book is readable.

The dashboard prefers a valid summary `as_of_date` and uses this endpoint only
as its fallback. Reports and transaction quick presets use the endpoint too.
Date-only strings are pinned to midnight UTC solely for calendar arithmetic;
no frontend server derives installation today from a UTC instant. If the date
cannot be read/validated, defaults/presets are unavailable with a visible status,
not silently replaced by a different clock. Valid explicit report periods still
work without the current-date endpoint.

Scheduled page `as_of_date` is forwarded to the backend and retained by its filter
links. The dashboard pins scheduled requests to its chosen summary date.

Tests inject clocks only inside disposable test runtimes. Coverage includes
positive/negative UTC offsets, year/month rollover, leap February, DST, explicit
periods, metadata-only auth checks and unavailable clock/summary behavior. No
production freeze-clock parameter or host-clock mutation is introduced.
