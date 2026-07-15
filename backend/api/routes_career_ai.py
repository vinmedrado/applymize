from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.career_ai import CareerAIConversation, CareerAIMessage
from backend.services.ai.career_ai_service import CareerAIService, create_conversation, get_user_conversation

logger = get_logger(__name__)
router = APIRouter(prefix="/api/career-ai", tags=["career-ai"])


class CareerAIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000)
    conversation_id: int | None = None


class CareerAIChatResponse(BaseModel):
    conversation_id: int
    answer: str
    provider: str
    model: str
    fallback_used: bool = False


class CareerAIConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class CareerAIConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)


class CareerAIConversationResponse(BaseModel):
    id: int
    title: str
    summary: str = ""
    pinned: bool = False
    archived: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CareerAIMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    provider: str = ""
    model: str = ""
    tokens_estimated: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


def _conversation_or_404(db: Session, ctx: AuthContext, conversation_id: int) -> CareerAIConversation:
    conversation = get_user_conversation(db, ctx.tenant_id, ctx.user.id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversation


@router.get("/conversations", response_model=list[CareerAIConversationResponse])
def list_conversations(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return (
        db.query(CareerAIConversation)
        .filter(
            CareerAIConversation.tenant_id == ctx.tenant_id,
            CareerAIConversation.user_id == ctx.user.id,
            CareerAIConversation.archived.is_(False),
        )
        .order_by(CareerAIConversation.pinned.desc(), CareerAIConversation.updated_at.desc())
        .limit(80)
        .all()
    )


@router.post("/conversations", response_model=CareerAIConversationResponse)
def create_career_ai_conversation(payload: CareerAIConversationCreateRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    conversation = create_conversation(db, ctx.tenant_id, ctx.user.id, title=payload.title or "Nova conversa")
    db.commit()
    db.refresh(conversation)
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=CareerAIConversationResponse)
def rename_career_ai_conversation(conversation_id: int, payload: CareerAIConversationUpdateRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    conversation = _conversation_or_404(db, ctx, conversation_id)
    conversation.title = payload.title.strip()[:120] or "Nova conversa"
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    logger.info("career_ai_conversation_renamed tenant_id=%s user_id=%s conversation_id=%s", ctx.tenant_id, ctx.user.id, conversation.id)
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_career_ai_conversation(conversation_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    conversation = _conversation_or_404(db, ctx, conversation_id)
    db.delete(conversation)
    db.commit()
    logger.info("career_ai_conversation_deleted tenant_id=%s user_id=%s conversation_id=%s", ctx.tenant_id, ctx.user.id, conversation_id)
    return {"ok": True}


@router.get("/conversations/{conversation_id}/messages", response_model=list[CareerAIMessageResponse])
def list_career_ai_messages(conversation_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    _conversation_or_404(db, ctx, conversation_id)
    return (
        db.query(CareerAIMessage)
        .filter(
            CareerAIMessage.tenant_id == ctx.tenant_id,
            CareerAIMessage.user_id == ctx.user.id,
            CareerAIMessage.conversation_id == conversation_id,
        )
        .order_by(CareerAIMessage.created_at.asc(), CareerAIMessage.id.asc())
        .limit(300)
        .all()
    )


@router.post("/chat", response_model=CareerAIChatResponse)
async def career_ai_chat(payload: CareerAIChatRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    service = CareerAIService()
    try:
        result = await service.chat(db, ctx.tenant_id, ctx.user, payload.message, payload.conversation_id)
    except ValueError as exc:
        message = str(exc)
        status_code = 429 if ("Muitas mensagens" in message or "Limite diário" in message) else 400
        if "não encontrada" in message.lower() or "sem acesso" in message.lower():
            status_code = 404
        raise HTTPException(status_code=status_code, detail=message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return CareerAIChatResponse(conversation_id=result.conversation_id, answer=result.answer, provider=result.provider, model=result.model, fallback_used=result.fallback_used)
