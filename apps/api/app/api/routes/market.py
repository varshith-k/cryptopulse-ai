from fastapi import APIRouter

from app.schemas.market import DashboardOverview, InsightCard, MarketSnapshot

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/overview", response_model=DashboardOverview)
async def get_market_overview() -> DashboardOverview:
    snapshots = [
        MarketSnapshot(
            symbol="BTC",
            name="Bitcoin",
            price_usd=68420.55,
            percent_change_24h=2.84,
            trend="Bullish",
        ),
        MarketSnapshot(
            symbol="ETH",
            name="Ethereum",
            price_usd=3521.18,
            percent_change_24h=1.91,
            trend="Constructive",
        ),
        MarketSnapshot(
            symbol="SOL",
            name="Solana",
            price_usd=162.74,
            percent_change_24h=4.33,
            trend="Momentum breakout",
        ),
    ]
    insights = [
        InsightCard(
            title="Momentum leaders",
            content="SOL and BTC are leading the 24h move, with strength supported by positive price change.",
        ),
        InsightCard(
            title="Watchlist candidate",
            content="ETH is trending upward more slowly and may deserve a volume confirmation check.",
        ),
    ]
    return DashboardOverview(snapshots=snapshots, insights=insights)

