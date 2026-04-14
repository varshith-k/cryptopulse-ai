from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db_session
from app.dependencies.auth import get_current_user
from app.repositories.alerts import list_alerts_for_user
from app.schemas.alerts import AlertCreate, AlertRead
from app.services.alerts import create_alert


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
async def get_user_alerts(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[AlertRead]:
    alerts = list_alerts_for_user(session, user.id)
    return [AlertRead.model_validate(alert) for alert in alerts]


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_user_alert(
    payload: AlertCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> AlertRead:
    try:
        alert = create_alert(session, user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return AlertRead.model_validate(alert)
