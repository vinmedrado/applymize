from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, date
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.application import Application
from backend.models.application_agent import ApplicationAgentEvent, ApplicationQueueItem
from backend.models.job import Job
from backend.models.user import User
from backend.services.cv_engine import generate_cv_content
from backend.services.profile_service import profile_context_text, serialize_profile
from backend.services.strategy_engine import get_strategy_recommendations

logger = get_logger(__name__)

QUEUE_STATUSES = {"queued", "approved", "skipped", "applied", "failed"}
APPLY_DAILY_LIMIT = int(getattr(settings, "application_agent_daily_limit", 10) or 10)
MIN_PROFILE_COMPLETENESS = float(getattr(settings, "application_agent_min_profile_completeness", 35) or 35)


def grade_from_score(score: float) -> str:
    if score >= 88:
        return "A"
    if score >= 78:
        return "B"
    if score >= 68:
        return "C"
    if score >= 58:
        return "D"
    return "F"


def build_cover_message(user: User, job: Job, strategy_score: float) -> str:
    return (
        f"Olá, tenho interesse na vaga de {job.title} na {job.company}. "
        f"Meu perfil combina com os requisitos da posição e o score estratégico interno foi {strategy_score:.1f}. "
        f"Tenho experiência em {user.skills}. Posso contribuir com execução prática, organização e melhoria contínua. "
        "Fico à disposição para conversar sobre a oportunidade."
    )


def serialize_queue_item(item: ApplicationQueueItem) -> dict:
    job = item.job
    return {
        "id": item.id,
        "tenant_id": item.tenant_id,
        "user_id": item.user_id,
        "job_id": item.job_id,
        "strategy_score": item.strategy_score,
        "evaluation_grade": item.evaluation_grade,
        "generated_cv": item.generated_cv,
        "cover_message": item.cover_message,
        "status": item.status,
        "failure_reason": item.failure_reason,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "job_title": job.title if job else None,
        "company": job.company if job else None,
        "location": job.location if job else None,
        "remote": job.remote if job else None,
        "job_url": job.url if job else None,
    }


def daily_applied_count(db: Session, tenant_id: int, user_id: int) -> int:
    today = date.today()
    return (
        db.query(ApplicationQueueItem)
        .filter(
            ApplicationQueueItem.tenant_id == tenant_id,
            ApplicationQueueItem.user_id == user_id,
            ApplicationQueueItem.status == "applied",
        )
        .all()
    ).count if False else sum(
        1 for item in db.query(ApplicationQueueItem).filter(
            ApplicationQueueItem.tenant_id == tenant_id,
            ApplicationQueueItem.user_id == user_id,
            ApplicationQueueItem.status == "applied",
        ).all()
        if item.updated_at.date() == today
    )


def has_existing_application(db: Session, tenant_id: int, user_id: int, job_id: int) -> bool:
    return db.query(Application).filter(
        Application.tenant_id == tenant_id,
        Application.user_id == user_id,
        Application.job_id == job_id,
    ).first() is not None


def get_queue(db: Session, tenant_id: int, user_id: int) -> list[ApplicationQueueItem]:
    return (
        db.query(ApplicationQueueItem)
        .filter(ApplicationQueueItem.tenant_id == tenant_id, ApplicationQueueItem.user_id == user_id)
        .order_by(ApplicationQueueItem.strategy_score.desc(), ApplicationQueueItem.created_at.desc())
        .all()
    )


def create_event(db: Session, tenant_id: int, user_id: int, queue_item_id: int, action: str, note: str = "") -> None:
    db.add(
        ApplicationAgentEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            queue_item_id=queue_item_id,
            action=action,
            note=note,
        )
    )


