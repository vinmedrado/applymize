from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.schemas.interview import InterviewPrepOut
from backend.services.interview_engine import generate_interview_prep
from backend.services.profile_service import profile_context_text

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.get("/jobs/{job_id}", response_model=InterviewPrepOut)
def prepare(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return generate_interview_prep(ctx.user, job, profile_context=profile_context_text(db, ctx.tenant_id, ctx.user))
