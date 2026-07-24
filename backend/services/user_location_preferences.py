from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.profile import UserProfile
from backend.models.user import User

logger = get_logger(__name__)

INFOJOBS_CITY_CODES = {
    "sao paulo": "5211323",
    "são paulo": "5211323",
    "santo andre": "5211403",
    "santo andré": "5211403",
    "sao bernardo do campo": "5211387",
    "são bernardo do campo": "5211387",
    "sao caetano do sul": "5211391",
    "são caetano do sul": "5211391",
}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower().strip()


def _cities_from_profile(profile: UserProfile | None) -> list[str]:
    if not profile or not profile.job_cities:
        return []
    try:
        data = json.loads(profile.job_cities)
        if isinstance(data, list):
            return [_clean(item) for item in data if _clean(item)]
    except Exception:
        return [_clean(item) for item in profile.job_cities.split(",") if _clean(item)]
    return []


def _infojobs_city_code(city: str, fallback: str = "5211323") -> str:
    normalized = _ascii(city)
    return INFOJOBS_CITY_CODES.get(normalized) or INFOJOBS_CITY_CODES.get(city.lower().strip()) or fallback


@dataclass
class JobSearchLocationPreference:
    country: str = "Brasil"
    state: str = "São Paulo"
    state_code: str = "SP"
    cities: list[str] | None = None
    all_cities: bool = False
    remote_preference: str = "any"
    city_code: str = "5211323"

    @property
    def primary_city(self) -> str:
        if self.all_cities:
            return ""
        return (self.cities or [""])[0]

    @property
    def provider_country(self) -> str:
        return "Brazil" if _ascii(self.country) in {"brasil", "brazil"} else self.country

    @property
    def workplace_types(self) -> str:
        preference = (self.remote_preference or "any").lower().strip()
        if preference == "remote":
            return "remote"
        if preference == "hybrid":
            return "hybrid"
        if preference == "onsite":
            return "on-site"
        return ""

    def to_provider_options(self, base: dict[str, Any] | None = None, default_term: str | None = None) -> dict[str, Any]:
        options = dict(base or {})
        if default_term:
            options.setdefault("term", default_term)
        options.setdefault("country", self.provider_country)
        options.setdefault("state", self.state_code or self.state)
        options.setdefault("state_name", self.state)
        if self.primary_city:
            options.setdefault("city", self.primary_city)
            options.setdefault("location", f"{self.primary_city}, {self.state_code or self.state}, {self.provider_country}")
            options.setdefault("poblacion", self.city_code or _infojobs_city_code(self.primary_city))
            options.setdefault("city_code", self.city_code or _infojobs_city_code(self.primary_city))
        else:
            options.setdefault("location", f"{self.state or self.state_code}, {self.provider_country}")
            # InfoJobs does not have a stable public state-wide code in this MVP;
            # fallback to the configured default city code when all cities are selected.
            options.setdefault("poblacion", self.city_code or settings.automation_default_infojobs_city_code)
            options.setdefault("city_code", self.city_code or settings.automation_default_infojobs_city_code)
        if self.workplace_types:
            options.setdefault("workplace_types", self.workplace_types)
        logger.info(
            "job_search_location_preferences_applied country=%s state=%s cities=%s all_cities=%s remote=%s options=%s",
            self.country,
            self.state,
            self.cities or [],
            self.all_cities,
            self.remote_preference,
            options,
        )
        return options


def get_user_job_search_location_preference(db: Session, tenant_id: int, user: User) -> JobSearchLocationPreference:
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user.id).first()
    if not profile:
        return JobSearchLocationPreference(
            country=settings.automation_default_country,
            state=settings.automation_default_state,
            state_code=settings.automation_default_state,
            cities=[settings.automation_default_city],
            all_cities=False,
            city_code=settings.automation_default_infojobs_city_code,
        )
    cities = _cities_from_profile(profile)
    city_code = profile.job_city_code or (_infojobs_city_code(cities[0]) if cities else settings.automation_default_infojobs_city_code)
    return JobSearchLocationPreference(
        country=profile.job_country or "Brasil",
        state=profile.job_state or "São Paulo",
        state_code=profile.job_state_code or "SP",
        cities=cities,
        all_cities=bool(profile.job_all_cities),
        remote_preference=profile.job_remote_preference or "any",
        city_code=city_code,
    )
