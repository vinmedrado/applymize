from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.user import User
from backend.services.matching_engine import calculate_match, split_skills, tokenize
from backend.services.profile_service import profile_context_text, serialize_profile
from backend.services.resume_parser import parse_resume_text


GENERIC_TERMS = {
    "proativo", "dinamico", "dinâmico", "responsavel", "responsável", "comunicativo",
    "trabalho em equipe", "facil aprendizado", "fácil aprendizado", "pontual",
    "dedicado", "comprometido", "sou uma pessoa", "em busca de oportunidade",
}

ATS_SECTIONS = {
    "summary": ["resumo", "objetivo", "profile", "summary"],
    "skills": ["skills", "habilidades", "competencias", "competências", "tecnologias"],
    "experience": ["experiencia", "experiência", "experience", "historico profissional", "carreira"],
    "projects": ["projetos", "projeto", "projects", "portfolio", "github"],
    "education": ["educacao", "educação", "formacao", "formação", "education"],
    "certifications": ["certificacoes", "certificações", "certifications", "certificates", "cursos"],
}


@dataclass
class AtsSuggestion:
    priority: str
    title: str
    description: str


@dataclass
class AtsAnalysis:
    ats_score: float
    rh_score: float
    match_score: float
    keyword_score: float
    experience_score: float
    clarity_score: float
    seniority_score: float
    final_score: float
    grade: str
    probability: str
    strengths: list[str]
    weaknesses: list[str]
    missing_keywords: list[str]
    suggestions: list[AtsSuggestion]
    warnings: list[str]
    compared_job_id: int | None = None


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def clamp(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))


def grade_from_score(score: float) -> str:
    if score >= 95:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 72:
        return "B"
    if score >= 58:
        return "C"
    if score >= 42:
        return "D"
    return "F"


def probability_from_score(score: float) -> str:
    if score >= 85:
        return "Alta probabilidade de passar na triagem inicial."
    if score >= 70:
        return "Boa probabilidade, com ajustes pontuais recomendados."
    if score >= 55:
        return "Probabilidade moderada; revise palavras-chave, clareza e evidências."
    return "Baixa probabilidade; currículo precisa de ajustes importantes antes de aplicar."


def section_presence_score(text: str) -> tuple[float, list[str], list[str]]:
    clean = normalize(text)
    found, missing = [], []
    for section, aliases in ATS_SECTIONS.items():
        if any(normalize(alias) in clean for alias in aliases):
            found.append(section)
        else:
            missing.append(section)
    return clamp(len(found) / len(ATS_SECTIONS) * 100), found, missing


def clarity_score(text: str, parsed: dict[str, Any]) -> tuple[float, list[str]]:
    warnings: list[str] = []
    length = len(text or "")
    score = 70.0

    if 1200 <= length <= 6500:
        score += 18
    elif length < 600:
        score -= 25
        warnings.append("Currículo muito curto para avaliação robusta.")
    elif length > 8500:
        score -= 15
        warnings.append("Currículo muito longo; pode dificultar leitura de RH e ATS.")

    line_count = len([line for line in (text or "").splitlines() if line.strip()])
    if line_count >= 12:
        score += 8
    else:
        score -= 8
        warnings.append("Poucas linhas/seções detectadas; organize melhor o currículo.")

    generic_hits = [term for term in GENERIC_TERMS if term in normalize(text)]
    if len(generic_hits) >= 4:
        score -= 15
        warnings.append("Há excesso de termos genéricos sem evidência prática.")
    elif len(generic_hits) >= 2:
        score -= 8

    if parsed.get("email"):
        score += 3
    else:
        score -= 8
        warnings.append("E-mail não detectado.")
    if parsed.get("phone"):
        score += 3
    else:
        score -= 5
        warnings.append("Telefone não detectado.")
    if parsed.get("linkedin") or parsed.get("github"):
        score += 4

    return clamp(score), warnings


