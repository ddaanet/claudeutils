"""Token cache database management using SQLAlchemy."""

from datetime import datetime

from sqlalchemy import Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class TokenCacheEntry(Base):
    """Cached token count entry."""

    __tablename__ = "token_cache"

    md5_hex: Mapped[str] = mapped_column(String, primary_key=True)
    model_id: Mapped[str] = mapped_column(String, primary_key=True)
    token_count: Mapped[int] = mapped_column(Integer)
    last_used: Mapped[datetime] = mapped_column()


def create_cache_engine(db_path: str) -> Engine:
    """Create database engine and initialize tables.

    Args:
        db_path: Path to database file (or ":memory:" for in-memory)

    Returns:
        SQLAlchemy Engine instance with tables created
    """
    engine = create_engine(
        f"sqlite:///{db_path}" if db_path != ":memory:" else "sqlite:///:memory:"
    )
    Base.metadata.create_all(engine)
    return engine
