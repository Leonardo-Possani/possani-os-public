from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import (
    get_in_memory_service_order_repository,
    get_service_order_repository,
)
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.repository import SqlAlchemyServiceOrderRepository


@pytest.mark.anyio
async def test_get_service_order_repository_returns_in_memory_when_configured() -> None:
    original_type = settings.repository_type
    settings.repository_type = "memory"

    try:
        get_in_memory_service_order_repository.cache_clear()
        repository = get_service_order_repository(db=None)
        same_repository = get_service_order_repository(db=None)

        assert isinstance(repository, InMemoryServiceOrderRepository)
        assert repository is same_repository
    finally:
        settings.repository_type = original_type
        get_in_memory_service_order_repository.cache_clear()


@pytest.mark.anyio
async def test_get_service_order_repository_returns_sqlalchemy_when_configured() -> None:
    mock_db = MagicMock(spec=Session)
    original_type = settings.repository_type
    settings.repository_type = "sqlalchemy"

    try:
        repository = get_service_order_repository(db=mock_db)

        assert isinstance(repository, SqlAlchemyServiceOrderRepository)
        assert repository.session is mock_db
    finally:
        settings.repository_type = original_type
