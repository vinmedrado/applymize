from __future__ import annotations

import threading
import time as time_module
from datetime import datetime, time, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.models.automation import AutomationSettings, JobNotification
from backend.models.job import Job
from backend.models.membership import Membership
from backend.models.user import User
from backend.models.whatsapp_session import WhatsAppSession
from backend.services.job_eligibility_filter import evaluate_job_eligibility
from backend.services.job_ingestion import ingest_jobs
from backend.core.timezone import to_app_timezone_iso
from backend.services.strategy_engine import StrategyRecommendation, get_strategy_recommendations
from backend.services.whatsapp_job_alert_service import format_job_whatsapp_message
from backend.services.whatsapp_session_service import WhatsAppSessionService

logger = get_logger(__name__)

_DEFAULT_INTERVAL_MINUTES = 60
_started = False
_lock = threading.Lock()


def _loop_seconds() -> int:
    return max(int(getattr(settings, "automation_scheduler_loop_seconds", 300) or 300), 60)


def _default_ingest_limit() -> int:
    return max(int(getattr(settings, "automation_default_ingest_limit", 20) or 20), 1)


def _default_provider() -> str:
    provider = (getattr(settings, "automation_default_provider", "all") or "all").strip().lower()
    return provider or "all"


def _default_provider_options() -> dict[str, Any]:
    return {
        "term": getattr(settings, "automation_default_term", "Analista de Dados"),
        "city": getattr(settings, "automation_default_city", "São Paulo"),
        "state": getattr(settings, "automation_default_state", "SP"),
        "country": getattr(settings, "automation_default_country", "Brazil"),
        "poblacion": getattr(settings, "automation_default_infojobs_city_code", "5211323"),
        "city_code": getattr(settings, "automation_default_infojobs_city_code", "5211323"),
    }


def _whatsapp_delay_seconds() -> float:
    return max(float(getattr(settings, "automation_whatsapp_delay_seconds", 2) or 0), 0.0)


def _max_notifications_per_run() -> int:
    return max(int(getattr(settings, "automation_max_notifications_per_run", 5) or 5), 1)


def _normalize_time_value(value: Any) -> str | None:
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, str):
        raw = value.strip()
        if len(raw) >= 5:
            return raw[:5]
    if isinstance(value, dict):
        raw = value.get("time") or value.get("hour") or value.get("value")
        return _normalize_time_value(raw)
    return None


def _configured_times(raw_times: Any) -> set[str]:
    if raw_times is None:
        return set()
    if isinstance(raw_times, list):
        return {item for item in (_normalize_time_value(v) for v in raw_times) if item}
    if isinstance(raw_times, dict):
        values = raw_times.get("times") or raw_times.get("values") or raw_times.get("items") or []
        if isinstance(values, list):
            return {item for item in (_normalize_time_value(v) for v in values) if item}
        item = _normalize_time_value(values)
        return {item} if item else set()
    item = _normalize_time_value(raw_times)
    return {item} if item else set()


def _inside_window(now_time: time, start: time | None, end: time | None) -> bool:
    if not start or not end:
        return False
    if start <= end:
        return start <= now_time <= end
    return now_time >= start or now_time <= end


def _minutes_since_last_run(setting: AutomationSettings, now: datetime) -> float | None:
    if not setting.last_run:
        return None
    return (now - setting.last_run).total_seconds() / 60


def estimate_next_run(setting: AutomationSettings, now: datetime | None = None) -> datetime | None:
    now = now or datetime.utcnow()
    if not setting.enabled:
        return None
    mode = (setting.mode or "interval").strip().lower()
    interval = max(int(setting.interval_minutes or _DEFAULT_INTERVAL_MINUTES), 1)

    if mode == "interval":
        return now if not setting.last_run else setting.last_run + timedelta(minutes=interval)

    if mode == "fixed":
        times = sorted(_configured_times(setting.times))
        if not times:
            return None
        today = now.date()
        candidates = []
        for day_offset in (0, 1):
            day = today + timedelta(days=day_offset)
            for raw in times:
                hour, minute = raw.split(":", 1)
                candidate = datetime.combine(day, time(int(hour), int(minute)))
                if candidate >= now:
                    candidates.append(candidate)
        return min(candidates) if candidates else None

    if mode == "window":
        if not setting.window_start or not setting.window_end:
            return None
        if _inside_window(now.time(), setting.window_start, setting.window_end):
            if not setting.last_run:
                return now
            return setting.last_run + timedelta(minutes=interval)
        candidate = datetime.combine(now.date(), setting.window_start)
        if candidate < now:
            candidate += timedelta(days=1)
        return candidate

    return None


