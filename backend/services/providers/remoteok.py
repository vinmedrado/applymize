from __future__ import annotations

import hashlib
from typing import Any

import requests
from bs4 import BeautifulSoup

from backend.services.providers.base import JobProvider, ProviderJob


def stable_id(source: str, raw: str) -> str:
    return hashlib.sha256(f"{source}:{raw}".encode("utf-8")).hexdigest()[:40]


def infer_seniority(text: str) -> str:
    value = (text or "").lower()
    if any(item in value for item in ["senior", "sr.", "lead", "principal"]):
        return "senior"
    if any(item in value for item in ["junior", "jr.", "entry"]):
        return "junior"
    if any(item in value for item in ["mid", "pleno"]):
        return "mid"
    return "unspecified"


class RemoteOKProvider(JobProvider):
    provider_name = "remoteok"
    enabled = True
    api_url = "https://remoteok.com/api"

    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        response = requests.get(
            self.api_url,
            headers={"User-Agent": "ApplymizeCareerBot/1.0"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()

        jobs: list[ProviderJob] = []
        for item in payload:
            if not isinstance(item, dict) or not item.get("position"):
                continue
            normalized = self.normalize_job(item)
            if normalized:
                jobs.append(normalized)
            if len(jobs) >= limit:
                break
        return jobs

    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        title = (raw.get("position") or "").strip()
        if not title:
            return None

        description_html = raw.get("description") or ""
        description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True) if description_html else title
        raw_id = str(raw.get("id") or raw.get("url") or f"{raw.get('company')}-{title}")
        tags = raw.get("tags") or []

        return ProviderJob(
            source=self.provider_name,
            external_id=stable_id(self.provider_name, raw_id),
            title=title,
            company=raw.get("company") or "Unknown",
            location=raw.get("location") or "Remote",
            url=raw.get("url") or f"https://remoteok.com/remote-jobs/{raw_id}",
            description=description,
            requirements=", ".join(tags),
            seniority=infer_seniority(f"{title} {description}"),
            employment_type="full_time",
            salary_min=float(raw.get("salary_min") or 0),
            salary_max=float(raw.get("salary_max") or 0),
            remote=True,
        )
