from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.market import get_latest_market_rows, list_recent_ai_insights
from app.schemas.market import InsightCard, MarketOverviewItem, MarketOverviewResponse


def build_market_overview(session: Session) -> MarketOverviewResponse:
    rows = get_latest_market_rows(session)
    insights = list_recent_ai_insights(session)

    assets = []
    for asset, snapshot, indicator in rows:
        trend = (
            indicator.trend_summary
            if indicator and indicator.trend_summary
            else "Awaiting indicator output."
        )
        assets.append(
            MarketOverviewItem(
                symbol=asset.symbol,
                name=asset.name,
                price_usd=float(snapshot.price_usd),
                percent_change_24h=float(snapshot.percent_change_24h),
                volume_24h=float(snapshot.volume_24h)
                if snapshot.volume_24h is not None
                else None,
                market_cap=float(snapshot.market_cap)
                if snapshot.market_cap is not None
                else None,
                trend=trend,
                sma_20=float(indicator.sma_20)
                if indicator and indicator.sma_20 is not None
                else None,
                ema_20=float(indicator.ema_20)
                if indicator and indicator.ema_20 is not None
                else None,
                rsi_14=float(indicator.rsi_14)
                if indicator and indicator.rsi_14 is not None
                else None,
                macd=float(indicator.macd)
                if indicator and indicator.macd is not None
                else None,
                signal=float(indicator.signal)
                if indicator and indicator.signal is not None
                else None,
                rolling_volatility=float(indicator.rolling_volatility)
                if indicator and indicator.rolling_volatility is not None
                else None,
            )
        )

    insight_cards = [
        InsightCard(title=insight.title, content=insight.content) for insight in insights
    ]
    return MarketOverviewResponse(
        generated_at=datetime.now(UTC).isoformat(),
        assets=assets,
        insights=insight_cards,
    )