def _is_due(setting: AutomationSettings, now: datetime) -> bool:
    mode = (setting.mode or "interval").strip().lower()
    elapsed = _minutes_since_last_run(setting, now)

    if mode == "interval":
        interval = max(int(setting.interval_minutes or _DEFAULT_INTERVAL_MINUTES), 1)
        return elapsed is None or elapsed >= interval

    if mode == "fixed":
        current = now.strftime("%H:%M")
        if current not in _configured_times(setting.times):
            return False
        return not setting.last_run or setting.last_run.strftime("%Y-%m-%d %H:%M") != now.strftime("%Y-%m-%d %H:%M")

    if mode == "window":
        if not _inside_window(now.time(), setting.window_start, setting.window_end):
            return False
        interval = max(int(setting.interval_minutes or _DEFAULT_INTERVAL_MINUTES), 1)
        return elapsed is None or elapsed >= interval

    logger.warning("automation_user_skipped user_id=%s reason=unknown_mode mode=%s", setting.user_id, setting.mode)
    return False


def _tenant_id_for_user(db: Session, user_id: int) -> int | None:
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id, Membership.is_active.is_(True))
        .order_by(Membership.id.asc())
        .first()
    )
    return membership.tenant_id if membership else None


def _already_sent(db: Session, user_id: int, job_id: int) -> bool:
    return db.query(JobNotification).filter(
        JobNotification.user_id == user_id,
        JobNotification.job_id == job_id,
    ).first() is not None


def _save_job_notification(db: Session, user_id: int, job_id: int) -> bool:
    db.add(JobNotification(user_id=user_id, job_id=job_id))
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        logger.info("automation_user_skipped user_id=%s job_id=%s reason=duplicate_notification", user_id, job_id)
        return False


def _user_whatsapp_session(db: Session, tenant_id: int, user_id: int) -> WhatsAppSession | None:
    return db.query(WhatsAppSession).filter(
        WhatsAppSession.tenant_id == tenant_id,
        WhatsAppSession.user_id == user_id,
    ).first()


def _priority_is_eligible(recommendation: StrategyRecommendation) -> bool:
    return recommendation.priority in {"HIGH_PRIORITY", "MEDIUM_PRIORITY", "HIGH", "MEDIUM"}


def _select_jobs_to_send(
    db: Session,
    tenant_id: int,
    user_id: int,
    limit: int,
) -> list[tuple[Job, StrategyRecommendation]]:
    recommendations = get_strategy_recommendations(db, user_id=user_id, tenant_id=tenant_id, limit=max(limit * 30, 100))
    selected: list[tuple[Job, StrategyRecommendation]] = []

    for recommendation in recommendations:
        if not _priority_is_eligible(recommendation):
            continue
        if _already_sent(db, user_id, recommendation.job_id):
            continue
        job = db.query(Job).filter(Job.id == recommendation.job_id, Job.tenant_id == tenant_id).first()
        if not job:
            continue


        eligibility = evaluate_job_eligibility(job)
        if not eligibility.get("eligible", True):
            logger.info(
                "job_blocked_by_eligibility tenant_id=%s user_id=%s job_id=%s blockers=%s",
                tenant_id,
                user_id,
                job.id,
                eligibility.get("blockers", []),
            )
            continue

        selected.append((job, recommendation))
        if len(selected) >= limit:
            break

    return selected


