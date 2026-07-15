"""Admin-only local app-user management service."""

from __future__ import annotations

import json
from typing import Literal

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, load_only

from app.models import AuditLog, User, UserBookAccess
from app.schemas.users import (
    AdminUserDetail,
    AdminUserListResponse,
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

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


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
        items = [self._detail_from_row(row) for row in rows]
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
            raise UserAdminError(404, "User not found")
        return self._detail_from_row(row)

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
        password_hash = hash_password(password)

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
            raise UserAdminError(409, "Username already exists") from exc
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
                raise UserAdminError(404, "User not found")
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
                raise UserAdminError(404, "User not found")
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
                raise UserAdminError(404, "User not found")
            if not bool(user.is_enabled):
                detail = self.get_user_detail(subject_user_id=subject_user_id)
                self.session.commit()
                return detail
            if subject_user_id == actor_user_id:
                raise UserAdminError(409, "Cannot disable the current admin user")
            if bool(user.is_admin):
                enabled_admin_count = int(
                    self.session.query(func.count(User.id))
                    .filter(User.is_admin.is_(True), User.is_enabled.is_(True))
                    .scalar()
                    or 0
                )
                if enabled_admin_count <= 1:
                    raise UserAdminError(409, "At least one enabled admin user is required")
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
    ) -> AdminUserDetail:
        self._begin_immediate()
        try:
            self._require_actor_admin_locked(actor_user_id)
            user = self._get_user_locked(subject_user_id)
            if user is None:
                raise UserAdminError(404, "User not found")
            self._validate_password(new_password, str(user.username_normalized))
            user.password_hash = hash_password(new_password)
            user.auth_version = int(user.auth_version) + 1
            self._audit(
                actor_user_id=actor_user_id,
                subject_user_id=subject_user_id,
                action="password_reset",
                changed_fields=["credentials", "session_version"],
                result="reset",
            )
            self.session.flush()
            detail = self.get_user_detail(subject_user_id=subject_user_id)
            self.session.commit()
            return detail
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _validate_state(state: str) -> UserState:
        if state not in {"all", "enabled", "disabled"}:
            raise UserAdminError(422, "Invalid state")
        return state  # type: ignore[return-value]

    @staticmethod
    def _normalize_username(username: str) -> str:
        try:
            return normalize_username(username)
        except UsernameValidationError as exc:
            raise UserAdminError(422, "Invalid username") from exc

    @staticmethod
    def _normalize_display_name(display_name: str) -> str:
        try:
            return normalize_display_name(display_name)
        except DisplayNameValidationError as exc:
            raise UserAdminError(422, "Invalid display name") from exc

    @staticmethod
    def _validate_password(password: str, username_normalized: str) -> None:
        try:
            validate_password_policy(password, username_normalized)
        except PasswordPolicyError as exc:
            raise UserAdminError(422, "Password does not satisfy policy") from exc

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
            raise UserAdminError(403, "Admin privileges required")
        return actor

    def _get_user_locked(self, subject_user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == subject_user_id).first()

    def _get_user_row(self, subject_user_id: int):
        return (
            self._user_with_assignment_count_query()
            .filter(User.id == subject_user_id)
            .first()
        )

    def _user_with_assignment_count_query(self):
        assignment_counts = (
            self.session.query(
                UserBookAccess.user_id.label("user_id"),
                func.count(UserBookAccess.book_id).label("assignment_count"),
            )
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

    @staticmethod
    def _apply_state_filter(query, state: UserState):
        if state == "enabled":
            return query.filter(User.is_enabled.is_(True))
        if state == "disabled":
            return query.filter(User.is_enabled.is_(False))
        return query

    @staticmethod
    def _detail_from_row(row) -> AdminUserDetail:
        user = row[0]
        assignment_count = row[1]
        return AdminUserDetail(
            id=int(user.id),
            username=str(user.username),
            display_name=str(user.display_name),
            is_admin=bool(user.is_admin),
            is_enabled=bool(user.is_enabled),
            assignment_count=int(assignment_count or 0),
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
