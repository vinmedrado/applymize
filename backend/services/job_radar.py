from __future__ import annotations
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.models.radar import JobRadarRun
from backend.models.user import User
from backend.services.job_ingestion import ingest_jobs
from backend.services.strategy_engine import get_strategy_recommendations
from backend.services.notification_center import send_high_priority_notifications


def run_radar(db: Session, tenant_id: int, user: User, provider: str = "remoteok", limit: int = 25) -> dict:
    message = ""
    total_ingested = 0
    notified_count = 0
    try:
        result = ingest_jobs(db, tenant_id, provider=provider, limit=limit)
        total_ingested = int(result.get("inserted", 0)) if isinstance(result, dict) else 0
    except Exception as exc:
        message = f"Ingestão falhou sem quebrar sistema: {exc}"

    recs = get_strategy_recommendations(db, user.id, tenant_id, limit=50)
    high = [rec for rec in recs if rec.priority == "HIGH_PRIORITY"]

    if settings.notifications_enabled:
        notify = send_high_priority_notifications(db, tenant_id, user)
        notified_count = int(notify.get("sent", 0))

    run = JobRadarRun(
        tenant_id=tenant_id,
        user_id=user.id,
        provider=provider,
        total_ingested=total_ingested,
        high_priority_count=len(high),
        notified_count=notified_count,
        status="completed",
        message=message or "Radar executado com sucesso.",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return {
        "id": run.id,
        "enabled": settings.job_radar_enabled,
        "provider": provider,
        "total_ingested": total_ingested,
        "high_priority_count": len(high),
        "notified_count": notified_count,
        "status": run.status,
        "message": run.message,
    }


def radar_history(db: Session, tenant_id: int, user: User) -> list[dict]:
    rows = db.query(JobRadarRun).filter(
        JobRadarRun.tenant_id == tenant_id,
        JobRadarRun.user_id == user.id,
    ).order_by(JobRadarRun.created_at.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "provider": row.provider,
            "total_ingested": row.total_ingested,
            "high_priority_count": row.high_priority_count,
            "notified_count": row.notified_count,
            "status": row.status,
            "message": row.message,
            "created_at": row.created_at,
        }
        for row in rows
    ]
