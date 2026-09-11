from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import OrderStatus, PortfolioStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.credit import CarbonCredit
    from app.models.user import BuyerPreference, User


class Portfolio(TimestampMixin, Base):
    __tablename__ = "portfolios"
    __table_args__ = (
        CheckConstraint("char_length(name) BETWEEN 2 AND 160", name="name_length"),
        CheckConstraint("char_length(currency) = 3", name="currency_length"),
        CheckConstraint("total_cost >= 0", name="total_cost_non_negative"),
        CheckConstraint("total_credits >= 0", name="total_credits_non_negative"),
        CheckConstraint(
            "average_quality IS NULL OR average_quality BETWEEN 0 AND 100",
            name="average_quality_range",
        ),
        CheckConstraint(
            "portfolio_risk IS NULL OR portfolio_risk BETWEEN 0 AND 100",
            name="portfolio_risk_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    preference_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("buyer_preferences.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[PortfolioStatus] = mapped_column(
        Enum(
            PortfolioStatus,
            name="portfolio_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=PortfolioStatus.DRAFT,
        server_default=PortfolioStatus.DRAFT.value,
    )
    currency: Mapped[str] = mapped_column(String(3))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, server_default="0")
    total_credits: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), default=0, server_default="0"
    )
    average_quality: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    portfolio_risk: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    optimizer_version: Mapped[str | None] = mapped_column(String(40), nullable=True)

    user: Mapped[User] = relationship(back_populates="portfolios")
    preference: Mapped[BuyerPreference | None] = relationship(back_populates="portfolios")
    items: Mapped[list[PortfolioItem]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )
    simulated_order: Mapped[SimulatedOrder | None] = relationship(
        back_populates="portfolio", uselist=False
    )


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "credit_id", name="uq_portfolio_items_portfolio_credit"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price_snapshot >= 0", name="unit_price_non_negative"),
        CheckConstraint("allocation_percent BETWEEN 0 AND 100", name="allocation_percent_range"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    credit_id: Mapped[UUID] = mapped_column(
        ForeignKey("carbon_credits.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    allocation_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    portfolio: Mapped[Portfolio] = relationship(back_populates="items")
    credit: Mapped[CarbonCredit] = relationship(back_populates="portfolio_items")


class SimulatedOrder(Base):
    __tablename__ = "simulated_orders"
    __table_args__ = (
        UniqueConstraint("portfolio_id", name="uq_simulated_orders_portfolio_id"),
        CheckConstraint("total_cost_snapshot >= 0", name="total_cost_non_negative"),
        CheckConstraint("total_credits_snapshot > 0", name="total_credits_positive"),
        CheckConstraint(
            "retirement_quantity IS NULL OR retirement_quantity > 0",
            name="retirement_quantity_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    reference: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    portfolio_id: Mapped[UUID] = mapped_column(
        ForeignKey("portfolios.id", ondelete="RESTRICT")
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=OrderStatus.SIMULATED,
        server_default=OrderStatus.SIMULATED.value,
    )
    total_cost_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_credits_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    disclaimer_version: Mapped[str] = mapped_column(String(40))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    certificate_reference: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    certificate_issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retirement_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="simulated_orders")
    portfolio: Mapped[Portfolio] = relationship(back_populates="simulated_order")
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """Immutable credit, project, quantity, and price snapshot for a simulated order."""

    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "credit_id", name="uq_order_items_order_credit"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price_snapshot >= 0", name="unit_price_non_negative"),
        CheckConstraint("line_total_snapshot >= 0", name="line_total_non_negative"),
        CheckConstraint("char_length(currency) = 3", name="currency_length"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("simulated_orders.id", ondelete="CASCADE"), index=True
    )
    credit_id: Mapped[UUID] = mapped_column(
        ForeignKey("carbon_credits.id", ondelete="RESTRICT"), index=True
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), index=True
    )
    project_name_snapshot: Mapped[str] = mapped_column(String(240))
    vintage: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    line_total_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    registry_snapshot: Mapped[str | None] = mapped_column(String(160), nullable=True)
    methodology_snapshot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_as_of_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)
    carboniq_score_snapshot: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    quality_score_snapshot: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    risk_score_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    score_methodology_version_snapshot: Mapped[str | None] = mapped_column(
        String(40), nullable=True
    )
    risk_signals_snapshot: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    order: Mapped[SimulatedOrder] = relationship(back_populates="items")
    credit: Mapped[CarbonCredit] = relationship(back_populates="order_items")
