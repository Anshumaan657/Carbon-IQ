from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import BuyerPreference, User
from app.schemas.preference import PreferenceCreate, PreferenceResponse, PreferenceUpdate


router = APIRouter(prefix="/preferences", tags=["buyer preferences"])


def get_owned_preference(db: Session, user_id: UUID, preference_id: UUID) -> BuyerPreference:
    preference = db.scalar(
        select(BuyerPreference).where(
            BuyerPreference.id == preference_id,
            BuyerPreference.user_id == user_id,
        )
    )
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference profile not found.",
        )
    return preference


def validate_delivery_period(preference: BuyerPreference) -> None:
    if (
        preference.delivery_start is not None
        and preference.delivery_end is not None
        and preference.delivery_end < preference.delivery_start
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="delivery_end must be greater than or equal to delivery_start.",
        )


@router.post("", response_model=PreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_preference(
    payload: PreferenceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BuyerPreference:
    preference = BuyerPreference(user_id=current_user.id, **payload.model_dump())
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


@router.get("", response_model=list[PreferenceResponse])
def list_preferences(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[BuyerPreference]:
    return list(
        db.scalars(
            select(BuyerPreference)
            .where(BuyerPreference.user_id == current_user.id)
            .order_by(BuyerPreference.created_at.desc(), BuyerPreference.id)
        )
    )


@router.get("/{preference_id}", response_model=PreferenceResponse)
def read_preference(
    preference_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BuyerPreference:
    return get_owned_preference(db, current_user.id, preference_id)


@router.patch("/{preference_id}", response_model=PreferenceResponse)
def update_preference(
    preference_id: UUID,
    payload: PreferenceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BuyerPreference:
    preference = get_owned_preference(db, current_user.id, preference_id)
    changes = payload.model_dump(exclude_unset=True)
    required_fields = {"name", "budget", "currency", "required_credits", "risk_tolerance"}
    if any(changes.get(field) is None for field in required_fields & changes.keys()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Required preference fields cannot be null.",
        )
    for field, value in changes.items():
        setattr(preference, field, value)
    validate_delivery_period(preference)
    db.commit()
    db.refresh(preference)
    return preference


@router.delete("/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(
    preference_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    preference = get_owned_preference(db, current_user.id, preference_id)
    db.delete(preference)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Preference profile is referenced by another resource and cannot be deleted.",
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
