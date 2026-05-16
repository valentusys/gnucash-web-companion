"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, get_engine, get_session_factory
from app.routers.auth import router as auth_router
from app.services.seed import seed_default_book
from app.services.auth import seed_admin_user

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = get_session_factory(engine)
    with Session() as session:
        seed_default_book(session, settings.gnucash_default_book_path)
        seed_admin_user(session)
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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}
