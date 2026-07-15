from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.user_settings import UserSettings


def get_or_create_settings(db: Session, user_id: int) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if settings:
        return settings

    settings = UserSettings(user_id=user_id, onboarding_completed=False)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def get_onboarding_status(db: Session, user_id: int) -> dict:
    settings = get_or_create_settings(db, user_id)
    return {"completed": bool(settings.onboarding_completed)}


def complete_onboarding(db: Session, user_id: int) -> dict:
    settings = get_or_create_settings(db, user_id)
    settings.onboarding_completed = True
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    return {"completed": True}
