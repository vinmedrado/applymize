from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.job import Job
from backend.models.automation import AutomationSettings
from backend.schemas.job import IngestResult, JobCreate, JobOut, JobPageOut, JobUpdate
from backend.services.job_ingestion import ingest_jobs
from backend.services.translation_service import clean_text, normalize_job_text
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change
from backend.services.job_role_relevance import RoleRelevance, evaluate_role_relevance, role_search_terms

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _relevance_preferences(db: Session, ctx: AuthContext) -> tuple[list[str], float]:
    setting = (
        db.query(AutomationSettings)
        .filter(AutomationSettings.user_id == ctx.user.id)
        .order_by(AutomationSettings.id.desc())
        .first()
    )
    return (
        role_search_terms(ctx.user.target_role, setting.search_terms if setting else None),
        float(setting.min_role_relevance if setting else 55.0),
    )


def _personalized_jobs(db: Session, ctx: AuthContext, query, include_irrelevant: bool) -> tuple[list[dict], int]:
    terms, threshold = _relevance_preferences(db, ctx)
    rows: list[dict] = []
    hidden = 0
    for job in query.order_by(Job.created_at.desc()).all():
        relevance = evaluate_role_relevance(ctx.user.target_role, job, terms, threshold)
        if job.source == "manual":
            relevance = RoleRelevance(100.0, True, relevance.matched_terms, "vaga adicionada manualmente")
        if not relevance.relevant and not include_irrelevant:
            hidden += 1
            continue
        payload = {column.name: getattr(job, column.name) for column in Job.__table__.columns}
        payload["role_relevance_score"] = relevance.score
        payload["role_relevance_reason"] = relevance.reason
        rows.append(payload)
    rows.sort(key=lambda item: (item["role_relevance_score"], item["created_at"]), reverse=True)
    return rows, hidden


def normalize_job_payload(data: dict, *, translate: bool = True) -> dict:
    title_original = data.get("title_original") or data.get("title") or ""
    description_original = data.get("description_original") or data.get("description") or ""
    if not translate:
        data["title_original"] = clean_text(title_original)
        data["description_original"] = clean_text(description_original)
        data["title"] = clean_text(data.get("title") or title_original)
        data["description"] = clean_text(data.get("description") or description_original)
        return data
    normalized = normalize_job_text(title_original, description_original)
    data["title_original"] = normalized["title_original"]
    data["description_original"] = normalized["description_original"]
    data["title"] = normalized["title"]
    data["description"] = normalized["description"]
    return data


@router.post("/", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    raw_data = payload.model_dump()
    data = normalize_job_payload(raw_data, translate=raw_data.get("source") != "manual")
    job = Job(tenant_id=ctx.tenant_id, **data)
    if not job.external_id:
        job.external_id = f"manual-{ctx.tenant_id}-{payload.company}-{payload.title}"
    db.add(job)
    db.commit()
    db.refresh(job)
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    return job


@router.get("/", response_model=list[JobOut])
def list_jobs(
    response: Response,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    include_irrelevant: bool = Query(False),
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    query = db.query(Job).filter(Job.tenant_id == ctx.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter((Job.title.ilike(like)) | (Job.company.ilike(like)) | (Job.description.ilike(like)))

    items, hidden = _personalized_jobs(db, ctx, query, include_irrelevant)
    total = len(items)
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)

    response.headers["X-Hidden-Irrelevant"] = str(hidden)
    start = (page - 1) * page_size
    return items[start:start + page_size]


@router.get("/paged", response_model=JobPageOut)
def list_jobs_paged(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    include_irrelevant: bool = Query(False),
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    query = db.query(Job).filter(Job.tenant_id == ctx.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter((Job.title.ilike(like)) | (Job.company.ilike(like)) | (Job.description.ilike(like)))

    items, hidden = _personalized_jobs(db, ctx, query, include_irrelevant)
    total = len(items)
    start = (page - 1) * page_size
    return JobPageOut(
        items=items[start:start + page_size],
        total=total,
        page=page,
        page_size=page_size,
        hidden_irrelevant=hidden,
    )


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    data = payload.model_dump(exclude_unset=True)
    if "title" in data or "description" in data or "title_original" in data or "description_original" in data:
        merged = {
            "title": data.get("title", job.title),
            "title_original": data.get("title_original", job.title_original or job.title),
            "description": data.get("description", job.description),
            "description_original": data.get("description_original", job.description_original or job.description),
        }
        normalized = normalize_job_payload(merged, translate=job.source != "manual")
        data["title"] = normalized["title"]
        data["title_original"] = normalized["title_original"]
        data["description"] = normalized["description"]
        data["description_original"] = normalized["description_original"]
    for field, value in data.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == ctx.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    db.delete(job)
    db.commit()
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    return {"deleted": True}


@router.post("/ingest", response_model=IngestResult)
def ingest(
    provider: str = Query("remoteok"),
    source: str | None = Query(None),
    limit: int = Query(300, ge=1, le=500),
    term: str | None = Query(None),
    state: str | None = Query(None),
    city: str | None = Query(None),
    workplace_types: str | None = Query(None),
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    selected_provider = source or provider
    provider_options = {
        "term": term,
        "state": state,
        "city": city,
        "workplace_types": workplace_types,
    }
    provider_options = {key: value for key, value in provider_options.items() if value not in (None, "")}

    try:
        inserted, skipped, jobs, collected_by_provider, errors = ingest_jobs(
            db,
            ctx.tenant_id,
            source=selected_provider,
            limit=limit,
            provider_options=provider_options,
            user=ctx.user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    return IngestResult(
        inserted=inserted,
        skipped=skipped,
        collected_by_provider=collected_by_provider,
        errors=errors,
        jobs=jobs,
    )
