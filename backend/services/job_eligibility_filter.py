from __future__ import annotations

import re
import unicodedata
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)

_OPTIONAL_MARKERS = (
    "desejavel",
    "desejaveis",
    "diferencial",
    "sera um diferencial",
    "será um diferencial",
    "plus",
    "nice to have",
    "preferencialmente",
    # Signals that an in-progress degree is accepted, not just a finished one.
    "cursando",
    "em andamento",
    "em curso",
    "completo ou cursando",
    "cursando ou completo",
    "trancado",
)

_BLOCKING_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("superior_completo_obrigatorio", (
        "ensino superior completo",
        "superior completo",
        "nivel superior completo",
        "curso superior completo",
        "ensino superior concluido",
        "formacao superior concluida",
        "formacao completa em nivel superior",
        "diploma de nivel superior",
        "graduacao completa",
        "graduado em",
        "formado em nivel superior",
        "superior completo obrigatorio",
        "formacao superior completa",
        "bacharelado completo",
    )),
    ("ingles_avancado_ou_fluente_obrigatorio", (
        "ingles avancado",
        "inglês avançado",
        "ingles fluente",
        "inglês fluente",
        "advanced english",
        "fluent english",
    )),
    ("espanhol_avancado_ou_fluente_obrigatorio", (
        "espanhol avancado",
        "espanhol avançado",
        "espanhol fluente",
    )),
    ("mba_ou_pos_obrigatorio", (
        "mba obrigatorio",
        "mba obrigatório",
        "pos-graduacao obrigatoria",
        "pós-graduação obrigatória",
        "pos graduacao obrigatoria",
        "pós graduação obrigatória",
    )),
    ("certificacao_obrigatoria", (
        "certificacao obrigatoria",
        "certificação obrigatória",
        "certificacoes obrigatorias",
        "certificações obrigatórias",
    )),
)


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _normalize(value: Any) -> str:
    text = _strip_accents(str(value or "")).lower()
    return re.sub(r"\s+", " ", text).strip()


def _job_text(job: Any) -> str:
    parts = []
    for attr in ("title", "company", "location", "description", "requirements", "title_original", "description_original"):
        if isinstance(job, dict):
            value = job.get(attr)
        else:
            value = getattr(job, attr, None)
        if value:
            parts.append(str(value))
    return "\n".join(parts)


def _context_for(text: str, phrase: str, window: int = 120) -> str:
    index = text.find(phrase)
    if index < 0:
        return ""
    start = max(0, index - window)
    end = min(len(text), index + len(phrase) + window)
    return text[start:end]


def _is_optional_requirement(text: str, phrase: str) -> bool:
    context = _context_for(text, phrase)
    if not context:
        return False
    return any(marker in context for marker in _OPTIONAL_MARKERS)

_LINKEDIN_SOURCE_MARKERS = ("linkedin", "linkedin_guest")

_BRAZIL_LINKEDIN_ALLOW_PATTERNS = (
    "brazil",
    "brasil",
    "sao paulo",
    "são paulo",
    "remote brazil",
    "remoto brasil",
)

_FOREIGN_LINKEDIN_BLOCK_REGEXES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("linkedin_foreign_united_states", re.compile(r"\bunited\s+states\b", re.IGNORECASE)),
    ("linkedin_foreign_usa", re.compile(r"\busa\b", re.IGNORECASE)),
    ("linkedin_foreign_us", re.compile(r"(?<![a-z0-9])u\.?s\.?(?![a-z0-9])", re.IGNORECASE)),
    ("linkedin_foreign_remote_us", re.compile(r"\bremote\s*-?\s*u\.?s\.?\b", re.IGNORECASE)),
    ("linkedin_foreign_north_america", re.compile(r"\bnorth\s+america\b", re.IGNORECASE)),
    ("linkedin_foreign_canada", re.compile(r"\bcanada\b", re.IGNORECASE)),
    ("linkedin_foreign_worldwide", re.compile(r"\bworldwide\b", re.IGNORECASE)),
    ("linkedin_foreign_global", re.compile(r"\bglobal\b", re.IGNORECASE)),
    ("linkedin_foreign_anywhere", re.compile(r"\banywhere\b", re.IGNORECASE)),
)


def _job_value(job: Any, attr: str) -> Any:
    if isinstance(job, dict):
        return job.get(attr)
    return getattr(job, attr, None)


def _job_linkedin_scan_text(job: Any) -> str:
    parts = []
    for attr in ("title", "location", "description", "requirements", "url", "source", "title_original", "description_original"):
        value = _job_value(job, attr)
        if value:
            parts.append(str(value))
    return "\n".join(parts)


