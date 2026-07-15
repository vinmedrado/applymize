import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from backend.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_strength(password: str) -> None:
    errors = []
    if len(password or "") < settings.password_min_length:
        errors.append(f"mínimo de {settings.password_min_length} caracteres")
    if not re.search(r"[A-Z]", password or ""):
        errors.append("uma letra maiúscula")
    if not re.search(r"[a-z]", password or ""):
        errors.append("uma letra minúscula")
    if not re.search(r"[0-9]", password or ""):
        errors.append("um número")
    if not re.search(r"[^A-Za-z0-9]", password or ""):
        errors.append("um caractere especial")
    if errors:
        raise HTTPException(status_code=422, detail="Senha fraca: exige " + ", ".join(errors))


def hash_password(password: str) -> str:
    validate_password_strength(password)
    return pwd_context.hash(password)


def hash_password_without_validation(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _create_jwt(subject: str, tenant_id: int, token_type: Literal["access", "refresh"], expires_delta: timedelta) -> str:
    secret = settings.secret_key if token_type == "access" else settings.refresh_secret_key
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "type": token_type,
        "exp": now + expires_delta,
        "iat": now,
        "jti": secrets.token_hex(12),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_access_token(email: str, tenant_id: int) -> str:
    return _create_jwt(email, tenant_id, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(email: str, tenant_id: int) -> str:
    nonce = secrets.token_hex(16)
    return _create_jwt(f"{email}:{nonce}", tenant_id, "refresh", timedelta(days=settings.refresh_token_expire_days))


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.refresh_secret_key, algorithms=["HS256"])


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
