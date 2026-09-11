from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.credit import CarbonCredit
from app.models.enums import PortfolioStatus, ProjectStatus
from app.models.portfolio import Portfolio, PortfolioItem
from app.models.project import Project
from app.models.score import ProjectScore
from app.models.user import BuyerPreference, User
from app.schemas.portfolio import (
    HoldingCreate,
    HoldingResponse,
    HoldingUpdate,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
)


router = APIRouter(prefix="/portfolios", tags=["portfolios"])
CENT = Decimal("0.01")
MILLI_CREDIT = Decimal("0.001")


def portfolio_query():
    return select(Portfolio).options(
        selectinload(Portfolio.items)
        .joinedload(PortfolioItem.credit)
        .joinedload(CarbonCredit.project)
        .selectinload(Project.scores)
    )


def get_owned_portfolio(db: Session, user_id: UUID, portfolio_id: UUID) -> Portfolio:
    portfolio = db.scalar(
        portfolio_query().where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
        )
    )
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    return portfolio


def get_holding(portfolio: Portfolio, holding_id: UUID) -> PortfolioItem:
    holding = next((item for item in portfolio.items if item.id == holding_id), None)
    if holding is None:
        raise HTTPException(status_code=404, detail="Portfolio holding not found.")
    return holding


def latest_project_score(project: Project) -> ProjectScore | None:
    return max(
        project.scores,
        key=lambda score: (score.calculated_at, str(score.id)),
        default=None,
    )


def weighted_score(items: list[PortfolioItem], attribute: str) -> Decimal | None:
    scored = []
    for item in items:
        score = latest_project_score(item.credit.project)
        value = getattr(score, attribute, None) if score else None
        if value is not None:
            scored.append((item.quantity, value))
    denominator = sum((quantity for quantity, _ in scored), Decimal("0"))
    if denominator == 0:
        return None
    result = sum((quantity * value for quantity, value in scored), Decimal("0")) / denominator
    return result.quantize(CENT, rounding=ROUND_HALF_UP)


def recalculate_portfolio(portfolio: Portfolio) -> None:
    total_credits = sum((item.quantity for item in portfolio.items), Decimal("0"))
    total_cost = sum(
        (item.quantity * item.unit_price_snapshot for item in portfolio.items),
        Decimal("0"),
    )
    portfolio.total_credits = total_credits.quantize(MILLI_CREDIT, rounding=ROUND_HALF_UP)
    portfolio.total_cost = total_cost.quantize(CENT, rounding=ROUND_HALF_UP)
    portfolio.average_quality = weighted_score(portfolio.items, "quality_score")
    portfolio.portfolio_risk = weighted_score(portfolio.items, "risk_score")
    for item in portfolio.items:
        item.allocation_percent = (
            (item.quantity * Decimal("100") / total_credits).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
            if total_credits
            else Decimal("0")
        )


def holding_response(item: PortfolioItem) -> HoldingResponse:
    score = latest_project_score(item.credit.project)
    return HoldingResponse(
        id=item.id,
        credit_id=item.credit_id,
        project_id=item.credit.project_id,
        project_name=item.credit.project.name,
        vintage=item.credit.vintage,
        quantity=float(item.quantity),
        unit_price_snapshot=float(item.unit_price_snapshot),
        line_total=float(item.quantity * item.unit_price_snapshot),
        allocation_percent=float(item.allocation_percent),
        current_quantity_available=float(item.credit.quantity_available),
        quality_score=float(score.quality_score) if score and score.quality_score is not None else None,
        risk_score=float(score.risk_score) if score and score.risk_score is not None else None,
        is_locked=item.is_locked,
    )


def portfolio_response(portfolio: Portfolio) -> PortfolioResponse:
    return PortfolioResponse(
        id=portfolio.id,
        user_id=portfolio.user_id,
        preference_id=portfolio.preference_id,
        name=portfolio.name,
        status=portfolio.status,
        currency=portfolio.currency,
        total_cost=float(portfolio.total_cost),
        total_credits=float(portfolio.total_credits),
        estimated_carbon_impact_tonnes=float(portfolio.total_credits),
        average_quality=(
            float(portfolio.average_quality) if portfolio.average_quality is not None else None
        ),
        portfolio_risk=(
            float(portfolio.portfolio_risk) if portfolio.portfolio_risk is not None else None
        ),
        optimizer_version=portfolio.optimizer_version,
        holdings=[holding_response(item) for item in portfolio.items],
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at,
    )


