from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.services.cover_letter_service import generate_cover_messages

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])


@router.get("/jobs/{job_id}")
def cover(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return generate_cover_messages(db, ctx.tenant_id, ctx.user, job)
