from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.followup_service import generate_followup, list_followups

router = APIRouter(prefix="/api/followups", tags=["followups"])


@router.get("/")
def list_all(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return list_followups(db, ctx.tenant_id, ctx.user)


@router.get("/{application_id}")
def one(application_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return generate_followup(db, ctx.tenant_id, ctx.user, application_id)
