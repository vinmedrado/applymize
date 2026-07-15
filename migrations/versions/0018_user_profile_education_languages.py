"""add education and language fields to user profile

Revision ID: 0018_profile_education_languages
Revises: 0017_ai_usage_events
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa


revision = "0018_profile_education_languages"
down_revision = "0017_ai_usage_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("education_level", sa.String(length=120), nullable=False, server_default="Superior completo"))
    op.add_column("user_profiles", sa.Column("english_level", sa.String(length=80), nullable=False, server_default="Intermediário"))
    op.add_column("user_profiles", sa.Column("spanish_level", sa.String(length=80), nullable=False, server_default="Nenhum"))


def downgrade() -> None:
    op.drop_column("user_profiles", "spanish_level")
    op.drop_column("user_profiles", "english_level")
    op.drop_column("user_profiles", "education_level")
