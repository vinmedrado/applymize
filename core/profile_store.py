from pathlib import Path
import json
from datetime import datetime

DATA_DIR = Path.home() / ".applymize"
PROFILE_FILE = DATA_DIR / "profile.json"

def save_profile(cv_data=None, ats_result=None, job_terms=None, emp_score=None):
    DATA_DIR.mkdir(exist_ok=True)

    atual = load_profile() or {}

    if cv_data is not None:
        atual["cv_data"] = cv_data

    if ats_result is not None:
        atual["ats_result"] = ats_result

    if job_terms is not None:
        atual["job_terms"] = job_terms

    if emp_score is not None:
        atual["emp_score"] = emp_score

    atual["saved_at"] = datetime.now().isoformat()

    PROFILE_FILE.write_text(
        json.dumps(atual, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def load_profile():
    if not PROFILE_FILE.exists():
        return None

    try:
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except:
        return None

def delete_profile():
    if PROFILE_FILE.exists():
        PROFILE_FILE.unlink()


# compatibilidade com o código antigo
def save_cv_profile(cv_data):
    save_profile(cv_data=cv_data)

def load_cv_profile():
    profile = load_profile()
    return profile.get("cv_data") if profile else None

def delete_cv_profile():
    delete_profile()