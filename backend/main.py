from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import models  # noqa: F401
from backend.api import routes_applications, routes_auth, routes_cv, routes_interview, routes_jobs, routes_matching, routes_providers, routes_strategy, routes_application_agent, routes_profile, routes_ats, routes_notifications, routes_whatsapp, routes_cover_letter, routes_followup, routes_analytics, routes_skill_gap, routes_radar, routes_user, routes_dashboard, routes_automation, routes_career_ai, routes_linkedin_analyzer, routes_applymize_fit, routes_billing, routes_admin, routes_recruiter
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.exceptions import AppError, app_error_handler, integrity_error_handler, unhandled_error_handler
from backend.core.logging import configure_logging, get_logger
from backend.middlewares.rate_limit import RateLimitMiddleware
from backend.services.automation_scheduler import start_automation_scheduler

configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        started = start_automation_scheduler()
        logger.info("automation_scheduler_startup_checked started=%s", started)
    except Exception as exc:
        logger.error("automation_scheduler_startup_failed error=%s", exc, exc_info=True)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

origins = settings.cors_origin_list()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(routes_auth.router)
app.include_router(routes_jobs.router)
app.include_router(routes_providers.router)
app.include_router(routes_applications.router)
app.include_router(routes_matching.router)
app.include_router(routes_strategy.router)
app.include_router(routes_application_agent.router)
app.include_router(routes_profile.router)
app.include_router(routes_ats.router)
app.include_router(routes_cv.router)
app.include_router(routes_interview.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "ok",
    }

app.include_router(routes_notifications.router)

app.include_router(routes_whatsapp.router)

app.include_router(routes_cover_letter.router)

app.include_router(routes_followup.router)

app.include_router(routes_analytics.router)

app.include_router(routes_skill_gap.router)

app.include_router(routes_radar.router)

app.include_router(routes_user.router)

app.include_router(routes_dashboard.router)

app.include_router(routes_automation.router)

app.include_router(routes_career_ai.router)

app.include_router(routes_linkedin_analyzer.router)
app.include_router(routes_linkedin_analyzer.public_router)
app.include_router(routes_applymize_fit.router)
app.include_router(routes_billing.router)
app.include_router(routes_admin.router)
app.include_router(routes_recruiter.router)
app.include_router(routes_billing.public_router)
