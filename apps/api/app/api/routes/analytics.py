from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.analytics import (
    AnomalyResponse,
    RealtimeAnomalyResponse,
    SummaryResponse,
)
from app.services.analytics import (
    detect_market_anomalies,
    generate_market_summary,
    list_realtime_anomalies,
    recommend_metrics,
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/anomalies", response_model=AnomalyResponse)
async def get_market_anomalies(
    session: Session = Depends(get_db_session),
) -> AnomalyResponse:
    return detect_market_anomalies(session)


@router.get("/summary", response_model=SummaryResponse)
async def get_market_summary(
    scope: str = Query(default="market"),
    session: Session = Depends(get_db_session),
) -> SummaryResponse:
    return generate_market_summary(session, scope=scope)


@router.get("/recommendations", response_model=list[str])
async def get_metric_recommendations(
    session: Session = Depends(get_db_session),
) -> list[str]:
    return recommend_metrics(session)


@router.get("/realtime-anomalies", response_model=RealtimeAnomalyResponse)
async def get_realtime_anomalies(
    limit: int = Query(default=12, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> RealtimeAnomalyResponse:
    return list_realtime_anomalies(session, limit=limit)
