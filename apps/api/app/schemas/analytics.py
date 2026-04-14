from pydantic import BaseModel


class AnomalyRecord(BaseModel):
    symbol: str
    anomaly_score: float
    direction: str
    reason: str
    percent_change_24h: float
    rolling_volatility: float | None = None
    rsi_14: float | None = None


class AnomalyResponse(BaseModel):
    generated_at: str
    anomalies: list[AnomalyRecord]
    recommendations: list[str]


class SummaryResponse(BaseModel):
    generated_at: str
    scope: str
    summary: str
    highlights: list[str]
