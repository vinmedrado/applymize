from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./local_smoke_applymize.db")
os.environ.setdefault("SECRET_KEY", "local-smoke-secret")
os.environ.setdefault("REFRESH_SECRET_KEY", "local-smoke-refresh-secret")
os.environ.setdefault("RATE_LIMIT_REQUESTS", "1000")

from backend.core.database import Base, engine
from backend.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

register = client.post("/api/auth/register", json={
    "tenant_name": "Smoke Tenant",
    "full_name": "Smoke User",
    "email": "smoke@applymize.local",
    "password": "Strong123!",
    "skills": "Python, SQL, FastAPI, Docker",
    "seniority": "mid",
    "target_role": "Backend Python"
})
assert register.status_code == 200, register.text
token = register.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

job = client.post("/api/jobs/", headers=headers, json={
    "title": "Backend FastAPI Developer",
    "company": "Smoke Co",
    "description": "Python FastAPI PostgreSQL Docker SQL",
    "requirements": "Python, FastAPI, PostgreSQL, Docker",
    "seniority": "mid",
    "remote": True
})
assert job.status_code == 200, job.text

strategy = client.get("/api/strategy/recommendations", headers=headers)
assert strategy.status_code == 200, strategy.text
assert len(strategy.json()) == 1

print("Smoke check OK")
