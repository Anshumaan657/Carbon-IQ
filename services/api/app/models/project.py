from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ProjectCategory, ProjectStatus, VerificationStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.credit import CarbonCredit
    from app.models.document import ProjectDocument
    from app.models.recommendation import RecommendationItem
    from app.models.score import ProjectScore, RiskSignal


class Project(TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("registry", "registry_project_id", name="uq_projects_registry_project_id"),
        CheckConstraint("char_length(name) BETWEEN 2 AND 240", name="name_length"),
        CheckConstraint("char_length(country_code) = 2", name="country_code_length"),
        CheckConstraint("latitude IS NULL OR latitude BETWEEN -90 AND 90", name="latitude_range"),
        CheckConstraint("longitude IS NULL OR longitude BETWEEN -180 AND 180", name="longitude_range"),
        CheckConstraint(
            "vintage_end IS NULL OR vintage_start IS NULL OR vintage_end >= vintage_start",
            name="vintage_period_order",
        ),
        CheckConstraint(
            "price_per_credit IS NULL OR price_per_credit >= 0", name="price_non_negative"
        ),
        CheckConstraint(
            "available_quantity IS NULL OR available_quantity >= 0",
            name="quantity_non_negative",
        ),
        CheckConstraint(
            "price_per_credit IS NULL OR currency IS NOT NULL", name="priced_currency_required"
        ),
        CheckConstraint("currency IS NULL OR char_length(currency) = 3", name="currency_length"),
        Index("ix_projects_catalogue", "status", "category", "country_code"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    external_id: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(240), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    developer_name: Mapped[str] = mapped_column(String(240), index=True)
    description: Mapped[str] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    region: Mapped[str | None] = mapped_column(String(160), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    project_type: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[ProjectCategory] = mapped_column(
        Enum(
            ProjectCategory,
            name="project_category",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    registry: Mapped[str] = mapped_column(String(160), index=True)
    registry_project_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    methodology: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vintage_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vintage_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="project_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ProjectStatus.UNKNOWN,
        server_default=ProjectStatus.UNKNOWN.value,
        index=True,
    )
    price_per_credit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    available_quantity: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    sdgs: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list, server_default="{}")
    source_url: Mapped[str] = mapped_column(Text)
    data_as_of: Mapped[date] = mapped_column(Date, index=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    credits: Mapped[list[CarbonCredit]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    documents: Mapped[list[ProjectDocument]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    scores: Mapped[list[ProjectScore]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    risk_signals: Mapped[list[RiskSignal]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    recommendation_items: Mapped[list[RecommendationItem]] = relationship(
        back_populates="project"
    )
