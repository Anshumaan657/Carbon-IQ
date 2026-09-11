from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import OrderStatus


class QuoteRequest(BaseModel):
    portfolio_id: UUID


class OrderCreate(BaseModel):
    portfolio_id: UUID
    acknowledge_simulation: Literal[True]
    simulate_retirement: bool = False


class QuoteItemResponse(BaseModel):
    credit_id: UUID
    project_id: UUID
    project_name: str
    vintage: int
    quantity: float
    unit_price: float
    line_total: float
    currency: str
    quantity_available: float


class QuoteResponse(BaseModel):
    portfolio_id: UUID
    items: list[QuoteItemResponse]
    total_cost: float
    total_credits: float
    currency: str
    expires_at: datetime
    disclaimer: str


class OrderItemResponse(BaseModel):
    id: UUID
    credit_id: UUID
    project_id: UUID
    project_name: str
    vintage: int
    quantity: float
    unit_price_snapshot: float
    line_total_snapshot: float
    currency: str


class CertificateResponse(BaseModel):
    reference: str
    issued_at: datetime
    quantity: float
    statement: str


class OrderResponse(BaseModel):
    id: UUID
    reference: str
    portfolio_id: UUID
    status: OrderStatus
    total_cost_snapshot: float
    total_credits_snapshot: float
    currency: str
    disclaimer_version: str
    created_at: datetime
    cancelled_at: datetime | None
    items: list[OrderItemResponse]
    simulated_retirement_certificate: CertificateResponse | None


class ReportRiskSignal(BaseModel):
    code: str
    severity: str
    title: str
    message: str
    rule_version: str


class ReportAllocation(BaseModel):
    credit_id: UUID
    project_id: UUID
    project_name: str
    vintage: int
    quantity: float
    unit_price_snapshot: float
    line_total_snapshot: float
    allocation_percent: float
    registry: str | None
    methodology: str | None
    source_url: str | None
    data_as_of: date | None
    carboniq_score: float | None
    quality_score: float | None
    risk_score: float | None
    score_methodology_version: str | None
    risk_signals: list[ReportRiskSignal]


class OrderReportResponse(BaseModel):
    report_version: str
    generated_at: datetime
    order_id: UUID
    order_reference: str
    order_status: OrderStatus
    order_created_at: datetime
    cancelled_at: datetime | None
    buyer_organization: str
    currency: str
    total_cost_snapshot: float
    total_credits: float
    estimated_carbon_impact_tonnes: float
    allocations: list[ReportAllocation]
    simulated_retirement_certificate: CertificateResponse | None
    limitations: list[str]
    disclaimer: str