def keyword_score(profile_text: str, job: Job | None, parsed: dict[str, Any]) -> tuple[float, list[str]]:
    if not job:
        skills = parsed.get("skills") or []
        if len(skills) >= 12:
            return 90.0, []
        if len(skills) >= 7:
            return 78.0, []
        if len(skills) >= 4:
            return 62.0, []
        return 38.0, ["Inclua mais skills técnicas específicas."]

    job_terms = list(dict.fromkeys(split_skills(job.requirements) + tokenize(f"{job.title} {job.description} {job.requirements}")[:35]))
    profile_norm = normalize(profile_text)
    missing = []
    matched = 0

    for term in job_terms:
        term_norm = normalize(term)
        if len(term_norm) < 3:
            continue
        if term_norm in profile_norm:
            matched += 1
        else:
            missing.append(term)

    denominator = max(len([t for t in job_terms if len(normalize(t)) >= 3]), 1)
    return clamp(matched / denominator * 100), list(dict.fromkeys(missing))[:18]


def experience_score(profile: dict[str, Any], parsed: dict[str, Any], job: Job | None) -> float:
    experiences = profile.get("experiences") or []
    parsed_exp = parsed.get("experiences") or []
    projects = profile.get("projects") or []
    score = 35.0

    if experiences:
        score += min(len(experiences) * 15, 35)
    elif parsed_exp:
        score += min(len(parsed_exp) * 10, 25)

    if projects:
        score += min(len(projects) * 8, 20)
    elif parsed.get("projects"):
        score += 10

    if job:
        context = normalize(" ".join([
            profile.get("summary", ""),
            profile.get("resume_text", ""),
            " ".join(str(x) for x in parsed_exp),
            " ".join(str(x) for x in parsed.get("projects", [])),
        ]))
        overlap = set(tokenize(context)) & set(tokenize(f"{job.title} {job.description} {job.requirements}"))
        score += min(len(overlap) * 1.2, 18)

    return clamp(score)


def seniority_score(user: User, profile_text: str, job: Job | None) -> float:
    clean = normalize(profile_text)
    user_seniority = normalize(user.seniority or "")
    job_seniority = normalize(job.seniority if job else "")

    inferred = user_seniority or "mid"
    if any(term in clean for term in ["senior", "lider", "lead", "especialista", "principal"]):
        inferred = "senior"
    elif any(term in clean for term in ["junior", "estagio", "trainee"]):
        inferred = "junior"

    order = {"junior": 1, "jr": 1, "mid": 2, "pleno": 2, "senior": 3, "sr": 3, "lead": 4, "principal": 4, "unspecified": 2, "": 2}
    if not job:
        return 80.0 if inferred else 60.0

    u = order.get(inferred, 2)
    j = order.get(job_seniority, 2)

    if abs(u - j) == 0:
        return 95.0
    if u > j:
        return 86.0
    return clamp(95 - abs(u - j) * 25)


