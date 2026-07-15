from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.services.ai_usage_limit_service import assert_daily_limit, record_ai_usage
from backend.services.linkedin_profile_analyzer import analyze_linkedin_profile
logger = get_logger(__name__)
router = APIRouter(prefix="/api/linkedin-analyzer", tags=["linkedin-analyzer"])
public_router = APIRouter(prefix="/api/public/linkedin-analyzer", tags=["public-linkedin-analyzer"])
class LinkedInAnalyzeRequest(BaseModel):
    linkedin_url: str | None = Field(default=None, max_length=500)
    profile_text: str = Field(..., min_length=80, max_length=12000)
    target_role: str | None = Field(default="Analista de Dados", max_length=120)
class LinkedInAnalyzeResponse(BaseModel):
    score: int
    categories: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    ats_keywords: list[str]
    suggested_headline: str
    suggested_about: str
    recruiter_feedback: str
    ats_feedback: str
    improvement_actions: list[str]
def _demo_response(target_role: str | None = None) -> LinkedInAnalyzeResponse:
    role = (target_role or "Analista de Dados").strip() or "Analista de Dados"
    return LinkedInAnalyzeResponse(score=78, categories={"headline":76,"sobre":74,"experiencias":82,"palavras_chave":79,"clareza_para_recrutador":80}, strengths=["Boa combinação entre experiência prática, dados e automação.","Perfil demonstra capacidade de transformar processos manuais em soluções mais eficientes.","As palavras-chave técnicas aparecem de forma coerente para uma vaga de dados."], weaknesses=["O resumo pode destacar resultados mensuráveis com mais força.","Projetos técnicos podem ser explicados com linguagem mais clara para RH.","Vale reforçar ferramentas principais logo no início do perfil."], ats_keywords=["SQL","Power BI","Python","ETL","Automação","Dashboards","Análise de Dados", role], suggested_headline=f"{role} | SQL, Power BI, Python e Automação de Processos", suggested_about="Profissional de dados com experiência em análise, automação e construção de soluções que tornam processos mais rápidos, confiáveis e orientados por indicadores. Atua com SQL, Power BI, Python e ETL para transformar informações em decisões mais claras para o negócio.", recruiter_feedback="Demonstra bom potencial para posições de dados, principalmente quando conecta tecnologia com impacto operacional.", ats_feedback="O perfil ficaria mais forte incluindo resultados, ferramentas e palavras-chave do cargo alvo em pontos estratégicos.", improvement_actions=["Adicionar resultados com números no resumo e nas experiências.","Organizar skills por prioridade: SQL, Power BI, Python, ETL e automação.","Explicar projetos técnicos com foco no problema, solução e impacto."])
@router.post("/analyze", response_model=LinkedInAnalyzeResponse)
def analyze_linkedin(payload: LinkedInAnalyzeRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    try:
        assert_daily_limit(db, ctx.tenant_id, ctx.user.id, "linkedin_analyzer", settings.linkedin_analyzer_daily_limit, "linkedin_analyzer_limit_reached")
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    logger.info("linkedin_analyzer_real_used tenant_id=%s user_id=%s url_present=%s text_chars=%s", ctx.tenant_id, ctx.user.id, bool(payload.linkedin_url), len(payload.profile_text or ""))
    try:
        result = analyze_linkedin_profile(payload.profile_text, payload.linkedin_url, payload.target_role)
        record_ai_usage(db, ctx.tenant_id, ctx.user.id, "linkedin_analyzer", provider="internal", model="linkedin_profile_analyzer")
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("linkedin_analysis_failed tenant_id=%s user_id=%s error=%s", ctx.tenant_id, ctx.user.id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Não foi possível analisar o perfil agora.") from exc
    logger.info("linkedin_analysis_finished tenant_id=%s user_id=%s score=%s", ctx.tenant_id, ctx.user.id, result.score)
    return LinkedInAnalyzeResponse(**result.__dict__)
@public_router.post("/demo", response_model=LinkedInAnalyzeResponse)
def linkedin_demo(payload: LinkedInAnalyzeRequest):
    logger.info("public_linkedin_demo_used target_role=%s text_chars=%s", payload.target_role, len(payload.profile_text or ""))
    return _demo_response(payload.target_role)
