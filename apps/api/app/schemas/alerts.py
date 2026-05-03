import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    symbol: str
    alert_type: str
    threshold: float | None = None


class AlertRead(BaseModel):
    id: uuid.UUID
    symbol: str
    alert_type: str
    threshold: float | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TriggeredAlertRead(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    symbol: str
    alert_type: str
    threshold: float | None
    observed_value: float
    message: str
    triggered_at: datetime

    model_config = {"from_attributes": True}
