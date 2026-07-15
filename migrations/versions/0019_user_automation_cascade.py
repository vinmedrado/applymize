"""cascade user deletion into automation tables

Revision ID: 0019_user_automation_cascade
Revises: 0018_profile_education_languages
Create Date: 2026-07-15
"""

from alembic import op


revision = "0019_user_automation_cascade"
down_revision = "0018_profile_education_languages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "automation_settings_user_id_fkey",
        "automation_settings",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "automation_settings_user_id_fkey",
        "automation_settings",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "job_notifications_user_id_fkey",
        "job_notifications",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "job_notifications_user_id_fkey",
        "job_notifications",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "job_notifications_user_id_fkey",
        "job_notifications",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "job_notifications_user_id_fkey",
        "job_notifications",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(
        "automation_settings_user_id_fkey",
        "automation_settings",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "automation_settings_user_id_fkey",
        "automation_settings",
        "users",
        ["user_id"],
        ["id"],
    )
