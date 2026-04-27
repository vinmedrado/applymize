"""CareerLens v3 - Auth & Persistence"""
import os, json, hashlib, base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime

DATA_DIR = Path.home() / ".applymize"
CONFIG_FILE = DATA_DIR / "config.enc"
SALT_FILE   = DATA_DIR / ".salt"

def _ensure(): DATA_DIR.mkdir(exist_ok=True)

def _salt():
    _ensure()
    if SALT_FILE.exists(): return SALT_FILE.read_bytes()
    s = os.urandom(16); SALT_FILE.write_bytes(s); return s

def _key(pwd):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=_salt(), iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(pwd.encode()))

def _hash(pwd): return hashlib.pbkdf2_hmac("sha256", pwd.encode(), _salt(), 480000).hex()

def user_exists(): _ensure(); return CONFIG_FILE.exists()

def register_user(name, pwd, groq_key):
    try:
        _ensure()
        cfg = {"username": name, "password_hash": _hash(pwd), "groq_api_key": groq_key, "prefs": {}}
        CONFIG_FILE.write_bytes(Fernet(_key(pwd)).encrypt(json.dumps(cfg).encode()))
        return True
    except: return False

def login_user(pwd):
    try:
        cfg = json.loads(Fernet(_key(pwd)).decrypt(CONFIG_FILE.read_bytes()).decode())
        return cfg if cfg.get("password_hash") == _hash(pwd) else None
    except: return None

def update_config(pwd, updates):
    cfg = login_user(pwd)
    if not cfg: return False
    cfg.update(updates)
    CONFIG_FILE.write_bytes(Fernet(_key(pwd)).encrypt(json.dumps(cfg).encode()))
    return True

# ── JSON stores ──
def _load(fname, default):
    _ensure()
    p = DATA_DIR / fname
    try: return json.loads(p.read_text()) if p.exists() else default
    except: return default

def _save(fname, data):
    _ensure()
    (DATA_DIR / fname).write_text(json.dumps(data, ensure_ascii=False, indent=2))

def load_funnel():   return _load("funnel.json",   {"Interesse":[],"Aplicado":[],"Entrevista":[],"Oferta":[],"Recusado":[]})
def save_funnel(d):  _save("funnel.json", d)
def load_history():  return _load("history.json",  [])
def save_history(d): _save("history.json", d)
def load_alerts():   return _load("alerts.json",   [])
def save_alerts(d):  _save("alerts.json", d)
def load_abtest():   return _load("abtest.json",   {"cv_a": "", "cv_b": "", "results": {"a": [], "b": []}})
def save_abtest(d):  _save("abtest.json", d)
def load_stats():    return _load("stats.json",    {"weekly": [], "applications": 0, "interviews": 0, "offers": 0, "score_history": []})
def save_stats(d):   _save("stats.json", d)
def load_market():   return _load("market_cache.json", {})
def save_market(d):  _save("market_cache.json", d)
