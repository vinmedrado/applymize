from __future__ import annotations
from sqlalchemy.orm import Session
from backend.models.job import Job
from backend.models.user import User
from backend.services.profile_service import serialize_profile, profile_context_text
from backend.services.matching_engine import calculate_match


def generate_cover_messages(db: Session, tenant_id: int, user: User, job: Job) -> dict:
    profile = serialize_profile(db, tenant_id, user.id)
    context = profile_context_text(db, tenant_id, user)
    match = calculate_match(user, job, profile_context=context)
    name = profile.get("full_name") or user.full_name
    title = profile.get("professional_title") or user.target_role or job.title
    skills = ", ".join(match.matched_skills[:6]) if match.matched_skills else user.skills

    short = (
        f"Olá! Tenho interesse na vaga de {job.title} na {job.company}. "
        f"Meu perfil como {title} tem aderência com {skills}. Posso contribuir com execução prática e foco em resultado."
    )
    email = (
        f"Assunto: Candidatura para {job.title}\n\n"
        f"Olá, time {job.company}.\n\n"
        f"Sou {name}, {title}. Tenho experiência alinhada aos requisitos da vaga, especialmente em {skills}. "
        f"Gostaria de participar do processo para {job.title}.\n\n"
        f"Obrigado pela atenção,\n{name}"
    )
    linkedin = (
        f"Olá! Vi a vaga de {job.title} na {job.company} e acredito que meu perfil em {skills} pode gerar valor. "
        "Posso te enviar meu currículo adaptado?"
    )
    followup = (
        f"Olá! Passando para reforçar meu interesse na vaga de {job.title}. "
        "Continuo à disposição para conversar sobre como posso contribuir com a posição."
    )
    return {
        "job_id": job.id,
        "short_message": short,
        "application_email": email,
        "linkedin_message": linkedin,
        "followup_message": followup,
        "match_score": match.score,
        "matched_skills": match.matched_skills,
        "warnings": [] if profile.get("completeness", 0) >= 45 else ["Perfil incompleto; complete Meu Perfil para mensagens melhores."],
    }