def _is_linkedin_source(job: Any) -> bool:
    source = _normalize(_job_value(job, "source"))
    url = _normalize(_job_value(job, "url"))
    return any(marker in source for marker in _LINKEDIN_SOURCE_MARKERS) or "linkedin.com" in url


def _linkedin_has_brazil_exception(text: str) -> bool:
    normalized = _normalize(text)
    return any(_normalize(pattern) in normalized for pattern in _BRAZIL_LINKEDIN_ALLOW_PATTERNS)


def linkedin_foreign_blockers(job: Any) -> list[str]:
    """Block LinkedIn jobs that are clearly located outside Brazil.

    Relying only on the provider's search filters (city/state/country) is not
    reliable for LinkedIn, since it also returns global/remote-anywhere and
    US/Canada postings even when a Brazil location is requested. This checks
    the job text for foreign-location markers and only blocks when there is
    no explicit Brazil exception in the same text.
    """
    if not _is_linkedin_source(job):
        return []

    text = _job_linkedin_scan_text(job)
    if _linkedin_has_brazil_exception(text):
        return []

    blockers = [code for code, pattern in _FOREIGN_LINKEDIN_BLOCK_REGEXES if pattern.search(text)]
    if blockers:
        logger.info(
            "linkedin_foreign_blockers_matched job_id=%s url=%s blockers=%s",
            _job_value(job, "id"),
            _job_value(job, "url"),
            blockers,
        )
    return blockers

def is_foreign_linkedin_job(job: Any) -> bool:
    return bool(linkedin_foreign_blockers(job))


_NON_LINKEDIN_FOREIGN_LOCATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("foreign_united_states", re.compile(r"\b(united\s+states|usa|u\.?s\.?)\b", re.IGNORECASE)),
    ("foreign_canada", re.compile(r"\bcanada\b", re.IGNORECASE)),
    ("foreign_peru", re.compile(r"\b(peru|peru)\b", re.IGNORECASE)),
    ("foreign_united_kingdom", re.compile(r"\b(united\s+kingdom|uk|england|scotland)\b", re.IGNORECASE)),
    ("foreign_india", re.compile(r"\bindia\b", re.IGNORECASE)),
    ("foreign_saudi_arabia", re.compile(r"\b(saudi\s+arabia|arabia\s+saudita)\b", re.IGNORECASE)),
)


def foreign_location_blockers(job: Any) -> list[str]:
    """Block jobs explicitly tied to another country for the Brazil-focused MVP."""
    if _is_linkedin_source(job):
        return linkedin_foreign_blockers(job)
    location = _normalize(_job_value(job, "location"))
    if not location or any(marker in location for marker in ("brasil", "brazil")):
        return []
    return [code for code, pattern in _NON_LINKEDIN_FOREIGN_LOCATION_PATTERNS if pattern.search(location)]


def evaluate_job_eligibility(job: Any) -> dict[str, Any]:
    """Evaluate if a job can be sent automatically to the user.

    Conservative rule: block only when an unsupported requirement appears as mandatory.
    If the same requirement appears near optional markers such as "desejável" or
    "diferencial", keep the job eligible and add a warning/soft penalty.
    """
    text = _normalize(_job_text(job))
    blockers: list[str] = []
    warnings: list[str] = []
    penalty = 0

    location_blockers = foreign_location_blockers(job)
    if location_blockers:
        blockers.extend(location_blockers)
        logger.info(
            "linkedin_job_blocked_foreign_location job_id=%s source=%s location=%s url=%s blockers=%s",
            _job_value(job, "id"),
            _job_value(job, "source"),
            _job_value(job, "location"),
            _job_value(job, "url"),
            location_blockers,
        )

    for blocker_code, phrases in _BLOCKING_RULES:
        matched_optional = False
        matched_blocker = False
        for raw_phrase in phrases:
            phrase = _normalize(raw_phrase)
            if not phrase or phrase not in text:
                continue
            if _is_optional_requirement(text, phrase):
                matched_optional = True
            else:
                matched_blocker = True

        if matched_blocker and blocker_code not in blockers:
            blockers.append(blocker_code)
        elif matched_optional:
            warnings.append(f"requisito_desejavel_detectado:{blocker_code}")
            penalty += 5

    result = {
        "eligible": not blockers,
        "blockers": blockers,
        "penalty": min(penalty, 30),
        "warnings": warnings,
    }
    logger.info(
        "job_eligibility_checked job_id=%s source=%s eligible=%s blockers=%s penalty=%s warnings=%s",
        getattr(job, "id", None) if not isinstance(job, dict) else job.get("id"),
        getattr(job, "source", None) if not isinstance(job, dict) else job.get("source"),
        result["eligible"],
        result["blockers"],
        result["penalty"],
        result["warnings"],
    )
    return result
