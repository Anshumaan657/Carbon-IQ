from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.portfolio import PortfolioItem
    from app.models.project import Project


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"
    __table_args__ = (
        UniqueConstraint("project_id", "vintage", name="uq_carbon_credits_project_vintage"),
        CheckConstraint("vintage BETWEEN 1900 AND 2200", name="vintage_range"),
        CheckConstraint("quantity_available >= 0", name="quantity_non_negative"),
        CheckConstraint("price_per_credit >= 0", name="price_non_negative"),
        CheckConstraint("char_length(currency) = 3", name="currency_length"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    vintage: Mapped[int] = mapped_column(Integer)
    quantity_available: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    price_per_credit: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_as_of: Mapped[date] = mapped_column(Date)

    project: Mapped[Project] = relationship(back_populates="credits")
    portfolio_items: Mapped[list[PortfolioItem]] = relationship(back_populates="credit")
