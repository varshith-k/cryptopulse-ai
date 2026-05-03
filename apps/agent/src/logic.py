from __future__ import annotations

from src.client import (
    fetch_anomalies,
    fetch_market_overview,
    fetch_recommendations,
    fetch_summary,
)
from src.groq_client import compose_grounded_answer, plan_tools


TRACKED_SYMBOLS = ("BTC", "ETH", "SOL", "ADA")
AVAILABLE_TOOLS = (
    "market.overview",
    "analytics.anomalies",
    "analytics.summary",
    "analytics.recommendations",
)


async def answer_question(question: str) -> tuple[str, list[str]]:
    groq_answer = await _answer_with_groq(question)
    if groq_answer is not None:
        return groq_answer

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


async def _answer_with_groq(question: str) -> tuple[str, list[str]] | None:
    requested_tools = _merge_tool_plans(
        await plan_tools(question, list(AVAILABLE_TOOLS)),
        _required_tool_plan(question),
    )

    tool_results: dict[str, object] = {}
    sources: list[str] = []

    for tool_name in requested_tools:
        result = await _call_tool(tool_name, question)
        if result is None:
            continue
        tool_results[tool_name] = result
        sources.append(tool_name)

    if not tool_results:
        return None

    answer = await compose_grounded_answer(question, tool_results)
    if answer is None:
        return None

    return answer, sources


def _required_tool_plan(question: str) -> list[str]:
    normalized = question.lower()
    requested_symbols = [
        symbol for symbol in TRACKED_SYMBOLS if symbol.lower() in normalized
    ]
    tools = ["market.overview"]

    is_comparison = (
        "compare" in normalized
        or "versus" in normalized
        or " vs " in f" {normalized} "
        or len(requested_symbols) >= 2
    )
    asks_about_risk = any(
        term in normalized
        for term in ("anomal", "volatile", "volatility", "risk", "worry", "unusual")
    )
    asks_for_recommendations = any(
        term in normalized
        for term in ("recommend", "inspect next", "what next", "watch", "monitor")
    )
    asks_for_summary = (
        "summarize" in normalized
        or "summary" in normalized
        or "today" in normalized
        or bool(requested_symbols)
    )

    if is_comparison or asks_about_risk:
        tools.append("analytics.anomalies")

    if asks_for_recommendations or asks_about_risk:
        tools.append("analytics.recommendations")

    if asks_for_summary or is_comparison or asks_about_risk:
        tools.append("analytics.summary")

    return list(dict.fromkeys(tools))


def _merge_tool_plans(
    model_tools: list[str] | None,
    required_tools: list[str],
) -> list[str]:
    merged = [tool for tool in required_tools if tool in AVAILABLE_TOOLS]
    if model_tools:
        merged.extend(tool for tool in model_tools if tool in AVAILABLE_TOOLS)
    return list(dict.fromkeys(merged))


async def _call_tool(tool_name: str, question: str) -> object | None:
    if tool_name == "market.overview":
        return await fetch_market_overview()

    if tool_name == "analytics.anomalies":
        return await fetch_anomalies()

    if tool_name == "analytics.recommendations":
        return await fetch_recommendations()

    if tool_name == "analytics.summary":
        return await fetch_summary(_summary_scope_for_question(question))

    return None


def _summary_scope_for_question(question: str) -> str:
    normalized = question.lower()
    for symbol in TRACKED_SYMBOLS:
        if symbol.lower() in normalized:
            return symbol
    return "market"
