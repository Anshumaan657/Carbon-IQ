from __future__ import annotations

import logging
import re
import time
from uuid import uuid4

from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger("carboniq.requests")
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def request_id_from_scope(scope: Scope) -> str:
    state = scope.setdefault("state", {})
    return state.get("request_id", "unknown")


def error_body(code: str, message: str, request_id: str, details: object = None) -> dict:
    error = {"code": code, "message": message, "request_id": request_id}
    if details is not None:
        error["details"] = details
    return {"error": error}


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope.get("headers", [])).get(b"x-request-id", b"").decode(
            "ascii", errors="ignore"
        )
        request_id = incoming if REQUEST_ID_PATTERN.fullmatch(incoming) else uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        response_status = 500

        async def send_with_context(message: Message) -> None:
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_context)
        finally:
            logger.info(
                "request_complete",
                extra={
                    "request_id": request_id,
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": response_status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )


class RequestBodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        raw_length = headers.get(b"content-length")
        if raw_length:
            try:
                if int(raw_length) > self.max_bytes:
                    await self._reject(scope, send)
                    return
            except ValueError:
                pass

        body_parts: list[bytes] = []
        received = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                await self.app(scope, _single_message_receiver(message), send)
                return
            chunk = message.get("body", b"")
            body_parts.append(chunk)
            received += len(chunk)
            if received > self.max_bytes:
                await self._reject(scope, send)
                return
            if not message.get("more_body", False):
                break

        replay = _single_message_receiver(
            {"type": "http.request", "body": b"".join(body_parts), "more_body": False}
        )
        await self.app(scope, replay, send)

    async def _reject(self, scope: Scope, send: Send) -> None:
        response = JSONResponse(
            status_code=413,
            content=error_body(
                "request_too_large",
                f"Request body exceeds the {self.max_bytes}-byte limit.",
                request_id_from_scope(scope),
            ),
        )
        await response(scope, _single_message_receiver({"type": "http.disconnect"}), send)


def _single_message_receiver(message: Message) -> Receive:
    delivered = False

    async def receive_once() -> Message:
        nonlocal delivered
        if not delivered:
            delivered = True
            return message
        return {"type": "http.disconnect"}

    return receive_once


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("X-Frame-Options", "DENY")
                headers.setdefault("Referrer-Policy", "no-referrer")
                headers.setdefault("Cache-Control", "no-store")
            await send(message)

        await self.app(scope, receive, send_with_security_headers)
