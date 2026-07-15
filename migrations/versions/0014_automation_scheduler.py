"""automation scheduler settings and job notifications

Revision ID: 0014_automation_scheduler
Revises: 0013_career_metrics_decisions
Create Date: 2026-05-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0014_automation_scheduler"
down_revision = "0013_career_metrics_decisions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "automation_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="interval"),
        sa.Column("interval_minutes", sa.Integer(), nullable=True),
        sa.Column("times", sa.JSON(), nullable=True),
        sa.Column("window_start", sa.Time(), nullable=True),
        sa.Column("window_end", sa.Time(), nullable=True),
        sa.Column("last_run", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_automation_settings_user_id"), "automation_settings", ["user_id"], unique=False)
    op.create_index(op.f("ix_automation_settings_enabled"), "automation_settings", ["enabled"], unique=False)

    op.create_table(
        "job_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_job_notifications_user_job"),
    )
    op.create_index(op.f("ix_job_notifications_user_id"), "job_notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_job_notifications_job_id"), "job_notifications", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_notifications_job_id"), table_name="job_notifications")
    op.drop_index(op.f("ix_job_notifications_user_id"), table_name="job_notifications")
    op.drop_table("job_notifications")

    op.drop_index(op.f("ix_automation_settings_enabled"), table_name="automation_settings")
    op.drop_index(op.f("ix_automation_settings_user_id"), table_name="automation_settings")
    op.drop_table("automation_settings")
