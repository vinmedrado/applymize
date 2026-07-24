from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from math import exp
from typing import Any

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.job import Job
from backend.models.user import User
from backend.models.automation import AutomationSettings
from backend.services.job_role_relevance import evaluate_role_relevance, role_search_terms
from backend.services.matching_engine import calculate_match
from backend.services.profile_service import profile_context_text

logger = get_logger(__name__)


@dataclass
class StrategyFactors:
    match_score: float
    recency_score: float
    competition_score: float
    location_score: float
    remote_score: float
    seniority_score: float
    role_relevance_score: float = 100.0


@dataclass
class StrategyRecommendation:
    job_id: int
    title: str
    company: str
    location: str
    remote: bool
    strategy_score: float
    priority: str
    explanation: str
    factors: StrategyFactors


def strategy_weights() -> dict[str, float]:
    existing = {
        "match_score": settings.strategy_weight_match,
        "recency_score": settings.strategy_weight_recency,
        "competition_score": settings.strategy_weight_competition,
        "location_score": settings.strategy_weight_location,
        "remote_score": settings.strategy_weight_remote,
        "seniority_score": settings.strategy_weight_seniority,
    }
    existing_total = sum(existing.values()) or 1.0
    return {
        **{key: (value / existing_total) * 0.65 for key, value in existing.items()},
        "role_relevance_score": 0.35,
    }

GENERIC_TITLES = {
    "analista", "assistente", "auxiliar", "developer", "desenvolvedor",
    "engenheiro", "consultor", "manager", "specialist", "estagiario",
}

