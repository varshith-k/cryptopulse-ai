from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    MarketSnapshot,
    TechnicalIndicator,
    TriggeredAlert,
    User,
    UserAlert,
    WatchedAsset,
)
from app.repositories.alerts import list_active_alerts_for_user
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


def evaluate_alerts_for_user(session: Session, user: User) -> list[TriggeredAlert]:
    triggered: list[TriggeredAlert] = []

    for alert in list_active_alerts_for_user(session, user.id):
        observed_value = _get_observed_value(session, alert)
        if observed_value is None or alert.threshold is None:
            continue

        if not _is_triggered(alert.alert_type, observed_value, alert.threshold):
            continue

        trigger = TriggeredAlert(
            alert_id=alert.id,
            user_id=user.id,
            symbol=alert.symbol,
            alert_type=alert.alert_type,
            threshold=alert.threshold,
            observed_value=observed_value,
            message=_build_trigger_message(alert, observed_value),
        )
        alert.is_active = False
        session.add(trigger)
        triggered.append(trigger)

    session.commit()
    for trigger in triggered:
        session.refresh(trigger)
    return triggered


def _get_observed_value(session: Session, alert: UserAlert) -> Decimal | None:
    if alert.alert_type in {"price_above", "price_below"}:
        statement = (
            select(MarketSnapshot.price_usd)
            .where(MarketSnapshot.symbol == alert.symbol)
            .order_by(MarketSnapshot.observed_at.desc())
            .limit(1)
        )
        return session.scalar(statement)

    if alert.alert_type == "volatility_spike":
        latest_computed_at = (
            select(func.max(TechnicalIndicator.computed_at))
            .where(
                TechnicalIndicator.symbol == alert.symbol,
                TechnicalIndicator.timeframe == "1d",
            )
            .scalar_subquery()
        )
        statement = select(TechnicalIndicator.rolling_volatility).where(
            TechnicalIndicator.symbol == alert.symbol,
            TechnicalIndicator.timeframe == "1d",
            TechnicalIndicator.computed_at == latest_computed_at,
        )
        return session.scalar(statement)

    return None


def _is_triggered(
    alert_type: str,
    observed_value: Decimal,
    threshold: Decimal,
) -> bool:
    if alert_type in {"price_above", "volatility_spike"}:
        return observed_value >= threshold
    if alert_type == "price_below":
        return observed_value <= threshold
    return False


def _build_trigger_message(alert: UserAlert, observed_value: Decimal) -> str:
    label = alert.alert_type.replace("_", " ")
    return (
        f"{alert.symbol} {label} alert triggered at {observed_value} "
        f"against threshold {alert.threshold}."
    )
