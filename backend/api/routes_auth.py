from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.schemas.auth import ForgotPasswordRequest, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, ResetPasswordRequest, TokenPair, UserMe
from backend.services.auth_service import issue_token_pair, login_user, logout_user, refresh_tokens, register_user, request_password_reset, reset_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user, tenant, membership = register_user(
        db=db,
        tenant_name=payload.tenant_name,
        full_name=payload.full_name,
        email=str(payload.email),
        password=payload.password,
        skills=payload.skills,
        seniority=payload.seniority,
        target_role=payload.target_role,
        location_preferences={
            "job_country": payload.job_country,
            "job_state": payload.job_state,
            "job_state_code": payload.job_state_code,
            "job_cities": payload.job_cities,
            "job_all_cities": payload.job_all_cities,
            "job_remote_preference": payload.job_remote_preference,
            "job_city_code": payload.job_city_code,
            "education_level": payload.education_level,
            "english_level": payload.english_level,
            "spanish_level": payload.spanish_level,
        },
    )
    access, refresh = issue_token_pair(db, user, tenant.id)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    access, refresh = login_user(db, str(payload.email), payload.password)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access, refresh = refresh_tokens(db, payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    logout_user(db, payload.refresh_token)
    return {"logged_out": True}


@router.get("/me", response_model=UserMe)
def me(ctx: AuthContext = Depends(get_auth_context)):
    return UserMe(
        id=ctx.user.id,
        email=ctx.user.email,
        full_name=ctx.user.full_name,
        tenant_id=ctx.tenant.id,
        tenant_name=ctx.tenant.name,
        role=ctx.membership.role,
        skills=ctx.user.skills,
        seniority=ctx.user.seniority,
        target_role=ctx.user.target_role,
    )


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    request_password_reset(db, str(payload.email))
    return {"message": "Se o e-mail estiver cadastrado, enviaremos um link para redefinir sua senha."}


@router.post("/reset-password")
def reset_password_route(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_password(db, payload.token, payload.new_password)
    return {"message": "Senha redefinida com sucesso."}
