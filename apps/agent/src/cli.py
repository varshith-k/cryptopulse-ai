"""CryptoPulse agent CLI.

A thin Agents CLI over the running agent service. Ask the grounded agent a
question straight from the terminal and see both the answer and the backend
tool sources that grounded it::

    cd apps/agent
    python -m src.cli "which coins are trending upward today?"

The CLI talks to the agent's HTTP endpoint (the same one the dashboard uses), so
it exercises the full plan-tools -> call-tools -> compose-answer path rather than
re-implementing any logic here.
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx

# Defaults to the agent's local port (see docker-compose / README). Override
# with AGENT_URL when the agent runs elsewhere.
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8080/insights/query")


async def _ask(question: str) -> int:
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(AGENT_URL, json={"question": question})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        print(f"Could not reach the agent at {AGENT_URL}: {exc}", file=sys.stderr)
        return 2

    print(data.get("answer", "(no answer returned)"))
    sources = ", ".join(data.get("sources", [])) or "none"
    print(f"\nGrounded sources: {sources}")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m src.cli "your question"', file=sys.stderr)
        raise SystemExit(1)

    question = " ".join(sys.argv[1:])
    raise SystemExit(asyncio.run(_ask(question)))


if __name__ == "__main__":
    main()
