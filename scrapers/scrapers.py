# -*- coding: utf-8 -*-
"""
Applymize - Job Scrapers v6
Gupy API + Gupy portal fallback + Vagas.com + filtros melhores.
"""

from __future__ import annotations

import re
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus, urljoin
from datetime import datetime, date
from typing import Dict, List, Optional


HDR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HDR)


def log(msg: str):
    print(f"[SCRAPER] {datetime.now().strftime('%H:%M:%S')} | {msg}")


def _delay(a=0.25, b=0.8):
    time.sleep(random.uniform(a, b))


def _clean(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def _clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return _clean(soup.get_text(" "))


def _get(url: str, timeout: int = 15) -> Optional[requests.Response]:
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code in (200, 201):
            return r
        log(f"HTTP {r.status_code} em {url[:130]}")
        return None
    except Exception as e:
        log(f"GET falhou: {url[:130]} | {e}")
        return None


def _slug_hifen(text: str) -> str:
    text = _clean(text).lower()
    text = re.sub(r"[^\w\sÀ-ÿ-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def build_query_variants(query: str) -> List[str]:
    q = _clean(query)
    variants = [q]
    base = q

    for r in [
        " Pleno", " pleno", " Júnior", " Junior", " júnior", " junior",
        " Sênior", " Senior", " sênior", " senior", " Especialista", " especialista",
    ]:
        base = base.replace(r, "")

    if base and base not in variants:
        variants.append(base)

    lower = q.lower()
    if "dados" in lower and "Analista de Dados" not in variants:
        variants.append("Analista de Dados")
    if "bi" in lower and "Analista de BI" not in variants:
        variants.append("Analista de BI")
    if "python" in lower and "Desenvolvedor Python" not in variants:
        variants.append("Desenvolvedor Python")
    if "engenheiro" in lower and "Engenheiro de Dados" not in variants:
        variants.append("Engenheiro de Dados")

    out = []
    for v in variants:
        if v and v not in out:
            out.append(v)
    return out[:4]


def location_to_gupy_state(location: str) -> str:
    loc = _clean(location).lower()
    if not loc:
        return ""
    if loc in ["são paulo", "sao paulo", "sp", "grande abc", "abc", "santo andré", "santo andre"]:
        return "São Paulo"
    if loc in ["rio de janeiro", "rj"]:
        return "Rio de Janeiro"
    if loc in ["minas gerais", "mg", "belo horizonte", "bh"]:
        return "Minas Gerais"
    if loc in ["paraná", "parana", "pr", "curitiba"]:
        return "Paraná"
    if loc in ["santa catarina", "sc"]:
        return "Santa Catarina"
    if loc in ["rio grande do sul", "rs", "porto alegre"]:
        return "Rio Grande do Sul"
    return location


def expand_location_terms(location: str) -> List[str]:
    loc = _clean(location).lower()
    aliases = {
        "grande abc": [
            "grande abc", "abc", "santo andré", "santo andre", "são bernardo", "sao bernardo",
            "são caetano", "sao caetano", "diadema", "mauá", "maua", "ribeirão pires",
            "ribeirao pires", "rio grande da serra", "são paulo", "sao paulo", "sp",
            "híbrido", "hibrido", "remoto", "home office",
        ],
        "abc": [
            "grande abc", "abc", "santo andré", "santo andre", "são bernardo", "sao bernardo",
            "são caetano", "sao caetano", "diadema", "mauá", "maua", "são paulo",
            "sao paulo", "sp", "híbrido", "hibrido", "remoto", "home office",
        ],
        "são paulo": ["são paulo", "sao paulo", "sp"],
        "sao paulo": ["são paulo", "sao paulo", "sp"],
        "sp": ["são paulo", "sao paulo", "sp"],
        "remoto": ["remoto", "home office", "teletrabalho"],
        "home office": ["remoto", "home office", "teletrabalho"],
        "hibrido": ["híbrido", "hibrido"],
        "híbrido": ["híbrido", "hibrido"],
    }
    return aliases.get(loc, [loc])


def _contains_location(job_location: str, wanted: str, description: str = "") -> bool:
    if not wanted:
        return True

    loc = _clean(job_location).lower()
    wanted_clean = _clean(wanted).lower()
    desc = _clean(description).lower()
    terms = expand_location_terms(wanted_clean)

    if wanted_clean in ["remoto", "home office"]:
        return any(t in f"{loc} {desc}" for t in terms)

    if not loc and wanted_clean not in ["remoto", "home office"]:
        return False

    if wanted_clean in ["grande abc", "abc"]:
        return any(t in f"{loc} {desc}" for t in terms)

    if wanted_clean in ["são paulo", "sao paulo", "sp"]:
        invalid = [
            "rio de janeiro", "rj", "minas gerais", "mg", "paraná", "parana", "pr",
            "santa catarina", "sc", "rio grande do sul", "rs", "bahia", "ba",
            "pernambuco", "pe", "ceará", "ceara", "ce", "goiás", "goias", "go",
            "espírito santo", "espirito santo", "es",
        ]
        if any(e in loc for e in invalid):
            return False
        return (
            "são paulo" in loc or "sao paulo" in loc or loc == "sp"
            or loc.endswith(", sp") or " - sp" in loc or "/sp" in loc or "sp/" in loc
        )

    return any(t in loc for t in terms)


def normalize_job(job: Dict) -> Dict:
    title = _clean(job.get("title", ""))
    company = _clean(job.get("company", "")) or "Empresa não informada"
    location = _clean(job.get("location", ""))
    modality = _clean(job.get("modality", ""))
    url = _clean(job.get("url", ""))
    desc = _clean(job.get("description", ""))
    posted = _clean(job.get("posted", ""))

    joined = f"{title} {location} {desc}".lower()
    if not modality:
        if any(x in joined for x in ["remoto", "home office", "teletrabalho", "remote"]):
            modality = "Remoto"
        elif any(x in joined for x in ["híbrido", "hibrido", "hybrid"]):
            modality = "Híbrido"
        elif any(x in joined for x in ["presencial", "on-site", "onsite"]):
            modality = "Presencial"
        elif location:
            modality = "Presencial"

    return {
        "title": title,
        "company": company,
        "location": location,
        "modality": modality,
        "url": url,
        "source": job.get("source", ""),
        "posted": posted[:10] if posted else "",
        "description": desc,
        "job_id": _clean(job.get("job_id", "")),
    }


def dedupe_jobs(jobs: List[Dict]) -> List[Dict]:
    seen = {}
    for job in jobs:
        url = job.get("url", "").split("?")[0].rstrip("/")
        key = url or f"{job.get('title','').lower()}|{job.get('company','').lower()}|{job.get('location','').lower()}"

        if key not in seen:
            seen[key] = job
        else:
            old_q = len(seen[key].get("description", "")) + len(seen[key].get("location", ""))
            new_q = len(job.get("description", "")) + len(job.get("location", ""))
            if new_q > old_q:
                seen[key] = job
    return list(seen.values())


def ghost_detect(job):
    score = 0
    flags = []
    company = job.get("company", "").lower()
    desc = job.get("description", "").lower()
    title = job.get("title", "").lower()

    if not company or company in ["empresa confidencial", "confidential", "não informada", "nao informada", "empresa não informada"]:
        score += 25
        flags.append("Empresa oculta")

    if len(desc) < 120:
        score += 20
        flags.append("Descrição genérica/vazia")

    vague = ["profissional dinâmico", "perfil proativo", "boa comunicação", "trabalho em equipe", "fácil aprendizado"]
    if sum(1 for p in vague if p in desc) >= 3:
        score += 15
        flags.append("Linguagem excessivamente genérica")

    if "urgente" in title:
        score += 10
        flags.append("Marcada como urgente")

    posted = job.get("posted", "")
    if posted:
        try:
            pd = datetime.strptime(posted[:10], "%Y-%m-%d").date()
            age = (date.today() - pd).days
            if age > 45:
                score += 20
                flags.append(f"Publicada há {age} dias")
        except Exception:
            pass

    level = "🔴 Alta" if score >= 50 else "🟡 Média" if score >= 25 else "🟢 Baixa"
    return {"ghost_score": score, "ghost_level": level, "ghost_flags": flags}


def local_match(job, kws):
    if not kws:
        return 50

    text = (job.get("title", "") + " " + job.get("description", "") + " " + job.get("company", "")).lower()
    kws_clean = [str(k).lower().strip() for k in kws if str(k).strip()]
    if not kws_clean:
        return 50

    hits = sum(1 for k in kws_clean if k in text)
    score = int((hits / max(len(kws_clean), 1)) * 100)
    if hits:
        score += 25
    if any(x in job.get("title", "").lower() for x in ["dados", "bi", "python", "engenheiro"]):
        score += 10
    return min(100, max(30, score))


def job_quality_score(job: Dict) -> int:
    score = 0
    if job.get("title"): score += 15
    if job.get("company") and job.get("company") != "Empresa não informada": score += 15
    if job.get("location"): score += 10
    if job.get("posted"): score += 10
    if len(job.get("description", "")) >= 300: score += 30
    elif len(job.get("description", "")) >= 120: score += 15
    if job.get("url"): score += 10
    if job.get("modality"): score += 10
    return min(score, 100)


def enrich_generic(job: Dict) -> Dict:
    url = job.get("url", "")
    if not url:
        return job

    r = _get(url, timeout=15)
    if not r:
        return job

    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = _clean(soup.get_text(" "))
    if len(text) > len(job.get("description", "")):
        job["description"] = text[:6000]

    if not job.get("location"):
        m = re.search(r"(Local(?:ização)?|Cidade)\s*[:\-]?\s*([A-Za-zÀ-ÿ\s,\/-]{3,80})", text, re.I)
        if m:
            job["location"] = _clean(m.group(2))[:80]

    return job


def enrich_job(job: Dict) -> Dict:
    if job.get("source") != "Gupy":
        return enrich_generic(job)
    return job


def _gupy_job_from_api(j: Dict) -> Dict:
    company = j.get("company", {}) or {}
    return normalize_job({
        "title": j.get("name", "") or j.get("title", ""),
        "company": company.get("name", "") or j.get("companyName", ""),
        "location": j.get("city", "") or j.get("state", "") or j.get("country", ""),
        "modality": j.get("workplaceType", "") or j.get("workplaceTypeName", ""),
        "url": j.get("jobUrl", "") or j.get("url", ""),
        "source": "Gupy",
        "posted": (j.get("publishedDate", "") or j.get("publishedAt", "") or "")[:10],
        "description": _clean_html(j.get("description", "") or ""),
        "job_id": str(j.get("id", "") or j.get("jobId", "")),
    })


def _find_jobs_recursive(obj):
    results = []
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if (("name" in keys or "title" in keys) and ("id" in keys or "jobId" in keys or "jobUrl" in keys or "url" in keys)):
            results.append(obj)
        for v in obj.values():
            results.extend(_find_jobs_recursive(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_find_jobs_recursive(item))
    return results


def _normalize_gupy_portal_item(item: Dict) -> Optional[Dict]:
    title = item.get("name") or item.get("title") or item.get("jobName") or ""
    job_id = str(item.get("id") or item.get("jobId") or "")
    url = item.get("jobUrl") or item.get("url") or item.get("applyUrl") or item.get("portalUrl") or ""
    if not url and job_id:
        url = f"https://portal.gupy.io/job-search/job/{job_id}"

    company = ""
    if isinstance(item.get("company"), dict):
        company = item.get("company", {}).get("name", "")
    else:
        company = item.get("companyName", "") or str(item.get("company") or "")

    location = (
        item.get("city", "") or item.get("state", "") or item.get("location", "")
        or item.get("addressCity", "") or item.get("addressState", "")
    )
    modality = item.get("workplaceType", "") or item.get("workplaceTypeName", "")
    posted = item.get("publishedDate", "") or item.get("publishedAt", "") or item.get("createdAt", "") or ""
    desc = _clean_html(item.get("description", "") or item.get("jobDescription", "") or "")

    if not title and not url:
        return None

    return normalize_job({
        "title": title,
        "company": company,
        "location": location,
        "modality": modality,
        "url": url,
        "source": "Gupy",
        "posted": posted[:10] if posted else "",
        "description": desc,
        "job_id": job_id,
    })


def _extract_gupy_jobs_from_portal_html(html: str) -> List[Dict]:
    jobs = []
    soup = BeautifulSoup(html, "lxml")

    for script in soup.find_all("script"):
        txt = script.string or script.get_text() or ""
        if not txt:
            continue

        if "__NEXT_DATA__" in txt or '"props"' in txt or '"jobs"' in txt:
            try:
                start = txt.find("{")
                end = txt.rfind("}")
                if start != -1 and end != -1 and end > start:
                    payload = json.loads(txt[start:end + 1])
                    for item in _find_jobs_recursive(payload):
                        job = _normalize_gupy_portal_item(item)
                        if job:
                            jobs.append(job)
            except Exception:
                pass

        for m in re.finditer(r"https://[^\"']*gupy[^\"']*/jobs/[^\"']+", txt):
            jobs.append(normalize_job({
                "title": "",
                "company": "",
                "location": "",
                "modality": "",
                "url": m.group(0),
                "source": "Gupy",
                "posted": "",
                "description": "",
                "job_id": "",
            }))

    for a in soup.select("a[href*='/jobs/'], a[href*='gupy.io/jobs/']"):
        href = a.get("href", "")
        text = _clean(a.get_text(" "))
        if not href:
            continue
        jobs.append(normalize_job({
            "title": text[:120],
            "company": "",
            "location": "",
            "modality": "",
            "url": urljoin("https://portal.gupy.io", href),
            "source": "Gupy",
            "posted": "",
            "description": text,
            "job_id": "",
        }))

    return dedupe_jobs([j for j in jobs if j.get("url") or j.get("title")])


def scrape_gupy(query, location="", limit=20):
    jobs = []
    variants = build_query_variants(query)

    # 1) API antiga
    for q in variants:
        try:
            params = {"jobName": q, "offset": 0, "limit": limit}
            if location:
                state = location_to_gupy_state(location)
                params["state"] = state
                params["city"] = location

            url = f"https://portal.api.gupy.io/api/v1/jobs?{urlencode(params)}"
            r = SESSION.get(url, timeout=18)
            if r.status_code != 200:
                log(f"Gupy API HTTP {r.status_code} para termo '{q}'")
                continue

            data = r.json().get("data", [])
            log(f"Gupy API termo '{q}': {len(data)}")
            for j in data:
                jobs.append(_gupy_job_from_api(j))

            _delay(0.15, 0.45)
            if len(jobs) >= limit:
                break
        except Exception as e:
            log(f"Gupy API erro termo '{q}': {e}")

    # 2) portal público: /job-search/?term=...
    if len(jobs) < limit:
        for q in variants:
            try:
                params = [
                    ("term", q),
                    ("workplaceTypes[]", "on-site"),
                    ("workplaceTypes[]", "hybrid"),
                    ("workplaceTypes[]", "remote"),
                ]
                state = location_to_gupy_state(location)
                if state:
                    params.insert(1, ("state", state))

                url = "https://portal.gupy.io/job-search/" + "?" + urlencode(params)
                r = _get(url, timeout=18)
                if not r:
                    continue

                portal_jobs = _extract_gupy_jobs_from_portal_html(r.text)
                log(f"Gupy Portal termo '{q}': {len(portal_jobs)}")
                jobs.extend(portal_jobs)

                _delay(0.2, 0.5)
                if len(jobs) >= limit:
                    break
            except Exception as e:
                log(f"Gupy Portal erro termo '{q}': {e}")

    return dedupe_jobs(jobs)[:limit]


def scrape_vagas_com(query, location="", limit=20):
    jobs = []
    for q in build_query_variants(query):
        try:
            url = f"https://www.vagas.com.br/vagas-de-{quote_plus(q)}"
            r = _get(url)
            if not r:
                continue

            soup = BeautifulSoup(r.text, "lxml")
            cards = soup.select("li.vaga") or soup.select("[class*='vaga']")
            log(f"Vagas.com termo '{q}': {len(cards)} cards")

            for card in cards[:limit]:
                te = card.select_one("h2") or card.select_one("h3") or card.select_one("[class*='cargo']")
                ce = card.select_one("[class*='empresa']") or card.select_one("span.emprVaga")
                le = card.select_one("[class*='local']") or card.select_one("span.local")
                ae = card.select_one("a[href*='/vaga']") or card.select_one("a[href*='vagas/']") or card.select_one("a[href]")

                title = _clean(te.get_text(" ")) if te else ""
                href = ae.get("href", "") if ae else ""
                if title and href:
                    jobs.append(normalize_job({
                        "title": title,
                        "company": _clean(ce.get_text(" ")) if ce else "",
                        "location": _clean(le.get_text(" ")) if le else "",
                        "modality": "",
                        "url": urljoin("https://www.vagas.com.br", href),
                        "source": "Vagas.com",
                        "posted": "",
                        "description": _clean(card.get_text(" "))[:1600],
                        "job_id": "",
                    }))

            _delay(0.2, 0.5)
            if len(jobs) >= limit:
                break
        except Exception as e:
            log(f"Vagas.com erro termo '{q}': {e}")

    return dedupe_jobs(jobs)[:limit]


def scrape_catho(query, location="", limit=20):
    jobs = []
    for q in build_query_variants(query):
        urls = [
            f"https://www.catho.com.br/vagas/{quote_plus(q)}/",
            f"https://www.catho.com.br/vagas/{_slug_hifen(q)}/",
            f"https://www.catho.com.br/vagas/?q={quote_plus(q)}",
        ]
        for url in urls:
            try:
                r = _get(url)
                if not r:
                    continue

                soup = BeautifulSoup(r.text, "lxml")
                cards = soup.select("article") or soup.select("[class*='JobCard']") or soup.select("li")
                log(f"Catho termo '{q}' url '{url[-45:]}': {len(cards)} cards")

                for card in cards[:limit]:
                    te = card.select_one("h2") or card.select_one("h3") or card.select_one("[class*='title']")
                    ce = card.select_one("[class*='company']") or card.select_one("[class*='empresa']")
                    le = card.select_one("[class*='location']") or card.select_one("[class*='local']") or card.select_one("[class*='city']")
                    ae = card.select_one("a[href*='/vagas/']") or card.select_one("a[href]")
                    title = _clean(te.get_text(" ")) if te else ""
                    href = ae.get("href", "") if ae else ""
                    if title and href:
                        jobs.append(normalize_job({
                            "title": title,
                            "company": _clean(ce.get_text(" ")) if ce else "",
                            "location": _clean(le.get_text(" ")) if le else "",
                            "modality": "",
                            "url": urljoin("https://www.catho.com.br", href),
                            "source": "Catho",
                            "posted": "",
                            "description": _clean(card.get_text(" "))[:1600],
                            "job_id": "",
                        }))
                if len(jobs) >= limit:
                    return dedupe_jobs(jobs)[:limit]
            except Exception as e:
                log(f"Catho erro termo '{q}': {e}")
            _delay(0.2, 0.5)

    return dedupe_jobs(jobs)[:limit]


def scrape_infojobs(query, location="", limit=20):
    jobs = []
    try:
        url = f"https://www.infojobs.com.br/empregos.aspx?palabra={quote_plus(query)}"
        if location:
            url += f"&poblacion={quote_plus(location)}"
        r = _get(url)
        if not r:
            return jobs

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("li.ij-OfferList-item") or soup.select("[class*='OfferList']") or soup.select("[class*='offer']")
        log(f"InfoJobs cards: {len(cards)}")

        for card in cards[:limit]:
            te = card.select_one("h2") or card.select_one("h3") or card.select_one("a[class*='title']")
            ce = card.select_one("[class*='company']")
            le = card.select_one("[class*='location']")
            ae = card.select_one("a[href]")
            title = _clean(te.get_text(" ")) if te else ""
            href = ae.get("href", "") if ae else ""
            if title and href:
                jobs.append(normalize_job({
                    "title": title,
                    "company": _clean(ce.get_text(" ")) if ce else "",
                    "location": _clean(le.get_text(" ")) if le else "",
                    "modality": "",
                    "url": urljoin("https://www.infojobs.com.br", href),
                    "source": "InfoJobs",
                    "posted": "",
                    "description": _clean(card.get_text(" "))[:1600],
                    "job_id": "",
                }))
    except Exception as e:
        log(f"InfoJobs erro: {e}")

    return dedupe_jobs(jobs)[:limit]


def scrape_indeed(query, location="Brasil", limit=20):
    jobs = []
    try:
        url = f"https://br.indeed.com/jobs?{urlencode({'q': query, 'l': location or 'Brasil', 'lang': 'pt'})}"
        r = _get(url)
        if not r:
            return jobs

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("div.job_seen_beacon") or soup.select("[data-jk]")
        log(f"Indeed cards: {len(cards)}")

        for card in cards[:limit]:
            te = card.select_one("h2.jobTitle span") or card.select_one("h2 a span") or card.select_one("a span")
            ce = card.select_one("[data-testid='company-name']") or card.select_one(".companyName")
            le = card.select_one("[data-testid='text-location']") or card.select_one(".companyLocation")
            ae = card.select_one("h2 a") or card.select_one("a[href*='/rc/clk']") or card.select_one("a[href*='jk=']")
            title = _clean(te.get_text(" ")) if te else ""
            href = ae.get("href", "") if ae else ""
            if title and href:
                jobs.append(normalize_job({
                    "title": title,
                    "company": _clean(ce.get_text(" ")) if ce else "",
                    "location": _clean(le.get_text(" ")) if le else "",
                    "modality": "",
                    "url": urljoin("https://br.indeed.com", href),
                    "source": "Indeed",
                    "posted": "",
                    "description": _clean(card.get_text(" "))[:1600],
                    "job_id": card.get("data-jk", ""),
                }))
    except Exception as e:
        log(f"Indeed erro: {e}")

    return dedupe_jobs(jobs)[:limit]


def scrape_linkedin(query, location="Brasil", limit=20):
    jobs = []
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(f"user-agent={HDR['User-Agent']}")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        driver.get(f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(query)}&location={quote_plus(location or 'Brasil')}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list, .jobs-search-results-list")))
        _delay(2, 3)
        cards = driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item, .job-search-card")
        for card in cards[:limit]:
            try:
                jobs.append(normalize_job({
                    "title": card.find_element(By.CSS_SELECTOR, "h3, .base-search-card__title").text.strip(),
                    "company": card.find_element(By.CSS_SELECTOR, "h4, .base-search-card__subtitle").text.strip(),
                    "location": card.find_element(By.CSS_SELECTOR, ".job-search-card__location, .base-search-card__metadata").text.strip(),
                    "modality": "",
                    "url": card.find_element(By.CSS_SELECTOR, "a").get_attribute("href"),
                    "source": "LinkedIn",
                    "posted": "",
                    "description": "",
                    "job_id": "",
                }))
            except Exception:
                continue
        driver.quit()
    except Exception as e:
        log(f"LinkedIn erro: {e}")

    return dedupe_jobs(jobs)[:limit]


SCRAPERS = {
    "gupy": scrape_gupy,
    "indeed": scrape_indeed,
    "catho": scrape_catho,
    "infojobs": scrape_infojobs,
    "vagas_com": scrape_vagas_com,
    "linkedin": scrape_linkedin,
}


def search_all(query, location="", platforms=None, limit=15, cv_keywords=None, enrich=True, filter_location=True):
    if platforms is None:
        platforms = ["gupy", "vagas_com", "catho", "infojobs"]

    all_jobs = []
    log(f"Busca iniciada | query='{query}' | location='{location}' | platforms={platforms}")

    for p in platforms:
        if p not in SCRAPERS:
            log(f"Plataforma ignorada: {p}")
            continue
        try:
            log(f"Coletando {p}...")
            results = SCRAPERS[p](query, location, limit)
            log(f"{p}: {len(results)} vagas brutas")
            all_jobs.extend(results)
            _delay(0.3, 0.9)
        except Exception as e:
            log(f"Error {p}: {e}")

    jobs = [normalize_job(j) for j in all_jobs if j.get("title") or j.get("url")]
    log(f"Após normalização: {len(jobs)}")
    jobs = dedupe_jobs(jobs)
    log(f"Após deduplicação inicial: {len(jobs)}")

    if enrich:
        enriched = []
        max_enrich = min(len(jobs), max(limit, 20))
        for idx, job in enumerate(jobs[:max_enrich]):
            try:
                if job.get("source") != "Gupy" and job.get("url"):
                    log(f"Enriquecendo {idx + 1}/{max_enrich} | {job.get('source')} | {job.get('title')[:55]}")
                    job = enrich_job(job)
                    _delay(0.15, 0.45)
                enriched.append(normalize_job(job))
            except Exception as e:
                log(f"Falha enrich: {e}")
                enriched.append(job)
        if len(jobs) > max_enrich:
            enriched.extend(jobs[max_enrich:])
        jobs = enriched

    if filter_location and location:
        before = len(jobs)
        jobs = [j for j in jobs if _contains_location(j.get("location", ""), location, j.get("description", ""))]
        log(f"Após filtro de localização '{location}' pós-enriquecimento: {len(jobs)} de {before}")

    jobs = dedupe_jobs(jobs)

    final = []
    for job in jobs:
        job.update(ghost_detect(job))
        job["match_score"] = local_match(job, cv_keywords or [])
        job["quality_score"] = job_quality_score(job)
        final.append(job)

    final.sort(key=lambda x: (x.get("match_score", 0), x.get("quality_score", 0), -x.get("ghost_score", 0)), reverse=True)
    log(f"Busca finalizada: {len(final)} vagas finais")
    return final[:max(limit * max(len(platforms), 1), limit)]
