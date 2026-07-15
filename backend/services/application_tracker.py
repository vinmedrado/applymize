from sqlalchemy.orm import Session
from backend.models.application import Application, ApplicationEvent
from backend.models.job import Job
from backend.models.user import User
from backend.services.career_metrics_service import record_decision
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change

VALID_STATUSES = {"saved", "applied", "screening", "interview", "technical_test", "offer", "rejected", "withdrawn"}


def ensure_status(status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Status inválido: {status}")


def create_application(db: Session, tenant_id: int, user: User, job: Job, status: str, notes: str, next_action: str) -> Application:
    ensure_status(status)
    app = Application(tenant_id=tenant_id, user_id=user.id, job_id=job.id, status=status, notes=notes, next_action=next_action)
    db.add(app)
    db.flush()
    db.add(ApplicationEvent(tenant_id=tenant_id, application_id=app.id, from_status="", to_status=status, note="Candidatura criada"))
    record_decision(
        db,
        tenant_id=tenant_id,
        user_id=user.id,
        decision_type="application_created",
        title=f"Vaga adicionada: {job.title}",
        detail=f"Status inicial: {status}",
        job_id=job.id,
        application_id=app.id,
        metadata={"company": job.company, "status": status},
        commit=False,
    )
    db.commit()
    invalidate_cache(f"dashboard:summary:{tenant_id}:{user.id}")
    notify_dashboard_change(tenant_id, user.id)
    db.refresh(app)
    return app


def update_application(db: Session, tenant_id: int, app: Application, status: str | None, notes: str | None, next_action: str | None) -> Application:
    old_status = app.status
    if status is not None:
        ensure_status(status)
        app.status = status
    if notes is not None:
        app.notes = notes
    if next_action is not None:
        app.next_action = next_action

    if status is not None and status != old_status:
        db.add(ApplicationEvent(tenant_id=tenant_id, application_id=app.id, from_status=old_status, to_status=status, note="Status atualizado"))
        record_decision(
            db,
            tenant_id=tenant_id,
            user_id=app.user_id,
            decision_type="application_status_changed",
            title=f"Status atualizado: candidatura #{app.id}",
            detail=f"{old_status} → {status}",
            job_id=app.job_id,
            application_id=app.id,
            metadata={"from_status": old_status, "to_status": status},
            commit=False,
        )
    db.commit()
    invalidate_cache(f"dashboard:summary:{tenant_id}:{app.user_id}")
    notify_dashboard_change(tenant_id, app.user_id)
    db.refresh(app)
    return app
