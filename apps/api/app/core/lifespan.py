from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed_reference_data
from app.db.session import SessionLocal, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_reference_data(
            session,
            include_demo_user=settings.seed_demo_user,
            include_demo_alerts=settings.seed_demo_alerts,
        )
    yield
