from datetime import datetime
from pydantic import BaseModel


class MatchScoreOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    job_id: int
    score: float
    skill_score: float
    seniority_score: float
    keyword_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    created_at: datetime


class RankOut(BaseModel):
    job_id: int
    title: str
    company: str
    score: float
    explanation: str
