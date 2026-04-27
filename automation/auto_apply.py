"""
CareerLens v3 - Auto-Apply Engine
Auto-candidatura no Gupy + Modo Campanha
"""
import time, random, requests, json
from datetime import datetime
from urllib.parse import urlencode

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Content-Type": "application/json",
}

def _delay(): time.sleep(random.uniform(2.5, 5.0))


def apply_gupy(job_id: str, cv_path: str, user_info: dict) -> dict:
    """
    Submete candidatura no Gupy via Selenium (formulário público).
    Retorna dict com status e mensagem.
    """
    result = {"job_id": job_id, "status": "pending", "message": "", "timestamp": datetime.now().isoformat()}
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from webdriver_manager.chrome import ChromeDriverManager

        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        wait = WebDriverWait(driver, 15)

        # Navigate to job page
        job_url = f"https://portal.gupy.io/job/{job_id}"
        driver.get(job_url)
        _delay()

        # Look for apply button
        try:
            apply_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Candidatar') or contains(text(),'Aplicar') or contains(text(),'Apply')]")
            ))
            apply_btn.click()
            _delay()

            # Fill email if asked
            try:
                email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
                email_field.clear()
                email_field.send_keys(user_info.get("email", ""))
                _delay()
            except: pass

            # Upload CV if file input exists
            try:
                file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(cv_path)
                _delay()
            except: pass

            # Submit
            try:
                submit_btn = driver.find_element(By.XPATH,
                    "//button[contains(text(),'Enviar') or contains(text(),'Confirmar') or contains(text(),'Submit')]")
                submit_btn.click()
                _delay()
                result["status"] = "success"
                result["message"] = "Candidatura enviada com sucesso"
            except:
                result["status"] = "partial"
                result["message"] = "Formulário aberto — submissão manual necessária"

        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Não foi possível localizar botão de candidatura: {e}"

        driver.quit()

    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Erro no Selenium: {e}"

    return result


def run_campaign(
    jobs: list,
    cv_path: str,
    user_info: dict,
    min_match: int = 70,
    max_ghost: int = 40,
    max_per_day: int = 20,
    auto_apply: bool = True,
    progress_callback=None,
) -> list:
    """
    Modo Campanha: filtra vagas por critérios e processa em lote.
    Retorna lista de resultados.
    """
    results = []
    filtered = [
        j for j in jobs
        if j.get("match_score", 0) >= min_match
        and j.get("ghost_score", 100) <= max_ghost
    ][:max_per_day]

    total = len(filtered)
    for i, job in enumerate(filtered):
        if progress_callback:
            progress_callback(i, total, job.get("title", ""), job.get("company", ""))

        entry = {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "source": job.get("source", ""),
            "match_score": job.get("match_score", 0),
            "ghost_level": job.get("ghost_level", ""),
            "timestamp": datetime.now().isoformat(),
            "apply_status": "skipped",
            "apply_message": "",
        }

        if auto_apply and job.get("source") == "Gupy" and job.get("job_id"):
            apply_result = apply_gupy(job["job_id"], cv_path, user_info)
            entry["apply_status"] = apply_result["status"]
            entry["apply_message"] = apply_result["message"]
        elif auto_apply:
            # Non-Gupy: mark as needs manual application but tracked
            entry["apply_status"] = "tracked"
            entry["apply_message"] = "Adicionada ao funil — aplique manualmente"

        results.append(entry)
        _delay()

    return results


def get_company_intel(company_name: str) -> dict:
    """
    Busca inteligência pública sobre a empresa:
    - Dados do Glassdoor (scraping público)
    - Reclame Aqui score
    - LinkedIn employee count estimado
    """
    intel = {
        "company": company_name,
        "glassdoor_rating": None,
        "glassdoor_reviews": None,
        "recommend_to_friend": None,
        "ceo_approval": None,
        "reclameaqui_score": None,
        "red_flags": [],
        "green_flags": [],
        "summary": "",
    }

    # ── Glassdoor ──
    try:
        import urllib.parse
        from bs4 import BeautifulSoup
        search_url = f"https://www.glassdoor.com.br/Avaliações/{urllib.parse.quote(company_name)}-avaliações-SRCH_KE0,{len(company_name)}.htm"
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
        r = requests.get(search_url, headers=hdrs, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            rating_el = soup.select_one("[data-test='rating-info-score']") or soup.select_one(".ratingNumber")
            if rating_el:
                try:
                    intel["glassdoor_rating"] = float(rating_el.get_text(strip=True).replace(",","."))
                except: pass
    except: pass

    # ── Reclame Aqui ──
    try:
        ra_url = f"https://www.reclameaqui.com.br/empresa/{company_name.lower().replace(' ','-')}/"
        from bs4 import BeautifulSoup
        r = requests.get(ra_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            score_el = soup.select_one("[class*='score']") or soup.select_one("[class*='nota']")
            if score_el:
                try:
                    intel["reclameaqui_score"] = float(score_el.get_text(strip=True).replace(",","."))
                except: pass
    except: pass

    # ── Build flags & summary ──
    if intel["glassdoor_rating"]:
        if intel["glassdoor_rating"] >= 4.0:
            intel["green_flags"].append(f"Glassdoor {intel['glassdoor_rating']}/5 ⭐ — avaliação excelente")
        elif intel["glassdoor_rating"] >= 3.0:
            intel["green_flags"].append(f"Glassdoor {intel['glassdoor_rating']}/5 — avaliação razoável")
        else:
            intel["red_flags"].append(f"Glassdoor {intel['glassdoor_rating']}/5 ⚠️ — avaliação baixa")

    if intel["reclameaqui_score"]:
        if intel["reclameaqui_score"] >= 7.0:
            intel["green_flags"].append(f"Reclame Aqui {intel['reclameaqui_score']}/10 — boa reputação")
        else:
            intel["red_flags"].append(f"Reclame Aqui {intel['reclameaqui_score']}/10 ⚠️ — reputação questionável")

    flags_txt = ""
    if intel["green_flags"]: flags_txt += "✅ " + " | ".join(intel["green_flags"])
    if intel["red_flags"]:   flags_txt += " ⚠️ " + " | ".join(intel["red_flags"])
    intel["summary"] = flags_txt or "Dados públicos não encontrados para esta empresa."

    return intel
