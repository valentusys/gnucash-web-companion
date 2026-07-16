"""Backup restore smoke tests for GnuCash books.

Exercises the backup -> write -> restore -> verify cycle against disposable
copies of the synthetic fixture, confirming the original book state is fully
recoverable.

No production code changes: these tests call the same backup service and write
service that production uses, then restore by copying the backup back over the
modified book (shutil.copy2, matching the production backup model).

No HTTP endpoints are tested — this validates the service layer directly.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import piecash
import pytest

from app.services import backup as backup_mod
from app.services.backup import create_book_backup
from app.schemas.gnucash_writes import (
    TransactionCreateRequestDTO,
    TransactionSplitWriteDTO,
)
from app.services import gnucash_write as gw_mod
from app.services.gnucash_write import GnuCashWriteService
from app.services.write_lock import WriteLockService

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"

# Account GUIDs from the synthetic fixture (same as test_write_integration.py)
CHECKING = "c73e8aa01e6345288662b556f2f866f3"
FOOD = "388a85676d4a4643ae6cd28166c34e79"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _book_config(book_path: Path) -> dict[str, Any]:
    """Return a book config dict suitable for GnuCashWriteService."""
    return {"uri_or_path": str(book_path), "base_currency": "SEK"}


def _count_transactions(book_path: Path) -> int:
    """Open the book read-only and return the transaction count."""
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return len(list(book.transactions))
    finally:
        book.close()


def _count_accounts(book_path: Path) -> int:
    """Open the book read-only and return the account count."""
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return len(list(book.accounts))
    finally:
        book.close()


def _transaction_guids(book_path: Path) -> set[str]:
    """Open the book read-only and return the set of transaction GUIDs."""
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return {tx.guid for tx in book.transactions}
    finally:
        book.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def book_copy(tmp_path: Path) -> Path:
    """Return a fresh copy of the synthetic fixture in tmp_path."""
    dst = tmp_path / "test.gnucash.sqlite"
    shutil.copy2(str(FIXTURE_PATH), str(dst))
    return dst


@pytest.fixture
def write_service(book_copy: Path, tmp_path: Path) -> GnuCashWriteService:
    """Return a GnuCashWriteService configured for the copied book, with tmp lock dir."""
    lock_dir = tmp_path / "locks"
    from app.services import write_lock as wl_mod

    new_svc = WriteLockService(lock_dir=lock_dir)
    wl_mod.write_lock_service = new_svc
    gw_mod.write_lock_service = new_svc
    return GnuCashWriteService(_book_config(book_copy))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBackupFileValidity:
    """Verify the backup file created before a write is a valid GnuCash book."""

    def test_rapid_backups_have_unique_paths_and_do_not_overwrite(
        self,
        book_copy: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Multiple backups for one source at the same clock tick must not overwrite evidence."""

        fixed_now = datetime(2026, 5, 21, 4, 30, 1, 123456, tzinfo=timezone.utc)

        class FixedDateTime:
            @classmethod
            def now(cls, tz=None):
                return fixed_now if tz is not None else fixed_now.replace(tzinfo=None)

        monkeypatch.setattr(backup_mod, "datetime", FixedDateTime)

        first = Path(create_book_backup(_book_config(book_copy)))
        second = Path(create_book_backup(_book_config(book_copy)))
        third = Path(create_book_backup(_book_config(book_copy)))

        assert first != second != third
        assert first.exists()
        assert second.exists()
        assert third.exists()
        assert first.name == "test_gnucash_20260521_043001_123456.sqlite"
        assert second.name == "test_gnucash_20260521_043001_123456_1.sqlite"
        assert third.name == "test_gnucash_20260521_043001_123456_2.sqlite"
        fixed_tick_backups = sorted(first.parent.glob("test_gnucash_20260521_043001_123456*.sqlite"))
        assert fixed_tick_backups == [first, second, third]

        with first.open("rb") as first_handle, second.open("rb") as second_handle, third.open("rb") as third_handle:
            assert first_handle.read() == second_handle.read() == third_handle.read()

    def test_backup_file_exists_and_readable(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """After a write, the backup file must exist and be readable by piecash."""
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Backup validity test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-75.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="75.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = write_service.create_transaction(request, user_id=1, book_id=1)
        backup_path = Path(result.backup_path)

        # Backup file exists and is non-empty
        assert backup_path.exists(), "Backup file must exist after write"
        assert backup_path.stat().st_size > 0, "Backup file must not be empty"

        # Backup is a valid SQLite GnuCash book: piecash can open it read-only
        book = piecash.open_book(str(backup_path), readonly=True)
        try:
            accounts = list(book.accounts)
            transactions = list(book.transactions)
        finally:
            book.close()

        assert len(accounts) > 0, "Backup must contain accounts"
        assert len(transactions) > 0, "Backup must contain transactions"

    def test_backup_contains_pre_write_state(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """The backup must contain the original transaction count (pre-write state)."""
        # Record original state from the copy (same as fixture)
        original_tx_count = _count_transactions(book_copy)
        original_account_count = _count_accounts(book_copy)

        # Perform a write
        request = TransactionCreateRequestDTO(
            date="2026-06-15",
            description="Pre-write state test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-200.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="200.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = write_service.create_transaction(request, user_id=1, book_id=1)
        backup_path = Path(result.backup_path)

        # Backup must have the original transaction count (one fewer than modified book)
        backup_tx_count = _count_transactions(backup_path)
        assert backup_tx_count == original_tx_count, (
            f"Backup must have original tx count {original_tx_count}, got {backup_tx_count}"
        )

        # Backup must have the same account count
        backup_account_count = _count_accounts(backup_path)
        assert backup_account_count == original_account_count, (
            f"Backup must have original account count {original_account_count}, got {backup_account_count}"
        )


class TestRestoreUndoesWrite:
    """Verify that restoring a backup over a modified book recovers the original state."""

    def test_restore_undoes_transaction_count(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """After write + restore, the book must have the original transaction count."""
        original_tx_count = _count_transactions(book_copy)
        original_guids = _transaction_guids(book_copy)

        # Perform a write (adds one transaction)
        request = TransactionCreateRequestDTO(
            date="2026-07-01",
            description="Restore undo test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-150.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="150.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = write_service.create_transaction(request, user_id=1, book_id=1)
        backup_path = Path(result.backup_path)

        # Modified book now has one more transaction
        modified_tx_count = _count_transactions(book_copy)
        assert modified_tx_count == original_tx_count + 1, (
            f"Modified book should have {original_tx_count + 1} transactions, got {modified_tx_count}"
        )

        # Restore: copy backup back over the modified book (production restore model)
        shutil.copy2(str(backup_path), str(book_copy))

        # After restore, transaction count must match original
        restored_tx_count = _count_transactions(book_copy)
        assert restored_tx_count == original_tx_count, (
            f"Restored book must have original tx count {original_tx_count}, got {restored_tx_count}"
        )

        # After restore, the new transaction GUID must be gone
        restored_guids = _transaction_guids(book_copy)
        assert restored_guids == original_guids, (
            "Restored book must have exactly the original transaction GUIDs"
        )

    def test_restore_preserves_account_count(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """After write + restore, the book must have the original account count."""
        original_account_count = _count_accounts(book_copy)

        # Perform a write
        request = TransactionCreateRequestDTO(
            date="2026-08-01",
            description="Account count restore test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-300.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="300.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = write_service.create_transaction(request, user_id=1, book_id=1)
        backup_path = Path(result.backup_path)

        # Restore from backup
        shutil.copy2(str(backup_path), str(book_copy))

        # Account count must match original
        restored_account_count = _count_accounts(book_copy)
        assert restored_account_count == original_account_count, (
            f"Restored book must have original account count {original_account_count}, "
            f"got {restored_account_count}"
        )

    def test_restore_preserves_original_transaction_data(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """After restore, original transactions must be intact (same GUIDs, descriptions)."""
        # Capture original transaction data before any write
        book = piecash.open_book(str(book_copy), readonly=True)
        try:
            original_txs = {
                tx.guid: {"description": tx.description, "post_date": tx.post_date}
                for tx in book.transactions
            }
        finally:
            book.close()

        # Perform a write
        request = TransactionCreateRequestDTO(
            date="2026-09-01",
            description="Data preservation test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-50.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="50.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = write_service.create_transaction(request, user_id=1, book_id=1)
        backup_path = Path(result.backup_path)

        # Restore from backup
        shutil.copy2(str(backup_path), str(book_copy))

        # Verify original transactions are intact
        book = piecash.open_book(str(book_copy), readonly=True)
        try:
            restored_txs = {
                tx.guid: {"description": tx.description, "post_date": tx.post_date}
                for tx in book.transactions
            }
        finally:
            book.close()

        assert restored_txs == original_txs, (
            "Restored book must have identical original transaction data"
        )

    def test_original_fixture_never_modified(self, write_service: GnuCashWriteService, book_copy: Path, tmp_path: Path):
        """The committed fixture file must never be modified by any test."""
        # Record fixture state before
        fixture_before = FIXTURE_PATH.stat().st_mtime

        # Perform a write
        request = TransactionCreateRequestDTO(
            date="2026-10-01",
            description="Fixture safety test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=CHECKING,
                    amount="-25.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FOOD,
                    amount="25.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        write_service.create_transaction(request, user_id=1, book_id=1)

        # Record fixture state after
        fixture_after = FIXTURE_PATH.stat().st_mtime
        assert fixture_before == fixture_after, (
            "The committed fixture file must never be modified"
        )
