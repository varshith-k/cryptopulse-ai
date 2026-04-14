from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from src.health import check_backend_health
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


@app.get("/health/ready")
async def ready() -> dict[str, object]:
    try:
        dependency_status = await check_backend_health()
    except Exception as exc:  # pragma: no cover - readiness guard
        raise HTTPException(status_code=503, detail=f"Backend dependency unavailable: {exc}") from exc

    return {
        "status": "ready",
        "timestamp": datetime.now(UTC).isoformat(),
        "dependencies": dependency_status,
    }


@app.post("/insights/query")
async def query_insights(payload: InsightRequest) -> dict[str, object]:
    answer, sources = await answer_question(payload.question)

    return {
        "question": payload.question,
        "answer": answer,
        "grounded": True,
        "sources": sources,
    }
