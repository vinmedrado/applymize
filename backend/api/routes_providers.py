from fastapi import APIRouter, Depends

from backend.middlewares.auth import AuthContext, get_auth_context
from backend.schemas.provider import ProviderHealthOut, ProviderOut
from backend.services.provider_registry import providers_health, providers_summary

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=list[ProviderOut])
def list_providers(ctx: AuthContext = Depends(get_auth_context)):
    return providers_summary()


@router.get("/health", response_model=list[ProviderHealthOut])
def healthcheck_providers(ctx: AuthContext = Depends(get_auth_context)):
    return providers_health()
