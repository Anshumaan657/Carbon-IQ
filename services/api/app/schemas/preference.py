from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import ProjectCategory, RiskTolerance


def _unique(values: list) -> list:
    return list(dict.fromkeys(values))


class PreferenceBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    budget: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    required_credits: Decimal = Field(gt=0, max_digits=14, decimal_places=3)
    risk_tolerance: RiskTolerance
    preferred_project_types: list[str] = Field(default_factory=list)
    preferred_countries: list[str] = Field(default_factory=list)
    preferred_category: ProjectCategory | None = None
    sdg_priorities: list[int] = Field(default_factory=list, max_length=17)
    minimum_quality_score: Decimal | None = Field(default=None, ge=0, le=100)
    delivery_start: date | None = None
    delivery_end: date | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized.isalpha():
            raise ValueError("currency must contain three letters.")
        return normalized

    @field_validator("preferred_project_types")
    @classmethod
    def normalize_project_types(cls, values: list[str]) -> list[str]:
        normalized = [value.strip().lower() for value in values if value.strip()]
        return _unique(normalized)

    @field_validator("preferred_countries")
    @classmethod
    def normalize_countries(cls, values: list[str]) -> list[str]:
        normalized = [value.strip().upper() for value in values]
        if any(len(value) != 2 or not value.isalpha() for value in normalized):
            raise ValueError("Preferred countries must use two-letter country codes.")
        return _unique(normalized)

    @field_validator("sdg_priorities")
    @classmethod
    def validate_sdgs(cls, values: list[int]) -> list[int]:
        unique = _unique(values)
        if any(value < 1 or value > 17 for value in unique):
            raise ValueError("SDGs must be integers between 1 and 17.")
        return unique

    @model_validator(mode="after")
    def validate_delivery_period(self) -> PreferenceBase:
        if (
            self.delivery_start is not None
            and self.delivery_end is not None
            and self.delivery_end < self.delivery_start
        ):
            raise ValueError("delivery_end must be greater than or equal to delivery_start.")
        return self


class PreferenceCreate(PreferenceBase):
    pass


class PreferenceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    budget: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    required_credits: Decimal | None = Field(
        default=None, gt=0, max_digits=14, decimal_places=3
    )
    risk_tolerance: RiskTolerance | None = None
    preferred_project_types: list[str] | None = None
    preferred_countries: list[str] | None = None
    preferred_category: ProjectCategory | None = None
    sdg_priorities: list[int] | None = Field(default=None, max_length=17)
    minimum_quality_score: Decimal | None = Field(default=None, ge=0, le=100)
    delivery_start: date | None = None
    delivery_end: date | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized.isalpha():
            raise ValueError("currency must contain three letters.")
        return normalized

    @field_validator("preferred_project_types")
    @classmethod
    def normalize_project_types(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        return _unique([value.strip().lower() for value in values if value.strip()])

    @field_validator("preferred_countries")
    @classmethod
    def normalize_countries(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized = [value.strip().upper() for value in values]
        if any(len(value) != 2 or not value.isalpha() for value in normalized):
            raise ValueError("Preferred countries must use two-letter country codes.")
        return _unique(normalized)

    @field_validator("sdg_priorities")
    @classmethod
    def validate_sdgs(cls, values: list[int] | None) -> list[int] | None:
        if values is None:
            return None
        unique = _unique(values)
        if any(value < 1 or value > 17 for value in unique):
            raise ValueError("SDGs must be integers between 1 and 17.")
        return unique


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    budget: float
    currency: str
    required_credits: float
    risk_tolerance: RiskTolerance
    preferred_project_types: list[str]
    preferred_countries: list[str]
    preferred_category: ProjectCategory | None
    sdg_priorities: list[int]
    minimum_quality_score: float | None
    delivery_start: date | None
    delivery_end: date | None
    created_at: datetime
    updated_at: datetime
