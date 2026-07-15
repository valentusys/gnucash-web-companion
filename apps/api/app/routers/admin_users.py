"""Admin-only local user management API."""

from __future__ import annotations

from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models import User
from app.routers.auth import get_current_user, get_db
from app.schemas.users import (
    AdminUserCreateRequest,
    AdminUserDetail,
    AdminUserListResponse,
    AdminUserPasswordResetRequest,
    AdminUserPatchRequest,
)
from app.services.user_admin import UserAdminError, UserAdminService

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


def _require_admin(user: User) -> int:
    if not bool(user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return int(user.id)


def _raise_user_admin_error(exc: UserAdminError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("", response_model=AdminUserListResponse)
def list_admin_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    state: str = Query(default="all"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserListResponse:
    _require_admin(user)
    try:
        return UserAdminService(session).list_users(limit=limit, offset=offset, state=state)
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.post("", response_model=AdminUserDetail, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    body: AdminUserCreateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    actor_user_id = _require_admin(user)
    try:
        return UserAdminService(session).create_user(
            actor_user_id=actor_user_id,
            username=body.username,
            display_name=body.display_name,
            password=body.password,
            is_admin=body.is_admin,
        )
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.get("/{subject_user_id}", response_model=AdminUserDetail)
def get_admin_user(
    subject_user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    _require_admin(user)
    try:
        return UserAdminService(session).get_user_detail(subject_user_id=subject_user_id)
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.patch("/{subject_user_id}", response_model=AdminUserDetail)
def patch_admin_user(
    subject_user_id: int,
    body: AdminUserPatchRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    actor_user_id = _require_admin(user)
    try:
        return UserAdminService(session).update_display_name(
            actor_user_id=actor_user_id,
            subject_user_id=subject_user_id,
            display_name=body.display_name,
        )
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.post("/{subject_user_id}/enable", response_model=AdminUserDetail)
def enable_admin_user(
    subject_user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    actor_user_id = _require_admin(user)
    try:
        return UserAdminService(session).enable_user(
            actor_user_id=actor_user_id,
            subject_user_id=subject_user_id,
        )
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.post("/{subject_user_id}/disable", response_model=AdminUserDetail)
def disable_admin_user(
    subject_user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    actor_user_id = _require_admin(user)
    try:
        return UserAdminService(session).disable_user(
            actor_user_id=actor_user_id,
            subject_user_id=subject_user_id,
        )
    except UserAdminError as exc:
        _raise_user_admin_error(exc)


@router.post("/{subject_user_id}/password-reset", response_model=AdminUserDetail)
def reset_admin_user_password(
    subject_user_id: int,
    body: AdminUserPasswordResetRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AdminUserDetail:
    actor_user_id = _require_admin(user)
    try:
        return UserAdminService(session).reset_password(
            actor_user_id=actor_user_id,
            subject_user_id=subject_user_id,
            new_password=body.new_password,
        )
    except UserAdminError as exc:
        _raise_user_admin_error(exc)
