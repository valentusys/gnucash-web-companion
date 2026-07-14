"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, get_engine, get_session_factory
from app.diagnostics import build_health_payload, log_startup_diagnostics
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.accounts import router as accounts_router
from app.routers.transactions import router as transactions_router
from app.routers.owner_writebeta import router as owner_writebeta_router
from app.routers.scheduled_transactions import router as scheduled_transactions_router
from app.routers.reports import router as reports_router
from app.services.seed import seed_admin_default_book_access, seed_default_book
from app.services.auth import seed_admin_user
from app.services.metadata_migrations import run_app_metadata_migrations

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    current_settings = get_settings()
    engine = get_engine()
    Base.metadata.create_all(engine)
    run_app_metadata_migrations(engine, current_settings)
    log_startup_diagnostics(current_settings, engine)
    Session = get_session_factory(engine)
    with Session() as session:
        seed_default_book(session, current_settings.gnucash_default_book_path)
        seed_admin_user(session)
        seed_admin_default_book_access(session)
    yield


app = FastAPI(title="gnucash-web-companion API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(owner_writebeta_router)
app.include_router(scheduled_transactions_router)
app.include_router(reports_router)


def _redacted_validation_errors(exc: RequestValidationError) -> list[dict[str, object]]:
    """Return FastAPI validation errors without echoing private request values."""

    redacted: list[dict[str, object]] = []
    for error in exc.errors():
        item = {key: value for key, value in error.items() if key != "input"}
        ctx = item.get("ctx")
        if isinstance(ctx, dict):
            safe_ctx = {
                key: value
                for key, value in ctx.items()
                if isinstance(value, (bool, int, float)) or value is None
            }
            if safe_ctx:
                item["ctx"] = safe_ctx
            else:
                item.pop("ctx", None)
        redacted.append(item)
    return redacted


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": _redacted_validation_errors(exc)})


@app.get("/health")
async def health() -> dict[str, object]:
    return build_health_payload(get_settings(), get_engine())
