from pydantic import BaseModel


class AtsSuggestionOut(BaseModel):
    priority: str
    title: str
    description: str


class AtsAnalysisOut(BaseModel):
    ats_score: float
    rh_score: float
    match_score: float
    keyword_score: float
    experience_score: float
    clarity_score: float
    seniority_score: float
    final_score: float
    grade: str
    probability: str
    strengths: list[str]
    weaknesses: list[str]
    missing_keywords: list[str]
    suggestions: list[AtsSuggestionOut]
    warnings: list[str]
    compared_job_id: int | None = None
