import importlib
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def memory_only_connections():
    def guard(dialect, connection_record, connection_args, connection_params):
        if dialect.name != "sqlite" or connection_args != [":memory:"]:
            raise RuntimeError("Tests may only connect to SQLite in memory")

    event.listen(Engine, "do_connect", guard)
    try:
        yield
    finally:
        event.remove(Engine, "do_connect", guard)


@pytest.fixture(scope="session")
def test_app(memory_only_connections):
    # Importing app.main creates tables: force an in-memory URL first.
    modules = ("app.config", "app.db", "app.main")
    if any(name in sys.modules for name in modules):
        pytest.fail("Application modules must only be imported through test_app")

    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        main = importlib.import_module("app.main")
        db = importlib.import_module("app.db")
        try:
            yield main.app
        finally:
            db.engine.dispose()


@pytest.fixture
def test_database(test_app):
    from app.db import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        Base.metadata.create_all(bind=engine)
        yield sessionmaker(bind=engine, autoflush=False)
    finally:
        engine.dispose()


@pytest.fixture
def client(test_app, test_database):
    from app.db import get_db

    def override_get_db():
        with test_database() as session:
            yield session

    previous_overrides = test_app.dependency_overrides.copy()
    test_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(test_app) as test_client:
            yield test_client
    finally:
        test_app.dependency_overrides.clear()
        test_app.dependency_overrides.update(previous_overrides)
