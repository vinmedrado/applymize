from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class WhatsAppSession(Base):
    __tablename__ = "whatsapp_sessions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_whatsapp_sessions_tenant_user"),
        UniqueConstraint("instance_name", name="uq_whatsapp_sessions_instance_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    instance_name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="not_configured", nullable=False)
    qrcode: Mapped[str] = mapped_column(Text, default="", nullable=False)
    qrcode_type: Mapped[str] = mapped_column(String(30), default="none", nullable=False)
    connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_error: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_qr_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
