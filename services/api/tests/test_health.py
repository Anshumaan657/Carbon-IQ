from fastapi.testclient import TestClient

from app.database.session import get_database_status
from app.main import app

client = TestClient(app)


def database_is_available() -> str:
    return "ok"


def database_is_unavailable() -> str:
    return "unavailable"


def test_health_check() -> None:
    app.dependency_overrides[get_database_status] = database_is_available
    try:
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.1.0",
        "database": "ok",
    }


def test_health_check_reports_unavailable_database() -> None:
    app.dependency_overrides[get_database_status] = database_is_unavailable
    try:
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "version": "0.1.0",
        "database": "unavailable",
    }
