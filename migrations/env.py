from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

from backend.core.config import settings
from backend.core.database import Base
from backend.models.tenant import Tenant
from backend.models.user import User
from backend.models.membership import Membership
from backend.models.job import Job
from backend.models.application import Application, ApplicationEvent
from backend.models.resume import Resume
from backend.models.match_score import MatchScore
from backend.models.token import RefreshToken
from backend.models.password_reset_token import PasswordResetToken
from backend.models.application_agent import ApplicationQueueItem, ApplicationAgentEvent

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

from backend.models.profile import UserProfile, UserSkill, UserExperience, UserProject, UserEducation, ResumeUpload

from backend.models.notification import NotificationLog

from backend.models.radar import JobRadarRun

from backend.models.user_settings import UserSettings

from backend.models.career import CareerMetricSnapshot, DecisionHistory

from backend.models.automation import AutomationSettings, JobNotification
