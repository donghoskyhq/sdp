from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class ServiceStatusResponse(HealthResponse):
    environment: str
    database: Literal["configured", "not_configured"]
    redis: Literal["configured", "not_configured"]


ProjectStatus = Literal["pending", "provisioning", "ready", "failed"]
DeploymentTarget = Literal["vercel", "railway"]


class ProjectCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    repository_name: Annotated[
        str,
        Field(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9._-]*$"),
    ]
    description: Annotated[str | None, Field(max_length=350)] = None
    deployment_target: DeploymentTarget

    @field_validator("name", "repository_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        if value in {".", ".."}:
            raise ValueError("must be a valid repository name")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    repository_name: str
    description: str | None
    status: ProjectStatus
    github_url: str | None
    github_full_name: str | None
    deployment_target: DeploymentTarget | None
    deployment_project_id: str | None
    deployment_service_id: str | None
    deployment_id: str | None
    deployment_url: str | None
    deployment_project_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
