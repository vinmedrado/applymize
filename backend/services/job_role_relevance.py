from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable


_STOPWORDS = {
    "a", "as", "de", "da", "das", "do", "dos", "e", "em", "para", "com",
    "jr", "junior", "pl", "pleno", "sr", "senior", "analista", "assistente",
    "especialista", "coordenador", "coordenadora", "gerente", "pessoa",
}

_AUTOMATION_PROCESS_ALIASES = (
    "Automação de Processos",
    "Analista de Processos",
    "RPA",
    "BPM",
    "Power Automate",
    "Melhoria Contínua",
    "Excelência Operacional",
    "Workflow",
)

_AUTOMATION_ROLE_MARKERS = {
    "automacao", "processo", "processos", "rpa", "bpm", "workflow",
    "power automate", "melhoria continua", "excelencia operacional",
}

_AUTOMATION_SUPPORT_TITLE_MARKERS = {
    "operacoes", "operacional", "melhoria", "eficiencia", "excelencia",
}

_AUTOMATION_NEGATIVE_TITLE_MARKERS = {
    "financeiro", "comercial", "vendas", "marketing", "renda fixa", "middle office",
    "armazem", "armazens", "logistica", "seguranca da informacao", "qualidade",
    "qa", "testes", "suporte", "atendimento", "product manager", "sinistros",
    "ambiental", "meio ambiente", "roll up",
    "bolsista", "contabil", "contabilidade", "sucesso do cliente",
}


@dataclass(frozen=True)
class RoleRelevance:
    score: float
    relevant: bool
    matched_terms: list[str]
    reason: str


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    text = re.sub(r"[^a-z0-9+#.]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = str(value or "").strip()
        key = normalize_text(cleaned)
        if cleaned and key and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def role_search_terms(target_role: str, configured_terms: Iterable[str] | None = None) -> list[str]:
    configured = _dedupe(configured_terms or [])
    if configured:
        return configured[:8]

    role = str(target_role or "").strip()
    normalized = normalize_text(role)
    if "automacao" in normalized and ("processo" in normalized or "rpa" in normalized):
        return list(_AUTOMATION_PROCESS_ALIASES)
    return [role] if role else []


def provider_search_terms(target_role: str, configured_terms: Iterable[str] | None = None) -> list[str]:
    """Return a bounded query set so scheduled runs do not multiply without control."""
    terms = role_search_terms(target_role, configured_terms)
    if not terms:
        return []
    if "automacao" in normalize_text(target_role) and "processo" in normalize_text(target_role):
        preferred = ("Automação de Processos", "Analista de Processos", "RPA", "Power Automate")
        normalized = {normalize_text(term): term for term in terms}
        ordered = [normalized[normalize_text(term)] for term in preferred if normalize_text(term) in normalized]
        ordered += [term for term in terms if normalize_text(term) not in {normalize_text(item) for item in ordered}]
        return ordered[:4]
    return terms[:4]


def _value(job: Any, key: str) -> str:
    if isinstance(job, dict):
        return str(job.get(key) or "")
    return str(getattr(job, key, "") or "")


def _tokens(value: str) -> set[str]:
    return {token for token in normalize_text(value).split() if len(token) > 1 and token not in _STOPWORDS}


def _contains_marker(text: str, marker: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", text) is not None


def evaluate_role_relevance(
    target_role: str,
    job: Any,
    search_terms: Iterable[str] | None = None,
    threshold: float = 55.0,
) -> RoleRelevance:
    title = normalize_text(_value(job, "title") or _value(job, "title_original"))
    body = normalize_text(" ".join([
        _value(job, "description"),
        _value(job, "description_original"),
        _value(job, "requirements"),
    ]))
    terms = role_search_terms(target_role, search_terms)
    normalized_role = normalize_text(target_role)
    matched: list[str] = []

    automation_family = (
        "automacao" in normalized_role
        and ("processo" in normalized_role or "rpa" in normalized_role)
    )
    if automation_family:
        title_hits = {marker for marker in _AUTOMATION_ROLE_MARKERS if _contains_marker(title, marker)}
        body_hits = {marker for marker in _AUTOMATION_ROLE_MARKERS if _contains_marker(body, marker)}
        support_hits = {marker for marker in _AUTOMATION_SUPPORT_TITLE_MARKERS if _contains_marker(title, marker)}
        negative_hits = {marker for marker in _AUTOMATION_NEGATIVE_TITLE_MARKERS if _contains_marker(title, marker)}
        matched = sorted(title_hits | body_hits)

        if negative_hits:
            score = 35.0
            reason = "título pertence a outra área de negócio"
        elif "automacao de processos" in title or "analista de processos" in title:
            score = 100.0
            reason = "cargo/família aparece diretamente no título"
        elif title_hits - {"automacao"}:
            score = min(96.0, 78.0 + 8.0 * len(title_hits))
            reason = "título contém especialidade de automação/processos"
        elif title_hits == {"automacao"} and any(
            marker in body_hits for marker in {"rpa", "bpm", "workflow", "power automate"}
        ):
            score = 78.0
            reason = "título de automação com especialidade de processos confirmada na descrição"
        elif (
            support_hits
            and not negative_hits
            and len(body_hits) >= 2
            and any(marker in body_hits for marker in {"automacao", "rpa", "bpm", "workflow", "power automate"})
        ):
            score = min(78.0, 54.0 + 8.0 * len(body_hits))
            reason = "título correlato e descrição contém múltiplos sinais da área"
        else:
            score = min(48.0, 12.0 * len(body_hits))
            reason = "aderência insuficiente ao cargo-alvo"

        return RoleRelevance(round(score, 2), score >= threshold, matched, reason)

    title_tokens = _tokens(title)
    role_tokens = _tokens(" ".join(terms) or target_role)
    if not role_tokens:
        return RoleRelevance(100.0, True, [], "cargo-alvo não configurado")

    overlap = title_tokens & role_tokens
    title_ratio = len(overlap) / max(len(role_tokens), 1)
    exact_phrase = any(normalize_text(term) in title for term in terms if normalize_text(term))
    body_tokens = _tokens(body)
    body_ratio = len(body_tokens & role_tokens) / max(len(role_tokens), 1)
    score = 100.0 if exact_phrase else min(100.0, title_ratio * 85.0 + body_ratio * 25.0)
    matched = sorted(overlap | (body_tokens & role_tokens))
    reason = "cargo aparece no título" if exact_phrase else "similaridade lexical entre cargo e vaga"
    return RoleRelevance(round(score, 2), score >= threshold, matched, reason)


def relevance_preferences_for_user(db, user) -> tuple[list[str], float]:
    from backend.models.automation import AutomationSettings

    setting = (
        db.query(AutomationSettings)
        .filter(AutomationSettings.user_id == user.id)
        .order_by(AutomationSettings.id.desc())
        .first()
    )
    return (
        role_search_terms(user.target_role, setting.search_terms if setting else None),
        float(setting.min_role_relevance if setting else 55.0),
    )


def relevant_jobs_for_user(db, user, jobs: Iterable[Any], include_manual: bool = True) -> list[Any]:
    terms, threshold = relevance_preferences_for_user(db, user)
    return [
        job for job in jobs
        if (include_manual and _value(job, "source") == "manual")
        or evaluate_role_relevance(user.target_role, job, terms, threshold).relevant
    ]
