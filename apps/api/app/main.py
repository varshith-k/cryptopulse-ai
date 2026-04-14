from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.system import router as system_router
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.observability import log_request, now_ms


app = FastAPI(
    title="CryptoPulse AI API",
    version="0.1.0",
    summary="Backend API for live crypto analytics, alerts, and AI insights.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.api_cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    started_at = now_ms()
    response = await call_next(request)
    duration_ms = now_ms() - started_at
    log_request(request.method, request.url.path, response.status_code, duration_ms)
    return response

app.include_router(health_router)
app.include_router(system_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "service": settings.project_name,
        "environment": settings.environment,
        "docs": "/docs",
    }
