from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import User, UserAlert, WatchedAsset
from app.schemas.alerts import AlertCreate


def create_alert(session: Session, user: User, payload: AlertCreate) -> UserAlert:
    asset = session.get(WatchedAsset, payload.symbol.upper())
    if asset is None:
        raise ValueError(f"Unknown symbol '{payload.symbol}'.")

    alert = UserAlert(
        user_id=user.id,
        symbol=payload.symbol.upper(),
        alert_type=payload.alert_type,
        threshold=Decimal(str(payload.threshold)) if payload.threshold is not None else None,
        is_active=True,
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert

