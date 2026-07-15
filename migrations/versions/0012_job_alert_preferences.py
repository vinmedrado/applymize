"""job alert preferences

Revision ID: 0012_job_alert_preferences
Revises: 0011_password_reset_tokens
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa

revision = "0012_job_alert_preferences"
down_revision = "0011_password_reset_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_settings", sa.Column("job_alerts_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("user_settings", sa.Column("job_alert_min_priority", sa.String(length=20), nullable=False, server_default="MEDIUM"))
    op.add_column("user_settings", sa.Column("job_alert_remote_only", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("user_settings", sa.Column("job_alert_frequency", sa.String(length=20), nullable=False, server_default="immediate"))
    op.add_column("user_settings", sa.Column("job_alert_summary_mode", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("user_settings", sa.Column("job_alert_email_fallback", sa.Boolean(), nullable=False, server_default=sa.text("true")))


def downgrade() -> None:
    op.drop_column("user_settings", "job_alert_email_fallback")
    op.drop_column("user_settings", "job_alert_summary_mode")
    op.drop_column("user_settings", "job_alert_frequency")
    op.drop_column("user_settings", "job_alert_remote_only")
    op.drop_column("user_settings", "job_alert_min_priority")
    op.drop_column("user_settings", "job_alerts_enabled")
