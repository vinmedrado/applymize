from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.ai_usage_limit_service import assert_daily_limit, record_ai_usage
from backend.services.applymize_fit_service import evaluate_fit_answer, start_fit_session

logger = get_logger(__name__)
router = APIRouter(prefix="/api/applymize-fit", tags=["applymize-fit"])


class FitStartRequest(BaseModel):
    company: str = Field(default="", max_length=120)
    target_role: str = Field(default="", max_length=160)
    focus: str = Field(default="Fit cultural geral", max_length=200)


class FitQuestionResponse(BaseModel):
    id: str
    title: str
    question: str
    dimension: str
    what_recruiter_expects: str


class FitStartResponse(BaseModel):
    session_id: str
    company: str
    target_role: str
    focus: str
    profile_summary: str
    questions: list[FitQuestionResponse]
    provider: str
    model: str
    fallback_used: bool = False


class FitEvaluateRequest(BaseModel):
    company: str = Field(default="", max_length=120)
    target_role: str = Field(default="", max_length=160)
    focus: str = Field(default="Fit cultural geral", max_length=200)
    question: str = Field(..., min_length=8, max_length=1000)
    answer: str = Field(..., min_length=5, max_length=4000)


class FitEvaluateResponse(BaseModel):
    score: int
    level: str
    recruiter_reading: str
    strengths: list[str]
    risks: list[str]
    improved_answer: str
    next_tip: str
    provider: str
    model: str
    fallback_used: bool = False


def _fit_limit() -> int:
    return int(getattr(settings, "applymize_fit_daily_limit", 8))


@router.post("/start", response_model=FitStartResponse)
async def start_fit(payload: FitStartRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    try:
        assert_daily_limit(db, ctx.tenant_id, ctx.user.id, "applymize_fit", _fit_limit(), "applymize_fit_limit_reached")
        logger.info("applymize_fit_session_started tenant_id=%s user_id=%s company=%s target_role=%s", ctx.tenant_id, ctx.user.id, payload.company, payload.target_role)
        result = await start_fit_session(db, ctx.tenant_id, ctx.user, payload.company, payload.target_role, payload.focus)
        record_ai_usage(db, ctx.tenant_id, ctx.user.id, "applymize_fit", provider=result.provider, model=result.model)
        db.commit()
        return FitStartResponse(
            session_id=result.session_id,
            company=result.company,
            target_role=result.target_role,
            focus=result.focus,
            profile_summary=result.profile_summary,
            questions=[FitQuestionResponse(**q.__dict__) for q in result.questions],
            provider=result.provider,
            model=result.model,
            fallback_used=result.fallback_used,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        logger.error("applymize_fit_start_failed tenant_id=%s user_id=%s error=%s", ctx.tenant_id, ctx.user.id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Não foi possível iniciar o treino agora.") from exc


@router.post("/evaluate", response_model=FitEvaluateResponse)
async def evaluate_answer(payload: FitEvaluateRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    try:
        assert_daily_limit(db, ctx.tenant_id, ctx.user.id, "applymize_fit", _fit_limit(), "applymize_fit_limit_reached")
        logger.info("applymize_fit_answer_evaluation_started tenant_id=%s user_id=%s answer_chars=%s", ctx.tenant_id, ctx.user.id, len(payload.answer or ""))
        result = await evaluate_fit_answer(db, ctx.tenant_id, ctx.user, payload.company, payload.target_role, payload.focus, payload.question, payload.answer)
        record_ai_usage(db, ctx.tenant_id, ctx.user.id, "applymize_fit", provider=result.provider, model=result.model)
        db.commit()
        logger.info("applymize_fit_answer_evaluated tenant_id=%s user_id=%s score=%s", ctx.tenant_id, ctx.user.id, result.score)
        return FitEvaluateResponse(**result.__dict__)
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        logger.error("applymize_fit_evaluate_failed tenant_id=%s user_id=%s error=%s", ctx.tenant_id, ctx.user.id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Não foi possível avaliar a resposta agora.") from exc
