"""Controlled errors for GnuCash book operations."""


class BookNotFoundError(Exception):
    """Raised when the configured GnuCash book path does not exist or cannot be opened."""

    def __init__(self, path: str, detail: str | None = None):
        self.path = path
        self.detail = detail
        msg = f"GnuCash book not found: {path}"
        if detail:
            msg += f" ({detail})"
        super().__init__(msg)


class BookNotConfiguredError(Exception):
    """Raised when no GnuCash book path is configured."""

    def __init__(self, detail: str | None = None):
        self.detail = detail or "No GnuCash book path configured"
        super().__init__(self.detail)


class EntityNotFoundError(Exception):
    """Raised when a requested entity (account, transaction) does not exist in the book."""

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class GnuCashReadError(Exception):
    """Raised when a read operation on the GnuCash book fails."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(f"GnuCash read error: {detail}")


class ScheduledRecurrenceError(Exception):
    """Typed, redacted failure for unsafe scheduled recurrence metadata."""

    MESSAGES = {
        "scheduled_recurrence_invalid_metadata": "Scheduled transaction recurrence metadata is invalid.",
        "scheduled_recurrence_cycle": "Scheduled transaction recurrence could not advance safely.",
    }

    def __init__(self, code: str):
        if code not in self.MESSAGES:
            code = "scheduled_recurrence_invalid_metadata"
        self.code = code
        self.message = self.MESSAGES[code]
        super().__init__(self.message)

    def detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}
