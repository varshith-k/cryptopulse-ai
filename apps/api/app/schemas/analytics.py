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


class RealtimeAnomalyRecord(BaseModel):
    symbol: str
    price_usd: float
    window_mean: float
    window_std: float
    z_score: float
    deviation_pct: float
    sample_size: int
    direction: str
    detected_at: str


class RealtimeAnomalyResponse(BaseModel):
    generated_at: str
    window_summary: str
    anomalies: list[RealtimeAnomalyRecord]
