from uuid import uuid4

import pytest

from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.service import ServiceOrderNotFoundError, ServiceOrderService


def make_service_order(**overrides: object) -> ServiceOrder:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
    }
    data.update(overrides)
    return ServiceOrder(**data)


def make_service(repository: InMemoryServiceOrderRepository) -> ServiceOrderService:
    return ServiceOrderService(
        repository=repository,
        customer_repository=InMemoryCustomerRepository(),
    )


def test_update_status_applies_valid_transition() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = repository.add(make_service_order())
    service = make_service(repository)

    updated = service.update_status(
        service_order.id,
        ServiceOrderStatus.IN_PROGRESS,
    )

    assert updated.status == ServiceOrderStatus.IN_PROGRESS
    assert updated.updated_at > service_order.updated_at
    assert updated.closed_at is None
    assert repository.get_by_id(service_order.id) == updated


def test_update_status_raises_error_when_service_order_not_found() -> None:
    service = make_service(InMemoryServiceOrderRepository())

    with pytest.raises(ServiceOrderNotFoundError, match="Service order not found."):
        service.update_status(uuid4(), ServiceOrderStatus.IN_PROGRESS)


def test_update_status_rejects_invalid_transition_without_persisting() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = repository.add(make_service_order())
    service = make_service(repository)

    with pytest.raises(ValueError, match="Invalid service order status transition."):
        service.update_status(service_order.id, ServiceOrderStatus.DELIVERED)

    assert repository.get_by_id(service_order.id) == service_order


def test_update_status_rejects_terminal_service_order_without_persisting() -> None:
    repository = InMemoryServiceOrderRepository()
    terminal_service_order = repository.add(
        make_service_order(status=ServiceOrderStatus.CANCELLED),
    )
    service = make_service(repository)

    with pytest.raises(ValueError, match="Terminal service order cannot change status."):
        service.update_status(
            terminal_service_order.id,
            ServiceOrderStatus.IN_PROGRESS,
        )

    assert repository.get_by_id(terminal_service_order.id) == terminal_service_order


def test_update_status_sets_closed_at_when_entering_terminal_status() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = repository.add(make_service_order())
    service = make_service(repository)

    updated = service.update_status(service_order.id, ServiceOrderStatus.CANCELLED)

    assert updated.status == ServiceOrderStatus.CANCELLED
    assert updated.closed_at is not None
    assert repository.get_by_id(service_order.id) == updated
