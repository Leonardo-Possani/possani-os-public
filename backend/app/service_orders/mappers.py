from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.models import ServiceOrderModel


class ServiceOrderMapper:
    _REQUIRED_MODEL_FIELDS = {
        "id": "Service order ID is required.",
        "customer_id": "Customer ID is required.",
        "equipment_type": "Equipment type is required.",
        "reported_problem": "Reported problem is required.",
        "status": "Status is required.",
        "created_at": "Created at is required.",
        "updated_at": "Updated at is required.",
    }

    @staticmethod
    def to_orm(service_order: ServiceOrder) -> ServiceOrderModel:
        return ServiceOrderModel(
            id=service_order.id,
            customer_id=service_order.customer_id,
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

    @staticmethod
    def to_domain(model: ServiceOrderModel) -> ServiceOrder:
        ServiceOrderMapper._validate_required_model_fields(model)

        return ServiceOrder(
            id=model.id,
            customer_id=model.customer_id,
            equipment_type=model.equipment_type,
            reported_problem=model.reported_problem,
            equipment_brand=model.equipment_brand,
            equipment_model=model.equipment_model,
            equipment_identification=model.equipment_identification,
            internal_notes=model.internal_notes,
            status=ServiceOrderStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            closed_at=model.closed_at,
        )

    @staticmethod
    def _validate_required_model_fields(model: ServiceOrderModel) -> None:
        for field_name, message in ServiceOrderMapper._REQUIRED_MODEL_FIELDS.items():
            if getattr(model, field_name) is None:
                raise ValueError(message)
