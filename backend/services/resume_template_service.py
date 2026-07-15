from __future__ import annotations

from html import escape
from textwrap import shorten
from sqlalchemy.orm import Session

from backend.models.profile import UserEducation, UserExperience, UserProfile, UserProject, UserSkill
from backend.models.user import User
from backend.services.profile_service import get_or_create_profile


def _clean(value: object, fallback: str = "") -> str:
    text = str(value or "").replace("\x00", "").strip()
    return escape(text if text else fallback)


def _plain(value: object, fallback: str = "") -> str:
    text = str(value or "").replace("\x00", "").strip()
    return text if text else fallback


def _split_items(value: str, max_items: int = 5) -> list[str]:
    raw = _plain(value)
    if not raw:
        return []
    parts: list[str] = []
    for chunk in raw.replace("•", "\n").replace(";", "\n").splitlines():
        clean = chunk.strip(" -•\t")
        if clean and clean not in parts:
            parts.append(clean)
    if len(parts) == 1 and len(parts[0]) > 220:
        sentences = [item.strip() for item in parts[0].replace(". ", ".\n").splitlines() if item.strip()]
        parts = sentences or parts
    return parts[:max_items]


def _format_date_range(start: str = "", end: str = "") -> str:
    start = _plain(start)
    end = _plain(end)
    if start and end:
        return f"{start} – {end}"
    if start:
        return f"{start} – Atual"
    if end:
        return end
    return ""


def _skill_grid(skills: list[UserSkill], resume_text: str) -> str:
    values = [_plain(skill.name) for skill in skills if _plain(skill.name)]
    if not values and resume_text:
        # Fallback leve para currículos importados com pouco parse estruturado.
        known = [
            "Python", "SQL", "Power BI", "Excel", "Pandas", "NumPy", "Scikit-learn", "FastAPI",
            "Docker", "PostgreSQL", "SQLite", "Selenium", "BeautifulSoup", "Machine Learning",
            "ETL", "APIs", "Git", "Airflow", "Streamlit", "React", "VBA", "DAX"
        ]
        lower = resume_text.lower()
        values = [item for item in known if item.lower() in lower]
    values = values[:42]
    groups = [
        ("Dados & BI", ["Python", "SQL", "Power BI", "DAX", "Power Query", "Excel", "Pandas", "NumPy"]),
        ("Backend & APIs", ["FastAPI", "Flask", "REST", "GraphQL", "SQLAlchemy", "PostgreSQL", "SQLite"]),
        ("ML & Automação", ["Machine Learning", "Scikit-learn", "XGBoost", "LightGBM", "Selenium", "BeautifulSoup", "ETL"]),
        ("DevOps & Web", ["Docker", "Git", "Airflow", "Streamlit", "React", "Linux"]),
    ]
    used: set[str] = set()
    rows: list[str] = []
    for label, keys in groups:
        matched = [skill for skill in values if any(key.lower() in skill.lower() for key in keys)]
        for skill in matched:
            used.add(skill)
        if matched:
            rows.append(
                f'<div class="skill-row"><span class="skill-label">{escape(label)}</span>'
                f'<span class="skill-value">{" · ".join(escape(item) for item in matched[:10])}</span></div>'
            )
    remaining = [skill for skill in values if skill not in used]
    if remaining:
        rows.append(
            f'<div class="skill-row"><span class="skill-label">Outras</span>'
            f'<span class="skill-value">{" · ".join(escape(item) for item in remaining[:12])}</span></div>'
        )
    if not rows:
        rows.append('<div class="skill-row"><span class="skill-label">Competências</span><span class="skill-value">Adicione skills no perfil para enriquecer esta seção.</span></div>')
    return "\n".join(rows)


