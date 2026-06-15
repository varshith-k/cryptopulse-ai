from datetime import datetime

from pydantic import BaseModel, Field


class NormalizedMarketEvent(BaseModel):
    source: str
    exchange_symbol: str
    base_symbol: str
    quote_symbol: str = Field(default="USD")
    price_usd: float
    percent_change_24h: float
    volume_24h: float | None = None
    market_cap: float | None = None
    event_type: str = "ticker"
    observed_at: datetime
