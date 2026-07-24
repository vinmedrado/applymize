from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.application import Application
from backend.models.job import Job
from backend.services.job_role_relevance import relevant_jobs_for_user
from backend.models.user import User

router = APIRouter(prefix="/api/recruiter", tags=["recruiter"])

PIPELINE = ["saved", "applied", "screening", "interview", "technical", "offer", "hired", "rejected"]

@router.get("/dashboard")
def recruiter_dashboard(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    candidates = db.query(Job).filter(Job.tenant_id == ctx.tenant_id).order_by(Job.created_at.desc()).limit(500).all()
    jobs = relevant_jobs_for_user(db, ctx.user, candidates)[:8]
    applications = db.query(Application).filter(Application.tenant_id == ctx.tenant_id).order_by(Application.updated_at.desc()).limit(50).all()
    users_by_id = {user.id: user for user in db.query(User).filter(User.id.in_([a.user_id for a in applications] or [ctx.user.id])).all()}
    jobs_by_id = {job.id: job for job in jobs}
    pipeline = {stage: 0 for stage in PIPELINE}
    candidates = []
    for app in applications:
        pipeline[app.status] = pipeline.get(app.status, 0) + 1
        job = jobs_by_id.get(app.job_id) or db.query(Job).filter(Job.id == app.job_id, Job.tenant_id == ctx.tenant_id).first()
        user = users_by_id.get(app.user_id)
        score = 78
        if job and user:
            text = f"{job.title} {job.description} {job.requirements}".lower()
            matches = sum(1 for skill in (user.skills or "").split(",") if skill.strip().lower() in text)
            score = min(96, 60 + matches * 8)
        candidates.append({
            "application_id": app.id,
            "candidate": user.full_name if user else "Candidato",
            "job": job.title if job else "Vaga",
            "company": job.company if job else "",
            "status": app.status,
            "score": score,
            "risk": "baixo" if score >= 80 else "médio",
        })
    return {
        "pipeline": pipeline,
        "open_jobs": [{"id": job.id, "title": job.title, "company": job.company, "location": job.location} for job in jobs],
        "candidates": candidates,
        "summary": {
            "active_jobs": len(jobs),
            "candidates": len(candidates),
            "avg_score": round(sum(c["score"] for c in candidates) / max(len(candidates), 1), 1),
        },
    }
