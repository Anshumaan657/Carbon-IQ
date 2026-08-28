from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API for the CarbonIQ carbon-credit intelligence platform.",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
