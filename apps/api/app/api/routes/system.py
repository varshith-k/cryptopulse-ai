from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.observability import metrics
from app.db.session import get_db_session


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/ready")
async def readiness_check(
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    session.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "timestamp": datetime.now(UTC).isoformat(),
        "dependencies": {
            "database": "ok",
        },
    }


@router.get("/metrics")
async def get_metrics() -> dict[str, object]:
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        **metrics.snapshot(),
    }
