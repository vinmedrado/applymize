from datetime import datetime
from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    job_id: int
    content_md: str
    version: int
    created_at: datetime

    class Config:
        from_attributes = True
