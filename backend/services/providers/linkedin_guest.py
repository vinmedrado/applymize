from __future__ import annotations

import hashlib
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from backend.core.logging import get_logger
from backend.services.providers.base import JobProvider, ProviderJob

logger = get_logger(__name__)

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

_FOREIGN_LOCATION_PATTERNS = (
    "united states",
    "usa",
    " u.s.",
    " u.s ",
    " us ",
    "remote us",
    "remote - us",
    "north america",
    "canada",
)

_BRAZIL_LOCATION_PATTERNS = (
    "brazil",
    "brasil",
    "sao paulo",
    "são paulo",
    "remote brazil",
    "remoto brasil",
    "remoto",
)


def _normalize_location(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _is_foreign_location(location: str) -> bool:
    normalized = f" {_normalize_location(location)} "
    if not normalized.strip() or "nao informado" in normalized or "não informado" in normalized:
        return False
    has_brazil_signal = any(pattern in normalized for pattern in _BRAZIL_LOCATION_PATTERNS)
    has_foreign_signal = any(pattern in normalized for pattern in _FOREIGN_LOCATION_PATTERNS)
    return has_foreign_signal and not has_brazil_signal


def stable_id(source: str, raw: str) -> str:
    return hashlib.sha256(f"{source}:{raw}".encode("utf-8")).hexdigest()[:40]


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


class LinkedInGuestProvider(JobProvider):
    provider_name = "linkedin"
    enabled = True

    def fetch_jobs(self, limit: int = 50, **kwargs: Any) -> list[ProviderJob]:
        requested_limit = min(max(int(limit or 50), 1), 100)
        term = clean_text(kwargs.get("term") or kwargs.get("keywords") or "Analista de dados")
        state = clean_text(kwargs.get("state") or "SP")
        city = clean_text(kwargs.get("city") or "São Paulo")
        country = clean_text(kwargs.get("country") or "Brasil")
        # O controle principal agora é filtro de busca por São Paulo/Brasil, não
        # bloqueio duro pós-coleta. Isso evita descartar vagas válidas por texto ambíguo.
        location = clean_text(", ".join([x for x in [city, state, country] if x])) or "São Paulo, SP, Brasil"

        jobs: list[ProviderJob] = []
        start = 0
        page_size = 25

        while len(jobs) < requested_limit:
            params = {
                "keywords": term,
                "location": location,
                "start": start,
            }

            try:
                response = requests.get(
                    BASE_URL,
                    params=params,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "text/html,*/*",
                    },
                    timeout=20,
                )
            except Exception as exc:
                logger.warning("linkedin_fetch_failed error=%s", exc)
                break

            logger.info(
                "linkedin_guest_response status=%s url=%s",
                response.status_code,
                response.url,
            )

            if response.status_code != 200:
                break

            cards = BeautifulSoup(response.text, "html.parser").select("li")
            if not cards:
                break

            before = len(jobs)

            for card in cards:
                normalized = self.normalize_job(card)
                if normalized:
                    jobs.append(normalized)

                if len(jobs) >= requested_limit:
                    break

            if len(jobs) == before:
                break

            start += page_size

        return jobs

    def normalize_job(self, raw: Any) -> ProviderJob | None:
        card = raw

        title_el = card.select_one(".base-search-card__title")
        company_el = card.select_one(".base-search-card__subtitle")
        location_el = card.select_one(".job-search-card__location")
        link_el = card.select_one("a.base-card__full-link")

        title = clean_text(title_el.get_text(" ", strip=True) if title_el else "")
        if not title:
            return None

        company = clean_text(company_el.get_text(" ", strip=True) if company_el else "LinkedIn")
        location = clean_text(location_el.get_text(" ", strip=True) if location_el else "Não informado")
        url = clean_text(link_el.get("href") if link_el else "")


        remote = "remoto" in location.lower() or "remote" in location.lower()

        return ProviderJob(
            source=self.provider_name,
            external_id=stable_id(self.provider_name, url or f"{title}|{company}|{location}"),
            title=title,
            company=company,
            location=location,
            url=url,
            description=title,
            requirements="",
            seniority="unspecified",
            employment_type="full_time",
            salary_min=0,
            salary_max=0,
            remote=remote,
        )

    def healthcheck(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": self.enabled,
            "status": "ok",
            "message": "LinkedIn guest provider focused on São Paulo/Brasil.",
        }