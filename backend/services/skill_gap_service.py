from __future__ import annotations
from collections import Counter
from sqlalchemy.orm import Session
from backend.models.job import Job
from backend.models.user import User
from backend.services.matching_engine import calculate_match
from backend.services.profile_service import profile_context_text
from backend.services.job_role_relevance import relevant_jobs_for_user


def skill_gap_roadmap(db: Session, tenant_id: int, user: User, limit: int = 50) -> dict:
    candidates = db.query(Job).filter(Job.tenant_id == tenant_id).order_by(Job.created_at.desc()).limit(max(limit * 20, 500)).all()
    jobs = relevant_jobs_for_user(db, user, candidates)[:limit]
    context = profile_context_text(db, tenant_id, user)
    missing = Counter()
    strong = Counter()

    for job in jobs:
        result = calculate_match(user, job, profile_context=context)
        for skill in result.missing_skills:
            missing[skill] += 1
        for skill in result.matched_skills:
            strong[skill] += 1

    roadmap = []
    for skill, count in missing.most_common(20):
        priority = "alta" if count >= 5 else "média" if count >= 2 else "baixa"
        roadmap.append({
            "skill": skill,
            "priority": priority,
            "count": count,
            "action": f"Estudar {skill}, criar projeto prático e incluir evidência no currículo.",
        })

    return {
        "jobs_analyzed": len(jobs),
        "strong_skills": [{"skill": k, "count": v} for k, v in strong.most_common(15)],
        "missing_skills": [{"skill": k, "count": v} for k, v in missing.most_common(15)],
        "roadmap": roadmap,
        "warnings": [] if jobs else ["Sem vagas suficientes para calcular gaps. Importe vagas primeiro."],
    }
