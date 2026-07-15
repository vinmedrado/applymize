from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.skill_gap_service import skill_gap_roadmap

router = APIRouter(prefix="/api/skill-gap", tags=["skill-gap"])


@router.get("/roadmap")
def roadmap(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return skill_gap_roadmap(db, ctx.tenant_id, ctx.user)