def _experience_html(experiences: list[UserExperience]) -> str:
    if not experiences:
        return """
        <div class="entry">
          <div class="entry-head"><span class="entry-title">Experiência profissional</span><span class="entry-date">Atualize seu perfil</span></div>
          <div class="entry-company">Dados extraídos do currículo importado</div>
          <ul><li>Adicione experiências estruturadas para gerar uma versão mais forte e personalizada.</li></ul>
        </div>
        """
    blocks: list[str] = []
    for exp in experiences[:6]:
        items = _split_items(exp.achievements or exp.description, 6)
        if not items and exp.description:
            items = [_plain(exp.description)]
        bullets = "".join(f"<li>{_clean(item)}</li>" for item in items[:6]) or "<li>Responsabilidades e resultados descritos no currículo importado.</li>"
        date = _format_date_range(exp.start_date, exp.end_date)
        blocks.append(f"""
        <div class="entry">
          <div class="entry-head"><span class="entry-title">{_clean(exp.role, 'Cargo')}</span><span class="entry-date">{_clean(date)}</span></div>
          <div class="entry-company">{_clean(exp.company, 'Empresa')}</div>
          <ul>{bullets}</ul>
        </div>
        """)
    return '<hr class="entry-divider">'.join(blocks)


def _projects_html(projects: list[UserProject]) -> str:
    if not projects:
        return """
        <div class="project">
          <div class="project-head"><span class="project-name">Projetos</span><span class="entry-date">Portfólio</span></div>
          <div class="project-stack">Adicione projetos no perfil para destacar entregas técnicas.</div>
        </div>
        """
    blocks: list[str] = []
    for project in projects[:5]:
        items = _split_items(project.description, 4)
        bullets = "".join(f"<li>{_clean(item)}</li>" for item in items) or "<li>Projeto técnico descrito no perfil profissional.</li>"
        url = _clean(project.url)
        blocks.append(f"""
        <div class="project">
          <div class="project-head"><span class="project-name">{_clean(project.name, 'Projeto')}</span><span class="entry-date">{url}</span></div>
          <div class="project-stack">{_clean(project.technologies, 'Tecnologias não informadas')}</div>
          <ul>{bullets}</ul>
        </div>
        """)
    return '<hr class="entry-divider">'.join(blocks)


def _education_html(items: list[UserEducation]) -> str:
    if not items:
        return """
        <div class="educ-row"><span class="educ-inst">Formação</span><span class="educ-date">Atualize seu perfil</span></div>
        <div class="educ-sub">Adicione sua formação para completar o currículo.</div>
        """
    blocks: list[str] = []
    for item in items[:4]:
        date = _format_date_range(item.start_date, item.end_date)
        blocks.append(f"""
        <div class="educ-row"><span class="educ-inst">{_clean(item.institution, 'Instituição')}</span><span class="educ-date">{_clean(date)}</span></div>
        <div class="educ-sub">{_clean(item.course, 'Curso')} {_clean('· ' + item.description if item.description else '')}</div>
        """)
    return "\n".join(blocks)


