from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.dashboard_realtime import notify_dashboard_change
from backend.services.user_settings_service import complete_onboarding, get_onboarding_status

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/onboarding-status")
def onboarding_status(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return get_onboarding_status(db, ctx.user.id)


@router.post("/onboarding-complete")
def onboarding_complete(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return complete_onboarding(db, ctx.user.id)


@router.delete("/delete-account")
def delete_account(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    user = ctx.user
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user_id = user.id
    tenant_id = ctx.tenant_id
    db.delete(user)
    db.commit()
    notify_dashboard_change(tenant_id, user_id)
    return {"success": True, "message": "Conta excluída com sucesso"}
