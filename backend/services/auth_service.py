from datetime import datetime, timedelta
import secrets
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
import jwt

from backend.core.config import settings
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    token_hash,
    verify_password,
)
from backend.models.tenant import Tenant
from backend.models.user import User
from backend.models.membership import Membership
from backend.models.token import RefreshToken
from backend.models.password_reset_token import PasswordResetToken
from backend.models.profile import UserProfile
from backend.services.email_service import send_password_reset_email
from backend.services.tenant_service import unique_slug


def register_user(db: Session, tenant_name: str, full_name: str, email: str, password: str, skills: str, seniority: str, target_role: str, location_preferences: dict | None = None):
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    tenant = Tenant(name=tenant_name, slug=unique_slug(db, tenant_name), plan="free")
    user = User(
        email=email.lower(),
        full_name=full_name,
        password_hash=hash_password(password),
        skills=skills,
        seniority=seniority,
        target_role=target_role,
    )
    db.add(tenant)
    db.add(user)
    db.flush()

    membership = Membership(tenant_id=tenant.id, user_id=user.id, role="owner")
    db.add(membership)

    prefs = location_preferences or {}
    profile = UserProfile(
        tenant_id=tenant.id,
        user_id=user.id,
        full_name=full_name,
        professional_title=target_role,
        email=email.lower(),
        work_preferences="remote,hybrid",
        job_country=prefs.get("job_country") or "Brasil",
        job_state=prefs.get("job_state") or "São Paulo",
        job_state_code=prefs.get("job_state_code") or "SP",
        job_cities=json.dumps(prefs.get("job_cities") or [], ensure_ascii=False),
        job_all_cities=bool(prefs.get("job_all_cities") or False),
        job_remote_preference=prefs.get("job_remote_preference") or "any",
        job_city_code=prefs.get("job_city_code") or "5211323",
        education_level=prefs.get("education_level") or "Superior completo",
        english_level=prefs.get("english_level") or "Intermediário",
        spanish_level=prefs.get("spanish_level") or "Nenhum",
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(tenant)
    return user, tenant, membership


def issue_token_pair(db: Session, user: User, tenant_id: int):
    access = create_access_token(user.email, tenant_id)
    refresh = create_refresh_token(user.email, tenant_id)
    stored = RefreshToken(
        tenant_id=tenant_id,
        user_id=user.id,
        token_hash=token_hash(refresh),
        expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(stored)
    db.commit()
    return access, refresh


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower(), User.is_active.is_(True)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    membership = db.query(Membership).filter(Membership.user_id == user.id, Membership.is_active.is_(True)).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Usuário sem tenant")

    return issue_token_pair(db, user, membership.tenant_id)


def refresh_tokens(db: Session, refresh_token: str):
    try:
        payload = decode_refresh_token(refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Refresh token inválido") from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")

    email_nonce = payload.get("sub", "")
    email = email_nonce.split(":", 1)[0]
    tenant_id = payload.get("tenant_id")

    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    stored = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash(refresh_token),
        RefreshToken.tenant_id == tenant_id,
        RefreshToken.user_id == user.id,
        RefreshToken.revoked_at.is_(None),
    ).first()

    if not stored or stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expirado ou revogado")

    stored.revoked_at = datetime.utcnow()
    db.commit()
    return issue_token_pair(db, user, tenant_id)


def logout_user(db: Session, refresh_token: str) -> None:
    hashed = token_hash(refresh_token)
    stored = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed, RefreshToken.revoked_at.is_(None)).first()
    if stored:
        stored.revoked_at = datetime.utcnow()
        db.commit()


def _password_reset_hash(token: str) -> str:
    return token_hash(token)


def request_password_reset(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.lower(), User.is_active.is_(True)).first()
    # Segurança: não revela se o e-mail existe.
    if not user:
        return

    token = secrets.token_urlsafe(40)
    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=_password_reset_hash(token),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.password_reset_token_minutes),
    )
    db.add(reset)
    db.commit()

    reset_link = f"{settings.frontend_base_url.rstrip('/')}/reset-password?token={token}"
    send_password_reset_email(user.email, reset_link)


def reset_password(db: Session, token: str, new_password: str) -> None:
    if len(new_password or "") < settings.password_min_length:
        raise HTTPException(status_code=400, detail=f"Senha deve ter pelo menos {settings.password_min_length} caracteres")

    stored = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == _password_reset_hash(token),
        PasswordResetToken.used_at.is_(None),
    ).first()

    if not stored or stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(User).filter(User.id == stored.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário inválido")

    user.password_hash = hash_password(new_password)
    stored.used_at = datetime.utcnow()

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked_at.is_(None),
    ).update({"revoked_at": datetime.utcnow()})

    db.commit()
