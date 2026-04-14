from dataclasses import dataclass


@dataclass
class VolatilityObservation:
    symbol: str
    score: float
    flagged: bool


def score_volatility(symbol: str, score: float) -> VolatilityObservation:
    return VolatilityObservation(symbol=symbol, score=score, flagged=score >= 2.0)

