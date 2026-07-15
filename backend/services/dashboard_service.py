from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.application import Application
from backend.models.job import Job
from backend.models.match_score import MatchScore
from backend.models.radar import JobRadarRun
from backend.models.user import User
from backend.services.career_metrics_service import career_score_from_summary, get_score_trend, latest_decisions, upsert_daily_snapshot
from backend.services.dashboard_cache import get_cache, set_cache


def _status_label(status: str) -> str:
    return {
        "saved": "Salvas",
        "applied": "Aplicadas",
        "screening": "Triagem",
        "interview": "Entrevistas",
        "technical_test": "Teste técnico",
        "offer": "Propostas",
        "rejected": "Recusadas",
        "withdrawn": "Desistências",
    }.get(status, status)


def dashboard_summary(db: Session, tenant_id: int, user: User, use_cache: bool = True) -> dict[str, Any]:
    cache_key = f"dashboard:summary:{tenant_id}:{user.id}"
    if use_cache:
        cached = get_cache(cache_key)
        if cached:
            return cached

    total_jobs = db.query(func.count(Job.id)).filter(Job.tenant_id == tenant_id).scalar() or 0

    applications_total = (
        db.query(func.count(Application.id))
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .scalar()
        or 0
    )

    active_applications = (
        db.query(func.count(Application.id))
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .filter(Application.status.in_(["applied", "screening", "interview", "technical_test", "offer"]))
        .scalar()
        or 0
    )

    ranked_jobs = (
        db.query(func.count(MatchScore.id))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id)
        .scalar()
        or 0
    )

    avg_match = (
        db.query(func.avg(MatchScore.score))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id)
        .scalar()
        or 0
    )

    high_match_jobs = (
        db.query(func.count(MatchScore.id))
        .filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.score >= 78)
        .scalar()
        or 0
    )

    last_7_days = datetime.utcnow() - timedelta(days=7)
    new_jobs_7d = (
        db.query(func.count(Job.id))
        .filter(Job.tenant_id == tenant_id, Job.created_at >= last_7_days)
        .scalar()
        or 0
    )

    latest_radar = (
        db.query(JobRadarRun)
        .filter(JobRadarRun.tenant_id == tenant_id, JobRadarRun.user_id == user.id)
        .order_by(JobRadarRun.created_at.desc())
        .first()
    )

    status_rows = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .group_by(Application.status)
        .all()
    )
    status_counts = {status: count for status, count in status_rows}
    response_count = sum(status_counts.get(s, 0) for s in ["interview", "technical_test", "offer"])
    response_rate = round((response_count / max(applications_total, 1)) * 100, 2)

    source_rows = (
        db.query(Job.source, func.count(Job.id))
        .filter(Job.tenant_id == tenant_id)
        .group_by(Job.source)
        .order_by(func.count(Job.id).desc())
        .limit(8)
        .all()
    )

    score_buckets = [
        {"label": "90+", "count": db.query(func.count(MatchScore.id)).filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.score >= 90).scalar() or 0},
        {"label": "78-89", "count": db.query(func.count(MatchScore.id)).filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.score >= 78, MatchScore.score < 90).scalar() or 0},
        {"label": "58-77", "count": db.query(func.count(MatchScore.id)).filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.score >= 58, MatchScore.score < 78).scalar() or 0},
        {"label": "0-57", "count": db.query(func.count(MatchScore.id)).filter(MatchScore.tenant_id == tenant_id, MatchScore.user_id == user.id, MatchScore.score < 58).scalar() or 0},
    ]

    result = {
        "total_jobs": int(total_jobs),
        "applications_total": int(applications_total),
        "active_applications": int(active_applications),
        "ranked_jobs": int(ranked_jobs),
        "average_match_score": round(float(avg_match or 0), 2),
        "high_match_jobs": int(high_match_jobs),
        "new_jobs_7d": int(new_jobs_7d),
        "response_rate": response_rate,
        "source_diversity": len(source_rows),
        "top_sources": [{"source": source or "manual", "count": int(count)} for source, count in source_rows],
        "status_counts": [{"status": _status_label(status), "count": int(count)} for status, count in status_rows],
        "score_buckets": [{"label": item["label"], "count": int(item["count"])} for item in score_buckets],
        "latest_radar": {
            "provider": latest_radar.provider,
            "total_ingested": latest_radar.total_ingested,
            "notified_count": latest_radar.notified_count,
            "created_at": latest_radar.created_at.isoformat(),
        } if latest_radar else None,
        "cached": False,
    }
    result["career_score"] = career_score_from_summary(result)

    upsert_daily_snapshot(db, tenant_id, user.id, result)
    db.commit()
    result["score_trend"] = get_score_trend(db, tenant_id, user.id, limit=14)
    result["decision_history"] = latest_decisions(db, tenant_id, user.id, limit=8)

    return set_cache(cache_key, result)
