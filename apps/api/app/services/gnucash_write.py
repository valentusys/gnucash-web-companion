"""Controlled write service for GnuCash books.

Implements the write flow:
1. Validate request
2. Check user can edit book
3. Acquire per-book write lock
4. Backup GnuCash book
5. Open book for write
6. Apply change
7. Commit/save
8. Write audit log
9. Release lock
10. Return result
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import piecash

from app.schemas.gnucash_writes import (
    DECIMAL_STRING_PATTERN,
    TransactionCreateRequestDTO,
    TransactionPatchRequestDTO,
    TransactionSplitWriteDTO,
    TransactionValidationResultDTO,
    TransactionWriteResultDTO,
)
from app.services.backup import BackupError, create_book_backup
from app.services.gnucash_book import GnuCashBookService, _guid
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)
from app.services.write_lock import WriteLockError, write_lock_service

logger = logging.getLogger(__name__)

VALIDATION_ACCOUNT_READ_FAILURE_DETAIL = "Could not validate accounts from configured disposable test book"


def _book_config_value(book_config: Any, key: str, default: Any = None) -> Any:
    """Read a value from either a Book-like object or a pinned-source config dict."""

    if isinstance(book_config, dict):
        return book_config.get(key, default)
    return getattr(book_config, key, default)


class GnuCashWriteError(Exception):
    """Raised when a write operation on the GnuCash book fails."""

    def __init__(self, detail: str, backup_path: str | None = None):
        self.detail = detail
        self.backup_path = backup_path
        super().__init__(f"GnuCash write error: {detail}")


class GnuCashWriteService(GnuCashBookService):
    """Write service extending the read-only GnuCashBookService.

    All write operations follow the strict flow: validate, lock, backup, write, audit.
    """

    def validate_transaction_create(
        self,
        request: TransactionCreateRequestDTO,
    ) -> TransactionValidationResultDTO:
        """Validate a transaction create request without writing.

        Checks:
        - At least two splits
        - Sum of splits equals zero per currency
        - Single-currency CREATE only; no synthetic conversion is attempted
        - All accounts exist
        - Amounts are valid decimal strings
        - Placeholder/hidden accounts are blocked
        - Currency is valid and matches each account and the book default currency
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Check at least two splits
        if len(request.splits) < 2:
            errors.append("At least two splits are required")

        # Validate amounts are valid finite decimals and sum to zero per currency.
        totals_by_currency: dict[str, Decimal] = {}
        for split in request.splits:
            amount_text = str(split.amount)
            if not re.fullmatch(DECIMAL_STRING_PATTERN, amount_text):
                errors.append(f"Invalid amount '{amount_text}' for account {split.account_id}")
                continue
            try:
                amount = Decimal(amount_text)
            except (InvalidOperation, ValueError):
                errors.append(f"Invalid amount '{amount_text}' for account {split.account_id}")
                continue
            if not amount.is_finite():
                errors.append(f"Invalid amount '{amount_text}' for account {split.account_id}")
                continue
            currency = split.currency.upper()
            if len(currency) != 3 or not currency.isalpha():
                errors.append(f"Invalid currency code '{split.currency}' for account {split.account_id}")
                continue
            if currency not in totals_by_currency:
                totals_by_currency[currency] = Decimal("0")
            totals_by_currency[currency] += amount

        for currency, total in totals_by_currency.items():
            if total != Decimal("0"):
                errors.append(
                    f"Splits do not balance to zero for currency {currency}: sum is {total}"
                )
        if len(totals_by_currency) > 1:
            errors.append(
                "Multiple split currencies are not supported by write-alpha CREATE; "
                "submit one currency per synthetic request"
            )

        # Check accounts exist and are selectable for postings.
        try:
            uri_or_path = self._validate_configured_book()
            book = self._open_piecash_book(uri_or_path)
            try:
                default_commodity = getattr(book, "default_currency", None)
                book_currency = str(
                    getattr(default_commodity, "mnemonic", default_commodity) or ""
                ).upper()
                if len(totals_by_currency) == 1:
                    split_currency = next(iter(totals_by_currency))
                    if (
                        book_currency
                        and book_currency != "XXX"
                        and split_currency != book_currency
                    ):
                        errors.append(
                            f"Currency {split_currency} does not match book default currency "
                            f"{book_currency}"
                        )

                requested_account_ids = self._distinct_account_ids(
                    (str(split.account_id) for split in request.splits),
                    max_accounts=50,
                )
                accounts_by_id = {
                    self._account_id(account): account
                    for account in self._accounts_by_ids(book, requested_account_ids)
                }
                amounts_by_account = {str(split.account_id): Decimal(str(split.amount)) for split in request.splits if re.fullmatch(DECIMAL_STRING_PATTERN, str(split.amount))}
                for split in request.splits:
                    account = accounts_by_id.get(str(split.account_id))
                    if account is None:
                        errors.append(f"Account not found: {split.account_id}")
                    elif str(getattr(account, "type", "") or "").upper() == "ROOT":
                        errors.append(
                            f"Account {split.account_id} is a root account and cannot receive postings"
                        )
                    elif bool(getattr(account, "placeholder", False)):
                        errors.append(
                            f"Account {split.account_id} is a placeholder account and cannot receive postings"
                        )
                    elif bool(getattr(account, "hidden", False)):
                        errors.append(
                            f"Account {split.account_id} is hidden and cannot receive postings"
                        )
                    else:
                        commodity = getattr(account, "commodity", None)
                        account_currency = str(getattr(commodity, "mnemonic", split.currency)).upper()
                        account_namespace = str(getattr(commodity, "namespace", "CURRENCY") or "").upper()
                        if account_namespace != "CURRENCY":
                            errors.append(
                                f"Account {split.account_id} commodity namespace {account_namespace} is not supported"
                            )
                        if account_currency and account_currency != split.currency.upper():
                            errors.append(
                                f"Currency {split.currency} does not match account {split.account_id} currency {account_currency}"
                            )
                        fraction = getattr(commodity, "fraction", None)
                        if fraction is not None:
                            try:
                                fraction_int = int(fraction)
                            except (TypeError, ValueError):
                                fraction_int = 0
                            amount = amounts_by_account.get(str(split.account_id))
                            if fraction_int <= 0:
                                errors.append(
                                    f"Account {split.account_id} commodity fraction is not supported"
                                )
                            elif amount is not None and (amount * Decimal(fraction_int)) != (amount * Decimal(fraction_int)).to_integral_value():
                                errors.append(
                                    f"Amount precision for account {split.account_id} exceeds commodity fraction {fraction_int}"
                                )
            finally:
                close = getattr(book, "close", None)
                if callable(close):
                    close()
        except Exception:
            errors.append(VALIDATION_ACCOUNT_READ_FAILURE_DETAIL)

        # Validate date format
        try:
            date.fromisoformat(request.date)
        except (ValueError, TypeError):
            errors.append(f"Invalid date format: {request.date}")

        valid = len(errors) == 0

        summary = {
            "date": request.date,
            "description": request.description,
            "split_count": len(request.splits),
            "currencies": list(totals_by_currency.keys()),
        }

        return TransactionValidationResultDTO(
            valid=valid,
            errors=errors,
            warnings=warnings,
            summary=summary,
        )

    def create_transaction(
        self,
        request: TransactionCreateRequestDTO,
        user_id: int,
        book_id: int,
        planned_transaction_guid: str | None = None,
        lock_key: str | None = None,
        pre_backup_hook: Callable[[], None] | None = None,
    ) -> TransactionWriteResultDTO:
        """Create a new transaction following the full write flow.

        Flow:
        1. Validate request
        2. Acquire per-book write lock
        3. Backup GnuCash book
        4. Open book for write
        5. Create transaction with splits
        6. Save
        7. Return result with transaction_id and backup_path
        """
        # Step 1: Validate
        validation = self.validate_transaction_create(request)
        if not validation.valid:
            raise GnuCashWriteError(
                f"Validation failed: {'; '.join(validation.errors)}"
            )

        book_key = lock_key or str(self.uri_or_path or book_id)
        backup_path = None

        # Step 2: Acquire lock (uses context manager for safe release)
        try:
            with write_lock_service.lock(book_key):
                # Step 3-7: Backup, open, write, save
                backup_path, transaction_id = self._execute_write_transaction(
                    request,
                    book_key,
                    planned_transaction_guid=planned_transaction_guid,
                    pre_backup_hook=pre_backup_hook,
                )
        except WriteLockError as exc:
            # If the error carries inspection info (stale vs active), include it
            if exc.inspection is not None and exc.inspection.status == "stale_released":
                raise WriteLockError(
                    book_key,
                    inspection=exc.inspection,
                ) from exc
            raise

        return TransactionWriteResultDTO(
            transaction_id=transaction_id,
            backup_path=backup_path or "",
            audit_log_id=None,
        )

    def _execute_write_transaction(
        self,
        request: TransactionCreateRequestDTO,
        book_key: str,
        *,
        planned_transaction_guid: str | None = None,
        pre_backup_hook: Callable[[], None] | None = None,
    ) -> tuple[str | None, str]:
        """Execute backup + write inside the lock (extracted for reuse)."""
        backup_path: str | None = None
        transaction_id: str = ""

        if pre_backup_hook is not None:
            pre_backup_hook()

        # Backup
        try:
            backup_path = create_book_backup(self.book_config)
        except BackupError as exc:
            raise GnuCashWriteError(f"Backup failed: {exc}") from exc

        # Open, write, save
        uri_or_path = self._validate_configured_book()
        book = None
        try:
            book = self._open_piecash_book_for_write(uri_or_path)
            sentinel = object()
            previous_planned_guid = getattr(self, "_planned_transaction_guid", sentinel)
            if planned_transaction_guid is not None:
                setattr(self, "_planned_transaction_guid", planned_transaction_guid)
            try:
                tx = self._do_create_transaction(book, request)
            finally:
                if previous_planned_guid is sentinel:
                    try:
                        delattr(self, "_planned_transaction_guid")
                    except AttributeError:
                        pass
                else:
                    setattr(self, "_planned_transaction_guid", previous_planned_guid)
            book.save()
            transaction_id = _guid(tx)
        except GnuCashWriteError as exc:
            if exc.backup_path is None:
                exc.backup_path = backup_path
            raise
        except Exception as exc:
            raise GnuCashWriteError(
                f"Write failed: {exc}", backup_path=backup_path
            ) from exc
        finally:
            if book is not None:
                close = getattr(book, "close", None)
                if callable(close):
                    close()

        return backup_path, transaction_id

    def _open_piecash_book_for_write(self, uri_or_path: str):
        """Open a piecash book in write mode for paths and SQL connection URIs."""
        disable_internal_backup = bool(
            _book_config_value(self.book_config, "disable_piecash_internal_backup", False)
        )
        if "://" in uri_or_path:
            if disable_internal_backup:
                return piecash.open_book(uri_conn=uri_or_path, readonly=False, do_backup=False)
            return piecash.open_book(uri_conn=uri_or_path, readonly=False)
        if disable_internal_backup:
            return piecash.open_book(uri_or_path, readonly=False, do_backup=False)
        return piecash.open_book(uri_or_path, readonly=False)

    def _do_create_transaction(
        self,
        book: Any,
        request: TransactionCreateRequestDTO,
        *,
        planned_transaction_guid: str | None = None,
    ) -> Any:
        """Create a transaction in an already-open writeable book.

        Uses piecash API to create a transaction with splits.
        """
        # Get the book's default currency
        commodity = book.default_currency
        currency_code = str(getattr(commodity, "mnemonic", "XXX"))

        # Parse date
        tx_date = date.fromisoformat(request.date)

        accounts_by_id = {
            self._account_id(account): account
            for account in self._accounts_by_ids(
                book,
                self._distinct_account_ids((str(split.account_id) for split in request.splits), max_accounts=50),
            )
        }

        # Create the transaction
        # piecash API: book.Transaction(commodity=commodity, currency=commodity, ...)
        transaction = piecash.Transaction(
            currency=commodity,
            description=request.description,
            post_date=tx_date,
            splits=[
                self._create_split(book, split, accounts_by_id=accounts_by_id)
                for split in request.splits
            ],
        )
        if planned_transaction_guid is None:
            planned_transaction_guid = getattr(self, "_planned_transaction_guid", None)
        if planned_transaction_guid and re.fullmatch(r"[0-9a-f]{32}", planned_transaction_guid):
            setattr(transaction, "guid", planned_transaction_guid)
        return transaction

    def _create_split(
        self,
        book: Any,
        split_dto: TransactionSplitWriteDTO,
        *,
        accounts_by_id: dict[str, Any] | None = None,
    ) -> Any:
        """Create a piecash Split for a transaction."""
        account = (accounts_by_id or {}).get(str(split_dto.account_id))
        if account is None and accounts_by_id is None:
            account = self._find_account(book, split_dto.account_id)
        if account is None:
            raise GnuCashWriteError(f"Account not found: {split_dto.account_id}")

        amount = Decimal(split_dto.amount)

        # piecash Split: account=account, value=amount, memo=memo
        return piecash.Split(
            account=account,
            value=amount,
            memo=split_dto.memo or "",
        )

    def validate_transaction_patch(
        self,
        transaction_id: str,
        request: TransactionPatchRequestDTO,
    ) -> TransactionValidationResultDTO:
        """Validate a transaction patch request."""
        errors: list[str] = []
        warnings: list[str] = []

        # Require at least one allowed field to avoid no-op writes.
        if request.description is None and request.split_memos is None:
            errors.append("At least one editable field is required")

        # Check transaction exists
        try:
            uri_or_path = self._validate_configured_book()
            book = self._open_piecash_book(uri_or_path)
            try:
                transaction = self._find_transaction(book, transaction_id)
                if transaction is None:
                    errors.append(f"Transaction not found: {transaction_id}")
                elif request.split_memos is not None:
                    split_ids = {_guid(split) for split in transaction.splits}
                    unknown_split_count = sum(
                        1
                        for split_id in request.split_memos
                        if split_id not in split_ids
                    )
                    if unknown_split_count:
                        errors.append(
                            "Unknown split memo target; split_memos may reference only "
                            "splits belonging to the target transaction"
                        )
            finally:
                close = getattr(book, "close", None)
                if callable(close):
                    close()
        except Exception as exc:
            errors.append(f"Could not validate transaction: {exc}")

        valid = len(errors) == 0
        return TransactionValidationResultDTO(
            valid=valid,
            errors=errors,
            warnings=warnings,
            summary={"transaction_id": transaction_id},
        )

    def patch_transaction_metadata(
        self,
        transaction_id: str,
        request: TransactionPatchRequestDTO,
        user_id: int,
        book_id: int,
    ) -> TransactionWriteResultDTO:
        """Patch description and/or split memos for an existing transaction.

        Does NOT allow editing dates, split amounts, accounts, split structure,
        or currencies.
        """
        # Step 1: Validate. Missing transactions are reported as 404 by the
        # route and must be detected before acquiring a lock or creating a
        # backup, so keep that case distinct from normal 422 validation errors.
        validation = self.validate_transaction_patch(transaction_id, request)
        if not validation.valid:
            if any(error == f"Transaction not found: {transaction_id}" for error in validation.errors):
                raise EntityNotFoundError("transaction", transaction_id)
            raise GnuCashWriteError(
                f"Validation failed: {'; '.join(validation.errors)}"
            )

        book_key = str(self.uri_or_path or book_id)
        backup_path = None

        # Step 2: Acquire lock (uses context manager for safe release)
        try:
            with write_lock_service.lock(book_key):
                backup_path = self._execute_patch_transaction(
                    transaction_id, request
                )
        except WriteLockError as exc:
            if exc.inspection is not None and exc.inspection.status == "stale_released":
                raise WriteLockError(
                    book_key,
                    inspection=exc.inspection,
                ) from exc
            raise

        return TransactionWriteResultDTO(
            transaction_id=transaction_id,
            backup_path=backup_path or "",
            audit_log_id=None,
        )

    def _execute_patch_transaction(
        self,
        transaction_id: str,
        request: TransactionPatchRequestDTO,
    ) -> str | None:
        """Execute backup + patch inside the lock (extracted for reuse)."""
        backup_path: str | None = None

        # Backup
        try:
            backup_path = create_book_backup(self.book_config)
        except BackupError as exc:
            raise GnuCashWriteError(f"Backup failed: {exc}") from exc

        # Open, patch, save
        uri_or_path = self._validate_configured_book()
        book = None
        try:
            book = self._open_piecash_book_for_write(uri_or_path)
            self._do_patch_transaction(book, transaction_id, request)
            book.save()
        except GnuCashWriteError as exc:
            if exc.backup_path is None:
                exc.backup_path = backup_path
            raise
        except Exception as exc:
            raise GnuCashWriteError(
                f"Write failed: {exc}", backup_path=backup_path
            ) from exc
        finally:
            if book is not None:
                close = getattr(book, "close", None)
                if callable(close):
                    close()

        return backup_path

    def _do_patch_transaction(
        self,
        book: Any,
        transaction_id: str,
        request: TransactionPatchRequestDTO,
    ) -> Any:
        """Patch an existing transaction in an already-open writeable book.

        This intentionally limits PATCH to transaction description and split memos;
        transaction dates, split accounts, split amounts, split structure, and
        currencies are not editable through write-alpha.
        """
        transaction = self._find_transaction(book, transaction_id)
        if transaction is None:
            raise EntityNotFoundError("transaction", transaction_id)

        if request.description is not None:
            transaction.description = request.description
        if request.split_memos is not None:
            for split in transaction.splits:
                split_guid = _guid(split)
                if split_guid in request.split_memos:
                    split.memo = request.split_memos[split_guid]

        return transaction

    def delete_transaction(
        self,
        transaction_id: str,
        user_id: int,
        book_id: int,
    ) -> TransactionWriteResultDTO:
        """Delete an existing transaction following the write-alpha safety flow."""
        # Missing transactions are reported before lock/backup/mutation so a
        # typo cannot create an unnecessary backup or lock contention. Corrupt
        # or unavailable disposable fixtures must also fail before lock/backup
        # with a path-safe write error instead of bubbling a raw piecash error.
        try:
            uri_or_path = self._validate_configured_book()
            read_book = self._open_piecash_book(uri_or_path)
            try:
                transaction = self._find_transaction(read_book, transaction_id)
                if transaction is None:
                    raise EntityNotFoundError("transaction", transaction_id)
            finally:
                close = getattr(read_book, "close", None)
                if callable(close):
                    close()
        except EntityNotFoundError:
            raise
        except (BookNotConfiguredError, BookNotFoundError, GnuCashReadError) as exc:
            raise GnuCashWriteError(
                "GnuCash write failed; check the configured disposable test book and backup evidence."
            ) from exc
        except Exception as exc:
            raise GnuCashWriteError(
                "GnuCash write failed; check the configured disposable test book and backup evidence."
            ) from exc

        book_key = str(self.uri_or_path or book_id)
        backup_path = None

        # Acquire lock (uses context manager for safe release)
        try:
            with write_lock_service.lock(book_key):
                backup_path = self._execute_delete_transaction(
                    transaction_id, uri_or_path
                )
        except WriteLockError as exc:
            if exc.inspection is not None and exc.inspection.status == "stale_released":
                raise WriteLockError(
                    book_key,
                    inspection=exc.inspection,
                ) from exc
            raise

        return TransactionWriteResultDTO(
            transaction_id=transaction_id,
            backup_path=backup_path or "",
            audit_log_id=None,
        )

    def _execute_delete_transaction(
        self,
        transaction_id: str,
        uri_or_path: str,
    ) -> str | None:
        """Execute backup + delete inside the lock (extracted for reuse)."""
        backup_path: str | None = None

        # Backup
        try:
            backup_path = create_book_backup(self.book_config)
        except BackupError as exc:
            raise GnuCashWriteError(f"Backup failed: {exc}") from exc

        # Open, delete, save
        book = None
        try:
            book = self._open_piecash_book_for_write(uri_or_path)
            self._do_delete_transaction(book, transaction_id)
            book.save()
        except GnuCashWriteError as exc:
            if exc.backup_path is None:
                exc.backup_path = backup_path
            raise
        except Exception as exc:
            raise GnuCashWriteError(
                f"Write failed: {exc}", backup_path=backup_path
            ) from exc
        finally:
            if book is not None:
                close = getattr(book, "close", None)
                if callable(close):
                    close()

        return backup_path

    def _do_delete_transaction(self, book: Any, transaction_id: str) -> None:
        """Delete one transaction from an already-open writeable book."""
        transaction = self._find_transaction(book, transaction_id)
        if transaction is None:
            raise EntityNotFoundError("transaction", transaction_id)
        delete = getattr(book, "delete", None)
        if not callable(delete):
            raise GnuCashWriteError("piecash book does not support delete")
        delete(transaction)
