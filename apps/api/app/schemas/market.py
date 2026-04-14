from pydantic import BaseModel


class MarketSnapshot(BaseModel):
    symbol: str
    name: str
    price_usd: float
    percent_change_24h: float
    trend: str


class IndicatorSnapshot(BaseModel):
    symbol: str
    timeframe: str
    sma_20: float | None = None
    ema_20: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    signal: float | None = None
    rolling_volatility: float | None = None
    trend_summary: str | None = None


class InsightCard(BaseModel):
    title: str
    content: str


class DashboardOverview(BaseModel):
    snapshots: list[MarketSnapshot]
    insights: list[InsightCard]


class MarketOverviewItem(BaseModel):
    symbol: str
    name: str
    price_usd: float
    percent_change_24h: float
    volume_24h: float | None = None
    market_cap: float | None = None
    trend: str
    sma_20: float | None = None
    ema_20: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    signal: float | None = None
    rolling_volatility: float | None = None


class MarketOverviewResponse(BaseModel):
    generated_at: str
    assets: list[MarketOverviewItem]
    insights: list[InsightCard]
