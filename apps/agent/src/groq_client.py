from __future__ import annotations

import json
from typing import Any

import httpx

from src.config import settings


SYSTEM_PROMPT = """You are CryptoPulse AI, a grounded crypto market analysis agent.
Use only the provided tool data. Do not invent prices, indicators, alerts, or events.
Do not provide financial advice or buy/sell instructions.
Explain uncertainty clearly and cite the tool sources that support your answer."""


async def ask_groq(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str | None:
    if not settings.groq_api_key:
        return None

    payload = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(
            f"{settings.groq_base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


async def plan_tools(question: str, available_tools: list[str]) -> list[str] | None:
    prompt = (
        "Choose the backend tools needed to answer the user question. "
        "Return JSON only with this shape: {\"tools\": [\"tool_name\"]}. "
        "Use one or more of these tools: "
        f"{', '.join(available_tools)}."
    )
    content = await ask_groq(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
        max_tokens=160,
    )
    if content is None:
        return None

    try:
        parsed = json.loads(_extract_json(content))
    except json.JSONDecodeError:
        return None

    requested = parsed.get("tools", [])
    if not isinstance(requested, list):
        return None

    return [tool for tool in requested if tool in available_tools]


async def compose_grounded_answer(
    question: str,
    tool_results: dict[str, Any],
) -> str | None:
    data_block = json.dumps(tool_results, default=str, indent=2)
    return await ask_groq(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"User question: {question}\n\n"
                    f"Tool data:\n{data_block}\n\n"
                    "Answer in 2-5 concise paragraphs. Include practical interpretation, "
                    "but avoid financial advice. If data is missing, say what is missing."
                ),
            },
        ],
        temperature=0.25,
        max_tokens=700,
    )


def _extract_json(content: str) -> str:
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end < start:
        return content
    return content[start : end + 1]
