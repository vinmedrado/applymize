from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ProviderJob:
    source: str
    external_id: str
    title: str
    company: str
    location: str

    title_original: str = ""
    url: str = None
    description: str = None
    description_original: str = ""
    requirements: str = ""
    seniority: str = "unspecified"
    employment_type: str = "full_time"
    salary_min: float = 0.0
    salary_max: float = 0.0
    remote: bool = False
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JobProvider(ABC):
    provider_name: str
    enabled: bool = True

    @abstractmethod
    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        raise NotImplementedError

    @abstractmethod
    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        raise NotImplementedError

    def healthcheck(self) -> dict[str, Any]:
        if not self.enabled:
            return {
                "provider": self.provider_name,
                "enabled": False,
                "status": "disabled",
                "message": "Provider desabilitado.",
            }

        return {
            "provider": self.provider_name,
            "enabled": True,
            "status": "ok",
            "message": "Provider registrado e pronto para ingestão. Healthcheck externo pesado não é executado por padrão.",
        }
