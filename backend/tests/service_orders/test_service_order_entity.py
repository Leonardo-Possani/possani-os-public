from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.service_orders.domain import ServiceOrder, ServiceOrderStatus


OPTIONAL_STRING_FIELDS = (
    "equipment_brand",
    "equipment_model",
    "equipment_identification",
    "internal_notes",
)


def make_service_order(**overrides: object) -> ServiceOrder:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return ServiceOrder(**data)


def test_create_service_order_with_initial_status_and_no_closed_at() -> None:
    service_order = make_service_order()

    assert service_order.status == ServiceOrderStatus.OPENED
    assert service_order.closed_at is None


def test_optional_fields_accept_none() -> None:
    service_order = make_service_order(
        equipment_brand=None,
        equipment_model=None,
        equipment_identification=None,
        internal_notes=None,
    )

    for field_name in OPTIONAL_STRING_FIELDS:
        assert getattr(service_order, field_name) is None


def test_optional_fields_strip_whitespace_to_none() -> None:
    service_order = make_service_order(
        equipment_brand="   ",
        equipment_model="   ",
        equipment_identification="   ",
        internal_notes="   ",
    )

    for field_name in OPTIONAL_STRING_FIELDS:
        assert getattr(service_order, field_name) is None


def test_optional_fields_normalize_string_values() -> None:
    service_order = make_service_order(
        equipment_brand="  Dell  ",
        equipment_model="  Notebook  ",
        equipment_identification="  SN-123  ",
        internal_notes="  Priority customer  ",
    )

    assert service_order.equipment_brand == "Dell"
    assert service_order.equipment_model == "Notebook"
    assert service_order.equipment_identification == "SN-123"
    assert service_order.internal_notes == "Priority customer"


@pytest.mark.parametrize(
    ("field_name", "valid_value"),
    [
        ("equipment_brand", "a" * 255),
        ("equipment_model", "a" * 255),
        ("equipment_identification", "a" * 255),
        ("internal_notes", "a" * 2000),
    ],
)
def test_optional_text_fields_accept_max_length(
    field_name: str,
    valid_value: str,
) -> None:
    service_order = make_service_order(**{field_name: valid_value})

    assert getattr(service_order, field_name) == valid_value


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        (
            "equipment_brand",
            "a" * 256,
            "Equipment brand cannot exceed 255 characters.",
        ),
        (
            "equipment_model",
            "a" * 256,
            "Equipment model cannot exceed 255 characters.",
        ),
        (
            "equipment_identification",
            "a" * 256,
            "Equipment identification cannot exceed 255 characters.",
        ),
        (
            "internal_notes",
            "a" * 2001,
            "Internal notes cannot exceed 2000 characters.",
        ),
    ],
)
def test_optional_text_fields_reject_values_over_max_length(
    field_name: str,
    invalid_value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_service_order(**{field_name: invalid_value})


@pytest.mark.parametrize("field_name", OPTIONAL_STRING_FIELDS)
@pytest.mark.parametrize("value", [123, True, object()])
def test_optional_fields_reject_non_string_types(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="must be a string"):
        make_service_order(**{field_name: value})


@pytest.mark.parametrize("field_name", ["id", "customer_id"])
@pytest.mark.parametrize("value", ["not-a-uuid", 123, True, object()])
def test_id_and_customer_id_must_be_uuid(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_service_order(**{field_name: value})


def test_created_at_and_updated_at_are_set_on_creation() -> None:
    before = datetime.now(timezone.utc)

    service_order = ServiceOrder(
        id=uuid4(),
        customer_id=uuid4(),
        equipment_type="Notebook",
        reported_problem="Does not turn on",
    )

    after = datetime.now(timezone.utc)

    assert before <= service_order.created_at <= after
    assert before <= service_order.updated_at <= after
    assert service_order.created_at.tzinfo == timezone.utc
    assert service_order.updated_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("customer_id", None, "Customer ID is required."),
        ("equipment_type", None, "Equipment type is required."),
        ("equipment_type", "", "Equipment type cannot be empty."),
        ("equipment_type", "   ", "Equipment type cannot be empty."),
        ("reported_problem", None, "Reported problem is required."),
        ("reported_problem", "", "Reported problem cannot be empty."),
        ("reported_problem", "   ", "Reported problem cannot be empty."),
    ],
)
def test_reject_service_order_without_required_fields(
    field_name: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_service_order(**{field_name: value})


@pytest.mark.parametrize(
    ("field_name", "valid_value"),
    [
        ("equipment_type", "a" * 500),
        ("reported_problem", "a" * 2000),
    ],
)
def test_required_text_fields_accept_max_length(
    field_name: str,
    valid_value: str,
) -> None:
    service_order = make_service_order(**{field_name: valid_value})

    assert getattr(service_order, field_name) == valid_value


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("equipment_type", "a" * 501, "Equipment type cannot exceed 500 characters."),
        (
            "reported_problem",
            "a" * 2001,
            "Reported problem cannot exceed 2000 characters.",
        ),
    ],
)
def test_required_text_fields_reject_values_over_max_length(
    field_name: str,
    invalid_value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_service_order(**{field_name: invalid_value})


@pytest.mark.parametrize(
    ("status", "expected_is_terminal"),
    [
        (ServiceOrderStatus.OPENED, False),
        (ServiceOrderStatus.IN_PROGRESS, False),
        (ServiceOrderStatus.WAITING_CUSTOMER, False),
        (ServiceOrderStatus.WAITING_PART, False),
        (ServiceOrderStatus.FINISHED, False),
        (ServiceOrderStatus.DELIVERED, True),
        (ServiceOrderStatus.CANCELLED, True),
    ],
)
def test_is_terminal_returns_expected_value(
    status: ServiceOrderStatus,
    expected_is_terminal: bool,
) -> None:
    service_order = make_service_order(status=status)

    assert service_order.is_terminal is expected_is_terminal


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (ServiceOrderStatus.OPENED, ServiceOrderStatus.IN_PROGRESS),
        (ServiceOrderStatus.OPENED, ServiceOrderStatus.WAITING_CUSTOMER),
        (ServiceOrderStatus.OPENED, ServiceOrderStatus.CANCELLED),
        (ServiceOrderStatus.IN_PROGRESS, ServiceOrderStatus.WAITING_CUSTOMER),
        (ServiceOrderStatus.IN_PROGRESS, ServiceOrderStatus.WAITING_PART),
        (ServiceOrderStatus.IN_PROGRESS, ServiceOrderStatus.FINISHED),
        (ServiceOrderStatus.IN_PROGRESS, ServiceOrderStatus.CANCELLED),
        (ServiceOrderStatus.WAITING_CUSTOMER, ServiceOrderStatus.IN_PROGRESS),
        (ServiceOrderStatus.WAITING_CUSTOMER, ServiceOrderStatus.CANCELLED),
        (ServiceOrderStatus.WAITING_PART, ServiceOrderStatus.IN_PROGRESS),
        (ServiceOrderStatus.WAITING_PART, ServiceOrderStatus.CANCELLED),
        (ServiceOrderStatus.FINISHED, ServiceOrderStatus.DELIVERED),
        (ServiceOrderStatus.FINISHED, ServiceOrderStatus.IN_PROGRESS),
        (ServiceOrderStatus.FINISHED, ServiceOrderStatus.CANCELLED),
    ],
)
def test_change_status_allows_valid_transitions(
    current_status: ServiceOrderStatus,
    new_status: ServiceOrderStatus,
) -> None:
    service_order = make_service_order(status=current_status)

    updated = service_order.change_status(new_status)

    assert updated.status == new_status
    assert updated is not service_order


