import httpx

from src.config import settings


async def fetch_market_overview() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{settings.backend_base_url}/api/v1/market/overview")
        response.raise_for_status()
        return response.json()


async def fetch_anomalies() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{settings.backend_base_url}/api/v1/analytics/anomalies")
        response.raise_for_status()
        return response.json()


async def fetch_summary(scope: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{settings.backend_base_url}/api/v1/analytics/summary",
            params={"scope": scope},
        )
        response.raise_for_status()
        return response.json()


async def fetch_recommendations() -> list[str]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{settings.backend_base_url}/api/v1/analytics/recommendations"
        )
        response.raise_for_status()
        return response.json()
