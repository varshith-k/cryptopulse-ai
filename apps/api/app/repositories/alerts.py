from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import UserAlert


def list_alerts_for_user(session: Session, user_id: str) -> list[UserAlert]:
    statement = (
        select(UserAlert)
        .where(UserAlert.user_id == user_id)
        .order_by(UserAlert.created_at.desc())
    )
    return list(session.scalars(statement).all())

