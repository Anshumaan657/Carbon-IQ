from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.database import session as database_session


def test_session_factory_creates_sqlalchemy_session() -> None:
    session = database_session.SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_get_db_closes_successful_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSession:
        closed = False

        def close(self) -> None:
            self.closed = True

    session = FakeSession()
    monkeypatch.setattr(database_session, "SessionLocal", lambda: session)

    dependency: Generator[Session, None, None] = database_session.get_db()
    assert next(dependency) is session

    with pytest.raises(StopIteration):
        next(dependency)

    assert session.closed is True


def test_get_db_rolls_back_and_closes_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSession:
        rolled_back = False
        closed = False

        def rollback(self) -> None:
            self.rolled_back = True

        def close(self) -> None:
            self.closed = True

    session = FakeSession()
    monkeypatch.setattr(database_session, "SessionLocal", lambda: session)

    dependency: Generator[Session, None, None] = database_session.get_db()
    assert next(dependency) is session

    with pytest.raises(RuntimeError, match="database operation failed"):
        dependency.throw(RuntimeError("database operation failed"))

    assert session.rolled_back is True
    assert session.closed is True
