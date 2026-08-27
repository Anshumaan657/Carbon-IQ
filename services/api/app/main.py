from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="CarbonIQ API",
    description="API for the CarbonIQ carbon-credit intelligence platform.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
