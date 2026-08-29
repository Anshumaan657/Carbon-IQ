import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


TEST_DATABASE_URL = "postgresql+psycopg://test-user@test-db:5432/test-db"


ENVIRONMENT_KEYS = (
    "APP_NAME",
    "APP_VERSION",
    "API_V1_PREFIX",
    "ENVIRONMENT",
    "DEBUG",
    "DATABASE_URL",
    "DATABASE_ECHO",
    "DATABASE_CONNECT_TIMEOUT",
)


def clear_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENVIRONMENT_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_environment(monkeypatch)

    settings = Settings(database_url=TEST_DATABASE_URL, _env_file=None)

    assert settings.app_name == "CarbonIQ API"
    assert settings.app_version == "0.1.0"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.database_connect_timeout == 5


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_environment(monkeypatch)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_environment(monkeypatch)
    monkeypatch.setenv("APP_NAME", "CarbonIQ Test API")
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv(
        "DATABASE_URL",
        TEST_DATABASE_URL,
    )
    monkeypatch.setenv("DATABASE_ECHO", "true")
    monkeypatch.setenv("DATABASE_CONNECT_TIMEOUT", "10")

    settings = Settings(_env_file=None)

    assert settings.app_name == "CarbonIQ Test API"
    assert settings.app_version == "9.9.9"
    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.database_url == TEST_DATABASE_URL
    assert settings.database_echo is True
    assert settings.database_connect_timeout == 10


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    (("true", True), ("1", True), ("false", False), ("0", False)),
)
def test_boolean_parsing(
    monkeypatch: pytest.MonkeyPatch, raw_value: str, expected: bool
) -> None:
    clear_environment(monkeypatch)
    monkeypatch.setenv("DEBUG", raw_value)

    settings = Settings(database_url=TEST_DATABASE_URL, _env_file=None)

    assert settings.debug is expected


def test_invalid_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_environment(monkeypatch)
    monkeypatch.setenv("ENVIRONMENT", "invalid")

    with pytest.raises(ValidationError):
        Settings(database_url=TEST_DATABASE_URL, _env_file=None)


def test_settings_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_environment(monkeypatch)
    get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "Cached API")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

    first = get_settings()
    monkeypatch.setenv("APP_NAME", "Changed API")
    second = get_settings()

    assert first is second
    assert second.app_name == "Cached API"

    get_settings.cache_clear()
