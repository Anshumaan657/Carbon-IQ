from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import RiskSeverity

if TYPE_CHECKING:
    from app.models.project import Project


SCORE_RANGE_CONSTRAINTS = tuple(
    CheckConstraint(
        f"{field} IS NULL OR {field} BETWEEN 0 AND 100",
        name=f"{field}_range",
    )
    for field in (
        "integrity_score",
        "permanence_score",
        "verification_score",
        "co_benefits_score",
        "value_score",
        "delivery_score",
        "compatibility_score",
        "quality_score",
        "impact_score",
        "risk_score",
        "carboniq_score",
    )
)


class ProjectScore(Base):
    __tablename__ = "project_scores"
    __table_args__ = (
        *SCORE_RANGE_CONSTRAINTS,
        CheckConstraint("confidence BETWEEN 0 AND 1", name="confidence_range"),
        UniqueConstraint(
            "project_id", "methodology_version", name="uq_project_scores_project_methodology"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    integrity_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    permanence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    verification_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    co_benefits_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    value_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    delivery_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    compatibility_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    impact_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    carboniq_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3))
    explanation: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    methodology_version: Mapped[str] = mapped_column(String(40))
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    project: Mapped[Project] = relationship(back_populates="scores")


class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[RiskSeverity] = mapped_column(
        Enum(
            RiskSeverity,
            name="risk_severity",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    rule_version: Mapped[str] = mapped_column(String(40))
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship(back_populates="risk_signals")