def ensure_editable(portfolio: Portfolio) -> None:
    if portfolio.status == PortfolioStatus.ORDERED or portfolio.simulated_order is not None:
        raise HTTPException(status_code=409, detail="An ordered portfolio cannot be modified.")


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    payload: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioResponse:
    if payload.preference_id is not None:
        preference = db.scalar(
            select(BuyerPreference).where(
                BuyerPreference.id == payload.preference_id,
                BuyerPreference.user_id == current_user.id,
            )
        )
        if preference is None:
            raise HTTPException(status_code=404, detail="Preference profile not found.")
        if preference.currency != payload.currency:
            raise HTTPException(
                status_code=422,
                detail="Portfolio and preference currencies must match.",
            )
    portfolio = Portfolio(
        user_id=current_user.id,
        preference_id=payload.preference_id,
        name=payload.name.strip(),
        currency=payload.currency,
        status=PortfolioStatus.DRAFT,
    )
    db.add(portfolio)
    db.commit()
    return portfolio_response(get_owned_portfolio(db, current_user.id, portfolio.id))


@router.get("", response_model=list[PortfolioResponse])
def list_portfolios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[PortfolioResponse]:
    portfolios = db.scalars(
        portfolio_query()
        .where(Portfolio.user_id == current_user.id)
        .order_by(Portfolio.updated_at.desc(), Portfolio.id)
    ).unique()
    return [portfolio_response(portfolio) for portfolio in portfolios]


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(
    portfolio_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioResponse:
    return portfolio_response(get_owned_portfolio(db, current_user.id, portfolio_id))


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: UUID,
    payload: PortfolioUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioResponse:
    portfolio = get_owned_portfolio(db, current_user.id, portfolio_id)
    ensure_editable(portfolio)
    portfolio.name = payload.name.strip()
    db.commit()
    return portfolio_response(get_owned_portfolio(db, current_user.id, portfolio_id))


@router.post(
    "/{portfolio_id}/holdings",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_holding(
    portfolio_id: UUID,
    payload: HoldingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioResponse:
    portfolio = get_owned_portfolio(db, current_user.id, portfolio_id)
    ensure_editable(portfolio)
    credit = db.scalar(
        select(CarbonCredit)
        .join(CarbonCredit.project)
        .where(
            CarbonCredit.id == payload.credit_id,
            Project.status == ProjectStatus.ACTIVE,
        )
    )
    if credit is None:
        raise HTTPException(status_code=404, detail="Carbon credit not found.")
    if credit.currency != portfolio.currency:
        raise HTTPException(status_code=422, detail="Holding currency must match the portfolio.")
    if payload.quantity > credit.quantity_available:
        raise HTTPException(status_code=409, detail="Requested quantity exceeds availability.")
    portfolio.items.append(
        PortfolioItem(
            credit=credit,
            quantity=payload.quantity,
            unit_price_snapshot=credit.price_per_credit,
            allocation_percent=Decimal("0"),
        )
    )
    recalculate_portfolio(portfolio)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Credit already exists in this portfolio.") from exc
    return portfolio_response(get_owned_portfolio(db, current_user.id, portfolio_id))


@router.patch("/{portfolio_id}/holdings/{holding_id}", response_model=PortfolioResponse)
def update_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    payload: HoldingUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioResponse:
    portfolio = get_owned_portfolio(db, current_user.id, portfolio_id)
    ensure_editable(portfolio)
    holding = get_holding(portfolio, holding_id)
    if holding.is_locked:
        raise HTTPException(status_code=409, detail="Locked holdings cannot be modified.")
    if payload.quantity > holding.credit.quantity_available:
        raise HTTPException(status_code=409, detail="Requested quantity exceeds availability.")
    holding.quantity = payload.quantity
    recalculate_portfolio(portfolio)
    db.commit()
    return portfolio_response(get_owned_portfolio(db, current_user.id, portfolio_id))


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    portfolio = get_owned_portfolio(db, current_user.id, portfolio_id)
    ensure_editable(portfolio)
    holding = get_holding(portfolio, holding_id)
    if holding.is_locked:
        raise HTTPException(status_code=409, detail="Locked holdings cannot be removed.")
    portfolio.items.remove(holding)
    db.delete(holding)
    recalculate_portfolio(portfolio)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
