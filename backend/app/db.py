from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings


Base = declarative_base()

def create_db_engine(database_url: str) -> Engine:
    return create_engine(database_url, future=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

engine = create_db_engine(settings.database_url)
SessionFactory = create_session_factory(engine)
SessionLocal = SessionFactory

# Models must be imported here to be registered with Base for migrations
from app.customers.models import CustomerModel # noqa: E402,F401
from app.service_orders.models import ServiceOrderModel # noqa: E402,F401

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()

    except Exception:
        db.rollback()
        raise 
    finally:
        db.close()
