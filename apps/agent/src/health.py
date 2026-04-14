from __future__ import annotations

import httpx

from src.config import settings


async def check_backend_health() -> dict[str, str]:
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(f"{settings.backend_base_url}/health")
        response.raise_for_status()
        payload = response.json()
        return {"backend": payload.get("status", "unknown")}
