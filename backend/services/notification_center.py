from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.job import Job
from backend.models.notification import NotificationLog
from backend.models.user import User
from backend.services.notifiers.base import NotificationResult
from backend.services.notifiers.telegram_notifier import TelegramNotifier
from backend.services.notifiers.whatsapp_evolution_notifier import WhatsAppEvolutionNotifier
from backend.services.strategy_engine import get_strategy_recommendations

logger = get_logger(__name__)


def enabled_channels(db: Session | None = None, tenant_id: int | None = None, user: User | None = None):
    return [TelegramNotifier(), WhatsAppEvolutionNotifier(db, user.id if user else None, tenant_id)]


def notification_settings() -> dict[str, Any]:
    return {
        "enabled": settings.notifications_enabled,
        "max_per_run": settings.notification_max_per_run,
        "min_priority": settings.notification_min_priority,
        "telegram": {"configured": TelegramNotifier().is_configured()},
        "whatsapp_evolution": {"configured": bool(settings.whatsapp_enabled and settings.evolution_api_url and settings.evolution_api_key), "mode": "per_user_session"},
        "auto_send": False,
        "responsible_use": "Envio automático permanece desativado por padrão. Use apenas alertas controlados.",
    }


def format_job_alert(job: Job, score: float | None = None, priority: str | None = None) -> str:
    parts = [
        "🚀 Vaga prioritária encontrada",
        f"Cargo: {job.title}",
        f"Empresa: {job.company}",
        f"Local: {job.location or 'Não informado'}",
        f"Remoto: {'sim' if job.remote else 'não'}",
    ]
    if priority:
        parts.append(f"Prioridade: {priority}")
    if score is not None:
        parts.append(f"Score: {score}%")
    if job.url:
        parts.append(f"Link: {job.url}")
    return "\n".join(parts)


def already_notified(db: Session, tenant_id: int, user_id: int, job_id: int, channel: str) -> bool:
    return db.query(NotificationLog).filter(
        NotificationLog.tenant_id == tenant_id,
        NotificationLog.user_id == user_id,
        NotificationLog.job_id == job_id,
        NotificationLog.channel == channel,
    ).first() is not None


def save_log(db: Session, tenant_id: int, user_id: int, job_id: int, result: NotificationResult) -> NotificationLog:
    log = NotificationLog(
        tenant_id=tenant_id,
        user_id=user_id,
        job_id=job_id,
        channel=result.channel,
        status=result.status,
        message=result.message,
        sent_at=datetime.utcnow(),
        error_message=result.error_message,
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(log)
    except IntegrityError:
        db.rollback()
        log = db.query(NotificationLog).filter(
            NotificationLog.tenant_id == tenant_id,
            NotificationLog.user_id == user_id,
            NotificationLog.job_id == job_id,
            NotificationLog.channel == result.channel,
        ).first()
    return log


def send_test_notification(db: Session, tenant_id: int, user: User) -> dict[str, Any]:
    if not settings.notifications_enabled:
        return {
            "enabled": False,
            "sent": 0,
            "results": [{"channel": "all", "status": "disabled", "error_message": "Notificações desativadas. Configure NOTIFICATIONS_ENABLED=true."}],
        }
    message = "✅ Teste Applymize: notificações configuradas para alertas controlados de vagas prioritárias."
    results = [asdict(notifier.send_message(message)) for notifier in enabled_channels(db, tenant_id, user)]
    return {"enabled": True, "sent": sum(1 for item in results if item["status"] == "sent"), "results": results}


def send_high_priority_notifications(db: Session, tenant_id: int, user: User) -> dict[str, Any]:
    if not settings.notifications_enabled:
        return {
            "enabled": False,
            "sent": 0,
            "skipped": 0,
            "results": [{"channel": "all", "status": "disabled", "error_message": "Notificações desativadas. Configure NOTIFICATIONS_ENABLED=true."}],
        }

    max_per_run = max(int(settings.notification_max_per_run or 5), 1)
    min_priority = (settings.notification_min_priority or "HIGH").upper()
    recommendations = get_strategy_recommendations(db, user.id, tenant_id, limit=50)

    selected = []
    for rec in recommendations:
        allowed = rec.priority == "HIGH_PRIORITY" if min_priority == "HIGH" else rec.priority in {"HIGH_PRIORITY", "MEDIUM_PRIORITY"}
        if allowed:
            selected.append(rec)
        if len(selected) >= max_per_run:
            break

    results = []
    sent = 0
    skipped = 0

    for rec in selected:
        job = db.query(Job).filter(Job.id == rec.job_id, Job.tenant_id == tenant_id).first()
        if not job:
            continue
        message = format_job_alert(job, rec.strategy_score, rec.priority)
        for notifier in enabled_channels(db, tenant_id, user):
            if already_notified(db, tenant_id, user.id, job.id, notifier.channel_name):
                skipped += 1
                results.append({"channel": notifier.channel_name, "job_id": job.id, "status": "duplicate", "error_message": "Vaga já notificada neste canal."})
                continue
            result = notifier.send_message(message)
            log = save_log(db, tenant_id, user.id, job.id, result)
            if result.status == "sent":
                sent += 1
            results.append({"channel": result.channel, "job_id": job.id, "status": result.status, "error_message": result.error_message, "log_id": log.id if log else None})

    logger.info("notifications_high_priority_done tenant_id=%s user_id=%s selected=%s sent=%s skipped=%s", tenant_id, user.id, len(selected), sent, skipped)
    return {"enabled": True, "sent": sent, "skipped": skipped, "selected": len(selected), "max_per_run": max_per_run, "results": results}
