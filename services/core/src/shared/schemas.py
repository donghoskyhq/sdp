from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class ServiceStatusResponse(HealthResponse):
    environment: str
    database: Literal["configured", "not_configured"]
    redis: Literal["configured", "not_configured"]
