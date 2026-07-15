from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.schemas.notification import NotificationResultOut, NotificationSettingsOut
from backend.services.notification_center import notification_settings, send_high_priority_notifications, send_test_notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/settings", response_model=NotificationSettingsOut)
def settings(ctx: AuthContext = Depends(get_auth_context)):
    return notification_settings()


@router.post("/test", response_model=NotificationResultOut)
def test_notification(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    result = send_test_notification(db, ctx.tenant_id, ctx.user)
    return {"enabled": result.get("enabled", False), "sent": result.get("sent", 0), "skipped": result.get("skipped", 0), "selected": result.get("selected"), "max_per_run": result.get("max_per_run"), "results": result.get("results", [])}


@router.post("/send-high-priority", response_model=NotificationResultOut)
def send_high_priority(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    result = send_high_priority_notifications(db, ctx.tenant_id, ctx.user)
    return {"enabled": result.get("enabled", False), "sent": result.get("sent", 0), "skipped": result.get("skipped", 0), "selected": result.get("selected"), "max_per_run": result.get("max_per_run"), "results": result.get("results", [])}
