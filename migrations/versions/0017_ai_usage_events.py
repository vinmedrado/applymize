"""ai usage events for daily limits
Revision ID: 0017_ai_usage_events
Revises: 0016_user_location
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa
revision = "0017_ai_usage_events"
down_revision = "0016_user_location"
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.create_table("ai_usage_events", sa.Column("id", sa.Integer(), nullable=False), sa.Column("tenant_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("feature", sa.String(length=80), nullable=False), sa.Column("provider", sa.String(length=80), nullable=False, server_default=""), sa.Column("model", sa.String(length=120), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_usage_events_tenant_id", "ai_usage_events", ["tenant_id"], unique=False)
    op.create_index("ix_ai_usage_events_user_id", "ai_usage_events", ["user_id"], unique=False)
    op.create_index("ix_ai_usage_events_tenant_user_feature_created", "ai_usage_events", ["tenant_id", "user_id", "feature", "created_at"], unique=False)
def downgrade() -> None:
    op.drop_index("ix_ai_usage_events_tenant_user_feature_created", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_user_id", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_tenant_id", table_name="ai_usage_events")
    op.drop_table("ai_usage_events")
