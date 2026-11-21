"""Database connection.

Gate 1 mein sync SQLAlchemy kaafi hai: orchestrator scan ke baad ek dafa save karta hai
(asyncio.to_thread se). Async engine ki zaroorat latency naapne (S7) ke baad dekhi jayegi.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from mailonix.config import get_settings

# Database na mile to chand second mein saaf error, lamba intezar nahi.
CONNECT_TIMEOUT_SECONDS = 5


def make_engine(url: str | None = None, **kwargs) -> Engine:
    """Har jagah (gateway, tests, alembic) engine yahin se banta hai, taake settings ek jaisi rahen."""
    return create_engine(
        url or get_settings().database_url,
        connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
        **kwargs,
    )


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = make_engine(pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


@contextmanager
def session_scope() -> Iterator[Session]:
    """with session_scope() as s: ...  -> kaam theek ho to commit, error par rollback."""
    get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
