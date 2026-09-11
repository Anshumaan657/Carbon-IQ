from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_administrator
from app.api.routes.projects import (
    PROJECT_REQUIRED_FIELDS,
    commit_project,
    detail_from_project,
    validate_project_state,
)
from app.database.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectUpdate


router = APIRouter(prefix="/admin/projects", tags=["project administration"])


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    _administrator: Annotated[User, Depends(require_administrator)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectDetail:
    values = payload.model_dump()
    values["source_url"] = str(payload.source_url)
    project = Project(**values)
    db.add(project)
    commit_project(db, project)
    return detail_from_project(project)


@router.patch("/{project_id}", response_model=ProjectDetail)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    _administrator: Annotated[User, Depends(require_administrator)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectDetail:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    changes = payload.model_dump(exclude_unset=True)
    if any(changes.get(field) is None for field in PROJECT_REQUIRED_FIELDS & changes.keys()):
        raise HTTPException(status_code=422, detail="Required project fields cannot be null.")
    if "source_url" in changes and changes["source_url"] is not None:
        changes["source_url"] = str(changes["source_url"])
    for field, value in changes.items():
        setattr(project, field, value)
    validate_project_state(project)
    commit_project(db, project)
    return detail_from_project(project)
