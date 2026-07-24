from datetime import datetime
from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    title_original: str | None = None
    company: str
    description: str
    description_original: str | None = None
    requirements: str = ""
    location: str = ""
    url: str = ""
    source: str = "manual"
    external_id: str = ""
    seniority: str = "unspecified"
    employment_type: str = "full_time"
    salary_min: float = 0
    salary_max: float = 0
    remote: bool = False


class JobUpdate(BaseModel):
    title: str | None = None
    title_original: str | None = None
    company: str | None = None
    description: str | None = None
    description_original: str | None = None
    requirements: str | None = None
    location: str | None = None
    url: str | None = None
    seniority: str | None = None
    employment_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    remote: bool | None = None


class JobOut(BaseModel):
    id: int
    tenant_id: int
    title: str
    title_original: str
    company: str
    description: str
    description_original: str
    requirements: str
    location: str
    url: str
    source: str
    external_id: str
    seniority: str
    employment_type: str
    salary_min: float
    salary_max: float
    remote: bool
    created_at: datetime
    role_relevance_score: float | None = None
    role_relevance_reason: str | None = None

    class Config:
        from_attributes = True


class JobPageOut(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    page_size: int
    hidden_irrelevant: int = 0


class IngestResult(BaseModel):
    inserted: int
    skipped: int
    collected_by_provider: dict[str, int] = {}
    errors: dict[str, str] = {}
    jobs: list[JobOut]
