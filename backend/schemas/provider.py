from pydantic import BaseModel


class ProviderOut(BaseModel):
    provider: str
    enabled: bool


class ProviderHealthOut(BaseModel):
    provider: str
    enabled: bool
    status: str
    message: str | None = None
    error: str | None = None
    sample_count: int | None = None
