from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as api_v1_router
from shared.config import get_settings
from shared.schemas import HealthResponse

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Return a lightweight liveness response without checking dependencies."""
    return HealthResponse(
        status="ok",
        service="sdp-api",
        version=settings.app_version,
    )
