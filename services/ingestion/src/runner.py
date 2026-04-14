from __future__ import annotations

import time

from src.coingecko_backfill import run_backfill
from src.config import settings


def main() -> None:
    print(
        "Starting continuous ingestion worker with "
        f"{settings.refresh_interval_seconds}s refresh interval."
    )
    while True:
        try:
            run_backfill()
        except Exception as exc:  # pragma: no cover
            print(f"[ingestion] refresh failed: {exc}")
        time.sleep(settings.refresh_interval_seconds)


if __name__ == "__main__":
    main()
