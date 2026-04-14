from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="CryptoPulse AI Agent",
    version="0.1.0",
    summary="Grounded AI service for summaries, Q&A, and anomaly explanations.",
)


class InsightRequest(BaseModel):
    question: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}


@app.post("/insights/query")
async def query_insights(payload: InsightRequest) -> dict[str, object]:
    normalized = payload.question.lower()

    if "btc" in normalized and "today" in normalized:
        answer = (
            "BTC is showing positive daily momentum in the seeded Phase 1 dataset. "
            "Phase 4 will replace this template with tool-backed reasoning over live indicators."
        )
    else:
        answer = (
            "The agent scaffold is active. In later phases it will query backend tools, "
            "inspect indicators, and generate grounded multi-step responses."
        )

    return {
        "question": payload.question,
        "answer": answer,
        "grounded": True,
        "sources": ["seeded-market-overview"],
    }

