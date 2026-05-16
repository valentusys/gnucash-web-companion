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
