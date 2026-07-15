"""job original translation fields

Revision ID: 0006_job_original_translation_fields
Revises: 0005_notification_logs
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_job_translation"
down_revision = "0005_notification_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("title_original", sa.String(255), nullable=False, server_default=""))
    op.add_column("jobs", sa.Column("description_original", sa.Text(), nullable=False, server_default=""))
    op.execute("UPDATE jobs SET title_original = title WHERE title_original = ''")
    op.execute("UPDATE jobs SET description_original = description WHERE description_original = ''")


def downgrade() -> None:
    op.drop_column("jobs", "description_original")
    op.drop_column("jobs", "title_original")
