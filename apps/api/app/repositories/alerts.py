from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TriggeredAlert, UserAlert


def list_alerts_for_user(session: Session, user_id: str) -> list[UserAlert]:
    statement = (
        select(UserAlert)
        .where(UserAlert.user_id == user_id)
        .order_by(UserAlert.created_at.desc())
    )
    return list(session.scalars(statement).all())


def list_active_alerts_for_user(session: Session, user_id: str) -> list[UserAlert]:
    statement = (
        select(UserAlert)
        .where(UserAlert.user_id == user_id, UserAlert.is_active.is_(True))
        .order_by(UserAlert.created_at.asc())
    )
    return list(session.scalars(statement).all())


def list_triggered_alerts_for_user(
    session: Session,
    user_id: str,
    limit: int = 20,
) -> list[TriggeredAlert]:
    statement = (
        select(TriggeredAlert)
        .where(TriggeredAlert.user_id == user_id)
        .order_by(TriggeredAlert.triggered_at.desc())
        .limit(limit)
    )
    return list(session.scalars(statement).all())
