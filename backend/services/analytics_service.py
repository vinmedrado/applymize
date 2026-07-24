from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.application import Application
from backend.models.job import Job
from backend.models.match_score import MatchScore
from backend.models.user import User
from backend.services.career_metrics_service import career_score_from_summary, get_score_trend, latest_decisions, upsert_daily_snapshot
from backend.services.job_role_relevance import relevant_jobs_for_user
from collections import Counter


def overview(db: Session, tenant_id: int, user: User) -> dict:
    tenant_jobs = db.query(Job).filter(Job.tenant_id == tenant_id).all()
    relevant_jobs = relevant_jobs_for_user(db, user, tenant_jobs)
    relevant_job_ids = [job.id for job in relevant_jobs]
    jobs_total = len(relevant_jobs)
    applications_total = (
        db.query(func.count(Application.id))
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .scalar()
        or 0
    )
    jobs_analyzed = (
        db.query(func.count(MatchScore.id))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.job_id.in_(relevant_job_ids))
        .scalar()
        or 0
    )
    avg_match = (
        db.query(func.avg(MatchScore.score))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.job_id.in_(relevant_job_ids))
        .scalar()
        or 0
    )
    high_match = (
        db.query(func.count(MatchScore.id))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.job_id.in_(relevant_job_ids), MatchScore.score >= 78)
        .scalar()
        or 0
    )

    status_rows = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .group_by(Application.status)
        .all()
    )
    status_counts = {status: int(count) for status, count in status_rows}
    response_statuses = {"interview", "technical_test", "offer"}
    response_rate = round((sum(status_counts.get(s, 0) for s in response_statuses) / max(applications_total, 1)) * 100, 2)

    source_rows = Counter(job.source or "manual" for job in relevant_jobs).most_common(8)
    role_rows = Counter(job.title or "Sem título" for job in relevant_jobs).most_common(8)

    result = {
        "jobs_total": int(jobs_total),
        "jobs_analyzed": int(jobs_analyzed),
        "applications_total": int(applications_total),
        "active_applications": int(sum(status_counts.get(s, 0) for s in ["applied", "screening", "interview", "technical_test", "offer"])),
        "response_rate": response_rate,
        "status_counts": status_counts,
        "top_sources": [{"source": source or "manual", "count": int(count)} for source, count in source_rows],
        "top_roles": [{"role": (role or "Sem título")[:60], "count": int(count)} for role, count in role_rows],
        "average_match_score": round(float(avg_match or 0), 2),
        "high_match_jobs": int(high_match),
        "source_diversity": len(source_rows),
        "career_efficiency": round((high_match / max(jobs_analyzed, 1)) * 100, 2) if jobs_analyzed else 0,
        "warnings": [] if jobs_total or applications_total else ["Ainda não há dados suficientes. Importe vagas e registre candidaturas."],
    }
    result["career_score"] = career_score_from_summary({
        "average_match_score": result["average_match_score"],
        "response_rate": result["response_rate"],
        "ranked_jobs": result["jobs_analyzed"],
        "high_match_jobs": result["high_match_jobs"],
        "applications_total": result["applications_total"],
    })
    upsert_daily_snapshot(db, tenant_id, user.id, {
        "total_jobs": result["jobs_total"],
        "applications_total": result["applications_total"],
        "active_applications": result["active_applications"],
        "ranked_jobs": result["jobs_analyzed"],
        "average_match_score": result["average_match_score"],
        "high_match_jobs": result["high_match_jobs"],
        "response_rate": result["response_rate"],
    })
    db.commit()
    result["score_trend"] = get_score_trend(db, tenant_id, user.id, limit=30)
    result["decision_history"] = latest_decisions(db, tenant_id, user.id, limit=20)
    return result
