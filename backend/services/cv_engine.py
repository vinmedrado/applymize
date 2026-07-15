from dataclasses import dataclass
from sqlalchemy.orm import Session
from backend.models.job import Job
from backend.models.user import User
from backend.models.resume import Resume
from backend.services.matching_engine import calculate_match
from backend.services.profile_service import profile_context_text, serialize_profile


@dataclass
class CVSections:
    summary: bool = True
    skills: bool = True
    experience: bool = True
    projects: bool = True
    keywords: bool = True
    cover_note: bool = True


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def generate_cv_content(user: User, job: Job, sections: CVSections | None = None, profile_data: dict | None = None, profile_context: str | None = None) -> str:
    sections = sections or CVSections()
    match = calculate_match(user, job, profile_context=profile_context)
    matched = match.matched_skills[:12]
    gaps = match.missing_skills[:8]
    skills = [s.strip() for s in user.skills.replace("\n", ",").split(",") if s.strip()]
    keywords = list(dict.fromkeys(matched + [job.title, job.company, job.seniority, job.employment_type]))

    display_name = (profile_data or {}).get("full_name") or user.full_name
    display_email = (profile_data or {}).get("email") or user.email
    display_title = (profile_data or {}).get("professional_title") or user.target_role or job.title
    parts = [f"# {display_name}", "", f"**E-mail:** {display_email}", f"**Título profissional:** {display_title}", f"**Cargo alvo:** {job.title}", f"**Empresa alvo:** {job.company}", ""]

    if sections.summary:
        parts += [
            "## Resumo Profissional",
            (
                f"Profissional {user.seniority} com foco em {user.target_role or job.title}, "
                f"experiência em {', '.join(matched) if matched else user.skills}. "
                f"Perfil orientado a resultados, automação, dados, APIs, integração entre sistemas e entrega de soluções úteis ao negócio."
            ),
            "",
        ]

    if sections.skills:
        parts += ["## Competências Técnicas", _bullet_list(skills or matched or ["Python", "SQL", "APIs", "Automação"]), ""]

    if sections.experience:
        parts += [
            "## Experiência Profissional",
            "**Projetos e entregas alinhados à vaga**",
            _bullet_list([
                f"Construção de soluções usando {', '.join(matched[:5]) if matched else 'tecnologias aderentes à vaga'}.",
                "Desenvolvimento de automações para reduzir tarefas manuais e aumentar confiabilidade operacional.",
                "Estruturação de dados, validação de qualidade e geração de indicadores para tomada de decisão.",
                "Integração com APIs, bancos de dados e serviços externos com foco em rastreabilidade e manutenção.",
            ]),
            "",
        ]

    if sections.projects:
        parts += [
            "## Projetos Relevantes",
            _bullet_list([
                f"Sistema adaptado para desafios próximos da vaga de {job.title}, com foco em entrega ponta a ponta.",
                "Pipelines de dados com coleta, transformação, persistência e validação.",
                "APIs e serviços backend com autenticação, banco relacional e documentação testável.",
                "Dashboards e relatórios para transformar dados em decisões práticas.",
            ]),
            "",
        ]

    if sections.keywords:
        parts += [
            "## Palavras-chave da Vaga",
            ", ".join([k for k in keywords if k]) or job.requirements or job.title,
            "",
            "## Lacunas para Reforçar",
            _bullet_list(gaps) if gaps else "- Sem lacunas críticas detectadas pelo matching.",
            "",
        ]

    parts += [
        "## Aderência Calculada",
        f"- Score geral: {match.score}%",
        f"- Required skills: {match.required_skill_score}%",
        f"- Desired skills: {match.desired_skill_score}%",
        f"- Senioridade: {match.seniority_score}%",
        f"- Local/remoto: {match.remote_location_score}%",
        "",
    ]

    if sections.cover_note:
        parts += [
            "## Mensagem Curta para Recrutador",
            (
                f"Olá, tenho interesse na vaga de {job.title} na {job.company}. "
                f"Minha experiência em {', '.join(matched[:6]) if matched else user.skills} está alinhada aos requisitos da posição. "
                "Posso contribuir com execução prática, visão analítica e entregas bem documentadas."
            ),
            "",
        ]

    return "\n".join(parts).strip() + "\n"


def create_resume(db: Session, tenant_id: int, user: User, job: Job) -> Resume:
    last = db.query(Resume).filter(
        Resume.tenant_id == tenant_id,
        Resume.user_id == user.id,
        Resume.job_id == job.id,
    ).order_by(Resume.version.desc()).first()
    version = 1 if not last else last.version + 1
    resume = Resume(
        tenant_id=tenant_id,
        user_id=user.id,
        job_id=job.id,
        content_md=generate_cv_content(user, job, profile_data=serialize_profile(db, tenant_id, user.id), profile_context=profile_context_text(db, tenant_id, user)),
        version=version,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume
