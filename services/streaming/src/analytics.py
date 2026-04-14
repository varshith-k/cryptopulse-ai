from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import stdev

import httpx

from src.config import settings
from src.schema import NormalizedMarketEvent


COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
}


@dataclass
class ComputedIndicator:
    symbol: str
    timeframe: str
    sma_20: float | None
    ema_20: float | None
    rsi_14: float | None
    macd: float | None
    signal: float | None
    rolling_volatility: float | None
    trend_summary: str
    computed_at: datetime


@dataclass
class GeneratedInsight:
    symbol: str | None
    insight_type: str
    title: str
    content: str
    confidence: float
    generated_at: datetime


def fetch_daily_closes(client: httpx.Client, symbol: str, days: int = 60) -> list[float]:
    coin_id = COIN_IDS.get(symbol)
    if coin_id is None:
        return []

    response = client.get(
        f"{settings.coingecko_base_url}/coins/{coin_id}/market_chart",
        params={"vs_currency": "usd", "days": days, "interval": "daily"},
    )
    response.raise_for_status()
    prices = response.json().get("prices", [])
    return [float(entry[1]) for entry in prices if len(entry) >= 2]


def compute_indicator(symbol: str, event: NormalizedMarketEvent, closes: list[float]) -> ComputedIndicator:
    computed_at = datetime.now(UTC)
    series = closes[-60:] if closes else [event.price_usd]

    sma_20 = _mean(series[-20:]) if len(series) >= 20 else _mean(series)
    ema_20_series = _ema_series(series, span=20)
    ema_20 = ema_20_series[-1] if ema_20_series else None

    rsi_14 = _rsi(series, window=14)
    ema_12_series = _ema_series(series, span=12)
    ema_26_series = _ema_series(series, span=26)

    macd_series: list[float] = []
    offset = len(ema_12_series) - len(ema_26_series)
    if offset >= 0:
        for index, value in enumerate(ema_26_series):
            macd_series.append(ema_12_series[index + offset] - value)

    macd = macd_series[-1] if macd_series else None
    signal_series = _ema_series(macd_series, span=9)
    signal = signal_series[-1] if signal_series else None
    rolling_volatility = _rolling_volatility(series, window=14)

    trend_summary = _build_trend_summary(
        symbol=symbol,
        price=event.price_usd,
        percent_change_24h=event.percent_change_24h,
        sma_20=sma_20,
        ema_20=ema_20,
        rsi_14=rsi_14,
        rolling_volatility=rolling_volatility,
    )

    return ComputedIndicator(
        symbol=symbol,
        timeframe="1d",
        sma_20=sma_20,
        ema_20=ema_20,
        rsi_14=rsi_14,
        macd=macd,
        signal=signal,
        rolling_volatility=rolling_volatility,
        trend_summary=trend_summary,
        computed_at=computed_at,
    )


def generate_insights(
    events: dict[str, NormalizedMarketEvent],
    indicators: dict[str, ComputedIndicator],
) -> list[GeneratedInsight]:
    generated_at = datetime.now(UTC)
    ranked = sorted(events.values(), key=lambda item: item.percent_change_24h, reverse=True)
    anomalies = sorted(
        (
            indicator
            for indicator in indicators.values()
            if (indicator.rolling_volatility or 0) >= 2.5
            or (indicator.rsi_14 is not None and (indicator.rsi_14 >= 68 or indicator.rsi_14 <= 35))
        ),
        key=lambda item: ((item.rolling_volatility or 0) * 0.7) + abs(events[item.symbol].percent_change_24h),
        reverse=True,
    )

    insights: list[GeneratedInsight] = []
    leader = ranked[0] if ranked else None
    if leader is not None:
        leader_indicator = indicators.get(leader.base_symbol)
        leader_volatility = (
            f"{leader_indicator.rolling_volatility:.2f}"
            if leader_indicator and leader_indicator.rolling_volatility is not None
            else "n/a"
        )
        insights.append(
            GeneratedInsight(
                symbol=leader.base_symbol,
                insight_type="daily_summary",
                title=f"{leader.base_symbol} leads the latest market move",
                content=(
                    f"{leader.base_symbol} is up {leader.percent_change_24h:.2f}% over the last 24 hours "
                    f"at {leader.price_usd:.2f} USD, with rolling volatility near {leader_volatility}."
                ),
                confidence=0.83,
                generated_at=generated_at,
            )
        )

    anomaly = anomalies[0] if anomalies else None
    if anomaly is not None:
        anomaly_event = events[anomaly.symbol]
        direction = "upside acceleration" if anomaly_event.percent_change_24h >= 0 else "downside stress"
        insights.append(
            GeneratedInsight(
                symbol=anomaly.symbol,
                insight_type="anomaly_watch",
                title=f"{anomaly.symbol} volatility watch",
                content=(
                    f"{anomaly.symbol} is showing {direction} with a {anomaly_event.percent_change_24h:.2f}% "
                    f"24-hour move, RSI near {anomaly.rsi_14:.1f} and rolling volatility at "
                    f"{anomaly.rolling_volatility:.2f}."
                ),
                confidence=0.79,
                generated_at=generated_at,
            )
        )

    breadth = sum(event.percent_change_24h > 0 for event in events.values())
    insights.append(
        GeneratedInsight(
            symbol=None,
            insight_type="market_breadth",
            title="Market breadth snapshot",
            content=(
                f"{breadth} of {len(events)} tracked assets are positive on the day. "
                f"Use breadth, volatility, and RSI together before chasing the strongest mover."
            ),
            confidence=0.74,
            generated_at=generated_at,
        )
    )
    return insights


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    multiplier = 2 / (span + 1)
    ema_values: list[float] = [values[0]]
    for value in values[1:]:
        ema_values.append((value - ema_values[-1]) * multiplier + ema_values[-1])
    return ema_values


def _rsi(values: list[float], window: int) -> float | None:
    if len(values) <= window:
        return None

    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-(window + 1) : -1], values[-window:]):
        delta = current - previous
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    if average_loss == 0:
        return 100.0

    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def _rolling_volatility(values: list[float], window: int) -> float | None:
    if len(values) <= window:
        return None
    returns = [
        ((current - previous) / previous) * 100
        for previous, current in zip(values[-(window + 1) : -1], values[-window:])
        if previous
    ]
    if len(returns) < 2:
        return None
    return stdev(returns)


def _build_trend_summary(
    symbol: str,
    price: float,
    percent_change_24h: float,
    sma_20: float | None,
    ema_20: float | None,
    rsi_14: float | None,
    rolling_volatility: float | None,
) -> str:
    regime = "holding above" if sma_20 is not None and price >= sma_20 else "trading below"
    ema_context = f"EMA20 {ema_20:.2f}" if ema_20 is not None else "EMA20 still warming up"
    rsi_context = "balanced momentum"
    if rsi_14 is not None and rsi_14 >= 68:
        rsi_context = "overbought momentum"
    elif rsi_14 is not None and rsi_14 <= 35:
        rsi_context = "oversold pressure"

    volatility_context = (
        f"rolling volatility {rolling_volatility:.2f}"
        if rolling_volatility is not None
        else "limited realized volatility history"
    )
    direction = "constructive upside" if percent_change_24h >= 0 else "near-term drawdown"
    sma_text = f"SMA20 {sma_20:.2f}" if sma_20 is not None else "SMA20 unavailable"

    return (
        f"{symbol} is {regime} its 20-day average with {direction}. "
        f"{sma_text}, {ema_context}, {rsi_context}, and {volatility_context}."
    )
