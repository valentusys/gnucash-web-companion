"""Deterministic generated-matrix tests for read-only scheduled forecasts."""

from __future__ import annotations

from datetime import date

import pytest

import app.services.scheduled_recurrence as scheduled_recurrence
from app.services.gnucash_exceptions import ScheduledRecurrenceError
from app.services.scheduled_recurrence import RecurrenceSpec, build_schedule_forecast


def spec(
    period_type: str,
    period_start: date,
    *,
    multiplier: int = 1,
    weekend_adjust: str = "none",
) -> RecurrenceSpec:
    return RecurrenceSpec(
        period_type=period_type,
        multiplier=multiplier,
        period_start=period_start,
        weekend_adjust=weekend_adjust,
    )


@pytest.mark.parametrize(
    ("recurrence", "start_date", "last_occurrence", "as_of_date", "expected"),
    [
        (spec("once", date(2026, 6, 1), multiplier=0), date(2026, 6, 1), None, date(2026, 5, 31), "2026-06-01"),
        (spec("day", date(2026, 6, 1), multiplier=2), date(2026, 6, 1), date(2026, 6, 1), date(2026, 6, 2), "2026-06-03"),
        (spec("week", date(2026, 6, 1), multiplier=2), date(2026, 6, 1), date(2026, 6, 1), date(2026, 6, 2), "2026-06-15"),
        (spec("month", date(2026, 1, 31)), date(2026, 1, 31), date(2026, 1, 31), date(2026, 2, 1), "2026-02-28"),
        (spec("end of month", date(2026, 1, 31)), date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 1), "2026-03-31"),
        (spec("nth weekday", date(2026, 1, 13)), date(2026, 1, 13), date(2026, 1, 13), date(2026, 1, 14), "2026-02-10"),
        (spec("last weekday", date(2026, 1, 30)), date(2026, 1, 30), date(2026, 1, 30), date(2026, 1, 31), "2026-02-27"),
        (spec("year", date(2024, 2, 29)), date(2024, 2, 29), date(2024, 2, 29), date(2025, 1, 1), "2025-02-28"),
        (spec("month", date(2026, 8, 1), weekend_adjust="back"), date(2026, 7, 1), None, date(2026, 7, 31), "2026-07-31"),
        (spec("month", date(2026, 8, 1), weekend_adjust="forward"), date(2026, 7, 1), None, date(2026, 8, 1), "2026-08-03"),
    ],
)
def test_generated_recurrence_matrix_is_deterministic(
    recurrence: RecurrenceSpec,
    start_date: date,
    last_occurrence: date | None,
    as_of_date: date,
    expected: str,
):
    forecast = build_schedule_forecast(
        [recurrence],
        as_of_date=as_of_date,
        start_date=start_date,
        end_date=None,
        last_occurrence=last_occurrence,
        num_occurrences=0,
        remaining_occurrences=0,
        enabled=True,
    )

    assert forecast.status == "ready"
    assert forecast.next_due_date == expected
    assert forecast.new_transactions_created == 0


def test_composite_recurrence_uses_every_row_and_deduplicates_dates():
    forecast = build_schedule_forecast(
        [
            spec("month", date(2026, 1, 1)),
            spec("month", date(2026, 1, 5)),
            spec("month", date(2026, 1, 5)),
        ],
        as_of_date=date(2026, 6, 1),
        start_date=date(2026, 1, 1),
        end_date=None,
        last_occurrence=date(2026, 5, 5),
        num_occurrences=0,
        remaining_occurrences=0,
        enabled=True,
    )

    assert forecast.next_due_date == "2026-06-01"
    assert forecast.upcoming_7_days == ["2026-06-01", "2026-06-05"]
    assert forecast.upcoming_30_days == ["2026-06-01", "2026-06-05"]


def test_forecast_respects_finite_occurrences_and_inclusive_end_date_limits():
    end_limited = build_schedule_forecast(
        [spec("day", date(2026, 6, 1))],
        as_of_date=date(2026, 6, 1),
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 2),
        last_occurrence=None,
        num_occurrences=0,
        remaining_occurrences=0,
        enabled=True,
    )

    assert end_limited.next_due_date == "2026-06-01"
    assert end_limited.upcoming_7_days == ["2026-06-01", "2026-06-02"]
    assert end_limited.upcoming_30_days == ["2026-06-01", "2026-06-02"]

    finite = build_schedule_forecast(
        [spec("day", date(2026, 6, 1))],
        as_of_date=date(2026, 6, 1),
        start_date=date(2026, 6, 1),
        end_date=None,
        last_occurrence=None,
        num_occurrences=2,
        remaining_occurrences=2,
        enabled=True,
    )

    assert finite.next_due_date == "2026-06-01"
    assert finite.upcoming_7_days == ["2026-06-01", "2026-06-02"]
    assert finite.upcoming_30_days == ["2026-06-01", "2026-06-02"]

    exhausted = build_schedule_forecast(
        [spec("day", date(2026, 6, 1))],
        as_of_date=date(2026, 6, 1),
        start_date=date(2026, 6, 1),
        end_date=None,
        last_occurrence=date(2026, 6, 1),
        num_occurrences=2,
        remaining_occurrences=0,
        enabled=True,
    )
    assert exhausted.status == "exhausted"
    assert exhausted.next_due_date is None
    assert exhausted.upcoming_7_days == []
    assert exhausted.upcoming_30_days == []


