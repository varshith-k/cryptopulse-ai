import logging
import time
from collections import Counter
from threading import Lock


logger = logging.getLogger("cryptopulse.api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


class RequestMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests = 0
        self._status_codes: Counter[str] = Counter()

    def record(self, status_code: int) -> None:
        with self._lock:
            self._requests += 1
            self._status_codes[str(status_code)] += 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "requests_total": self._requests,
                "status_codes": dict(self._status_codes),
            }


metrics = RequestMetrics()


def log_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    logger.info(
        "%s %s -> %s in %.2fms",
        method,
        path,
        status_code,
        duration_ms,
    )
    metrics.record(status_code)


def now_ms() -> float:
    return time.perf_counter() * 1000
