import json
import math
import os
import re
import unicodedata
from dataclasses import dataclass
from collections import Counter
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.user import User
from backend.models.match_score import MatchScore
from backend.services.career_metrics_service import record_decision
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change


SENIORITY_ORDER = {
    "intern": 0, "estagio": 0, "estagiario": 0,
    "junior": 1, "jr": 1,
    "mid": 2, "pleno": 2,
    "senior": 3, "sr": 3,
    "lead": 4, "principal": 4,
    "manager": 5, "gerente": 5,
    "unspecified": 2,
}

DEFAULT_WEIGHTS = {
    "required_skills": float(os.getenv("MATCH_WEIGHT_REQUIRED_SKILLS", "0.35")),
    "desired_skills": float(os.getenv("MATCH_WEIGHT_DESIRED_SKILLS", "0.20")),
    "seniority": float(os.getenv("MATCH_WEIGHT_SENIORITY", "0.15")),
    "keyword": float(os.getenv("MATCH_WEIGHT_KEYWORD", "0.15")),
    "salary": float(os.getenv("MATCH_WEIGHT_SALARY", "0.05")),
    "remote_location": float(os.getenv("MATCH_WEIGHT_REMOTE_LOCATION", "0.10")),
}


@dataclass
class MatchResult:
    score: float
    skill_score: float
    seniority_score: float
    keyword_score: float
    salary_score: float
    remote_location_score: float
    required_skill_score: float
    desired_skill_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return [t for t in normalize_text(text).split() if len(t) > 1]


def split_skills(skills: str) -> list[str]:
    raw = re.split(r"[,;|\n]", skills or "")
    return [s.strip() for s in raw if s.strip()]


def extract_job_skills(job: Job) -> tuple[list[str], list[str]]:
    required = split_skills(job.requirements)
    corpus = f"{job.title}, {job.description}"

    desired_patterns = [
        "desejavel", "differential", "diferencial", "nice to have",
        "preferred", "plus", "bonus", "seria bom"
    ]
    desired = []
    for sentence in re.split(r"[.\n;]", corpus):
        normalized = normalize_text(sentence)
        if any(p in normalized for p in desired_patterns):
            desired.extend(split_skills(sentence.replace(":", ",")))

    if not required:
        required = list(dict.fromkeys(tokenize(job.title + " " + job.description)[:12]))

    desired = [s for s in dict.fromkeys(desired) if normalize_text(s) not in {normalize_text(x) for x in required}]
    return required, desired[:12]


def score_skill_group(user_skills: list[str], group: list[str]) -> tuple[float, list[str], list[str]]:
    if not group:
        return 50.0, [], []
    user_norm = {normalize_text(s): s for s in user_skills}
    user_tokens = set(tokenize(" ".join(user_skills)))
    matched, missing = [], []

    for skill in group:
        skill_norm = normalize_text(skill)
        skill_tokens = set(tokenize(skill))
        if skill_norm in user_norm or (skill_tokens and skill_tokens.issubset(user_tokens)):
            matched.append(skill)
        else:
            missing.append(skill)

    return round((len(matched) / len(group)) * 100, 2), matched, missing


def cosine_similarity(a_tokens: list[str], b_tokens: list[str]) -> float:
    if not a_tokens or not b_tokens:
        return 0.0
    ca, cb = Counter(a_tokens), Counter(b_tokens)
    common = set(ca) & set(cb)
    dot = sum(ca[t] * cb[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in ca.values()))
    norm_b = math.sqrt(sum(v * v for v in cb.values()))
    return 0.0 if not norm_a or not norm_b else dot / (norm_a * norm_b)


def seniority_score(user_seniority: str, job_seniority: str) -> float:
    u = SENIORITY_ORDER.get(normalize_text(user_seniority), 2)
    j = SENIORITY_ORDER.get(normalize_text(job_seniority), 2)
    if normalize_text(job_seniority) in {"", "unspecified"}:
        return 85.0
    distance = abs(u - j)
    if u > j:
        return max(70.0, 100.0 - distance * 12.5)
    return max(0.0, 100.0 - distance * 28.0)


def salary_score(job: Job) -> float:
    if not job.salary_min and not job.salary_max:
        return 75.0
    if job.salary_max and job.salary_max < 1000:
        return 40.0
    if job.salary_min >= 6000 or job.salary_max >= 9000:
        return 95.0
    if job.salary_min >= 3000 or job.salary_max >= 5000:
        return 80.0
    return 60.0


def remote_location_score(job: Job) -> float:
    if job.remote:
        return 100.0
    loc = normalize_text(job.location)
    if not loc:
        return 70.0
    if any(x in loc for x in ["sao paulo", "santo andre", "remoto", "hybrid", "hibrido"]):
        return 85.0
    return 55.0


