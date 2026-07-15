from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
import jwt

from backend.core.database import SessionLocal, get_db
from backend.core.logging import get_logger
from backend.core.security import decode_access_token
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.membership import Membership
from backend.models.tenant import Tenant
from backend.models.user import User
from backend.services.dashboard_service import dashboard_summary
from backend.services.dashboard_realtime import current_dashboard_version, wait_for_dashboard_change

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = get_logger(__name__)


@router.get("/summary")
def summary(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return dashboard_summary(db, ctx.tenant_id, ctx.user)


def _auth_from_token(db: Session, token: str) -> tuple[User, int] | None:
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    email = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        return None
    membership = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.tenant_id == tenant_id,
        Membership.is_active.is_(True),
    ).first()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active.is_(True)).first()
    if not membership or not tenant:
        return None
    return user, int(tenant_id)


@router.websocket("/realtime")
async def dashboard_realtime(websocket: WebSocket):
    await websocket.accept()
    try:
        auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10)
    except (asyncio.TimeoutError, WebSocketDisconnect, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = auth_message.get("token", "") if isinstance(auth_message, dict) else ""
    db = SessionLocal()
    auth = _auth_from_token(db, token)
    if not auth:
        db.close()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user, tenant_id = auth
    version = current_dashboard_version(tenant_id, user.id)
    try:
        payload = dashboard_summary(db, tenant_id, user, use_cache=False)
        payload["realtime"] = True
        payload["push_version"] = version
        await websocket.send_json(payload)

        while True:
            change_task = asyncio.create_task(wait_for_dashboard_change(tenant_id, user.id, version, timeout=30))
            receive_task = asyncio.create_task(websocket.receive())
            done, pending = await asyncio.wait(
                {change_task, receive_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

            if receive_task in done:
                message = receive_task.result()
                if message.get("type") == "websocket.disconnect":
                    return
            if change_task not in done:
                continue

            version = change_task.result()
            db.rollback()
            db.expire_all()
            auth = _auth_from_token(db, token)
            if not auth:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            user, tenant_id = auth
            payload = dashboard_summary(db, tenant_id, user, use_cache=False)
            payload["realtime"] = True
            payload["push_version"] = version
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        return
    except Exception:
        db.rollback()
        logger.exception("dashboard_realtime_failed tenant_id=%s user_id=%s", tenant_id, user.id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except RuntimeError:
            pass
    finally:
        db.close()
