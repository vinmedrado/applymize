from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.schemas.resume import ResumeOut
from backend.services.cv_engine import create_resume

router = APIRouter(prefix="/api/cv", tags=["cv"])


@router.post("/jobs/{job_id}", response_model=ResumeOut)
def generate_cv(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return create_resume(db, ctx.tenant_id, ctx.user, job)
