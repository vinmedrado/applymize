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


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


class InfoJobsProvider(JobProvider):
    provider_name = "infojobs"
    enabled = True
    base_url = "https://www.infojobs.com.br"

    def build_search_url(self, term: str = "Analista de Dados", city_code: str = "5211323") -> str:
        return f"{self.base_url}/empregos.aspx?palabra={quote_plus(clean_text(term) or 'Analista de Dados')}&poblacion={city_code}"

    def fetch_jobs(self, limit: int = 25, **kwargs: Any) -> list[ProviderJob]:
        requested_limit = min(max(int(limit or 25), 1), 100)
        term = kwargs.get("term") or "Analista de Dados"
        city_code = str(kwargs.get("poblacion") or kwargs.get("city_code") or "5211323")
        search_url = self.build_search_url(term, city_code)

        logger.info("infojobs_fetch_jobs url=%s term=%s limit=%s", search_url, term, requested_limit)
        response = requests.get(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7",
            },
            timeout=25,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("div.element-vaga, div.js_cardLink, div[data-id], article, .vaga, .job-card")
        if not cards:
            cards = soup.select("a[href*='vaga'], a[href*='emprego']")

        jobs: list[ProviderJob] = []
        seen: set[str] = set()
        for card in cards:
            raw = self._extract_raw(card)
            normalized = self.normalize_job(raw)
            if normalized and normalized.external_id not in seen:
                jobs.append(normalized)
                seen.add(normalized.external_id)
            if len(jobs) >= requested_limit:
                break

        logger.info("infojobs_fetch_done total_collected=%s", len(jobs))
        return jobs

    def _extract_raw(self, card: Any) -> dict[str, str]:
        link = card if getattr(card, "name", "") == "a" else card.select_one("a[href]")
        href = clean_text(link.get("href") if link else "")
        url = urljoin(self.base_url, href)

        title_node = card.select_one("h2, h3, h4, .h3, .h4, .title, .js_vacancyTitle, a") if getattr(card, "select_one", None) else None
        title = clean_text(title_node.get_text(" ", strip=True) if title_node else card.get_text(" ", strip=True))
        company_node = card.select_one(".company, .empresa, .js_companyName, .text-muted") if getattr(card, "select_one", None) else None
        location_node = card.select_one(".location, .local, .js_vacancyLocation, [class*='location']") if getattr(card, "select_one", None) else None
        description = clean_text(card.get_text(" ", strip=True))

        return {
            "title": title,
            "company": clean_text(company_node.get_text(" ", strip=True) if company_node else "InfoJobs"),
            "location": clean_text(location_node.get_text(" ", strip=True) if location_node else "São Paulo, Brasil"),
            "url": url,
            "description": description,
        }

    def normalize_job(self, raw: dict[str, Any]) -> ProviderJob | None:
        title = clean_text(raw.get("title"))
        url = clean_text(raw.get("url"))
        if not title or len(title) < 3 or not url or "infojobs" not in url.lower():
            return None

        description = clean_text(raw.get("description") or title)
        location = clean_text(raw.get("location") or "São Paulo, Brasil")
        remote = any(word in f"{title} {location} {description}".lower() for word in ["remoto", "home office", "híbrido", "hibrido", "remote", "hybrid"])

        return ProviderJob(
            source=self.provider_name,
            external_id=stable_id(self.provider_name, url),
            title=title[:255],
            company=clean_text(raw.get("company") or "InfoJobs")[:255],
            location=location[:255],
            url=url,
            description=description or title,
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
