"""user profile resume engine

Revision ID: 0003_user_profile_resume_engine
Revises: 0002_application_agent
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_user_profile_resume_engine"
down_revision = "0002_application_agent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("professional_title", sa.String(255), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("work_preferences", sa.Text(), nullable=False, server_default=""),
        sa.Column("salary_expectation", sa.Float(), nullable=False, server_default="0"),
        sa.Column("phone", sa.String(80), nullable=False, server_default=""),
        sa.Column("email", sa.String(255), nullable=False, server_default=""),
        sa.Column("resume_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("completeness", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_user_profiles_tenant_user"),
    )
    op.create_index("ix_user_profiles_tenant_id", "user_profiles", ["tenant_id"])
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])

    for table, columns in {
        "user_skills": [
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("level", sa.String(80), nullable=False, server_default="intermediate"),
            sa.Column("category", sa.String(120), nullable=False, server_default="technical"),
        ],
        "user_experiences": [
            sa.Column("company", sa.String(255), nullable=False),
            sa.Column("role", sa.String(255), nullable=False),
            sa.Column("start_date", sa.String(50), nullable=False, server_default=""),
            sa.Column("end_date", sa.String(50), nullable=False, server_default=""),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("achievements", sa.Text(), nullable=False, server_default=""),
        ],
        "user_projects": [
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("technologies", sa.Text(), nullable=False, server_default=""),
            sa.Column("url", sa.String(1000), nullable=False, server_default=""),
        ],
        "user_education": [
            sa.Column("institution", sa.String(255), nullable=False),
            sa.Column("course", sa.String(255), nullable=False),
            sa.Column("start_date", sa.String(50), nullable=False, server_default=""),
            sa.Column("end_date", sa.String(50), nullable=False, server_default=""),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
        ],
    }.items():
        op.create_table(table,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            *columns,
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])
        op.create_index(f"ix_{table}_user_id", table, ["user_id"])

    op.create_unique_constraint("uq_user_skills_tenant_user_name", "user_skills", ["tenant_id", "user_id", "name"])

    op.create_table("resume_uploads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=False, server_default=""),
        sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("parsed_data", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_resume_uploads_tenant_id", "resume_uploads", ["tenant_id"])
    op.create_index("ix_resume_uploads_user_id", "resume_uploads", ["user_id"])


def downgrade() -> None:
    op.drop_table("resume_uploads")
    op.drop_table("user_education")
    op.drop_table("user_projects")
    op.drop_table("user_experiences")
    op.drop_table("user_skills")
    op.drop_table("user_profiles")
