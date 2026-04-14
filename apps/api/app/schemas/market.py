from pydantic import BaseModel


class MarketSnapshot(BaseModel):
    symbol: str
    name: str
    price_usd: float
    percent_change_24h: float
    trend: str


class InsightCard(BaseModel):
    title: str
    content: str


class DashboardOverview(BaseModel):
    snapshots: list[MarketSnapshot]
    insights: list[InsightCard]

