"""whatsapp connections

Revision ID: 0009_whatsapp_connections
Revises: 0008_user_settings_onboarding
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0009_whatsapp_connections"
down_revision = "0008_user_settings_onboarding"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instance_id", sa.String(160), nullable=False),
        sa.Column("phone_number", sa.String(32), nullable=False, server_default=""),
        sa.Column("status", sa.String(50), nullable=False, server_default="nao_configurado"),
        sa.Column("qr_code", sa.Text(), nullable=False, server_default=""),
        sa.Column("qr_type", sa.String(30), nullable=False, server_default="none"),
        sa.Column("last_qr_at", sa.DateTime(), nullable=True),
        sa.Column("connected_at", sa.DateTime(), nullable=True),
        sa.Column("disconnected_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_whatsapp_connection_tenant_user"),
        sa.UniqueConstraint("instance_id", name="uq_whatsapp_connection_instance_id"),
    )
    op.create_index("ix_whatsapp_connections_tenant_id", "whatsapp_connections", ["tenant_id"])
    op.create_index("ix_whatsapp_connections_user_id", "whatsapp_connections", ["user_id"])
    op.create_index("ix_whatsapp_connections_instance_id", "whatsapp_connections", ["instance_id"])


def downgrade() -> None:
    op.drop_table("whatsapp_connections")
