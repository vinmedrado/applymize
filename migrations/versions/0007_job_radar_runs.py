"""job radar runs

Revision ID: 0007_job_radar_runs
Revises: 0006_job_original_translation_fields
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_job_radar_runs"
down_revision = "0006_job_translation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_radar_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False, server_default="all"),
        sa.Column("total_ingested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("high_priority_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notified_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(80), nullable=False, server_default="completed"),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_radar_runs_tenant_id", "job_radar_runs", ["tenant_id"])
    op.create_index("ix_job_radar_runs_user_id", "job_radar_runs", ["user_id"])


def downgrade() -> None:
    op.drop_table("job_radar_runs")