class FutureMLScoringAdapter:
    def predict_score(self, features: dict) -> None:
        return None


def calculate_match(user: User, job: Job, weights: dict | None = None, profile_context: str | None = None) -> MatchResult:
    weights = weights or DEFAULT_WEIGHTS
    weight_sum = sum(weights.values()) or 1.0
    weights = {k: v / weight_sum for k, v in weights.items()}

    user_source = profile_context or user.skills
    user_skills = split_skills(user_source)
    required_skills, desired_skills = extract_job_skills(job)

    required_score, required_matched, required_missing = score_skill_group(user_skills, required_skills)
    desired_score, desired_matched, desired_missing = score_skill_group(user_skills, desired_skills)

    matched = list(dict.fromkeys(required_matched + desired_matched))
    missing = list(dict.fromkeys(required_missing + desired_missing))

    keyword = cosine_similarity(
        tokenize(f"{user_source} {user.target_role} {user.seniority}"),
        tokenize(f"{job.title} {job.description} {job.requirements} {job.seniority}"),
    ) * 100
    senior = seniority_score(user.seniority, job.seniority)
    salary = salary_score(job)
    remote_loc = remote_location_score(job)

    score = round(
        required_score * weights["required_skills"]
        + desired_score * weights["desired_skills"]
        + senior * weights["seniority"]
        + keyword * weights["keyword"]
        + salary * weights["salary"]
        + remote_loc * weights["remote_location"],
        2,
    )

    skill_score = round(required_score * 0.7 + desired_score * 0.3, 2)

    explanation = (
        f"Score final {score}. Required skills: {required_score:.1f}% "
        f"({len(required_matched)}/{len(required_skills)}). Desired skills: {desired_score:.1f}% "
        f"({len(desired_matched)}/{len(desired_skills)}). Senioridade: {senior:.1f}%. "
        f"Keyword/texto: {keyword:.1f}%. Salário: {salary:.1f}%. Remoto/localização: {remote_loc:.1f}%. "
        f"Pesos usados: {json.dumps(weights, ensure_ascii=False)}."
    )

    return MatchResult(
        score=score,
        skill_score=skill_score,
        seniority_score=round(senior, 2),
        keyword_score=round(keyword, 2),
        salary_score=round(salary, 2),
        remote_location_score=round(remote_loc, 2),
        required_skill_score=round(required_score, 2),
        desired_skill_score=round(desired_score, 2),
        matched_skills=matched,
        missing_skills=missing,
        explanation=explanation,
    )


def upsert_match_score(db: Session, tenant_id: int, user: User, job: Job) -> MatchScore:
    result = calculate_match(user, job)
    # React StrictMode and multiple browser tabs can request the same score at
    # the same time. Serialize this key in PostgreSQL so the unique constraint
    # remains an invariant instead of surfacing a transient HTTP 409.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(:user_id, :job_id)"),
            {"user_id": user.id, "job_id": job.id},
        )
    existing = db.query(MatchScore).filter(
        MatchScore.tenant_id == tenant_id,
        MatchScore.user_id == user.id,
        MatchScore.job_id == job.id,
    ).first()

    if not existing:
        existing = MatchScore(
            tenant_id=tenant_id,
            user_id=user.id,
            job_id=job.id,
            score=0,
            skill_score=0,
            seniority_score=0,
            keyword_score=0,
            explanation="",
        )
        db.add(existing)

    existing.score = result.score
    existing.skill_score = result.skill_score
    existing.seniority_score = result.seniority_score
    existing.keyword_score = result.keyword_score
    existing.matched_skills = json.dumps(result.matched_skills, ensure_ascii=False)
    existing.missing_skills = json.dumps(result.missing_skills, ensure_ascii=False)
    existing.explanation = result.explanation
    record_decision(
        db,
        tenant_id=tenant_id,
        user_id=user.id,
        decision_type="score_calculated",
        title=f"Score calculado: {job.title}",
        detail=result.explanation[:1000],
        job_id=job.id,
        score=result.score,
        metadata={"company": job.company, "source": job.source},
        commit=False,
    )
    db.commit()
    db.refresh(existing)
    invalidate_cache(f"dashboard:summary:{tenant_id}:{user.id}")
    notify_dashboard_change(tenant_id, user.id)
    return existing


def serialize_match(score: MatchScore) -> dict:
    return {
        "id": score.id,
        "tenant_id": score.tenant_id,
        "user_id": score.user_id,
        "job_id": score.job_id,
        "score": score.score,
        "skill_score": score.skill_score,
        "seniority_score": score.seniority_score,
        "keyword_score": score.keyword_score,
        "matched_skills": json.loads(score.matched_skills or "[]"),
        "missing_skills": json.loads(score.missing_skills or "[]"),
        "explanation": score.explanation,
        "created_at": score.created_at,
    }