def test_change_status_accepts_string_status() -> None:
    service_order = make_service_order(status=ServiceOrderStatus.OPENED)

    updated = service_order.change_status("in_progress")

    assert updated.status == ServiceOrderStatus.IN_PROGRESS


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (ServiceOrderStatus.OPENED, ServiceOrderStatus.DELIVERED),
        (ServiceOrderStatus.WAITING_PART, ServiceOrderStatus.FINISHED),
        (ServiceOrderStatus.WAITING_CUSTOMER, ServiceOrderStatus.WAITING_PART),
        (ServiceOrderStatus.FINISHED, ServiceOrderStatus.WAITING_CUSTOMER),
    ],
)
def test_change_status_rejects_invalid_transitions(
    current_status: ServiceOrderStatus,
    new_status: ServiceOrderStatus,
) -> None:
    service_order = make_service_order(status=current_status)

    with pytest.raises(ValueError, match="Invalid service order status transition."):
        service_order.change_status(new_status)


def test_change_status_sets_closed_at_when_delivered() -> None:
    service_order = make_service_order(status=ServiceOrderStatus.FINISHED)

    updated = service_order.change_status(ServiceOrderStatus.DELIVERED)

    assert updated.closed_at is not None
    assert updated.closed_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    "current_status",
    [
        ServiceOrderStatus.OPENED,
        ServiceOrderStatus.IN_PROGRESS,
        ServiceOrderStatus.WAITING_CUSTOMER,
        ServiceOrderStatus.WAITING_PART,
        ServiceOrderStatus.FINISHED,
    ],
)
def test_change_status_sets_closed_at_when_cancelled(
    current_status: ServiceOrderStatus,
) -> None:
    service_order = make_service_order(status=current_status)

    updated = service_order.change_status(ServiceOrderStatus.CANCELLED)

    assert updated.closed_at is not None
    assert updated.closed_at.tzinfo == timezone.utc


def test_change_status_keeps_closed_at_empty_when_finished() -> None:
    service_order = make_service_order(status=ServiceOrderStatus.IN_PROGRESS)

    updated = service_order.change_status(ServiceOrderStatus.FINISHED)

    assert updated.closed_at is None


@pytest.mark.parametrize(
    "terminal_status",
    [
        ServiceOrderStatus.DELIVERED,
        ServiceOrderStatus.CANCELLED,
    ],
)
def test_change_status_rejects_changes_from_terminal_statuses(
    terminal_status: ServiceOrderStatus,
) -> None:
    service_order = make_service_order(status=terminal_status)

    with pytest.raises(ValueError, match="Terminal service order cannot change status."):
        service_order.change_status(ServiceOrderStatus.IN_PROGRESS)


def test_change_status_updates_updated_at() -> None:
    initial_updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    service_order = make_service_order(
        status=ServiceOrderStatus.OPENED,
        updated_at=initial_updated_at,
    )

    updated = service_order.change_status(ServiceOrderStatus.IN_PROGRESS)

    assert updated.updated_at > initial_updated_at
    assert updated.updated_at.tzinfo == timezone.utc
