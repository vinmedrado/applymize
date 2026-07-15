import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:5173"
os.environ["RATE_LIMIT_REQUESTS"] = "1000"
os.environ["AUTOMATION_SCHEDULER_ENABLED"] = "false"
os.environ["NOTIFICATIONS_ENABLED"] = "false"
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""

from backend.core.database import Base, engine
from backend.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    payload = {
        "tenant_name": "Tenant Test",
        "full_name": "User Test",
        "email": "user@test.com",
        "password": "Strong123!",
        "skills": "Python, SQL, FastAPI, PostgreSQL, Docker",
        "seniority": "mid",
        "target_role": "Backend Python",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
