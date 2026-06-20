from datetime import datetime, timezone
from uuid import uuid4

from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.service_orders.domain import ServiceOrder
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.service import ServiceOrderService


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


def test_list_returns_all_service_orders() -> None:
    repository = InMemoryServiceOrderRepository()
    oldest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
    )
    newest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
    )
    service = make_service(repository)

    assert service.list() == [newest, oldest]


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
    repository.add(make_service_order(customer_id=other_customer_id))
    second = repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        ),
    )
    service = make_service(repository)

    assert service.list(customer_id=target_customer_id) == [second, first]


def test_list_delegates_pagination_to_repository() -> None:
    repository = InMemoryServiceOrderRepository()
    oldest = repository.add(
        make_service_order(created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
    )
    expected = repository.add(
        make_service_order(created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
    )
    repository.add(
        make_service_order(created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)),
    )
    service = make_service(repository)

    assert service.list(limit=1, offset=1) == [expected]


def test_list_delegates_customer_filter_and_pagination_to_repository() -> None:
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
    service = make_service(repository)

    assert service.list(customer_id=target_customer_id, limit=1, offset=1) == [
        expected,
    ]


def test_list_returns_empty_list_when_repository_is_empty() -> None:
    service = make_service(InMemoryServiceOrderRepository())

    assert service.list() == []


def test_list_returns_empty_list_when_customer_filter_has_no_matches() -> None:
    repository = InMemoryServiceOrderRepository()
    repository.add(make_service_order(customer_id=uuid4()))
    service = make_service(repository)

    assert service.list(customer_id=uuid4()) == []
