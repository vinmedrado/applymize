"""notification logs

Revision ID: 0005_notification_logs
Revises: 0003_user_profile_resume_engine
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_notification_logs"
down_revision = "0003_user_profile_resume_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
        sa.UniqueConstraint("tenant_id", "user_id", "job_id", "channel", name="uq_notification_log_once_per_channel"),
    )
    op.create_index("ix_notification_logs_tenant_id", "notification_logs", ["tenant_id"])
    op.create_index("ix_notification_logs_user_id", "notification_logs", ["user_id"])
    op.create_index("ix_notification_logs_channel", "notification_logs", ["channel"])
    op.create_index("ix_notification_logs_status", "notification_logs", ["status"])


def downgrade() -> None:
    op.drop_table("notification_logs")
