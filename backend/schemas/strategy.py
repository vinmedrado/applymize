from pydantic import BaseModel


class StrategyFactorsOut(BaseModel):
    match_score: float
    recency_score: float
    competition_score: float
    location_score: float
    remote_score: float
    seniority_score: float
    role_relevance_score: float


class StrategyRecommendationOut(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    remote: bool
    strategy_score: float
    priority: str
    explanation: str
    factors: StrategyFactorsOut
