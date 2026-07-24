from __future__ import annotations

from datetime import datetime, time
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.automation import AutomationSettings, JobNotification
from backend.services.automation_scheduler import estimate_next_run
from backend.services.job_role_relevance import role_search_terms
from backend.core.timezone import to_app_timezone_iso
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change

logger = get_logger(__name__)

router = APIRouter(prefix="/api/automation", tags=["automation"])

_ALLOWED_MODES = {"interval", "fixed", "window"}


def _time_to_str(value: time | None) -> str | None:
    return value.strftime("%H:%M") if value else None


def _parse_hhmm(value: str | time | None, field_name: str) -> time | None:
    if value is None or isinstance(value, time):
        return value
    raw = value.strip()
    try:
        return datetime.strptime(raw, "%H:%M").time()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} deve estar no formato HH:MM") from exc


class AutomationSettingsPayload(BaseModel):
    enabled: bool = False
    mode: Literal["interval", "fixed", "window"] = "interval"
    interval_minutes: int | None = Field(default=None)
    times: list[str] | None = None
    window_start: str | None = None
    window_end: str | None = None
    search_terms: list[str] | None = None
    min_role_relevance: float = Field(default=55.0, ge=40.0, le=95.0)

    @field_validator("times")
    @classmethod
    def validate_times_format(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        cleaned: list[str] = []
        for item in value:
            raw = str(item).strip()
            try:
                datetime.strptime(raw, "%H:%M")
            except ValueError as exc:
                raise ValueError("times deve conter horários no formato HH:MM") from exc
            cleaned.append(raw)
        return cleaned

    @field_validator("search_terms")
    @classmethod
    def validate_search_terms(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        cleaned = list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))
        if len(cleaned) > 8:
            raise ValueError("search_terms aceita no máximo 8 termos")
        return cleaned or None

    @model_validator(mode="after")
    def validate_mode_requirements(self):
        mode = (self.mode or "interval").lower()
        if mode not in _ALLOWED_MODES:
            raise ValueError("mode inválido. Use interval, fixed ou window")

        if mode == "interval" and (self.interval_minutes is None or self.interval_minutes < 15):
            raise ValueError("interval_minutes deve ser maior ou igual a 15 quando mode=interval")

        if mode == "fixed" and not self.times:
            raise ValueError("times não pode ser vazio quando mode=fixed")

        if mode == "window":
            if not self.window_start or not self.window_end:
                raise ValueError("window_start e window_end são obrigatórios quando mode=window")
            try:
                datetime.strptime(self.window_start, "%H:%M")
                datetime.strptime(self.window_end, "%H:%M")
            except ValueError as exc:
                raise ValueError("window_start e window_end devem estar no formato HH:MM") from exc

        return self


def _status_payload(db: Session, user, setting: AutomationSettings | None) -> dict[str, Any]:
    user_id = user.id
    total_sent = db.query(JobNotification).filter(JobNotification.user_id == user_id).count()

    if not setting:
        return {
            "enabled": False,
            "mode": "interval",
            "interval_minutes": None,
            "times": None,
            "window_start": None,
            "window_end": None,
            "search_terms": role_search_terms(user.target_role),
            "min_role_relevance": 55.0,
            "last_run": None,
            "next_run_estimate": None,
            "total_notifications_sent": total_sent,
            "scheduler_enabled": bool(settings.automation_scheduler_enabled),
        }

    next_run = estimate_next_run(setting)
    return {
        "enabled": bool(setting.enabled),
        "mode": setting.mode,
        "interval_minutes": setting.interval_minutes,
        "times": setting.times,
        "window_start": _time_to_str(setting.window_start),
        "window_end": _time_to_str(setting.window_end),
        "search_terms": role_search_terms(user.target_role, setting.search_terms),
        "min_role_relevance": float(setting.min_role_relevance or 55.0),
        "last_run": to_app_timezone_iso(setting.last_run) if setting.last_run else None,
        "next_run_estimate": to_app_timezone_iso(next_run) if next_run else None,
        "total_notifications_sent": total_sent,
        "scheduler_enabled": bool(settings.automation_scheduler_enabled),
    }


def _current_setting(db: Session, user_id: int) -> AutomationSettings | None:
    return (
        db.query(AutomationSettings)
        .filter(AutomationSettings.user_id == user_id)
        .order_by(AutomationSettings.id.desc())
        .first()
    )


@router.get("/status")
def automation_status(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return _status_payload(db, ctx.user, _current_setting(db, ctx.user.id))


@router.put("/settings")
def update_automation_settings(
    payload: AutomationSettingsPayload,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    setting = _current_setting(db, ctx.user.id)
    created = False

    if not setting:
        setting = AutomationSettings(user_id=ctx.user.id, enabled=False)
        db.add(setting)
        created = True
        logger.info(
            "automation_settings_created tenant_id=%s user_id=%s enabled=%s mode=%s",
            ctx.tenant_id,
            ctx.user.id,
            False,
            payload.mode,
        )

    setting.enabled = bool(payload.enabled)
    setting.mode = payload.mode
    setting.interval_minutes = payload.interval_minutes
    setting.times = payload.times
    setting.window_start = _parse_hhmm(payload.window_start, "window_start")
    setting.window_end = _parse_hhmm(payload.window_end, "window_end")
    setting.search_terms = payload.search_terms
    setting.min_role_relevance = payload.min_role_relevance

    try:
        db.commit()
        db.refresh(setting)
    except Exception:
        db.rollback()
        raise

    logger.info(
        "automation_settings_updated tenant_id=%s user_id=%s created=%s enabled=%s mode=%s interval_minutes=%s",
        ctx.tenant_id,
        ctx.user.id,
        created,
        setting.enabled,
        setting.mode,
        setting.interval_minutes,
    )
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:{ctx.user.id}")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    return _status_payload(db, ctx.user, setting)