SPECIFIC_KEYWORDS = {
    "fastapi", "postgresql", "etl", "power bi", "machine learning", "ml",
    "python", "sql", "docker", "kubernetes", "data engineering", "analytics",
    "api", "automacao", "automação", "backend", "spark", "airflow",
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def weighted_score(factors: StrategyFactors, weights: dict[str, float] | None = None) -> float:
    weights = weights or strategy_weights()
    total_weight = sum(weights.values()) or 1.0
    normalized = {key: value / total_weight for key, value in weights.items()}
    data = asdict(factors)
    return round(sum(data[key] * normalized[key] for key in normalized), 2)


def recency_score(job: Job, now: datetime | None = None) -> float:
    now = now or datetime.utcnow()
    if not job.created_at:
        return 65.0
    age_days = max((now - job.created_at).days, 0)
    return round(clamp(100.0 * exp(-age_days / 21.0), 35.0, 100.0), 2)


def competition_score(job: Job) -> float:
    text = f"{job.title} {job.description} {job.requirements}".lower()
    title_words = {word.strip(".,:;()[]{}").lower() for word in job.title.split()}
    generic_hits = len(title_words & GENERIC_TITLES)
    specific_hits = sum(1 for keyword in SPECIFIC_KEYWORDS if keyword in text)

    base = 65.0
    base -= generic_hits * 8.0
    base += min(specific_hits * 5.0, 30.0)

    if job.remote:
        base -= 8.0

    if job.requirements and len(job.requirements.split(",")) >= 4:
        base += 8.0

    return round(clamp(base, 25.0, 95.0), 2)


def location_score(user: User, job: Job) -> float:
    user_text = f"{user.target_role} {user.skills}".lower()
    job_location = (job.location or "").lower()

    if job.remote:
        return 95.0

    preferred_locations = ["são paulo", "sao paulo", "santo andre", "santo andré", "remote", "remoto", "hibrido", "híbrido"]
    if any(location in job_location for location in preferred_locations):
        return 82.0

    if any(location in user_text for location in preferred_locations) and any(location in job_location for location in preferred_locations):
        return 88.0

    if not job_location:
        return 60.0

    return 50.0


def remote_score(job: Job) -> float:
    if job.remote:
        return 100.0
    location = (job.location or "").lower()
    if "hibrido" in location or "híbrido" in location or "hybrid" in location:
        return 80.0
    return 55.0


def classify_priority(score: float) -> str:
    if score >= 78:
        return "HIGH_PRIORITY"
    if score >= 58:
        return "MEDIUM_PRIORITY"
    return "LOW_PRIORITY"


def recommendation_text(priority: str, factors: StrategyFactors) -> str:
    if priority == "HIGH_PRIORITY":
        return "Alta chance de retorno. Recomendado aplicar imediatamente."
    if priority == "MEDIUM_PRIORITY":
        if factors.competition_score < 55:
            return "Boa oportunidade, mas concorrência moderada. Aplicar após ajustar CV."
        return "Boa oportunidade. Vale aplicar após revisar requisitos principais."
    return "Baixa prioridade. Aplicar apenas se houver tempo ou interesse estratégico."


def calculate_strategy_for_job(
    user: User,
    job: Job,
    profile_context: str | None = None,
    search_terms: list[str] | None = None,
    min_role_relevance: float = 55.0,
) -> StrategyRecommendation:
    match = calculate_match(user, job, profile_context=profile_context)
    relevance = evaluate_role_relevance(
        user.target_role,
        job,
        search_terms=search_terms,
        threshold=min_role_relevance,
    )

    factors = StrategyFactors(
        match_score=match.score,
        recency_score=recency_score(job),
        competition_score=competition_score(job),
        location_score=location_score(user, job),
        remote_score=remote_score(job),
        seniority_score=match.seniority_score,
        role_relevance_score=relevance.score,
    )
    score = weighted_score(factors)

    # =========================
    #  PENALIDADE INTELIGENTE
    # =========================

    text = f"{job.title} {job.description} {job.requirements}".lower()

    penalty = 0

    # Ensino superior obrigatório
    if "ensino superior completo" in text or "graduação completa" in text:
        penalty += 25

    # Inglês avançado obrigatório
    if "inglês avançado" in text or "advanced english" in text:
        penalty += 20

    # Certificações obrigatórias
    if "certificação" in text or "certificado obrigatório" in text:
        penalty += 10

    # aplica penalidade
    score = max(score - penalty, 0)
    if not relevance.relevant:
        score = min(score, 35.0)
    priority = classify_priority(score)
    explanation = recommendation_text(priority, factors)

    logger.info(
        "strategy_score_calculated user_id=%s job_id=%s score=%s priority=%s factors=%s",
        user.id,
        job.id,
        score,
        priority,
        asdict(factors),
    )

    return StrategyRecommendation(
        job_id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        remote=job.remote,
        strategy_score=score,
        priority=priority,
        explanation=explanation,
        factors=factors,
    )


def get_strategy_recommendations(db: Session, user_id: int, tenant_id: int, limit: int = 25) -> list[StrategyRecommendation]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    automation = (
        db.query(AutomationSettings)
        .filter(AutomationSettings.user_id == user_id)
        .order_by(AutomationSettings.id.desc())
        .first()
    )
    search_terms = role_search_terms(user.target_role, automation.search_terms if automation else None)
    min_role_relevance = float(automation.min_role_relevance if automation else 55.0)

    jobs = (
        db.query(Job)
        .filter(Job.tenant_id == tenant_id)
        .order_by(Job.created_at.desc())
        .limit(max(limit * 20, 500))
        .all()
    )

    context = profile_context_text(db, tenant_id, user)
    relevant_jobs = [
        job for job in jobs
        if job.source == "manual" or evaluate_role_relevance(
            user.target_role,
            job,
            search_terms=search_terms,
            threshold=min_role_relevance,
        ).relevant
    ]
    recommendations = [
        calculate_strategy_for_job(
            user,
            job,
            profile_context=context,
            search_terms=search_terms,
            min_role_relevance=min_role_relevance,
        )
        for job in relevant_jobs
    ]
    recommendations.sort(key=lambda item: item.strategy_score, reverse=True)
    recommendations = recommendations[:max(limit, 1)]

    logger.info(
        "strategy_recommendations_generated user_id=%s tenant_id=%s analyzed=%s top_jobs=%s",
        user_id,
        tenant_id,
        len(recommendations),
        [item.job_id for item in recommendations[:5]],
    )

    return recommendations


class FutureMLStrategyScorer:
    def predict(self, features: dict[str, Any]) -> None:
        return None
