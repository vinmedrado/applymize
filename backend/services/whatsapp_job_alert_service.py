from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.core.logging import get_logger
from backend.models.job import Job
from backend.models.notification import NotificationLog
from backend.models.user import User
from backend.models.whatsapp_session import WhatsAppSession
from backend.services.strategy_engine import StrategyRecommendation, get_strategy_recommendations
from backend.services.user_settings_service import get_or_create_settings
from backend.services.job_eligibility_filter import evaluate_job_eligibility
from backend.services.whatsapp_session_service import WhatsAppSessionService

def send_job_alert_email(to_email: str, subject: str, message: str) -> bool:
    return False

logger = get_logger(__name__)

CHANNEL_NAME = "whatsapp_job_alert"
EMAIL_FALLBACK_CHANNEL = "email_job_alert"


def normalize_min_priority(value: str | None) -> str:
    raw = (value or "MEDIUM").strip().upper()
    if raw in {"HIGH", "ALTA", "HIGH_PRIORITY"}:
        return "HIGH"
    if raw in {"MEDIUM", "MEDIA", "MÉDIA", "MEDIUM_PRIORITY"}:
        return "MEDIUM"
    if raw in {"LOW", "BAIXA", "LOW_PRIORITY"}:
        return "LOW"
    return "MEDIUM"


def priority_rank(priority: str | None) -> int:
    return {"LOW_PRIORITY": 1, "MEDIUM_PRIORITY": 2, "HIGH_PRIORITY": 3}.get(priority or "", 0)


