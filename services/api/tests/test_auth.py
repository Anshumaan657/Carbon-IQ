from __future__ import annotations

from collections.abc import Generator
from datetime import timedelta
from uuid import uuid4

import psycopg
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg import sql
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import require_administrator
from app.core.config import get_settings
from app.core.security import create_access_token
from app.database.session import get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import RefreshToken, User


@pytest.fixture(scope="module")
def auth_session_factory() -> Generator[sessionmaker[Session], None, None]:
    application_url = make_url(get_settings().database_url)
    schema_name = f"carboniq_auth_test_{uuid4().hex}"
    connection_url = application_url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    test_url = application_url.update_query_dict(
        {"options": f"-csearch_path={schema_name},public"}
    ).render_as_string(hide_password=False)

    with psycopg.connect(connection_url, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name)))

    test_engine = create_engine(test_url, pool_pre_ping=True)
    User.__table__.create(test_engine)
    RefreshToken.__table__.create(test_engine)
    factory = sessionmaker(bind=test_engine, expire_on_commit=False)

    try:
        yield factory
    finally:
        test_engine.dispose()
        with psycopg.connect(connection_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema_name))
            )


@pytest.fixture()
def client(auth_session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    with auth_session_factory() as cleanup_session:
        cleanup_session.execute(delete(RefreshToken))
        cleanup_session.execute(delete(User))
        cleanup_session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        session = auth_session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def registration_payload(email: str = "buyer@example.com") -> dict[str, str]:
    return {
        "email": email,
        "password": "correct-horse-battery-staple",
        "organization_name": "Example University",
    }


def register_and_login(client: TestClient) -> dict[str, str | int]:
    payload = registration_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200
    return response.json()


def test_successful_registration_and_login(
    client: TestClient,
    auth_session_factory: sessionmaker[Session],
) -> None:
    payload = registration_payload("Buyer@Example.com")
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == "buyer@example.com"
    assert response.json()["role"] == "buyer"
    assert "password" not in response.json()

    with auth_session_factory() as session:
        user = session.scalar(select_user("buyer@example.com"))
        assert user is not None
        assert user.password_hash != payload["password"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert login_response.json()["access_token"]
    assert login_response.json()["refresh_token"]


def select_user(email: str):
    from sqlalchemy import select

    return select(User).where(User.email == email)


def test_duplicate_email_is_rejected(client: TestClient) -> None:
    payload = registration_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_incorrect_password_is_rejected(client: TestClient) -> None:
    payload = registration_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": "definitely-wrong"},
    )

    assert response.status_code == 401


def test_protected_route_accepts_valid_token(client: TestClient) -> None:
    tokens = register_and_login(client)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "buyer@example.com"


@pytest.mark.parametrize("token", ["invalid-token", ""])
def test_protected_route_rejects_invalid_token(client: TestClient, token: str) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_expired_token(client: TestClient) -> None:
    payload = registration_payload()
    registration = client.post("/api/v1/auth/register", json=payload).json()
    token = create_access_token(
        uuid4() if "id" not in registration else registration["id"],
        UserRole.BUYER,
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_refresh_rotation_and_logout(client: TestClient) -> None:
    first_tokens = register_and_login(client)
    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_tokens["refresh_token"]},
    )

    assert refreshed.status_code == 200
    second_tokens = refreshed.json()
    assert second_tokens["refresh_token"] != first_tokens["refresh_token"]
    assert (
        client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first_tokens["refresh_token"]},
        ).status_code
        == 401
    )

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": second_tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
    )
    assert logout_response.status_code == 204
    assert (
        client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": second_tokens["refresh_token"]},
        ).status_code
        == 401
    )


def test_disabled_user_cannot_login_or_access_protected_route(
    client: TestClient,
    auth_session_factory: sessionmaker[Session],
) -> None:
    tokens = register_and_login(client)
    with auth_session_factory() as session:
        user = session.scalar(select_user("buyer@example.com"))
        assert user is not None
        user.is_active = False
        session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "buyer@example.com", "password": "correct-horse-battery-staple"},
    )
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert login_response.status_code == 401
    assert me_response.status_code == 403


def test_role_based_authorization() -> None:
    buyer = User(
        email="buyer@example.com",
        password_hash="not-used",
        organization_name="Buyer Organization",
        role=UserRole.BUYER,
    )
    administrator = User(
        email="admin@example.com",
        password_hash="not-used",
        organization_name="Admin Organization",
        role=UserRole.ADMIN,
    )

    with pytest.raises(HTTPException) as exc_info:
        require_administrator(buyer)
    assert exc_info.value.status_code == 403
    assert require_administrator(administrator) is administrator
