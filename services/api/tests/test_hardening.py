from __future__ import annotations

import json
import logging
import re

from fastapi.testclient import TestClient

from app.core.logging import JsonFormatter
from app.database.session import get_database_status
from app.main import app


client = TestClient(app)


def database_is_available() -> str:
    return "ok"


def test_request_ids_and_security_headers_are_added() -> None:
    app.dependency_overrides[get_database_status] = database_is_available
    try:
        generated = client.get("/api/v1/health")
        supplied = client.get(
            "/api/v1/health", headers={"X-Request-ID": "frontend-flow-123"}
        )
        unsafe = client.get(
            "/api/v1/health", headers={"X-Request-ID": "unsafe request id"}
        )
    finally:
        app.dependency_overrides.clear()

    assert re.fullmatch(r"[0-9a-f]{32}", generated.headers["x-request-id"])
    assert supplied.headers["x-request-id"] == "frontend-flow-123"
    assert unsafe.headers["x-request-id"] != "unsafe request id"
    assert generated.headers["x-content-type-options"] == "nosniff"
    assert generated.headers["x-frame-options"] == "DENY"
    assert generated.headers["referrer-policy"] == "no-referrer"


def test_standard_error_envelopes_cover_not_found_and_validation() -> None:
    missing = client.get("/api/v1/does-not-exist")
    invalid = client.get("/api/v1/projects", params={"page_size": 101})

    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "http_404"
    assert missing.json()["error"]["request_id"] == missing.headers["x-request-id"]
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"
    assert invalid.json()["error"]["details"]


def test_request_body_limit_rejects_oversized_payloads() -> None:
    response = client.post(
        "/api/v1/auth/login",
        content=b"x" * 1_048_577,
        headers={"Content-Type": "application/json"},
    )
    streamed = client.post(
        "/api/v1/auth/login",
        content=(chunk for chunk in (b"x" * 700_000, b"y" * 400_000)),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]
    assert streamed.status_code == 413
    assert streamed.json()["error"]["code"] == "request_too_large"


def test_cors_preflight_uses_the_configured_allowlist() -> None:
    allowed = client.options(
        "/api/v1/projects",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    denied = client.options(
        "/api/v1/projects",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_exposes_core_contracts_and_bearer_authentication() -> None:
    schema = client.get("/openapi.json").json()
    expected_paths = {
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/projects",
        "/api/v1/portfolios",
        "/api/v1/orders",
        "/api/v1/orders/{order_id}/report",
    }

    assert expected_paths <= set(schema["paths"])
    assert schema["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
    assert schema["paths"]["/api/v1/auth/me"]["get"]["security"] == [
        {"HTTPBearer": []}
    ]


def test_json_log_formatter_emits_machine_readable_context() -> None:
    record = logging.LogRecord(
        name="carboniq.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_complete",
        args=(),
        exc_info=None,
    )
    record.request_id = "test-request"
    record.status_code = 200

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "request_complete"
    assert payload["request_id"] == "test-request"
    assert payload["status_code"] == 200
    assert "timestamp" in payload
