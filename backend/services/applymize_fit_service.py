from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.profile import UserExperience, UserProject, UserSkill
from backend.models.user import User
from backend.services.ai.providers.groq_provider import GroqProvider
from backend.services.ai.providers.ollama_provider import OllamaProvider
from backend.services.profile_service import get_or_create_profile

logger = get_logger(__name__)


@dataclass
class FitQuestion:
    id: str
    title: str
    question: str
    dimension: str
    what_recruiter_expects: str


@dataclass
class FitSession:
    session_id: str
    company: str
    target_role: str
    focus: str
    profile_summary: str
    questions: list[FitQuestion]
    provider: str
    model: str
    fallback_used: bool


@dataclass
class FitEvaluation:
    score: int
    level: str
    recruiter_reading: str
    strengths: list[str]
    risks: list[str]
    improved_answer: str
    next_tip: str
    provider: str
    model: str
    fallback_used: bool


DEFAULT_DIMENSIONS = [
    "Comunicação",
    "Colaboração",
    "Autonomia",
    "Organização",
    "Adaptabilidade",
]


def _clip(value: Any, limit: int = 1000) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def _safe_json(text: str) -> dict[str, Any]:
    content = text.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content, flags=re.IGNORECASE).strip()
        content = re.sub(r"```$", "", content).strip()
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if match:
        content = match.group(0)
    return json.loads(content)


def _list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [_clip(item, 260) for item in value if str(item or "").strip()]
        return items[:5] or fallback
    return fallback


def build_fit_context(db: Session, tenant_id: int, user: User) -> str:
    profile = get_or_create_profile(db, tenant_id, user)
    skills = (
        db.query(UserSkill)
        .filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user.id)
        .order_by(UserSkill.id.desc())
        .limit(25)
        .all()
    )
    experiences = (
        db.query(UserExperience)
        .filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user.id)
        .order_by(UserExperience.id.desc())
        .limit(8)
        .all()
    )
    projects = (
        db.query(UserProject)
        .filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user.id)
        .order_by(UserProject.id.desc())
        .limit(6)
        .all()
    )

    parts = [
        f"Nome: {_clip(profile.full_name or user.full_name, 160)}",
        f"Cargo alvo: {_clip(profile.professional_title or user.target_role, 180)}",
        f"Senioridade: {_clip(user.seniority, 80)}",
        f"Skills do cadastro: {_clip(user.skills, 700)}",
        f"Resumo profissional: {_clip(profile.summary or profile.resume_text, 1200)}",
    ]
    if skills:
        parts.append("Skills estruturadas: " + ", ".join(_clip(s.name, 80) for s in skills))
    if experiences:
        exp = []
        for item in experiences:
            exp.append(f"{item.role} em {item.company}: {_clip(item.description or item.achievements, 420)}")
        parts.append("Experiências: " + " | ".join(exp))
    if projects:
        proj = []
        for item in projects:
            proj.append(f"{item.name}: {_clip(item.description, 320)}")
        parts.append("Projetos: " + " | ".join(proj))
    return "\n".join(parts)


async def _call_ai(messages: list[dict[str, str]], timeout_seconds: float | None = None) -> dict[str, str | bool]:
    timeout = timeout_seconds or settings.career_ai_timeout_seconds
    groq = GroqProvider()
    if groq.is_configured():
        try:
            result = await groq.chat(messages, timeout_seconds=timeout)
            return {"answer": result["answer"], "provider": result["provider"], "model": result["model"], "fallback_used": False}
        except Exception as exc:
            logger.warning("applymize_fit_groq_failed error=%s", exc)

    ollama = OllamaProvider()
    if ollama.is_configured():
        try:
            result = await ollama.chat(messages, timeout_seconds=max(timeout, 35))
            return {"answer": result["answer"], "provider": result["provider"], "model": result["model"], "fallback_used": True}
        except Exception as exc:
            logger.warning("applymize_fit_ollama_failed error=%s", exc)

    raise RuntimeError("Nenhum provedor de IA disponível para o Applymize Fit.")


