from __future__ import annotations

import io
import json
import re
import unicodedata
from typing import Any

from docx import Document
from pypdf import PdfReader


KNOWN_SKILLS = [
    "Python", "SQL", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL", "SQLite",
    "Docker", "Kubernetes", "Power BI", "Excel", "VBA", "Machine Learning",
    "Scikit-learn", "Pandas", "NumPy", "APIs", "REST", "GraphQL", "ETL", "Airflow",
    "Spark", "React", "TypeScript", "JavaScript", "Node.js", "AWS", "Azure", "GCP",
    "Git", "GitHub", "Selenium", "Playwright", "Automação", "Data Engineering",
    "Data Analysis", "DAX", "Power Query", "SQLAlchemy", "Alembic", "Pytest",
    "CI/CD", "Linux", "Postman", "Streamlit", "PyQt", "Scraping", "BeautifulSoup",
]

SECTION_ALIASES = {
    "experiences": ["experiência", "experiencia", "experience", "histórico profissional", "historico profissional", "carreira", "employment"],
    "education": ["educação", "educacao", "formação", "formacao", "academic", "education", "graduação", "graduacao"],
    "projects": ["projetos", "projeto", "projects", "portfolio", "github"],
    "languages": ["idiomas", "languages", "línguas", "linguas"],
    "certifications": ["certificações", "certificacoes", "certificates", "certifications", "cursos"],
    "skills": ["skills", "habilidades", "competências", "competencias", "tecnologias", "ferramentas"],
}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()


def extract_resume_text(filename: str, content_type: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf") or "pdf" in content_type:
        reader = PdfReader(io.BytesIO(content))
        return normalize_text("\n".join(page.extract_text() or "" for page in reader.pages))
    if lower.endswith(".docx") or "word" in content_type or "officedocument" in content_type:
        document = Document(io.BytesIO(content))
        return normalize_text("\n".join(paragraph.text for paragraph in document.paragraphs))
    if lower.endswith(".txt") or "text" in content_type:
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return normalize_text(content.decode(encoding))
            except UnicodeDecodeError:
                pass
        return normalize_text(content.decode("utf-8", errors="ignore"))
    raise ValueError("Formato não suportado. Use PDF, DOCX ou TXT.")


def extract_links(text: str) -> dict[str, str]:
    urls = re.findall(r"https?://[^\s)>\]]+", text or "", flags=re.I)
    linkedin = ""
    github = ""
    for url in urls:
        low = url.lower()
        if "linkedin.com" in low and not linkedin:
            linkedin = url.rstrip(".,;")
        if "github.com" in low and not github:
            github = url.rstrip(".,;")
    return {"linkedin": linkedin, "github": github}


def probable_name(lines: list[str], email: str = "") -> str:
    ignored = {"curriculum", "currículo", "resume", "cv", "perfil", "contato"}
    for line in lines[:10]:
        clean = line.strip(" -•|")
        low = normalize_ascii(clean)
        if not clean or "@" in clean or any(ch.isdigit() for ch in clean):
            continue
        if any(word in low for word in ignored):
            continue
        if 2 <= len(clean.split()) <= 5 and 5 <= len(clean) <= 80:
            return clean
    return email.split("@")[0] if email else ""


def detect_section(line: str) -> str | None:
    low = normalize_ascii(line).strip(" :|-")
    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalize_ascii(alias) in low and len(low) <= 55:
                return section
    return None


def sectionize(lines: list[str]) -> dict[str, list[str]]:
    sections = {key: [] for key in SECTION_ALIASES}
    current: str | None = None
    for line in lines:
        section = detect_section(line)
        if section:
            current = section
            continue
        if current and line.strip():
            sections[current].append(line.strip())
    return sections


def split_bullets(lines: list[str], limit: int = 8) -> list[str]:
    items: list[str] = []
    for line in lines:
        parts = re.split(r"\s*[•●▪\-]\s+", line)
        for part in parts:
            clean = part.strip(" -•\t")
            if 4 <= len(clean) <= 500:
                items.append(clean)
    dedup = []
    seen = set()
    for item in items:
        key = normalize_ascii(item)
        if key not in seen:
            seen.add(key)
            dedup.append(item)
    return dedup[:limit]


def extract_skills(text: str, sections: dict[str, list[str]]) -> list[str]:
    found = []
    lower = normalize_ascii(text)
    for skill in KNOWN_SKILLS:
        pattern = re.escape(normalize_ascii(skill))
        if re.search(rf"(^|[^a-z0-9]){pattern}([^a-z0-9]|$)", lower):
            found.append(skill)

    skill_lines = " ".join(sections.get("skills", []))
    for raw in re.split(r"[,;|/]", skill_lines):
        clean = raw.strip(" .-•")
        if 2 <= len(clean) <= 40 and not any(clean.lower() == s.lower() for s in found):
            found.append(clean)
    return found[:40]


def parse_resume_text(text: str) -> dict[str, Any]:
    text = normalize_text(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = sectionize(lines)

    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}", text)
    links = extract_links(text)

    parsed = {
        "probable_name": probable_name(lines, email_match.group(0) if email_match else ""),
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "linkedin": links["linkedin"],
        "github": links["github"],
        "skills": extract_skills(text, sections),
        "experiences": split_bullets(sections.get("experiences", []), 8),
        "education": split_bullets(sections.get("education", []), 6),
        "projects": split_bullets(sections.get("projects", []), 8),
        "languages": split_bullets(sections.get("languages", []), 6),
        "certifications": split_bullets(sections.get("certifications", []), 8),
        "raw_length": len(text),
        "clean_text_preview": text[:1000],
    }

    if not parsed["experiences"]:
        parsed["experiences"] = [line for line in lines if any(k in normalize_ascii(line) for k in ["empresa", "analista", "developer", "engenheiro", "assistente"])][:5]
    if not parsed["projects"]:
        parsed["projects"] = [line for line in lines if any(k in normalize_ascii(line) for k in ["projeto", "github", "sistema", "dashboard", "pipeline"])][:5]
    if not parsed["education"]:
        parsed["education"] = [line for line in lines if any(k in normalize_ascii(line) for k in ["curso", "certificacao", "faculdade", "universidade", "graduacao"])][:5]

    return parsed


def dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False)
