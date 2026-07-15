"""whatsapp sessions provider runs ml base

Revision ID: 0010_whatsapp_sessions_provider_runs_ml_base
Revises: 0009_whatsapp_connections
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0010_whatsapp_sessions"
down_revision = "0009_whatsapp_connections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instance_name", sa.String(160), nullable=False),
        sa.Column("phone_number", sa.String(32), nullable=False, server_default=""),
        sa.Column("status", sa.String(50), nullable=False, server_default="not_configured"),
        sa.Column("qrcode", sa.Text(), nullable=False, server_default=""),
        sa.Column("qrcode_type", sa.String(30), nullable=False, server_default="none"),
        sa.Column("connected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_error", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("connected_at", sa.DateTime(), nullable=True),
        sa.Column("last_qr_at", sa.DateTime(), nullable=True),
        sa.Column("disconnected_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_whatsapp_sessions_tenant_user"),
        sa.UniqueConstraint("instance_name", name="uq_whatsapp_sessions_instance_name"),
    )
    op.create_index("ix_whatsapp_sessions_tenant_id", "whatsapp_sessions", ["tenant_id"])
    op.create_index("ix_whatsapp_sessions_user_id", "whatsapp_sessions", ["user_id"])
    op.create_index("ix_whatsapp_sessions_instance_name", "whatsapp_sessions", ["instance_name"])

    op.create_table(
        "provider_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="running"),
        sa.Column("requested_limit", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("collected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Text(), nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_provider_runs_tenant_id", "provider_runs", ["tenant_id"])
    op.create_index("ix_provider_runs_provider", "provider_runs", ["provider"])

    op.create_table(
        "application_feedbacks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feedback_type", sa.String(60), nullable=False),
        sa.Column("outcome", sa.String(80), nullable=False, server_default=""),
        sa.Column("rating", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "user_id", "application_id", name="uq_application_feedback_tenant_user_application"),
    )
    op.create_index("ix_application_feedbacks_tenant_id", "application_feedbacks", ["tenant_id"])
    op.create_index("ix_application_feedbacks_user_id", "application_feedbacks", ["user_id"])
    op.create_index("ix_application_feedbacks_feedback_type", "application_feedbacks", ["feedback_type"])

    op.create_table(
        "application_ml_feature_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("label", sa.String(80), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_application_ml_feature_snapshots_tenant_id", "application_ml_feature_snapshots", ["tenant_id"])
    op.create_index("ix_application_ml_feature_snapshots_user_id", "application_ml_feature_snapshots", ["user_id"])


def downgrade() -> None:
    op.drop_table("application_ml_feature_snapshots")
    op.drop_table("application_feedbacks")
    op.drop_table("provider_runs")
    op.drop_table("whatsapp_sessions")
