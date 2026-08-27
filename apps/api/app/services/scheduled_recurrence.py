"""Pure, deterministic recurrence forecasting for read-only scheduled transactions."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from app.services.gnucash_exceptions import ScheduledRecurrenceError

SUPPORTED_PERIOD_TYPES = {
    "once",
    "day",
    "week",
    "month",
    "end of month",
    "nth weekday",
    "last weekday",
    "year",
}
SUPPORTED_WEEKEND_ADJUSTMENTS = {"none", "back", "forward"}
WEEKEND_ADJUSTABLE_PERIOD_TYPES = {"month", "end of month", "year"}
MAX_RECURRENCE_MULTIPLIER = 65_535
# GnuCash constrains finite scheduled-transaction counts to G_MAXINT16.
MAX_FINITE_OCCURRENCES = 32_767
FORECAST_HORIZON_DAYS = 30


@dataclass(frozen=True)
class RecurrenceSpec:
    """One normalized GnuCash recurrence table row."""

    period_type: str
    multiplier: int
    period_start: date
    weekend_adjust: str


@dataclass(frozen=True)
class ScheduleForecast:
    """Bounded, non-materializing scheduled occurrence projection."""

    status: Literal["ready", "disabled", "exhausted"]
    as_of_date: str
    next_due_date: str | None
    is_overdue: bool
    upcoming_7_days: list[str]
    upcoming_30_days: list[str]
    new_transactions_created: Literal[0] = 0


def _invalid_metadata() -> ScheduledRecurrenceError:
    return ScheduledRecurrenceError("scheduled_recurrence_invalid_metadata")


def _validate_recurrence(recurrence: RecurrenceSpec) -> None:
    if recurrence.period_type not in SUPPORTED_PERIOD_TYPES:
        raise _invalid_metadata()
    if not isinstance(recurrence.period_start, date):
        raise _invalid_metadata()
    if recurrence.weekend_adjust not in SUPPORTED_WEEKEND_ADJUSTMENTS:
        raise _invalid_metadata()
    if (
        recurrence.period_type not in WEEKEND_ADJUSTABLE_PERIOD_TYPES
        and recurrence.weekend_adjust != "none"
    ):
        raise _invalid_metadata()
    if recurrence.period_type == "once":
        if recurrence.multiplier not in (0, 1):
            raise _invalid_metadata()
    elif not 1 <= recurrence.multiplier <= MAX_RECURRENCE_MULTIPLIER:
        raise _invalid_metadata()

    days_in_anchor_month = monthrange(recurrence.period_start.year, recurrence.period_start.month)[1]
    if recurrence.period_type == "end of month" and recurrence.period_start.day != days_in_anchor_month:
        raise _invalid_metadata()
    if recurrence.period_type == "nth weekday" and not 1 <= recurrence.period_start.day <= 28:
        raise _invalid_metadata()
    if (
        recurrence.period_type == "last weekday"
        and recurrence.period_start.day + 7 <= days_in_anchor_month
    ):
        raise _invalid_metadata()


def _validate_schedule_metadata(
    recurrences: list[RecurrenceSpec],
    *,
    start_date: date | None,
    end_date: date | None,
    last_occurrence: date | None,
    num_occurrences: int | None,
    remaining_occurrences: int | None,
) -> tuple[date, int, int]:
    if not recurrences:
        raise _invalid_metadata()
    for recurrence in recurrences:
        _validate_recurrence(recurrence)

    if start_date is not None and not isinstance(start_date, date):
        raise _invalid_metadata()
    if end_date is not None and not isinstance(end_date, date):
        raise _invalid_metadata()
    if last_occurrence is not None and not isinstance(last_occurrence, date):
        raise _invalid_metadata()

    effective_start = start_date or min(recurrence.period_start for recurrence in recurrences)
    if end_date is not None and end_date < effective_start:
        raise _invalid_metadata()
    if end_date is not None and last_occurrence is not None and last_occurrence > end_date:
        raise _invalid_metadata()

    total = 0 if num_occurrences is None else num_occurrences
    remaining = 0 if remaining_occurrences is None else remaining_occurrences
    if not isinstance(total, int) or not isinstance(remaining, int):
        raise _invalid_metadata()
    if not 0 <= total <= MAX_FINITE_OCCURRENCES:
        raise _invalid_metadata()
    if not 0 <= remaining <= MAX_FINITE_OCCURRENCES:
        raise _invalid_metadata()
    if total == 0 and remaining != 0:
        raise _invalid_metadata()
    if total > 0 and remaining > total:
        raise _invalid_metadata()
    if end_date is not None and total > 0:
        raise _invalid_metadata()
    return effective_start, total, remaining


def _add_months(anchor: date, months: int, *, mode: str) -> date | None:
    absolute_month = anchor.year * 12 + (anchor.month - 1) + months
    year, zero_based_month = divmod(absolute_month, 12)
    if not 1 <= year <= date.max.year:
        return None
    month = zero_based_month + 1
    days_in_month = monthrange(year, month)[1]

    if mode == "end of month":
        day = days_in_month
    elif mode == "nth weekday":
        nth_index = (anchor.day - 1) // 7
        first_weekday = date(year, month, 1).weekday()
        day = 1 + (anchor.weekday() - first_weekday) % 7 + nth_index * 7
        if day > days_in_month:
            return None
    elif mode == "last weekday":
        last = date(year, month, days_in_month)
        day = days_in_month - (last.weekday() - anchor.weekday()) % 7
    else:
        day = min(anchor.day, days_in_month)
    return date(year, month, day)


def _adjust_for_weekend(value: date, adjustment: str) -> date | None:
    if adjustment == "none" or value.weekday() < 5:
        return value
    offset = 1 if value.weekday() == 5 else 2
    if adjustment == "forward":
        offset = 2 if value.weekday() == 5 else 1
    try:
        return value + timedelta(days=offset if adjustment == "forward" else -offset)
    except OverflowError:
        return None


def _occurrence_at(recurrence: RecurrenceSpec, index: int) -> date | None:
    if index < 0:
        return None
    period_type = recurrence.period_type
    anchor = recurrence.period_start
    try:
        if period_type == "once":
            return anchor if index == 0 else None
        if period_type == "day":
            return anchor + timedelta(days=index * recurrence.multiplier)
        if period_type == "week":
            return anchor + timedelta(days=index * recurrence.multiplier * 7)
        month_multiplier = recurrence.multiplier * (12 if period_type == "year" else 1)
        value = _add_months(anchor, index * month_multiplier, mode=period_type)
    except OverflowError:
        return None
    if value is None:
        return None
    return _adjust_for_weekend(value, recurrence.weekend_adjust)


def _next_recurrence_date(recurrence: RecurrenceSpec, reference: date) -> date | None:
    """Return the first recurrence date strictly after reference without iteration by day."""

    first = _occurrence_at(recurrence, 0)
    if first is None:
        return None
    if first > reference:
        return first
    if recurrence.period_type == "once":
        return None

    lower_index = 0
    upper_index = 1
    while True:
        upper_value = _occurrence_at(recurrence, upper_index)
        if upper_value is None or upper_value > reference:
            break
        lower_index = upper_index
        upper_index *= 2
        if upper_index > 2**31:
            raise ScheduledRecurrenceError("scheduled_recurrence_cycle")

    while lower_index + 1 < upper_index:
        middle = (lower_index + upper_index) // 2
        middle_value = _occurrence_at(recurrence, middle)
        if middle_value is None or middle_value > reference:
            upper_index = middle
        else:
            lower_index = middle

    candidate = _occurrence_at(recurrence, upper_index)
    if candidate is not None and candidate <= reference:
        raise ScheduledRecurrenceError("scheduled_recurrence_cycle")
    return candidate


def _composite_next(recurrences: list[RecurrenceSpec], reference: date) -> date | None:
    candidates: list[date] = []
    for recurrence in recurrences:
        candidate = _next_recurrence_date(recurrence, reference)
        if candidate is None:
            continue
        if candidate <= reference:
            raise ScheduledRecurrenceError("scheduled_recurrence_cycle")
        candidates.append(candidate)
    return min(candidates) if candidates else None


def _composite_on_or_after(recurrences: list[RecurrenceSpec], lower_bound: date) -> date | None:
    candidates: list[date] = []
    for recurrence in recurrences:
        first = _occurrence_at(recurrence, 0)
        if first is None:
            continue
        if first >= lower_bound:
            candidates.append(first)
            continue
        candidate = _next_recurrence_date(recurrence, lower_bound - timedelta(days=1))
        if candidate is not None:
            if candidate < lower_bound:
                raise ScheduledRecurrenceError("scheduled_recurrence_cycle")
            candidates.append(candidate)
    return min(candidates) if candidates else None


def _within_end_date(candidate: date | None, end_date: date | None) -> date | None:
    if candidate is None or (end_date is not None and candidate > end_date):
        return None
    return candidate


def _window_end(as_of_date: date, days: int) -> date:
    try:
        return as_of_date + timedelta(days=days - 1)
    except OverflowError:
        return date.max


def build_schedule_forecast(
    recurrences: list[RecurrenceSpec],
    *,
    as_of_date: date,
    start_date: date | None,
    end_date: date | None,
    last_occurrence: date | None,
    num_occurrences: int | None,
    remaining_occurrences: int | None,
    enabled: bool,
) -> ScheduleForecast:
    """Compute a bounded forecast without creating or mutating any GnuCash entity."""

    if not isinstance(as_of_date, date):
        raise _invalid_metadata()
    effective_start, total, remaining = _validate_schedule_metadata(
        recurrences,
        start_date=start_date,
        end_date=end_date,
        last_occurrence=last_occurrence,
        num_occurrences=num_occurrences,
        remaining_occurrences=remaining_occurrences,
    )

    if not enabled:
        return ScheduleForecast(
            status="disabled",
            as_of_date=as_of_date.isoformat(),
            next_due_date=None,
            is_overdue=False,
            upcoming_7_days=[],
            upcoming_30_days=[],
        )
    if total > 0 and remaining == 0:
        return ScheduleForecast(
            status="exhausted",
            as_of_date=as_of_date.isoformat(),
            next_due_date=None,
            is_overdue=False,
            upcoming_7_days=[],
            upcoming_30_days=[],
        )

    if last_occurrence is not None and last_occurrence >= effective_start:
        next_due = _composite_next(recurrences, last_occurrence)
    else:
        next_due = _composite_on_or_after(recurrences, effective_start)
    next_due = _within_end_date(next_due, end_date)
    if next_due is None:
        return ScheduleForecast(
            status="exhausted",
            as_of_date=as_of_date.isoformat(),
            next_due_date=None,
            is_overdue=False,
            upcoming_7_days=[],
            upcoming_30_days=[],
        )

    finite_remaining: int | None = remaining if total > 0 else None
    candidate = next_due
    if finite_remaining is None:
        if candidate < as_of_date:
            candidate = _composite_on_or_after(recurrences, as_of_date)
            candidate = _within_end_date(candidate, end_date)
    else:
        while candidate is not None and candidate < as_of_date and finite_remaining > 0:
            finite_remaining -= 1
            if finite_remaining == 0:
                candidate = None
                break
            candidate = _within_end_date(_composite_next(recurrences, candidate), end_date)

    upcoming_30: list[str] = []
    thirty_day_end = _window_end(as_of_date, FORECAST_HORIZON_DAYS)
    while candidate is not None and candidate <= thirty_day_end:
        if candidate >= as_of_date:
            upcoming_30.append(candidate.isoformat())
        if finite_remaining is not None:
            finite_remaining -= 1
            if finite_remaining == 0:
                break
        candidate = _within_end_date(_composite_next(recurrences, candidate), end_date)

    seven_day_end = _window_end(as_of_date, 7)
    upcoming_7 = [value for value in upcoming_30 if date.fromisoformat(value) <= seven_day_end]
    return ScheduleForecast(
        status="ready",
        as_of_date=as_of_date.isoformat(),
        next_due_date=next_due.isoformat(),
        is_overdue=next_due < as_of_date,
        upcoming_7_days=upcoming_7,
        upcoming_30_days=upcoming_30,
    )
