from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from statistics import fmean, pstdev


@dataclass
class VolatilitySignal:
    symbol: str
    price: float
    window_mean: float
    window_std: float
    z_score: float
    deviation_pct: float
    sample_size: int
    direction: str
    is_anomaly: bool
    detected_at: datetime


class SlidingWindowDetector:
    """Real-time volatility detector.

    Maintains a bounded per-symbol price window (a ``deque`` capped at
    ``window_size``) and flags any incoming tick that deviates more than
    ``z_threshold`` standard deviations from the rolling mean of the window.

    The window is compared *before* the new tick is appended, so each tick is
    scored against its own recent history rather than against itself. Memory is
    O(symbols x window_size); old ticks fall off the deque automatically.
    """

    def __init__(self, window_size: int, z_threshold: float, min_samples: int) -> None:
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.min_samples = min_samples
        self._windows: dict[str, deque[float]] = {}

    def observe(self, symbol: str, price: float, observed_at: datetime) -> VolatilitySignal:
        window = self._windows.setdefault(symbol, deque(maxlen=self.window_size))
        baseline = list(window)  # recent history, excluding the current tick
        window.append(price)

        if len(baseline) < self.min_samples:
            return VolatilitySignal(
                symbol=symbol,
                price=price,
                window_mean=price,
                window_std=0.0,
                z_score=0.0,
                deviation_pct=0.0,
                sample_size=len(baseline),
                direction="flat",
                is_anomaly=False,
                detected_at=observed_at,
            )

        mean = fmean(baseline)
        std = pstdev(baseline)
        z_score = (price - mean) / std if std > 0 else 0.0
        deviation_pct = ((price - mean) / mean * 100) if mean else 0.0
        is_anomaly = abs(z_score) >= self.z_threshold

        if not is_anomaly:
            direction = "flat"
        elif z_score > 0:
            direction = "spike_up"
        else:
            direction = "spike_down"

        return VolatilitySignal(
            symbol=symbol,
            price=price,
            window_mean=mean,
            window_std=std,
            z_score=z_score,
            deviation_pct=deviation_pct,
            sample_size=len(baseline),
            direction=direction,
            is_anomaly=is_anomaly,
            detected_at=observed_at,
        )
