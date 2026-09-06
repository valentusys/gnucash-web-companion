"""The API process's local calendar date is the installation reporting clock."""
from datetime import date


def reporting_today() -> date:
    return date.today()
