from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ProjectCategory, RiskTolerance, UserRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio, SimulatedOrder
    from app.models.recommendation import RecommendationRun


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("char_length(organization_name) BETWEEN 2 AND 160", name="organization_name_length"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    organization_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda enum: [item.value for item in enum]),
        default=UserRole.BUYER,
        server_default=UserRole.BUYER.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

    preferences: Mapped[list[BuyerPreference]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    recommendation_runs: Mapped[list[RecommendationRun]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    portfolios: Mapped[list[Portfolio]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    simulated_orders: Mapped[list[SimulatedOrder]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """A hashed, revocable refresh token. Raw tokens are never persisted."""

    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class BuyerPreference(TimestampMixin, Base):
    __tablename__ = "buyer_preferences"
    __table_args__ = (
        CheckConstraint("char_length(name) BETWEEN 1 AND 160", name="name_length"),
        CheckConstraint("budget > 0", name="budget_positive"),
        CheckConstraint("required_credits > 0", name="required_credits_positive"),
        CheckConstraint("char_length(currency) = 3", name="currency_length"),
        CheckConstraint(
            "minimum_quality_score IS NULL OR minimum_quality_score BETWEEN 0 AND 100",
            name="minimum_quality_score_range",
        ),
        CheckConstraint(
            "delivery_end IS NULL OR delivery_start IS NULL OR delivery_end >= delivery_start",
            name="delivery_period_order",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    budget: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    required_credits: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    risk_tolerance: Mapped[RiskTolerance] = mapped_column(
        Enum(
            RiskTolerance,
            name="risk_tolerance",
            values_callable=lambda enum: [item.value for item in enum],
        )
    )
    preferred_project_types: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)), default=list, server_default="{}"
    )
    preferred_countries: Mapped[list[str]] = mapped_column(
        ARRAY(String(2)), default=list, server_default="{}"
    )
    preferred_category: Mapped[ProjectCategory | None] = mapped_column(
        Enum(
            ProjectCategory,
            name="project_category",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=True,
    )
    sdg_priorities: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), default=list, server_default="{}"
    )
    minimum_quality_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    delivery_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped[User] = relationship(back_populates="preferences")
    recommendation_runs: Mapped[list[RecommendationRun]] = relationship(
        back_populates="preference"
    )
    portfolios: Mapped[list[Portfolio]] = relationship(back_populates="preference")
