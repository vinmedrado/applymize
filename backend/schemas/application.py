from datetime import datetime
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "saved"
    notes: str = ""
    next_action: str = ""


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    next_action: str | None = None


class ApplicationOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    job_id: int
    status: str
    notes: str
    next_action: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationEventOut(BaseModel):
    id: int
    application_id: int
    from_status: str
    to_status: str
    note: str
    created_at: datetime

    class Config:
        from_attributes = True
