"""Tests require a running PostgreSQL instance."""
from sqlalchemy import text
from app.database import engine, SessionLocal


def test_engine_is_configured():
    assert engine is not None
    assert "preprank" in str(engine.url)


def test_session_factory_returns_session():
    """Requires live PostgreSQL."""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close()
