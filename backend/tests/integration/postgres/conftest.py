import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db import Base, create_db_engine, create_session_factory


def _get_postgres_test_database_url() -> str:
    database_url = os.environ.get("POSTGRES_TEST_DATABASE_URL", "")

    if not database_url:
        raise RuntimeError("POSTGRES_TEST_DATABASE_URL is not configured.")

    if "possani_os_test" not in database_url:
        raise RuntimeError(
            "Refusing to run PostgreSQL tests outside possani_os_test. "
            f"Current URL: {database_url}"
        )

    if database_url.endswith("/possani_os"):
        raise RuntimeError(
            "Refusing to run PostgreSQL tests against the development database."
        )

    return database_url


@pytest.fixture(scope="session")
def postgres_database_url() -> str:
    return _get_postgres_test_database_url()


@pytest.fixture(scope="session")
def postgres_engine(postgres_database_url: str) -> Generator[Engine, None, None]:
    engine = create_db_engine(postgres_database_url)

    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.commit()

    old_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = postgres_database_url

    alembic_ini_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "alembic.ini")
    )
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_database_url)
    command.upgrade(alembic_cfg, "head")

    if old_database_url is not None:
        os.environ["DATABASE_URL"] = old_database_url

    yield engine

    engine.dispose()


@pytest.fixture()
def postgres_session(postgres_engine: Engine) -> Generator[Session, None, None]:
    SessionFactory = create_session_factory(postgres_engine)
    session = SessionFactory()

    try:
        yield session
    finally:
        session.rollback()
        with postgres_engine.begin() as connection:
            for table in Base.metadata.sorted_tables:
                connection.execute(
                    text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE")
                )
        session.close()
