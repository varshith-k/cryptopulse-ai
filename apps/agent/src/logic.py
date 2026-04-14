from __future__ import annotations

from src.client import (
    fetch_anomalies,
    fetch_market_overview,
    fetch_recommendations,
    fetch_summary,
)


TRACKED_SYMBOLS = ("BTC", "ETH", "SOL", "ADA")


async def answer_question(question: str) -> tuple[str, list[str]]:
    normalized = question.lower()
    requested_symbols = [symbol for symbol in TRACKED_SYMBOLS if symbol.lower() in normalized]

    if "trending upward" in normalized or "upward" in normalized or "trending" in normalized:
        return await _answer_trending_upward()

    if "unusual volatility" in normalized or "volatile" in normalized or "anomal" in normalized:
        return await _answer_anomalies()

    if ("compare" in normalized or "versus" in normalized or "vs" in normalized) and len(requested_symbols) >= 2:
        return await _answer_compare(requested_symbols[:2])

    if ("summarize" in normalized or "summary" in normalized or "today" in normalized) and requested_symbols:
        return await _answer_symbol_summary(requested_symbols[0])

    if "recommend" in normalized or "inspect next" in normalized or "what next" in normalized:
        return await _answer_recommendations()

    return await _answer_fallback()


async def _answer_trending_upward() -> tuple[str, list[str]]:
    overview = await fetch_market_overview()
    rising_assets = [
        asset for asset in overview["assets"] if asset["percent_change_24h"] > 0
    ]
    ordered = sorted(
        rising_assets,
        key=lambda asset: asset["percent_change_24h"],
        reverse=True,
    )
    if not ordered:
        return (
            "No tracked assets are currently positive in the latest dataset.",
            ["market.overview"],
        )

    top_symbols = ", ".join(
        f'{asset["symbol"]} ({asset["percent_change_24h"]:.2f}%)'
        for asset in ordered[:3]
    )
    return (
        f"The strongest upward movers in the latest 24-hour snapshot are {top_symbols}.",
        ["market.overview"],
    )


async def _answer_anomalies() -> tuple[str, list[str]]:
    anomalies = await fetch_anomalies()
    if not anomalies["anomalies"]:
        return (
            "No assets currently breach the anomaly thresholds in the latest dataset.",
            ["analytics.anomalies"],
        )

    details = "; ".join(
        f'{item["symbol"]}: {item["reason"]} (score {item["anomaly_score"]:.2f})'
        for item in anomalies["anomalies"][:3]
    )
    return (
        f"The most unusual volatility signatures are: {details}.",
        ["analytics.anomalies"],
    )


async def _answer_compare(symbols: list[str]) -> tuple[str, list[str]]:
    overview = await fetch_market_overview()
    lookup = {asset["symbol"]: asset for asset in overview["assets"]}
    left = lookup.get(symbols[0])
    right = lookup.get(symbols[1])
    if left is None or right is None:
        return (
            "One of the requested assets is missing from the current tracked set.",
            ["market.overview"],
        )

    stronger = left if left["percent_change_24h"] >= right["percent_change_24h"] else right
    weaker = right if stronger is left else left
    return (
        f'{stronger["symbol"]} currently has stronger momentum than {weaker["symbol"]}, with a '
        f'{stronger["percent_change_24h"]:.2f}% 24-hour move versus {weaker["percent_change_24h"]:.2f}%. '
        f'RSI is {_format_metric(stronger["rsi_14"], 1)} versus {_format_metric(weaker["rsi_14"], 1)}, '
        f'and rolling volatility is {_format_metric(stronger["rolling_volatility"], 2)} versus '
        f'{_format_metric(weaker["rolling_volatility"], 2)}.',
        ["market.overview"],
    )


async def _answer_symbol_summary(symbol: str) -> tuple[str, list[str]]:
    summary = await fetch_summary(symbol)
    return (
        f'{summary["summary"]} Highlights: ' + " ".join(summary["highlights"]),
        ["analytics.summary", "market.overview"],
    )


async def _answer_recommendations() -> tuple[str, list[str]]:
    recommendations = await fetch_recommendations()
    return (
        "Next metrics to inspect: " + " ".join(recommendations),
        ["analytics.recommendations", "analytics.anomalies"],
    )


async def _answer_fallback() -> tuple[str, list[str]]:
    summary = await fetch_summary("market")
    recommendations = await fetch_recommendations()
    fallback = (
        f'{summary["summary"]} Next suggested checks: '
        + " ".join(recommendations[:2])
    )
    return (fallback, ["analytics.summary", "analytics.recommendations"])


def _format_metric(value: float | None, digits: int) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"
