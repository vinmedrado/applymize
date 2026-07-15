"""career ai persistent conversations

Revision ID: 0015_career_ai_conversations
Revises: 0014_automation_scheduler
Create Date: 2026-05-06
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_career_ai_conversations"
down_revision = "0014_automation_scheduler"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "career_ai_conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Nova conversa"),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_ai_conversations_tenant_id", "career_ai_conversations", ["tenant_id"], unique=False)
    op.create_index("ix_career_ai_conversations_user_id", "career_ai_conversations", ["user_id"], unique=False)
    op.create_index("ix_career_ai_conversations_tenant_user_updated", "career_ai_conversations", ["tenant_id", "user_id", "updated_at"], unique=False)

    op.create_table(
        "career_ai_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=24), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("model", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("tokens_estimated", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conversation_id"], ["career_ai_conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_ai_messages_tenant_id", "career_ai_messages", ["tenant_id"], unique=False)
    op.create_index("ix_career_ai_messages_user_id", "career_ai_messages", ["user_id"], unique=False)
    op.create_index("ix_career_ai_messages_conversation_id", "career_ai_messages", ["conversation_id"], unique=False)
    op.create_index("ix_career_ai_messages_conversation_created", "career_ai_messages", ["conversation_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_career_ai_messages_conversation_created", table_name="career_ai_messages")
    op.drop_index("ix_career_ai_messages_conversation_id", table_name="career_ai_messages")
    op.drop_index("ix_career_ai_messages_user_id", table_name="career_ai_messages")
    op.drop_index("ix_career_ai_messages_tenant_id", table_name="career_ai_messages")
    op.drop_table("career_ai_messages")
    op.drop_index("ix_career_ai_conversations_tenant_user_updated", table_name="career_ai_conversations")
    op.drop_index("ix_career_ai_conversations_user_id", table_name="career_ai_conversations")
    op.drop_index("ix_career_ai_conversations_tenant_id", table_name="career_ai_conversations")
    op.drop_table("career_ai_conversations")
