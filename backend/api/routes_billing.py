from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context

router = APIRouter(prefix="/api/billing", tags=["billing"])
public_router = APIRouter(prefix="/api/public/billing", tags=["public-billing"])

PLANS = [
    {
        "code": "free",
        "name": "Free",
        "monthly_price": 0,
        "annual_price": 0,
        "description": "Validação inicial com limites seguros de IA.",
        "features": ["ATS básico", "LinkedIn demo", "Applymize Fit demo", "Limites diários reduzidos"],
    },
    {
        "code": "pro",
        "name": "Pro",
        "monthly_price": 49,
        "annual_price": 490,
        "description": "Copiloto de carreira com IA, ATS e automação.",
        "features": ["Applymize IA completa", "LinkedIn Analyzer real", "Applymize Fit IA", "WhatsApp", "Histórico IA"],
    },
    {
        "code": "recruiter",
        "name": "Recruiter",
        "monthly_price": 149,
        "annual_price": 1490,
        "description": "Pipeline de candidatos, ranking e inteligência para recrutamento.",
        "features": ["Painel recruiter", "Pipeline Kanban", "Ranking IA", "Analytics RH", "Multiusuários"],
    },
    {
        "code": "enterprise",
        "name": "Enterprise",
        "monthly_price": None,
        "annual_price": None,
        "description": "Operação multiempresa com branding, governança e suporte.",
        "features": ["Multiempresa", "Branding", "SLA", "Admin avançado", "Deploy dedicado"],
    },
]

class CheckoutRequest(BaseModel):
    plan_code: str
    billing_cycle: str = "monthly"

@public_router.get("/plans")
def public_plans():
    return {"plans": PLANS}

@router.get("/plans")
def plans(ctx: AuthContext = Depends(get_auth_context)):
    return {"plans": PLANS, "current_plan": ctx.tenant.plan}

@router.get("/subscription")
def subscription(ctx: AuthContext = Depends(get_auth_context)):
    active_plan = next((plan for plan in PLANS if plan["code"] == ctx.tenant.plan), PLANS[0])
    return {
        "tenant_id": ctx.tenant_id,
        "plan_code": ctx.tenant.plan,
        "plan": active_plan,
        "status": "active" if ctx.tenant.is_active else "inactive",
        "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "stripe_configured": bool(getattr(settings, "stripe_secret_key", "")),
        "mode": "mock_checkout" if not getattr(settings, "stripe_secret_key", "") else "stripe_ready",
    }

@router.post("/checkout")
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    plan = next((item for item in PLANS if item["code"] == payload.plan_code), None)
    if not plan:
        return {"ok": False, "message": "Plano inválido."}
    # MVP seguro: se Stripe ainda não estiver configurado, simula upgrade para demo comercial.
    if not getattr(settings, "stripe_secret_key", ""):
        ctx.tenant.plan = payload.plan_code
        db.add(ctx.tenant)
        db.commit()
        return {
            "ok": True,
            "mode": "mock_checkout",
            "message": f"Plano {plan['name']} ativado em modo demonstrativo.",
            "checkout_url": None,
        }
    return {
        "ok": True,
        "mode": "stripe_checkout_placeholder",
        "message": "Stripe configurado. Conecte Price IDs reais para gerar sessão de checkout.",
        "checkout_url": getattr(settings, "frontend_base_url", "http://localhost:5173") + "/billing",
    }
