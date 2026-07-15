from pydantic import BaseModel


class NotificationSettingsOut(BaseModel):
    enabled: bool
    max_per_run: int
    min_priority: str
    telegram: dict
    whatsapp_evolution: dict
    auto_send: bool
    responsible_use: str


class NotificationResultOut(BaseModel):
    enabled: bool
    sent: int
    skipped: int = 0
    selected: int | None = None
    max_per_run: int | None = None
    results: list[dict]
