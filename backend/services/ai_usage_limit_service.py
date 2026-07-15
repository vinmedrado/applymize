from __future__ import annotations
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.ai_usage import AIUsageEvent
logger = get_logger(__name__)
def _today_window() -> tuple[datetime, datetime]:
    try: tz = ZoneInfo(settings.app_timezone)
    except Exception: tz = ZoneInfo("America/Sao_Paulo")
    now = datetime.now(tz)
    start = datetime.combine(now.date(), time.min, tzinfo=tz)
    return start.replace(tzinfo=None), (start + timedelta(days=1)).replace(tzinfo=None)
def get_daily_usage_count(db: Session, tenant_id: int, user_id: int, feature: str) -> int:
    start, end = _today_window()
    return db.query(AIUsageEvent).filter(AIUsageEvent.tenant_id == tenant_id, AIUsageEvent.user_id == user_id, AIUsageEvent.feature == feature, AIUsageEvent.created_at >= start, AIUsageEvent.created_at < end).count()
def assert_daily_limit(db: Session, tenant_id: int, user_id: int, feature: str, limit: int, log_event: str) -> None:
    if limit <= 0: return
    used = get_daily_usage_count(db, tenant_id, user_id, feature)
    if used >= limit:
        logger.warning("%s tenant_id=%s user_id=%s feature=%s used=%s limit=%s", log_event, tenant_id, user_id, feature, used, limit)
        raise PermissionError("Limite diário atingido. Tente novamente amanhã ou ajuste o limite no ambiente.")
def record_ai_usage(db: Session, tenant_id: int, user_id: int, feature: str, provider: str = "", model: str = "") -> None:
    db.add(AIUsageEvent(tenant_id=tenant_id, user_id=user_id, feature=feature, provider=provider or "", model=model or ""))
