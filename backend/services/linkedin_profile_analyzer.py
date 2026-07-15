from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)

TECH_KEYWORDS = {
    "dados", "data", "python", "sql", "power bi", "excel", "etl", "dashboard", "analytics",
    "automação", "automation", "api", "postgresql", "sqlite", "fastapi", "machine learning",
    "business intelligence", "bi", "kpi", "dax", "power query", "pipeline", "indicadores",
}

ACTION_WORDS = {
    "desenvolvi", "criei", "automatizei", "implementei", "reduzi", "otimizei", "integrei",
    "analisei", "liderei", "construí", "estruturei", "entreguei", "melhorei", "implantei",
}

RESULT_WORDS = {
    "redução", "reduzi", "aumento", "resultado", "impacto", "%", "kpi", "indicadores", "produtividade",
    "eficiência", "tempo", "custo", "decisão", "estratégica", "performance", "melhoria",
}

SECTION_HINTS = {
    "headline": ["analista", "data", "dados", "bi", "business intelligence", "automação", "automation", "python", "sql"],
    "about": ["sobre", "experiência", "profissional", "atuação", "projetos", "resultados"],
    "experience": ["experiência", "empresa", "cargo", "responsabilidades", "conquistas", "resultados"],
    "skills": ["competências", "skills", "habilidades", "python", "sql", "power bi", "excel"],
}

@dataclass
class LinkedInAnalysisResult:
    score: int
    categories: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    ats_keywords: list[str]
    suggested_headline: str
    suggested_about: str
    recruiter_feedback: str
    ats_feedback: str
    improvement_actions: list[str]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _contains_any(text: str, words: set[str] | list[str]) -> bool:
    low = text.lower()
    return any(word.lower() in low for word in words)


def _extract_keywords(text: str) -> list[str]:
    low = text.lower()
    found = sorted({keyword for keyword in TECH_KEYWORDS if keyword in low})
    return found[:18]


def _score_length(text: str, min_chars: int, ideal_chars: int) -> int:
    length = len(text)
    if length <= 0:
        return 0
    if length < min_chars:
        return max(20, int((length / min_chars) * 55))
    if length <= ideal_chars:
        return 85
    return 78


def _infer_focus(keywords: list[str]) -> str:
    if any(k in keywords for k in ["power bi", "bi", "business intelligence", "dashboard"]):
        return "BI, dados e automação"
    if any(k in keywords for k in ["python", "sql", "etl", "pipeline"]):
        return "dados, SQL e automação"
    return "dados, tecnologia e melhoria de processos"


