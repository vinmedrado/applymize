from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.schemas.application_agent import ApplicationQueueItemOut, QueueBuildRequest, QueueBuildResponse
from backend.services.application_agent import (
    approve_item,
    build_queue,
    get_queue,
    get_queue_item,
    mark_applied,
    serialize_queue_item,
    skip_item,
)

router = APIRouter(prefix="/api/application-agent", tags=["application-agent"])


@router.get("/queue", response_model=list[ApplicationQueueItemOut])
def queue(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return [serialize_queue_item(item) for item in get_queue(db, ctx.tenant_id, ctx.user.id)]


@router.post("/build-queue", response_model=QueueBuildResponse)
def build(payload: QueueBuildRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    result = build_queue(
        db=db,
        tenant_id=ctx.tenant_id,
        user=ctx.user,
        limit=payload.limit,
        min_strategy_score=payload.min_strategy_score,
        generate_cv=payload.generate_cv,
        generate_message=payload.generate_message,
    )
    return {
        "created": result["created"],
        "skipped": result["skipped"],
        "blocked_low_priority": result["blocked_low_priority"],
        "daily_limit_remaining": result["daily_limit_remaining"],
        "items": [serialize_queue_item(item) for item in result["items"]],
    }


@router.post("/{queue_id}/approve", response_model=ApplicationQueueItemOut)
def approve(queue_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    item = get_queue_item(db, ctx.tenant_id, ctx.user.id, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item da fila não encontrado")
    return serialize_queue_item(approve_item(db, ctx.tenant_id, ctx.user, item))


@router.post("/{queue_id}/skip", response_model=ApplicationQueueItemOut)
def skip(queue_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    item = get_queue_item(db, ctx.tenant_id, ctx.user.id, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item da fila não encontrado")
    return serialize_queue_item(skip_item(db, ctx.tenant_id, ctx.user, item))


@router.post("/{queue_id}/mark-applied", response_model=ApplicationQueueItemOut)
def applied(queue_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    item = get_queue_item(db, ctx.tenant_id, ctx.user.id, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item da fila não encontrado")
    return serialize_queue_item(mark_applied(db, ctx.tenant_id, ctx.user, item))