def build_modern_resume_html(db: Session, tenant_id: int, user: User) -> str:
    profile: UserProfile = get_or_create_profile(db, tenant_id, user)
    skills = db.query(UserSkill).filter(UserSkill.tenant_id == tenant_id, UserSkill.user_id == user.id).order_by(UserSkill.id.asc()).all()
    experiences = db.query(UserExperience).filter(UserExperience.tenant_id == tenant_id, UserExperience.user_id == user.id).order_by(UserExperience.id.asc()).all()
    projects = db.query(UserProject).filter(UserProject.tenant_id == tenant_id, UserProject.user_id == user.id).order_by(UserProject.id.asc()).all()
    education = db.query(UserEducation).filter(UserEducation.tenant_id == tenant_id, UserEducation.user_id == user.id).order_by(UserEducation.id.asc()).all()

    full_name = _clean(profile.full_name or user.full_name, "Nome do candidato")
    title = _clean(profile.professional_title or user.target_role, "Profissional")
    email = _clean(profile.email or user.email)
    phone = _clean(profile.phone)
    location = _clean(profile.location)
    summary_plain = _plain(profile.summary) or shorten(_plain(profile.resume_text), width=650, placeholder="...")
    summary = _clean(summary_plain, "Resumo profissional extraído do currículo importado.")
    skill_rows = _skill_grid(skills, profile.resume_text)
    experience_blocks = _experience_html(experiences)
    project_blocks = _projects_html(projects)
    education_blocks = _education_html(education)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{full_name} — Currículo</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{ --ink:#1a1a1a; --mid:#444; --light:#777; --rule:#d0d0d0; --accent:#1a3a6b; --accent2:#2d5fa8; --page-w:210mm; --page-h:297mm; --pad:14mm; }}
  body {{ font-family:'DM Sans', Arial, sans-serif; font-size:9.4pt; line-height:1.45; color:var(--ink); background:#e8e8e8; -webkit-font-smoothing:antialiased; }}
  .page {{ width:var(--page-w); min-height:var(--page-h); margin:20px auto; background:#fff; padding:var(--pad); box-shadow:0 4px 40px rgba(0,0,0,.18); }}
  .header {{ display:flex; justify-content:space-between; align-items:flex-end; padding-bottom:9px; border-bottom:1.5px solid var(--accent); margin-bottom:12px; gap:18px; }}
  .header-left {{ flex:1; }} .name {{ font-family:'EB Garamond', Georgia, serif; font-size:24pt; font-weight:600; letter-spacing:.01em; color:var(--accent); line-height:1; margin-bottom:4px; }}
  .title-tag {{ font-size:8.4pt; color:var(--mid); letter-spacing:.06em; text-transform:uppercase; font-weight:400; }}
  .header-right {{ text-align:right; font-size:8.2pt; color:var(--mid); line-height:1.7; }}
  .section {{ margin-bottom:10px; }} .section-title {{ font-size:7.8pt; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin-bottom:5px; padding-bottom:3px; border-bottom:1px solid var(--rule); }}
  .resume-text {{ font-size:9pt; color:var(--mid); line-height:1.5; }}
  .skills-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:2px 20px; }} .skill-row {{ display:flex; gap:5px; font-size:8.8pt; line-height:1.55; align-items:baseline; }}
  .skill-label {{ font-weight:600; color:var(--accent); white-space:nowrap; flex-shrink:0; min-width:90px; }} .skill-value {{ color:var(--mid); }}
  .entry,.project {{ margin-bottom:8px; }} .entry-head,.project-head,.educ-row {{ display:flex; justify-content:space-between; align-items:baseline; gap:8px; }}
  .entry-title,.project-name,.educ-inst {{ font-weight:600; font-size:9.4pt; color:var(--ink); flex:1; }} .entry-date,.educ-date {{ font-size:8.2pt; color:var(--light); font-style:italic; white-space:nowrap; }}
  .entry-company,.project-stack,.educ-sub {{ font-size:8.4pt; color:var(--mid); font-style:italic; margin-bottom:4px; }}
  ul {{ list-style:none; padding:0; margin:0; }} ul li {{ font-size:8.8pt; color:var(--mid); padding-left:11px; position:relative; margin-bottom:2px; line-height:1.45; }} ul li::before {{ content:'·'; position:absolute; left:2px; color:var(--accent2); font-weight:700; }}
  ul li strong {{ color:var(--ink); font-weight:600; }} .entry-divider {{ border:none; border-top:1px dashed #e0e0e0; margin:6px 0; }}
  .print-hint {{ position:fixed; right:18px; bottom:18px; padding:10px 14px; border-radius:999px; background:var(--accent); color:white; font-size:12px; box-shadow:0 10px 30px rgba(0,0,0,.18); }}
  @media print {{ body {{ background:none; }} .page {{ margin:0; width:210mm; min-height:297mm; padding:13mm; box-shadow:none; }} .print-hint {{ display:none; }} @page {{ size:A4; margin:0; }} }}
</style>
</head>
<body>
<div class="page">
  <header class="header">
    <div class="header-left"><div class="name">{full_name}</div><div class="title-tag">{title}</div></div>
    <div class="header-right">{email}{' | ' if email and phone else ''}{phone}<br>{location}</div>
  </header>
  <section class="section"><div class="section-title">Resumo Profissional</div><p class="resume-text">{summary}</p></section>
  <section class="section"><div class="section-title">Competências Técnicas</div><div class="skills-grid">{skill_rows}</div></section>
  <section class="section"><div class="section-title">Experiência Profissional</div>{experience_blocks}</section>
  <section class="section"><div class="section-title">Projetos</div>{project_blocks}</section>
  <section class="section"><div class="section-title">Formação</div>{education_blocks}</section>
</div>
<div class="print-hint">Ctrl+P → Salvar como PDF</div>
</body>
</html>"""
