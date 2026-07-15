from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass

try:
    from langdetect import LangDetectException, detect
except Exception:  # pragma: no cover
    detect = None

    class LangDetectException(Exception):
        pass


TECHNICAL_TERMS = [
    "Python", "SQL", "API", "APIs", "REST", "GraphQL", "Machine Learning", "Data Science",
    "Power BI", "Excel", "VBA", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL",
    "SQLite", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub",
    "React", "TypeScript", "JavaScript", "Node.js", "Pandas", "NumPy", "Scikit-learn",
    "ETL", "ELT", "Airflow", "Spark", "Kafka", "Terraform", "Linux", "CI/CD",
    "Selenium", "Playwright", "Pytest", "SQLAlchemy", "Alembic", "Streamlit",
]

ROLE_TRANSLATIONS = {
    "Software Engineer": "Engenheiro de Software",
    "Data Analyst": "Analista de Dados",
    "Backend Developer": "Desenvolvedor Backend",
    "Frontend Developer": "Desenvolvedor Frontend",
    "Data Engineer": "Engenheiro de Dados",
    "Business Analyst": "Analista de Negócios",
    "Product Manager": "Gerente de Produto",
    "Full Stack Developer": "Desenvolvedor Full Stack",
    "DevOps Engineer": "Engenheiro DevOps",
    "Machine Learning Engineer": "Engenheiro de Machine Learning",
}

PHRASE_TRANSLATIONS = {
    "we are looking for": "estamos buscando",
    "you will be responsible for": "você será responsável por",
    "experience with": "experiência com",
    "knowledge of": "conhecimento em",
    "strong communication skills": "boa comunicação",
    "problem solving": "resolução de problemas",
    "job description": "descrição da vaga",
    "about the role": "sobre a vaga",
    "about us": "sobre a empresa",
    "requirements": "requisitos",
    "responsibilities": "responsabilidades",
    "qualifications": "qualificações",
    "benefits": "benefícios",
    "remote job": "vaga remota",
    "remote work": "trabalho remoto",
    "full time": "tempo integral",
    "part time": "meio período",
    "on-site": "presencial",
}

WORD_TRANSLATIONS = {
    "and": "e",
    "or": "ou",
    "with": "com",
    "for": "para",
    "in": "em",
    "to": "para",
    "of": "de",
    "the": "o",
    "a": "um",
    "an": "um",
    "senior": "sênior",
    "junior": "júnior",
    "mid": "pleno",
    "lead": "líder",
    "manager": "gerente",
    "analyst": "analista",
    "engineer": "engenheiro",
    "developer": "desenvolvedor",
    "specialist": "especialista",
    "coordinator": "coordenador",
    "remote": "remoto",
    "hybrid": "híbrido",
    "onsite": "presencial",
    "skills": "habilidades",
    "experience": "experiência",
    "knowledge": "conhecimento",
    "team": "time",
    "business": "negócio",
    "data": "dados",
    "software": "software",
    "system": "sistema",
    "systems": "sistemas",
    "development": "desenvolvimento",
    "automation": "automação",
    "dashboard": "dashboard",
    "reports": "relatórios",
    "reporting": "relatórios",
    "analytics": "analytics",
    "process": "processo",
    "processes": "processos",
    "quality": "qualidade",
    "testing": "testes",
    "support": "suporte",
    "cloud": "cloud",
    "database": "banco de dados",
    "queries": "consultas",
    "pipeline": "pipeline",
    "pipelines": "pipelines",
    "scraping": "scraping",
    "web": "web",
    "application": "aplicação",
    "applications": "aplicações",
}

POST_PROCESS_REPLACEMENTS = {
    "engenheiro de software software": "engenheiro de software",
    "desenvolvedor backend backend": "desenvolvedor backend",
    "desenvolvedor frontend frontend": "desenvolvedor frontend",
    "analista de dados dados": "analista de dados",
    "engenheiro de dados dados": "engenheiro de dados",
    "com com": "com",
    "para para": "para",
    "de de": "de",
    "e e": "e",
    "vaga vaga": "vaga",
}


@dataclass(frozen=True)
class TranslationResult:
    original_text: str
    normalized_text: str
    language: str
    translated: bool


_TRANSLATION_CACHE: dict[str, TranslationResult] = {}


def cache_key(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[“”]", "\"", text)
    text = re.sub(r"[‘’]", "'", text)
    return text.strip()


def mark_technical_terms(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}
    result = text

    terms = sorted(set(TECHNICAL_TERMS), key=len, reverse=True)
    for idx, term in enumerate(terms):
        token = f"__TECH_TERM_{idx}__"
        pattern = re.compile(rf"(?<![\w+#.]){re.escape(term)}(?![\w+#.])", re.IGNORECASE)

        def repl(match):
            protected[token] = match.group(0)
            return token

        result = pattern.sub(repl, result)

    url_pattern = re.compile(r"https?://[^\s)>\]]+", re.IGNORECASE)
    for match_idx, match in enumerate(url_pattern.findall(result)):
        token = f"__URL_TERM_{match_idx}__"
        protected[token] = match
        result = result.replace(match, token)

    return result, protected


