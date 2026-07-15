"""application agent queue

Revision ID: 0002_application_agent
Revises: 0001_initial_schema
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_application_agent"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_queue_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("evaluation_grade", sa.String(2), nullable=False, server_default="C"),
        sa.Column("generated_cv", sa.Text(), nullable=False, server_default=""),
        sa.Column("cover_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(40), nullable=False, server_default="queued"),
        sa.Column("failure_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("tenant_id", "user_id", "job_id", name="uq_application_queue_tenant_user_job"),
    )
    op.create_index("ix_application_queue_items_tenant_id", "application_queue_items", ["tenant_id"])
    op.create_index("ix_application_queue_items_user_id", "application_queue_items", ["user_id"])
    op.create_index("ix_application_queue_items_job_id", "application_queue_items", ["job_id"])
    op.create_index("ix_application_queue_items_status", "application_queue_items", ["status"])

    op.create_table(
        "application_agent_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("application_queue_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_application_agent_events_tenant_id", "application_agent_events", ["tenant_id"])
    op.create_index("ix_application_agent_events_user_id", "application_agent_events", ["user_id"])
    op.create_index("ix_application_agent_events_queue_item_id", "application_agent_events", ["queue_item_id"])


def downgrade() -> None:
    op.drop_table("application_agent_events")
    op.drop_table("application_queue_items")
