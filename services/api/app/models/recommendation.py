from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import BuyerPreference, User


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    preference_id: Mapped[UUID] = mapped_column(
        ForeignKey("buyer_preferences.id", ondelete="RESTRICT"), index=True
    )
    engine_version: Mapped[str] = mapped_column(String(40))
    project_data_as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped[User] = relationship(back_populates="recommendation_runs")
    preference: Mapped[BuyerPreference] = relationship(back_populates="recommendation_runs")
    items: Mapped[list[RecommendationItem]] = relationship(
        back_populates="recommendation_run", cascade="all, delete-orphan"
    )


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    __table_args__ = (
        UniqueConstraint(
            "recommendation_run_id", "rank", name="uq_recommendation_items_run_rank"
        ),
        UniqueConstraint(
            "recommendation_run_id", "project_id", name="uq_recommendation_items_run_project"
        ),
        CheckConstraint("rank >= 1", name="rank_positive"),
        CheckConstraint("match_score BETWEEN 0 AND 100", name="match_score_range"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    recommendation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("recommendation_runs.id", ondelete="CASCADE"), index=True
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), index=True
    )
    rank: Mapped[int] = mapped_column(Integer)
    match_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, server_default="[]")
    trade_offs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    excluded_constraints: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]"
    )

    recommendation_run: Mapped[RecommendationRun] = relationship(back_populates="items")
    project: Mapped[Project] = relationship(back_populates="recommendation_items")
