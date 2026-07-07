"""CryptoPulse MCP server.

Exposes the grounded CryptoPulse backend analytics tools over the Model Context
Protocol (MCP) so *any* MCP-compatible client — Claude Desktop, the MCP
Inspector, or another agent — can call the same tools our own agent uses. The
tool implementations come straight from the shared registry in ``src.tools``,
so there is exactly one definition of each tool behind both surfaces.

Run locally over stdio (the transport MCP clients launch)::

    cd apps/agent
    python -m src.mcp_server

Point an MCP client at it with a config like::

    {
      "mcpServers": {
        "cryptopulse": {
          "command": "python",
          "args": ["-m", "src.mcp_server"],
          "cwd": "apps/agent",
          "env": {"BACKEND_BASE_URL": "http://localhost:8000"}
        }
      }
    }

Each ``@mcp.tool()`` function's name, type hints and docstring become the tool's
public MCP schema, which is how the client knows what it can call and why.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.tools import call_tool

mcp = FastMCP("cryptopulse")


@mcp.tool()
async def market_overview() -> dict[str, Any]:
    """Latest market snapshot for every tracked coin.

    Returns price, 24-hour percent change, volume, RSI(14), rolling volatility
    and trend context. Use this for "what's moving", comparisons, and any
    question that needs current prices or indicators.
    """
    return await call_tool("market.overview")


@mcp.tool()
async def analytics_anomalies() -> dict[str, Any]:
    """Assets flagged as anomalous by the backend's scoring model.

    Combines volatility, momentum and RSI into an anomaly score and returns the
    offending symbols with a human-readable reason each. Use this for risk,
    "anything unusual", or volatility questions.
    """
    return await call_tool("analytics.anomalies")


@mcp.tool()
async def analytics_recommendations() -> list[str]:
    """Ranked list of what to inspect next given current conditions."""
    return await call_tool("analytics.recommendations")


@mcp.tool()
async def analytics_summary(scope: str = "market") -> dict[str, Any]:
    """Narrative summary + highlights for one symbol or the whole market.

    Pass a tracked symbol such as ``"BTC"`` for a single-coin summary, or leave
    ``scope`` as ``"market"`` for the portfolio-wide view.
    """
    return await call_tool("analytics.summary", scope=scope)


if __name__ == "__main__":
    # Default stdio transport: the MCP client spawns this process and speaks MCP
    # over stdin/stdout.
    mcp.run()
