from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints, field_validator

from app.service_orders.domain import ServiceOrder, ServiceOrderStatus


RequiredEquipmentType = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]
RequiredReportedProblem = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2000),
]
OptionalShortText = Annotated[
    str | None,
    StringConstraints(strip_whitespace=True, max_length=255),
]
OptionalLongText = Annotated[
    str | None,
    StringConstraints(strip_whitespace=True, max_length=2000),
]


class ServiceOrderCreate(BaseModel):
    customer_id: UUID
    equipment_type: RequiredEquipmentType
    reported_problem: RequiredReportedProblem
    equipment_brand: OptionalShortText = None
    equipment_model: OptionalShortText = None
    equipment_identification: OptionalShortText = None
    internal_notes: OptionalLongText = None

    @field_validator(
        "equipment_brand",
        "equipment_model",
        "equipment_identification",
        "internal_notes",
        mode="after",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value or None


class ServiceOrderStatusUpdate(BaseModel):
    status: ServiceOrderStatus


class ServiceOrderRead(BaseModel):
    id: str
    customer_id: str
    equipment_type: str
    reported_problem: str
    equipment_brand: str | None
    equipment_model: str | None
    equipment_identification: str | None
    internal_notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    @classmethod
    def from_domain(cls, service_order: ServiceOrder) -> "ServiceOrderRead":
        return cls(
            id=str(service_order.id),
            customer_id=str(service_order.customer_id),
            equipment_type=service_order.equipment_type,
            reported_problem=service_order.reported_problem,
            equipment_brand=service_order.equipment_brand,
            equipment_model=service_order.equipment_model,
            equipment_identification=service_order.equipment_identification,
            internal_notes=service_order.internal_notes,
            status=service_order.status.value,
            created_at=service_order.created_at,
            updated_at=service_order.updated_at,
            closed_at=service_order.closed_at,
        )
