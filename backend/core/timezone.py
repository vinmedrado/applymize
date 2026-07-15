from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from backend.core.config import settings


def app_zone() -> ZoneInfo:
    try:
        return ZoneInfo(settings.app_timezone or "America/Sao_Paulo")
    except Exception:
        return ZoneInfo("America/Sao_Paulo")


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_app_timezone(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    value = dt
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(app_zone())


def to_app_timezone_iso(dt: datetime | None) -> str | None:
    localized = to_app_timezone(dt)
    return localized.isoformat() if localized else None


def app_now_iso() -> str:
    return datetime.now(app_zone()).isoformat()
