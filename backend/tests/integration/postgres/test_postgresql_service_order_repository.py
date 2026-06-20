from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.customers.models import CustomerModel
from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.interfaces import AbstractServiceOrderRepository
from app.service_orders.models import ServiceOrderModel
from app.service_orders.repository import SqlAlchemyServiceOrderRepository


pytestmark = pytest.mark.postgres


def create_customer(postgres_session, *, customer_id: UUID | None = None) -> UUID:
    customer_id = customer_id or uuid4()
    customer = CustomerModel(
        id=customer_id,
        name="Cliente Teste",
        whatsapp=f"119{str(customer_id.int)[-8:]}",
    )
    postgres_session.add(customer)
    postgres_session.flush()
    return customer_id


def make_service_order(**overrides: object) -> ServiceOrder:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
        "equipment_brand": "Dell",
        "equipment_model": "Latitude 5420",
        "equipment_identification": "SN-123",
        "internal_notes": "Priority customer",
        "created_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return ServiceOrder(**data)


def test_repository_implements_service_order_repository_contract(postgres_session) -> None:
    repository = SqlAlchemyServiceOrderRepository(postgres_session)

    assert isinstance(repository, AbstractServiceOrderRepository)


def test_add_persists_service_order(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    service_order = make_service_order(customer_id=customer_id)
    repository = SqlAlchemyServiceOrderRepository(postgres_session)

    result = repository.add(service_order)
    postgres_session.commit()

    persisted = postgres_session.get(ServiceOrderModel, service_order.id)
    assert result == service_order
    assert persisted is not None
    assert persisted.id == service_order.id
    assert persisted.customer_id == customer_id
    assert persisted.equipment_type == "Notebook"
    assert persisted.reported_problem == "Does not turn on"
    assert persisted.equipment_brand == "Dell"
    assert persisted.equipment_model == "Latitude 5420"
    assert persisted.equipment_identification == "SN-123"
    assert persisted.internal_notes == "Priority customer"
    assert persisted.status == ServiceOrderStatus.OPENED.value


def test_add_rejects_duplicate_id(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    service_order = make_service_order(customer_id=customer_id)
    repository = SqlAlchemyServiceOrderRepository(postgres_session)

    repository.add(service_order)

    with pytest.raises(ValueError, match="Service order with this ID already exists."):
        repository.add(service_order)


def test_get_by_id_returns_persisted_service_order(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    service_order = make_service_order(customer_id=customer_id)
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(service_order)
    postgres_session.commit()

    result = repository.get_by_id(service_order.id)

    assert result == service_order


def test_get_by_id_returns_none_when_not_found(postgres_session) -> None:
    repository = SqlAlchemyServiceOrderRepository(postgres_session)

    assert repository.get_by_id(uuid4()) is None


def test_list_returns_all_service_orders(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    first = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    second = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(first)
    repository.add(second)
    postgres_session.commit()

    results = repository.list()

    assert [service_order.id for service_order in results] == [
        second.id,
        first.id,
    ]


def test_list_filters_by_customer_id(postgres_session) -> None:
    target_customer_id = create_customer(postgres_session)
    other_customer_id = create_customer(postgres_session)
    target_first = make_service_order(
        customer_id=target_customer_id,
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    other = make_service_order(customer_id=other_customer_id)
    target_second = make_service_order(
        customer_id=target_customer_id,
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(target_first)
    repository.add(other)
    repository.add(target_second)
    postgres_session.commit()

    results = repository.list(customer_id=target_customer_id)

    assert [service_order.id for service_order in results] == [
        target_second.id,
        target_first.id,
    ]
    assert other.id not in [service_order.id for service_order in results]


def test_list_applies_limit_and_offset(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    oldest = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    middle = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )
    newest = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
    )
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(oldest)
    repository.add(middle)
    repository.add(newest)
    postgres_session.commit()

    results = repository.list(limit=1, offset=1)

    assert [service_order.id for service_order in results] == [middle.id]


def test_list_applies_pagination_after_customer_filter(postgres_session) -> None:
    target_customer_id = create_customer(postgres_session)
    other_customer_id = create_customer(postgres_session)
    target_oldest = make_service_order(
        customer_id=target_customer_id,
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    target_middle = make_service_order(
        customer_id=target_customer_id,
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )
    target_newest = make_service_order(
        customer_id=target_customer_id,
        created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
    )
    other = make_service_order(
        customer_id=other_customer_id,
        created_at=datetime(2026, 1, 4, 10, 0, tzinfo=timezone.utc),
    )
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(target_oldest)
    repository.add(target_middle)
    repository.add(target_newest)
    repository.add(other)
    postgres_session.commit()

    results = repository.list(customer_id=target_customer_id, limit=1, offset=1)

    assert [service_order.id for service_order in results] == [target_middle.id]
    assert other.id not in [service_order.id for service_order in results]


def test_list_returns_service_orders_ordered_by_created_at_desc(postgres_session) -> None:
    customer_id = create_customer(postgres_session)
    newest = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
    )
    oldest = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    middle = make_service_order(
        customer_id=customer_id,
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(newest)
    repository.add(oldest)
    repository.add(middle)
    postgres_session.commit()

    results = repository.list()

    assert [service_order.id for service_order in results] == [
        newest.id,
        middle.id,
        oldest.id,
    ]


def test_update_replaces_all_mutable_fields(postgres_session) -> None:
    original_customer_id = create_customer(postgres_session)
    updated_customer_id = create_customer(postgres_session)
    service_order = make_service_order(customer_id=original_customer_id)
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    repository.add(service_order)
    postgres_session.commit()
    updated_created_at = datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)
    closed_at = datetime(2026, 1, 4, 10, 0, tzinfo=timezone.utc)
    updated = ServiceOrder(
        id=service_order.id,
        customer_id=updated_customer_id,
        equipment_type="Desktop",
        reported_problem="Unexpected shutdown",
        equipment_brand="Lenovo",
        equipment_model="ThinkCentre",
        equipment_identification="SN-999",
        internal_notes="Changed after diagnosis",
        status=ServiceOrderStatus.CANCELLED,
        created_at=updated_created_at,
        updated_at=updated_at,
        closed_at=closed_at,
    )

    result = repository.update(updated)
    postgres_session.commit()

    persisted = postgres_session.get(ServiceOrderModel, service_order.id)
    assert result == updated
    assert persisted.customer_id == updated_customer_id
    assert persisted.equipment_type == "Desktop"
    assert persisted.reported_problem == "Unexpected shutdown"
    assert persisted.equipment_brand == "Lenovo"
    assert persisted.equipment_model == "ThinkCentre"
    assert persisted.equipment_identification == "SN-999"
    assert persisted.internal_notes == "Changed after diagnosis"
    assert persisted.status == ServiceOrderStatus.CANCELLED.value
    assert persisted.created_at == updated_created_at
    assert persisted.updated_at == updated_at
    assert persisted.closed_at == closed_at


def test_update_raises_error_when_service_order_not_found(postgres_session) -> None:
    repository = SqlAlchemyServiceOrderRepository(postgres_session)
    service_order = make_service_order()

    with pytest.raises(ValueError, match="Service order with this ID does not exist."):
        repository.update(service_order)
