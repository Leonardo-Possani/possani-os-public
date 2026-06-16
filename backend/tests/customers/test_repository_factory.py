import pytest
from unittest.mock import MagicMock
from fastapi import Request
from sqlalchemy.orm import Session
from app.dependencies import get_customer_repository, get_in_memory_customer_repository
from app.config import settings
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.repository import SqlAlchemyCustomerRepository

@pytest.mark.anyio
async def test_get_customer_repository_returns_in_memory_when_configured():
    # Force settings
    original_type = settings.repository_type
    settings.repository_type = "memory"
    
    try:
        # Clear cache to ensure we get a fresh check (though in tests it might not matter much)
        get_in_memory_customer_repository.cache_clear()
        repo = get_customer_repository(db=None)
        assert isinstance(repo, InMemoryCustomerRepository)
        
        # Test singleton behavior
        repo2 = get_customer_repository(db=None)
        assert repo is repo2
    finally:
        settings.repository_type = original_type

@pytest.mark.anyio
async def test_get_customer_repository_returns_sqlalchemy_when_configured():
    # Setup
    mock_db = MagicMock(spec=Session)
    
    # Force settings
    original_type = settings.repository_type
    settings.repository_type = "sqlalchemy"
    
    try:
        repo = get_customer_repository(db=mock_db)
        assert isinstance(repo, SqlAlchemyCustomerRepository)
        assert repo.session is mock_db
    finally:
        settings.repository_type = original_type
