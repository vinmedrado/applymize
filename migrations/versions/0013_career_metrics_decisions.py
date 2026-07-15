"""career metrics and decision history

Revision ID: 0013_career_metrics_decisions
Revises: 0012_job_alert_preferences
Create Date: 2026-05-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0013_career_metrics_decisions"
down_revision = "0012_job_alert_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "career_metric_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.String(length=10), nullable=False),
        sa.Column("total_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("applications_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_applications", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ranked_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_match_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("high_match_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("career_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", "snapshot_date", name="uq_career_snapshot_day"),
    )
    op.create_index(op.f("ix_career_metric_snapshots_tenant_id"), "career_metric_snapshots", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_career_metric_snapshots_user_id"), "career_metric_snapshots", ["user_id"], unique=False)
    op.create_index(op.f("ix_career_metric_snapshots_snapshot_date"), "career_metric_snapshots", ["snapshot_date"], unique=False)

    op.create_table(
        "decision_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("decision_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decision_history_tenant_id"), "decision_history", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_decision_history_user_id"), "decision_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_decision_history_job_id"), "decision_history", ["job_id"], unique=False)
    op.create_index(op.f("ix_decision_history_application_id"), "decision_history", ["application_id"], unique=False)
    op.create_index(op.f("ix_decision_history_decision_type"), "decision_history", ["decision_type"], unique=False)
    op.create_index(op.f("ix_decision_history_created_at"), "decision_history", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_decision_history_created_at"), table_name="decision_history")
    op.drop_index(op.f("ix_decision_history_decision_type"), table_name="decision_history")
    op.drop_index(op.f("ix_decision_history_application_id"), table_name="decision_history")
    op.drop_index(op.f("ix_decision_history_job_id"), table_name="decision_history")
    op.drop_index(op.f("ix_decision_history_user_id"), table_name="decision_history")
    op.drop_index(op.f("ix_decision_history_tenant_id"), table_name="decision_history")
    op.drop_table("decision_history")
    op.drop_index(op.f("ix_career_metric_snapshots_snapshot_date"), table_name="career_metric_snapshots")
    op.drop_index(op.f("ix_career_metric_snapshots_user_id"), table_name="career_metric_snapshots")
    op.drop_index(op.f("ix_career_metric_snapshots_tenant_id"), table_name="career_metric_snapshots")
    op.drop_table("career_metric_snapshots")
