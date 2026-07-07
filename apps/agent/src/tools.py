"""Shared CryptoPulse tool registry.

This module is the single source of truth for the agent's toolset. Both the
in-process agent (``src.logic``) and the standalone MCP server
(``src.mcp_server``) build their tools from this registry, so an external MCP
client (Claude Desktop, the MCP Inspector, or another agent) calls exactly the
same grounded backend tools our own agent uses. That "define once, expose to
many consumers" split is what keeps the agent's behavior and the public MCP
surface from drifting apart.

Each tool is a thin, typed wrapper over a backend analytics endpoint (see
``src.client``). The tools never fabricate market data; they only relay what the
FastAPI backend returns, which is what keeps agent answers grounded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from src.client import (
    fetch_anomalies,
    fetch_market_overview,
    fetch_recommendations,
    fetch_summary,
)


@dataclass(frozen=True)
class Tool:
    """A single grounded tool the agent (or an MCP client) can call.

    ``name`` is the stable identifier used by the LLM tool planner and returned
    to the user as a citation source. ``handler`` is the async callable that
    fetches the backing data from the backend.
    """

    name: str
    description: str
    handler: Callable[..., Awaitable[Any]]


async def _market_overview() -> dict[str, Any]:
    """Latest price, 24h move, volume, RSI, volatility and trend per symbol."""
    return await fetch_market_overview()


async def _analytics_anomalies() -> dict[str, Any]:
    """Anomaly-scored assets (volatility / momentum / RSI) with reasons."""
    return await fetch_anomalies()


async def _analytics_recommendations() -> list[str]:
    """Ranked list of what to inspect next, given current market conditions."""
    return await fetch_recommendations()


async def _analytics_summary(scope: str = "market") -> dict[str, Any]:
    """Narrative summary + highlights for one symbol, or the whole market.

    ``scope`` is a tracked symbol (e.g. ``"BTC"``) or ``"market"`` for the
    portfolio-wide view.
    """
    return await fetch_summary(scope)


# Registry keyed by the stable tool name. Adding a tool here automatically
# exposes it to both the agent's planner and the MCP server.
TOOLS: dict[str, Tool] = {
    "market.overview": Tool(
        "market.overview",
        _market_overview.__doc__ or "",
        _market_overview,
    ),
    "analytics.anomalies": Tool(
        "analytics.anomalies",
        _analytics_anomalies.__doc__ or "",
        _analytics_anomalies,
    ),
    "analytics.recommendations": Tool(
        "analytics.recommendations",
        _analytics_recommendations.__doc__ or "",
        _analytics_recommendations,
    ),
    "analytics.summary": Tool(
        "analytics.summary",
        _analytics_summary.__doc__ or "",
        _analytics_summary,
    ),
}


def tool_names() -> list[str]:
    """Stable tool identifiers, in registry order."""
    return list(TOOLS)


async def call_tool(name: str, **kwargs: Any) -> Any:
    """Invoke a registered tool by name.

    Raises ``KeyError`` for an unknown tool so callers can fall back cleanly
    instead of silently returning nothing.
    """
    tool = TOOLS.get(name)
    if tool is None:
        raise KeyError(name)
    return await tool.handler(**kwargs)