def test_overdue_next_due_is_preserved_while_windows_are_bounded_from_as_of():
    forecast = build_schedule_forecast(
        [spec("day", date(2026, 1, 1))],
        as_of_date=date(2026, 1, 5),
        start_date=date(2026, 1, 1),
        end_date=None,
        last_occurrence=date(2026, 1, 1),
        num_occurrences=0,
        remaining_occurrences=0,
        enabled=True,
    )

    assert forecast.next_due_date == "2026-01-02"
    assert forecast.is_overdue is True
    assert forecast.upcoming_7_days == [
        "2026-01-05",
        "2026-01-06",
        "2026-01-07",
        "2026-01-08",
        "2026-01-09",
        "2026-01-10",
        "2026-01-11",
    ]
    assert len(forecast.upcoming_30_days) == 30
    assert forecast.upcoming_30_days[0] == "2026-01-05"
    assert forecast.upcoming_30_days[-1] == "2026-02-03"
    assert forecast.new_transactions_created == 0


def test_disabled_schedule_has_no_due_dates_and_never_materializes():
    forecast = build_schedule_forecast(
        [spec("day", date(2026, 1, 1))],
        as_of_date=date(2026, 1, 5),
        start_date=date(2026, 1, 1),
        end_date=None,
        last_occurrence=None,
        num_occurrences=0,
        remaining_occurrences=0,
        enabled=False,
    )

    assert forecast.status == "disabled"
    assert forecast.next_due_date is None
    assert forecast.upcoming_7_days == []
    assert forecast.upcoming_30_days == []
    assert forecast.new_transactions_created == 0


@pytest.mark.parametrize(
    ("recurrence", "num_occurrences", "remaining_occurrences"),
    [
        (spec("unsupported", date(2026, 1, 1)), 0, 0),
        (spec("month", date(2026, 1, 1), multiplier=0), 0, 0),
        (spec("day", date(2026, 1, 1), weekend_adjust="forward"), 0, 0),
        (spec("end of month", date(2026, 1, 30)), 0, 0),
        (spec("day", date(2026, 1, 1)), 2, 3),
        (spec("day", date(2026, 1, 1)), -1, 0),
        (spec("day", date(2026, 1, 1)), 32_768, 32_768),
    ],
)
def test_invalid_metadata_fails_with_typed_redacted_error(
    recurrence: RecurrenceSpec,
    num_occurrences: int,
    remaining_occurrences: int,
):
    with pytest.raises(ScheduledRecurrenceError) as exc_info:
        build_schedule_forecast(
            [recurrence],
            as_of_date=date(2026, 1, 1),
            start_date=date(2026, 1, 1),
            end_date=None,
            last_occurrence=None,
            num_occurrences=num_occurrences,
            remaining_occurrences=remaining_occurrences,
            enabled=True,
        )

    assert exc_info.value.code == "scheduled_recurrence_invalid_metadata"
    assert "unsupported" not in str(exc_info.value).lower()


def test_conflicting_end_and_occurrence_limits_fail_as_invalid_metadata():
    with pytest.raises(ScheduledRecurrenceError) as exc_info:
        build_schedule_forecast(
            [spec("day", date(2026, 1, 1))],
            as_of_date=date(2026, 1, 1),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            last_occurrence=None,
            num_occurrences=2,
            remaining_occurrences=2,
            enabled=True,
        )

    assert exc_info.value.code == "scheduled_recurrence_invalid_metadata"


def test_last_occurrence_after_end_date_fails_as_invalid_metadata():
    with pytest.raises(ScheduledRecurrenceError) as exc_info:
        build_schedule_forecast(
            [spec("day", date(2026, 1, 1))],
            as_of_date=date(2026, 1, 1),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            last_occurrence=date(2026, 2, 1),
            num_occurrences=0,
            remaining_occurrences=0,
            enabled=True,
        )

    assert exc_info.value.code == "scheduled_recurrence_invalid_metadata"


def test_non_progressing_recurrence_fails_as_typed_cycle(monkeypatch):
    monkeypatch.setattr(
        scheduled_recurrence,
        "_next_recurrence_date",
        lambda recurrence, reference: reference,
    )

    with pytest.raises(ScheduledRecurrenceError) as exc_info:
        build_schedule_forecast(
            [spec("day", date(2026, 1, 1))],
            as_of_date=date(2026, 1, 1),
            start_date=date(2026, 1, 1),
            end_date=None,
            last_occurrence=None,
            num_occurrences=0,
            remaining_occurrences=0,
            enabled=True,
        )

    assert exc_info.value.code == "scheduled_recurrence_cycle"
    assert "2026" not in str(exc_info.value)
