import asyncio
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.market import MarketHistoryResponse, MarketOverviewResponse
from app.services.market import build_market_history, build_market_overview

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    session: Session = Depends(get_db_session),
) -> MarketOverviewResponse:
    return build_market_overview(session)


@router.get("/history", response_model=MarketHistoryResponse)
async def get_market_history(
    symbol: str,
    points: int = 48,
    session: Session = Depends(get_db_session),
) -> MarketHistoryResponse:
    normalized_points = max(8, min(points, 240))
    return build_market_history(session, symbol=symbol, points=normalized_points)


@router.get("/stream")
async def stream_market_overview(
    session: Session = Depends(get_db_session),
) -> StreamingResponse:
    async def event_generator():
        while True:
            overview = build_market_overview(session)
            payload = json.dumps(overview.model_dump())
            yield (
                f"id: {datetime.now(UTC).timestamp()}\n"
                "event: market_overview\n"
                f"data: {payload}\n\n"
            )
            await asyncio.sleep(15)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
