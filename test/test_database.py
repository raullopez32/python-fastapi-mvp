import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def test_engine_uses_settings(test_app):
    from app.config import settings
    from app.db import engine

    assert str(engine.url) == settings.DATABASE_URL == "sqlite://"


def test_file_database_connections_are_blocked(memory_only_connections, tmp_path):
    database_path = tmp_path / "forbidden.db"
    engine = create_engine(URL.create("sqlite", database=str(database_path)))
    try:
        with pytest.raises(RuntimeError, match="SQLite in memory"):
            engine.connect()
        assert not database_path.exists()
    finally:
        engine.dispose()


def test_database_url_from_dotenv(test_app, monkeypatch, tmp_path):
    from app.config import Settings

    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from-dotenv.db\n", encoding="utf-8")
    monkeypatch.delenv("DATABASE_URL")

    # Only parse settings; never create or connect an engine for this URL.
    assert Settings(_env_file=env_file).DATABASE_URL == "sqlite:///from-dotenv.db"


def test_database_url_environment_overrides_dotenv(test_app, monkeypatch, tmp_path):
    from app.config import Settings

    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from-dotenv.db\n", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    assert Settings(_env_file=env_file).DATABASE_URL == "sqlite://"


def test_client_uses_temporary_database(client, test_database):
    from app.models import Item

    with test_database() as session:
        databases = session.execute(text("PRAGMA database_list")).all()
        assert any(row[1] == "main" for row in databases)
        assert all(row[2] == "" for row in databases)
        assert session.query(Item).count() == 0

    response = client.post("/items/", json={"name": "Temporary", "price": 1})
    assert response.status_code == 201

    with test_database() as session:
        assert session.query(Item).count() == 1
    # Deliberately leave the item: fixture teardown discards the entire database.
