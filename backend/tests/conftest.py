import os
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)

def pytest_configure() -> None:
    from app.config import settings
    from app import db

    assert settings.database_url == os.environ["DATABASE_URL"]
    assert db.engine.url.drivername == "sqlite+pysqlite"
    assert hasattr(db, "SessionFactory")

    session = db.SessionFactory()
    try:
        assert session.get_bind() is db.engine
    finally:
        session.close()
