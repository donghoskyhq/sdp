from fastapi import APIRouter

from shared.config import get_settings
from shared.schemas import ServiceStatusResponse

router = APIRouter()


@router.get("/status", response_model=ServiceStatusResponse, tags=["status"])
def status() -> ServiceStatusResponse:
    """Describe API configuration without exposing connection details."""
    settings = get_settings()
    return ServiceStatusResponse(
        status="ok",
        service="sdp-api",
        version=settings.app_version,
        environment=settings.environment,
        database="configured" if settings.database_url else "not_configured",
        redis="configured" if settings.redis_url else "not_configured",
    )
