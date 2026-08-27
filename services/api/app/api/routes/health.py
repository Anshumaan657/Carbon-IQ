from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "0.1.0",
        "database": "not_configured",
    }
