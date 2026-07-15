from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from backend.core.logging import get_logger
from backend.services.providers.base import JobProvider, ProviderJob

logger = get_logger(__name__)


GUPY_API_BASE_URL = "https://employability-portal.gupy.io/api/v1/jobs"
GUPY_PORTAL_BASE_URL = "https://portal.gupy.io"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://portal.gupy.io",
    "Referer": "https://portal.gupy.io/",
}


def stable_id(source: str, raw: str) -> str:
    return hashlib.sha256(f"{source}:{raw}".encode("utf-8")).hexdigest()[:40]


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_workplace_types(value: str | list[str] | None) -> list[str]:
    if value is None or value == "":
        return []

    items = value if isinstance(value, list) else str(value).split(",")
    normalized: list[str] = []

    aliases = {
        "onsite": "on-site",
        "on_site": "on-site",
        "presencial": "on-site",
        "hibrido": "hybrid",
        "híbrido": "hybrid",
        "remoto": "remote",
    }

    for item in items:
        clean = clean_text(item).lower()
        clean = aliases.get(clean, clean)
        if clean and clean not in normalized:
            normalized.append(clean)

    return normalized


def parse_published_date(value: Any) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


class GupyProvider(JobProvider):
    provider_name = "gupy"
    enabled = True

    search_page_url = "https://portal.gupy.io/job-search"
    api_url = GUPY_API_BASE_URL

    def build_search_params(
        self,
        term: str | None = None,
        state: str | None = None,
        city: str | None = None,
        workplace_types: str | list[str] | None = None,
        limit: int = 25,
        offset: int = 0,
        country: str | None = None,
        job_types: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Parâmetros do endpoint público correto da Gupy:
        https://employability-portal.gupy.io/api/v1/jobs

        Importante:
        - busca por cargo usa jobName, não term;
        - filtro de modalidade usa workplaceTypes, não workplaceTypes[];
        - paginação usa limit/offset.
        """
        params: dict[str, Any] = {
            "limit": min(max(int(limit or 25), 1), 100),
            "offset": max(int(offset or 0), 0),
        }

        if term:
            params["jobName"] = clean_text(term)

        if state:
            params["state"] = clean_text(state)

        if city:
            # O endpoint geralmente filtra melhor por estado/país, mas manter cidade
            # não quebra se a API aceitar esse parâmetro.
            params["city"] = clean_text(city)

        if country:
            params["country"] = clean_text(country)

        types = parse_workplace_types(workplace_types)
        if types:
            params["workplaceTypes"] = ",".join(types)

        if job_types:
            job_type_items = job_types if isinstance(job_types, list) else str(job_types).split(",")
            normalized_job_types = [clean_text(item).lower() for item in job_type_items if clean_text(item)]
            if normalized_job_types:
                params["jobTypes"] = ",".join(normalized_job_types)

        return params

    def build_search_url(
        self,
        term: str | None = None,
        state: str | None = None,
        city: str | None = None,
        workplace_types: str | list[str] | None = None,
        limit: int = 25,
    ) -> str:
        page_params: dict[str, Any] = {}
        if term:
            page_params["term"] = clean_text(term)
        if state:
            page_params["state"] = clean_text(state)
        if city:
            page_params["city"] = clean_text(city)
        types = parse_workplace_types(workplace_types)
        if types:
            page_params["workplaceTypes[]"] = ",".join(types)

        query = urlencode(page_params, doseq=True)
        return f"{self.search_page_url}?{query}" if query else self.search_page_url

    def _extract_jobs_from_payload(self, payload: Any) -> tuple[list[dict[str, Any]], int]:
        if isinstance(payload, list):
            jobs = [item for item in payload if isinstance(item, dict)]
            return jobs, len(jobs)

        if not isinstance(payload, dict):
            return [], 0

        data = payload.get("data")
        if isinstance(data, list):
            pagination = payload.get("pagination") or {}
            total = pagination.get("total") or payload.get("total") or len(data)
            return [item for item in data if isinstance(item, dict)], int(total or 0)

        for key in ["jobs", "results", "items", "content"]:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)], len(value)
            if isinstance(value, dict):
                nested, total = self._extract_jobs_from_payload(value)
                if nested:
                    return nested, total

        return [], 0

    def _fetch_page(self, params: dict[str, Any]) -> tuple[list[dict[str, Any]], int, str]:
        response = requests.get(
            self.api_url,
            params=params,
            headers=HEADERS,
            timeout=30,
        )

        body_sample = response.text[:600].replace("\n", " ").replace("\r", " ")
        logger.info(
            "gupy_api_response provider=%s status=%s final_url=%s body_sample=%s",
            self.provider_name,
            response.status_code,
            response.url,
            body_sample,
        )

        response.raise_for_status()
        jobs, total = self._extract_jobs_from_payload(response.json())
        return jobs, total, response.url

    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        requested_limit = min(max(int(limit or 300), 1), 300)
        term = kwargs.get("term") or kwargs.get("jobName")
        state = kwargs.get("state")
        city = kwargs.get("city")
        workplace_types = kwargs.get("workplace_types") or kwargs.get("workplaceTypes")
        country = kwargs.get("country")
        job_types = kwargs.get("job_types") or kwargs.get("jobTypes")

        search_url = self.build_search_url(
            term=term,
            state=state,
            city=city,
            workplace_types=workplace_types,
            limit=requested_limit,
        )

        logger.info(
            "gupy_fetch_start provider=%s mode=employability_api term=%s state=%s city=%s workplace_types=%s search_url=%s",
            self.provider_name,
            term,
            state,
            city,
            workplace_types,
            search_url,
        )

        errors: list[str] = []
        raw_jobs: list[dict[str, Any]] = []
        total_available = 0

        offset = 0
        page_size = min(100, requested_limit)

        try:
            while len(raw_jobs) < requested_limit:
                params = self.build_search_params(
                    term=term,
                    state=state,
                    city=city,
                    workplace_types=workplace_types,
                    limit=page_size,
                    offset=offset,
                    country=country,
                    job_types=job_types,
                )

                page_jobs, total_available, final_url = self._fetch_page(params)
                logger.info(
                    "gupy_api_page provider=%s offset=%s page_size=%s received=%s total_available=%s final_url=%s",
                    self.provider_name,
                    offset,
                    page_size,
                    len(page_jobs),
                    total_available,
                    final_url,
                )

                if not page_jobs:
                    break

                raw_jobs.extend(page_jobs)

                offset += page_size
                if total_available and offset >= total_available:
                    break
                if len(page_jobs) < page_size:
                    break

        except Exception as exc:
            errors.append(str(exc))
            logger.warning(
                "gupy_api_failed provider=%s error=%s",
                self.provider_name,
                exc,
            )

        jobs: list[ProviderJob] = []
        seen: set[str] = set()
        discarded = 0

        for raw in raw_jobs:
            normalized = self.normalize_job(raw)
            if not normalized:
                discarded += 1
                continue

            dedup_key = normalized.external_id or f"{normalized.title}|{normalized.company}|{normalized.url}"
            if dedup_key in seen:
                continue

            seen.add(dedup_key)
            jobs.append(normalized)

            if len(jobs) >= requested_limit:
                break

        logger.info(
            "gupy_fetch_done provider=%s mode=employability_api total_available=%s total_raw=%s total_collected=%s total_discarded=%s errors=%s",
            self.provider_name,
            total_available,
            len(raw_jobs),
            len(jobs),
            discarded,
            errors,
        )

        return jobs

    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        title = clean_text(raw.get("name") or raw.get("title") or raw.get("jobName"))
        if not title:
            logger.warning("gupy_job_descartado reason=sem_titulo raw_keys=%s", list(raw.keys()))
            return None

        raw_id = clean_text(raw.get("id") or raw.get("jobId") or raw.get("code"))

        public_url = clean_text(
            raw.get("jobUrl")
            or raw.get("url")
            or raw.get("publicUrl")
            or raw.get("applicationUrl")
        )

        if not public_url:
            if raw_id:
                public_url = f"{GUPY_PORTAL_BASE_URL}/job/{raw_id}"
            else:
                public_url = self.build_search_url(term=title)

        if public_url.startswith("/"):
            public_url = f"{GUPY_PORTAL_BASE_URL}{public_url}"

        company = clean_text(raw.get("careerPageName") or raw.get("companyName") or raw.get("company"))
        company_obj = raw.get("careerPage") or raw.get("organization") or {}
        if not company and isinstance(company_obj, dict):
            company = clean_text(company_obj.get("name") or company_obj.get("companyName") or company_obj.get("title"))
        if not company:
            company = "Gupy"

        location_parts: list[str] = []
        for key in ["city", "state", "country"]:
            value = clean_text(raw.get(key))
            if value:
                location_parts.append(value)

        location_raw = raw.get("location") or raw.get("workplace") or raw.get("address")
        if isinstance(location_raw, dict):
            for value in location_raw.values():
                clean = clean_text(value)
                if clean:
                    location_parts.append(clean)
        elif location_raw:
            location_parts.append(clean_text(location_raw))

        location = clean_text(", ".join(dict.fromkeys([part for part in location_parts if part])))

        workplace_types_raw = raw.get("workplaceTypes") or raw.get("workplaceType") or raw.get("workplace_type") or raw.get("type") or []
        if isinstance(workplace_types_raw, list):
            workplace_type = ",".join(clean_text(item) for item in workplace_types_raw if clean_text(item))
        else:
            workplace_type = clean_text(workplace_types_raw)

        remote = bool(
            raw.get("isRemoteWork")
            or "remote" in workplace_type.lower()
            or "remoto" in workplace_type.lower()
            or "remote" in location.lower()
            or "remoto" in location.lower()
        )

        description_raw = (
            raw.get("description")
            or raw.get("jobDescription")
            or raw.get("responsibilities")
            or raw.get("descriptionHtml")
            or title
        )
        description = BeautifulSoup(str(description_raw), "html.parser").get_text(" ", strip=True)

        requirements_raw = raw.get("requirements") or raw.get("prerequisites") or raw.get("qualifications") or ""
        requirements = BeautifulSoup(str(requirements_raw), "html.parser").get_text(" ", strip=True)

        published = raw.get("publishedDate")
        published_dt = parse_published_date(published)
        if published and not published_dt:
            logger.warning("gupy_published_parse_failed url=%s published=%s", public_url, published)

        # Mantém filtro anti-lixo antigo, mas sem descartar por URL diferente.
        max_age_days = 365
        if published_dt:
            now = datetime.now(timezone.utc)
            if published_dt.tzinfo is None:
                published_dt = published_dt.replace(tzinfo=timezone.utc)
            if (now - published_dt).days > max_age_days:
                logger.info(
                    "gupy_job_antiga_descartado url=%s title=%s published=%s",
                    public_url,
                    title,
                    published,
                )
                return None

        stable_raw_id = raw_id or public_url or title

        return ProviderJob(
            source=self.provider_name,
            external_id=stable_id(self.provider_name, stable_raw_id),
            title=title,
            company=company or "Gupy",
            location=location,
            url=public_url,
            description=description or title,
            requirements=requirements,
            seniority=self._infer_seniority(f"{title} {description}"),
            employment_type=workplace_type or "full_time",
            salary_min=0,
            salary_max=0,
            remote=remote,
        )

    def healthcheck(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": self.enabled,
            "status": "ok" if self.enabled else "disabled",
            "message": "Gupy provider usando employability-portal.gupy.io/api/v1/jobs.",
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
