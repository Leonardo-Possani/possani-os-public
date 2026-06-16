from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.customers.interfaces import AbstractCustomerRepository
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.repository import SqlAlchemyCustomerRepository


@lru_cache()
def get_in_memory_customer_repository() -> AbstractCustomerRepository:
    return InMemoryCustomerRepository()


def get_customer_repository(
    db: Session = Depends(get_db)
) -> AbstractCustomerRepository:
    if settings.repository_type == "sqlalchemy":
        return SqlAlchemyCustomerRepository(db)
    
    return get_in_memory_customer_repository()
