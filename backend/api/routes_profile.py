import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.middlewares.auth import AuthContext, get_auth_context
from backend.models.profile import UserEducation, UserExperience, UserProject, UserSkill
from backend.schemas.profile import EducationCreate, ExperienceCreate, ParseResumeResponse, ProjectCreate, ResumeUploadOut, SkillCreate, UserProfileOut, UserProfileUpdate
from backend.services.profile_service import apply_parsed_resume_to_profile, get_or_create_profile, refresh_completeness, save_resume_upload, serialize_profile
from backend.services.resume_parser import parse_resume_text
from backend.services.resume_template_service import build_modern_resume_html
from backend.services.dashboard_cache import invalidate_cache
from backend.services.dashboard_realtime import notify_dashboard_change

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileOut)
def get_profile(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.put("/me", response_model=UserProfileOut)
def update_profile(payload: UserProfileUpdate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    profile = get_or_create_profile(db, ctx.tenant_id, ctx.user)
    data = payload.model_dump()
    if "job_cities" in data:
        data["job_cities"] = json.dumps(data.get("job_cities") or [], ensure_ascii=False)
    for field, value in data.items():
        setattr(profile, field, value)
    if payload.professional_title is not None:
        ctx.user.target_role = payload.professional_title.strip()
    db.commit()
    invalidate_cache(f"dashboard:summary:{ctx.tenant_id}:{ctx.user.id}")
    notify_dashboard_change(ctx.tenant_id, ctx.user.id)
    refresh_completeness(db, ctx.tenant_id, ctx.user.id)
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.post("/skills", response_model=UserProfileOut)
def add_skill(payload: SkillCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    get_or_create_profile(db, ctx.tenant_id, ctx.user)
    if not db.query(UserSkill).filter(UserSkill.tenant_id == ctx.tenant_id, UserSkill.user_id == ctx.user.id, UserSkill.name == payload.name).first():
        db.add(UserSkill(tenant_id=ctx.tenant_id, user_id=ctx.user.id, **payload.model_dump()))
        db.commit()
    refresh_completeness(db, ctx.tenant_id, ctx.user.id)
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.post("/experiences", response_model=UserProfileOut)
def add_experience(payload: ExperienceCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    get_or_create_profile(db, ctx.tenant_id, ctx.user)
    db.add(UserExperience(tenant_id=ctx.tenant_id, user_id=ctx.user.id, **payload.model_dump()))
    db.commit()
    refresh_completeness(db, ctx.tenant_id, ctx.user.id)
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.post("/projects", response_model=UserProfileOut)
def add_project(payload: ProjectCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    get_or_create_profile(db, ctx.tenant_id, ctx.user)
    db.add(UserProject(tenant_id=ctx.tenant_id, user_id=ctx.user.id, **payload.model_dump()))
    db.commit()
    refresh_completeness(db, ctx.tenant_id, ctx.user.id)
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.post("/education", response_model=UserProfileOut)
def add_education(payload: EducationCreate, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    get_or_create_profile(db, ctx.tenant_id, ctx.user)
    db.add(UserEducation(tenant_id=ctx.tenant_id, user_id=ctx.user.id, **payload.model_dump()))
    db.commit()
    refresh_completeness(db, ctx.tenant_id, ctx.user.id)
    return serialize_profile(db, ctx.tenant_id, ctx.user.id)


@router.post("/upload-resume", response_model=ResumeUploadOut)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    content = await file.read()
    try:
        upload = save_resume_upload(db, ctx.tenant_id, ctx.user, file.filename or "resume.txt", file.content_type or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResumeUploadOut(id=upload.id, filename=upload.filename, content_type=upload.content_type, extracted_text=upload.extracted_text, parsed_data=json.loads(upload.parsed_data or "{}"), created_at=upload.created_at)


@router.get("/resume-modern", response_class=HTMLResponse)
def modern_resume_html(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    html = build_modern_resume_html(db, ctx.tenant_id, ctx.user)
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


@router.post("/parse-resume", response_model=ParseResumeResponse)
def parse_resume(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    profile = get_or_create_profile(db, ctx.tenant_id, ctx.user)
    parsed = parse_resume_text(profile.resume_text)
    apply_parsed_resume_to_profile(db, ctx.tenant_id, ctx.user, profile.resume_text, parsed)
    return {"upload_id": None, "extracted_text": profile.resume_text, "parsed_data": parsed, "profile": serialize_profile(db, ctx.tenant_id, ctx.user.id)}
