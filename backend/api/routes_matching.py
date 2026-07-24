from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.schemas.matching import MatchScoreOut, RankOut
from backend.services.matching_engine import serialize_match, upsert_match_score
from backend.services.job_role_relevance import relevant_jobs_for_user

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/jobs/{job_id}", response_model=MatchScoreOut)
def score_job(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    score = upsert_match_score(db, ctx.tenant_id, ctx.user, job)
    return serialize_match(score)


@router.post("/rank", response_model=list[RankOut])
def rank_jobs(limit: int = Query(25, ge=1, le=200), db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    candidates = (
        db.query(Job)
        .filter(Job.tenant_id == ctx.tenant_id)
        .order_by(Job.created_at.desc())
        .limit(max(limit * 20, 500))
        .all()
    )
    jobs = relevant_jobs_for_user(db, ctx.user, candidates)[:limit]
    ranked = []
    for job in jobs:
        score = upsert_match_score(db, ctx.tenant_id, ctx.user, job)
        ranked.append(RankOut(job_id=job.id, title=job.title, company=job.company, score=score.score, explanation=score.explanation))
    return sorted(ranked, key=lambda item: item.score, reverse=True)
