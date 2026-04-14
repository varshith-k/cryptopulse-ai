from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import (
    AIInsight,
    MarketSnapshot,
    TechnicalIndicator,
    User,
    UserAlert,
    WatchedAsset,
)


def seed_reference_data(
    session: Session,
    include_demo_user: bool = False,
    include_demo_alerts: bool = False,
) -> None:
    assets = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("SOL", "Solana"),
        ("ADA", "Cardano"),
    ]
    for symbol, name in assets:
        if session.get(WatchedAsset, symbol) is None:
            session.add(WatchedAsset(symbol=symbol, name=name, market="crypto"))
    session.flush()

    demo_user = None
    if include_demo_user:
        demo_user = session.scalar(select(User).where(User.email == "demo@cryptopulse.ai"))
        if demo_user is None:
            demo_user = User(
                email="demo@cryptopulse.ai",
                hashed_password=hash_password("DemoPass123!"),
            )
            session.add(demo_user)
            session.flush()

    has_snapshots = session.scalar(select(MarketSnapshot.id).limit(1))
    if has_snapshots is None:
        now = datetime.now(UTC)
        session.add_all(
            [
                MarketSnapshot(
                    symbol="BTC",
                    price_usd=Decimal("68420.55"),
                    percent_change_24h=Decimal("2.8400"),
                    volume_24h=Decimal("28100000000.00"),
                    market_cap=Decimal("1340000000000.00"),
                    observed_at=now,
                ),
                MarketSnapshot(
                    symbol="ETH",
                    price_usd=Decimal("3521.18"),
                    percent_change_24h=Decimal("1.9100"),
                    volume_24h=Decimal("14900000000.00"),
                    market_cap=Decimal("423000000000.00"),
                    observed_at=now - timedelta(minutes=1),
                ),
                MarketSnapshot(
                    symbol="SOL",
                    price_usd=Decimal("162.74"),
                    percent_change_24h=Decimal("4.3300"),
                    volume_24h=Decimal("3800000000.00"),
                    market_cap=Decimal("71000000000.00"),
                    observed_at=now - timedelta(minutes=2),
                ),
                MarketSnapshot(
                    symbol="ADA",
                    price_usd=Decimal("0.61"),
                    percent_change_24h=Decimal("-1.2400"),
                    volume_24h=Decimal("590000000.00"),
                    market_cap=Decimal("21700000000.00"),
                    observed_at=now - timedelta(minutes=3),
                ),
            ]
        )

    has_indicators = session.scalar(select(TechnicalIndicator.id).limit(1))
    if has_indicators is None:
        session.add_all(
            [
                TechnicalIndicator(
                    symbol="BTC",
                    timeframe="1d",
                    sma_20=Decimal("66120.11"),
                    ema_20=Decimal("66941.24"),
                    rsi_14=Decimal("62.40"),
                    macd=Decimal("218.55"),
                    signal=Decimal("184.03"),
                    rolling_volatility=Decimal("1.92"),
                    trend_summary="BTC is trading above its 20-day averages with constructive momentum.",
                ),
                TechnicalIndicator(
                    symbol="ETH",
                    timeframe="1d",
                    sma_20=Decimal("3440.10"),
                    ema_20=Decimal("3472.87"),
                    rsi_14=Decimal("58.20"),
                    macd=Decimal("16.83"),
                    signal=Decimal("13.70"),
                    rolling_volatility=Decimal("2.11"),
                    trend_summary="ETH remains constructive but is not accelerating as quickly as SOL.",
                ),
                TechnicalIndicator(
                    symbol="SOL",
                    timeframe="1d",
                    sma_20=Decimal("149.60"),
                    ema_20=Decimal("153.42"),
                    rsi_14=Decimal("68.90"),
                    macd=Decimal("7.16"),
                    signal=Decimal("5.02"),
                    rolling_volatility=Decimal("3.40"),
                    trend_summary="SOL is showing the strongest relative momentum in the seeded fallback dataset.",
                ),
                TechnicalIndicator(
                    symbol="ADA",
                    timeframe="1d",
                    sma_20=Decimal("0.64"),
                    ema_20=Decimal("0.63"),
                    rsi_14=Decimal("42.70"),
                    macd=Decimal("-0.01"),
                    signal=Decimal("0.00"),
                    rolling_volatility=Decimal("2.80"),
                    trend_summary="ADA is lagging with softer momentum and mild downside pressure.",
                ),
            ]
        )

    has_insights = session.scalar(select(AIInsight.id).limit(1))
    if has_insights is None:
        session.add_all(
            [
                AIInsight(
                    symbol="BTC",
                    insight_type="daily_summary",
                    title="BTC holds constructive momentum",
                    content="Bitcoin is holding above short-term trend support with stable volatility.",
                    confidence=Decimal("0.84"),
                ),
                AIInsight(
                    symbol="SOL",
                    insight_type="anomaly_watch",
                    title="SOL volatility elevated",
                    content="Solana is showing unusually strong upside momentum relative to its peers.",
                    confidence=Decimal("0.78"),
                ),
            ]
        )

    has_alerts = session.scalar(select(UserAlert.id).limit(1))
    if has_alerts is None and include_demo_alerts and demo_user is not None:
        session.add(
            UserAlert(
                user_id=demo_user.id,
                symbol="BTC",
                alert_type="price_above",
                threshold=Decimal("70000.00"),
                is_active=True,
            )
        )

    session.commit()