def analyze_linkedin_profile(profile_text: str, linkedin_url: str | None = None, target_role: str | None = None) -> LinkedInAnalysisResult:
    text = _normalize(profile_text)
    low = text.lower()
    target = (target_role or "Analista de Dados").strip() or "Analista de Dados"
    keywords = _extract_keywords(text)

    headline_score = 45
    if _contains_any(low, SECTION_HINTS["headline"]):
        headline_score += 25
    if target.lower() in low or "analista" in low:
        headline_score += 15
    if any(k in low for k in ["resultado", "automação", "bi", "sql", "python"]):
        headline_score += 10
    headline_score = min(100, headline_score)

    about_score = _score_length(text, 350, 1600)
    if _contains_any(low, RESULT_WORDS):
        about_score += 8
    if len(keywords) >= 5:
        about_score += 7
    about_score = min(100, about_score)

    experience_score = 40
    if _contains_any(low, ACTION_WORDS):
        experience_score += 20
    if _contains_any(low, RESULT_WORDS):
        experience_score += 20
    if any(char.isdigit() for char in text):
        experience_score += 10
    if len(text) > 900:
        experience_score += 10
    experience_score = min(100, experience_score)

    keyword_score = min(100, 35 + len(keywords) * 6)
    clarity_score = 80 if len(text) < 2500 else 72
    if len(text) < 250:
        clarity_score = 48
    if "responsável por" in low and not _contains_any(low, RESULT_WORDS):
        clarity_score -= 8
    clarity_score = max(0, min(100, clarity_score))

    ats_score = int((keyword_score * 0.45) + (experience_score * 0.35) + (clarity_score * 0.20))
    seniority_score = 55
    if any(term in low for term in ["pleno", "senior", "sênior", "especialista", "coordenador"]):
        seniority_score += 20
    if _contains_any(low, RESULT_WORDS):
        seniority_score += 15
    if len(keywords) >= 7:
        seniority_score += 10
    seniority_score = min(100, seniority_score)

    categories = {
        "headline": headline_score,
        "about": about_score,
        "experiencia": experience_score,
        "palavras_chave": keyword_score,
        "clareza": clarity_score,
        "ats_readiness": ats_score,
        "senioridade_percebida": seniority_score,
    }
    score = int(sum(categories.values()) / len(categories))

    strengths: list[str] = []
    if len(keywords) >= 5:
        strengths.append("O perfil já possui boas palavras-chave técnicas para busca e ATS.")
    if _contains_any(low, RESULT_WORDS):
        strengths.append("Há sinais de impacto e resultados, o que melhora a percepção de recrutadores.")
    if _contains_any(low, ACTION_WORDS):
        strengths.append("A experiência usa verbos de ação, deixando a trajetória mais ativa e profissional.")
    if not strengths:
        strengths.append("O perfil tem uma base inicial, mas precisa comunicar melhor foco, impacto e palavras-chave.")

    weaknesses: list[str] = []
    if len(text) < 450:
        weaknesses.append("O texto está curto para transmitir posicionamento profissional com força.")
    if len(keywords) < 5:
        weaknesses.append("Faltam palavras-chave técnicas relevantes para melhorar descoberta por recrutadores.")
    if not _contains_any(low, RESULT_WORDS):
        weaknesses.append("Faltam resultados mensuráveis ou impactos claros nas experiências.")
    if not any(k in low for k in ["power bi", "sql", "python", "excel", "etl"]):
        weaknesses.append("As ferramentas principais não aparecem com força suficiente no texto analisado.")

    missing_keywords = [k for k in ["Power BI", "SQL", "Python", "ETL", "Dashboards", "KPIs", "Power Query", "Automação", "Análise de Dados"] if k.lower() not in low]
    ats_keywords = keywords + missing_keywords[: max(0, 10 - len(keywords))]

    focus = _infer_focus(keywords)
    suggested_headline = f"{target} | {focus} | SQL, Power BI e automação de processos"
    suggested_about = (
        f"Sou profissional com atuação em {focus}, com experiência em transformar dados e processos em soluções mais eficientes para o negócio. "
        "Minha trajetória combina análise, automação, construção de indicadores e melhoria operacional, conectando ferramentas como SQL, Power BI, Excel/Power Query e Python para apoiar decisões e reduzir retrabalho. "
        "Busco oportunidades em que eu possa aplicar visão analítica, organização de dados e automação para gerar impacto mensurável."
    )

    recruiter_feedback = (
        "Para recrutadores, o perfil fica mais forte quando comunica rapidamente cargo-alvo, ferramentas principais e impacto. "
        "Priorize uma headline objetiva e experiências com resultados, não apenas responsabilidades."
    )
    ats_feedback = (
        "Para ATS e busca no LinkedIn, reforce palavras-chave alinhadas à vaga-alvo, como SQL, Power BI, Python, ETL, dashboards, KPIs e automação, quando forem verdadeiras no perfil."
    )
    improvement_actions = [
        "Adicionar uma headline com cargo-alvo + especialidade + principais ferramentas.",
        "Reescrever o Sobre em primeira pessoa, conectando experiência, ferramentas e impacto.",
        "Transformar responsabilidades em conquistas com números, prazos, redução de tempo ou ganho de eficiência.",
        "Padronizar palavras-chave técnicas iguais às usadas nas vagas desejadas.",
    ]

    logger.info("linkedin_profile_analysis_finished score=%s keywords=%s url_present=%s", score, len(keywords), bool(linkedin_url))
    return LinkedInAnalysisResult(
        score=score,
        categories=categories,
        strengths=strengths,
        weaknesses=weaknesses,
        ats_keywords=ats_keywords[:18],
        suggested_headline=suggested_headline,
        suggested_about=suggested_about,
        recruiter_feedback=recruiter_feedback,
        ats_feedback=ats_feedback,
        improvement_actions=improvement_actions,
    )