def restore_technical_terms(text: str, protected: dict[str, str]) -> str:
    result = text
    for token, term in protected.items():
        result = result.replace(token, term)
    return result


def detect_language(text: str) -> str:
    cleaned = clean_text(text)
    if not cleaned:
        return "unknown"

    lower = f" {cleaned.lower()} "
    pt_markers = [
        " vaga ", " experiência ", " remoto ", " benefícios ", " requisitos ", " empresa ",
        " conhecimento ", " dados ", " formação ", " atuação ", " candidato ", " pessoa ",
    ]
    en_markers = [
        " we are ", " looking for ", " responsibilities ", " requirements ", " experience with ",
        " remote job ", " full time ", " apply ", " role ", " team ",
    ]

    pt_hits = sum(1 for item in pt_markers if item in lower)
    en_hits = sum(1 for item in en_markers if item in lower)

    if pt_hits > en_hits:
        return "pt"
    if en_hits > pt_hits:
        return "en"

    if detect is None:
        return "unknown"

    try:
        return detect(cleaned[:4000])
    except (LangDetectException, Exception):
        return "unknown"


def apply_role_dictionary(text: str) -> str:
    result = text
    for original, translated in sorted(ROLE_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"\b{re.escape(original)}\b", translated, result, flags=re.IGNORECASE)
    return result


def apply_phrase_dictionary(text: str) -> str:
    result = text
    for original, translated in sorted(PHRASE_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"\b{re.escape(original)}\b", translated, result, flags=re.IGNORECASE)
    return result


def apply_word_dictionary(text: str) -> str:
    def translate_word(match: re.Match) -> str:
        word = match.group(0)
        translated = WORD_TRANSLATIONS.get(word.lower())
        if not translated:
            return word
        if word[:1].isupper():
            return translated[:1].upper() + translated[1:]
        return translated

    return re.sub(r"\b[A-Za-z][A-Za-z\-]+\b", translate_word, text)


def post_process(text: str) -> str:
    result = clean_text(text)
    result = re.sub(r"\s+([,.;:!?])", r"\1", result)
    result = re.sub(r"([,.;:!?])([^\s\n])", r"\1 \2", result)
    result = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", result, flags=re.IGNORECASE)

    lowered = result.lower()
    for wrong, right in POST_PROCESS_REPLACEMENTS.items():
        lowered = lowered.replace(wrong, right)

    result = lowered
    result = re.sub(r"(^|[.!?]\s+)([a-záéíóúâêôãõç])", lambda m: m.group(1) + m.group(2).upper(), result)

    for term in TECHNICAL_TERMS:
        pattern = re.escape(term) if " " in term else rf"(?<![A-Za-z0-9_+#.]){re.escape(term)}(?![A-Za-z0-9_+#.])"
        result = re.sub(pattern, term, result, flags=re.IGNORECASE)

    for role in ROLE_TRANSLATIONS.values():
        result = re.sub(
            rf"(?<![A-Za-z0-9_+#.]){re.escape(role)}(?![A-Za-z0-9_+#.])",
            role,
            result,
            flags=re.IGNORECASE,
        )

    return clean_text(result)


def translate_en_to_pt(text: str) -> str:
    # Pipeline: texto -> limpeza -> protecao tecnica -> traducao -> restauracao -> pos-processamento
    cleaned = clean_text(text)
    if not cleaned:
        return ""

    protected_text, protected = mark_technical_terms(cleaned)
    translated = apply_role_dictionary(protected_text)
    translated = apply_phrase_dictionary(translated)
    translated = apply_word_dictionary(translated)
    restored = restore_technical_terms(translated, protected)
    return post_process(restored)


def normalize_free_text(text: str) -> TranslationResult:
    original = clean_text(text)
    key = cache_key(original)
    if key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[key]

    try:
        language = detect_language(original)
        if language not in {"pt", "pt-br"}:
            normalized = translate_en_to_pt(original)
            translated = normalized != original and bool(normalized)
            result = TranslationResult(original, normalized or original, language, translated)
        else:
            result = TranslationResult(original, original, language, False)
    except Exception:
        result = TranslationResult(original, original, "unknown", False)

    _TRANSLATION_CACHE[key] = result
    return result


def dictionary_translate_en_to_pt(text: str) -> str:
    try:
        return translate_en_to_pt(text)
    except Exception:
        return clean_text(text)


def normalize_job_text(title: str, description: str) -> dict:
    title_original = clean_text(title)
    description_original = clean_text(description)

    try:
        title_result = normalize_free_text(title_original)
        description_result = normalize_free_text(description_original)
        language = description_result.language if description_result.language != "unknown" else title_result.language
        translated = title_result.translated or description_result.translated

        return {
            "title_original": title_original,
            "description_original": description_original,
            "title": title_result.normalized_text or title_original,
            "description": description_result.normalized_text or description_original,
            "language": language,
            "translated": translated,
        }
    except Exception:
        return {
            "title_original": title_original,
            "description_original": description_original,
            "title": title_original,
            "description": description_original,
            "language": "unknown",
            "translated": False,
        }


def clear_translation_cache() -> None:
    _TRANSLATION_CACHE.clear()


def translation_cache_size() -> int:
    return len(_TRANSLATION_CACHE)
