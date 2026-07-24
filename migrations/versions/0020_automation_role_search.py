"""add per-user automation role search preferences

Revision ID: 0020_automation_role_search
Revises: 0019_user_automation_cascade
Create Date: 2026-07-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0020_automation_role_search"
down_revision = "0019_user_automation_cascade"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("automation_settings", sa.Column("search_terms", sa.JSON(), nullable=True))
    op.add_column(
        "automation_settings",
        sa.Column("min_role_relevance", sa.Float(), nullable=False, server_default="55"),
    )
    op.add_column(
        "provider_runs",
        sa.Column("search_term", sa.String(length=255), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("provider_runs", "search_term")
    op.drop_column("automation_settings", "min_role_relevance")
    op.drop_column("automation_settings", "search_terms")
