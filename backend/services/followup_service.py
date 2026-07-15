from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.application import Application
from backend.models.job import Job
from backend.models.user import User


def days_since(dt) -> int:
    if not dt:
        return 0
    return max((datetime.utcnow() - dt).days, 0)


def should_follow_up(application: Application, after_days: int = 5) -> bool:
    return application.status in {"applied", "interview"} and days_since(application.updated_at) >= after_days


def generate_followup(db: Session, tenant_id: int, user: User, application_id: int, after_days: int = 5) -> dict:
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.tenant_id == tenant_id,
        Application.user_id == user.id,
    ).first()
    if not app:
        return {"found": False, "message": "Candidatura não encontrada.", "suggested": False}

    job = db.query(Job).filter(Job.id == app.job_id, Job.tenant_id == tenant_id).first()
    due = should_follow_up(app, after_days)
    message = (
        f"Olá! Passando para reforçar meu interesse na vaga de {job.title if job else 'informada'}. "
        "Continuo à disposição para conversar e enviar informações adicionais sobre meu perfil."
    )
    return {
        "found": True,
        "application_id": app.id,
        "job_id": app.job_id,
        "suggested": due,
        "days_since_update": days_since(app.updated_at),
        "next_action": "Enviar follow-up" if due else f"Aguardar até completar {after_days} dias",
        "message": message,
    }


def list_followups(db: Session, tenant_id: int, user: User) -> list[dict]:
    apps = db.query(Application).filter(Application.tenant_id == tenant_id, Application.user_id == user.id).all()
    return [generate_followup(db, tenant_id, user, app.id) for app in apps]
