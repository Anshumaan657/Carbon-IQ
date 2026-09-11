from fastapi import FastAPI

from app.api.routes.admin_projects import router as admin_projects_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.preferences import router as preferences_router
from app.api.routes.projects import router as projects_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API for the CarbonIQ carbon-credit intelligence platform.",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(projects_router, prefix=settings.api_v1_prefix)
app.include_router(preferences_router, prefix=settings.api_v1_prefix)
app.include_router(admin_projects_router, prefix=settings.api_v1_prefix)
