from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

from src.logic import answer_question


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
    answer, sources = await answer_question(payload.question)

    return {
        "question": payload.question,
        "answer": answer,
        "grounded": True,
        "sources": sources,
    }
