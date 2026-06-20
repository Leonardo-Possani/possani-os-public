from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.interfaces import AbstractServiceOrderRepository


def make_service_order(**overrides: object) -> ServiceOrder:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
    }
    data.update(overrides)
    return ServiceOrder(**data)


def test_repository_implements_service_order_repository_contract() -> None:
    repository = InMemoryServiceOrderRepository()

    assert isinstance(repository, AbstractServiceOrderRepository)


def test_add_and_get_by_id() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = make_service_order()

    added = repository.add(service_order)

    assert added == service_order
    assert repository.get_by_id(service_order.id) == service_order


def test_get_by_id_returns_none_when_not_found() -> None:
    repository = InMemoryServiceOrderRepository()

    assert repository.get_by_id(uuid4()) is None


def test_add_rejects_duplicate_id() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = make_service_order()
    repository.add(service_order)

    with pytest.raises(ValueError, match="Service order with this ID already exists."):
        repository.add(service_order)


def test_list_returns_all_service_orders() -> None:
    repository = InMemoryServiceOrderRepository()
    oldest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
    )
    newest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
    )

    assert repository.list() == [newest, oldest]


def test_list_filters_by_customer_id() -> None:
    repository = InMemoryServiceOrderRepository()
    target_customer_id = uuid4()
    other_customer_id = uuid4()
    first = repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
    )
    second = repository.add(make_service_order(customer_id=other_customer_id))
    third = repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        ),
    )

    assert repository.list(customer_id=target_customer_id) == [third, first]
    assert second not in repository.list(customer_id=target_customer_id)


def test_list_applies_limit_and_offset() -> None:
    repository = InMemoryServiceOrderRepository()
    oldest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
    )
    middle = repository.add(
        make_service_order(created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
    )
    repository.add(
        make_service_order(created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)),
    )

    assert repository.list(limit=2, offset=1) == [middle, oldest]


def test_list_applies_pagination_after_customer_filter() -> None:
    repository = InMemoryServiceOrderRepository()
    target_customer_id = uuid4()
    other_customer_id = uuid4()
    repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
    )
    expected = repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        ),
    )
    repository.add(make_service_order(customer_id=other_customer_id))
    repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
        ),
    )

    assert repository.list(customer_id=target_customer_id, limit=1, offset=1) == [
        expected,
    ]


def test_list_returns_empty_list_when_no_service_orders_match_customer_id() -> None:
    repository = InMemoryServiceOrderRepository()
    repository.add(make_service_order(customer_id=uuid4()))

    assert repository.list(customer_id=uuid4()) == []


def test_update_existing_service_order() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = repository.add(make_service_order())
    updated = service_order.change_status(ServiceOrderStatus.IN_PROGRESS)

    result = repository.update(updated)

    assert result == updated
    assert repository.get_by_id(service_order.id) == updated


def test_update_raises_error_when_service_order_not_found() -> None:
    repository = InMemoryServiceOrderRepository()
    service_order = make_service_order()

    with pytest.raises(ValueError, match="Service order with this ID does not exist."):
        repository.update(service_order)