def _fallback_questions(company: str, target_role: str, focus: str, context: str) -> FitSession:
    role = target_role or "cargo alvo"
    company_label = company or "empresa alvo"
    dimensions = DEFAULT_DIMENSIONS
    questions = [
        FitQuestion("q1", "Pressão e priorização", f"Imagine que você está em um processo na {company_label} para {role}. Conte uma situação em que precisou lidar com pressão, prazos curtos e prioridades conflitantes.", dimensions[3], "RH espera organização, critério de priorização, comunicação e foco em resultado."),
        FitQuestion("q2", "Colaboração", "Descreva uma situação em que precisou trabalhar com pessoas de áreas diferentes para resolver um problema.", dimensions[1], "Recrutadores buscam cooperação, escuta ativa, alinhamento e maturidade para lidar com opiniões diferentes."),
        FitQuestion("q3", "Autonomia com responsabilidade", "Conte um exemplo em que você tomou iniciativa para melhorar um processo ou entregar algo sem depender de cobrança constante.", dimensions[2], "A resposta deve mostrar iniciativa, ownership, responsabilidade e impacto concreto."),
        FitQuestion("q4", "Feedback e evolução", "Fale sobre uma vez em que recebeu feedback e precisou ajustar sua forma de trabalhar.", dimensions[4], "RH observa abertura para aprender, humildade profissional e capacidade de evolução."),
        FitQuestion("q5", "Comunicação", "Como você explicaria um projeto técnico para uma pessoa de RH ou negócio que não domina tecnologia?", dimensions[0], "A resposta deve traduzir o técnico em impacto, clareza e valor para o negócio."),
    ]
    if focus and "lider" in focus.lower():
        questions[1] = FitQuestion("q2", "Influência sem autoridade", "Conte uma situação em que precisou influenciar pessoas sem ser o líder formal do time.", "Liderança", "RH espera influência, comunicação, negociação e responsabilidade sem imposição.")
    return FitSession(str(uuid.uuid4()), company_label, role, focus or "Fit cultural geral", _clip(context, 700), questions, "internal", "fallback-fit-v1", True)


