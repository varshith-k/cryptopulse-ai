from datetime import UTC, datetime

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


def pair_to_base_symbol(pair: str) -> str:
    pair = pair.upper()
    suffixes = ("USDT", "USD", "BUSD", "USDC")
    for suffix in suffixes:
        if pair.endswith(suffix):
            return pair[: -len(suffix)]
    return pair


def build_binance_event(payload: dict) -> NormalizedMarketEvent:
    symbol = payload["s"].upper()
    return NormalizedMarketEvent(
        source="binance",
        exchange_symbol=symbol,
        base_symbol=pair_to_base_symbol(symbol),
        quote_symbol="USD",
        price_usd=float(payload["c"]),
        percent_change_24h=float(payload["P"]),
        volume_24h=float(payload["q"]),
        observed_at=datetime.now(UTC),
    )
