from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.middleware import error_body


logger = logging.getLogger("carboniq.errors")


def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exception: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                error_body(
                    "validation_error",
                    "The request could not be validated.",
                    request_id(request),
                    exception.errors(),
                )
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request, exception: StarletteHTTPException
    ) -> JSONResponse:
        message = exception.detail if isinstance(exception.detail, str) else "Request failed."
        details = None if isinstance(exception.detail, str) else exception.detail
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                error_body(
                    f"http_{exception.status_code}",
                    message,
                    request_id(request),
                    details,
                )
            ),
            headers=exception.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exception: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_request_error",
            extra={"request_id": request_id(request)},
        )
        return JSONResponse(
            status_code=500,
            content=error_body(
                "internal_server_error",
                "An unexpected error occurred.",
                request_id(request),
            ),
        )
