from datetime import datetime
from pydantic import BaseModel


class QueueBuildRequest(BaseModel):
    limit: int = 10
    min_strategy_score: float = 58
    generate_cv: bool = True
    generate_message: bool = True


class ApplicationQueueItemOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    job_id: int
    strategy_score: float
    evaluation_grade: str
    generated_cv: str
    cover_message: str
    status: str
    failure_reason: str
    created_at: datetime
    updated_at: datetime
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    remote: bool | None = None
    job_url: str | None = None

    class Config:
        from_attributes = True


class QueueBuildResponse(BaseModel):
    created: int
    skipped: int
    blocked_low_priority: int
    daily_limit_remaining: int
    items: list[ApplicationQueueItemOut]
