from __future__ import annotations

from collections.abc import Generator
from datetime import date
from decimal import Decimal
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.database.session import get_db
from app.main import app
from app.models.credit import CarbonCredit
from app.models.document import ProjectDocument
from app.models.enums import (
    DocumentStatus,
    ProjectCategory,
    ProjectStatus,
    RiskSeverity,
    UserRole,
    VerificationStatus,
)
from app.models.project import Project
from app.models.score import ProjectScore, RiskSignal
from app.models.user import User


API_DIRECTORY = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def catalog_session_factory() -> Generator[sessionmaker[Session], None, None]:
    application_url = make_url(get_settings().database_url)
    schema_name = f"carboniq_catalog_test_{uuid4().hex}"
    connection_url = application_url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    test_url = application_url.update_query_dict(
        {"options": f"-csearch_path={schema_name},public"}
    ).render_as_string(hide_password=False)

    with psycopg.connect(connection_url, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name)))

    environment = os.environ.copy()
    environment["DATABASE_URL"] = test_url
    environment["ALEMBIC_VERSION_SCHEMA"] = schema_name
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=API_DIRECTORY,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    test_engine = create_engine(test_url, pool_pre_ping=True)
    factory = sessionmaker(bind=test_engine, expire_on_commit=False)

    try:
        yield factory
    finally:
        test_engine.dispose()
        with psycopg.connect(connection_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(schema_name)
                )
            )


@pytest.fixture()
def client(catalog_session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    with catalog_session_factory() as cleanup_session:
        table_names = cleanup_session.scalars(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = current_schema() AND table_name <> 'alembic_version'"
            )
        ).all()
        if table_names:
            quoted = ", ".join(f'"{name}"' for name in table_names)
            cleanup_session.execute(text(f"TRUNCATE TABLE {quoted} CASCADE"))
            cleanup_session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        session = catalog_session_factory()
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


