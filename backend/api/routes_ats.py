from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.schemas.ats import AtsAnalysisOut
from backend.services.ats_analyzer import analyze_resume, serialize_analysis

router = APIRouter(prefix="/api/ats", tags=["ats-analyzer"])


@router.get("/analyze-me", response_model=AtsAnalysisOut)
def analyze_me(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    analysis = analyze_resume(db, ctx.tenant_id, ctx.user, None)
    return serialize_analysis(analysis)


@router.get("/analyze-job/{job_id}", response_model=AtsAnalysisOut)
def analyze_job(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    analysis = analyze_resume(db, ctx.tenant_id, ctx.user, job)
    return serialize_analysis(analysis)