def build_queue(
    db: Session,
    tenant_id: int,
    user: User,
    limit: int = 10,
    min_strategy_score: float = 58,
    generate_cv: bool = True,
    generate_message: bool = True,
) -> dict:
    profile_data = serialize_profile(db, tenant_id, user.id)
    context = profile_context_text(db, tenant_id, user)
    if profile_data.get("completeness", 0) < MIN_PROFILE_COMPLETENESS:
        logger.info("application_queue_blocked_incomplete_profile tenant_id=%s user_id=%s completeness=%s", tenant_id, user.id, profile_data.get("completeness", 0))
        return {"created": 0, "skipped": 0, "blocked_low_priority": 0, "daily_limit_remaining": max(APPLY_DAILY_LIMIT - daily_applied_count(db, tenant_id, user.id), 0), "items": []}

    recommendations = get_strategy_recommendations(db, user.id, tenant_id, limit=max(limit * 3, limit))
    created = 0
    skipped = 0
    blocked_low_priority = 0
    items: list[ApplicationQueueItem] = []

    for recommendation in recommendations:
        if created >= limit:
            break

        if recommendation.priority == "LOW_PRIORITY" or recommendation.strategy_score < min_strategy_score:
            blocked_low_priority += 1
            continue

        existing_queue = db.query(ApplicationQueueItem).filter(
            ApplicationQueueItem.tenant_id == tenant_id,
            ApplicationQueueItem.user_id == user.id,
            ApplicationQueueItem.job_id == recommendation.job_id,
        ).first()
        if existing_queue:
            skipped += 1
            items.append(existing_queue)
            continue

        if has_existing_application(db, tenant_id, user.id, recommendation.job_id):
            skipped += 1
            continue

        job = db.query(Job).filter(Job.id == recommendation.job_id, Job.tenant_id == tenant_id).first()
        if not job:
            skipped += 1
            continue

        queue_item = ApplicationQueueItem(
            tenant_id=tenant_id,
            user_id=user.id,
            job_id=job.id,
            strategy_score=recommendation.strategy_score,
            evaluation_grade=grade_from_score(recommendation.strategy_score),
            generated_cv=generate_cv_content(user, job, profile_data=profile_data, profile_context=context) if generate_cv else "",
            cover_message=(build_cover_message(user, job, recommendation.strategy_score) + ("\n\nAviso: complete seu perfil para melhorar a personalização." if profile_data.get("completeness", 0) < 50 else "")) if generate_message else "",
            status="queued",
        )
        db.add(queue_item)
        db.flush()
        create_event(db, tenant_id, user.id, queue_item.id, "queued", "Item criado pelo Application Agent.")
        items.append(queue_item)
        created += 1

    db.commit()
    for item in items:
        db.refresh(item)

    logger.info(
        "application_queue_built tenant_id=%s user_id=%s created=%s skipped=%s blocked_low_priority=%s",
        tenant_id,
        user.id,
        created,
        skipped,
        blocked_low_priority,
    )

    return {
        "created": created,
        "skipped": skipped,
        "blocked_low_priority": blocked_low_priority,
        "daily_limit_remaining": max(APPLY_DAILY_LIMIT - daily_applied_count(db, tenant_id, user.id), 0),
        "items": items,
    }


def get_queue_item(db: Session, tenant_id: int, user_id: int, queue_id: int) -> ApplicationQueueItem | None:
    return db.query(ApplicationQueueItem).filter(
        ApplicationQueueItem.id == queue_id,
        ApplicationQueueItem.tenant_id == tenant_id,
        ApplicationQueueItem.user_id == user_id,
    ).first()


def approve_item(db: Session, tenant_id: int, user: User, item: ApplicationQueueItem) -> ApplicationQueueItem:
    if item.status in {"applied", "skipped"}:
        return item
    item.status = "approved"
    create_event(db, tenant_id, user.id, item.id, "approved", "Usuário aprovou candidatura assistida.")
    db.commit()
    db.refresh(item)
    return item


def skip_item(db: Session, tenant_id: int, user: User, item: ApplicationQueueItem) -> ApplicationQueueItem:
    item.status = "skipped"
    create_event(db, tenant_id, user.id, item.id, "skipped", "Usuário pulou candidatura.")
    db.commit()
    db.refresh(item)
    return item


def mark_applied(db: Session, tenant_id: int, user: User, item: ApplicationQueueItem) -> ApplicationQueueItem:
    if item.status == "skipped":
        item.status = "failed"
        item.failure_reason = "Item pulado não pode ser marcado como aplicado."
        create_event(db, tenant_id, user.id, item.id, "failed", item.failure_reason)
        db.commit()
        db.refresh(item)
        return item

    if item.strategy_score < 58:
        item.status = "failed"
        item.failure_reason = "Score baixo bloqueado por regra anti-spam."
        create_event(db, tenant_id, user.id, item.id, "failed", item.failure_reason)
        db.commit()
        db.refresh(item)
        return item

    if daily_applied_count(db, tenant_id, user.id) >= APPLY_DAILY_LIMIT:
        item.status = "failed"
        item.failure_reason = "Limite diário de candidaturas atingido."
        create_event(db, tenant_id, user.id, item.id, "failed", item.failure_reason)
        db.commit()
        db.refresh(item)
        return item

    existing_app = db.query(Application).filter(
        Application.tenant_id == tenant_id,
        Application.user_id == user.id,
        Application.job_id == item.job_id,
    ).first()
    if not existing_app:
        db.add(
            Application(
                tenant_id=tenant_id,
                user_id=user.id,
                job_id=item.job_id,
                status="applied",
                notes="Marcada como aplicada via Application Agent.",
                next_action="Acompanhar retorno.",
            )
        )

    item.status = "applied"
    item.failure_reason = ""
    create_event(db, tenant_id, user.id, item.id, "applied", "Usuário marcou como aplicada manualmente.")
    db.commit()
    db.refresh(item)
    return item