def _fallback_evaluation(answer: str, question: str, company: str, target_role: str, context: str) -> FitEvaluation:
    text = answer.strip()
    length_score = min(35, max(8, len(text) // 18))
    has_result = bool(re.search(r"\b(resultado|reduzi|aumentei|melhorei|impacto|entreguei|consegui|%|por cento|indicador|kpi)\b", text, re.I))
    has_action = bool(re.search(r"\b(fiz|criei|organizei|alinhei|automatizei|analisei|priorizei|conversei|desenvolvi)\b", text, re.I))
    has_context = len(text.split()) >= 35
    score = 42 + length_score + (12 if has_result else 0) + (8 if has_action else 0) + (6 if has_context else 0)
    score = max(35, min(92, score))
    level = "Forte" if score >= 82 else "Boa base" if score >= 68 else "Precisa melhorar"
    risks = []
    if not has_result:
        risks.append("Faltou deixar mais claro o resultado ou impacto da situação.")
    if not has_context:
        risks.append("A resposta ainda parece curta; inclua contexto, ação e resultado.")
    if not risks:
        risks.append("Pode ficar ainda mais forte conectando a resposta ao cargo alvo.")
    improved = "Eu explicaria com contexto, ação e resultado: primeiro apresentaria o problema, depois o que fiz de forma objetiva e, por fim, o impacto gerado para o time ou negócio."
    if text:
        improved = f"Uma forma mais forte seria: '{_clip(text, 300)}'. Depois eu fecharia destacando o resultado concreto e o aprendizado que isso trouxe para minha atuação profissional."
    return FitEvaluation(
        score=score,
        level=level,
        recruiter_reading="A resposta demonstra potencial, mas fica mais competitiva quando conecta comportamento com impacto concreto e maturidade profissional.",
        strengths=["Mostra intenção de explicar uma experiência real.", "Pode ser bem alinhada ao perfil se trouxer contexto, ação e resultado."],
        risks=risks,
        improved_answer=improved,
        next_tip="Use a estrutura CAR: Contexto, Ação e Resultado. Isso costuma funcionar muito bem em testes comportamentais e entrevistas.",
        provider="internal",
        model="fallback-fit-v1",
        fallback_used=True,
    )


async def start_fit_session(db: Session, tenant_id: int, user: User, company: str, target_role: str, focus: str) -> FitSession:
    context = build_fit_context(db, tenant_id, user)
    system = (
        "Você é o Applymize Fit, especialista em testes comportamentais, fit cultural, Gupy e entrevistas. "
        "Gere perguntas realistas e úteis, baseadas no perfil do usuário, empresa alvo e cargo. "
        "Não invente experiências. Responda SOMENTE em JSON válido."
    )
    user_prompt = f"""
Contexto profissional do usuário:
{context}

Empresa alvo: {company or 'não informada'}
Cargo alvo: {target_role or user.target_role or 'não informado'}
Foco do treino: {focus or 'fit cultural geral'}

Crie 5 perguntas de fit cultural/comportamental no estilo Gupy/RH.
Cada pergunta deve ter: id, title, question, dimension, what_recruiter_expects.
Também retorne profile_summary em 2 frases sobre como adaptar o treino ao usuário.
Formato JSON obrigatório:
{{
  "profile_summary": "...",
  "questions": [
    {{"id":"q1","title":"...","question":"...","dimension":"...","what_recruiter_expects":"..."}}
  ]
}}
"""
    try:
        ai = await _call_ai([{"role": "system", "content": system}, {"role": "user", "content": user_prompt}])
        data = _safe_json(str(ai["answer"]))
        raw_questions = data.get("questions") or []
        questions: list[FitQuestion] = []
        for idx, item in enumerate(raw_questions[:5], start=1):
            questions.append(
                FitQuestion(
                    id=_clip(item.get("id") or f"q{idx}", 20),
                    title=_clip(item.get("title") or f"Pergunta {idx}", 120),
                    question=_clip(item.get("question") or "Conte uma situação profissional relevante.", 700),
                    dimension=_clip(item.get("dimension") or DEFAULT_DIMENSIONS[(idx - 1) % len(DEFAULT_DIMENSIONS)], 120),
                    what_recruiter_expects=_clip(item.get("what_recruiter_expects") or "RH espera clareza, maturidade e exemplo concreto.", 500),
                )
            )
        if len(questions) < 3:
            raise ValueError("IA retornou poucas perguntas")
        return FitSession(str(uuid.uuid4()), company or "Empresa alvo", target_role or user.target_role or "Cargo alvo", focus or "Fit cultural geral", _clip(data.get("profile_summary") or context, 900), questions, str(ai["provider"]), str(ai["model"]), bool(ai["fallback_used"]))
    except Exception as exc:
        logger.warning("applymize_fit_start_fallback tenant_id=%s user_id=%s error=%s", tenant_id, user.id, exc)
        return _fallback_questions(company, target_role or user.target_role or "Cargo alvo", focus, context)


async def evaluate_fit_answer(db: Session, tenant_id: int, user: User, company: str, target_role: str, focus: str, question: str, answer: str) -> FitEvaluation:
    context = build_fit_context(db, tenant_id, user)
    system = (
        "Você é o Applymize Fit, especialista em fit cultural, Gupy, entrevistas e leitura de RH. "
        "Avalie a resposta com rigor profissional, sem humilhar o usuário. "
        "Use o contexto do currículo/perfil apenas para coerência. Não invente experiências. "
        "Responda SOMENTE em JSON válido."
    )
    user_prompt = f"""
Contexto profissional do usuário:
{context}

Empresa alvo: {company or 'não informada'}
Cargo alvo: {target_role or user.target_role or 'não informado'}
Foco do treino: {focus or 'fit cultural geral'}
Pergunta feita: {question}
Resposta do usuário: {answer}

Avalie como um RH/recrutador perceberia esta resposta.
Retorne JSON obrigatório:
{{
  "score": 0-100,
  "level": "Precisa melhorar | Boa base | Forte | Excelente",
  "recruiter_reading": "...",
  "strengths": ["..."],
  "risks": ["..."],
  "improved_answer": "resposta reescrita em primeira pessoa, natural para entrevista",
  "next_tip": "..."
}}
"""
    try:
        ai = await _call_ai([{"role": "system", "content": system}, {"role": "user", "content": user_prompt}])
        data = _safe_json(str(ai["answer"]))
        score = int(float(data.get("score", 70)))
        score = max(0, min(100, score))
        return FitEvaluation(
            score=score,
            level=_clip(data.get("level") or ("Forte" if score >= 82 else "Boa base" if score >= 68 else "Precisa melhorar"), 80),
            recruiter_reading=_clip(data.get("recruiter_reading") or "A resposta foi avaliada com base em clareza, maturidade e impacto.", 900),
            strengths=_list(data.get("strengths"), ["Boa base para estruturar uma resposta comportamental."]),
            risks=_list(data.get("risks"), ["Inclua mais contexto, ação e resultado para fortalecer a resposta."]),
            improved_answer=_clip(data.get("improved_answer") or answer, 1200),
            next_tip=_clip(data.get("next_tip") or "Use contexto, ação e resultado.", 500),
            provider=str(ai["provider"]),
            model=str(ai["model"]),
            fallback_used=bool(ai["fallback_used"]),
        )
    except Exception as exc:
        logger.warning("applymize_fit_evaluate_fallback tenant_id=%s user_id=%s error=%s", tenant_id, user.id, exc)
        return _fallback_evaluation(answer, question, company, target_role or user.target_role or "Cargo alvo", context)
