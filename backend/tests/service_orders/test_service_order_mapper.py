from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.mappers import ServiceOrderMapper
from app.service_orders.models import ServiceOrderModel


def make_service_order_model(**overrides: object) -> ServiceOrderModel:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
        "equipment_brand": "Dell",
        "equipment_model": "Latitude 5420",
        "equipment_identification": "SN-123",
        "internal_notes": "Priority customer",
        "status": ServiceOrderStatus.OPENED.value,
        "created_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        "closed_at": None,
    }
    data.update(overrides)
    return ServiceOrderModel(**data)


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
        "status": ServiceOrderStatus.IN_PROGRESS,
        "created_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 2, 11, 0, tzinfo=timezone.utc),
        "closed_at": None,
    }
    data.update(overrides)
    return ServiceOrder(**data)


def test_to_orm_maps_all_domain_fields() -> None:
    service_order = make_service_order(
        status=ServiceOrderStatus.DELIVERED,
        closed_at=datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc),
    )

    model = ServiceOrderMapper.to_orm(service_order)

    assert isinstance(model, ServiceOrderModel)
    assert model.id == service_order.id
    assert model.customer_id == service_order.customer_id
    assert model.equipment_type == service_order.equipment_type
    assert model.reported_problem == service_order.reported_problem
    assert model.equipment_brand == service_order.equipment_brand
    assert model.equipment_model == service_order.equipment_model
    assert model.equipment_identification == service_order.equipment_identification
    assert model.internal_notes == service_order.internal_notes
    assert model.status == service_order.status.value
    assert model.created_at == service_order.created_at
    assert model.updated_at == service_order.updated_at
    assert model.closed_at == service_order.closed_at


def test_to_domain_maps_all_orm_fields() -> None:
    service_order_id = uuid4()
    customer_id = uuid4()
    created_at = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 1, 2, 11, 0, tzinfo=timezone.utc)
    closed_at = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)
    model = ServiceOrderModel(
        id=service_order_id,
        customer_id=customer_id,
        equipment_type="Notebook",
        reported_problem="Does not turn on",
        equipment_brand="Dell",
        equipment_model="Latitude 5420",
        equipment_identification="SN-123",
        internal_notes="Priority customer",
        status=ServiceOrderStatus.DELIVERED.value,
        created_at=created_at,
        updated_at=updated_at,
        closed_at=closed_at,
    )

    domain = ServiceOrderMapper.to_domain(model)

    assert domain.id == service_order_id
    assert domain.customer_id == customer_id
    assert domain.equipment_type == "Notebook"
    assert domain.reported_problem == "Does not turn on"
    assert domain.equipment_brand == "Dell"
    assert domain.equipment_model == "Latitude 5420"
    assert domain.equipment_identification == "SN-123"
    assert domain.internal_notes == "Priority customer"
    assert domain.status == ServiceOrderStatus.DELIVERED
    assert domain.created_at == created_at
    assert domain.updated_at == updated_at
    assert domain.closed_at == closed_at


def test_round_trip_with_optional_fields() -> None:
    service_order = make_service_order()

    model = ServiceOrderMapper.to_orm(service_order)
    domain = ServiceOrderMapper.to_domain(model)

    assert domain == service_order


def test_round_trip_with_null_optional_fields() -> None:
    service_order = make_service_order(
        equipment_brand=None,
        equipment_model=None,
        equipment_identification=None,
        internal_notes=None,
        status=ServiceOrderStatus.OPENED,
        closed_at=None,
    )

    model = ServiceOrderMapper.to_orm(service_order)
    domain = ServiceOrderMapper.to_domain(model)

    assert domain == service_order
    assert domain.equipment_brand is None
    assert domain.equipment_model is None
    assert domain.equipment_identification is None
    assert domain.internal_notes is None
    assert domain.closed_at is None


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("id", None, "Service order ID is required."),
        ("customer_id", None, "Customer ID is required."),
        ("equipment_type", None, "Equipment type is required."),
        ("reported_problem", None, "Reported problem is required."),
        ("status", None, "Status is required."),
        ("created_at", None, "Created at is required."),
        ("updated_at", None, "Updated at is required."),
    ],
)
def test_to_domain_rejects_invalid_required_fields(
    field_name: str,
    value: object,
    message: str,
) -> None:
    model = make_service_order_model(**{field_name: value})

    with pytest.raises(ValueError, match=message):
        ServiceOrderMapper.to_domain(model)


def test_to_domain_rejects_invalid_status_value() -> None:
    model = make_service_order_model(status="invalid")

    with pytest.raises(ValueError, match="'invalid' is not a valid ServiceOrderStatus"):
        ServiceOrderMapper.to_domain(model)