def minimum_rank(minimum: str | None) -> int:
    return {"LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(normalize_min_priority(minimum), 2)


def _priority_allowed(priority: str, minimum: str | None = None) -> bool:
    return priority_rank(priority) >= minimum_rank(minimum or settings.notification_min_priority)


def _human_priority(priority: str | None) -> str:
    mapping = {
        "HIGH_PRIORITY": "Alta",
        "MEDIUM_PRIORITY": "Média",
        "LOW_PRIORITY": "Baixa",
    }
    return mapping.get(priority or "", priority or "Não informado")


def format_job_whatsapp_message(job: Job, recommendation: StrategyRecommendation | None = None) -> str:
    model = "Remoto" if job.remote else "Presencial/Híbrido"
    title = job.title or "Não informado"
    company = job.company or "Não informado"
    location = job.location or "Não informado"
    employment_type = job.employment_type or "Não informado"
    source = (job.source or "Applymize").upper()
    url = job.url or "Link não informado"

    score_line = ""
    priority_line = ""
    reason_line = ""
    if recommendation:
        score_line = f"\n⭐ Score Applymize: {recommendation.strategy_score:.2f}"
        priority_line = f"\n🔥 Prioridade: {_human_priority(recommendation.priority)}"
        reason_line = f"\n🧠 Por que aplicar: {recommendation.explanation}"

    headline = "HOME OFFICE" if job.remote else "OPORTUNIDADE"
    now = datetime.now().strftime("%d/%m/%Y às %H:%M")

    return f"""🎯 VAGA APPLYMIZE - {headline}!

💼 Vaga: {title}
🏢 Empresa: {company}
📍 Local: {location}
💻 Modelo: {model}
📄 Tipo: {employment_type}
♿ PCD: Não informado
🌐 Fonte: {source}
📅 Data: {now}{score_line}{priority_line}{reason_line}

🔗 Clique aqui para aplicar:
{url}"""


def format_job_summary_message(items: list[tuple[Job, StrategyRecommendation]]) -> str:
    now = datetime.now().strftime("%d/%m/%Y às %H:%M")
    lines = [
        "🎯 TOP VAGAS APPLYMIZE",
        f"📅 {now}",
        "",
        f"Encontrei {len(items)} oportunidade(s) prioritária(s) para você:",
        "",
    ]
    for index, (job, rec) in enumerate(items, start=1):
        model = "Remoto" if job.remote else "Presencial/Híbrido"
        lines.extend([
            f"{index}. 💼 {job.title or 'Não informado'}",
            f"   🏢 {job.company or 'Não informado'}",
            f"   📍 {job.location or 'Local não informado'} • {model}",
            f"   ⭐ Score: {rec.strategy_score:.2f} • Prioridade: {_human_priority(rec.priority)}",
            f"   🔗 {job.url or 'Link não informado'}",
            "",
        ])
    lines.append("Dica: priorize as vagas com maior score e ajuste o currículo antes de aplicar.")
    return "\n".join(lines).strip()


def _already_notified(db: Session, tenant_id: int, user_id: int, job_id: int, channel: str = CHANNEL_NAME) -> bool:
    return db.query(NotificationLog).filter(
        NotificationLog.tenant_id == tenant_id,
        NotificationLog.user_id == user_id,
        NotificationLog.job_id == job_id,
        NotificationLog.channel == channel,
        NotificationLog.status == "sent",
    ).first() is not None


def _save_notification_log(
    db: Session,
    tenant_id: int,
    user_id: int,
    job_id: int,
    status: str,
    message: str,
    error_message: str = "",
    channel: str = CHANNEL_NAME,
) -> NotificationLog | None:
    log = NotificationLog(
        tenant_id=tenant_id,
        user_id=user_id,
        job_id=job_id,
        channel=channel,
        status=status,
        message=message,
        sent_at=datetime.utcnow(),
        error_message=error_message,
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(log)
        return log
    except IntegrityError:
        db.rollback()
        return db.query(NotificationLog).filter(
            NotificationLog.tenant_id == tenant_id,
            NotificationLog.user_id == user_id,
            NotificationLog.job_id == job_id,
            NotificationLog.channel == channel,
        ).first()


def _get_user_session(db: Session, tenant_id: int, user_id: int) -> WhatsAppSession | None:
    return db.query(WhatsAppSession).filter(
        WhatsAppSession.tenant_id == tenant_id,
        WhatsAppSession.user_id == user_id,
    ).first()


def _select_recommendations(db: Session, tenant_id: int, user: User, max_per_run: int) -> list[tuple[Job, StrategyRecommendation]]:
    prefs = get_or_create_settings(db, user.id)
    if not prefs.job_alerts_enabled:
        return []

    recommendations = get_strategy_recommendations(db, user.id, tenant_id, limit=max(max_per_run * 30, 100))
    selected: list[tuple[Job, StrategyRecommendation]] = []

    for rec in recommendations:
        if not _priority_allowed(rec.priority, prefs.job_alert_min_priority):
            continue
        job = db.query(Job).filter(Job.id == rec.job_id, Job.tenant_id == tenant_id).first()
        if not job:
            continue
        if prefs.job_alert_remote_only and not job.remote:
            continue
        if _already_notified(db, tenant_id, user.id, job.id, CHANNEL_NAME):
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

        selected.append((job, rec))
        if len(selected) >= max_per_run:
            break
    return selected


def send_job_alerts_for_user(
    db: Session,
    tenant_id: int,
    user: User,
    limit: int | None = None,
) -> dict[str, Any]:
    if not settings.whatsapp_enabled:
        return {"enabled": False, "sent": 0, "skipped": 0, "reason": "WHATSAPP_ENABLED=false"}

    prefs = get_or_create_settings(db, user.id)
    if not prefs.job_alerts_enabled:
        return {"enabled": False, "sent": 0, "skipped": 0, "reason": "Alertas desativados nas preferências do usuário."}
    if prefs.job_alert_frequency != "immediate":
        return {"enabled": True, "sent": 0, "skipped": 0, "reason": f"Frequência configurada como {prefs.job_alert_frequency}."}

    session = _get_user_session(db, tenant_id, user.id)
    if not session or not session.phone_number:
        return {"enabled": False, "sent": 0, "skipped": 0, "reason": "WhatsApp do usuário não configurado."}

    max_per_run = max(int(limit or settings.notification_max_per_run or 5), 1)
    selected = _select_recommendations(db, tenant_id, user, max_per_run)
    service = WhatsAppSessionService(db)

    results: list[dict[str, Any]] = []
    sent = 0
    skipped = 0

    if selected and prefs.job_alert_summary_mode:
        message = format_job_summary_message(selected)
        ok, error = service.send_notification_message(session, message)
        channel_status = "sent" if ok else "failed"
        for job, rec in selected:
            log = _save_notification_log(db, tenant_id, user.id, job.id, channel_status, message, error, CHANNEL_NAME)
            results.append({"job_id": job.id, "status": channel_status, "error_message": error, "log_id": log.id if log else None, "score": rec.strategy_score, "priority": rec.priority})
        if ok:
            sent = len(selected)
        else:
            skipped = len(selected)
            if prefs.job_alert_email_fallback:
                email_ok = send_job_alert_email(user.email, "Top vagas Applymize", message)
                email_status = "sent" if email_ok else "failed"
                for job, _rec in selected:
                    _save_notification_log(db, tenant_id, user.id, job.id, email_status, message, "" if email_ok else "Falha no fallback por e-mail.", EMAIL_FALLBACK_CHANNEL)
                results.append({"channel": EMAIL_FALLBACK_CHANNEL, "status": email_status, "jobs": len(selected)})
        logger.info("whatsapp_job_alerts_done tenant_id=%s user_id=%s summary=true selected=%s sent=%s skipped=%s", tenant_id, user.id, len(selected), sent, skipped)
        return {"enabled": True, "configured": True, "summary_mode": True, "selected": len(selected), "sent": sent, "skipped": skipped, "max_per_run": max_per_run, "results": results}

    for job, rec in selected:

        eligibility = evaluate_job_eligibility(job)
        if not eligibility.get("eligible", True):
            skipped += 1
            logger.info(
                "job_blocked_by_eligibility tenant_id=%s user_id=%s job_id=%s blockers=%s",
                tenant_id,
                user.id,
                job.id,
                eligibility.get("blockers", []),
            )
            results.append({"job_id": job.id, "status": "blocked_by_eligibility", "blockers": eligibility.get("blockers", [])})
            continue

        message = format_job_whatsapp_message(job, rec)
        ok, error = service.send_notification_message(session, message)
        status = "sent" if ok else "failed"
        log = _save_notification_log(db, tenant_id, user.id, job.id, status, message, error, CHANNEL_NAME)
        if ok:
            sent += 1
        else:
            skipped += 1
            if prefs.job_alert_email_fallback:
                email_ok = send_job_alert_email(user.email, f"Vaga Applymize: {job.title}", message)
                _save_notification_log(db, tenant_id, user.id, job.id, "sent" if email_ok else "failed", message, "" if email_ok else "Falha no fallback por e-mail.", EMAIL_FALLBACK_CHANNEL)
        results.append({"job_id": job.id, "status": status, "error_message": error, "log_id": log.id if log else None, "score": rec.strategy_score, "priority": rec.priority})

    logger.info(
        "whatsapp_job_alerts_done tenant_id=%s user_id=%s selected=%s sent=%s skipped=%s results=%s",
        tenant_id,
        user.id,
        len(selected),
        sent,
        skipped,
        [asdict(r.factors) for _j, r in selected[:3]],
    )
    return {"enabled": True, "configured": True, "summary_mode": False, "selected": len(selected), "sent": sent, "skipped": skipped, "max_per_run": max_per_run, "results": results}


def send_job_alerts_for_user_background(tenant_id: int, user_id: int, limit: int | None = None) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("whatsapp_job_alert_background_missing_user tenant_id=%s user_id=%s", tenant_id, user_id)
            return
        result = send_job_alerts_for_user(db=db, tenant_id=tenant_id, user=user, limit=limit)
        logger.info("whatsapp_job_alert_background_done tenant_id=%s user_id=%s result=%s", tenant_id, user_id, result)
    except Exception as exc:
        logger.warning("whatsapp_job_alert_background_failed tenant_id=%s user_id=%s error=%s", tenant_id, user_id, exc)
    finally:
        db.close()
