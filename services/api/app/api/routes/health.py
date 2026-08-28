from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.database.session import get_database_status

router = APIRouter(prefix="/health", tags=["Health"])
DatabaseStatus = Annotated[
    Literal["ok", "unavailable"], Depends(get_database_status)
]


@router.get(
    "",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The API is running but PostgreSQL is unavailable."
        }
    },
)
async def health_check(database_status: DatabaseStatus) -> JSONResponse:
    settings = get_settings()
    is_healthy = database_status == "ok"

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if is_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "ok" if is_healthy else "degraded",
            "version": settings.app_version,
            "database": database_status,
        },
    )
