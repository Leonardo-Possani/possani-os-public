from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID


class ServiceOrderStatus(str, Enum):
    OPENED = "opened"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_PART = "waiting_part"
    FINISHED = "finished"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


_ALLOWED_STATUS_TRANSITIONS: dict[ServiceOrderStatus, set[ServiceOrderStatus]] = {
    ServiceOrderStatus.OPENED: {
        ServiceOrderStatus.IN_PROGRESS,
        ServiceOrderStatus.WAITING_CUSTOMER,
        ServiceOrderStatus.CANCELLED,
    },
    ServiceOrderStatus.IN_PROGRESS: {
        ServiceOrderStatus.WAITING_CUSTOMER,
        ServiceOrderStatus.WAITING_PART,
        ServiceOrderStatus.FINISHED,
        ServiceOrderStatus.CANCELLED,
    },
    ServiceOrderStatus.WAITING_CUSTOMER: {
        ServiceOrderStatus.IN_PROGRESS,
        ServiceOrderStatus.CANCELLED,
    },
    ServiceOrderStatus.WAITING_PART: {
        ServiceOrderStatus.IN_PROGRESS,
        ServiceOrderStatus.CANCELLED,
    },
    ServiceOrderStatus.FINISHED: {
        ServiceOrderStatus.DELIVERED,
        ServiceOrderStatus.IN_PROGRESS,
        ServiceOrderStatus.CANCELLED,
    },
}


_TERMINAL_STATUSES: set[ServiceOrderStatus] = {
    ServiceOrderStatus.DELIVERED,
    ServiceOrderStatus.CANCELLED,
}

_EQUIPMENT_TYPE_MAX_LENGTH = 500
_REPORTED_PROBLEM_MAX_LENGTH = 2000
_EQUIPMENT_BRAND_MAX_LENGTH = 255
_EQUIPMENT_MODEL_MAX_LENGTH = 255
_EQUIPMENT_IDENTIFICATION_MAX_LENGTH = 255
_INTERNAL_NOTES_MAX_LENGTH = 2000

_OPTIONAL_TEXT_FIELD_MAX_LENGTHS = {
    "equipment_brand": _EQUIPMENT_BRAND_MAX_LENGTH,
    "equipment_model": _EQUIPMENT_MODEL_MAX_LENGTH,
    "equipment_identification": _EQUIPMENT_IDENTIFICATION_MAX_LENGTH,
    "internal_notes": _INTERNAL_NOTES_MAX_LENGTH,
}


@dataclass(frozen=True)
class ServiceOrder:
    id: UUID
    customer_id: UUID
    equipment_type: str
    reported_problem: str
    equipment_brand: str | None = None
    equipment_model: str | None = None
    equipment_identification: str | None = None
    internal_notes: str | None = None
    status: ServiceOrderStatus = ServiceOrderStatus.OPENED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.id is None:
            raise ValueError("Service order ID is required.")
        if self.customer_id is None:
            raise ValueError("Customer ID is required.")
        if not isinstance(self.id, UUID):
            raise ValueError("Service order ID must be a UUID.")
        if not isinstance(self.customer_id, UUID):
            raise ValueError("Customer ID must be a UUID.")

        equipment_type = self._require_non_empty_string(
            self.equipment_type,
            "Equipment type",
            max_length=_EQUIPMENT_TYPE_MAX_LENGTH,
        )
        reported_problem = self._require_non_empty_string(
            self.reported_problem,
            "Reported problem",
            max_length=_REPORTED_PROBLEM_MAX_LENGTH,
        )
        object.__setattr__(self, "equipment_type", equipment_type)
        object.__setattr__(self, "reported_problem", reported_problem)

        for field_name, max_length in _OPTIONAL_TEXT_FIELD_MAX_LENGTHS.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            if not isinstance(value, str):
                label = self._field_label(field_name)
                raise ValueError(f"{label} must be a string.")
            normalized = value.strip()
            if len(normalized) > max_length:
                label = self._field_label(field_name)
                raise ValueError(f"{label} cannot exceed {max_length} characters.")
            object.__setattr__(self, field_name, normalized or None)

        if not isinstance(self.status, ServiceOrderStatus):
            object.__setattr__(self, "status", ServiceOrderStatus(self.status))

    def change_status(self, new_status: ServiceOrderStatus) -> "ServiceOrder":
        if not isinstance(new_status, ServiceOrderStatus):
            new_status = ServiceOrderStatus(new_status)

        if self.is_terminal:
            raise ValueError("Terminal service order cannot change status.")

        allowed_statuses = _ALLOWED_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed_statuses:
            raise ValueError("Invalid service order status transition.")

        now = datetime.now(timezone.utc)
        closed_at = now if new_status in _TERMINAL_STATUSES else self.closed_at

        return replace(
            self,
            status=new_status,
            updated_at=now,
            closed_at=closed_at,
        )

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES

    @staticmethod
    def _require_non_empty_string(
        value: object,
        field_name: str,
        *,
        max_length: int,
    ) -> str:
        if value is None:
            raise ValueError(f"{field_name} is required.")
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty.")
        if len(normalized) > max_length:
            raise ValueError(f"{field_name} cannot exceed {max_length} characters.")
        return normalized

    @staticmethod
    def _field_label(field_name: str) -> str:
        return field_name.replace("_", " ").capitalize()
