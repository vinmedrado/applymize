from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.database import SessionLocal
from backend.core.security import hash_password
from backend.models.application import Application, ApplicationEvent
from backend.models.job import Job
from backend.models.membership import Membership
from backend.models.tenant import Tenant
from backend.models.user import User
from backend.models.profile import UserProfile, UserSkill, UserExperience, UserProject, UserEducation


DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "Demo123!"


def get_or_create_tenant(db):
    tenant = db.query(Tenant).filter(Tenant.slug == "applymize-demo").first()
    if tenant:
        return tenant
    tenant = Tenant(name="Applymize Demo", slug="applymize-demo", plan="free", is_active=True)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def get_or_create_user(db):
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if user:
        return user
    user = User(
        email=DEMO_EMAIL,
        full_name="Usuário Demo",
        password_hash=hash_password(DEMO_PASSWORD),
        skills="Python, SQL, FastAPI, PostgreSQL, Docker, Power BI, APIs, Automação, Machine Learning",
        seniority="mid",
        target_role="Analista de Dados e Automação",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_membership(db, tenant, user):
    membership = db.query(Membership).filter(Membership.tenant_id == tenant.id, Membership.user_id == user.id).first()
    if membership:
        return membership
    membership = Membership(tenant_id=tenant.id, user_id=user.id, role="owner", is_active=True)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def ensure_demo_profile(db, tenant, user):
    profile = db.query(UserProfile).filter(UserProfile.tenant_id == tenant.id, UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(
            tenant_id=tenant.id,
            user_id=user.id,
            full_name=user.full_name,
            professional_title="Analista de Dados & Automação",
            summary="Profissional com experiência em Python, SQL, Power BI, automação, APIs, ETL e desenvolvimento de sistemas reais.",
            location="Santo André, São Paulo",
            work_preferences="remote,hybrid",
            salary_expectation=8000,
            phone="(11) 99999-9999",
            email=user.email,
            resume_text=(
                "Usuário Demo\n"
                "Analista de Dados e Automação\n"
                "Python SQL FastAPI PostgreSQL Docker Power BI APIs ETL Machine Learning GitHub LinkedIn Inglês técnico Certificação Python\n"
                "Experiência com automações, dashboards, sistemas backend e engenharia de dados.\n"
                "Projeto: Applymize, sistema de inteligência de carreira."
            ),
            completeness=85,
        )
        db.add(profile)
        db.commit()

    for skill in ["Python", "SQL", "FastAPI", "PostgreSQL", "Docker", "Power BI", "APIs", "Automação", "ETL"]:
        exists = db.query(UserSkill).filter(
            UserSkill.tenant_id == tenant.id,
            UserSkill.user_id == user.id,
            UserSkill.name == skill,
        ).first()
        if not exists:
            db.add(UserSkill(tenant_id=tenant.id, user_id=user.id, name=skill, level="advanced", category="technical"))

    if not db.query(UserExperience).filter(UserExperience.tenant_id == tenant.id, UserExperience.user_id == user.id).first():
        db.add(UserExperience(
            tenant_id=tenant.id,
            user_id=user.id,
            company="General Motors Brasil / Conduent",
            role="Analista de Dados & Automação",
            description="Criação de automações, relatórios, pipelines e análises para operação.",
            achievements="Redução de trabalho manual, melhoria de rastreabilidade e dashboards executivos.",
        ))

    if not db.query(UserProject).filter(UserProject.tenant_id == tenant.id, UserProject.user_id == user.id).first():
        db.add(UserProject(
            tenant_id=tenant.id,
            user_id=user.id,
            name="Applymize Demo",
            description="Sistema de inteligência de carreira com matching, strategy engine, resume engine e application agent.",
            technologies="Python, FastAPI, PostgreSQL, React, Docker",
        ))

    if not db.query(UserEducation).filter(UserEducation.tenant_id == tenant.id, UserEducation.user_id == user.id).first():
        db.add(UserEducation(
            tenant_id=tenant.id,
            user_id=user.id,
            institution="Cursos e Certificações",
            course="Python, Dados, BI e Automação",
            description="Formação complementar em dados, automação, IA e desenvolvimento.",
        ))

    db.commit()


def upsert_job(db, tenant_id, payload):
    job = db.query(Job).filter(
        Job.tenant_id == tenant_id,
        Job.source == payload["source"],
        Job.external_id == payload["external_id"],
    ).first()
    if job:
        return job
    job = Job(tenant_id=tenant_id, **payload)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def ensure_application(db, tenant_id, user_id, job_id, status, notes, next_action):
    app = db.query(Application).filter(
        Application.tenant_id == tenant_id,
        Application.user_id == user_id,
        Application.job_id == job_id,
    ).first()
    if app:
        return app
    app = Application(
        tenant_id=tenant_id,
        user_id=user_id,
        job_id=job_id,
        status=status,
        notes=notes,
        next_action=next_action,
    )
    db.add(app)
    db.flush()
    db.add(ApplicationEvent(
        tenant_id=tenant_id,
        application_id=app.id,
        from_status="",
        to_status=status,
        note="Candidatura demo criada pelo seed local.",
    ))
    db.commit()
    db.refresh(app)
    return app


def main():
    db = SessionLocal()
    try:
        tenant = get_or_create_tenant(db)
        user = get_or_create_user(db)
        ensure_membership(db, tenant, user)
        ensure_demo_profile(db, tenant, user)

        jobs_payload = [
            {
                "source": "demo",
                "external_id": "demo-data-analyst-001",
                "title": "Analista de Dados Pleno",
                "company": "Data Corp Demo",
                "location": "São Paulo / Remoto",
                "url": "https://www.linkedin.com/jobs/view/applymize-demo-data-analyst",
                "description": "Vaga para profissional com Python, SQL, Power BI, APIs, ETL e automação de processos.",
                "requirements": "Python, SQL, Power BI, ETL, APIs, Docker",
                "seniority": "mid",
                "employment_type": "full_time",
                "salary_min": 6000,
                "salary_max": 9000,
                "remote": True,
            },
            {
                "source": "demo",
                "external_id": "demo-backend-002",
                "title": "Backend Python FastAPI Developer",
                "company": "SaaS Demo",
                "location": "Remoto",
                "url": "https://remoteok.com/remote-jobs/applymize-demo-backend-fastapi",
                "description": "Construção de APIs com FastAPI, PostgreSQL, Docker, JWT, SQLAlchemy e Alembic.",
                "requirements": "Python, FastAPI, PostgreSQL, Docker, JWT, SQLAlchemy, Alembic",
                "seniority": "mid",
                "employment_type": "full_time",
                "salary_min": 8000,
                "salary_max": 12000,
                "remote": True,
            },
        ]

        jobs = [upsert_job(db, tenant.id, payload) for payload in jobs_payload]

        ensure_application(
            db,
            tenant.id,
            user.id,
            jobs[0].id,
            "applied",
            "Candidatura demo para validar tracker.",
            "Gerar CV adaptado e revisar perguntas de entrevista.",
        )

        print("Seed local concluído.")
        print(f"Usuário demo: {DEMO_EMAIL}")
        print(f"Senha demo: {DEMO_PASSWORD}")
        print(f"Tenant: {tenant.name}")
        print(f"Vagas demo: {len(jobs)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
