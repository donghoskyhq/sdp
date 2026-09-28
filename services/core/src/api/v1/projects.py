from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Project
from shared.queue import enqueue_project_provisioning
from shared.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ProjectResponse])
def list_projects(session: DatabaseSession) -> list[Project]:
    return list(session.scalars(select(Project).order_by(Project.created_at.desc())))


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_202_ACCEPTED)
def create_project(payload: ProjectCreate, session: DatabaseSession) -> Project:
    project = Project(
        name=payload.name,
        repository_name=payload.repository_name,
        description=payload.description,
        deployment_target=payload.deployment_target,
        status="pending",
    )
    session.add(project)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project with that repository name already exists.",
        ) from exc

    session.refresh(project)
    try:
        enqueue_project_provisioning(project.id)
    except Exception as exc:
        project.status = "failed"
        project.error_message = "The provisioning job could not be queued."
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The project was saved, but provisioning could not be started.",
        ) from exc

    return project
