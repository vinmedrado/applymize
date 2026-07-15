from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.schemas.strategy import StrategyRecommendationOut
from backend.services.strategy_engine import get_strategy_recommendations

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.get("/recommendations", response_model=list[StrategyRecommendationOut])
def recommendations(
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    return get_strategy_recommendations(
        db=db,
        user_id=ctx.user.id,
        tenant_id=ctx.tenant_id,
        limit=limit,
    )
