from __future__ import annotations

import hashlib
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.application import Application
from backend.models.career_ai import CareerAIConversation, CareerAIMessage
from backend.models.profile import UserEducation, UserExperience, UserProfile, UserProject, UserSkill
from backend.models.user import User
from backend.services.ai.prompts.career_prompt_builder import build_messages, format_context_section
from backend.services.ai.providers.groq_provider import GroqProvider
from backend.services.ai.providers.ollama_provider import OllamaProvider
from backend.services.ai_usage_limit_service import assert_daily_limit, record_ai_usage
from backend.services.ats_analyzer import analyze_resume
from backend.services.profile_service import get_or_create_profile

logger = get_logger(__name__)

_RATE_BUCKET: dict[int, deque[float]] = defaultdict(deque)
_RESPONSE_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
RATE_LIMIT_PER_MINUTE = 10
CACHE_TTL_SECONDS = 180
MAX_CONVERSATION_CONTEXT_CHARS = 3600
SUMMARY_AFTER_MESSAGES = 8


@dataclass
class CareerAIResult:
    answer: str
    provider: str
    model: str
    fallback_used: bool
    conversation_id: int


def _clip(text: Any, limit: int = 1200) -> str:
    value = str(text or "").strip()
    return value if len(value) <= limit else value[:limit].rstrip() + "..."


def _clean_text(value: Any) -> str:
    text = str(value or "").replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def _rate_limit_check(user_id: int) -> None:
    now = time.time()
    bucket = _RATE_BUCKET[user_id]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_PER_MINUTE:
        raise ValueError("Muitas mensagens em pouco tempo. Aguarde alguns segundos e tente novamente.")
    bucket.append(now)


def _cache_key(user_id: int, message: str, context: str, conversation_context: str) -> str:
    raw = f"{user_id}:{message.strip().lower()}:{context[:1800]}:{conversation_context[:1200]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_conversation_title(message: str) -> str:
    text = _clean_text(message)
    if not text:
        return "Nova conversa"

    text = re.sub(r"[?!.]+$", "", text)
    stop_prefixes = [
        r"^(me\s+ajude\s+a\s+)",
        r"^(me\s+ajuda\s+a\s+)",
        r"^(como\s+eu\s+posso\s+)",
        r"^(como\s+posso\s+)",
        r"^(explique\s+minha\s+)",
        r"^(explique\s+meu\s+)",
        r"^(resuma\s+minha\s+)",
        r"^(analise\s+meu\s+)",
    ]
    title = text
    for pattern in stop_prefixes:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE).strip()

    if not title:
        title = text
    title = title[:45].strip()
    return title[:1].upper() + title[1:] if title else "Nova conversa"


def get_user_conversation(db: Session, tenant_id: int, user_id: int, conversation_id: int) -> CareerAIConversation | None:
    return (
        db.query(CareerAIConversation)
        .filter(
            CareerAIConversation.id == conversation_id,
            CareerAIConversation.tenant_id == tenant_id,
            CareerAIConversation.user_id == user_id,
            CareerAIConversation.archived.is_(False),
        )
        .first()
    )


def create_conversation(db: Session, tenant_id: int, user_id: int, title: str | None = None, first_message: str | None = None) -> CareerAIConversation:
    conversation = CareerAIConversation(
        tenant_id=tenant_id,
        user_id=user_id,
        title=_clip(title or generate_conversation_title(first_message or ""), 120) or "Nova conversa",
    )
    db.add(conversation)
    db.flush()
    logger.info("career_ai_conversation_created tenant_id=%s user_id=%s conversation_id=%s", tenant_id, user_id, conversation.id)
    return conversation


