from uuid import uuid4

import pytest

from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.service_orders.domain import ServiceOrder
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.service import ServiceOrderNotFoundError, ServiceOrderService


def make_service_order() -> ServiceOrder:
    return ServiceOrder(
        id=uuid4(),
        customer_id=uuid4(),
        equipment_type="Notebook",
        reported_problem="Does not turn on",
    )


def test_get_by_id_returns_service_order() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = repository.add(make_service_order())
    service = ServiceOrderService(
        repository=repository,
        customer_repository=InMemoryCustomerRepository(),
    )

    assert service.get_by_id(service_order.id) == service_order


def test_get_by_id_raises_error_when_service_order_not_found() -> None:
    service = ServiceOrderService(
        repository=InMemoryServiceOrderRepository(),
        customer_repository=InMemoryCustomerRepository(),
    )

    with pytest.raises(ServiceOrderNotFoundError, match="Service order not found."):
        service.get_by_id(uuid4())
