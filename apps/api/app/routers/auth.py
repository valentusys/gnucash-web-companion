"""Authentication router: login, current user, and logout."""

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_engine, get_session_factory
from app.models import User
from app.services.auth import (
    AuthConfigurationError,
    authenticate_user,
    create_access_token,
    decode_access_token,
    require_configured_jwt_secret,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def get_db() -> Generator[Session, None, None]:
    engine = get_engine()
    SessionLocal = get_session_factory(engine)
    with SessionLocal() as session:
        yield session


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        is_admin=bool(user.is_admin),
    )


async def get_current_user(
    request: Request,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        jwt_secret = require_configured_jwt_secret(settings.jwt_secret)
    except AuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    token = auth_header.split(" ", 1)[1]
    payload = decode_access_token(token, jwt_secret)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        ) from exc

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    user = authenticate_user(session, body.username, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    try:
        jwt_secret = require_configured_jwt_secret(settings.jwt_secret)
    except AuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    token = create_access_token(
        data={"sub": str(user.id)},
        secret=jwt_secret,
        expire_minutes=settings.jwt_token_expire_minutes,
    )
    return LoginResponse(access_token=token, user=_user_response(user))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(user)


@router.post("/logout")
def logout() -> dict[str, str]:
    # Stateless JWT logout is completed by the frontend deleting its httpOnly cookie.
    return {"status": "ok"}
