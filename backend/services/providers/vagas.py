from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from backend.core.logging import get_logger
from backend.services.providers.base import JobProvider, ProviderJob

logger = get_logger(__name__)


def stable_id(source: str, raw: str) -> str:
    return hashlib.sha256(f"{source}:{raw}".encode("utf-8")).hexdigest()[:40]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


class VagasProvider(JobProvider):
    provider_name = "vagas"
    enabled = True
    base_url = "https://www.vagas.com.br"

    def build_search_url(self, term: str = "Analista de dados") -> str:
        safe_term = clean_text(term) or "Analista de dados"
        slug = quote_plus(safe_term.lower()).replace("+", "-")
        return f"{self.base_url}/vagas-de-{slug}"

    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        term = kwargs.get("term") or "Analista de dados"
        search_url = self.build_search_url(term)

        logger.info("vagas_fetch_jobs provider=%s url=%s term=%s", self.provider_name, search_url, term)

        response = requests.get(
            search_url,
            headers={"User-Agent": "ApplymizeCareerBot/1.0", "Accept": "text/html"},
            timeout=20,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("li[id^='vaga'], article, .vaga, .job, .resultado, .grupoDeVagas")
        if not cards:
            cards = soup.select("li, article")

        jobs: list[ProviderJob] = []
        seen: set[str] = set()

        for card in cards:
            link = card.select_one("a[href*='/vagas/'], a[href*='vagas.com.br']")
            title_node = card.select_one("h2, h3, .cargo, .titulo, a")
            if not link or not title_node:
                continue

            href = link.get("href") or ""
            url = urljoin(self.base_url, href)
            title = clean_text(title_node.get_text(" ", strip=True))
            if not title or len(title) < 3:
                continue

            company_node = card.select_one(".emprVaga, .empresa, .nome-empresa, .company")
            location_node = card.select_one(".local, .vaga-local, .location")
            description = clean_text(card.get_text(" ", strip=True))

            raw = {
                "title": title,
                "company": clean_text(company_node.get_text(" ", strip=True)) if company_node else "Vagas.com",
                "location": clean_text(location_node.get_text(" ", strip=True)) if location_node else "",
                "url": url,
                "description": description,
            }

            normalized = self.normalize_job(raw)
            if normalized and normalized.external_id not in seen:
                jobs.append(normalized)
                seen.add(normalized.external_id)

            if len(jobs) >= limit:
                break

        logger.info("vagas_fetch_done provider=%s total_collected=%s", self.provider_name, len(jobs))
        return jobs

    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        title = clean_text(str(raw.get("title") or ""))
        url = str(raw.get("url") or "")
        if not title or not url:
            return None

        description = clean_text(str(raw.get("description") or title))
        location = clean_text(str(raw.get("location") or ""))
        remote = any(term in f"{location} {description}".lower() for term in ["remoto", "home office", "remote", "híbrido", "hibrido"])

        return ProviderJob(
            source=self.provider_name,
            external_id=stable_id(self.provider_name, url or title),
            title=title,
            company=clean_text(str(raw.get("company") or "Vagas.com")),
            location=location,
            url=url or "",
            description=description,
            requirements="",
            seniority=self._infer_seniority(f"{title} {description}"),
            employment_type="full_time",
            salary_min=0,
            salary_max=0,
            remote=remote,
        )

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
