from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.whatsapp_session_service import WhatsAppSessionService

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


class WhatsAppPhonePayload(BaseModel):
    phone_number: str


class WhatsAppSessionPayload(BaseModel):
    phone_number: str | None = None


class WhatsAppTestPayload(BaseModel):
    target_number: str | None = None


def service(db: Session = Depends(get_db)) -> WhatsAppSessionService:
    return WhatsAppSessionService(db)


@router.get("/session")
def get_session(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    session = svc.get_session(ctx.user.id, ctx.tenant_id)
    return svc.safe_response(session)


@router.post("/session")
def create_session(payload: WhatsAppSessionPayload, ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.create_session(ctx.user.id, ctx.tenant_id, payload.phone_number)


@router.post("/session/connect")
def connect_session(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.connect_or_create(ctx.user.id, ctx.tenant_id)


@router.get("/session/qrcode")
def session_qrcode(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.get_qrcode(ctx.user.id, ctx.tenant_id)


@router.get("/session/status")
def session_status(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.get_status(ctx.user.id, ctx.tenant_id)


@router.post("/session/test")
def session_test(payload: WhatsAppTestPayload | None = None, ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.send_test_message(ctx.user.id, ctx.tenant_id, payload.target_number if payload else None)


@router.post("/session/disconnect")
def session_disconnect(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.disconnect(ctx.user.id, ctx.tenant_id)


@router.delete("/session")
def delete_session(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.delete_session(ctx.user.id, ctx.tenant_id)


# Backward-compatible aliases used by earlier frontend/tests.
@router.get("/status")
def whatsapp_status(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.get_status(ctx.user.id, ctx.tenant_id)


@router.post("/phone")
def whatsapp_save_phone(payload: WhatsAppPhonePayload, ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.save_phone_number(ctx.user.id, ctx.tenant_id, payload.phone_number)


@router.post("/connect")
def whatsapp_connect(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.connect_or_create(ctx.user.id, ctx.tenant_id)


@router.post("/instance")
def whatsapp_instance(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.connect_or_create(ctx.user.id, ctx.tenant_id)


@router.get("/qrcode")
def whatsapp_qrcode(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.get_qrcode(ctx.user.id, ctx.tenant_id)


@router.post("/check")
def whatsapp_check(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.get_status(ctx.user.id, ctx.tenant_id, force_refresh=True)


@router.post("/test")
def whatsapp_test(payload: WhatsAppTestPayload | None = None, ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.send_test_message(ctx.user.id, ctx.tenant_id, payload.target_number if payload else None)


@router.post("/disconnect")
def whatsapp_disconnect(ctx: AuthContext = Depends(get_auth_context), svc: WhatsAppSessionService = Depends(service)):
    return svc.disconnect(ctx.user.id, ctx.tenant_id)
