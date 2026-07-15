from __future__ import annotations

from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.application import Application
from backend.models.job import Job
from backend.models.membership import Membership
from backend.models.user import User
from backend.models.ai_usage import AIUsageEvent

router = APIRouter(prefix="/api/admin", tags=["admin"])


def ensure_owner(ctx: AuthContext):
    if ctx.membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Acesso restrito ao owner/admin do tenant")


@router.get("/overview")
def overview(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    ensure_owner(ctx)
    member_ids = [row.user_id for row in db.query(Membership.user_id).filter(Membership.tenant_id == ctx.tenant_id).all()]
    users_count = db.query(User).filter(User.id.in_(member_ids), User.is_active.is_(True)).count() if member_ids else 0
    jobs_count = db.query(Job).filter(Job.tenant_id == ctx.tenant_id).count()
    applications_count = db.query(Application).filter(Application.tenant_id == ctx.tenant_id).count()
    ai_count = db.query(AIUsageEvent).filter(AIUsageEvent.tenant_id == ctx.tenant_id).count()
    statuses = Counter(row.status for row in db.query(Application.status).filter(Application.tenant_id == ctx.tenant_id).all())
    features = Counter(row.feature for row in db.query(AIUsageEvent.feature).filter(AIUsageEvent.tenant_id == ctx.tenant_id).all())
    return {
        "tenant": {"id": ctx.tenant.id, "name": ctx.tenant.name, "plan": ctx.tenant.plan},
        "metrics": {
            "users": users_count,
            "jobs": jobs_count,
            "applications": applications_count,
            "ai_events": ai_count,
            "estimated_ai_cost_brl": round(ai_count * 0.015, 2),
        },
        "application_status": dict(statuses),
        "ai_features": dict(features),
        "retention_signal": "demo_ready" if jobs_count or applications_count or ai_count else "new_workspace",
    }