def create_user(
    factory: sessionmaker[Session],
    email: str,
    role: UserRole = UserRole.BUYER,
) -> tuple[User, str]:
    with factory() as session:
        user = User(
            email=email,
            password_hash=hash_password("test-password"),
            organization_name="CarbonIQ Test Organization",
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        token = create_access_token(user.id, user.role)
        return user, token


def project_values(suffix: str, **overrides) -> dict:
    values = {
        "external_id": f"project-{suffix}",
        "name": f"Forest Project {suffix}",
        "slug": f"forest-project-{suffix}",
        "developer_name": "Climate Developer",
        "description": "Restores degraded forest and supports biodiversity.",
        "country_code": "IN",
        "region": "South Asia",
        "project_type": "reforestation",
        "category": ProjectCategory.REMOVAL,
        "registry": "Test Registry",
        "registry_project_id": f"registry-{suffix}",
        "methodology": "TEST-001",
        "vintage_start": 2024,
        "vintage_end": 2026,
        "verification_status": VerificationStatus.VERIFIED,
        "status": ProjectStatus.ACTIVE,
        "price_per_credit": Decimal("10.00"),
        "currency": "USD",
        "available_quantity": Decimal("1000.000"),
        "sdgs": [13, 15],
        "source_url": "https://example.com/project",
        "data_as_of": date(2026, 9, 1),
        "is_synthetic": True,
    }
    values.update(overrides)
    return values


def seed_catalog(factory: sessionmaker[Session]) -> tuple[UUID, UUID, UUID]:
    with factory() as session:
        india = Project(**project_values("india"))
        brazil = Project(
            **project_values(
                "brazil",
                name="Methane Capture Brazil",
                country_code="BR",
                project_type="methane capture",
                category=ProjectCategory.REDUCTION,
                price_per_credit=Decimal("20.00"),
                sdgs=[7, 13],
            )
        )
        draft = Project(**project_values("draft", status=ProjectStatus.DRAFT))
        session.add_all([india, brazil, draft])
        session.flush()
        session.add_all(
            [
                ProjectScore(
                    project_id=india.id,
                    carboniq_score=Decimal("82.00"),
                    quality_score=Decimal("80.00"),
                    impact_score=Decimal("88.00"),
                    risk_score=Decimal("18.00"),
                    confidence=Decimal("0.850"),
                    methodology_version="v1",
                ),
                ProjectScore(
                    project_id=brazil.id,
                    carboniq_score=Decimal("71.00"),
                    quality_score=Decimal("60.00"),
                    risk_score=Decimal("34.00"),
                    confidence=Decimal("0.700"),
                    methodology_version="v1",
                ),
                CarbonCredit(
                    project_id=india.id,
                    vintage=2025,
                    quantity_available=Decimal("500.000"),
                    price_per_credit=Decimal("11.00"),
                    currency="USD",
                    data_as_of=date(2026, 9, 1),
                ),
                CarbonCredit(
                    project_id=brazil.id,
                    vintage=2025,
                    quantity_available=Decimal("300.000"),
                    price_per_credit=Decimal("20.00"),
                    currency="USD",
                    data_as_of=date(2026, 9, 1),
                ),
                ProjectDocument(
                    project_id=india.id,
                    document_type="pdd",
                    title="Project Design Document",
                    source_url="https://example.com/pdd.pdf",
                    status=DocumentStatus.READY,
                    page_count=25,
                ),
                RiskSignal(
                    project_id=india.id,
                    code="OLD_VINTAGE",
                    severity=RiskSeverity.LOW,
                    title="Older vintage",
                    message="Review vintage suitability.",
                    requires_review=False,
                    rule_version="v1",
                ),
            ]
        )
        session.commit()
        return india.id, brazil.id, draft.id


def project_payload(suffix: str = "created") -> dict:
    values = project_values(suffix)
    return {
        key: (
            str(value)
            if isinstance(value, Decimal)
            else value.isoformat()
            if isinstance(value, date)
            else value.value
            if hasattr(value, "value")
            else value
        )
        for key, value in values.items()
    }


def preference_payload() -> dict:
    return {
        "name": "India low-risk portfolio",
        "budget": 100000,
        "currency": "inr",
        "required_credits": 100,
        "risk_tolerance": "low",
        "preferred_project_types": ["Reforestation", "reforestation"],
        "preferred_countries": ["in", "IN"],
        "preferred_category": "removal",
        "sdg_priorities": [13, 15, 13],
        "minimum_quality_score": 70,
        "delivery_start": "2026-10-01",
        "delivery_end": "2026-12-31",
    }


def test_catalogue_search_filters_scores_and_hides_drafts(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    india_id, _, _ = seed_catalog(catalog_session_factory)

    response = client.get(
        "/api/v1/projects",
        params={
            "q": "forest",
            "country": "in",
            "region": "South Asia",
            "sdg": 15,
            "risk_max": 20,
            "impact_min": 85,
            "vintage_year": 2025,
            "available_only": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(india_id)
    assert body["items"][0]["carboniq_score"] == 82.0
    assert body["items"][0]["risk_score"] == 18.0


def test_catalogue_pagination_sorting_and_filter_validation(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    seed_catalog(catalog_session_factory)

    page = client.get(
        "/api/v1/projects", params={"sort": "price", "order": "desc", "page_size": 1}
    )
    invalid = client.get("/api/v1/projects", params={"price_min": 20, "price_max": 10})

    assert page.status_code == 200
    assert page.json()["total"] == 2
    assert page.json()["total_pages"] == 2
    assert page.json()["items"][0]["country_code"] == "BR"
    assert invalid.status_code == 422


def test_project_detail_contains_evidence_inventory_and_active_risk(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    india_id, _, draft_id = seed_catalog(catalog_session_factory)

    response = client.get(f"/api/v1/projects/{india_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_score"]["quality_score"] == 80.0
    assert body["inventory"][0]["vintage"] == 2025
    assert body["documents"][0]["page_count"] == 25
    assert body["active_risk_signals"][0]["code"] == "OLD_VINTAGE"
    assert client.get(f"/api/v1/projects/{draft_id}").status_code == 404
    assert client.get(f"/api/v1/projects/{india_id}/credits").json()[0]["vintage"] == 2025
    assert (
        client.get(f"/api/v1/projects/{india_id}/documents").json()[0]["title"]
        == "Project Design Document"
    )


def test_compare_requires_two_to_four_unique_public_projects(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    india_id, brazil_id, draft_id = seed_catalog(catalog_session_factory)

    response = client.post(
        "/api/v1/projects/compare",
        json={"project_ids": [str(brazil_id), str(india_id)]},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [
        str(brazil_id),
        str(india_id),
    ]
    assert client.post(
        "/api/v1/projects/compare", json={"project_ids": [str(india_id), str(india_id)]}
    ).status_code == 422
    assert client.post(
        "/api/v1/projects/compare", json={"project_ids": [str(india_id), str(draft_id)]}
    ).status_code == 404


def test_only_administrator_can_create_and_update_projects(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    _, buyer_token = create_user(catalog_session_factory, "buyer@example.com")
    _, admin_token = create_user(
        catalog_session_factory, "admin@example.com", UserRole.ADMIN
    )
    payload = project_payload()

    forbidden = client.post(
        "/api/v1/admin/projects",
        json=payload,
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    created = client.post(
        "/api/v1/admin/projects",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    updated = client.patch(
        f"/api/v1/admin/projects/{created.json()['id']}",
        json={"name": "Updated Carbon Project", "price_per_credit": 12.5},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert forbidden.status_code == 403
    assert created.status_code == 201
    assert created.json()["country_code"] == "IN"
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Carbon Project"


def test_project_uniqueness_and_cross_field_validation(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    _, admin_token = create_user(
        catalog_session_factory, "admin@example.com", UserRole.ADMIN
    )
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = project_payload()
    assert (
        client.post("/api/v1/admin/projects", json=payload, headers=headers).status_code
        == 201
    )

    assert (
        client.post("/api/v1/admin/projects", json=payload, headers=headers).status_code
        == 409
    )
    invalid = project_payload("invalid")
    invalid["currency"] = None
    assert (
        client.post("/api/v1/admin/projects", json=invalid, headers=headers).status_code
        == 422
    )


def test_preference_crud_normalizes_values(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    _, token = create_user(catalog_session_factory, "buyer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/preferences", json=preference_payload(), headers=headers)
    preference_id = created.json()["id"]
    listed = client.get("/api/v1/preferences", headers=headers)
    updated = client.patch(
        f"/api/v1/preferences/{preference_id}",
        json={"budget": 125000, "preferred_category": None},
        headers=headers,
    )
    deleted = client.delete(f"/api/v1/preferences/{preference_id}", headers=headers)

    assert created.status_code == 201
    assert created.json()["currency"] == "INR"
    assert created.json()["preferred_countries"] == ["IN"]
    assert created.json()["preferred_project_types"] == ["reforestation"]
    assert listed.status_code == 200 and len(listed.json()) == 1
    assert updated.status_code == 200 and updated.json()["budget"] == 125000.0
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/preferences/{preference_id}", headers=headers).status_code == 404


def test_preferences_are_authenticated_and_owner_scoped(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    _, first_token = create_user(catalog_session_factory, "first@example.com")
    _, second_token = create_user(catalog_session_factory, "second@example.com")
    created = client.post(
        "/api/v1/preferences",
        json=preference_payload(),
        headers={"Authorization": f"Bearer {first_token}"},
    )
    preference_id = created.json()["id"]

    assert client.get("/api/v1/preferences").status_code == 401
    assert client.get(
        f"/api/v1/preferences/{preference_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    ).status_code == 404
    assert client.delete(
        f"/api/v1/preferences/{preference_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    ).status_code == 404


@pytest.mark.parametrize(
    "changes",
    [
        {"delivery_start": "2027-01-01", "delivery_end": "2026-01-01"},
        {"sdg_priorities": [18]},
        {"preferred_countries": ["IND"]},
        {"budget": 0},
    ],
)
def test_preference_validation_rejects_invalid_input(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
    changes: dict,
) -> None:
    _, token = create_user(catalog_session_factory, "buyer@example.com")
    payload = preference_payload()
    payload.update(changes)

    response = client.post(
        "/api/v1/preferences",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def portfolio_setup(
    client: TestClient,
    factory: sessionmaker[Session],
    email: str = "portfolio@example.com",
) -> tuple[dict[str, str], str, list[UUID]]:
    india_id, brazil_id, _ = seed_catalog(factory)
    _, token = create_user(factory, email)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/portfolios",
        json={"name": "Procurement portfolio", "currency": "usd"},
        headers=headers,
    )
    assert created.status_code == 201
    with factory() as session:
        credit_ids = list(
            session.scalars(
                select(CarbonCredit.id)
                .where(CarbonCredit.project_id.in_([india_id, brazil_id]))
                .order_by(CarbonCredit.price_per_credit)
            )
        )
    return headers, created.json()["id"], credit_ids


def test_portfolio_crud_and_owner_scoping(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    headers, portfolio_id, _ = portfolio_setup(client, catalog_session_factory)
    _, other_token = create_user(catalog_session_factory, "other@example.com")
    other_headers = {"Authorization": f"Bearer {other_token}"}

    listed = client.get("/api/v1/portfolios", headers=headers)
    renamed = client.patch(
        f"/api/v1/portfolios/{portfolio_id}",
        json={"name": "Renamed portfolio"},
        headers=headers,
    )

    assert listed.status_code == 200 and len(listed.json()) == 1
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Renamed portfolio"
    assert client.get(f"/api/v1/portfolios/{portfolio_id}", headers=other_headers).status_code == 404
    assert client.get("/api/v1/portfolios").status_code == 401


def test_holdings_recalculate_financial_impact_score_and_allocation_totals(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    headers, portfolio_id, credit_ids = portfolio_setup(client, catalog_session_factory)

    first = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"credit_id": str(credit_ids[0]), "quantity": 40},
        headers=headers,
    )
    second = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"credit_id": str(credit_ids[1]), "quantity": 60},
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    body = second.json()
    assert body["total_credits"] == 100.0
    assert body["estimated_carbon_impact_tonnes"] == 100.0
    assert body["total_cost"] == 1640.0
    assert body["average_quality"] == 68.0
    assert body["portfolio_risk"] == 27.6
    assert sorted(item["allocation_percent"] for item in body["holdings"]) == [40.0, 60.0]


def test_holding_update_and_delete_recalculate_totals(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    headers, portfolio_id, credit_ids = portfolio_setup(client, catalog_session_factory)
    added = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"credit_id": str(credit_ids[0]), "quantity": 25},
        headers=headers,
    ).json()
    holding_id = added["holdings"][0]["id"]

    updated = client.patch(
        f"/api/v1/portfolios/{portfolio_id}/holdings/{holding_id}",
        json={"quantity": 10},
        headers=headers,
    )
    deleted = client.delete(
        f"/api/v1/portfolios/{portfolio_id}/holdings/{holding_id}", headers=headers
    )
    empty = client.get(f"/api/v1/portfolios/{portfolio_id}", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["total_cost"] == 110.0
    assert deleted.status_code == 204
    assert empty.json()["total_cost"] == 0.0
    assert empty.json()["total_credits"] == 0.0
    assert empty.json()["average_quality"] is None


def test_holding_rejects_duplicates_excess_quantity_and_currency_mismatch(
    client: TestClient,
    catalog_session_factory: sessionmaker[Session],
) -> None:
    headers, portfolio_id, credit_ids = portfolio_setup(client, catalog_session_factory)
    endpoint = f"/api/v1/portfolios/{portfolio_id}/holdings"
    assert client.post(
        endpoint, json={"credit_id": str(credit_ids[0]), "quantity": 1}, headers=headers
    ).status_code == 201
    assert client.post(
        endpoint, json={"credit_id": str(credit_ids[0]), "quantity": 1}, headers=headers
    ).status_code == 409
    assert client.post(
        endpoint, json={"credit_id": str(credit_ids[1]), "quantity": 1000}, headers=headers
    ).status_code == 409

    eur_portfolio = client.post(
        "/api/v1/portfolios",
        json={"name": "Euro portfolio", "currency": "EUR"},
        headers=headers,
    ).json()
    assert client.post(
        f"/api/v1/portfolios/{eur_portfolio['id']}/holdings",
        json={"credit_id": str(credit_ids[1]), "quantity": 1},
        headers=headers,
    ).status_code == 422
