from __future__ import annotations

import json
from sqlalchemy.orm import Session

from backend.models.profile import ResumeUpload, UserEducation, UserExperience, UserProfile, UserProject, UserSkill
from backend.models.user import User
from backend.services.resume_parser import dumps, extract_resume_text, parse_resume_text


def get_or_create_profile(db: Session, tenant_id: int, user: User) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user.id).first()
    if profile:
        return profile
    profile = UserProfile(
        tenant_id=tenant_id,
        user_id=user.id,
        full_name=user.full_name,
        professional_title=user.target_role,
        email=user.email,
        work_preferences="remote,hybrid",
        job_country="Brasil",
        job_state="São Paulo",
        job_state_code="SP",
        job_cities="[]",
        job_all_cities=False,
        job_remote_preference="any",
        job_city_code="5211323",
        education_level="Superior completo",
        english_level="Intermediário",
        spanish_level="Nenhum",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    refresh_completeness(db, tenant_id, user.id)
    return profile


def refresh_completeness(db: Session, tenant_id: int, user_id: int) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user_id).first()
    if not profile:
        raise ValueError("Perfil não encontrado")
    checks = [
        profile.full_name, profile.professional_title, profile.summary, profile.location,
        profile.work_preferences, profile.email, profile.phone, profile.resume_text,
        profile.education_level, profile.english_level, profile.spanish_level,
        db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user_id).first(),
        db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user_id).first(),
        db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user_id).first(),
        db.query(UserEducation).filter(UserEducation.tenant_id == tenant_id, UserEducation.user_id == user_id).first(),
    ]
    profile.completeness = round(sum(1 for item in checks if item) / len(checks) * 100, 2)
    db.commit()
    db.refresh(profile)
    return profile


def serialize_profile(db: Session, tenant_id: int, user_id: int) -> dict:
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user_id).first()
    if not profile:
        return {"id": None, "tenant_id": tenant_id, "user_id": user_id, "full_name": "", "professional_title": "", "summary": "", "location": "", "work_preferences": "", "job_country": "Brasil", "job_state": "São Paulo", "job_state_code": "SP", "job_cities": [], "job_all_cities": False, "job_remote_preference": "any", "job_city_code": "5211323", "education_level": "Superior completo", "english_level": "Intermediário", "spanish_level": "Nenhum", "salary_expectation": 0, "phone": "", "email": "", "resume_text": "", "completeness": 0, "skills": [], "experiences": [], "projects": [], "education": []}
    refresh_completeness(db, tenant_id, user_id)
    return {
        "id": profile.id, "tenant_id": tenant_id, "user_id": user_id,
        "full_name": profile.full_name, "professional_title": profile.professional_title,
        "summary": profile.summary, "location": profile.location, "work_preferences": profile.work_preferences,
        "job_country": profile.job_country or "Brasil", "job_state": profile.job_state or "São Paulo", "job_state_code": profile.job_state_code or "SP",
        "job_cities": json.loads(profile.job_cities or "[]"), "job_all_cities": bool(profile.job_all_cities),
        "job_remote_preference": profile.job_remote_preference or "any", "job_city_code": profile.job_city_code or "5211323",
        "education_level": profile.education_level or "Superior completo", "english_level": profile.english_level or "Intermediário", "spanish_level": profile.spanish_level or "Nenhum",
        "salary_expectation": profile.salary_expectation, "phone": profile.phone, "email": profile.email,
        "resume_text": profile.resume_text, "completeness": profile.completeness,
        "skills": db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user_id).all(),
        "experiences": db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user_id).all(),
        "projects": db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user_id).all(),
        "education": db.query(UserEducation).filter(UserEducation.tenant_id == tenant_id, UserEducation.user_id == user_id).all(),
    }


def profile_skill_text(db: Session, tenant_id: int, user: User) -> str:
    skills = db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user.id).all()
    if skills:
        return ", ".join(skill.name for skill in skills)
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user.id).first()
    if profile and profile.resume_text:
        parsed_skills = parse_resume_text(profile.resume_text).get("skills") or []
        if parsed_skills:
            return ", ".join(parsed_skills)
    return user.skills


def profile_context_text(db: Session, tenant_id: int, user: User) -> str:
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant_id, UserProfile.user_id == user.id).first()
    if not profile:
        return user.skills
    parts = [profile.full_name, profile.professional_title, profile.summary, profile.location, profile.work_preferences, profile.education_level, profile.english_level, profile.spanish_level, profile.resume_text[:2000], profile_skill_text(db, tenant_id, user)]
    parts += [f"{e.role} {e.company} {e.description} {e.achievements}" for e in db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user.id).all()]
    parts += [f"{p.name} {p.description} {p.technologies}" for p in db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user.id).all()]
    return "\n".join(part for part in parts if part)


def apply_parsed_resume_to_profile(db: Session, tenant_id: int, user: User, extracted_text: str, parsed: dict) -> UserProfile:
    profile = get_or_create_profile(db, tenant_id, user)
    profile.resume_text = extracted_text
    if parsed.get("probable_name"):
        profile.full_name = parsed["probable_name"]
    profile.email = profile.email or parsed.get("email", "") or user.email
    profile.phone = profile.phone or parsed.get("phone", "")
    profile.summary = profile.summary or extracted_text[:900]

    links = []
    if parsed.get("linkedin"):
        links.append(f"LinkedIn: {parsed['linkedin']}")
    if parsed.get("github"):
        links.append(f"GitHub: {parsed['github']}")
    if links and "LinkedIn:" not in profile.summary and "GitHub:" not in profile.summary:
        profile.summary = (profile.summary + "\n" + "\n".join(links)).strip()

    for skill in parsed.get("skills", []):
        if not db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user.id, UserSkill.name == skill).first():
            db.add(UserSkill(tenant_id=tenant_id, user_id=user.id, name=skill, level="inferred", category="resume"))

    for item in parsed.get("experiences", [])[:3]:
        if item and not db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user.id, UserExperience.description == item).first():
            db.add(UserExperience(tenant_id=tenant_id, user_id=user.id, company="Extraído do currículo", role="Experiência profissional", description=item, achievements=""))

    for item in parsed.get("projects", [])[:3]:
        if item and not db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user.id, UserProject.description == item).first():
            db.add(UserProject(tenant_id=tenant_id, user_id=user.id, name="Projeto extraído", description=item, technologies=""))

    for item in parsed.get("education", [])[:3]:
        if item and not db.query(UserEducation).filter(UserEducation.tenant_id == tenant_id, UserEducation.user_id == user.id, UserEducation.description == item).first():
            db.add(UserEducation(tenant_id=tenant_id, user_id=user.id, institution="Extraído do currículo", course="Formação/Curso", description=item))

    db.commit()
    return refresh_completeness(db, tenant_id, user.id)


def save_resume_upload(db: Session, tenant_id: int, user: User, filename: str, content_type: str, content: bytes) -> ResumeUpload:
    extracted_text = extract_resume_text(filename, content_type, content)
    parsed = parse_resume_text(extracted_text)
    upload = ResumeUpload(tenant_id=tenant_id, user_id=user.id, filename=filename, content_type=content_type, extracted_text=extracted_text, parsed_data=dumps(parsed))
    db.add(upload)
    db.flush()
    apply_parsed_resume_to_profile(db, tenant_id, user, extracted_text, parsed)
    db.commit()
    db.refresh(upload)
    return upload
