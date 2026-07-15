from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.job_radar import radar_history, run_radar
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change

router = APIRouter(prefix="/api/radar", tags=["radar"])


@router.post("/run")
def run(provider: str = Query("remoteok"), limit: int = Query(25), db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    result = run_radar(db, ctx.tenant_id, ctx.user, provider=provider, limit=limit)
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:{ctx.user.id}")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    return result


@router.get("/history")
def history(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return radar_history(db, ctx.tenant_id, ctx.user)
