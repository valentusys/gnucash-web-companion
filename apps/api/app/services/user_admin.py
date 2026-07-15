"""Admin-only local app-user management service."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Literal

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, load_only

from app.models import AuditLog, Book, User, UserBookAccess
from app.schemas.users import (
    AdminBookAccessBookListResponse,
    AdminBookAccessBookOption,
    AdminUserAssignment,
    AdminUserAccessRole,
    AdminUserDetail,
    AdminUserListResponse,
    AdminUserPasswordResetResponse,
    AdminUserSafeCode,
    DisplayNameValidationError,
    PasswordPolicyError,
    UsernameValidationError,
    normalize_display_name,
    normalize_username,
    validate_password_policy,
)
from app.services.auth import hash_password

UserState = Literal["all", "enabled", "disabled"]


class UserAdminError(RuntimeError):
    """Controlled, fixed-detail admin-user API error."""

    def __init__(self, status_code: int, safe_code: AdminUserSafeCode) -> None:
        super().__init__(safe_code)
        self.status_code = status_code
        self.safe_code = safe_code


class UserAdminService:
    """Service-layer app metadata operations for local users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_users(self, *, limit: int, offset: int, state: str) -> AdminUserListResponse:
        safe_state = self._validate_state(state)
        base_query = self.session.query(User.id)
        base_query = self._apply_state_filter(base_query, safe_state)
        total_count = int(base_query.count())

        query = self._user_with_assignment_count_query()
        query = self._apply_state_filter(query, safe_state)
        rows = (
            query.order_by(User.username_normalized, User.id)
            .limit(limit)
            .offset(offset)
            .all()
        )
        assignments_by_user_id = self._assignments_by_user_ids(
            int(row[0].id) for row in rows
        )
        items = [
            self._detail_from_row(
                row,
                assignments_by_user_id.get(int(row[0].id), []),
            )
            for row in rows
        ]
        return AdminUserListResponse(
            items=items,
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_next=offset + len(items) < total_count,
        )

    def get_user_detail(self, *, subject_user_id: int) -> AdminUserDetail:
        row = self._get_user_row(subject_user_id)
        if row is None:
            raise UserAdminError(404, "user_not_found")
        assignments = self._assignments_by_user_ids([subject_user_id]).get(
            subject_user_id,
            [],
        )
        return self._detail_from_row(row, assignments)

    def list_book_options(
        self,
        *,
        limit: int,
        offset: int,
    ) -> AdminBookAccessBookListResponse:
        """Return bounded active book options without touching GnuCash sources."""

        active_filter = (Book.is_archived.is_(False), Book.is_enabled.is_(True))
        total_count = int(self.session.query(Book.id).filter(*active_filter).count())
        rows = (
            self.session.query(Book.id, Book.name, Book.is_default)
            .filter(*active_filter)
            .order_by(func.lower(Book.name), Book.id)
            .limit(limit)
            .offset(offset)
            .all()
        )
        items = [
            AdminBookAccessBookOption(
                id=int(book_id),
                name=str(book_name),
                is_default=bool(is_default),
            )
            for book_id, book_name, is_default in rows
        ]
        return AdminBookAccessBookListResponse(
            items=items,
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_next=offset + len(items) < total_count,
        )

    def set_book_access(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        book_id: int,
        role: AdminUserAccessRole | str = "viewer",
    ) -> AdminUserAssignment:
        """Grant or update one active book assignment idempotently."""

        safe_role = self._validate_access_role(role)
        return self._set_book_access_transaction(
            actor_user_id=actor_user_id,
            subject_user_id=subject_user_id,
            book_id=book_id,
            role=safe_role,
            retry_on_integrity=True,
        )

    def delete_book_access(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        book_id: int,
    ) -> None:
        """Revoke one book assignment; missing/repeated revokes are 204/no-audit."""

        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            if self._get_user_locked(subject_user_id) is None:
                raise UserAdminError(404, "user_not_found")
            access = self._get_access(subject_user_id=subject_user_id, book_id=book_id)
            if access is not None:
                self.session.delete(access)
                self._audit_book_access(
                    actor_user_id=actor_user_id,
                    subject_user_id=subject_user_id,
                    book_id=book_id,
                    action="book_access_revoked",
                    changed_fields=["book_access"],
                    result="revoked",
                )
                self.session.flush()
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def create_user(
        self,
        *,
        actor_user_id: int,
        username: str,
        display_name: str,
        password: str,
        is_admin: bool = False,
    ) -> AdminUserDetail:
        username_normalized = self._normalize_username(username)
        display_name_normalized = self._normalize_display_name(display_name)
        self._validate_password(password, username_normalized)
        try:
            password_hash = hash_password(password)
        except PasswordPolicyError as exc:
            raise UserAdminError(422, "password_policy") from exc

        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = User(
                username=username_normalized,
                username_normalized=username_normalized,
                display_name=display_name_normalized,
                password_hash=password_hash,
                is_admin=bool(is_admin),
                is_enabled=True,
                auth_version=1,
            )
            self.session.add(user)
            self.session.flush()
            self._audit(
                actor_user_id=actor_user_id,
                subject_user_id=int(user.id),
                action="user_created",
                changed_fields=["identity", "display_name", "role", "status", "credentials"],
                result="created",
            )
            detail = self.get_user_detail(subject_user_id=int(user.id))
            self.session.commit()
            return detail
        except IntegrityError as exc:
            self.session.rollback()
            raise UserAdminError(409, "username_taken") from exc
        except Exception:
            self.session.rollback()
            raise

    def update_display_name(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        display_name: str,
    ) -> AdminUserDetail:
        display_name_normalized = self._normalize_display_name(display_name)
        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = self._get_user_locked(subject_user_id)
            if user is None:
                raise UserAdminError(404, "user_not_found")
            if user.display_name != display_name_normalized:
                user.display_name = display_name_normalized
                self._audit(
                    actor_user_id=actor_user_id,
                    subject_user_id=subject_user_id,
                    action="display_name_changed",
                    changed_fields=["display_name"],
                    result="changed",
                )
                self.session.flush()
            detail = self.get_user_detail(subject_user_id=subject_user_id)
            self.session.commit()
            return detail
        except Exception:
            self.session.rollback()
            raise

    def enable_user(self, *, actor_user_id: int, subject_user_id: int) -> AdminUserDetail:
        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = self._get_user_locked(subject_user_id)
            if user is None:
                raise UserAdminError(404, "user_not_found")
            if not bool(user.is_enabled):
                user.is_enabled = True
                self._audit(
                    actor_user_id=actor_user_id,
                    subject_user_id=subject_user_id,
                    action="user_enabled",
                    changed_fields=["status"],
                    result="enabled",
                )
                self.session.flush()
            detail = self.get_user_detail(subject_user_id=subject_user_id)
            self.session.commit()
            return detail
        except Exception:
            self.session.rollback()
            raise

    def disable_user(self, *, actor_user_id: int, subject_user_id: int) -> AdminUserDetail:
        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = self._get_user_locked(subject_user_id)
            if user is None:
                raise UserAdminError(404, "user_not_found")
            if not bool(user.is_enabled):
                detail = self.get_user_detail(subject_user_id=subject_user_id)
                self.session.commit()
                return detail
            if bool(user.is_admin):
                enabled_admin_count = int(
                    self.session.query(func.count(User.id))
                    .filter(User.is_admin.is_(True), User.is_enabled.is_(True))
                    .scalar()
                    or 0
                )
                if enabled_admin_count <= 1:
                    raise UserAdminError(409, "last_enabled_admin")
            if subject_user_id == actor_user_id:
                raise UserAdminError(409, "self_disable_forbidden")
            user.is_enabled = False
            user.auth_version = int(user.auth_version) + 1
            self._audit(
                actor_user_id=actor_user_id,
                subject_user_id=subject_user_id,
                action="user_disabled",
                changed_fields=["status", "session_version"],
                result="disabled",
            )
            self.session.flush()
            detail = self.get_user_detail(subject_user_id=subject_user_id)
            self.session.commit()
            return detail
        except Exception:
            self.session.rollback()
            raise

    def reset_password(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        new_password: str,
    ) -> AdminUserPasswordResetResponse:
        username_normalized = self._get_username_normalized(subject_user_id)
        if username_normalized is None:
            raise UserAdminError(404, "user_not_found")
        self._validate_password(new_password, username_normalized)
        try:
            password_hash = hash_password(new_password)
        except PasswordPolicyError as exc:
            raise UserAdminError(422, "password_policy") from exc

        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = self._get_user_locked(subject_user_id)
            if user is None:
                raise UserAdminError(404, "user_not_found")
            user.password_hash = password_hash
            user.auth_version = int(user.auth_version) + 1
            self._audit(
                actor_user_id=actor_user_id,
                subject_user_id=subject_user_id,
                action="password_reset",
                changed_fields=["credentials", "session_version"],
                result="reset",
            )
            self.session.flush()
            self.session.commit()
            return AdminUserPasswordResetResponse(subject_user_id=subject_user_id)
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _validate_state(state: str) -> UserState:
        if state not in {"all", "enabled", "disabled"}:
            raise UserAdminError(422, "invalid_state")
        return state  # type: ignore[return-value]

    @staticmethod
    def _normalize_username(username: str) -> str:
        try:
            return normalize_username(username)
        except UsernameValidationError as exc:
            raise UserAdminError(422, "username_invalid") from exc

    @staticmethod
    def _normalize_display_name(display_name: str) -> str:
        try:
            return normalize_display_name(display_name)
        except DisplayNameValidationError as exc:
            raise UserAdminError(422, "display_name_invalid") from exc

    @staticmethod
    def _validate_password(password: str, username_normalized: str) -> None:
        try:
            validate_password_policy(password, username_normalized)
        except PasswordPolicyError as exc:
            raise UserAdminError(422, "password_policy") from exc

    @staticmethod
    def _validate_access_role(role: AdminUserAccessRole | str) -> AdminUserAccessRole:
        if role not in {"owner", "editor", "viewer"}:
            raise UserAdminError(422, "invalid_state")
        return role  # type: ignore[return-value]

    def _set_book_access_transaction(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        book_id: int,
        role: AdminUserAccessRole,
        retry_on_integrity: bool,
    ) -> AdminUserAssignment:
        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            if self._get_user_locked(subject_user_id) is None:
                raise UserAdminError(404, "user_not_found")
            book = self._get_active_book(book_id)
            if book is None:
                raise UserAdminError(404, "book_not_found")

            access = self._get_access(subject_user_id=subject_user_id, book_id=book_id)
            if access is None:
                access = UserBookAccess(user_id=subject_user_id, book_id=book_id, role=role)
                self.session.add(access)
                try:
                    self.session.flush()
                except IntegrityError:
                    self.session.rollback()
                    if retry_on_integrity:
                        return self._set_book_access_transaction(
                            actor_user_id=actor_user_id,
                            subject_user_id=subject_user_id,
                            book_id=book_id,
                            role=role,
                            retry_on_integrity=False,
                        )
                    raise
                self._audit_book_access(
                    actor_user_id=actor_user_id,
                    subject_user_id=subject_user_id,
                    book_id=book_id,
                    action="book_access_granted",
                    changed_fields=["book_access", "role"],
                    result="granted",
                    role=role,
                )
            elif access.role != role:
                access.role = role
                self.session.flush()
                self._audit_book_access(
                    actor_user_id=actor_user_id,
                    subject_user_id=subject_user_id,
                    book_id=book_id,
                    action="book_access_role_changed",
                    changed_fields=["role"],
                    result="changed",
                    role=role,
                )

            assignment = self._assignment_from_book(book, role=access.role)
            self.session.commit()
            return assignment
        except Exception:
            self.session.rollback()
            raise

    def _get_active_book(self, book_id: int) -> Book | None:
        return (
            self.session.query(Book)
            .filter(
                Book.id == book_id,
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .first()
        )

    def _get_access(self, *, subject_user_id: int, book_id: int) -> UserBookAccess | None:
        return (
            self.session.query(UserBookAccess)
            .filter(
                UserBookAccess.user_id == subject_user_id,
                UserBookAccess.book_id == book_id,
            )
            .first()
        )

    @staticmethod
    def _assignment_from_book(book: Book, *, role: str) -> AdminUserAssignment:
        return AdminUserAssignment(
            book_id=int(book.id),
            book_name=str(book.name),
            is_default=bool(book.is_default),
            role=role,  # type: ignore[arg-type]
        )

    def _begin_immediate(self) -> None:
        bind = self.session.get_bind()
        if self.session.in_transaction():
            self.session.rollback()
        if bind.dialect.name == "sqlite":
            self.session.execute(text("BEGIN IMMEDIATE"))
        else:
            self.session.begin()

    def _require_actor_admin_locked(self, actor_user_id: int) -> User:
        actor = self._get_user_locked(actor_user_id)
        if actor is None or not bool(actor.is_enabled) or not bool(actor.is_admin):
            raise UserAdminError(403, "admin_required")
        return actor

    def _get_user_locked(self, subject_user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == subject_user_id).first()

    def _get_user_row(self, subject_user_id: int):
        return (
            self._user_with_assignment_count_query()
            .filter(User.id == subject_user_id)
            .first()
        )

    def _get_username_normalized(self, subject_user_id: int) -> str | None:
        row = (
            self.session.query(User.username_normalized)
            .filter(User.id == subject_user_id)
            .first()
        )
        if row is None:
            return None
        return str(row[0])

    def _user_with_assignment_count_query(self):
        assignment_counts = (
            self.session.query(
                UserBookAccess.user_id.label("user_id"),
                func.count(UserBookAccess.book_id).label("assignment_count"),
            )
            .join(Book, UserBookAccess.book_id == Book.id)
            .filter(Book.is_archived.is_(False), Book.is_enabled.is_(True))
            .group_by(UserBookAccess.user_id)
            .subquery()
        )
        return self.session.query(
            User,
            func.coalesce(assignment_counts.c.assignment_count, 0).label("assignment_count"),
        ).options(
            load_only(
                User.id,
                User.username,
                User.display_name,
                User.is_admin,
                User.is_enabled,
                User.created_at,
                User.updated_at,
            )
        ).outerjoin(assignment_counts, User.id == assignment_counts.c.user_id)

    def _assignments_by_user_ids(
        self,
        user_ids: Iterable[int],
    ) -> dict[int, list[AdminUserAssignment]]:
        ids = sorted({int(user_id) for user_id in user_ids})
        if not ids:
            return {}

        rows = (
            self.session.query(
                UserBookAccess.user_id,
                UserBookAccess.book_id,
                Book.name,
                Book.is_default,
                UserBookAccess.role,
            )
            .join(Book, UserBookAccess.book_id == Book.id)
            .filter(
                UserBookAccess.user_id.in_(ids),
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .order_by(UserBookAccess.user_id, func.lower(Book.name), Book.id)
            .all()
        )

        assignments_by_user_id: dict[int, list[AdminUserAssignment]] = {
            user_id: [] for user_id in ids
        }
        for user_id, book_id, book_name, is_default, role in rows:
            assignments_by_user_id[int(user_id)].append(
                AdminUserAssignment(
                    book_id=int(book_id),
                    book_name=str(book_name),
                    is_default=bool(is_default),
                    role=role,
                )
            )
        return assignments_by_user_id

    @staticmethod
    def _apply_state_filter(query, state: UserState):
        if state == "enabled":
            return query.filter(User.is_enabled.is_(True))
        if state == "disabled":
            return query.filter(User.is_enabled.is_(False))
        return query

    @staticmethod
    def _detail_from_row(
        row,
        assignments: list[AdminUserAssignment],
    ) -> AdminUserDetail:
        user = row[0]
        assignment_count = row[1]
        return AdminUserDetail(
            id=int(user.id),
            username=str(user.username),
            display_name=str(user.display_name),
            is_admin=bool(user.is_admin),
            is_enabled=bool(user.is_enabled),
            assignment_count=int(assignment_count or 0),
            assignments=list(assignments),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _audit(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        action: str,
        changed_fields: list[str],
        result: str,
    ) -> None:
        payload = {
            "subject_user_id": int(subject_user_id),
            "changed_fields": list(changed_fields),
            "result": result,
        }
        self.session.add(
            AuditLog(
                user_id=int(actor_user_id),
                book_id=None,
                action=action,
                payload_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
            )
        )

    def _audit_book_access(
        self,
        *,
        actor_user_id: int,
        subject_user_id: int,
        book_id: int,
        action: str,
        changed_fields: list[str],
        result: str,
        role: str | None = None,
    ) -> None:
        payload: dict[str, object] = {
            "subject_user_id": int(subject_user_id),
            "book_id": int(book_id),
            "changed_fields": list(changed_fields),
            "result": result,
        }
        if role is not None:
            payload["role"] = role
        self.session.add(
            AuditLog(
                user_id=int(actor_user_id),
                book_id=int(book_id),
                action=action,
                payload_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
            )
        )
