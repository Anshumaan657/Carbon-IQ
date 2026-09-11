from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import (
    DocumentStatus,
    ProjectCategory,
    ProjectStatus,
    RiskSeverity,
    VerificationStatus,
)


def _uppercase_code(value: str) -> str:
    return value.strip().upper()


def _unique_list(values: list) -> list:
    return list(dict.fromkeys(values))


class ProjectWriteBase(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=2, max_length=240)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=255)
    developer_name: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=160)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    project_type: str = Field(min_length=1, max_length=120)
    category: ProjectCategory
    registry: str = Field(min_length=1, max_length=160)
    registry_project_id: str | None = Field(default=None, max_length=255)
    methodology: str | None = Field(default=None, max_length=255)
    vintage_start: int | None = Field(default=None, ge=1900, le=2200)
    vintage_end: int | None = Field(default=None, ge=1900, le=2200)
    verification_status: VerificationStatus
    status: ProjectStatus = ProjectStatus.DRAFT
    price_per_credit: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    available_quantity: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=3
    )
    sdgs: list[int] = Field(default_factory=list, max_length=17)
    source_url: AnyHttpUrl
    data_as_of: date
    is_synthetic: bool = False

    @field_validator("country_code")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        normalized = _uppercase_code(value)
        if not normalized.isalpha():
            raise ValueError("country_code must contain two letters.")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = _uppercase_code(value)
        if not normalized.isalpha():
            raise ValueError("currency must contain three letters.")
        return normalized

    @field_validator("sdgs")
    @classmethod
    def validate_sdgs(cls, values: list[int]) -> list[int]:
        unique = _unique_list(values)
        if any(value < 1 or value > 17 for value in unique):
            raise ValueError("SDGs must be integers between 1 and 17.")
        return unique

    @model_validator(mode="after")
    def validate_periods_and_price(self) -> ProjectWriteBase:
        if (
            self.vintage_start is not None
            and self.vintage_end is not None
            and self.vintage_end < self.vintage_start
        ):
            raise ValueError("vintage_end must be greater than or equal to vintage_start.")
        if self.price_per_credit is not None and self.currency is None:
            raise ValueError("currency is required when price_per_credit is supplied.")
        return self


class ProjectCreate(ProjectWriteBase):
    pass


class ProjectUpdate(BaseModel):
    external_id: str | None = Field(default=None, min_length=1, max_length=255)
    name: str | None = Field(default=None, min_length=2, max_length=240)
    slug: str | None = Field(
        default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=255
    )
    developer_name: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, min_length=1)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=160)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    project_type: str | None = Field(default=None, min_length=1, max_length=120)
    category: ProjectCategory | None = None
    registry: str | None = Field(default=None, min_length=1, max_length=160)
    registry_project_id: str | None = Field(default=None, max_length=255)
    methodology: str | None = Field(default=None, max_length=255)
    vintage_start: int | None = Field(default=None, ge=1900, le=2200)
    vintage_end: int | None = Field(default=None, ge=1900, le=2200)
    verification_status: VerificationStatus | None = None
    status: ProjectStatus | None = None
    price_per_credit: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    available_quantity: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=3
    )
    sdgs: list[int] | None = Field(default=None, max_length=17)
    source_url: AnyHttpUrl | None = None
    data_as_of: date | None = None
    is_synthetic: bool | None = None

    @field_validator("country_code")
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = _uppercase_code(value)
        if not normalized.isalpha():
            raise ValueError("country_code must contain two letters.")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = _uppercase_code(value)
        if not normalized.isalpha():
            raise ValueError("currency must contain three letters.")
        return normalized

    @field_validator("sdgs")
    @classmethod
    def validate_sdgs(cls, values: list[int] | None) -> list[int] | None:
        if values is None:
            return None
        unique = _unique_list(values)
        if any(value < 1 or value > 17 for value in unique):
            raise ValueError("SDGs must be integers between 1 and 17.")
        return unique


class ScoreSummary(BaseModel):
    carboniq_score: float | None = None
    quality_score: float | None = None
    impact_score: float | None = None
    risk_score: float | None = None
    confidence: float | None = None
    methodology_version: str | None = None
    calculated_at: datetime | None = None


class CreditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vintage: int
    quantity_available: float
    price_per_credit: float
    currency: str
    delivery_date: date | None
    data_as_of: date


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: str
    title: str
    source_url: str
    published_at: date | None
    retrieved_at: datetime
    status: DocumentStatus
    page_count: int | None


class RiskSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    severity: RiskSeverity
    title: str
    message: str
    requires_review: bool
    detected_at: datetime


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    name: str
    developer_name: str
    country_code: str
    region: str | None
    project_type: str
    category: ProjectCategory
    registry: str
    methodology: str | None
    vintage_start: int | None
    vintage_end: int | None
    price_per_credit: float | None
    currency: str | None
    available_quantity: float | None
    verification_status: VerificationStatus
    status: ProjectStatus
    carboniq_score: float | None = None
    impact_score: float | None = None
    risk_score: float | None = None
    confidence: float | None = None
    data_as_of: date
    is_synthetic: bool


class ProjectDetail(ProjectSummary):
    slug: str
    description: str
    latitude: float | None
    longitude: float | None
    registry_project_id: str | None
    sdgs: list[int]
    source_url: str
    created_at: datetime
    updated_at: datetime
    latest_score: ScoreSummary | None = None
    active_risk_signals: list[RiskSignalResponse] = Field(default_factory=list)
    inventory: list[CreditResponse] = Field(default_factory=list)
    documents: list[DocumentResponse] = Field(default_factory=list)


class ProjectPage(BaseModel):
    items: list[ProjectSummary]
    page: int
    page_size: int
    total: int
    total_pages: int


class ProjectCompareRequest(BaseModel):
    project_ids: list[UUID] = Field(min_length=2, max_length=4)

    @field_validator("project_ids")
    @classmethod
    def unique_project_ids(cls, values: list[UUID]) -> list[UUID]:
        if len(set(values)) != len(values):
            raise ValueError("project_ids must contain between two and four unique IDs.")
        return values


class ProjectCompareResponse(BaseModel):
    items: list[ProjectDetail]
