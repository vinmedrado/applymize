from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("tenant_id", "source", "external_id", name="uq_jobs_tenant_source_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="manual", nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    title_original: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    company: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    url: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_original: Mapped[str] = mapped_column(Text, default="", nullable=False)
    requirements: Mapped[str] = mapped_column(Text, default="", nullable=False)
    seniority: Mapped[str] = mapped_column(String(80), default="unspecified", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(80), default="full_time", nullable=False)
    salary_min: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    salary_max: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="job", cascade="all, delete-orphan")
    match_scores = relationship("MatchScore", back_populates="job", cascade="all, delete-orphan")
