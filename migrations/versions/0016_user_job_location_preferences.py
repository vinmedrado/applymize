"""user job location preferences

Revision ID: 0016_user_job_location_preferences
Revises: 0015_career_ai_conversations
Create Date: 2026-05-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0016_user_location"
down_revision = "0015_career_ai_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("job_country", sa.String(length=120), nullable=False, server_default="Brasil"))
    op.add_column("user_profiles", sa.Column("job_state", sa.String(length=120), nullable=False, server_default="São Paulo"))
    op.add_column("user_profiles", sa.Column("job_state_code", sa.String(length=20), nullable=False, server_default="SP"))
    op.add_column("user_profiles", sa.Column("job_cities", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("user_profiles", sa.Column("job_all_cities", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("user_profiles", sa.Column("job_remote_preference", sa.String(length=50), nullable=False, server_default="any"))
    op.add_column("user_profiles", sa.Column("job_city_code", sa.String(length=50), nullable=False, server_default="5211323"))


def downgrade() -> None:
    op.drop_column("user_profiles", "job_city_code")
    op.drop_column("user_profiles", "job_remote_preference")
    op.drop_column("user_profiles", "job_all_cities")
    op.drop_column("user_profiles", "job_cities")
    op.drop_column("user_profiles", "job_state_code")
    op.drop_column("user_profiles", "job_state")
    op.drop_column("user_profiles", "job_country")
