from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
import jwt

from backend.core.database import get_db
from backend.core.security import decode_access_token
from backend.models.user import User
from backend.models.tenant import Tenant
from backend.models.membership import Membership


@dataclass
class AuthContext:
    user: User
    tenant: Tenant
    membership: Membership
    tenant_id: int


def get_auth_context(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token Bearer ausente")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")

    email = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    membership = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.tenant_id == tenant_id,
        Membership.is_active.is_(True),
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Sem acesso ao tenant")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active.is_(True)).first()
    if not tenant:
        raise HTTPException(status_code=403, detail="Tenant inválido")

    return AuthContext(user=user, tenant=tenant, membership=membership, tenant_id=tenant.id)
