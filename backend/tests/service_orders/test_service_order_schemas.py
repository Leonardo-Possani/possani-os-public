from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.schemas import (
    ServiceOrderCreate,
    ServiceOrderRead,
    ServiceOrderStatusUpdate,
)


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


def test_service_order_create_strips_text_fields() -> None:
    customer_id = uuid4()

    payload = ServiceOrderCreate(
        customer_id=customer_id,
        equipment_type="  Notebook  ",
        reported_problem="  Does not turn on  ",
        equipment_brand="  Dell  ",
        equipment_model="  Latitude 5420  ",
        equipment_identification="  SN-123  ",
        internal_notes="  Priority customer  ",
    )

    assert payload.customer_id == customer_id
    assert payload.equipment_type == "Notebook"
    assert payload.reported_problem == "Does not turn on"
    assert payload.equipment_brand == "Dell"
    assert payload.equipment_model == "Latitude 5420"
    assert payload.equipment_identification == "SN-123"
    assert payload.internal_notes == "Priority customer"


@pytest.mark.parametrize("field_name", ["equipment_type", "reported_problem"])
def test_service_order_create_rejects_blank_required_text(field_name: str) -> None:
    data = {
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
    }
    data[field_name] = "   "

    with pytest.raises(ValidationError):
        ServiceOrderCreate(**data)


@pytest.mark.parametrize(
    ("field_name", "valid_value"),
    [
        ("equipment_type", "a" * 500),
        ("reported_problem", "a" * 2000),
        ("equipment_brand", "a" * 255),
        ("equipment_model", "a" * 255),
        ("equipment_identification", "a" * 255),
        ("internal_notes", "a" * 2000),
    ],
)
def test_service_order_create_accepts_max_lengths(
    field_name: str,
    valid_value: str,
) -> None:
    data = {
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
        field_name: valid_value,
    }

    payload = ServiceOrderCreate(**data)

    assert getattr(payload, field_name) == valid_value


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("equipment_type", "a" * 501),
        ("reported_problem", "a" * 2001),
        ("equipment_brand", "a" * 256),
        ("equipment_model", "a" * 256),
        ("equipment_identification", "a" * 256),
        ("internal_notes", "a" * 2001),
    ],
)
def test_service_order_create_rejects_values_over_max_lengths(
    field_name: str,
    invalid_value: str,
) -> None:
    data = {
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
        field_name: invalid_value,
    }

    with pytest.raises(ValidationError):
        ServiceOrderCreate(**data)


@pytest.mark.parametrize(
    "missing_field",
    ["customer_id", "equipment_type", "reported_problem"],
)
def test_service_order_create_requires_mandatory_fields(missing_field: str) -> None:
    data = {
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
    }
    data.pop(missing_field)

    with pytest.raises(ValidationError):
        ServiceOrderCreate(**data)


def test_service_order_status_update_accepts_valid_status() -> None:
    payload = ServiceOrderStatusUpdate(status="in_progress")

    assert payload.status == ServiceOrderStatus.IN_PROGRESS


def test_service_order_status_update_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ServiceOrderStatusUpdate(status="unknown")


def test_service_order_read_from_domain_maps_all_fields() -> None:
    closed_at = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)
    service_order = make_service_order(
        status=ServiceOrderStatus.DELIVERED,
        closed_at=closed_at,
    )

    read_model = ServiceOrderRead.from_domain(service_order)

    assert read_model.id == str(service_order.id)
    assert read_model.customer_id == str(service_order.customer_id)
    assert read_model.equipment_type == "Notebook"
    assert read_model.reported_problem == "Does not turn on"
    assert read_model.equipment_brand == "Dell"
    assert read_model.equipment_model == "Latitude 5420"
    assert read_model.equipment_identification == "SN-123"
    assert read_model.internal_notes == "Priority customer"
    assert read_model.status == "delivered"
    assert read_model.created_at == service_order.created_at
    assert read_model.updated_at == service_order.updated_at
    assert read_model.closed_at == closed_at