def _safe_update_last_run(db: Session, setting: AutomationSettings, now: datetime) -> None:
    setting.last_run = now
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _run_pipeline_for_setting(db: Session, setting: AutomationSettings, now: datetime) -> None:
    tenant_id = _tenant_id_for_user(db, setting.user_id)
    if tenant_id is None:
        logger.info("automation_user_skipped user_id=%s reason=no_active_tenant", setting.user_id)
        _safe_update_last_run(db, setting, now)
        return

    user = db.query(User).filter(User.id == setting.user_id, User.is_active.is_(True)).first()
    if not user:
        logger.info("automation_user_skipped tenant_id=%s user_id=%s reason=inactive_or_missing_user", tenant_id, setting.user_id)
        _safe_update_last_run(db, setting, now)
        return

    session = _user_whatsapp_session(db, tenant_id, user.id)
    if not session or not session.phone_number:
        logger.info("automation_user_skipped tenant_id=%s user_id=%s reason=whatsapp_not_configured", tenant_id, user.id)
        _safe_update_last_run(db, setting, now)
        return

    logger.info("automation_user_due tenant_id=%s user_id=%s mode=%s", tenant_id, user.id, setting.mode)

    try:
        inserted, skipped, _jobs, collected_by_provider, errors = ingest_jobs(
            db,
            tenant_id,
            source=_default_provider(),
            limit=_default_ingest_limit(),
            provider_options=_default_provider_options(),
            user=user,
        )
        logger.info(
            "automation_ingest_finished tenant_id=%s user_id=%s provider=%s limit=%s inserted=%s skipped=%s collected=%s errors=%s",
            tenant_id,
            user.id,
            _default_provider(),
            _default_ingest_limit(),
            inserted,
            skipped,
            collected_by_provider,
            errors,
        )
    except Exception as exc:
        db.rollback()
        logger.error("scheduler_error stage=ingestion tenant_id=%s user_id=%s error=%s", tenant_id, user.id, exc, exc_info=True)

    selected = _select_jobs_to_send(db, tenant_id, user.id, _max_notifications_per_run())
    if not selected:
        logger.info("no_jobs_to_send tenant_id=%s user_id=%s reason=no_new_eligible_jobs", tenant_id, user.id)
        _safe_update_last_run(db, setting, now)
        return

    service = WhatsAppSessionService(db)
    sent = 0
    failed = 0
    delay_seconds = _whatsapp_delay_seconds()

    for index, (job, recommendation) in enumerate(selected):
        if _already_sent(db, user.id, job.id):
            logger.info("automation_user_skipped tenant_id=%s user_id=%s job_id=%s reason=already_notified", tenant_id, user.id, job.id)
            continue


        eligibility = evaluate_job_eligibility(job)
        if not eligibility.get("eligible", True):
            logger.info(
                "job_blocked_by_eligibility tenant_id=%s user_id=%s job_id=%s blockers=%s",
                tenant_id,
                user.id,
                job.id,
                eligibility.get("blockers", []),
            )
            continue

        message = format_job_whatsapp_message(job, recommendation)
        try:
            ok, error = service.send_notification_message(session, message)
        except Exception as exc:
            ok = False
            error = str(exc)
            logger.error("whatsapp_notification_failed tenant_id=%s user_id=%s job_id=%s error=%s", tenant_id, user.id, job.id, exc, exc_info=True)

        if ok:
            if _save_job_notification(db, user.id, job.id):
                sent += 1
                logger.info("whatsapp_notification_sent tenant_id=%s user_id=%s job_id=%s", tenant_id, user.id, job.id)
        else:
            failed += 1
            logger.error("whatsapp_notification_failed tenant_id=%s user_id=%s job_id=%s error=%s", tenant_id, user.id, job.id, error)

        if delay_seconds > 0 and index < len(selected) - 1:
            time_module.sleep(delay_seconds)

    _safe_update_last_run(db, setting, now)
    logger.info(
        "automation_user_finished tenant_id=%s user_id=%s selected=%s sent=%s failed=%s",
        tenant_id,
        user.id,
        len(selected),
        sent,
        failed,
    )


def run_scheduler_once() -> None:
    if not settings.whatsapp_enabled:
        logger.info("automation_user_skipped reason=WHATSAPP_ENABLED_false")
        return

    now = datetime.utcnow()
    db = SessionLocal()
    try:
        due_settings = db.query(AutomationSettings).filter(AutomationSettings.enabled.is_(True)).all()
        logger.info("scheduler_tick enabled_settings=%s", len(due_settings))
        for setting in due_settings:
            try:
                if not _is_due(setting, now):
                    next_run = estimate_next_run(setting, now)
                    logger.info("automation_user_skipped user_id=%s reason=not_due next_run_estimate=%s", setting.user_id, to_app_timezone_iso(next_run) if next_run else None)
                    continue
                _run_pipeline_for_setting(db, setting, now)
            except Exception as exc:
                db.rollback()
                logger.error("scheduler_error stage=user user_id=%s error=%s", setting.user_id, exc, exc_info=True)
    except Exception as exc:
        db.rollback()
        logger.error("scheduler_error stage=tick error=%s", exc, exc_info=True)
    finally:
        db.close()


def _scheduler_loop() -> None:
    logger.info("scheduler_started loop_seconds=%s provider=%s ingest_limit=%s max_notifications_per_run=%s", _loop_seconds(), _default_provider(), _default_ingest_limit(), _max_notifications_per_run())
    while True:
        try:
            run_scheduler_once()
        except Exception as exc:
            logger.error("scheduler_error stage=loop error=%s", exc, exc_info=True)
        time_module.sleep(_loop_seconds())


def start_automation_scheduler() -> bool:
    global _started
    with _lock:
        if _started:
            logger.info("automation_user_skipped reason=scheduler_already_started")
            return False
        if not settings.automation_scheduler_enabled:
            logger.info("automation_user_skipped reason=AUTOMATION_SCHEDULER_ENABLED_false")
            return False
        if not settings.whatsapp_enabled:
            logger.info("automation_user_skipped reason=WHATSAPP_ENABLED_false")
            return False
        thread = threading.Thread(target=_scheduler_loop, name="applymize-automation-scheduler", daemon=True)
        thread.start()
        _started = True
        logger.info("scheduler_started background_thread=true")
        return True
