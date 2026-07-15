from __future__ import annotations

import hashlib
import re
from typing import Any

from bs4 import BeautifulSoup

from backend.core.logging import get_logger
from backend.services.providers.base import JobProvider, ProviderJob

logger = get_logger(__name__)


def stable_id(source: str, raw: str) -> str:
    return hashlib.sha256(f"{source}:{raw}".encode("utf-8")).hexdigest()[:40]


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()




def normalize_remote_flag(value: Any) -> bool:
    """Normalize JobSpy remote flag to the strict boolean expected by ScraperInput."""
    normalized = bool(value) if value is not None else False
    logger.info(
        "jobspy_normalized_remote_flag provider=%s original=%r normalized=%s",
        "jobspy",
        value,
        normalized,
    )
    return normalized

def parse_workplace_types(value: str | list[str] | None) -> list[str]:
    if value is None or value == "":
        return []
    items = value if isinstance(value, list) else str(value).split(",")
    aliases = {
        "onsite": "on-site",
        "on_site": "on-site",
        "presencial": "on-site",
        "hibrido": "hybrid",
        "híbrido": "hybrid",
        "remoto": "remote",
    }
    result: list[str] = []
    for item in items:
        normalized = aliases.get(clean_text(item).lower(), clean_text(item).lower())
        if normalized and normalized not in result:
            result.append(normalized)
    return result


class JobSpyProvider(JobProvider):
    provider_name = "jobspy"
    enabled = True

    default_sites = ["indeed", "google"]

    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        try:
            from jobspy import scrape_jobs
        except Exception as exc:
            raise RuntimeError(
                "JobSpy não está instalado. Adicione python-jobspy ao requirements.txt e faça rebuild da imagem."
            ) from exc

        requested_limit = min(max(int(limit or 50), 1), 300)
        term = clean_text(kwargs.get("term") or kwargs.get("search_term") or "Analista de dados")
        state = clean_text(kwargs.get("state"))
        city = clean_text(kwargs.get("city"))
        country = clean_text(kwargs.get("country") or "Brazil")
        workplace_types = parse_workplace_types(kwargs.get("workplace_types") or kwargs.get("workplaceTypes"))
        sites = kwargs.get("sites") or kwargs.get("site_name") or self.default_sites
        if isinstance(sites, str):
            sites = [item.strip() for item in sites.split(",") if item.strip()]

        location = ", ".join(part for part in [city, state, country] if part)
        raw_is_remote = True if "remote" in workplace_types else kwargs.get("is_remote")
        is_remote = normalize_remote_flag(raw_is_remote)

        logger.info(
            "jobspy_fetch_start provider=%s sites=%s term=%s location=%s limit=%s workplace_types=%s",
            self.provider_name,
            sites,
            term,
            location,
            requested_limit,
            workplace_types,
        )

        df = scrape_jobs(
            site_name=sites,
            search_term=term,
            location=location or country,
            results_wanted=requested_limit,
            country_indeed=country,
            is_remote=normalize_remote_flag(is_remote),
            hours_old=168,
            verbose=0,
        )

        records = df.to_dict("records") if hasattr(df, "to_dict") else []
        jobs: list[ProviderJob] = []
        seen: set[str] = set()
        discarded = 0

        for raw in records:
            normalized = self.normalize_job(raw)
            if not normalized:
                discarded += 1
                continue
            if normalized.external_id in seen:
                continue
            seen.add(normalized.external_id)
            jobs.append(normalized)
            if len(jobs) >= requested_limit:
                break

        logger.info(
            "jobspy_fetch_done provider=%s raw=%s collected=%s discarded=%s",
            self.provider_name,
            len(records),
            len(jobs),
            discarded,
        )
        return jobs

    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        title = clean_text(raw.get("title") or raw.get("job_title") or raw.get("name"))
        company = clean_text(raw.get("company") or raw.get("company_name") or "")
        url = clean_text(raw.get("job_url") or raw.get("url") or raw.get("job_url_direct") or "")
        if not title or not url:
            return None

        site = clean_text(raw.get("site") or raw.get("source") or "jobspy")
        raw_id = clean_text(raw.get("id") or raw.get("job_id") or url)
        location = clean_text(raw.get("location") or ", ".join([clean_text(raw.get("city")), clean_text(raw.get("state")), clean_text(raw.get("country"))]).strip(", "))
        description_raw = raw.get("description") or raw.get("job_description") or title
        description = BeautifulSoup(str(description_raw), "html.parser").get_text(" ", strip=True)
        job_type = clean_text(raw.get("job_type") or raw.get("employment_type") or "full_time")
        interval = clean_text(raw.get("interval"))
        min_amount = raw.get("min_amount") or raw.get("salary_min") or 0
        max_amount = raw.get("max_amount") or raw.get("salary_max") or 0

        remote = bool(
            raw.get("is_remote")
            or "remote" in location.lower()
            or "remoto" in location.lower()
            or "remote" in job_type.lower()
            or "remoto" in job_type.lower()
        )

        source = f"jobspy:{site.lower()}" if site else self.provider_name

        return ProviderJob(
            source=source,
            external_id=stable_id(source, raw_id),
            title=title,
            company=company or site or "JobSpy",
            location=location,
            url=url,
            description=description or title,
            requirements="",
            seniority=self._infer_seniority(f"{title} {description}"),
            employment_type=job_type or interval or "full_time",
            salary_min=float(min_amount or 0),
            salary_max=float(max_amount or 0),
            remote=remote,
        )

    def healthcheck(self) -> dict[str, Any]:
        try:
            import jobspy  # noqa: F401
            return {
                "provider": self.provider_name,
                "enabled": self.enabled,
                "status": "ok",
                "message": "JobSpy instalado e registrado como provider agregado.",
            }
        except Exception as exc:
            return {
                "provider": self.provider_name,
                "enabled": False,
                "status": "missing_dependency",
                "message": "Instale python-jobspy e faça rebuild para habilitar este provider.",
                "error": str(exc),
            }

    @staticmethod
    def _infer_seniority(text: str) -> str:
        text = text.lower()
        if any(item in text for item in ["sênior", "senior", "sr", "especialista", "lead"]):
            return "senior"
        if any(item in text for item in ["júnior", "junior", "jr", "estágio", "estagio", "trainee"]):
            return "junior"
        if any(item in text for item in ["pleno", "mid"]):
            return "mid"
        return "unspecified"