def build_user_career_context(db: Session, tenant_id: int, user: User) -> str:
    profile = get_or_create_profile(db, tenant_id, user)
    skills = db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user.id).order_by(UserSkill.created_at.desc()).limit(60).all()
    experiences = db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user.id).order_by(UserExperience.created_at.desc()).limit(8).all()
    projects = db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user.id).order_by(UserProject.created_at.desc()).limit(8).all()
    education = db.query(UserEducation).filter(UserEducation.tenant_id == tenant_id, UserEducation.user_id == user.id).order_by(UserEducation.created_at.desc()).limit(6).all()
    applications = (
        db.query(Application)
        .filter(Application.tenant_id == tenant_id, Application.user_id == user.id)
        .order_by(Application.updated_at.desc())
        .limit(6)
        .all()
    )
    user_jobs = []
    seen_job_ids: set[int] = set()
    for application in applications:
        if application.job and application.job.id not in seen_job_ids:
            user_jobs.append(application.job)
            seen_job_ids.add(application.job.id)

    try:
        ats = analyze_resume(db, tenant_id, user, None)
        ats_summary = f"Score ATS: {ats.ats_score} | Score RH: {ats.rh_score} | Final: {ats.final_score} | Grade: {ats.grade} | Alertas: {', '.join(ats.warnings[:4]) or 'sem alertas críticos'}"
    except Exception as exc:
        logger.warning("career_ai_context_ats_failed user_id=%s error=%s", user.id, exc)
        ats_summary = "Análise ATS indisponível no momento."

    sections = [
        "# Perfil principal",
        f"Nome: {_clip(profile.full_name or user.full_name, 180)}",
        f"Título alvo: {_clip(profile.professional_title or user.target_role, 180)}",
        f"Localização: {_clip(profile.location, 180)}",
        f"Preferências: {_clip(profile.work_preferences, 260)}",
        f"Resumo: {_clip(profile.summary, 1000)}",
        f"Currículo base: {_clip(profile.resume_text, 2200)}",
        format_context_section("Skills", [f"{s.name} ({s.level}, {s.category})" for s in skills], 30),
        format_context_section("Experiências", [f"{e.role} em {e.company} ({e.start_date} - {e.end_date}): {e.description} | Resultados: {e.achievements}" for e in experiences], 8),
        format_context_section("Projetos", [f"{p.name}: {p.description} | Tecnologias: {p.technologies} | URL: {p.url}" for p in projects], 8),
        format_context_section("Formação", [f"{e.course} - {e.institution} ({e.start_date} - {e.end_date}): {e.description}" for e in education], 6),
        "## ATS analysis\n" + ats_summary,
        format_context_section("Últimas candidaturas", [f"{a.job.title if a.job else 'Vaga'} - {a.job.company if a.job else ''} | status: {a.status} | notas: {a.notes}" for a in applications], 6),
        format_context_section("Vagas salvas/candidaturas do usuário", [f"{j.title} - {j.company} | {j.location} | {j.source} | requisitos: {j.requirements or j.description[:500]}" for j in user_jobs], 6),
    ]
    return "\n\n".join(part for part in sections if part)


def build_conversation_context(db: Session, conversation: CareerAIConversation) -> str:
    last_messages = (
        db.query(CareerAIMessage)
        .filter(
            CareerAIMessage.tenant_id == conversation.tenant_id,
            CareerAIMessage.user_id == conversation.user_id,
            CareerAIMessage.conversation_id == conversation.id,
        )
        .order_by(CareerAIMessage.created_at.desc(), CareerAIMessage.id.desc())
        .limit(6)
        .all()
    )
    last_messages = list(reversed(last_messages))
    parts: list[str] = []
    if conversation.summary:
        parts.append("## Resumo da conversa anterior\n" + _clip(conversation.summary, 1400))
    if last_messages:
        formatted = []
        for msg in last_messages:
            role = "Usuário" if msg.role == "user" else "Applymize IA" if msg.role == "assistant" else "Sistema"
            formatted.append(f"{role}: {_clip(msg.content, 650)}")
        parts.append("## Últimas mensagens da conversa\n" + "\n".join(formatted))

    context = _clip("\n\n".join(parts), MAX_CONVERSATION_CONTEXT_CHARS)
    logger.info(
        "career_ai_context_built tenant_id=%s user_id=%s conversation_id=%s context_chars=%s",
        conversation.tenant_id,
        conversation.user_id,
        conversation.id,
        len(context),
    )
    return context


def update_conversation_summary_if_needed(db: Session, conversation: CareerAIConversation) -> None:
    count = (
        db.query(CareerAIMessage)
        .filter(
            CareerAIMessage.tenant_id == conversation.tenant_id,
            CareerAIMessage.user_id == conversation.user_id,
            CareerAIMessage.conversation_id == conversation.id,
        )
        .count()
    )
    if count < SUMMARY_AFTER_MESSAGES or count % 4 != 0:
        return

    recent_messages = (
        db.query(CareerAIMessage)
        .filter(
            CareerAIMessage.tenant_id == conversation.tenant_id,
            CareerAIMessage.user_id == conversation.user_id,
            CareerAIMessage.conversation_id == conversation.id,
        )
        .order_by(CareerAIMessage.created_at.desc(), CareerAIMessage.id.desc())
        .limit(12)
        .all()
    )
    recent_messages = list(reversed(recent_messages))
    points: list[str] = []
    for msg in recent_messages:
        if msg.role not in {"user", "assistant"}:
            continue
        role = "Usuário" if msg.role == "user" else "IA"
        points.append(f"{role}: {_clip(msg.content, 260)}")

    previous = _clip(conversation.summary, 900)
    next_summary = (previous + "\n" if previous else "") + "\n".join(points)
    conversation.summary = _clip(next_summary, 1800)
    conversation.updated_at = datetime.utcnow()
    logger.info("career_ai_summary_updated tenant_id=%s user_id=%s conversation_id=%s", conversation.tenant_id, conversation.user_id, conversation.id)


