from sqlalchemy import Enum, inspect

from app.database.base import Base
from app.models import (
    BuyerPreference,
    CarbonCredit,
    DocumentChunk,
    Portfolio,
    PortfolioItem,
    Project,
    ProjectDocument,
    ProjectScore,
    RecommendationItem,
    RecommendationRun,
    RiskSignal,
    SimulatedOrder,
    User,
)


EXPECTED_TABLES = {
    "buyer_preferences",
    "carbon_credits",
    "document_chunks",
    "portfolio_items",
    "portfolios",
    "project_documents",
    "project_scores",
    "projects",
    "recommendation_items",
    "recommendation_runs",
    "risk_signals",
    "simulated_orders",
    "users",
}


def test_data_model_registers_all_contract_tables() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_primary_keys_and_foreign_keys_are_declared() -> None:
    model_classes = (
        User,
        BuyerPreference,
        Project,
        CarbonCredit,
        ProjectDocument,
        DocumentChunk,
        ProjectScore,
        RiskSignal,
        RecommendationRun,
        RecommendationItem,
        Portfolio,
        PortfolioItem,
        SimulatedOrder,
    )

    for model_class in model_classes:
        mapper = inspect(model_class)
        assert [column.name for column in mapper.primary_key] == ["id"]

    assert BuyerPreference.__table__.c.user_id.foreign_keys
    assert CarbonCredit.__table__.c.project_id.foreign_keys
    assert DocumentChunk.__table__.c.document_id.foreign_keys
    assert PortfolioItem.__table__.c.credit_id.foreign_keys
    assert RecommendationItem.__table__.c.recommendation_run_id.foreign_keys


def test_enum_values_match_the_api_contract() -> None:
    role_type = User.__table__.c.role.type
    category_type = Project.__table__.c.category.type

    assert isinstance(role_type, Enum)
    assert role_type.enums == ["buyer", "curator", "admin"]
    assert isinstance(category_type, Enum)
    assert category_type.enums == ["avoidance", "reduction", "removal", "mixed"]


def test_sensitive_password_hash_is_not_exposed_by_repr() -> None:
    user = User(
        email="buyer@example.test",
        password_hash="not-a-real-password-hash",
        organization_name="Example Buyer",
    )

    assert "not-a-real-password-hash" not in repr(user)
