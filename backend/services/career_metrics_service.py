from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.models.career import CareerMetricSnapshot, DecisionHistory


def career_score_from_summary(summary: dict[str, Any]) -> float:
    avg = float(summary.get("average_match_score") or 0)
    response = float(summary.get("response_rate") or 0)
    analyzed = int(summary.get("ranked_jobs") or 0)
    high = int(summary.get("high_match_jobs") or 0)
    high_ratio = (high / max(analyzed, 1)) * 100 if analyzed else 0
    activity_bonus = min(int(summary.get("applications_total") or 0) * 2, 20)
    return round(min(avg * 0.45 + high_ratio * 0.25 + response * 0.2 + activity_bonus, 100), 2)


def upsert_daily_snapshot(db: Session, tenant_id: int, user_id: int, summary: dict[str, Any]) -> CareerMetricSnapshot:
    today = datetime.utcnow().date().isoformat()
    snapshot = db.query(CareerMetricSnapshot).filter(
        CareerMetricSnapshot.tenant_id == tenant_id,
        CareerMetricSnapshot.user_id == user_id,
        CareerMetricSnapshot.snapshot_date == today,
    ).first()
    if not snapshot:
        snapshot = CareerMetricSnapshot(tenant_id=tenant_id, user_id=user_id, snapshot_date=today)
        db.add(snapshot)

    snapshot.total_jobs = int(summary.get("total_jobs") or summary.get("jobs_total") or 0)
    snapshot.applications_total = int(summary.get("applications_total") or 0)
    snapshot.active_applications = int(summary.get("active_applications") or 0)
    snapshot.ranked_jobs = int(summary.get("ranked_jobs") or summary.get("jobs_analyzed") or 0)
    snapshot.average_match_score = float(summary.get("average_match_score") or 0)
    snapshot.high_match_jobs = int(summary.get("high_match_jobs") or 0)
    snapshot.response_rate = float(summary.get("response_rate") or 0)
    snapshot.career_score = career_score_from_summary(summary)
    snapshot.updated_at = datetime.utcnow()
    db.flush()
    return snapshot


def get_score_trend(db: Session, tenant_id: int, user_id: int, limit: int = 14) -> list[dict[str, Any]]:
    rows = (
        db.query(CareerMetricSnapshot)
        .filter(CareerMetricSnapshot.tenant_id == tenant_id, CareerMetricSnapshot.user_id == user_id)
        .order_by(CareerMetricSnapshot.snapshot_date.desc())
        .limit(max(1, min(limit, 60)))
        .all()
    )
    rows = list(reversed(rows))
    return [
        {
            "date": row.snapshot_date,
            "career_score": round(row.career_score, 2),
            "average_match_score": round(row.average_match_score, 2),
            "applications_total": row.applications_total,
            "high_match_jobs": row.high_match_jobs,
        }
        for row in rows
    ]


def record_decision(
    db: Session,
    tenant_id: int,
    user_id: int,
    decision_type: str,
    title: str,
    detail: str = "",
    job_id: int | None = None,
    application_id: int | None = None,
    score: float = 0,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> DecisionHistory:
    item = DecisionHistory(
        tenant_id=tenant_id,
        user_id=user_id,
        job_id=job_id,
        application_id=application_id,
        decision_type=decision_type,
        title=title[:255],
        detail=detail,
        score=float(score or 0),
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
    )
    db.add(item)
    if commit:
        db.commit()
        db.refresh(item)
    else:
        db.flush()
    return item


def latest_decisions(db: Session, tenant_id: int, user_id: int, limit: int = 8) -> list[dict[str, Any]]:
    rows = (
        db.query(DecisionHistory)
        .filter(DecisionHistory.tenant_id == tenant_id, DecisionHistory.user_id == user_id)
        .order_by(DecisionHistory.created_at.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    return [
        {
            "id": row.id,
            "type": row.decision_type,
            "title": row.title,
            "detail": row.detail,
            "score": row.score,
            "job_id": row.job_id,
            "application_id": row.application_id,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