class CareerAIService:
    def __init__(self, groq: GroqProvider | None = None, ollama: OllamaProvider | None = None):
        self.groq = groq or GroqProvider()
        self.ollama = ollama or OllamaProvider()

    async def chat(self, db: Session, tenant_id: int, user: User, message: str, conversation_id: int | None = None) -> CareerAIResult:
        message = (message or "").strip()
        if not message:
            raise ValueError("Mensagem vazia")
        if len(message) > settings.career_ai_max_message_chars:
            raise ValueError("Mensagem muito longa. Envie uma pergunta mais objetiva.")

        _rate_limit_check(user.id)
        try:
            assert_daily_limit(db, tenant_id, user.id, "career_ai", settings.career_ai_daily_limit, "career_ai_limit_reached")
        except PermissionError as exc:
            raise ValueError(str(exc)) from exc

        if conversation_id is None:
            conversation = create_conversation(db, tenant_id, user.id, first_message=message)
        else:
            conversation = get_user_conversation(db, tenant_id, user.id, conversation_id)
            if not conversation:
                raise ValueError("Conversa não encontrada ou sem acesso.")

        user_message = CareerAIMessage(
            tenant_id=tenant_id,
            user_id=user.id,
            conversation_id=conversation.id,
            role="user",
            content=message,
            tokens_estimated=_estimate_tokens(message),
        )
        db.add(user_message)
        conversation.updated_at = datetime.utcnow()
        db.flush()
        logger.info("career_ai_message_saved tenant_id=%s user_id=%s conversation_id=%s role=user", tenant_id, user.id, conversation.id)

        context = build_user_career_context(db, tenant_id, user)
        conversation_context = build_conversation_context(db, conversation)
        key = _cache_key(user.id, message, context, conversation_context)
        cached = _RESPONSE_CACHE.get(key)
        if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
            data = cached[1]
            payload = CareerAIResult(answer=data["answer"], provider=data["provider"], model=data["model"], fallback_used=data.get("fallback_used", False), conversation_id=conversation.id)
        else:
            messages = build_messages(message, context, conversation_context)
            logger.info("career_ai_request user_id=%s tenant_id=%s conversation_id=%s message_chars=%s context_chars=%s conversation_context_chars=%s", user.id, tenant_id, conversation.id, len(message), len(context), len(conversation_context))

            try:
                result = await self.groq.chat(messages, timeout_seconds=settings.career_ai_timeout_seconds)
                payload = CareerAIResult(answer=result["answer"], provider=result["provider"], model=result["model"], fallback_used=False, conversation_id=conversation.id)
                logger.info("career_ai_response user_id=%s conversation_id=%s provider=%s model=%s fallback_used=false", user.id, conversation.id, payload.provider, payload.model)
            except Exception as groq_exc:
                logger.warning("career_ai_fallback user_id=%s conversation_id=%s from_provider=groq error=%s", user.id, conversation.id, groq_exc)
                try:
                    result = await self.ollama.chat(messages, timeout_seconds=max(settings.career_ai_timeout_seconds, 45))
                    payload = CareerAIResult(answer=result["answer"], provider=result["provider"], model=result["model"], fallback_used=True, conversation_id=conversation.id)
                    logger.info("career_ai_response user_id=%s conversation_id=%s provider=%s model=%s fallback_used=true", user.id, conversation.id, payload.provider, payload.model)
                except Exception as ollama_exc:
                    logger.error("career_ai_error user_id=%s conversation_id=%s groq_error=%s ollama_error=%s", user.id, conversation.id, groq_exc, ollama_exc, exc_info=True)
                    db.rollback()
                    raise RuntimeError("Não consegui acessar a IA agora. Verifique GROQ_API_KEY ou o Ollama local e tente novamente.") from ollama_exc

            _RESPONSE_CACHE[key] = (time.time(), payload.__dict__)

        assistant_message = CareerAIMessage(
            tenant_id=tenant_id,
            user_id=user.id,
            conversation_id=conversation.id,
            role="assistant",
            content=payload.answer,
            provider=payload.provider,
            model=payload.model,
            tokens_estimated=_estimate_tokens(payload.answer),
        )
        db.add(assistant_message)
        conversation.updated_at = datetime.utcnow()
        logger.info("career_ai_message_saved tenant_id=%s user_id=%s conversation_id=%s role=assistant provider=%s", tenant_id, user.id, conversation.id, payload.provider)
        record_ai_usage(db, tenant_id, user.id, "career_ai", provider=payload.provider, model=payload.model)
        update_conversation_summary_if_needed(db, conversation)
        db.commit()
        return payload
