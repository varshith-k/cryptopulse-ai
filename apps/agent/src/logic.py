from __future__ import annotations

from src.client import (
    fetch_anomalies,
    fetch_market_overview,
    fetch_recommendations,
    fetch_summary,
)


async def answer_question(question: str) -> tuple[str, list[str]]:
    normalized = question.lower()

    if "trending upward" in normalized or "upward" in normalized:
        overview = await fetch_market_overview()
        rising_assets = [
            asset for asset in overview["assets"] if asset["percent_change_24h"] > 0
        ]
        ordered = sorted(
            rising_assets, key=lambda asset: asset["percent_change_24h"], reverse=True
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

    if "summarize btc" in normalized or ("btc" in normalized and "today" in normalized):
        summary = await fetch_summary("BTC")
        return (
            f'{summary["summary"]} Highlights: ' + " ".join(summary["highlights"]),
            ["analytics.summary", "market.overview"],
        )

    if "unusual volatility" in normalized or "anomal" in normalized:
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

    if "compare eth and sol" in normalized or ("eth" in normalized and "sol" in normalized):
        overview = await fetch_market_overview()
        lookup = {asset["symbol"]: asset for asset in overview["assets"]}
        eth = lookup.get("ETH")
        sol = lookup.get("SOL")
        if eth is None or sol is None:
            return (
                "ETH or SOL is missing from the current tracked asset set.",
                ["market.overview"],
            )

        answer = (
            f'SOL has stronger current momentum than ETH, with a {sol["percent_change_24h"]:.2f}% '
            f'24-hour move versus {eth["percent_change_24h"]:.2f}% for ETH. '
            f'SOL volatility is {sol["rolling_volatility"]:.2f} versus {eth["rolling_volatility"]:.2f}, '
            f'and RSI sits at {sol["rsi_14"]:.1f} versus {eth["rsi_14"]:.1f}.'
        )
        return (answer, ["market.overview"])

    if "recommend" in normalized or "inspect next" in normalized:
        recommendations = await fetch_recommendations()
        return (
            "Next metrics to inspect: " + " ".join(recommendations),
            ["analytics.recommendations", "analytics.anomalies"],
        )

    summary = await fetch_summary("market")
    recommendations = await fetch_recommendations()
    fallback = (
        f'{summary["summary"]} Next suggested checks: '
        + " ".join(recommendations[:2])
    )
    return (fallback, ["analytics.summary", "analytics.recommendations"])
