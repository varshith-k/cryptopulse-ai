from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.core.config import settings


app = FastAPI(
    title="CryptoPulse AI API",
    version="0.1.0",
    summary="Backend API for live crypto analytics, alerts, and AI insights.",
)

app.include_router(health_router)
app.include_router(market_router, prefix="/api/v1")


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "service": settings.project_name,
        "environment": settings.environment,
        "docs": "/docs",
    }

