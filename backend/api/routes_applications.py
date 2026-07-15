from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.application import Application, ApplicationEvent
from backend.models.job import Job
from backend.schemas.application import ApplicationCreate, ApplicationEventOut, ApplicationOut, ApplicationUpdate
from backend.services.application_tracker import create_application, update_application

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/", response_model=ApplicationOut)
def create(payload: ApplicationCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == payload.job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    try:
        return create_application(db, ctx.tenant_id, ctx.user, job, payload.status, payload.notes, payload.next_action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/", response_model=list[ApplicationOut])
def list_all(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return db.query(Application).filter(Application.tenant_id == ctx.tenant_id, Application.user_id == ctx.user.id).order_by(Application.updated_at.desc()).all()


@router.get("/{application_id}", response_model=ApplicationOut)
def get_one(application_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    app = db.query(Application).filter(Application.id == application_id, Application.tenant_id == ctx.tenant_id, Application.user_id == ctx.user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    return app


@router.patch("/{application_id}", response_model=ApplicationOut)
def update(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    app = db.query(Application).filter(Application.id == application_id, Application.tenant_id == ctx.tenant_id, Application.user_id == ctx.user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    try:
        return update_application(db, ctx.tenant_id, app, payload.status, payload.notes, payload.next_action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{application_id}/history", response_model=list[ApplicationEventOut])
def history(application_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    app = db.query(Application).filter(Application.id == application_id, Application.tenant_id == ctx.tenant_id, Application.user_id == ctx.user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    return db.query(ApplicationEvent).filter(ApplicationEvent.tenant_id == ctx.tenant_id, ApplicationEvent.application_id == app.id).order_by(ApplicationEvent.created_at.asc()).all()
