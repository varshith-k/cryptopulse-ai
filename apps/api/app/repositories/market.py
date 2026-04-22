from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AIInsight, MarketSnapshot, TechnicalIndicator, WatchedAsset


def get_latest_market_rows(
    session: Session,
) -> list[tuple[WatchedAsset, MarketSnapshot, TechnicalIndicator | None]]:
    latest_snapshot_subquery = (
        select(
            MarketSnapshot.symbol.label("symbol"),
            func.max(MarketSnapshot.observed_at).label("latest_observed_at"),
        )
        .group_by(MarketSnapshot.symbol)
        .subquery()
    )

    latest_indicator_subquery = (
        select(
            TechnicalIndicator.symbol.label("symbol"),
            func.max(TechnicalIndicator.computed_at).label("latest_computed_at"),
        )
        .where(TechnicalIndicator.timeframe == "1d")
        .group_by(TechnicalIndicator.symbol)
        .subquery()
    )

    statement = (
        select(WatchedAsset, MarketSnapshot, TechnicalIndicator)
        .join(MarketSnapshot, MarketSnapshot.symbol == WatchedAsset.symbol)
        .join(
            latest_snapshot_subquery,
            (latest_snapshot_subquery.c.symbol == MarketSnapshot.symbol)
            & (
                latest_snapshot_subquery.c.latest_observed_at
                == MarketSnapshot.observed_at
            ),
        )
        .outerjoin(
            latest_indicator_subquery,
            latest_indicator_subquery.c.symbol == WatchedAsset.symbol,
        )
        .outerjoin(
            TechnicalIndicator,
            (TechnicalIndicator.symbol == WatchedAsset.symbol)
            & (
                TechnicalIndicator.computed_at
                == latest_indicator_subquery.c.latest_computed_at
            ),
        )
        .order_by(MarketSnapshot.percent_change_24h.desc())
    )
    return list(session.execute(statement).all())


def list_recent_ai_insights(session: Session, limit: int = 3) -> list[AIInsight]:
    statement = select(AIInsight).order_by(AIInsight.generated_at.desc()).limit(limit)
    return list(session.scalars(statement).all())


def get_market_history(
    session: Session,
    symbol: str,
    points: int = 48,
) -> list[MarketSnapshot]:
    statement = (
        select(MarketSnapshot)
        .where(MarketSnapshot.symbol == symbol.upper())
        .order_by(MarketSnapshot.observed_at.desc())
        .limit(points)
    )
    rows = list(session.scalars(statement).all())
    rows.reverse()
    return rows
