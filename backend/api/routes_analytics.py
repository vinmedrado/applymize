from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.analytics_service import overview

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return overview(db, ctx.tenant_id, ctx.user)
