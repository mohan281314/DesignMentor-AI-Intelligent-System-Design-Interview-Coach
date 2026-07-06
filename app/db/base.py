"""
SQLAlchemy base — works with both SQLite (dev) and PostgreSQL (prod).
Tables are created automatically on first startup.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

_is_sqlite = settings.database_url.startswith("sqlite")

# SQLite needs special config (single-thread, same connection)
if _is_sqlite:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.db_echo,
        future=True,
    )
    # Enable foreign key enforcement on SQLite
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(
        settings.database_url,
        echo=settings.db_echo,
        future=True,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def create_tables() -> None:
    """Create all tables if they don't exist yet. Safe to call on every startup."""
    # Import all models so SQLAlchemy registers them before create_all
    from app.models import (  # noqa: F401
        User, UserProfile,
        Design,
        Interview, InterviewTurn,
        Diagram,
        ShareLink,
        PerformanceMetric, UserActivity,
    )
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