def ats_score(text: str, parsed: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    section_score, found_sections, missing_sections = section_presence_score(text)
    skills_count = len(parsed.get("skills") or [])
    contact_score = 0
    contact_score += 35 if parsed.get("email") else 0
    contact_score += 25 if parsed.get("phone") else 0
    contact_score += 20 if parsed.get("linkedin") else 0
    contact_score += 20 if parsed.get("github") else 0
    skills_score = clamp(skills_count * 8)
    score = clamp(section_score * 0.42 + contact_score * 0.20 + skills_score * 0.28 + (10 if len(text) > 1000 else 0))
    return score, found_sections, missing_sections


def rh_score(profile: dict[str, Any], parsed: dict[str, Any], clarity: float, experience: float) -> float:
    summary = profile.get("summary") or ""
    projects = profile.get("projects") or []
    education = profile.get("education") or []
    score = clarity * 0.35 + experience * 0.40
    score += 12 if len(summary) > 140 else 0
    score += 8 if projects or parsed.get("projects") else 0
    score += 5 if education or parsed.get("education") or parsed.get("certifications") else 0
    return clamp(score)


def build_suggestions(
    missing_sections: list[str],
    missing_keywords: list[str],
    warnings: list[str],
    scores: dict[str, float],
) -> list[AtsSuggestion]:
    suggestions: list[AtsSuggestion] = []

    if scores["ats_score"] < 70:
        suggestions.append(AtsSuggestion("alta", "Reforçar estrutura ATS", "Inclua seções claras: Resumo, Skills, Experiência, Projetos, Educação e Certificações."))
    if missing_keywords:
        suggestions.append(AtsSuggestion("alta", "Adicionar palavras-chave da vaga", f"Inclua naturalmente: {', '.join(missing_keywords[:8])}."))
    if scores["experience_score"] < 65:
        suggestions.append(AtsSuggestion("alta", "Evidenciar experiência com impacto", "Use bullets com ação, ferramenta, resultado e métrica."))
    if scores["clarity_score"] < 70:
        suggestions.append(AtsSuggestion("média", "Melhorar clareza", "Reduza termos genéricos e deixe o resumo mais direto e orientado à vaga."))
    if missing_sections:
        suggestions.append(AtsSuggestion("média", "Completar seções ausentes", f"Seções ausentes: {', '.join(missing_sections)}."))
    if warnings:
        suggestions.append(AtsSuggestion("baixa", "Revisar detalhes", "Corrija avisos detectados no currículo antes de aplicar."))

    if not suggestions:
        suggestions.append(AtsSuggestion("baixa", "Ajuste fino", "Currículo bem estruturado. Faça pequenos ajustes de palavras-chave para cada vaga."))

    return suggestions


def analyze_resume(db: Session, tenant_id: int, user: User, job: Job | None = None) -> AtsAnalysis:
    profile = serialize_profile(db, tenant_id, user.id)
    context = profile_context_text(db, tenant_id, user)
    resume_text = profile.get("resume_text") or context or user.skills or ""
    parsed = parse_resume_text(resume_text)
    warnings: list[str] = []

    if profile.get("completeness", 0) < 45:
        warnings.append("Perfil incompleto. Complete Meu Perfil e importe um currículo para análise mais precisa.")
    if not resume_text or len(resume_text) < 250:
        warnings.append("Currículo pouco detalhado. A análise foi feita com dados limitados.")

    ats, found_sections, missing_sections = ats_score(resume_text, parsed)
    clarity, clarity_warnings = clarity_score(resume_text, parsed)
    warnings.extend(clarity_warnings)
    experience = experience_score(profile, parsed, job)
    keywords, missing_keywords = keyword_score(resume_text, job, parsed)
    seniority = seniority_score(user, resume_text, job)

    if job:
        match = calculate_match(user, job, profile_context=context).score
    else:
        match = clamp((keywords * 0.45) + (experience * 0.35) + (seniority * 0.20))

    rh = rh_score(profile, parsed, clarity, experience)
    final = clamp(ats * 0.24 + rh * 0.20 + match * 0.22 + keywords * 0.16 + experience * 0.10 + clarity * 0.08)

    strengths: list[str] = []
    if parsed.get("skills"):
        strengths.append(f"Skills técnicas detectadas: {', '.join(parsed['skills'][:10])}.")
    if parsed.get("linkedin") or parsed.get("github"):
        strengths.append("Links profissionais detectados no currículo.")
    if experience >= 70:
        strengths.append("Experiência/projetos demonstram boa aderência.")
    if keywords >= 75:
        strengths.append("Boa cobertura de palavras-chave.")
    if not strengths:
        strengths.append("Há base inicial para análise, mas o currículo precisa de mais evidências.")

    weaknesses: list[str] = []
    if missing_sections:
        weaknesses.append(f"Seções ausentes ou pouco claras: {', '.join(missing_sections)}.")
    if missing_keywords:
        weaknesses.append("Algumas palavras-chave importantes da vaga não aparecem no currículo.")
    if clarity < 70:
        weaknesses.append("Clareza e objetividade podem melhorar.")
    if experience < 65:
        weaknesses.append("Experiências e projetos precisam de bullets mais orientados a impacto.")

    scores = {
        "ats_score": ats,
        "rh_score": rh,
        "match_score": match,
        "keyword_score": keywords,
        "experience_score": experience,
        "clarity_score": clarity,
        "seniority_score": seniority,
    }

    suggestions = build_suggestions(missing_sections, missing_keywords, warnings, scores)

    return AtsAnalysis(
        ats_score=ats,
        rh_score=rh,
        match_score=match,
        keyword_score=keywords,
        experience_score=experience,
        clarity_score=clarity,
        seniority_score=seniority,
        final_score=final,
        grade=grade_from_score(final),
        probability=probability_from_score(final),
        strengths=strengths,
        weaknesses=weaknesses,
        missing_keywords=missing_keywords,
        suggestions=suggestions,
        warnings=warnings,
        compared_job_id=job.id if job else None,
    )


def serialize_analysis(analysis: AtsAnalysis) -> dict[str, Any]:
    data = asdict(analysis)
    data["suggestions"] = [asdict(item) for item in analysis.suggestions]
    return data
